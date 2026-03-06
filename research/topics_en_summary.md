# Topics from English-Language Scraped Articles

**Generated:** 2026-03-06
**Source:** 128 EN articles from 9 sources (cnevpost: 69, carnewschina: 37, autochina: 6, carscoops: 6, liautocn: 5, electrek: 2, insideevs: 1, topelectricsuv: 1, wikipedia: 1)
**Output:** 25 topics in `topics_from_articles_en.json`

---

## Summary Statistics

| Metric | Value |
|--------|-------|
| Total topics | 25 |
| Category: market | 7 |
| Category: technology | 6 |
| Category: safety | 4 |
| Category: specs | 2 |
| Category: troubleshooting | 2 |
| Category: owner_experience | 1 |
| Category: comparison | 1 |
| Category: market (China-wide) | 2 |
| Overlaps with consensus_issues.json | 10 of 25 |
| New findings not in consensus | 15 of 25 |
| High confidence | 19 |
| Medium confidence | 6 |
| Articles covered | 122 of 128 (6 tangential industry articles excluded) |

---

## Topics by Category

### Safety (4 topics)
| ID | Title | Models | Overlap |
|----|-------|--------|---------|
| topic_en_001 | Li MEGA — Failed Launch, Battery Recall, Fire Incident | MEGA | issue_l2 |
| topic_en_006 | Li L9 Test Car Suspension Breakage + Li ONE Recall | L9, Li ONE | issue_c1 |
| topic_en_007 | ADAS/NOA Autopilot Failure on L9 | L9 | issue_h10 |
| topic_en_008 | Li ONE Cabin Fire — 9 Seconds, Vehicle Quality Ruled Out | Li ONE | issue_l2 |

### Market / Sales (7 topics)
| ID | Title | Models | New? |
|----|-------|--------|------|
| topic_en_002 | Sales Trajectory — Record 2023, 2025 Decline, 8-Month Slump | All | YES |
| topic_en_010 | China Price War — Price Cuts, Trim Restructure | All | YES |
| topic_en_011 | Li L7 — From Near-Cancellation to 300K Deliveries | L7 | YES |
| topic_en_016 | Global Expansion — Europe, Middle East, Central Asia | L6/L7/L9 | YES |
| topic_en_017 | Early History — Startup to IPO, Meituan Investment | Li ONE | YES |
| topic_en_024 | Q2 2022 Earnings — Losses During Li ONE Era | Li ONE | no |
| topic_en_025 | Li i8 Unveil — Stock +15%, Tesla Model X Competition | i8 | YES |

### Technology (6 topics)
| ID | Title | Models | New? |
|----|-------|--------|------|
| topic_en_003 | i8 and i6 BEV Transition, Launch Struggles | i8, i6 | YES |
| topic_en_005 | L9 Livis 2026 — M100 Chip, EMB Brakes, 800V | L9 | YES |
| topic_en_009 | 5C Charging and 800V Platform | MEGA/i8/i6 | YES |
| topic_en_012 | AI Strategy — Livis Glasses, Robots, VLA Driver | L9 | YES |
| topic_en_022 | L9 LiDAR Variants — Pro vs Max, Hesai AT128 | L9 | no |
| topic_en_023 | Humanoid Robots — Xpeng, Xiaomi, Li Auto Race | Industry | YES |

### Troubleshooting (2 topics)
| ID | Title | Models | Overlap |
|----|-------|--------|---------|
| topic_en_013 | 2025 L-Series Front Wheel Noise Defect | L6/L7/L8/L9 | issue_h1 |
| topic_en_015 | L9 1M km Test — Engine Died at 307K (Timing Chain) | L9 | issue_h7 |

### Other (6 topics)
| ID | Title | Category | New? |
|----|-------|----------|------|
| topic_en_004 | Nio/Onvo L90 vs i8/L9 Competition | comparison | YES |
| topic_en_014 | Sunwoda Battery Quality Scandal | technology | YES |
| topic_en_018 | Li L9 Reviews — Premium Family SUV | specs | no |
| topic_en_019 | L7/L8/L6/i8 Reviews from AutoChina | specs | no |
| topic_en_020 | EV Safety — Voice Glitches, Door Handles, Recalls | safety | YES |
| topic_en_021 | China Market — 2026 Subsidies, BYD/Xpeng Competition | market | YES |

---

## Key New Findings (not in consensus_issues.json)

1. **Li MEGA complete failure arc** — from 10K pre-orders in 1h42m to recall of half of all delivered units, RMB 1.14B loss, employee firings, and US class-action lawsuit. The most thoroughly documented product failure in EN sources.

2. **8 consecutive months of YoY sales decline** (Jun 2025 - Jan 2026) — unprecedented for Li Auto. Return to quarterly loss in Q3 2025. L6 now dominates (47%), L9 shrinking (12%).

3. **i-series BEV transition struggles** — i8 relaunched with price cuts 1 week after launch. i6 hit battery supply constraints 4 months post-launch. Sunwoda brand damage makes battery sourcing harder.

4. **L9 Livis 2026 with in-house M100 chip** (2,560 TOPS, 5nm) — 3x Nvidia Thor-U. First EMB brakes addressing the consensus spongy brake issue (issue_c2). Steer-by-wire, 4-wheel steering.

5. **AI pivot** — Li Auto repositioning from automaker to "embodied AI company." Livis smart glasses, Project Nexus humanoid robots, VLA Driver autonomous driving model. CEO: "2026 is the final window."

6. **Sunwoda battery scandal** — RMB 2.31B Geely lawsuit, Zeekr 38K-unit recall for thermal runaway. Directly impacts Li i6 (uses Sunwoda batteries). Buyers refuse Sunwoda option.

7. **Onvo L90 competitive threat** — 25% cheaper than Li i8 and physically larger. Nio's Onvo aggressively marketing direct comparisons with Li L9.

8. **Li Auto global expansion** — Munich R&D center, CCCEU membership, Dec 2025 entries into Egypt/Kazakhstan/Azerbaijan. But pace slower than BYD/Nio/Xpeng.

---

## Overlap with Consensus Issues

| Topic | Consensus Issue | How it connects |
|-------|----------------|-----------------|
| topic_en_001 (MEGA recall) | issue_l2 (Spontaneous Combustion) | MEGA fire + recall directly extends the fire/battery concern |
| topic_en_006 (Suspension) | issue_c1 (Air Suspension Failure) | L9 test car suspension + Li ONE recall = same pattern |
| topic_en_007 (ADAS failure) | issue_h10 (Phantom Braking) | NOA failure incident on L9 |
| topic_en_008 (Li ONE fire) | issue_l2 (Spontaneous Combustion) | Earlier fire incident with Li ONE |
| topic_en_013 (Front wheel noise) | issue_h1 (Lower Control Arm Defect) | 2025 L-series noise = likely same systemic defect |
| topic_en_014 (Sunwoda scandal) | issue_l4 (CATL vs Sunwoda) | Battery supplier controversy, now with legal dimension |
| topic_en_015 (Timing chain) | issue_h7 (1.5T Timing Chain Failure) | 307K km real-world confirmation of timing chain issue |
| topic_en_020 (EV safety) | issue_h2 (Door Handle Freezing) | Electronic door handle failures in broader context |
| topic_en_022 (LiDAR variants) | issue_c4 (LiDAR Issues) | Different LiDAR configurations affect reliability |
| topic_en_005 (L9 Livis EMB) | issue_c2 (Spongy Brakes) | EMB brakes = official engineering fix for brake complaints |

---

## Source Distribution

| Source | Articles | Main Coverage |
|--------|----------|---------------|
| cnevpost_en | 69 | Sales data, recalls, i-series, corporate strategy, industry news |
| carnewschina_en | 37 | MEGA specs/launch, pricing, sales targets, model updates |
| autochina_blog | 6 | Detailed model reviews (L6, L7, L8, L9, MEGA, i8) |
| carscoops_en | 6 | MEGA design/specs, L9 impressions, lawsuit, viral stories |
| liautocn_news | 5 | Official delivery updates, financial announcements |
| electrek_en | 2 | Q2 2022 earnings, i8 unveil + stock surge |
| insideevs | 1 | L9 1M km durability test in Russia |
| topelectricsuv | 1 | L9 first look review |
| wikipedia_en | 1 | L7 basic info |

**Note:** ~30 cnevpost articles cover competitors (BYD, Xpeng, Nio, Xiaomi, Arcfox, Deepal, Huawei/Yijing, Chery/Exeed) — included in industry context topics (020, 021, 023) rather than direct Li Auto topics.
