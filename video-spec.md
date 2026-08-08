请你按照以下 script，帮我生成一条视频；所有产品证据必须来自最终线上版本。

# RepairPilot Judge-Cut Video Specification

## 1. Delivery contract

- **Title:** RepairPilot — Block. Repair. Prove. Remember.
- **Audience:** DataHub hackathon judges first; data-platform engineers second.
- **Decision the video must earn:** this agent uses DataHub deeply, performs a
  bounded real repair, proves the result, preserves human authority, and writes
  reusable knowledge back.
- **Format:** 158.0 seconds, 1920×1080, 30 fps, 16:9, H.264/AAC, BT.709.
- **Pacing:** tutorial/editorial, 34 shots, ten evidence chapters; no empty
  promise scene.
- **Voice:** `en-US-AndrewMultilingualNeural`, calm technical-lead delivery;
  canonical 296 words in `video/narration.txt`.
- **Captions:** generated from exact TTS word boundaries; at most seven words,
  at most two lines, approximately 34 px, bottom safe offset 52 px.
- **Visual theme:** incident control room; background `#0B1020`, card
  `#141B2D`, DataHub `#3B82F6`, block `#EF4444`, approval `#F59E0B`, proof
  `#22C55E`, write-back `#8B5CF6`.
- **Evidence rule:** real RepairPilot, DataHub OSS, GitHub, and dbt output only.
  Waiting may be accelerated at `2×` and must be labeled. DataHub pages remain
  the native UI.
- **Disclosure:** Northstar Commerce business data is synthetic. DataHub, MCP,
  Postgres, dbt, DeepSeek, Git, GitHub, HTTPS, approval, and write-back execute
  for real.
- **Audio:** no music; original interface tones only; target -16 LUFS and no
  higher than -1 dBTP.

## 2. Narrative and chapter timing

| Chapter | Time | Judge question answered | Primary evidence |
|---|---:|---|---|
| Dangerous change | 0.0–14.0 | Is the problem real and immediately clear? | Live Run → BLOCK |
| DataHub context | 14.0–37.0 | Is DataHub essential rather than decorative? | Schema, Owner, Tags, Lineage, Queries, Quality |
| Deterministic policy | 37.0–51.0 | Can the model bypass safety? | HIGH 100/100, fail closed |
| Bounded repair | 51.0–69.0 | Does AI contribute useful but constrained work? | Alias, migration, schema test |
| Executable proof | 69.0–94.0 | Did the agent actually do and verify work? | Failure, worktree, dbt build, 14 tests |
| Owner authority | 94.0–103.0 | Who authorizes a high-risk action? | Approval unlocked only by proof |
| Reviewable PR | 103.0–113.0 | Can reviewers inspect the action? | Four-file PR, Diff, Actions |
| DataHub write-back | 113.0–133.0 | Does the result become reusable knowledge? | Assertion, real Incident, Runbook |
| Evidence Receipt | 133.0–150.0 | Is the chain tamper-evident and repeatable? | URNs, SHA, three runs, zero residue |
| Real boundary | 150.0–158.0 | What is synthetic and what is real? | Disclosure, URL, four-word mark |

Emotional curve: **risk → controlled confidence → verified institutional
memory**. The first real DataHub frame appears at 14.0 seconds. The final shot
holds on the disclosure and public URLs without a fade.

## 3. 34-shot execution table

The machine-readable source of truth is `video/timeline.json`. Each time range
below is exact. UI shots use a stable `broll-ui.browser` frame; graphic proof
uses the listed registered component family. Light UI is fully opaque on the
first frame and never uses a full-frame fade.

| # | Time | Component | Evidence / screen message | Motion, audio, transition |
|---:|---:|---|---|---|
| 01 | 0.0–4.0 | `broll-ui.browser` | Real RepairPilot; `gross_amount → gross_revenue` | native recording; click/state change at `1×`; hard cut |
| 02 | 4.0–9.0 | `broll-ui.browser` | Product context; four assets at risk | continuous native recording; wait only `2×`; hard cut |
| 03 | 9.0–14.0 | `broll-ui.browser` | Real Run → BLOCK | continuous native recording; wait only `2×`; hard cut |
| 04 | 14.0–17.7 | `broll-ui.browser` | `stg_orders.gross_amount`; official MCP | fixed high-resolution crop; hard cut |
| 05 | 17.7–21.3 | `broll-ui.browser` | Revenue Analytics Owner; Finance Domain | fixed crop; hard cut |
| 06 | 21.3–25.7 | `broll-ui.browser` | Tier1, FinancialMetric, quality | fixed crop; hard cut |
| 08 | 25.7–27.8 | `broll-ui.browser` | stored usage queries | fixed crop; hard cut |
| 07 | 27.8–34.0 | `broll-ui.browser` | field lineage, four consumers, not hard-coded | native lineage canvas; hard cut |
| 09 | 34.0–37.0 | `broll-ui.browser` | Assertions and health | fixed crop; hard cut + chapter tone |
| 10 | 37.0–41.3 | `broll-hero.big-number` | `HIGH · 100/100 · BLOCK` | number lands; soft entrance → hard cut |
| 11 | 41.3–46.0 | `broll-flows.branching` | DataHub/dbt failure remains blocked | checks CASCADE; hard cut |
| 12 | 46.0–51.0 | `broll-thinking.card-grid` | breaking + governed + downstream rules | checks CASCADE; soft entrance → hard cut |
| 13 | 51.0–54.3 | `broll-thinking.card-grid` | DeepSeek proposes; policy retains authority | cards CASCADE; soft entrance → hard cut |
| 14 | 54.3–58.0 | `broll-ui.browser` | retain `gross_amount` alias | static product evidence; hard cut |
| 15 | 58.0–61.0 | `broll-ui.browser` | migrate controlled downstream model | static product evidence; hard cut |
| 16 | 61.0–69.0 | `broll-thinking.card-grid` | add real schema test; reject shell/SQL | checks CASCADE; soft entrance → hard cut |
| 17 | 69.0–74.0 | `broll-structures2.layered-stack` | detached worktree + per-run schemas | layers CASCADE; hard cut |
| 18 | 74.0–77.0 | `broll-hero.big-number` | original breaking build `FAILED` | red result lands; soft entrance → hard cut |
| 19 | 77.0–79.7 | `broll-ui.browser` | affected `dbt build`; BLOCK and proof | native recording at `1×`; hard cut |
| 20 | 79.7–85.0 | `broll-ui.browser` | `14 tests · zero failures`; invocation + SHA | stable proof crop; hard cut |
| 21 | 85.0–94.0 | `broll-hero.big-number` | `14 tests`, `Zero failures` | green hold; soft entrance → hard cut |
| 22 | 94.0–98.2 | `broll-ui.browser` | Revenue Analytics approval unlocked | native recording at `1×`; hard cut |
| 23 | 98.2–103.0 | `broll-ui.browser` | approval recorded; reject semantics | native product screenshot; hard cut |
| 24 | 103.0–106.3 | `broll-ui.browser` | public draft PR #1; four files | fixed GitHub crop; hard cut |
| 25 | 106.3–109.7 | `broll-ui.browser` | alias, migration, test, guide Diff | fixed GitHub crop; hard cut |
| 26 | 109.7–113.0 | `broll-ui.browser` | GitHub Actions green | fixed GitHub crop; hard cut + chapter tone |
| 27 | 113.0–118.0 | `broll-ui.browser` | passing `gross_revenue` Assertion | native DataHub UI; hard cut |
| 28 | 118.0–121.8 | `broll-ui.browser` | real per-run Incident body | root cause, risk, invocation, SHA readable; hard cut |
| 29 | 121.8–128.0 | `broll-ui.browser` | Safe dbt Column Rename Runbook body | native DataHub UI; hard cut |
| 30 | 128.0–133.0 | `broll-ui.browser` | learned product state | stable write-back links; hard cut |
| 31 | 133.0–140.3 | `broll-thinking.card-grid` | immutable Receipt joins every proof | cards CASCADE; soft entrance → hard cut |
| 32 | 140.3–144.3 | `broll-hero.big-number` | three runs; one patch hash; one Runbook | metric hold; hard cut |
| 33 | 144.3–150.0 | `broll-thinking.card-grid` | zero schemas/worktrees; Receipts verify | checks CASCADE; hard cut |
| 34 | 150.0–158.0 | `broll-hero.big-type` | Synthetic business data · real execution; URLs | title hold; hard cut into the final frame |

Hard cuts are the default. Seven dark graphic shots use a six-frame content
entrance over an unchanged background; light UI never fades to the control-room
background. There is no Ken Burns motion, flash transition, shot number, or
large lower-third competing with captions.

## 4. Audio and shared timing source

`video/timeline.json` supplies every chapter and shot boundary. The TTS generator
reads the same file, anchors each narration paragraph inside its chapter, emits
`Caption` JSON from WordBoundary events, and fails if speech crosses the chapter
end. `AudioTracks.tsx`, `Captions.tsx`, and the visual composition consume those
generated manifests.

Only the closing line uses a faster voice rate so all 296 approved words remain
inside the eight-second final chapter; it still ends with a visible hold.

## 5. Encoding and visual constraints

- All Remotion intermediates are PNG.
- UI sources are lossless browser screenshots, captured at high pixel density
  and shown with static contain/fixed crops.
- Remotion performs one H.264 encode at CRF 14.
- Two-pass loudness normalization creates a separate AAC file; final packaging
  uses `-c:v copy`, so UI video is never encoded twice.
- Captions remain 52 px from the bottom and the evidence window is 824 px high.
- Accelerated footage is labeled `2× WAIT`; clicks, BLOCK, Approval, and LEARNED
  stay at normal speed.

## 6. Acceptance checks

1. Duration 157–159 seconds and strictly below 180; 1920×1080, 30 fps,
   H.264/AAC, yuv420p, BT.709.
2. Approximately -16 LUFS; true peak no higher than -1 dBTP.
3. Zero black segments and zero transient luminance valleys at light-UI cuts.
4. Every narration segment ends inside its chapter; at least 20 semantic anchors
   are within ±250 ms of the matching visual evidence.
5. Caption phrases contain at most seven words and use exact TTS word-boundary
   start/end timestamps.
6. OCR/manual review identifies `stg_orders`, `Revenue Analytics`, `Tier1`,
   `gross_revenue`, `14 tests`, `Incident`, and `Runbook` at 1080p.
7. Secret-pattern scan across source, metadata, frames, and captions is clean.
8. Machine results and manual visual scoring are recorded separately; no
   hard-coded quality score is permitted.
9. The video, README, deployed UI, public PR, and final Git commit agree.

## 7. References and anti-patterns

- Positive reference: a calm SRE incident review—fast proof, restrained motion,
  readable artifacts, and explicit authority boundaries.
- Differentiation: real catalog context and executable repair evidence appear
  before architectural explanation.
- Never: fade a light UI shot from black, animate a screenshot continuously, or
  claim evidence that is not visible in the frame.
- Never: repeat “not a chatbot,” synthetic disclosure, or Receipt fields merely
  to fill time.
- Never: use background music, fake enterprise integrations, or an unlabeled
  replay.

## 8. Open issues

None. The specification is locked to the judge-cut plan and the 296-word
narration.
