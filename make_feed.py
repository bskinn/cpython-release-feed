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

import sys

import requests as rq
from bs4 import BeautifulSoup as BSoup


STABLE_URL = "https://www.python.org/downloads/"
PRERELEASE_URL = "https://www.python.org/download/pre-releases/"


def logprint(text):
    """Print text to stderr instead of stdout."""
    print(text, file=sys.stderr)


def resp_report(resp):
    """Supply combo of status code and reason."""
    return f"{resp.status_code} {resp.reason}"


def get_release_pages():
    """Retrieve the release page contents."""
    return rq.get(STABLE_URL), rq.get(PRERELEASE_URL)


def gen_stable_entries(resp):
    """Yield the release entries from the stable downloads page."""
    soup = BSoup(resp.text, "html.parser")

    yield from (
        li for li in soup.find_all("li") if li.find("span", class_="release-number")
    )


def gen_pre_entries(resp):
    """Yield the release entries from the prerelease downloads page."""
    soup = BSoup(resp.text, "html.parser")

    # yield from ()


def main():
    """Execute data collection and feed generation."""
    resp_stable, resp_pre = get_release_pages()
    if not resp_stable.ok:
        logprint(f"Stable release page download failed: {resp_report(resp_stable)}")
        return 1
    if not resp_pre.ok:
        logprint(f"Prerelease page download failed: {resp_report(resp_pre)}")
        return 1

    for li in gen_stable_entries(resp_stable):
        print(li.find("span", class_="release-number").find("a").text)


if __name__ == "__main__":
    sys.exit(main())
