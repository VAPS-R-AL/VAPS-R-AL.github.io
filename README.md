# VAPS — anonymous project page

Static project page for *Continue, Abort, or Fall: Viability-Aware Policy
Selection (VAPS) for Safe Humanoid Acrobatics*, served from GitHub Pages during
double-blind review.

```
index.html                  the whole page
static/css/style.css        the whole stylesheet
static/images/              figures (exported from the paper) and video posters
static/videos/              simulation and hardware clips
static/paper/vaps_paper.pdf the compiled submission
scripts/build_assets.py     rebuilds every clip and poster from the video repo
```

No build step, no dependencies, no third-party requests, no analytics, no
cookies. Preview locally with:

```bash
python3 -m http.server 8000
```

## Publishing

The remote is set to `https://github.com/VAPS-R-AL/VAPS-R-AL.github.io.git`, and
commits in this repository are authored `Anonymous <anonymous@example.com>`
(set as a repo-local `user.name` / `user.email`, so a global identity cannot
leak into them). Verify before every push:

```bash
git log --format='%an <%ae>'
```

Then:

```bash
git push -u origin main
```

and enable Pages: **Settings → Pages → Source: Deploy from a branch → `main` /
`(root)`**. The site appears at

```
https://vaps-r-al.github.io/
```

within a minute or two. The bare address is what the repository name buys: a
user site must live in a repository named `<owner>.github.io`, and the owner
here is `VAPS-R-AL`, so `VAPS-R-AL.github.io` is the only name that works. Any
other name — `VAPS.github.io` included — makes this a *project* site served at
`https://vaps-r-al.github.io/<repo-name>/`. Every path in `index.html` is
relative, so the page itself is indifferent to which one you end up with.

After a rename, Pages needs to redeploy before the new address answers; if the
bare URL still 404s after a few minutes, re-select `main` / `(root)` in
Settings → Pages and Save, or push any commit, to trigger a build.

`.nojekyll` is present so GitHub serves `static/` verbatim rather than running
Jekyll over it.

## Anonymity

The page is written to survive a reviewer looking for the authors:

- no author names, affiliations, funding, acknowledgements or contact details;
- `static/paper/vaps_paper.pdf` is the anonymous build — its PDF metadata
  (`/Author`, `/Title`, `/Subject`, `/Keywords`) is empty;
- no external fonts, scripts, stylesheets or images, so no third-party host
  sees a reviewer's request;
- no links to code hosting, experiment trackers or personal pages.

**Hosting is the remaining exposure.** The repository owner, commit authors and
commit e-mail addresses are all public. This repository is owned by the
`VAPS-R-AL` account, which must carry no identifying display name, avatar or
public e-mail — check that before the first push. Push as that account, not as
a personal one: the push itself appears in the repository's public activity.

Check after the first deploy: the paper link resolves, the nineteen clips
autoplay, and the account's profile is clean.

## The clips

`raps_video/CLIP_INVENTORY.md` in the research repository is the sorted index
of every clip — by robot (Unitree G1 / LimX Oli) and by simulation / hardware —
and says which are published here, which are in the supplementary film, and
which must never be published. `scripts/build_assets.py` rebuilds all of them;
its paths point at the research repository, so run it from a checkout that sits
beside `raps_video/`.

Three rules the page keeps:

- **Nothing is retimed.** The annotated exports and both closed-loop trials
  carry burned-in speed badges, so a retime would falsify them.
- **Only privacy-passed footage ships.** The failure clips are the film's own
  `segment_blur.py` copies (robot sharp over a blurred frame, people removed
  from the sharp region by YOLO person masks); the predictor trials carry the
  approved face pass; the closed-loop trial keeps the film's feathered edge
  patch. `53/58-safe-fall` and `20260902-154410` carry unblurred bystanders and
  are **not** published.
- **Captions claim only what the paper reports.** The closed-loop routing table
  is §IV-C's 18-trial evaluation at τ_nom = 0.3, and the cascade clip's caption
  states that its escalation threshold was lowered further to exercise the
  second handoff.

## Keeping it in sync with the paper

Figures are exported from the paper's own sources: `pareto.png` from
`pictures/raps_pareto_front.pdf`, `untrusted.png` from
`figures/untrusted_policy_ieee.pdf` (both `pdftoppm -r 300`), `overview.png`
from `pictures/final_figure2.pdf` (`pdftoppm -r 220`, white margins trimmed),
`leadtime.png` from `pictures/fall_predictor_two_leadtime_ieee.png` (alpha
flattened), and `banner.jpg` from `pictures/fig0_banner.png` at 1800 px.
Re-export them when the paper's figures change, and re-copy `main.pdf` into
`static/paper/vaps_paper.pdf`.

Numbers on the page are checked against `chapters/*.tex` — every numeric token
in `index.html` appears in the paper, with one exception: the predictor's
0.12–0.80 s lead-time range, which was in §IV-B until commit `d346775`
("shortened") dropped it for page space. It is the measured range over the same
thirteen trials, and the page has room for it.

The supplementary film is `static/videos/vaps_supplementary.mp4` — the v9 cut
(`raps_video/raps_animatic_v9.mp4`, 1280×720, 194.4 s, 15 beats, silent),
remuxed with `-c copy -movflags +faststart` so it streams progressively
instead of buffering all 12.7 MB first. It is NOT re-encoded; replace it the
same way when a newer cut lands, and re-grab the poster:

```bash
ffmpeg -i ../raps_video/raps_animatic_vN.mp4 -c copy -movflags +faststart \
       static/videos/vaps_supplementary.mp4
ffmpeg -ss 3.5 -i static/videos/vaps_supplementary.mp4 -frames:v 1 -q:v 3 \
       static/images/poster_supplementary.jpg
```

The cut carries a silent AAC track, so the player shows a volume control that
does nothing; the caption says the film is silent. Note that `raps_video/`
also holds a v10 (180.2 s, beat 10 rebuilt as one shot) — v9 is on the site by
choice, so check which you mean before swapping.
