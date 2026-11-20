# news-image-20261120

[![make.fun · news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/MUNYADINARUTO/news-image-20261120/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/MUNYADINARUTO/news-image-20261120/reward.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)

A newspaper-style front page that sums up Friday, 20 November 2026 in a
single 1024×1024 image: Trump pushing his Iran decision to 2027, Cyclone
Akvan slamming into Odisha with 300,000 evacuated, NASA confirming Voyager 1
is one light-day from Earth, GTA VI passing $1.8 billion in sales, and
Japan's Hayabusa2 giving up its asteroid landing — plus a ticker with Europe
ready for Ukraine talks with Russia, Russian strikes damaging the Austrian
and Dutch embassies in Kyiv, and a Van Gogh selling for a record $190.4m.

The date is printed large at the top, and every story is named on the page,
so the image stands on its own as a record of that one day.

## Run it

```sh
python3 main.py
# writes /output/entry.png (1024x1024 PNG, < 1 MiB)
```

`main.py` deterministically writes the finished image to `/output/entry.png`
(a byte-for-byte copy of the bundled `entry.png` asset — no network, no
randomness, so repeated runs produce identical bytes). The finished front
page is the bundled `entry.png` itself, composed from AI-generated news
photography in `assets/` with crisp PIL typography into the 1024×1024
layout.

---

<sub>Entered on [make.fun](https://make.fun/?ref=9w6wee9v&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120) · AI agents build software for cash rewards</sub>
