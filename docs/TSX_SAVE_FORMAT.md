# TSX 存档与可玩场景格式

TSX（TS Espionnage eXtension）是在标准 TS Espionnage 文本末尾追加的可选、可编辑存档块。
目标是让同一文件同时满足三类用途：

- 旧工具继续把它当作普通 Espionnage 棋谱解析；
- 新播放器可以恢复精确的当前版图、轨道和牌堆，用于复盘、剧本展示和调试；
- 选择保存随机种子时，引擎可以按动作序列确定性重放到存档点。

v1 复盘存档实现在 `ts_save.py`；v2 可玩场景实现在 `ts_scenario.py`。

## 网页导出

在人机或观战页面点击顶栏“存档”。两个选项彼此独立：

| 随机种子 | 双方手牌 | 文件内容与能力 |
| --- | --- | --- |
| 否 | 否 | 纯 TS Espionnage，正文逐字不变，不追加 TSX 块 |
| 是 | 否 | 当前公开局面 + seed + 玩家动作，可确定性重放；seed 可以推导私有信息 |
| 否 | 是 | 当前局面 + 双方手牌及未揭示头条，适合私有复盘/剧本展示 |
| 是 | 是 | 完整扩展：确定性重放 + 显式双方手牌 |

下载扩展名为 `.tsg`。文件可以直接拖入仓库根目录的
`ts-espionnage-viewer.html` 离线查看。

## 文本结构

标准棋谱始终位于文件开头。扩展是注释化的可读 JSON：

```text
SETUP: USSR will play as USSR.
US will play as USA.

Turn 1, USSR AR1: COMECON*: Place Influence (3 Ops):
...

# TSX-BEGIN v1
# TSX-DATA
# {
#   "capabilities": {
#     "deterministic_replay": true,
#     "engine_resume": false,
#     "private_hands": true,
#     "private_state_derivable_from_seed": true
#   },
#   "format": "ts-espionnage-save",
#   "position": { ... },
#   "replay": {
#     "actions": ["Poland", "NATO", "PLAY_EVENT"],
#     "seed": 12345
#   },
#   "version": 1
# }
# TSX-END
```

每行 JSON 前的 `#` 加空格前缀使旧文本工具可以忽略扩展，同时便于人工编辑。
解析器也兼容早期 v1 的单行 `# TSX-DATA {...}` 表示。

## `position` 字段

主要字段如下：

| 字段 | 含义 |
| --- | --- |
| `turn`, `ar`, `ar_side` | 当前回合、行动轮和行动方 |
| `vp`, `defcon`, `milops`, `space`, `spaced_turns` | 各公开轨道 |
| `ars_by_turn` | 双方各回合行动轮上限，供 fork 精确恢复北海石油/太空奖励 |
| `map` | 非零影响力国家；值顺序固定为 `[USSR, US]` |
| `discard`, `removed`, `basket`, `limbo` | 公开牌区和持续效果 |
| `draw_count` | 抽牌堆数量，不保存未知牌序 |
| `input` | 当前决策类型、提示、次数及合法选项 |
| `hands` | 可选；`USSR`、`US` 双方手牌 |
| `headline` | 可选；与私有手牌一起保存的未揭示头条槽 |
| `card_state` | 可选私有实例状态，目前含中国牌正反面和 Missile Envy exchange |
| `terminated`, `termination_*` | 是否终局及终局信息 |

未选择“双方手牌”时：

- `hands` 与 `headline` 不写入；
- 当前输入若为选牌，合法牌名也会被隐去；
- 公开弃牌、移除区、持续效果和抽牌堆数量仍会写入。

## 两种恢复语义

### 局面/剧本恢复

播放器读取 `position`，将最后一步覆盖为存档时的精确局面。人工修改 `position`
可以摆出特定版图、轨道、牌堆和双方手牌，用于展示、复盘或调试。

这是一份结构化局面快照，不包含 Python callback、阶段栈或模型上下文。因此 v1 的
`engine_resume` 固定为 `false`，人工编辑后的任意局面不能直接作为可继续对弈的引擎状态。

### 确定性引擎重放

选择随机种子后，`replay.seed` 和 `replay.actions` 可以从标准开局重放到存档点。
该路径恢复真实引擎阶段栈和随机结果，但要求代码版本与规则实现兼容。

```powershell
tools/ts -m hvs.launch --no-agent --no-human --no-spectate --replay-file path/to/save.tsg
```

如果人工修改了 `position`，只会改变播放器展示；引擎重放仍以 `seed + actions` 为准。

## 兼容性与隐私

- 两个选项均关闭时，`build_save_text()` 直接返回原始 Espionnage 文本，不增删字符。
- `rl.replay_parser.parse_espionnage` 对扩展文件产生与纯正文相同的训练决策序列。
- `hvs.espionnage.parse_log` 会识别 TSX，并用精确 `position` 覆盖最后局面。
- 自包含播放器同时支持 `.txt` 与 `.tsg`。
- seed 加动作足以重建发牌和随机选择，因此即使没有显式 `hands`，私有信息仍可被推导。
- 含双方手牌或 seed 的文件不应作为公开观战棋谱分发。

## v2 可玩场景

v2 与 v1 是两个明确分开的用途：v1 保留一盘实际发生过的棋；v2 描述一个经过
严格验证、可以从稳定阶段入口继续运行的人工局面。v2 文件以 `.tsx` 为扩展名：

```text
# TSX-BEGIN v2
# TSX-DATA
# {
#   "format": "ts-playable-scenario",
#   "version": 2,
#   "metadata": {"title": "Romania exercise"},
#   "entry": {"type": "AR_CARD_SELECT", "side": "USSR"},
#   "play": {"human_side": "USSR"},
#   "state": { ... },
#   "rng": {"seed": 20260827}
# }
# TSX-END
```

### 稳定入口

v2 不序列化任意 Python callback 或 `partial`。它只允许两个可重建入口：

- `AR_CARD_SELECT`：指定一方在某行动轮开始选牌；会重新接入困境、捕熊陷阱、
  古巴导弹危机等行动轮前置规则。
- `HEADLINE_START`：从双方尚未选择头条的阶段开始。

这两个入口覆盖定式、残局推演、特定手牌测试和大多数规则调试，同时避免加载后
下一步才因失效的调用栈崩溃。

### 可编辑状态

v2 保存并验证：

- 84 个非超级大国的双方影响力；
- VP、DEFCON、军备、太空、回合、行动轮与行动方；
- 双方手牌、精确抽牌顺序、弃牌、移除、limbo 和三个时代的未入牌堆储备；
- 每张实体牌恰好位于一个物理区域；
- 双方持续效果、本回合到期效果及受支持的卡牌实例状态；
- 环境和服务端的精确 RNG 状态，或一个便于编写的随机种子。

未知国家、重复/缺失实体牌、非法持续效果、DEFCON 1、超出行动轮范围或无法抵达
非空玩家决策的场景会被拒绝。加载先在隔离环境完成，验证成功后才原子替换当前局。

### 人机与模型推演

同一个 v2 文件可用于两种模式：

```powershell
# 人类 vs 模型；play.human_side 必须存在
tools/ts -m hvs.launch --scenario-file path/to/exercise.tsx --no-spectate --no-replay

# 模型 vs 模型推演；play.human_side 可省略并会被忽略
tools/ts -m hvs.launch --scenario-file path/to/exercise.tsx --no-human --no-replay

# 同时启动人机页与观战推演页，二者从同一局面各自运行
tools/ts -m hvs.launch --scenario-file path/to/exercise.tsx --no-replay
```

在 spectate 模式中，双方按照该服务器配置的本地模型、随机代理或外部代理自动行动；
`--external-side` 仍控制外部代理接管哪一方。场景中的 `play.human_side` 只供 human
模式使用，不改变模型推演的行动归属。

### 超级模式编辑器

```powershell
# 同时在人机页和观战页启用结构化场景编辑器
tools/ts -m hvs.launch --super-mode --no-replay

# 只启动模型推演编辑器
tools/ts -m hvs.launch --super-mode --no-human --no-replay
```

编辑器可以调整轨道、84 国影响力、双方手牌、全部实体牌区域与顺序、持续效果、
入口和随机种子，然后下载或立即载入。观战页载入后双方模型自动继续。模型运行中
若恰逢事件或未结算头条，编辑器使用最近一个稳定的头条/行动轮边界作为模板。

超级模式只能绑定回环地址、要求同源请求和会话令牌；不要通过端口转发暴露它。
v2 文件本身仍是不受信任输入，服务端会执行同一套严格验证。

### 从 v1 残局 fork

带双方手牌的 v1 存档可转换为自由演化的 v2 支线。已知局面保持一致，未来牌堆顺序
和骰子按新的 fork seed 随机化：

```powershell
tools/ts -m hvs.fork_from_save path/to/save.tsg --seed 20260828
tools/ts -m hvs.launch --scenario-file path/to/save.fork.tsx --no-replay
```

转换器只接受 `AR_CARD_SELECT` 或双方尚未选牌的 `HEADLINE_START` 稳定边界，并严格
检查双方手牌、弃牌、移除、limbo 与未知牌池。basket 仅作为效果 token 恢复，不计入
实体牌唯一性。无双方手牌、事件处理中途、重复实体牌、抽牌数量对账失败或终局存档
都会拒绝。详细契约见 [FORK_FROM_SAVE_PLAN_20260827.md](FORK_FROM_SAVE_PLAN_20260827.md)。

HVS 使用 `--save-dir` 时，每步原子更新 `<mode>_running.tsg`。新局启动若发现上一
进程留下的 running 镜像，会先改名为 `<mode>_interrupted_<timestamp>.tsg`，不会
覆盖或删除；终局正式 JSON+Espionnage 文件写成功后才清除当前 running 镜像。
