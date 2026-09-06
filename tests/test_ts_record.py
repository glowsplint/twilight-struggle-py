# -*- coding: utf-8 -*-
"""ts_record 统一棋谱记录器测试:round-trip、单块渲染、终局行、样本回归。"""

import json
import os
import re
import sys
from copy import deepcopy
from functools import partial
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from game_mechanics import Game
from twilight_cards import Card
from twilight_enums import InputType, Side
from twilight_input_output import Input
from ts_record import GameRecorder
from tests.helpers import make_game


def _advance(game):
    """驱动 stage 直到出现玩家输入(同 UI.advance_game 的核心循环)。"""
    while game.stage_list:
        game.stage_complete()
        if game.input_state:
            return


def _play_full_game(seed):
    """RuleBasedAgent 双席位打完整局,返回 (rendered_text, game, recorder)。"""
    # rl/ 未随本版本分发时跳过(本地完整仓库含 RL 环境)
    TwilightSelfPlayEnv = pytest.importorskip("rl.env").TwilightSelfPlayEnv
    RuleBasedAgent = pytest.importorskip("rl.agent").RuleBasedAgent

    env = TwilightSelfPlayEnv(seed=seed, suppress_output=True)
    game = env.reset()
    rec = GameRecorder(lambda: game)
    rec.start()
    try:
        ussr = RuleBasedAgent(seed=seed)
        us = RuleBasedAgent(seed=seed + 1000)
        while not env.done:
            legal = env.legal_actions()
            if not legal:
                env.advance()
                continue
            side = env.current_side
            agent = ussr if side == Side.USSR else us
            decision = agent.choose(game, game.input_state, legal, sample=False)
            env.step(decision.action)
        return rec.render_all(), game, rec
    finally:
        rec.stop()


# ---------------------------------------------------------------------------
# A. 整局 round-trip
# ---------------------------------------------------------------------------
class TestRoundTrip:
    def test_full_game_parses_with_espionnage_parser(self, tmp_path):
        text, game, _rec = _play_full_game(seed=7)
        assert 'wins by' in text or text.rstrip().endswith('Draw.')
        path = tmp_path / 'game.tsg'
        path.write_text(text, encoding='utf-8')

        parse_espionnage = pytest.importorskip("rl.replay_parser").parse_espionnage
        decisions = parse_espionnage(str(path))
        assert decisions, 'parsed decisions should be non-empty'
        assert any(d.phase == 'Headline' for d in decisions)
        assert any(d.phase == 'AR' for d in decisions)

        _norm_card_name = pytest.importorskip("rl.build_bc_dataset")._norm_card_name
        for d in decisions:
            assert d.turn >= 1
            assert d.side in ('USSR', 'US')
            assert d.action in ('event', 'influence', 'coup', 'realignment', 'space', '')
            if d.card:
                assert _norm_card_name(d.card) in Card.ALL, \
                    f'card {d.card!r} should normalize to a registered card'
        # 每个渲染出的 AR header 都必须被 parser 一一还原。对局可因
        # DEFCON/VP 在 T1 合法早终局，不能用固定最少行动数验证 parser。
        ar_decisions = [d for d in decisions if d.phase == 'AR']
        ar_headers = re.findall(
            r'^Turn \d+, (?:USSR|US) AR\d+:', text, re.MULTILINE)
        assert ar_headers
        assert len(ar_decisions) == len(ar_headers)

    def test_parser_keeps_empty_trap_ar_header(self, tmp_path):
        path = tmp_path / 'trap.tsg'
        path.write_text(
            'Turn 4, USSR AR2:\n'
            'USSR discards Red Scare Purge.\n'
            'Bear Trap roll: 4.\n'
            'US wins by final scoring.\n',
            encoding='utf-8',
        )

        parse_espionnage = pytest.importorskip("rl.replay_parser").parse_espionnage
        decisions = parse_espionnage(str(path))

        assert len(decisions) == 1
        assert decisions[0].phase == 'AR'
        assert decisions[0].side == 'USSR'
        assert decisions[0].turn == 4
        assert decisions[0].ar == 2
        assert decisions[0].card == ''
        assert decisions[0].action == ''

    def test_termination_line_across_seeds(self):
        _parse_winner = pytest.importorskip("rl.replay_dataset")._parse_winner
        for seed in (7, 8, 9, 10, 11, 12):
            text, _game, _rec = _play_full_game(seed=seed)
            winner = _parse_winner(text)
            assert winner != 'unknown', f'seed {seed}: {text[-120:]!r}'
            assert re.search(r'^(USSR|US) wins by .+$|^Draw\.?$',
                             text.strip().splitlines()[-1], re.M)


# ---------------------------------------------------------------------------
# B. 单块渲染(手工驱动完整 AR 流)
# ---------------------------------------------------------------------------
class TestBlockRendering:
    def _play_ar(self, card_name, action, targets, rolls):
        """驱动:select_card → select_action → 目标/骰子,返回渲染文本。"""
        game = make_game()
        game.hand[Side.USSR] = [card_name]
        rec = GameRecorder(lambda: game)
        rec.start()
        try:
            game.stage_list.append(partial(game.select_card, Side.USSR))
            _advance(game)
            game.input_state.recv(card_name)
            _advance(game)
            assert game.input_state.state == InputType.SELECT_CARD_ACTION
            game.input_state.recv(action)
            _advance(game)
            for tgt in targets:
                assert game.input_state is not None
                game.input_state.recv(tgt)
                _advance(game)
            for roll in rolls:
                assert game.input_state is not None
                game.input_state.recv(roll)
                _advance(game)
            return rec.render_all()
        finally:
            rec.stop()

    def test_coup_block(self):
        # COMECON 3op 政变 Iran(稳定 2),die=4 → diff=4+3-4=3 成功
        text = self._play_ar('COMECON', 'COUP', ['Iran'], ['4'])
        assert 'Turn 1, USSR AR1: COMECON*: Coup (3 Ops):' in text
        assert 'Target: Iran' in text
        assert 'SUCCESS: 4 [ + 3 - 2x2 = 3 ]' in text
        assert 'USSR Military Ops to 3' in text
        assert 'DEFCON degrades to 4' in text
        assert 'USSR +2 in Iran [0][2]' in text

    def test_space_block(self):
        # COMECON 太空:等级 0 需 ≤3,die=2 成功
        text = self._play_ar('COMECON', 'SPACE', [], ['2'])
        assert 'Turn 1, USSR AR1: COMECON*: Space Race (3 Ops):' in text
        assert 'Die roll: 2 -- Success! (Needed 3 or less)' in text
        assert 'USSR advances to 1 in the Space Race.' in text

    def test_war_block(self):
        # Korean War 事件:die=2,modifier=1(日本被美控)→ 1 < 4 失败,但 milops 照加
        text = self._play_ar('Korean_War', 'PLAY_EVENT', [], ['2'])
        assert 'Turn 1, USSR AR1: Korean War*: Event: Korean War*' in text
        assert 'War in South Korea' in text
        # 真实 Playdek 格式:骰子嵌入战争结果行,无独立 rolls 行
        assert 'DEFEAT: 2 (-1)  < 4' in text
        assert 'USSR Military Ops to 2' in text

    def test_realignment_block(self):
        # COMECON 调整 Iran(标准图美 1 点):2d6 (4, 2) —— 引擎 2d6 输入是元组
        # 真实 Playdek 格式(村夫谱 行 362-363): 每方显示各自修正,无句号
        text = self._play_ar('COMECON', 'REALIGNMENT', ['Iran'], [(4, 2)])
        assert 'Turn 1, USSR AR1: COMECON*: Realignment (3 Ops):' in text
        assert 'Target: Iran' in text
        assert 'USSR rolls 4' in text
        assert 'US rolls 2 (+1) = 3' in text

    def test_coup_block_with_lads_modifier(self):
        # LADS 在 US 场上 → USSR 政变修正 -1(真实格式 "(-1)" 段,见 3318288:606)
        game = make_game()
        game.map['Cuba'].influence[Side.US] = 2
        game.hand[Side.USSR] = ['COMECON']
        game.basket[Side.US].append('Latin_American_Death_Squads')
        game.ar_side = Side.USSR
        rec = GameRecorder(lambda: game)
        rec.start()
        try:
            game.stage_list.append(partial(game.select_card, Side.USSR))
            _advance(game)
            game.input_state.recv('COMECON')
            _advance(game)
            game.input_state.recv('COUP')
            _advance(game)
            game.input_state.recv('Cuba')
            _advance(game)
            game.input_state.recv('3')
            _advance(game)
            text = rec.render_all()
        finally:
            rec.stop()
        assert 'Target: Cuba' in text
        assert 'FAILURE: 3 [ + 3 (-1)  - 2x3 = -1 ]' in text

    def test_trap_block_not_escaped(self):
        # 骰子 >4 → "Trap Remains in Effect" 且陷阱保留
        game = make_game()
        game.hand[Side.US] = ['NATO']
        game.basket[Side.US].append('Quagmire')
        game.ar_side = Side.US
        rec = GameRecorder(lambda: game)
        rec.start()
        try:
            game.stage_list.append(partial(game.qbt_discard, Side.US, 'Quagmire'))
            _advance(game)
            game.input_state.recv('NATO')
            _advance(game)
            game.input_state.recv('5')
            text = rec.render_all()
        finally:
            rec.stop()
        assert 'Turn 1, US AR1: NATO*: US discards NATO*' in text
        assert 'Trap Roll: 5 > 4 -- Trap Remains in Effect' in text
        assert 'Quagmire* is no longer in play.' not in text

    def test_blockade_discard_has_no_selects_line(self):
        # Blockade 弃牌:真实日志只有 "US discards X"(3305175 行 317),无 selects
        game = make_game()
        game.hand[Side.USSR] = ['Blockade']
        game.hand[Side.US] = ['East_European_Unrest', 'NATO']
        game.ar_side = Side.USSR
        rec = GameRecorder(lambda: game)
        rec.start()
        try:
            game.stage_list.append(partial(game.select_card, Side.USSR))
            _advance(game)
            game.input_state.recv('Blockade')
            _advance(game)
            game.input_state.recv('PLAY_EVENT')
            _advance(game)
            assert game.input_state is not None
            game.input_state.recv('East_European_Unrest')
            _advance(game)
            text = rec.render_all()
        finally:
            rec.stop()
        assert 'Event: Blockade*' in text
        assert 'US discards East European Unrest' in text
        assert 'selects' not in text

    def test_grain_sales_event_uses_real_format(self):
        # Grain Sales 事件: 真实格式(对局记录 3247482 行 448-450):
        # "USSR reveals X" + "USSR reveals X from hand" + "US returns X to USSR"
        game = make_game()
        game.hand[Side.US] = ['Grain_Sales_to_Soviets']
        game.hand[Side.USSR] = ['Mideast_Scoring', 'NATO']
        game.ar_side = Side.US
        rec = GameRecorder(lambda: game)
        rec.start()
        try:
            game.stage_list.append(partial(game.select_card, Side.US))
            _advance(game)
            game.input_state.recv('Grain_Sales_to_Soviets')
            _advance(game)
            game.input_state.recv('PLAY_EVENT')
            _advance(game)
            assert game.input_state is not None
            game.input_state.recv('Mideast_Scoring')  # 随机挑选
            _advance(game)
            game.input_state.recv('Return card to USSR')
            _advance(game)
            text = rec.render_all()
        finally:
            rec.stop()
        assert 'USSR reveals Mideast Scoring' in text
        assert 'USSR reveals Mideast Scoring from hand' in text
        assert 'US returns Mideast Scoring to USSR' in text
        assert 'chooses' not in text

    def test_hlstsw_defcon_choice_has_no_chooses_line(self):
        # How I Learned:真实日志只有 DEFCON 差行(3305175 行 464-474)
        game = make_game()
        game.hand[Side.USSR] = ['How_I_Learned_to_Stop_Worrying']
        game.ar_side = Side.USSR
        rec = GameRecorder(lambda: game)
        rec.start()
        try:
            game.stage_list.append(partial(game.select_card, Side.USSR))
            _advance(game)
            game.input_state.recv('How_I_Learned_to_Stop_Worrying')
            _advance(game)
            game.input_state.recv('PLAY_EVENT')
            _advance(game)
            assert game.input_state is not None
            game.input_state.recv('DEFCON 4')
            _advance(game)
            text = rec.render_all()
        finally:
            rec.stop()
        assert 'chooses DEFCON' not in text
        assert 'DEFCON degrades to 4' in text  # make_game 默认 DEFCON 5

    def test_realign_modifiers_match_engine_net(self):
        # 每方修正净差与引擎 ussr_advantage 的行结果等价(规则书 6.2.2)
        for country, a, b in (('Iran', 4, 1), ('Iraq', 3, 2), ('Vietnam', 2, 2)):
            game = make_game()
            from ts_record import _realign_modifiers, StateSnapshot
            if country == 'Iran':
                game.map['Iran'].influence[Side.US] = 3
                game.map['Iraq'].influence[Side.USSR] = 3
            if country == 'Iraq':
                game.map['Iraq'].influence[Side.USSR] = 3
                game.map['Iraq'].influence[Side.US] = 2
            if country == 'Vietnam':
                game.map['Vietnam'].influence[Side.USSR] = 2
                game.map['Vietnam'].influence[Side.US] = 1
            snap = StateSnapshot.snapshot(game)
            m1, m2 = _realign_modifiers(snap, country)
            predicted = a + m1 - (b + m2)
            before = game.map[country].influence.copy()
            game.map.realignment(game, country, Side.USSR, a, b)
            after = game.map[country].influence
            if predicted > 0:
                assert before[1] - after[1] == predicted
                assert before[0] - after[0] == 0
            else:
                assert before[0] - after[0] == -predicted
                assert before[1] - after[1] == 0

    def test_scoring_block_emits_no_vp_awarded(self):
        # 记分牌净 0:清空地图势力后 Asia Scoring 得 0 分 → "No VP awarded."
        game = make_game()
        for country in game.map.ALL.values():
            country.influence[Side.USSR] = 0
            country.influence[Side.US] = 0
        game.hand[Side.USSR] = ['Asia_Scoring']
        rec = GameRecorder(lambda: game)
        rec.start()
        try:
            game.stage_list.append(partial(game.select_card, Side.USSR))
            _advance(game)
            game.input_state.recv('Asia_Scoring')
            # 记分结算在 stage 里,推进到下一输入(这里没有,手动触发结账)
            _advance(game)
            text = rec.render_all()
        finally:
            rec.stop()
        assert 'Turn 1, USSR AR1: Asia Scoring: Event: Asia Scoring' in text
        assert 'No VP awarded.' in text
        assert 'Score is even.' in text

    def test_qbt_block(self):
        # 美方受 Quagmire 影响:弃牌 + 骰子 ≤4 释放
        game = make_game()
        game.hand[Side.US] = ['NATO']
        game.basket[Side.US].append('Quagmire')
        game.ar_side = Side.US
        rec = GameRecorder(lambda: game)
        rec.start()
        try:
            game.stage_list.append(partial(game.qbt_discard, Side.US, 'Quagmire'))
            _advance(game)
            assert 'You must discard a card to be released.' in game.input_state.prompt
            game.input_state.recv('NATO')
            _advance(game)
            assert game.input_state.state == InputType.ROLL_DICE
            game.input_state.recv('3')
            text = rec.render_all()
        finally:
            rec.stop()
        # 真实 Playdek 格式(3325831 行 329-331): 头部合一 + Trap Roll 行
        assert 'Turn 1, US AR1: NATO*: US discards NATO*' in text
        assert 'Trap Roll: 3 <= 4 -- Trap Escaped' in text
        assert 'Quagmire* is no longer in play.' in text


def test_parallel_recorders_route_inputs_to_their_own_games():
    games = [make_game(), make_game()]
    recorders = [GameRecorder(lambda game=game: game) for game in games]
    try:
        for recorder in recorders:
            recorder.start()
        for game, country in zip(games, ("Poland", "Romania")):
            def accept(_country, current_game=game):
                current_game.input_state.reps -= 1
                return True

            game.input_state = Input(
                Side.USSR, InputType.SELECT_COUNTRY, accept, [country],
                prompt="Place starting influence.",
            )
            assert game.input_state.recv(country) is True

        assert recorders[0]._rows[0].action == "Poland"
        assert recorders[1]._rows[0].action == "Romania"
        assert len(recorders[0]._rows) == len(recorders[1]._rows) == 1
    finally:
        for recorder in recorders:
            recorder.stop()


def test_render_all_preview_does_not_consume_finish_termination_line():
    game = make_game()
    game.terminate(Side.USSR, reason="preview_test")
    recorder = GameRecorder(lambda: game)

    preview = recorder.render_all()
    finished = recorder.finish()

    # 真实 Playdek 格式: "{side} wins by {type}"(无句号,type 大写显示名)
    assert preview == "USSR wins by Preview Test"
    assert finished == "USSR wins by Preview Test\n\n"


# ---------------------------------------------------------------------------
# C. UI 接线:.tsg 人类棋谱 + .moves sidecar、commit/revert
# ---------------------------------------------------------------------------
class TestUiIntegration:
    def _new_logging_ui(self, tmp_path, auto_commit=True):
        from twilight_ui import UI
        ui = UI()
        ui.auto_rng = True
        ui.auto_commit = auto_commit
        ui.logging = True
        ui.new_game()
        # new_game 会生成 log/ 下的真实路径,这里改指 tmp(尚未写任何文件)
        ui.log_filepath = str(tmp_path / 'game-test.tsg')
        ui.moves_filepath = str(tmp_path / 'game-test.tsg.moves')
        ui.game_rollback = deepcopy(ui.game)
        ui.game_state_changed(prompt=False)
        return ui

    def _drive(self, ui, steps):
        for _ in range(steps):
            if ui.game.terminated:
                return
            inp = ui.game.input_state
            if inp.side == Side.NEUTRAL:
                ui.game_state_changed(prompt=False)  # auto_rng 喂骰/洗牌并推进
                continue
            opts = list(inp.legal_options)
            if not opts:
                ui.advance_game()
                continue
            ui.move(opts[0])
            ui.game_state_changed(prompt=False)

    def test_writes_human_record_and_moves_sidecar(self, tmp_path):
        ui = self._new_logging_ui(tmp_path)
        try:
            self._drive(ui, 40)
            ui.log_write_out()
            record = Path(ui.log_filepath).read_text(encoding='utf-8')
            assert 'SETUP: USSR will play as USSR.' in record
            assert 'Turn 1, Headline Phase:' in record
            moves = Path(ui.moves_filepath).read_text(encoding='utf-8')
            assert moves, 'sidecar 应有原始 move 行'
        finally:
            ui.log_finish_out()

    def test_commit_revert_rolls_back_recorder(self, tmp_path):
        ui = self._new_logging_ui(tmp_path, auto_commit=False)
        try:
            # 苏联 setup 全部 6 步(自动 commit 关 → 输入完成后出现 lookahead)
            for move in ['Poland'] * 4 + ['Finland', 'Austria']:
                ui.move(move)
            ui.game_state_changed(prompt=False)
            assert ui.awaiting_commit
            ui.commit()
            committed = list(ui.recorder._rows)
            sidecar_before = Path(ui.moves_filepath).read_text(encoding='utf-8')

            # 美方 setup 两步后 revert:行回滚、已写文件不回退
            ui.move('West_Germany')
            ui.move('France')
            ui.revert()
            assert ui.recorder._rows == committed
            assert Path(ui.moves_filepath).read_text(encoding='utf-8') == sidecar_before

            # 重走两步:记录器从 commit 点继续
            ui.move('West_Germany')
            ui.move('France')
            assert len(ui.recorder._rows) == len(committed) + 2
        finally:
            ui.log_finish_out()


# ---------------------------------------------------------------------------
# D. 人类样本回归(防止解析器被我们改坏)
# ---------------------------------------------------------------------------
class TestSampleRegression:
    def test_norm_of_truncated_client_card_name(self):
        # 客户端截断标题 '"Ask Not What Your Country..."' (419 局实测 64+ 次;
        # 别名必须含前引号, 缺引号曾导致 round-trip 偶发失败)
        _norm_card_name = pytest.importorskip("rl.build_bc_dataset")._norm_card_name
        assert _norm_card_name(
            '"Ask Not What Your Country..."*'
        ) == 'Ask_Not_What_Your_Country_Can_Do_For_You'

    def test_parse_espionnage_sample_still_parses(self):
        """人类样本回归:解析器输出与历史产物同量级、关键决策在。

        (注:data/parsed_replays 产物由旧版解析器生成,现版可多解析出若干
        decisions,故不做逐条相等比对,只锁结构与关键内容。)
        """
        parse_espionnage = pytest.importorskip("rl.replay_parser").parse_espionnage
        sample = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                              'data', 'txt_replay', 'TS_Espionnage_log', '3305175.txt')
        if not os.path.exists(sample):
            pytest.skip('human sample not present')
        decisions = parse_espionnage(sample)
        artifact = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                'data', 'parsed_replays', 'espionnage_3305175.json')
        if not os.path.exists(artifact):
            pytest.skip('parsed artifact not present')
        with open(artifact, encoding='utf-8') as f:
            records = json.load(f)
        # 同量级(旧产物 105 条,现解析器允许小幅增长,但不许大崩)
        assert len(decisions) >= len(records) - 5
        assert len(decisions) <= len(records) + 15
        # 头条对与已知 AR 决策
        headlines = [(d.side, d.card.rstrip('*')) for d in decisions if d.phase == 'Headline']
        assert ('USSR', 'De Gaulle Leads France') in headlines
        assert ('US', 'Asia Scoring') in headlines
        ar_keys = {(d.turn, d.ar, d.side, d.card.rstrip('*'), d.action, d.target)
                   for d in decisions if d.phase == 'AR'}
        assert (1, 1, 'USSR', 'COMECON', 'coup', 'Italy') in ar_keys
        assert (1, 1, 'US', 'East European Unrest', 'influence', '') in ar_keys
