from urllib import parse


def api_bool(value: bool) -> str:
    """
    turns a python bool into a bool-string that the api understands (lowercase)
    """
    return str(value).lower()


def urljoin(url: str, api: str) -> str:
    """
    wrapper for urllib.parse.urljoin
    it appends the api to the given url, also if the api starts with a / or the url does not end with a /
    These were two edge-cases that lead to wrong urls
    :param url:
    :param api:
    :return:
    """
    if not url.endswith("/"):
        url += "/"
    while api.startswith("/"):
        api = api[1:]
    return parse.urljoin(url, api)


def strings_from_dict(source: dict) -> list[tuple[str, str]]:
    result: list[tuple[str, str]] = []
    for key in source.keys():
        entry = source[key]
        if entry is None:
            continue
        if isinstance(entry, str):
            result.append((key, entry))
        if isinstance(entry, list):
            if len(entry) == 0:
                continue
            for link in entry:
                result.append((key, link))
        if isinstance(entry, dict):
            result.extend(strings_from_dict(entry))
    return result
