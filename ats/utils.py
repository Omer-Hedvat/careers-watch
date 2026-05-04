HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}


def strip_html(text: str) -> str:
    import re
    return re.sub(r"<[^>]+>", " ", text).strip()
