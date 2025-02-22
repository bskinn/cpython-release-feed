# RSS Feed for CPython Releases

_Want to know when new versions of CPython are available?_

RSS to the rescue!

I build my own CPython from source on WSL and my Linux machines, and I didn't want to have to
manually check the downloads page to find out when new versions drop.

In 2021, I wasn't able to find an RSS feed that gave me what I was looking for,
so I built my own. As of 2025, per [python/pythondotorg#1612][#1612], an official
`python.org` feed has also now been implemented.

Point your RSS feed reader [here][my rss xml] or [there][pdo rss xml], and get notified!

----

Copyright (c) Brian Skinn 2021-2025

License: The MIT License. See [`LICENSE.txt`](https://github.com/bskinn/cpython-release-feed/blob/main/LICENSE.txt)
for full license terms.


[#1612]: https://github.com/python/pythondotorg/issues/1612
[my rss xml]: https://raw.githubusercontent.com/bskinn/cpython-release-feed/main/feed/feed.rss
[pdo rss xml]: https://www.python.org/downloads/feed.rss
