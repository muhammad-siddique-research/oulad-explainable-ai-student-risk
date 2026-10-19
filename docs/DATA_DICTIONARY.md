# Derived analytic dataset and temporal provenance

| Variable | Source | Definition |
|---|---|---|
| `student_id` | studentInfo.id_student | Public anonymized ID, locally retained only |
| `course_presentation` | module + presentation IDs | Entire-group split key; **not** used as model feature |
| `cutoff_day` | analysis protocol | Exclusive horizon: day 28 means days 0 through 27 |
| `lms_clicks_by_cutoff` | studentVle.sum_click | Total clicks before decision horizon |
| `active_days_by_cutoff` | studentVle.date | Unique active dates before cutoff |
| `tasks_completed_by_cutoff` | studentAssessment.date_submitted + assessments | Distinct assessments submitted before cutoff; scores omitted |
| `num_of_prev_attempts` | studentInfo | Prior course attempts |
| `studied_credits` | studentInfo | Credit enrollment, recorded in source |
| `gender` | studentInfo | Reported group, not a causal construct |
| `age_band` | studentInfo | Historical age interval |
| `disability` | studentInfo | Historical recorded category, not a diagnostic assessment |
| `imd_band` | studentInfo | UK deprivation-band group |
| `highest_education` | studentInfo | Recorded baseline education |
| `final_risk_label` | studentInfo.final_result | End-of-course Fail/Withdrawn=1, Pass/Distinction=0 |
| `data_origin` | pipeline | Distinguishes authentic OULAD from generated fiction |

The original public source contains seven related CSV tables. The primary preparation pipeline reads five, while the other two support documentation and further audits. Raw CSVs and row-level predictions stay untracked.
