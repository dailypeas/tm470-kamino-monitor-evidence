# Current risk register

Scale: likelihood and impact Low/Medium/High; overall rating is reasoned rather than numerically calculated.

| ID | Risk/cause | L | I | Rating | Mitigation | Contingency | Status/materialised/reflection |
|---|---|---|---|---|---|---|---|
| R1 | Scope growth from multiple indicators/products | High | High | Critical | Two mandatory rules; explicit exclusions and decision gates | Drop optional value rule, live mode and weighting | Materialised partly; tighter scope improved completion realism |
| R2 | Solana/Kamino interpretation is harder than expected | High | High | Critical | Direct programme invocation only; unknown state | Fixture-only evaluation and document false negatives | Materialised; original medium likelihood was optimistic |
| R3 | Data difficult to retain/structure | Medium | High | High | Canonical record, immutable fixtures, provenance | Synthetic cases labelled clearly | Materialised historically; current fixtures/tests mitigate it |
| R4 | Excessive false positives | High | Medium | High | Contextual wording, individual reasons, sensitivity analysis | Manual review; never infer maliciousness | Active; no operational dataset to quantify it |
| R5 | False negatives/incomplete coverage | High | High | Critical | Explicit programme boundary and missing-data states | Document indirect/other-programme exclusions | Active and unavoidable within MVP |
| R6 | Schedule slippage | High | High | Critical | Prioritise core evidence; remove lower-priority work | Stop development and assemble report | Materialised; corrective action was scope reduction |
| R7 | Insufficient reproducible evidence | Medium | High | High | Git checkpoints, commands, tests, JSON/CSV outputs | Use fixture path regardless of API availability | Previously materialised; now substantially mitigated |
| R8 | Credential exposure | Low | High | Medium | `.env` ignored; environment variables; no secret logging | Rotate key and remove affected outputs | Not observed; controls tested by inspection |
| R9 | Misclassification/reputational harm | Medium | High | High | Neutral terminology and manual review | Remove identifying/contextual claims | Not operationally materialised; remains an ethical constraint |

