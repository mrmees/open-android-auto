from __future__ import annotations


_DHU_DIRECTION = {"dhu": "in", "phone": "out"}


def normalize_dhu_direction(raw: str) -> str:
    """Convert DHU's `dhu`/`phone` direction labels to the phone-relative
    `in`/`out` convention used everywhere else in the parser.

    DHU labels things from the DHU's point of view (`dhu` = HU side, `phone`
    = phone side). The unified parser uses phone-relative labels:
    `in` = HU→phone, `out` = phone→HU. So `dhu` → `in`, `phone` → `out`.
    """
    if raw not in _DHU_DIRECTION:
        raise ValueError(f"unknown DHU direction: {raw!r}")
    return _DHU_DIRECTION[raw]
