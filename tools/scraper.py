from typing import Callable, TypeVar, Generic, List
from bs4 import BeautifulSoup, Tag
import requests

T = TypeVar("T")


def fetch(url: str = "") -> str:
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    return r.text


def parse(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "html.parser")


def extract(url: str, fn: Callable[[BeautifulSoup], T]) -> T:
    html = fetch(url)
    soup = parse(html)
    return fn(soup)


def extract_many(
    path: str,
    selector: str,
    fn: Callable[[Tag], T]
) -> List[T]:
    html = fetch(path)
    soup = parse(html)
    return [fn(node) for node in soup.select(selector)]
