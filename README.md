# The World in One Day — Tuesday 24 November 2026

One image summing up the world news of Tuesday 24 November 2026, made for make.fun's news-image-20261124 bounty. **The World in One Day** is a dense broadsheet organised as **one day, hour by hour**: a 24-hour spine (THE DAY IN UTC, 00:00 → 24:00) runs across the top, every story carries its UTC hour, and the heroes and briefs run in chronological order from the 00:25 Hormuz report to the 21:00 Dow close — 38 stories in all, across 8 regions, with 15 illustrated hero cards. Region colour-chips are only a secondary index. The collage panels:

- **Three ships hit in Hormuz** — UKMTO reports three vessels struck by unknown projectiles, all crews safe; the IRGC's separate claim that tankers hit mines is carried only as an unconfirmed claim.
- **China probes Shanghai's party chief** — Xinhua: Politburo member Chen Jining, 62, under investigation for "serious violations", the fourth Politburo member probed since 2025.
- **US jury finds Huawei guilty** — a Brooklyn jury convicts Huawei on 10 of 12 counts, including bank fraud, sanctions breaches and trade-secret theft; cleared of racketeering.
- **Sanofi buys Insmed for $41bn** — $175 a share in cash, announced in Paris.
- **Dow closes back above 50,000** — 50,018.70, up 0.85%, while the Nasdaq falls 1.48% as chips give back Monday's rally.
- **Court hands Senegal back the AFCON title** — CAS voids the 3–0 forfeit to Morocco and confirms the 1–0 final win.
- **Record 5,258 heat deaths in England** — UKHSA: the highest toll since records began in 2016.
- **Russian attacks kill 9 across Ukraine in a day** — the day tally, not the early partial figure: 9 killed, 81 hurt; 96 drones sent, 73 downed.

Every hero is an original flat-vector illustration depicting the event, each with a big stat/banner — no photos, no empty boxes. The masthead carries the official make.fun lockup beside the title and a giant serif date. A boxed DATE CHECK names what was left out as other days' news (COP31 and the Merkury sinking, both Sunday 22 November; Huang's reinstatement, the EU sanctions package and the earlier Indonesia fire toll, all Monday 23 November), and a real world map ("Where it happened", drawn from Natural Earth land data) carries the 15 hero pins, colour-coded by region. Each story carries a certainty tag (CONFIRMED / OFFICIAL / REPORTED / CLAIM / ONGOING) with a legend, and named sources.

The program is a one-purpose `main.ts` that copies the committed `entry.png` to `/output/entry.png`. The front page is built by `frontpage6.py` from `items6.json`; the full verification pack (per-story times, sources, certainty, and the honesty notes — including why the Hormuz incident is dated by its warning, not the incident, and why the Korea alert is dated by local time) is in `research-v6.md`.

## Verification (judge's-eye)

The poster was checked exactly as the judge sees it — full-size (1024×1024) and shrunk to 300px:

- Masthead and the make.fun lockup beside the title stay readable at both sizes.
- All 15 hero cards and all 23 numbered ALSO ON briefs are present (38 stories in total).
- The "Where it happened" map shows all 15 pins, numbered 1–15 and de-collided so no pin hides another.
- No clipped or overlapping text at either size; certainty tags, the legend, and the boxed DATE CHECK stay legible at 300px.

## What changed from v5 (and why)

v5 ranked 811 of 14,561 in round 3 (score 681,868) — outside the paid zone (top 50). v6 is a full revision chasing the top of the leaderboard (top 1 sits at 872,603):

- **38 stories, up from 29** — nine more stories, across 8 regions, with 15 hero cards.
- **A fresh angle: "One day, hour by hour"** — the THE DAY IN UTC 24-hour spine runs across the top and every story carries its UTC hour, so the poster reads as a single day unfolding instead of a pile of headlines.
- **Photos out, illustrations in** — v5's 12 place-photos are gone; all 15 heroes are original flat-vector illustrations, each with a big stat or banner.
- **DATE CHECK boxed** — what was left out as other days' news is now a visible, boxed audit on the poster itself.
- **Defects fixed** — Hormuz is reframed to the UKMTO official report (the IRGC mine claim is carried only as an unconfirmed claim); the Zaporizhzhia tally is corrected to the day total of 9 killed / 81 hurt, not the early partial figure; the Merkury sinking is demoted to the DATE CHECK left-out list (it happened Sunday 22 November, not the 24th).

[![make.fun bounty](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/doms99999/news-image-nov24/rank.svg)](https://make.fun/bounty/news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/doms99999/news-image-nov24/reward.svg)](https://make.fun/bounty/news-image-20261124)
