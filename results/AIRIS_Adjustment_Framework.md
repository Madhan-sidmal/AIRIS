# AIRIS Adjustment Framework
## Phase 4D | Unified Labour Market Outcome Framework
### Version 1.0 | June 2026

---

## 1. Framework Structure

The AIRIS Labour Market Adjustment Framework organises all district-level outcomes into four tiers that trace the adjustment pathway from structural conditions to distributional consequences.

```
                    BharatNet Connectivity (Treatment)
                              ↓
                    Post-2023 AI Diffusion Shock
                              ↓
        ┌─────────────────────┼──────────────────────┐
        ↓                     ↓                       ↓
   PARTICIPATION          EMPLOYMENT             EARNINGS
   (Who engages           (How many              (What do
    with labour           are employed,           workers
    market?)              and where?)             earn?)
        │                     │                       │
   [LFPR, WPR,           [agri share,            [log_wage
    NILF share]           nonagri share,          median]
                          services share]
        └─────────────────────┼──────────────────────┘
                              ↓
                    UNEMPLOYMENT
              (The residual: in labour force
               but not employed)
```

---

## 2. Outcome Variable Inventory

### Tier 1 — Participation

| Variable | Source | Interpretation | DiD Reliability |
|---|---|---|---|
| `lfpr_wt` | PLFS | % of working-age (15+) in labour force | ⚠️ UNRELIABLE for 2019 baseline (no age filter in 2019-20 round) |
| `wpr_wt` | PLFS | % of working-age employed | ⚠️ UNRELIABLE for 2019 baseline |
| `nilf_share_wt` | PLFS | % of working-age not in labour force | ⚠️ UNRELIABLE for 2019 baseline |

### Tier 2 — Employment (Primary Outcomes)

| Variable | Source | Interpretation | DiD Reliability |
|---|---|---|---|
| `unemp_rate_wt` | PLFS | % of labour force unemployed | ✅ HIGH — uses LF denominator (not affected by age issue) |
| `agri_share_wt` | PLFS | % of employed in agriculture | ✅ HIGH — employed only, no age issue |
| `nonagri_share_wt` | PLFS | % of employed in non-agriculture | ✅ HIGH |
| `services_share` | PLFS | % of employed in services sub-sector | ✅ HIGH |

### Tier 3 — Earnings

| Variable | Source | Interpretation | DiD Reliability |
|---|---|---|---|
| `log_wage_median` | PLFS | Median log weekly wage (wage workers) | ⚠️ MODERATE — 95.8% coverage; small wage-worker samples in rural areas |

### Tier 4 — Controls (Not DiD Outcomes)

| Variable | Source | Interpretation |
|---|---|---|
| `literacy_rate` | Census 2011 | Time-invariant human capital baseline |
| `agri_worker_share` | Census 2011 | Time-invariant structural baseline |
| `urban_share` | Census 2011 | Time-invariant urbanization baseline |

---

## 3. Adjustment Pathway Hypotheses

Three adjustment pathways are theoretically possible following the AI diffusion shock for digitally-connected rural districts:

### Pathway A — Structural Transformation (Positive Adjustment)

Expected pattern:
- Unemployment: Temporarily positive (transition friction)
- LFPR: Rising (new entrants attracted by digital job opportunities)
- Agri share: Falling (workers leave farming for digital/service jobs)
- Services share: Rising (workers move to service sector)
- Wages: Rising (productivity gains from AI complement)

### Pathway B — Labour Displacement (Negative Adjustment)

Expected pattern:
- Unemployment: Positive (job losses exceed new hires)
- LFPR: Falling (discouraged workers leave labour force)
- Agri share: Rising (displaced workers retreat to subsistence farming)
- Services share: Falling or flat (displacement without replacement)
- Wages: Flat or falling (remaining workers face wage pressure)

### Pathway C — Frictional Adjustment (Neutral, Transitional)

Expected pattern:
- Unemployment: Positive (workers between jobs, actively searching)
- LFPR: Stable or slightly rising
- Agri share: Stable (no sectoral reallocation yet)
- Services share: Stable
- Wages: Stable (workers who remain employed face no wage pressure)

---

## 4. Empirical Mapping (Phase 4D Results)

| Outcome | β3 (main) | Significance | Direction |
|---|---|---|---|
| Unemployment | +3.03pp | ✅ p=0.040 | Positive |
| LFPR | +3.00pp | — p=0.141 (unreliable) | Positive trend |
| WPR | +0.18pp | — p=0.946 | Near-zero |
| NILF | −3.00pp | — p=0.141 (unreliable) | Negative trend |
| Agri share | −0.27pp | — p=0.867 | Near-zero |
| Services share | −0.19pp | — p=0.932 | Near-zero |
| Log wage | +0.01 | — p=0.920 | Near-zero |

**Main finding:** Only unemployment is significantly affected at the aggregate level. Sectoral composition and wages are unchanged. This is consistent with **Pathway C (Frictional)** but the heterogeneity analysis changes this picture substantially.

---

## 5. Heterogeneity Framework

The aggregate null on secondary outcomes masks heterogeneous patterns that only become visible in subgroup analysis:

| Subgroup | Unemployment β3 | Services β3 | Agri β3 | Interpretation |
|---|---|---|---|---|
| **High literacy** | **+4.41pp ★** | **+3.42pp ★** | +2.45pp | Services expansion + unemployment |
| **Low literacy** | −0.88pp | −4.21pp | **−3.96pp ★** | Agricultural release (↓agri share) |
| **High agriculture** | **+4.90pp ★** | −2.79pp | −0.73pp | Unemployment spike; no sector shift |
| **Low agriculture** | −0.26pp | +4.29pp | +0.77pp | Services expansion, no unemployment |
| **Karnataka** | +3.00pp | +2.00pp | −2.23pp | Mixed; no significance |
| **Rajasthan** | **+5.84pp ★** | −5.40pp | +0.38pp | Strong unemployment; services decline |

---

## 6. Framework Summary

The full adjustment framework reveals that the AI-era labour market adjustment in digitally-connected rural India is **not uniform** — it is stratified by literacy and pre-existing sector composition:

1. **High-literacy, digitally-connected districts:** Both unemployment AND services employment are rising — consistent with a sector that is expanding but displacing existing workers in the transition process

2. **Low-literacy, digitally-connected districts:** Agricultural employment share is falling — consistent with workers leaving subsistence farming, but the destination is unclear (unemployment or services)

3. **High-agriculture districts:** Strong unemployment spike without sector shift — consistent with a sector-specific demand shock affecting agricultural-adjacent rural employment
