# -*- coding: utf-8 -*-
"""统一棋谱记录器 —— 输出 TS Espionnage 英文文本格式(人类棋谱)。

所有棋谱生成点(UI .tsg、rl/spectate_ruletable、log/watch_*、showmatch、
rl/play_match --record-dir)共用本模块,输出可被 `rl/replay_parser.parse_espionnage`
以及 replay_dataset / validate_replays / build_bc_dataset 解析的格式:

    SETUP: USSR will play as USSR.
    US will play as USA.

    Turn 1, Headline Phase: COMECON* & CIA Created: USSR Headlines COMECON*
    US Headlines CIA Created

    Turn 1, USSR AR1: COMECON*: Coup (3 Ops):
    Target: Italy
    FAILURE: 1 [ + 3 - 2x2 = 0 ]
    USSR Military Ops to 3
    DEFCON degrades to 4

    Turn 1, US AR1: Duck and Cover: Space Race (3 Ops):
    Die roll: 2 -- Success! (Needed 3 or less)
    US advances to 1 in the Space Race.

    Turn 1, USSR AR2: Quagmire*: USSR discards NATO*
    Trap Roll: 4 <= 4 -- Trap Escaped
    Quagmire* is no longer in play.

    USSR wins by Victory Points

实现方式:对 `Input.recv` 做猴子补丁探针 —— 引擎的一切玩家输入(含 UI 的
auto_rng 骰子、RL env 自动消费的 NEUTRAL 输入)都经 recv 同步执行 callback,
副作用全部发生在 recv 内,故在每次接受动作前后对游戏状态做轻量快照即可完整
捕获整局。渲染器把快照序列重组成 SETUP / Headline / AR 块;块与块之间的无输入
间隙(事件结算、回合清理)由"块末对账"补出状态差行。

下游解析锚点契约(勿改动):
  * ``Turn N, Headline Phase: A & B: USSR Headlines A`` + ``US Headlines B``
    (DEFCON 恢复/洗牌时拆行: 标题行尾接 ``: DEFCON improves to N``,
    下一行 ``*RESHUFFLE*``,再两行 USSR/US Headlines)
  * ``Turn N, (USSR|US) ARn: CARD: Mode (N Ops):``(Mode ∈ Event:/Place
    Influence/Coup/Realignment/Space Race); QBT 弃牌块头部合一行:
    ``Turn N, S ARn: CARD: S discards CARD``
  * ``Target: X``; 政变 ``SUCCESS/FAILURE: d [ + ops (mod)  - 2xS = diff ]``
    (修正段仅非零时出现); 战争 ``War in X`` + ``VICTORY/DEFEAT: d (mod)  >= N``;
    对齐 ``USSR rolls a (+m) = n`` / ``US rolls b (+m) = n``(每方各自修正,无句号)
  * QBT 逃脱 ``Trap Roll: d <= 4 -- Trap Escaped`` /
    ``Trap Roll: d > 4 -- Trap Remains in Effect``
  * ``Score is USSR N.`` / ``Score is US N.`` / ``Score is even.``、
    ``DEFCON degrades|improves to N``、``{side} Military Ops to N``(归零不输出)、
    ``{side} {+n} in {country} [us][ussr]``(bracket 为绝对值)、
    ``{card} is (no longer) in play.``、``{side} discards X``(无句号)、
    ``{side} reveals X`` / ``{side} has no cards to reveal``
  * 终局 ``{USSR|US} wins by {reason}``(无句号,reason 为 Playdek 显示名)
"""

from __future__ import annotations

import re
import threading
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Tuple

from game_mechanics import Game
from twilight_cards import Card
from twilight_enums import MapRegion, Side
from twilight_input_output import Input
from twilight_map import CountryInfo


# ---------------------------------------------------------------------------
# 名称显示:人类日志用空格分隔、斜杠国家、加星牌(event_unique)
# ---------------------------------------------------------------------------
_SLASH_COUNTRIES = {
    'Spain_Portugal': 'Spain/Portugal',
    'Laos_Cambodia': 'Laos/Cambodia',
}


def country_display(name: str) -> str:
    return _SLASH_COUNTRIES.get(name, name.replace('_', ' '))


# Playdek 客户端卡名表（TSEspionage 转储的真实日志反推，419 局词表核对）。
# 显示规则：基础名 + （星号事件）'*'。斜杠/连字符/引号/大小写以 Playdek Client 为准。
_PLAYDEK_CARD_NAMES = {
    "Arab_Israeli_War": "Arab-Israeli War",
    "De_Stalinization": "De-Stalinization",
    "How_I_Learned_to_Stop_Worrying": "How I Learned To Stop Worrying",
    "Indo_Pakistani_War": "Indo-Pakistani War",
    "Iran_Contra_Scandal": "Iran-Contra Scandal",
    "Iran_Iraq_War": "Iran-Iraq War",
    "Middle_East_Scoring": "Mideast Scoring",
    "Red_Scare_Purge": "Red Scare/Purge",
    "Salt_Negotiations": "SALT Negotiations",
    "Soviets_Shoot_Down_KAL_007": "Soviets Shoot Down KAL-007",
    "US_Japan_Mutual_Defense_Pact": "US/Japan Mutual Defense Pact",
    "Grain_Sales_to_Soviets": "Grain Sales To Soviets",
    "Alliance_for_Progress": "Alliance For Progress",
    "The_Voice_Of_America": "The Voice of America",
    "Our_Man_In_Tehran": "Our Man in Tehran",
    "Yuri_And_Samantha": "Yuri and Samantha",
    "AWACS_Sale_to_Saudis": "AWACS Sale To Saudis",
    "We_Will_Bury_You": '"We Will Bury You"',
    "One_Small_Step": '"One Small Step..."',
    "Lone_Gunman": '"Lone Gunman"',
    "An_Evil_Empire": '"An Evil Empire"',
    # 客户端标题截断为 "..."(419 局实测 64+ 次)
    "Ask_Not_What_Your_Country_Can_Do_For_You": '"Ask Not What Your Country..."',
}


def card_display(name: str) -> str:
    if not name:
        return name
    disp = _PLAYDEK_CARD_NAMES.get(name) or name.replace('_', ' ')
    if name in Card.ALL and Card.ALL[name].event_unique:
        disp += '*'
    return disp


# 揭示事件卡:事件化时揭示一方手牌/计分牌(真实格式 "USSR reveals X" 每卡一
# 行,或 "US has no cards to reveal";引擎通过 print 输出,不受 Input 捕获,
# 渲染时按事件触发时刻快照重建)。
# 关键词 = (被揭示侧, 揭示内容, "no cards" 行格式)。
# - 'hand': 全手牌 (CIA_Created / Lone_Gunman)
# - 'scoring': 手牌中的计分牌 (The_Cambridge_Five)
_REVEAL_SPECS = {
    'CIA_Created': ('USSR', 'hand'),
    'Lone_Gunman': ('US', 'hand'),
    'The_Cambridge_Five': ('US', 'scoring'),
}


def _reveal_lines(card_name: str, snap: StateSnapshot) -> List[str]:
    """事件触发时刻(快照)重建 "'X reveals Y' 行。snap 为事件前快照。"""
    spec = _REVEAL_SPECS.get(card_name)
    if not spec:
        return []
    side_key, kind = spec
    idx = 0 if side_key == 'USSR' else 1
    if kind == 'hand':
        cards = list(snap.hand[idx])
    else:
        cards = [n for n in snap.hand[idx]
                 if n in Card.ALL and Card.ALL[n].card_type == 'Scoring']
    if not cards:
        return [f'{side_key} has no cards to reveal']
    return [f'{side_key} reveals {card_display(n)}' for n in cards]


# ---------------------------------------------------------------------------
# 状态快照
# ---------------------------------------------------------------------------
@dataclass
class StateSnapshot:
    vp: int
    defcon: int
    turn: int
    ar_track: int
    ar_side: str
    milops: List[int]           # [USSR, US]
    space: List[int]            # [USSR, US]
    spaced_turns: List[int]     # [USSR, US]
    basket: List[List[str]]     # [USSR, US]
    hand: List[List[str]]       # [USSR, US]
    discard: List[str]
    map_inf: Dict[str, Tuple[int, int]]  # country -> (ussr, us),仅非零
    terminated: bool = False
    termination_reason: str = ''
    termination_winner: str = ''  # 'USSR' / 'US' / 'NEUTRAL'

    @classmethod
    def snapshot(cls, game: Game) -> 'StateSnapshot':
        winner = getattr(game, 'termination_winner', Side.NEUTRAL)
        ar_side = getattr(game, 'ar_side', Side.NEUTRAL)
        return cls(
            vp=game.vp_track,
            defcon=game.defcon_track,
            turn=game.turn_track,
            ar_track=game.ar_track,
            ar_side=ar_side.name if hasattr(ar_side, 'name') else str(ar_side),
            milops=list(game.milops_track),
            space=list(game.space_track),
            spaced_turns=list(game.spaced_turns),
            basket=[list(game.basket[Side.USSR]), list(game.basket[Side.US])],
            hand=[list(game.hand[Side.USSR]), list(game.hand[Side.US])],
            discard=list(game.discard_pile),
            map_inf={name: (c.influence[Side.USSR], c.influence[Side.US])
                     for name, c in game.map.ALL.items()
                     if c.influence[Side.USSR] or c.influence[Side.US]},
            terminated=game.terminated,
            termination_reason=getattr(game, 'termination_reason', '') or '',
            termination_winner=winner.name if hasattr(winner, 'name') else 'NEUTRAL',
        )


@dataclass
class StepRecord:
    """一次被接受的动作(recv 成功)及其前后状态。"""
    input_type: str
    prompt: str
    side: str
    action: str
    context: Dict
    pre: StateSnapshot
    post: StateSnapshot


# ---------------------------------------------------------------------------
# recv 探针(猴子补丁)
# ---------------------------------------------------------------------------
_ORIG_RECV = Input.recv
_ACTIVE: List['GameRecorder'] = []
_ACTIVE_LOCK = threading.Lock()


def _probe_recv(self, value):
    """探针:只记录"当前 game 的当前 input_state"上的接受动作。

    UI 的 lookahead/rollback 走 deepcopy 克隆,克隆的 input_state 是另一对象,
    身份过滤 `game.input_state is self` 保证克隆上的 recv 不被记录。"""
    with _ACTIVE_LOCK:
        recorders = tuple(_ACTIVE)
    rec = None
    game = None
    for candidate in recorders:
        if candidate._paused:
            continue
        candidate_game = candidate._game_provider()
        if candidate_game.input_state is self:
            rec = candidate
            game = candidate_game
            break
    if rec is None:
        return _ORIG_RECV(self, value)
    pre = StateSnapshot.snapshot(game)
    ok = _ORIG_RECV(self, value)
    if ok:
        rec._rows.append(StepRecord(
            input_type=self.state.name,
            prompt=self.prompt or '',
            side=self.side.name,
            action=str(value),
            context=dict(self.context),
            pre=pre,
            post=StateSnapshot.snapshot(game),
        ))
    return ok


# ---------------------------------------------------------------------------
# block 边界判定
# ---------------------------------------------------------------------------
def _block_kind(r: StepRecord) -> Optional[str]:
    st, p = r.input_type, r.prompt
    if st == 'SELECT_COUNTRY' and 'starting influence' in p:
        return 'setup'
    if st == 'SELECT_CARD':
        if p == 'Select headline.':
            return 'headline'
        if 'Select a card in hand to play.' in p:
            return 'ar'
        if ('You must play a scoring card.' in p
                or 'You must discard a card to be released.' in p):
            return 'qbt'
    return None


def _block_starts(rows: List[StepRecord]) -> List[int]:
    """块起点 = kind 或阶段锚变化处的 block-start 行。

    setup 的 6/7 次选国、头条的两次选牌都是同 prompt 的连续输入,
    必须归并为一个块;普通 AR 必须按 side 切开,否则同一 AR 的美国行动会并入
    苏联块;QBT 连续两个 AR 的选牌 prompt 相同但 ar 不同,也必须切开。
    """
    starts = []
    cur_kind = None
    cur_anchor = None
    for i, r in enumerate(rows):
        kind = _block_kind(r)
        if not kind:
            continue
        anchor = (
            r.pre.turn,
            r.pre.ar_track,
            r.side if kind in ("ar", "qbt") else None,
        )
        if kind != cur_kind or anchor != cur_anchor:
            starts.append(i)
            cur_kind, cur_anchor = kind, anchor
    return starts


# ---------------------------------------------------------------------------
# 公式复刻(全部只依赖快照 + 静态卡库/地图库,渲染时不得查活动 game)
# ---------------------------------------------------------------------------
def _side_from(side_name: str) -> Side:
    return Side[side_name] if side_name in ('USSR', 'US') else Side.NEUTRAL


def _global_eff_ops(pre: StateSnapshot, side: Side, raw: int) -> int:
    modifier = 0
    if side == Side.USSR and 'Brezhnev_Doctrine' in pre.basket[side]:
        modifier += 1
    if side == Side.US and 'Containment' in pre.basket[side]:
        modifier += 1
    if 'Red_Scare_Purge' in pre.basket[side.opp]:
        modifier -= 1
    return min(max(raw + modifier, 1), 4)


def _coup_eff_ops(pre: StateSnapshot, side: Side, card_name: str,
                  country: str) -> int:
    base = Card.ALL[card_name].ops if card_name in Card.ALL else 0
    eff = _global_eff_ops(pre, side, base)
    # local_ops_modifier(game_mechanics.py:1040-1044)
    if card_name == 'The_China_Card' and \
            country in Card.ALL['The_China_Card']._region:
        eff += 1
    if 'Vietnam_Revolts' in pre.basket[Side.USSR] and side == Side.USSR and \
            country in Card.ALL['Vietnam_Revolts']._region:
        eff += 1
    return eff


def _coup_modifier(pre: StateSnapshot, side: Side, country: str) -> int:
    # twilight_map.py:153-167
    modifier = 0
    info = CountryInfo.ALL.get(country)
    if info is not None and (MapRegion.CENTRAL_AMERICA in info.regions
                             or MapRegion.SOUTH_AMERICA in info.regions):
        if 'Latin_American_Death_Squads' in pre.basket[side]:
            modifier += 1
        elif 'Latin_American_Death_Squads' in pre.basket[side.opp]:
            modifier -= 1
    if ('Salt_Negotiations' in pre.basket[side]
            or 'Salt_Negotiations' in pre.basket[side.opp]):
        modifier -= 1
    return modifier


def _realign_modifiers(pre: StateSnapshot, country: str) -> Tuple[int, int]:
    """规则书 6.2.2 的每方骰修正 (ussr_mod, us_mod)。

    每方各自 +1：相邻**控制的**每国、在目标国影响力多于对方、己方超级大国
    与目标相邻。目标国用"多于对方"（非控制）；相邻国用控制（领先 ≥ 稳定度，
    同 Country.control 定义）。Iran Contra Scandal 在场上时 US 每骰 -1
    （卡面文本；引擎以网值 +1 记在 USSR 侧，等价）。两侧净差与引擎
    twilight_map.us_advantage 的 ussr_advantage 一致。
    """
    ussr_mod = 0
    us_mod = 0
    if 'Iran_Contra_Scandal' in pre.basket[Side.USSR]:
        us_mod -= 1
    info = CountryInfo.ALL.get(country)
    if info is None:
        return ussr_mod, us_mod
    for adj in info.adjacent_countries:
        if adj == 'USSR':
            ussr_mod += 1
            continue
        if adj == 'US':
            us_mod += 1
            continue
        inf = pre.map_inf.get(adj)
        if not inf:
            continue
        stab = CountryInfo.ALL.get(adj)
        stab = stab.stability if stab else 0
        if inf[0] - inf[1] >= stab:
            ussr_mod += 1
        elif inf[1] - inf[0] >= stab:
            us_mod += 1
    inf = pre.map_inf.get(country, (0, 0))
    if inf[0] > inf[1]:
        ussr_mod += 1
    elif inf[1] > inf[0]:
        us_mod += 1
    return ussr_mod, us_mod


def _war_modifier(pre: StateSnapshot, target: str, defender: Side,
                  country_itself: bool) -> int:
    # game_mechanics.py:1206-1210:邻接 defender 控制国数(+目标本身若 defender 控制)
    info = CountryInfo.ALL.get(target)
    modifier = 0
    if info is not None:
        for adj in info.adjacent_countries:
            if adj in ('USSR', 'US'):
                continue
            inf = pre.map_inf.get(adj, (0, 0))
            if defender == Side.US and inf[1] > inf[0]:
                modifier += 1
            elif defender == Side.USSR and inf[0] > inf[1]:
                modifier += 1
    if country_itself:
        inf = pre.map_inf.get(target, (0, 0))
        if (defender == Side.US and inf[1] > inf[0]) or \
                (defender == Side.USSR and inf[0] > inf[1]):
            modifier += 1
    return modifier


# 战争牌静态参数:固定目标卡 + 选目标卡(Korean/Arab-Israeli 目标固定)
_WAR_FIXED = {
    'Korean_War': ('South_Korea', Side.USSR, False, 4, 2, 2),
    'Arab_Israeli_War': ('Israel', Side.USSR, True, 4, 2, 2),
}
_WAR_SELECT = {
    'Indo_Pakistani_War': (4, 2, 2),
    'Brush_War': (3, 1, 3),
    'Iran_Iraq_War': (4, 2, 2),
}


def _score_line(vp: int) -> str:
    if vp > 0:
        return f'Score is USSR {vp}.'
    if vp < 0:
        return f'Score is US {-vp}.'
    return 'Score is even.'


def _diff_lines(pre: StateSnapshot, post: StateSnapshot) -> List[str]:
    """按真实 Espionnage 行序渲染 pre→post 的状态差行。

    行序（4 局真实样本统计）：influence → space → VP(单行) → milops → defcon
    → basket，与 Playdek 客户端事件结算打印序吻合（KAL-007 为已知反例：
    DEFCON 在 VP 前，客户端实际按引擎执行序，固定序无法覆盖）。
    """
    lines: List[str] = []

    # influence
    for name in sorted(set(pre.map_inf) | set(post.map_inf)):
        before = pre.map_inf.get(name, (0, 0))
        after = post.map_inf.get(name, (0, 0))
        d_ussr = after[0] - before[0]
        d_us = after[1] - before[1]
        if d_us:
            lines.append(
                f'US {d_us:+d} in {country_display(name)} [{after[1]}][{after[0]}]')
        if d_ussr:
            lines.append(
                f'USSR {d_ussr:+d} in {country_display(name)} [{after[1]}][{after[0]}]')

    # space（真实: advances 在 VP 之前）
    for idx, side in ((0, 'USSR'), (1, 'US')):
        if post.space[idx] > pre.space[idx]:
            lines.append(
                f'{side} advances to {post.space[idx]} in the Space Race.')

    # vp（真实: "X gains N VP. Score is ..." 单行）
    if post.vp != pre.vp:
        side = 'USSR' if post.vp > pre.vp else 'US'
        lines.append(
            f'{side} gains {abs(post.vp - pre.vp)} VP. {_score_line(post.vp)}')

    # milops（真实: 归零清零行不输出）
    for idx, side in ((0, 'USSR'), (1, 'US')):
        if post.milops[idx] != pre.milops[idx] and post.milops[idx] > 0:
            lines.append(f'{side} Military Ops to {post.milops[idx]}')

    # defcon
    if post.defcon != pre.defcon:
        verb = 'degrades' if post.defcon < pre.defcon else 'improves'
        lines.append(f'DEFCON {verb} to {post.defcon}')

    # basket
    for idx, side in ((0, 'USSR'), (1, 'US')):
        pre_set = set(pre.basket[idx])
        post_set = set(post.basket[idx])
        for name in sorted(post_set - pre_set):
            lines.append(f'{card_display(name)} is now in play.')
        for name in sorted(pre_set - post_set):
            lines.append(f'{card_display(name)} is no longer in play.')

    # discards: hand 减少且 discard 增加的牌
    # 真实格式(3305175 行 95/317/609-611/731-732): "US discards Summit" 无句号
    for idx, side in ((0, 'USSR'), (1, 'US')):
        lost = set(pre.hand[idx]) - set(post.hand[idx])
        gained_discard = set(post.discard) - set(pre.discard)
        for name in sorted(lost & gained_discard):
            lines.append(f'{side} discards {card_display(name)}')

    return lines


# ---------------------------------------------------------------------------
# 块渲染
# ---------------------------------------------------------------------------
def _render_block(rows: List[StepRecord], start: int, end: int,
                  next_pre: Optional[StateSnapshot],
                  rec: 'GameRecorder',
                  sections: Optional[List[Tuple[str, StateSnapshot]]] = None,
                  events: Optional[List[Tuple[str, str, StateSnapshot, int]]] = None,
                  prev_defcon: str = '',
                  prev_reshuffle: bool = False
                  ) -> Tuple[str, List[str], bool, List[str]]:
    """渲染 rows[start:end] 为一个日志块。

    返回 ``(text, out_defcon, out_reshuffle, out_cleanup)``:

    sections: 头条块内事件段快照 ``[(card_name, snap, anchor), ...]``（按执行
      顺序；卡名来自 dispose_headline 钩子,快照为事件结算后状态）。真实格式
      据此将头条块拆成多个 ``Event: X`` 段,段间空行。
    prev_defcon: 上一块回合末 gap 中提取的 "DEFCON improves to N" 行,本块为
      headline 块时合并到标题行尾（真实格式: "Turn 3, Headline Phase: A & B:
      DEFCON improves to 3"）。
    prev_reshuffle: 上一块 gap（回合发牌）夹带的洗牌标记,本块为 headline 块
      时在标题行后输出 ``*RESHUFFLE*`` 行（真实格式见 3305175 行 226/663）。
    out_defcon/out_reshuffle: 本块回合末 gap 中提取的残渣,由调用方传给下一块
      headline。
    out_cleanup: 跨回合 gap 的 "Turn N, Cleanup" 行,调用方作为独立块输出
      （真实格式前后空行,与上一 AR 块分隔; 见 3305175 行 108-110）。
    """
    if sections is None:
        sections = []
    if events is None:
        events = []
    kind = _block_kind(rows[start])
    block = rows[start:end]
    lines: List[str] = []
    out_defcon: List[str] = []
    out_reshuffle = False
    out_cleanup: List[str] = []
    # 块内事件化触发(anchor 落于 [start+1, end]):按锚点排序,渲染到该行
    # 前插入 "Event: X" 段标题 + reveal 行(真实: 村夫谱行197-205 CIA 段)。
    block_events = [ev for ev in events if start < ev[3] <= end]
    block_events.sort(key=lambda ev: ev[3])

    # -- 块头 ---------------------------------------------------------------
    side = _side_from(block[0].side)
    turn = block[0].pre.turn
    ar = block[0].pre.ar_track

    if kind == 'setup':
        lines.append(f'SETUP: {rec.ussr_name} will play as USSR.')
        lines.append(f'{rec.us_name} will play as USA.')
        extra = [r for r in block if 'additional starting' in r.prompt]
        if extra:
            # 真实格式: "Handicap influence: US +2"（无句号）
            lines.append(f'Handicap influence: {extra[0].side} +{len(extra)}')
        lines.append(f'Scenario: {rec.scenario}')
        lines.append('Optional Cards Added')
        lines.append(f'Time per Player: {rec.time_per_player}')
    elif kind == 'headline':
        ussr_hl = us_hl = None
        for r in block:
            if r.input_type == 'SELECT_CARD' and r.prompt == 'Select headline.':
                if r.side == 'USSR':
                    ussr_hl = r.action
                elif r.side == 'US':
                    us_hl = r.action
        ussr_hl = ussr_hl or ''
        us_hl = us_hl or ''
        head = (f'Turn {turn}, Headline Phase: {card_display(ussr_hl)} & '
                f'{card_display(us_hl)}')
        split_hl = bool(prev_defcon or prev_reshuffle)
        if prev_defcon:
            # 真实: "Turn 3, Headline Phase: A & B: DEFCON improves to 3"
            lines.append(f'{head}: {prev_defcon}')
        elif split_hl:
            lines.append(head)
        else:
            # 无 DEFCON/RESHUFFLE 尾缀时 "USSR Headlines" 并入标题行
            lines.append(f'{head}: USSR Headlines {card_display(ussr_hl)}')
        if prev_reshuffle:
            lines.append('*RESHUFFLE*')
        if split_hl:
            lines.append(f'USSR Headlines {card_display(ussr_hl)}')
        lines.append(f'US Headlines {card_display(us_hl)}')
        # 头条事件段:以 sections(dispose 钩子)为准分解;无 sections
        # (测试等无钩子场景)时退回 step/gap 渲染。
        if sections:
            base = block[0].pre
            for j, (card, pre_snap, snap, _anchor) in enumerate(sections):
                if j:
                    lines.append('')
                lines.append(f'Event: {card_display(card)}')
                lines.extend(_filter_routine_discards(
                    _diff_lines(base, snap), card))
                base = snap
            # 段间剩余(末段快照 → next_pre),通常为空
            gap_tail = [] if next_pre is None else _diff_lines(base, next_pre)
            lines.extend(_filter_routine_discards(gap_tail, ussr_hl))
            return '\n'.join(lines), out_defcon, out_reshuffle, out_cleanup
    else:  # ar / qbt
        header = f'Turn {turn}, {side.name if hasattr(side, "name") else side} AR{ar}:'
        lines.append(header)

    # -- 块状态 -------------------------------------------------------------
    card_name = ''          # 本块打出的卡(AR 选牌)
    block_card = ''         # 块首实际打出的卡(可能被 UN 等改写卡名,弃置过滤用)
    mode = ''               # CardAction 名
    header_emitted = False
    pending_coup = None     # (country, eff_ops)
    pending_realign = None  # country
    pending_war = None      # (target, attacker, country_itself, lower, win_vp, win_milops)
    pending_qbt_trap = False  # qbt 块已弃牌, 下一次 1d6 为逃脱判定
    grain_card = ''     # Grain Sales 随机选中的牌(揭示行/返还行)
    shuffle_emitted = False
    no_vp_emitted = False   # 计分牌 "No VP awarded." 只发一次
    played_after_discard = ''   # 块内"打断后被使用并弃置"的牌(UN 被选牌):
                                # 真实格式显示 "{side} plays X"、不显示其弃置行

    def emit_header(pre=None):
        nonlocal header_emitted
        if header_emitted or not card_name:
            return
        header_emitted = True
        label = {'INFLUENCE': 'Place Influence', 'COUP': 'Coup',
                 'REALIGNMENT': 'Realignment', 'SPACE': 'Space Race'}.get(mode, '')
        if kind not in ('ar', 'qbt'):
            # 头条块内的事件内嵌选择(如 UN Intervention / Missile Envy 作头条)
            if mode in ('PLAY_EVENT', 'RESOLVE_EVENT_FIRST'):
                lines.append(f'Event: {card_display(card_name)}')
            elif mode == 'SKIP_OPTIONAL_AR':
                lines.append('Skip Optional AR:')
            elif label:
                if mode == 'SPACE':
                    ops = _global_eff_ops(pre, side,
                                          Card.ALL[card_name].ops if card_name in Card.ALL else 0)
                else:
                    ops = Card.ALL[card_name].ops if card_name in Card.ALL else 0
                lines.append(f'{label} ({ops} Ops):')
            return
        head = f'Turn {turn}, {side.name} AR{ar}:'
        if mode in ('PLAY_EVENT', 'RESOLVE_EVENT_FIRST'):
            lines[lines.index(header)] = f'{head} {card_display(card_name)}: Event: {card_display(card_name)}'
        elif mode == 'SKIP_OPTIONAL_AR':
            lines[lines.index(header)] = f'{head} Skip Optional AR:'
        elif label:
            if mode == 'SPACE':
                ops = _global_eff_ops(pre, side,
                                      Card.ALL[card_name].ops if card_name in Card.ALL else 0)
            else:
                ops = Card.ALL[card_name].ops if card_name in Card.ALL else 0
            lines[lines.index(header)] = f'{head} {card_display(card_name)}: {label} ({ops} Ops):'
        else:
            lines[lines.index(header)] = f'{head} {card_display(card_name)}:'

    for i, r in enumerate(block):
        # 事件化触发锚点:该行 recv 之前发生的事件,插入独立段。
        # 标题行已由 emit_header 承载的(PLAY_EVENT/RESOLVE_EVENT_FIRST)事件
        # 不再重复;锚点晚于 SELECT_CARD_ACTION 行动的行间事件是
        # "行动后触发"事件(如 CIA Created 事件化后 US 用 Blank 1 Op)。
        while block_events and block_events[0][3] <= i + start:
            ev_card, ev_side, ev_pre, _ = block_events.pop(0)
            if kind == 'ar' and mode in ('PLAY_EVENT', 'RESOLVE_EVENT_FIRST') \
                    and ev_card == card_name:
                # 标题行已含 "Event: X",仅补 reveal 行
                lines.extend(_reveal_lines(ev_card, ev_pre))
            else:
                lines.append('')
                lines.append(f'Event: {card_display(ev_card)}')
                lines.extend(_reveal_lines(ev_card, ev_pre))

        step_lines: List[str] = []
        st, p, act = r.input_type, r.prompt, r.action

        if st == 'SELECT_CARD':
            if 'Shuffle the deck.' in p:
                # 洗牌确认(每张卡一次):真实格式不显示在发牌处,而是作为
                # *RESHUFFLE* 标记延迟到下一块 headline 标题行后。
                if not shuffle_emitted:
                    out_reshuffle = True
                    shuffle_emitted = True
            elif p == 'Select headline.':
                pass  # 头条选择已由块头承载
            elif 'Select a card in hand to play.' in p:
                card_name = act
                if not block_card:
                    block_card = act
                # 记分牌跳过 select_action 直接 PLAY_EVENT(card_callback)
                if act in Card.ALL and Card.ALL[act].card_type == 'Scoring':
                    mode = 'PLAY_EVENT'
                    emit_header()
            elif 'You must play a scoring card.' in p:
                card_name = act
                mode = 'PLAY_EVENT'
                emit_header()
            elif 'You must discard a card to be released.' in p:
                # 真实格式(3325831 行 329/543): 头部行合一
                # "Turn 4, USSR AR1: Our Man in Tehran*: USSR discards Our Man in Tehran*"
                # 弃牌差行由 _filter_routine_discards(card_name) 去重
                card_name = act
                disp = card_display(act)
                head = f'Turn {turn}, {side.name} AR{ar}:'
                lines[lines.index(head)] = (
                    f'{head} {disp}: {side.name} discards {disp}')
                pending_qbt_trap = True
            elif 'Eagle/Bear has landed' in p:
                pass  # 弃牌差行由 _diff_lines 输出
            elif 'Five Year Plan: USSR randomly discards a card.' == p:
                pass  # 弃牌行由 _diff_lines 承载(无句号,如 "USSR discards Mideast Scoring")
            elif p == ('You may pick a opponent-owned card from your hand '
                       'to use with UN Intervention.'):
                # 真实格式(3305175 行 142): "USSR plays Duck and Cover"(无句号)
                played_after_discard = card_display(act)
                step_lines.append(
                    f'{r.side} plays {played_after_discard}')
            elif 'randomly selects a card from USSR' in p:
                # Grain Sales 事件: 真实格式(对局记录 3247482 行 448-449)为
                # 揭示两行 "USSR reveals X" + "USSR reveals X from hand"
                grain_card = card_display(act)
                step_lines.append(f'USSR reveals {grain_card}')
                step_lines.append(f'USSR reveals {grain_card} from hand')
            elif 'discard' in p.lower():
                # 弃牌流(Blockade/Our Man/KAL-007/Aldrich Ames/随机弃牌等):
                # 真实日志只显示 "{side} discards X",无 "selects" 行
                # (3305175 行 317 Blockade 段);弃牌差行由 _diff_lines 输出
                pass
            else:
                step_lines.append(f'{r.side} selects {card_display(act).rstrip(".")}.')

        elif st == 'SELECT_CARD_ACTION':
            mode = act
            src = str(r.context.get('source_card', ''))
            if src and src != card_name:
                card_name = src
            if header_emitted:
                # 同一行动段内的第二次行动选择(事件化后使用 ops / UN 介入的
                # 后续行动):真实格式为无 Turn/AR 前缀的子标题行
                # (如 "Coup (3 Ops):"),与上一段以空行分隔。
                label = {'INFLUENCE': 'Place Influence', 'COUP': 'Coup',
                         'REALIGNMENT': 'Realignment', 'SPACE': 'Space Race'}.get(mode, '')
                if label:
                    if mode == 'SPACE':
                        ops = _global_eff_ops(r.pre, side,
                                              Card.ALL[card_name].ops
                                              if card_name in Card.ALL else 0)
                    else:
                        ops = Card.ALL[card_name].ops if card_name in Card.ALL else 0
                    lines.append('')
                    lines.append(f'{label} ({ops} Ops):')
            if card_name in _WAR_FIXED:
                target, attacker, itself, lower, vp_w, mil_w = _WAR_FIXED[card_name]
                owner = Card.ALL[card_name].owner if card_name in Card.ALL else None
                # 事件模式,或对方以 ops 打我方战争牌(opp 事件自动结算)
                war_fires = mode in ('PLAY_EVENT', 'RESOLVE_EVENT_FIRST') \
                    or owner == side.opp
                if war_fires and (attacker == side or owner == side.opp):
                    pending_war = (target, attacker, itself, lower, vp_w, mil_w)
            if not header_emitted:
                emit_header(r.pre)

        elif st == 'SELECT_COUNTRY':
            if act not in CountryInfo.ALL:
                pass  # 'Stop realignments.' 等提前停止选项
            elif 'coup using operations from' in p:
                eff = _coup_eff_ops(r.pre, side, card_name, act)
                pending_coup = (act, eff)
                step_lines.append(f'Target: {country_display(act)}')
            elif 'realignment using operations from' in p:
                pending_realign = act
                step_lines.append(f'Target: {country_display(act)}')
            elif ('Choose target country' in p or 'Choose a target country' in p
                  or 'Choose target of war' in p):
                params = _WAR_SELECT.get(card_name, (4, 2, 2))
                pending_war = (act, side, False, *params)
            # 影响力放置等其余选国:差行承载,不另出行

        elif st == 'ROLL_DICE':
            if p == '1d6 roll':
                die = int(act)
                if pending_coup is not None:
                    country, eff = pending_coup
                    info = CountryInfo.ALL.get(country)
                    stab = info.stability if info else 0
                    modifier = _coup_modifier(r.pre, side, country)
                    diff = die + eff + modifier - 2 * stab
                    outcome = 'SUCCESS' if diff > 0 else 'FAILURE'
                    if modifier:
                        # 真实格式(3318288 行 606/616): 修正段 (-1) 后双空格
                        step_lines.append(
                            f'{outcome}: {die} [ + {eff} ({modifier:+d})'
                            f'  - 2x{stab} = {diff} ]')
                    else:
                        step_lines.append(
                            f'{outcome}: {die} [ + {eff} - 2x{stab} = {diff} ]')
                    pending_coup = None
                elif pending_war is not None:
                    target, attacker, itself, lower, vp_w, mil_w = pending_war
                    modifier = _war_modifier(r.pre, target, attacker.opp, itself)
                    total = die - modifier
                    outcome = 'VICTORY' if total >= lower else 'DEFEAT'
                    cmp = '>=' if outcome == 'VICTORY' else '<'
                    step_lines.append(f'War in {country_display(target)}')
                    if modifier:
                        # 真实格式: "VICTORY: 6 (-2)  >= 4"（mod=0 省略括号段,单空格）
                        step_lines.append(
                            f'{outcome}: {die} (-{modifier})  {cmp} {lower}')
                    else:
                        step_lines.append(f'{outcome}: {die} {cmp} {lower}')
                    pending_war = None
                elif mode == 'SPACE':
                    needed = Game.Default.SPACE_ROLL_MAX[r.pre.space[side]]
                    ok = die <= needed
                    step_lines.append(
                        f'Die roll: {die} -- {"Success!" if ok else "Failed!"} '
                        f'(Needed {needed} or less)')
                elif pending_qbt_trap:
                    # 真实格式(3325831 行 330/544, 游戏本体字符串):
                    # "Trap Roll: 2 <= 4 -- Trap Escaped" / "> 4 -- Trap Remains in Effect"
                    if die <= 4:
                        step_lines.append(
                            f'Trap Roll: {die} <= 4 -- Trap Escaped')
                    else:
                        step_lines.append(
                            f'Trap Roll: {die} > 4 -- Trap Remains in Effect')
                else:
                    step_lines.append(f'Die roll: {die}.')
            elif p == '2d6 roll (Sponsor roll, Participant roll), no ties':
                a, b = _parse_dice(act)
                step_lines.append(f'Reroll: {a} {b}')
            else:  # 2d6 roll (USSR roll, US roll)
                a, b = _parse_dice(act)
                if pending_realign is not None:
                    # 真实格式(村夫谱 行 362-363/504-505): 每方各自修正,
                    # 修正仅在 >0(或 Iran Contra 的 -1)时显示,无句号
                    ussr_mod, us_mod = _realign_modifiers(
                        r.pre, pending_realign)
                    if ussr_mod:
                        step_lines.append(
                            f'USSR rolls {a} ({ussr_mod:+d}) = {a + ussr_mod}')
                    else:
                        step_lines.append(f'USSR rolls {a}')
                    if us_mod:
                        step_lines.append(
                            f'US rolls {b} ({us_mod:+d}) = {b + us_mod}')
                    else:
                        step_lines.append(f'US rolls {b}')
                    pending_realign = None
                else:
                    step_lines.append(f'USSR rolls {a}')
                    step_lines.append(f'US rolls {b}')

        elif st == 'SELECT_MULTIPLE':
            if act == 'Return card to USSR' and grain_card:
                # Grain Sales 返还: 真实格式(对局记录 3247482 行 450)
                # "US returns X to USSR"; 随后 Grain Sales 自身 ops 以子标题行渲染
                step_lines.append(f'{r.side} returns {grain_card} to USSR')
            elif act in ('Use card normally', 'Use card with UN Intervention'):
                pass  # 所选牌由后续子标题行(ops/事件)承载, 无泛化 chooses 行
            elif re.match(r'^DEFCON [1-5]($|:)', act):
                # How I Learned To Stop Worrying 的 DEFCON 选择: 真实日志
                # 只显示 "DEFCON degrades to N" (3305175 行 464-474), 无内嵌行
                pass
            else:
                step_lines.append(f'{r.side} chooses {act.rstrip(".")}.')

        lines.extend(step_lines)
        # step diff 同样过滤"本块刚打出的牌被常规弃置"(如 UN 打出后
        # UN Intervention 进弃牌堆的行;真实日志不显示)。
        lines.extend(_filter_routine_discards(
            _diff_lines(r.pre, r.post), card_name))
        if played_after_discard:
            # UN 被选牌(打断后使用并弃置):真实格式只保留 "{side} plays X",
            # 弃置行不显示(3305175 行 142 附近无 "USSR discards Duck and Cover")
            _drop_played_after_discard(lines, played_after_discard)

        # 步间间隙(同一 recv 外的阶段效应一般不在步间,防御性渲染)。
        # 回合末 gap 可能整个落在步间(shuffle 输入行把跨回合段切成两半)。
        if i + 1 < len(block):
            seg_pre, seg_post = r.post, block[i + 1].pre
            if seg_pre != seg_post:
                seg_lines = _filter_routine_discards(
                    _diff_lines(seg_pre, seg_post), card_name)
                if played_after_discard:
                    _drop_played_after_discard(seg_lines, played_after_discard)
                if seg_post.turn > seg_pre.turn:
                    _route_turn_gap(seg_pre, seg_post, seg_lines,
                                    out_defcon, out_cleanup)
                else:
                    lines.extend(seg_lines)

    # -- 块末事件段:锚点 = 块终止行之后的"行动后触发"事件(如 C5 展示手牌 /
    # U2 Incident / 对方牌 ops 打出的敌事件)。真实格式: 独立段,段前空行;
    # 事件效果差行由块末对账 gap 承载(3305175 行 382-386)。
    while block_events:
        ev_card, ev_side, ev_pre, _ = block_events.pop(0)
        if kind == 'ar' and mode in ('PLAY_EVENT', 'RESOLVE_EVENT_FIRST') \
                and ev_card == card_name:
            lines.extend(_reveal_lines(ev_card, ev_pre))
        else:
            lines.append('')
            lines.append(f'Event: {card_display(ev_card)}')
            lines.extend(_reveal_lines(ev_card, ev_pre))

    # -- 块末对账:最后一步 post → 下一块 pre(事件结算/回合清理的无输入间隙) --
    gap_pre = block[-1].post
    gap_post = next_pre
    if gap_post is not None and gap_pre != gap_post:
        scoring = bool(card_name and card_name in Card.ALL
                       and Card.ALL[card_name].scoring_region)
        gap_lines = _filter_routine_discards(
            _diff_lines(gap_pre, gap_post), block_card or card_name)
        if played_after_discard:
            _drop_played_after_discard(gap_lines, played_after_discard)
        if gap_post.turn > gap_pre.turn:
            _route_turn_gap(gap_pre, gap_post, gap_lines,
                            out_defcon, out_cleanup)
        else:
            if scoring and gap_post.vp == gap_pre.vp and not no_vp_emitted:
                # 计分牌净 0 分:人类日志会显式写 "No VP awarded. Score is X."
                if not any('Score is' in ln for ln in gap_lines):
                    gap_lines.insert(
                        0, f'No VP awarded. {_score_line(gap_post.vp)}')
                    no_vp_emitted = True
            lines.extend(gap_lines)

    return '\n'.join(lines), out_defcon, out_reshuffle, out_cleanup


def _filter_routine_discards(lines: List[str], card_name: str) -> List[str]:
    """过滤"本块刚打出的牌被常规弃置"的噪音行(人类日志不打印常规弃牌);
    保留 QBT/UN Intervention 等有信息量的弃牌。"""
    if not card_name:
        return lines
    disp = card_display(card_name)
    noisy = {f'USSR discards {disp}', f'US discards {disp}'}
    return [ln for ln in lines if ln not in noisy]


def _drop_played_after_discard(lines: List[str], disp: str) -> None:
    """从行列表中就地移除 UN 被选牌的弃置行(真实格式不显示)。"""
    for noisy in (f'USSR discards {disp}', f'US discards {disp}'):
        while noisy in lines:
            lines.remove(noisy)


def _route_turn_gap(pre: StateSnapshot, post: StateSnapshot,
                    gap_lines: List[str],
                    out_defcon: List[str],
                    out_cleanup: List[str]) -> None:
    """跨回合 gap(回合末清理):按真实格式路由。

    - "DEFCON improves to N" 行:回合并头自动恢复,延迟到下一块 headline 标题
      行尾(真实: "Turn 3, Headline Phase: A & B: DEFCON improves to 3")。
    - 其余行:独立 "Turn N, Cleanup" 块(turn 号按前置回合;Playdek 客户端
      存在恒显 7/5/4 的不一致显示,以真实回合为准)。
    无内容也输出标题行(见 3325831 行 110 / 村夫谱行 300)。
    """
    keep = [ln for ln in gap_lines if not ln.startswith('DEFCON improves')]
    out_defcon.extend(ln for ln in gap_lines
                      if ln.startswith('DEFCON improves'))
    title = f'Turn {pre.turn}, Cleanup'
    if keep:
        title += f': {keep[0]}'
    out_cleanup.append(title)
    out_cleanup.extend(keep[1:])


def _parse_dice(act: str) -> Tuple[int, int]:
    """解析 2d6 输入的 '(a, b)' 元组字符串。"""
    try:
        return eval(act)  # 引擎选项本身是元组 (a, b),repr 后回解析安全
    except Exception:
        return (0, 0)


# ---------------------------------------------------------------------------
# 记录器
# ---------------------------------------------------------------------------
class GameRecorder:
    """统一棋谱记录器；并行实例按当前 ``input_state`` 身份隔离。"""

    def __init__(self, game_provider: Callable[[], Game],
                 ussr_name: str = 'USSR', us_name: str = 'US',
                 scenario: str = 'Standard',
                 time_per_player: str = '90 Minutes'):
        self._game_provider = game_provider
        self.ussr_name = ussr_name
        self.us_name = us_name
        self.scenario = scenario
        self.time_per_player = time_per_player
        self._rows: List[StepRecord] = []
        # 头条事件段:(card_name, 事件前快照, 事件结算后快照, 捕获时刻的行号)。
        # 行号将 section 锚定到 rows 序列:即使头条事件内含交互行(事件内
        # 选国/选牌),也能把交互行与事件段对应起来。
        self._sections: List[Tuple[str, StateSnapshot, StateSnapshot, int]] = []
        # 事件化触发:(card_name, side, 事件前快照, 捕获时刻的行号)。
        # 覆盖头条段之外的事件化(敌牌行动后自动触发,如 CIA Created /
        # Five Year Plan):渲染时输出 "Event: X" 段标题与 reveal 行。
        self._events: List[Tuple[str, str, StateSnapshot, int]] = []
        self._paused = False
        self._commit_idx = 0        # mark() 之前的行不可回滚
        self._rendered_upto = -1    # render_new 已输出的行索引
        self._termination_emitted = False
        self._orig_dispose = None
        self._orig_trigger = None

    # -- 生命周期 -----------------------------------------------------------
    def start(self):
        with _ACTIVE_LOCK:
            if self not in _ACTIVE:
                _ACTIVE.append(self)
            Input.recv = _probe_recv
            if self._orig_dispose is None:
                game = self._game_provider()
                if game is not None:
                    # 头条事件段分割:每个头条事件的 dispose_headline 结束后
                    # 拍快照(事件全部效果已结算),供渲染拆成 "Event: X" 段。
                    # 每个活跃 recorder 记录自己的行号锚点。
                    orig = game.dispose_headline

                    def _wrapped(side):
                        card_name = game.headline_bin[side]
                        pre_snap = StateSnapshot.snapshot(game)
                        orig(side)
                        if card_name:
                            snap = StateSnapshot.snapshot(game)
                            for rec in list(_ACTIVE):
                                rec._sections.append(
                                    (card_name, pre_snap, snap, len(rec._rows)))
                    self._orig_dispose = orig
                    game.dispose_headline = _wrapped
                    # 事件化触发(头条之外;头条由 dispose 钩子经 sections 覆盖):
                    # 触发前拍快照 → reveal 行重建与 "Event: X" 段定位。
                    orig_trigger = game.trigger_event

                    def _trigger_wrapped(side, card_name):
                        pre = StateSnapshot.snapshot(game)
                        orig_trigger(side, card_name)
                        for rec in list(_ACTIVE):
                            rec._events.append(
                                (card_name, side.name if hasattr(side, 'name')
                                 else str(side), pre, len(rec._rows)))
                    self._orig_trigger = orig_trigger
                    game.trigger_event = _trigger_wrapped

    def stop(self):
        with _ACTIVE_LOCK:
            if self in _ACTIVE:
                _ACTIVE.remove(self)
            if self._orig_dispose is not None:
                game = self._game_provider()
                if game is not None:
                    game.dispose_headline = self._orig_dispose
                    if self._orig_trigger is not None:
                        game.trigger_event = self._orig_trigger
                self._orig_dispose = None
                self._orig_trigger = None
            if not _ACTIVE:
                Input.recv = _ORIG_RECV

    # -- UI 流控 -------------------------------------------------------------
    def mark(self):
        """commit 点:此前记录的行不可回滚。"""
        self._commit_idx = len(self._rows)

    def rollback(self):
        """revert:丢弃上次 mark 之后的行(与 UI temp_log.clear 同步)。"""
        self._rows = self._rows[:self._commit_idx]
        self._rendered_upto = min(self._rendered_upto, len(self._rows) - 1)

    def pause(self):
        self._paused = True

    def resume(self):
        self._paused = False

    # -- 输出 ---------------------------------------------------------------
    def _sections_for(self, s: int, e: int) -> List[Tuple[str, StateSnapshot, StateSnapshot, int]]:
        """块 rows[s:e) 对应的事件段(anchor 落于 (s, e] 区间)。

        事件段为 4 元组 (card_name, 事件前快照, 事件后快照, 捕获行号)。
        """
        return [sec for sec in self._sections if s < sec[3] <= e]

    def _events_for(self, s: int, e: int) -> List[Tuple[str, str, StateSnapshot, int]]:
        """块 rows[s:e) 对应的事件化触发(anchor 落于 (s, e] 区间)。"""
        return [ev for ev in self._events if s < ev[3] <= e]

    def render_new(self) -> str:
        """增量输出新关闭的块(流式写文件用,崩溃安全)。"""
        rows = self._rows
        starts = _block_starts(rows)
        closed = [(starts[i], starts[i + 1]) for i in range(len(starts) - 1)]
        parts: List[str] = []
        prev_defcon: List[str] = []
        prev_reshuffle = False
        for s, e in closed:
            if e - 1 <= self._rendered_upto:
                continue
            text, out_defcon, out_reshuffle, out_cleanup = _render_block(
                rows, s, e, next_pre=rows[e].pre, rec=self,
                sections=self._sections_for(s, e),
                prev_defcon=prev_defcon.pop(0) if prev_defcon else '',
                prev_reshuffle=prev_reshuffle)
            prev_defcon.extend(out_defcon)
            prev_reshuffle = out_reshuffle
            parts.append(text)
            if out_cleanup:
                parts.append('\n'.join(out_cleanup))
            self._rendered_upto = e - 1
        if parts:
            return '\n\n'.join(parts) + '\n\n'
        return ''

    def render_all(self) -> str:
        """一次性完整输出(含未关闭块与终局行)。"""
        rows = self._rows
        starts = _block_starts(rows)
        parts: List[str] = []
        prev_defcon: List[str] = []
        prev_reshuffle = False
        if starts:
            closed = [(starts[i], starts[i + 1]) for i in range(len(starts) - 1)]
            for s, e in closed:
                text, out_defcon, out_reshuffle, out_cleanup = _render_block(
                    rows, s, e, next_pre=rows[e].pre, rec=self,
                    sections=self._sections_for(s, e),
                    events=self._events_for(s, e),
                    prev_defcon=prev_defcon.pop(0) if prev_defcon else '',
                    prev_reshuffle=prev_reshuffle)
                prev_defcon.extend(out_defcon)
                prev_reshuffle = out_reshuffle
                parts.append(text)
                if out_cleanup:
                    parts.append('\n'.join(out_cleanup))
            # 未关闭的尾块:以活动 game 快照作块末对账(捕获最后一次输入之后的
            # 阶段效应,如记分结算/回合清理)
            tail, _, _, out_cleanup = _render_block(
                rows, starts[-1], len(rows),
                next_pre=StateSnapshot.snapshot(self._game_provider()),
                rec=self,
                sections=self._sections_for(starts[-1], len(rows)),
                events=self._events_for(starts[-1], len(rows)),
                prev_defcon=prev_defcon.pop(0) if prev_defcon else '',
                prev_reshuffle=prev_reshuffle)
            if tail:
                parts.append(tail)
            if out_cleanup:
                parts.append('\n'.join(out_cleanup))
        text = '\n\n'.join(parts)
        term = self._termination_text()
        if term:
            text = f'{text}\n\n{term}' if text else term
        return text

    def finish(self) -> str:
        """render_new() + 未关闭尾块 + 终局行(幂等,终局行只发一次)。"""
        new = self.render_new()
        if self._rendered_upto < len(self._rows) - 1:
            rows = self._rows
            starts = _block_starts(rows)
            if starts and starts[-1] > self._rendered_upto:
                tail, _, _, out_cleanup = _render_block(rows, starts[-1], len(rows),
                                        next_pre=StateSnapshot.snapshot(self._game_provider()),
                                        rec=self,
                                        sections=self._sections_for(starts[-1], len(rows)),
                                        events=self._events_for(starts[-1], len(rows)))
                if tail:
                    new = f'{new}{tail}\n\n'
                if out_cleanup:
                    new = f'{new}\n'.join(out_cleanup) + '\n\n'
                self._rendered_upto = len(rows) - 1
        term = self._termination_line()
        if term:
            new = f'{new}{term}\n\n' if new else f'{term}\n\n'
        return new

    def _termination_line(self) -> str:
        if self._termination_emitted:
            return ''
        text = self._termination_text()
        if text:
            self._termination_emitted = True
        return text

    def _termination_text(self) -> str:
        """Return the terminal line without mutating streaming output state.

        真实格式(Playdek GameLogWriter.cs WriteGameOver): "{winner} wins by
        {type}"（无句号,type 为 GameOverType 显示名）。映射:
        DEFCON / Victory Points / Europe Control / Final Scoring /
        Held Scoring Card / Cuban Missile Crisis / WarGames / Forfeit。
        """
        game = self._game_provider()
        if not game.terminated:
            return ''
        winner = getattr(game, 'termination_winner', Side.NEUTRAL)
        reason = getattr(game, 'termination_reason', '') or 'unknown'
        if winner in (Side.USSR, Side.US):
            type_map = {
                'thermonuclear_war': 'DEFCON',
                'vp_autovictory': 'Victory Points',
                'wargames': 'WarGames',
                'held_scoring_card': 'Held Scoring Card',
                'final_scoring_complete': 'Final Scoring',
                'europe_control': 'Europe Control',
                'deck_exhausted': 'Forfeit',
            }
            type_str = type_map.get(reason, reason.replace('_', ' ').title())
            return f'{winner.name} wins by {type_str}'
        return 'Draw.'
