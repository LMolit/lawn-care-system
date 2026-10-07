from typing import Annotated

from pydantic import AfterValidator, StringConstraints


def _clean(value: str) -> str:
    # Drop null bytes and other control characters, but keep tabs and newlines
    return "".join(ch for ch in value if ch in "\t\n" or ord(ch) >= 32)


def _text(max_length: int):
    return Annotated[
        str,
        StringConstraints(strip_whitespace=True, max_length=max_length),
        AfterValidator(_clean),
    ]


ShortText = _text(200)  # names, addresses, titles
LongText = _text(2000)  # messages, comments, notes
