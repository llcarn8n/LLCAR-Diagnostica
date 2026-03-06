# Li Auto L7/L9 Knowledge Enrichment Research

## Goal
Collect real-world owner experience data for Li Auto L7 and L9 vehicles.
Focus on: problems, faults, seasonal issues, maintenance, DTC codes, symptoms (noise, vibration, warning lights).
Full context required: mileage, season, triggers, affected systems, resolution.

## Process
- Round 1: 6 agents research independently (no source overlap)
- Round 2: Cross-validation (each agent checks another's sources)
- Round 3: Consensus — confirmed vs unconfirmed findings

## Agent Assignments (Round 1)

### Agent 1: Telegram Communities (RU)
Sources: @lixiangautorussia, @kitayskieavto, @chinese_cars_ru, other Li Auto TG groups
Focus: Q&A threads, owner complaints, seasonal tips, real maintenance cases

### Agent 2: Drom.ru + Review Platforms (RU)
Sources: drom.ru reviews, drom.ru "5 kopeek" (problems tab), otzovik.com, irecommend.ru
Focus: Structured owner reviews, mileage-tagged issues, pros/cons, reliability data

### Agent 3: Drive2.ru + RU Forums
Sources: drive2.ru journals, getcar.ru, liautorussia.ru, RU Chinese car forums
Focus: Detailed repair logs, maintenance diaries, long-term ownership reports

### Agent 4: English Sources
Sources: carnewschina.com, carscoops.com, insideevs.com, Reddit r/LiAuto, topelectricsuv.com
Focus: International reviews, long-term reports, comparative analysis

### Agent 5: Chinese Sources
Sources: autohome.com.cn reviews, dongchedi.com, lixiang.com/community, Bilibili transcripts
Focus: Primary market feedback, Chinese owner experience, official community

### Agent 6: Technical/DTC
Sources: OBDb GitHub, YouTube repair channels, DTC databases, service bulletins
Focus: DTC codes, repair procedures, technical service bulletins, diagnostic data

## Output Format (per issue found)

```markdown
### [Issue Title]
- **Models**: L7 / L9 / Both
- **Mileage**: range (e.g., 5,000-15,000 km)
- **Season**: winter / summer / all / rainy
- **Symptoms**: noise type, warning light, behavior change
- **Affected Systems**: suspension, brakes, battery, HVAC, etc.
- **DTC Codes**: if any
- **Root Cause**: if known
- **Resolution**: warranty replacement, repair procedure, OTA fix
- **Confidence**: HIGH (3+ sources) / MEDIUM (2 sources) / LOW (1 source)
- **Sources**: [url1], [url2], ...
- **How Found**: search queries, navigation path, API used
```

## Status
- [ ] Round 1: Agents 1-3 (RU sources)
- [ ] Round 1: Agents 4-6 (EN/CN/Tech sources)
- [ ] Round 2: Cross-validation
- [ ] Round 3: Consensus
- [ ] Final: JSON export for KB import
