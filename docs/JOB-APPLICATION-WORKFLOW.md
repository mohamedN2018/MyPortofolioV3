# Job Application Workflow

## Sources (lawful only)
1. Public APIs of connected sources: Remote OK, company Greenhouse/Lever boards (`/hub/jobs/` → Sync, or `search_jobs_from_connected_sources`).
2. Links you add (dashboard form or `add_job`). The server stores the link; it never fetches it.

Duplicates: identical URL (tracking parameters ignored) updates the same job; same company + title + location from another source is flagged as a possible duplicate; a second application to the same job — or the same job elsewhere after you applied — is blocked.

## Matching (transparent, 100 points)
| Part | Max | Data used |
|---|---|---|
| Skills | 40 | job skills vs **verified** skills (CV skill groups + active `core.Skill`) — missing skills listed |
| Experience | 15 | job's min years vs your verified years (`identity/years-experience`) |
| Location / mode | 15 | preferences (Egypt, KSA, UAE, Remote by default) |
| Seniority | 10 | title words vs preferred seniority |
| Language | 5 | stated requirements vs verified English level |
| Salary | 5 | only if published |
| Relevance | 10 | target roles; excluded technologies zero it |

Anything the posting doesn't state gets half credit and the label "not stated" — nothing is guessed.

## Preparation
`prepare_application` / **Prepare application** button:
- CV chosen by market: KSA/UAE → Gulf CV, Egypt → Egypt CV, else default.
- Cover letter from your template (`{name} {company} {title} {skills} {headline} {site}`) or a short neutral default — only verified data.
- Answers come from verified, non-sensitive "standard application answer" facts. **Salary, visa, notice period, nationality, age, references and similar are never auto-answered** (left `null` and flagged).
- Flags list missing skills (don't claim them), missing facts and questions you must answer.

## Approval and execution
```
Discovered → Analyzed → Shortlisted → Draft prepared → Awaiting approval → Ready to apply → Submitted → Assessment → Interview → Offer
                                                                                                     ↘ Rejected / Withdrawn
```
1. Draft → **Request approval** (blocked while any answer is still `null`).
2. `/hub/approvals/<id>/` shows the final preview: company, job, application URL, account, submission mode, CV version, cover letter, answers, documents, flags.
3. Approve → status *Ready to apply*. The approval works **once**, for **this** application with **exactly** this content, for 60 minutes. Editing the draft invalidates it.
4. `submit_application` consumes it. No catalogued platform offers candidate-side submission, so the result is a **manual hand-off**: the agent opens the official page, you submit.
5. Record the real outcome. *Submitted* requires a consumed approval **and** evidence (confirmation e-mail / reference number).

## Tracker
`/hub/applications/` — board (12 columns) or table, follow-up dates, notes, evidence, documents with hashes, approval history, **CSV export** (UTF-8 with BOM for Excel/Arabic).
