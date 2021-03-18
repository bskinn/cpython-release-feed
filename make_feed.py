r"""*Module to generate CPython release RSS feed.*

**Author**
    Brian Skinn (bskinn@alum.mit.edu)

**File Created**
    25 Feb 2021

**Copyright**
    \(c) Brian Skinn 2021

**Source Repository**
    http://www.github.com/bskinn/cpython-release-feed

**Documentation**
    N/A

**License**
    The MIT License; see |license_txt|_ for full license terms

**Members**

"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Iterable

import arrow  # type: ignore
import attr
import bs4  # type: ignore
import requests as rq
from bs4 import BeautifulSoup as BSoup
from feedgen.feed import FeedGenerator  # type: ignore
from packaging.utils import canonicalize_version


STABLE_URL: str = "https://www.python.org/downloads/"
PRERELEASE_URL: str = "https://www.python.org/download/pre-releases/"

ID_URL: str = "https://github.com/bskinn/cpython-release-feed"

FEED_PATH: Path = Path("feed", "feed.rss")

TIMESTAMP: datetime = arrow.utcnow().datetime

FORMAT: str = "%(asctime)-15s  [%(levelname)-10s]  %(message)s"
logging.basicConfig(format=FORMAT, stream=sys.stderr)

logger: logging.Logger = logging.getLogger()


@attr.s(slots=True)
class Info:
    version: str = attr.ib(validator=attr.validators.instance_of(str))
    url: str = attr.ib(validator=attr.validators.instance_of(str))
    released: datetime = attr.ib(validator=attr.validators.instance_of(datetime))


def resp_report(resp: rq.Response) -> str:
    """Supply combo of status code and reason."""
    return f"{resp.status_code} {resp.reason}"


def get_release_pages() -> tuple[rq.Response, rq.Response]:
    """Retrieve the release page contents."""
    return rq.get(STABLE_URL), rq.get(PRERELEASE_URL)


def gen_stable_entries(resp: rq.Response) -> Iterable[bs4.Tag]:
    """Yield the release entries from the stable downloads page."""
    soup = BSoup(resp.text, "html.parser")

    yield from (li for li in soup("li") if li.find("span", class_="release-number"))


def gen_pre_entries(resp: rq.Response) -> Iterable[bs4.Tag]:
    """Yield the release entries from the prerelease downloads page."""
    soup = BSoup(resp.text, "html.parser")

    yield from (li for li in soup("li") if li.find("a", class_="reference external"))


def released_date_conversion(dstr: str) -> datetime:
    """Attempt various possible formats for the release date."""
    FORMATS = ("MMM. DD, YYYY", "MMM DD, YYYY", "MMMM DD, YYYY")

    dstr = dstr.lower()

    # "Sept" is not a recognized abbreviation
    dstr = dstr.replace("sept", "sep")

    released = None

    for fstr in FORMATS:
        try:
            released = arrow.get(dstr, fstr)
        except arrow.parser.ParserMatchError:
            pass
        else:
            break

    if released is None:
        raise ValueError(f"Date format of '{dstr}' is not recognized")

    return released.datetime


def extract_stable_info(li: bs4.Tag) -> Info:
    """Produce an Info instance with relevant info for the provided stable release."""
    version = li.find("span", class_="release-number").string
    version = version.rpartition(" ")[2]

    released = li.find("span", class_="release-date").string
    released = released_date_conversion(released)

    url = li.find("span", class_="release-download").a["href"]
    url = f"https://python.org{url}"

    return Info(version=version, released=released, url=url)


def create_base_feed() -> FeedGenerator:
    """Create feed generator and configure feed-level data."""
    fg = FeedGenerator()

    fg.id(ID_URL)
    fg.title("CPython Release Downloads")
    fg.author({"name": "Brian Skinn", "email": "brian.skinn@gmail.com"})
    fg.link(
        href="https://github.com/bskinn/cpython-release-feed/raw/master/feed/feed.rss",
        rel="self",
    )
    fg.link(href="https://github.com/bskinn/cpython-release-feed", rel="alternate")
    fg.logo(
        "https://github.com/bskinn/cpython-release-feed/raw/master/_static/py-release-logo.jpg"
    )
    fg.language("en")
    fg.description("Feed for CPython releases posted to www.python.org")
    fg.docs("http://www.rssboard.org/rss-specification")

    return fg


def add_feed_item(fg: FeedGenerator, info: Info) -> None:
    """Add the item information from 'info' in a new entry on 'fg'."""
    fe = fg.add_entry()

    fe.id(f"{ID_URL}-{info.version}")
    fe.title(desc := f"CPython {info.version}")
    fe.link({"href": info.url, "rel": "alternate"})
    fe.author(fg.author())
    fe.content(desc)
    fe.updated(info.released)
    fe.published(arrow.utcnow().datetime)


def write_feed(fg: FeedGenerator) -> None:
    """Write the completed RSS feed to disk."""
    fg.rss_file(str(FEED_PATH), pretty=True)


def main():
    """Execute data collection and feed generation."""
    resp_stable, resp_pre = get_release_pages()
    if not resp_stable.ok:
        logger.critical(
            f"Stable release page download failed: {resp_report(resp_stable)}"
        )
        return 1
    if not resp_pre.ok:
        logger.critical(f"Prerelease page download failed: {resp_report(resp_pre)}")
        return 1

    logger.info("Download pages retrieved.")

    for li in gen_stable_entries(resp_stable):
        print(li.find("span", class_="release-number").find("a").text)

    for li in gen_pre_entries(resp_pre):
        print(li.find("a", class_="reference external").text)

    li = next(iter(gen_stable_entries(resp_stable)))
    print(li)
    breakpoint()


if __name__ == "__main__":
    sys.exit(main())
