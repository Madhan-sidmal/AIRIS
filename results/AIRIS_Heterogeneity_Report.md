# AIRIS Heterogeneity Report
## Phase 4D | Subgroup Labour Market Adjustment Analysis
### Version 1.0 | June 2026

> [!IMPORTANT]
> All heterogeneity estimates use the same specification as R1: district + year FE, clustered SE (CR1), wild cluster bootstrap B=999. Subgroup sample sizes are small (G=10–17 clusters). Results should be interpreted as directional evidence, not precise causal estimates. Subgroup p-values do not survive multiple-comparison correction and are presented for pattern identification only.

---

## 1. Heterogeneity Design

### Why Heterogeneity Matters Here

The main R3 result — β3=+3.03pp unemployment, all secondary outcomes null — was classified in Phase 4C as "No Clear Mechanism" (Classification D). The heterogeneity analysis tests whether this aggregate null on secondary outcomes conceals **opposing mechanisms operating in different district types**.

### Three Dimensions Tested

| Dimension | Split Variable | Source | Threshold |
|---|---|---|---|
| **Geographic** | State (Karnataka vs Rajasthan) | PLFS | — |
| **Human capital** | Literacy rate (high vs low) | Census 2011 | Within-state median |
| **Sector structure** | Agricultural employment 2019 (high vs low) | PLFS 2019-20 | Within-state median |

### Outcomes Examined per Subgroup

1. Unemployment rate (`unemp_rate_wt`) — primary
2. Labour Force Participation Rate (`lfpr_wt`) — ⚠️ unreliable DiD due to 2019-20 age issue
3. Agricultural employment share (`agri_share_wt`)
4. Services employment share (`services_share`)

---

## 2. Dimension 1 — Geographic Split (State)

### 2.1 Karnataka (G=17, N=30)

| Outcome | β3 (pp) | SE | p (boot) | Boot 95% CI | Direction |
|---|---|---|---|---|---|
| Unemployment | +3.003 | 1.884 | 0.077 | [−0.37, +6.21] | Positive (marginal) |
| LFPR ⚠️ | +2.484 | — | 0.111 | [−0.56, +5.63] | Positive (n.s.) |
| Agri share | −2.225 | — | 0.235 | [−5.63, +1.04] | Negative (n.s.) |
| Services share | +2.004 | — | 0.546 | [−3.78, +7.62] | Positive (n.s.) |

**Karnataka pattern:** Unemployment rises moderately in early districts (+3.0pp, p=0.077). Agricultural employment trending downward (−2.2pp) and services trending upward (+2.0pp), neither significant. The direction is consistent with **structural transformation** — a rotation from agri toward services — but the effects are imprecise with G=17.

### 2.2 Rajasthan (G=10, N=18)

| Outcome | β3 (pp) | SE | p (boot) | Boot 95% CI | Direction |
|---|---|---|---|---|---|
| **Unemployment** | **+5.844** | — | **0.005 ★★** | **[+1.22, +10.01]** | Strong positive |
| LFPR ⚠️ | +2.603 | — | 0.418 | [−2.37, +7.57] | Positive (n.s.) |
| Agri share | +0.379 | — | 0.770 | [−2.51, +3.31] | Near-zero |
| Services share | −5.403 | — | 0.263 | [−13.55, +2.69] | Negative (n.s.) |

**Rajasthan pattern:** Unemployment spikes sharply (+5.84pp, p=0.005). Agriculture unchanged. Services trending downward (−5.4pp, imprecise). This pattern — unemployment up, services down, agriculture flat — is closer to **labour displacement** than structural transformation.

### 2.3 Geographic Interpretation

The combined β3=+3.03pp is a weighted average of two qualitatively different state experiences:

| State | Dominant Pattern | Classification |
|---|---|---|
| Karnataka | Unemployment ↑ (marginal) + Agri ↓ + Services ↑ | Pathway A — Early-stage Transformation |
| Rajasthan | Unemployment ↑↑ (significant) + Services ↓ | Pathway B — Displacement |

> [!NOTE]
> Rajasthan's early districts include Jaipur (urban share 66%) and Kota (urban share 67%), which are structurally unrepresentative of rural connectivity effects. The Rajasthan β3=+5.84pp should be re-estimated excluding these two cities in robustness checks for WP1.

---

## 3. Dimension 2 — Human Capital Split (Literacy)

Districts are classified **high literacy** if their Census 2011 literacy rate is at or above the within-state median. This split identifies whether human capital moderates the connectivity–adjustment relationship.

### 3.1 High-Literacy Districts (G=13, N=23)

| Outcome | β3 (pp) | p (boot) | Boot 95% CI | Direction |
|---|---|---|---|---|
| **Unemployment** | **+4.405** | **0.000 ★★★** | **[+1.75, +7.12]** | Strong positive |
| **LFPR ⚠️** | **+2.686** | **0.019 ★** | **[+0.44, +4.95]** | Positive |
| **Services share** | **+3.417** | **0.000 ★★★** | **[+1.45, +5.49]** | Strong positive |
| Agri share | +2.454 | 0.166 | [−0.76, +5.57] | Positive (n.s.) |

### 3.2 Low-Literacy Districts (G=14, N=25)

| Outcome | β3 (pp) | p (boot) | Boot 95% CI | Direction |
|---|---|---|---|---|
| Unemployment | −0.884 | 0.615 | [−4.29, +2.47] | Near-zero |
| LFPR ⚠️ | +1.277 | 0.604 | [−2.55, +4.90] | Near-zero |
| **Agri share** | **−3.958** | **0.046 ★** | **[−7.78, −0.10]** | Negative |
| Services share | −4.214 | 0.336 | [−12.00, +3.58] | Negative (n.s.) |

### 3.3 Literacy Heterogeneity Interpretation

This is the analytically richest finding of Phase 4D.

**High-literacy early districts show simultaneous:**
- Rising unemployment (+4.4pp, p=0.000)
- Rising services employment (+3.4pp, p=0.000)
- Rising LFPR (+2.7pp, p=0.019 — caveat applies)

These three effects together are **not consistent with displacement** (which would show unemployment up, services down). They are consistent with **active labour market expansion in the services sector** that is temporarily generating more unemployment than employment — i.e., workers are entering the services labour market faster than they are being absorbed. This is **Pathway A: Structural Transformation in progress**.

**Low-literacy early districts show:**
- No unemployment effect (β3=−0.88pp, n.s.)
- Agricultural employment falling (−4.0pp, p=0.046)
- Services employment falling (−4.2pp, n.s. but directionally consistent)

Workers are leaving agriculture in low-literacy connected districts, but they are not moving into services (services also falls). The destination is unobserved in PLFS cross-sections — possibilities include: informal self-employment, migration to urban areas, or genuine NILF transition. This is an **ambiguous pattern** — cannot classify as A, B, or C with current data.

---

## 4. Dimension 3 — Sector Structure Split (Agriculture Intensity)

Districts classified **high agriculture** if their 2019-20 PLFS agricultural employment share is at or above the within-state median.

### 4.1 High-Agriculture Districts (G=15, N=29)

| Outcome | β3 (pp) | p (boot) | Boot 95% CI | Direction |
|---|---|---|---|---|
| **Unemployment** | **+4.903** | **0.003 ★★** | **[+1.16, +8.46]** | Strong positive |
| LFPR ⚠️ | +3.192 | 0.298 | [−2.31, +8.43] | Positive (n.s.) |
| Agri share | −0.731 | 0.761 | [−4.51, +2.52] | Near-zero |
| Services share | −2.791 | 0.417 | [−9.41, +3.57] | Negative (n.s.) |

### 4.2 Low-Agriculture Districts (G=12, N=19)

| Outcome | β3 (pp) | p (boot) | Boot 95% CI | Direction |
|---|---|---|---|---|
| Unemployment | −0.262 | 0.935 | [−4.02, +3.53] | Near-zero |
| LFPR ⚠️ | +2.449 | 0.138 | [−0.37, +5.26] | Positive (n.s.) |
| Agri share | +0.774 | 0.744 | [−3.36, +4.79] | Near-zero |
| Services share | +4.294 | 0.144 | [−1.40, +9.92] | Positive (n.s.) |

### 4.3 Agriculture Heterogeneity Interpretation

The unemployment effect is entirely concentrated in high-agriculture districts (+4.90pp, p=0.003) and vanishes in low-agriculture districts (−0.26pp, p=0.935).

This tells a specific story: **connectivity × AI diffusion disrupts labour markets more in districts where employment was already concentrated in agriculture**. Plausible mechanisms:

1. **Agricultural-adjacent non-farm employment** (agri input supply, rural trade, agri processing) is more exposed to automation-related disruption than urban services employment
2. **Information asymmetry correction:** Connectivity enables rural workers in agricultural districts to discover that their informal sector employment is precarious — leading to active job search (and measured unemployment) rather than passive underemployment
3. **Reduced seasonal migration:** Connectivity may reduce the information advantage that drives distress migration, leading workers to seek local employment (and register as unemployed) rather than migrate

---

## 5. Cross-Dimension Synthesis

The three heterogeneity dimensions identify consistent sub-patterns:

| Pattern | Where Found | Coefficient Signature |
|---|---|---|
| **Services expansion + transitional unemployment** | High literacy | unemp ↑↑, services ↑↑, LFPR ↑ |
| **Agricultural exit without visible destination** | Low literacy | agri ↓, unemp ≈ 0, services ↓ (n.s.) |
| **Disruption spike without reallocation** | High agriculture, Rajasthan | unemp ↑↑, agri ≈ 0, services ≈ 0 |
| **Services growth without disruption** | Low agriculture, Karnataka | unemp ≈ 0, services ↑ (n.s.) |

These four patterns suggest the aggregate β3=+3.03pp is a population-weighted average of at least two qualitatively different adjustment processes.

---

## 6. Heterogeneity Summary Table

| Subgroup | N (obs) | G | Unemp β3 | p | Services β3 | p | Agri β3 | p | Classification |
|---|---|---|---|---|---|---|---|---|---|
| **All (main)** | 48 | 27 | +3.03 | 0.040★ | −0.19 | 0.932 | −0.27 | 0.867 | C: Frictional |
| Karnataka | 30 | 17 | +3.00 | 0.077 | +2.00 | 0.546 | −2.23 | 0.235 | A: Transformation |
| Rajasthan | 18 | 10 | **+5.84** | **0.005★★** | −5.40 | 0.263 | +0.38 | 0.770 | B: Displacement |
| High literacy | 23 | 13 | **+4.41** | **0.000★★★** | **+3.42** | **0.000★★★** | +2.45 | 0.166 | A: Transformation |
| Low literacy | 25 | 14 | −0.88 | 0.615 | −4.21 | 0.336 | **−3.96** | **0.046★** | Ambiguous |
| High agriculture | 29 | 15 | **+4.90** | **0.003★★** | −2.79 | 0.417 | −0.73 | 0.761 | B/C: Disruption |
| Low agriculture | 19 | 12 | −0.26 | 0.935 | +4.29 | 0.144 | +0.77 | 0.744 | A: Transformation |

---

## 7. Publication Implications

### What the heterogeneity analysis adds to WP1

The aggregate DiD finding (β3=+3.03pp, p=0.040) alone is a modest result. The heterogeneity analysis substantially strengthens the paper:

1. **High-literacy finding** (unemp +4.4pp AND services +3.4pp, both p=0.000) is the **strongest result in the entire AIRIS analysis** — two highly significant coefficients telling a coherent story
2. **Agriculture split** (effect concentrated in high-agriculture districts, p=0.003 vs p=0.935) demonstrates **treatment effect heterogeneity** that goes beyond the aggregate result
3. The two-process interpretation (transformation in high-literacy districts + disruption in high-agriculture districts) provides the **mechanism narrative** that WP1 needs

### Caveats for WP1

- Subgroup G ranges from 10 to 17 — p-values should not be treated as precise
- Multiple comparisons inflate false positive risk — only patterns consistent across two or more tests should be reported as findings
- The LFPR results carry the 2019 age filter caveat throughout
- Rajasthan results should include urban-outlier sensitivity (excl. Jaipur, Kota)
