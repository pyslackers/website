from typing import Union


def formatted_number(value: Union[float, int]) -> str:
    return f"{value:,}"
