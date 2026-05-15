from typing import Any, Dict


def clear_output(data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        key: value
        for key, value in data.items()
        if not isinstance(value, (dict, list, set))
    }
