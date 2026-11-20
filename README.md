# THE WORLD IN ONE DAY — 20 November 2026

An entry for the make.fun bounty **news-image-20261120**: *sum up 20 November's 2026
world news in one image*.

`entry.png` is a one-day newspaper front page for **Friday, 20 November 2026** — edition
20 of "The World in One Day", masthead line *an independent daily front page · one
picture per day*, dateline *56 stories reported today · 6 continents*. It is drawn flat,
with no photographs: typography, rules and one small vector cyclone mark. The footer
strip reads **ONE DAY, SIX CONTINENTS — landfall · talks · sanctions · markets**, and the
credit line under it says the page was compiled from agency dispatches filed on
20 November 2026.

## The stories it carries

| Slot | Story | Where it came from |
|---|---|---|
| Lead, *Landfall* | Cyclone Akvan slams into India's east coast — landfall near Gopalpur, Odisha, by noon, 70–90 kmph winds, 100,000+ people in 1,224 shelters, 14 NDRF and 60 ODRAF teams out, 20–30 cm rain and storm surge warned | The day's India wires, quoting the IMD warning and the NDRF/ODRAF deployment figures |
| Right rail, *Climate* | COP31 closes in Antalya with no fossil-fuel pledge, finance and phase-out still disputed | Dispatches from the closing plenary of the COP31 summit |
| Right rail, *Middle East* | Trump puts off the decision on strikes on Iran — "after the beginning of the year"; war cost past $48bn, Hormuz still shut | Washington and Gulf dispatches of the day |
| Right rail, *Asia* | North Korea enlarges the Yongbyon enrichment plant, per a further IAEA report of an extension at the uranium site | The IAEA's reporting on Yongbyon |
| Bottom, *Africa* | Sudan tops the Security Council agenda — the council meets on protection of civilians as fighting continues | United Nations Security Council programme and briefing notes |
| Bottom, *Americas* | The real slides as Lula's fiscal plan clears the Senate; the dollar touches its highest since April 2025 and the lower house votes Monday | Brasília and market dispatches of the day |
| Bottom, *Economy* | Argentina joins the global patent treaty, 56 years after its first accord with the United States | Treaty-accession reporting of the day |

Nothing on the page is scraped or fetched at run time: the facts were gathered while the
page was drawn, and the page itself is the artifact.

## What `main.py` does

`main.py` is the submission program. It:

1. reads `MAKEFUN_INPUT_DIR` (default `/input`) and `MAKEFUN_OUTPUT_DIR` (default
   `/output`), and creates the output directory if it is missing;
2. reads `entry.png` beside itself, resolved from `__file__` so the program works from
   the read-only `/bot` mount;
3. validates the image the way the sealed scorer will — PNG signature, IHDR width and
   height within 1024 × 1024, file size at most 1 MiB, and every chunk's CRC checked
   with `zlib.crc32` while walking the chunk list — and aborts with a clear
   `SystemExit` message on any failure, because a malformed or oversized image scores
   a Valid column of 0 and takes no prize;
4. copies the bytes with `shutil.copyfile`, then reads the copy back and compares its
   SHA-256 with the source's, so a short write cannot slip through;
5. prints only deterministic lines — dimensions, byte count, chunk count, digest. No
   timestamp, no random value, no network call.

Python 3.13, standard library only (`hashlib`, `os`, `shutil`, `struct`, `sys`, `zlib`,
`pathlib`). Two runs write byte-identical files.

## Run it locally

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

The grader runs it as `python3 -P -s /bot/main.py` in `python:3.13-slim`, with no
network and no installed packages.

## Licence

MIT — see [LICENSE](LICENSE).
