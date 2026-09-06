"""卡名 token 源码扫描校验。

引擎/卡牌/地图/UI 代码里所有"类卡名"字符串字面量必须存在于
Card.ALL（或显式白名单）——防止拼错卡名静默失效（basket 查询返回 False、
效果静默不触发）。历史上 test_cards 有 'effect_name' 拼错进 basket 的实证
（tests/test_cards.py 的 assert 'effect_name' not in game.basket）。
"""

import re
from pathlib import Path

from twilight_cards import CARD_NAMES
from twilight_map import CountryInfo

# "类卡名"形态: PascalCase 且含下划线（'The_China_Card'/'Cuban_Missile_Crisis'）。
# 国家名（'South_Korea' 等）由 CountryInfo.ALL 自动排除。
TOKEN_RE = re.compile(r"['\"]([A-Z][A-Za-z0-9]+_[A-Za-z0-9_]+)['\"]")

# 有意不是真实卡名的 basket 效果 token（Chernobyl 的区域限制假卡）。
KNOWN_FAKE_TOKENS = {
    "Chernobyl_Africa", "Chernobyl_Asia", "Chernobyl_Central_America",
    "Chernobyl_Europe", "Chernobyl_Middle_East", "Chernobyl_South_America",
}

SCANNED_FILES = [
    "game_mechanics.py",
    "twilight_cards.py",
    "twilight_map.py",
    "twilight_playerview.py",
    "twilight_ui.py",
]


def _unknown_tokens() -> set:
    card_names = CARD_NAMES
    country_names = set(CountryInfo.ALL)
    unknown = set()
    for fname in SCANNED_FILES:
        src = Path(fname).read_text(encoding="utf-8")
        for match in TOKEN_RE.finditer(src):
            token = match.group(1)
            if token in card_names or token in country_names:
                continue
            if token in KNOWN_FAKE_TOKENS:
                continue
            unknown.add(token)
    return unknown


def test_all_card_like_tokens_are_known():
    unknown = _unknown_tokens()
    assert not unknown, (
        "源码里有不在 Card.ALL 的'类卡名'字符串（可能拼错卡名静默失效）: "
        f"{sorted(unknown)}"
    )
