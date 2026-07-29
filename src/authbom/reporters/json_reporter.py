from __future__ import annotations

import json
from typing import Any


def render(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=False) + "\n"
