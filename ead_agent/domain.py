"""EAD domain rules injected into the generate_sql prompt.

Everything here was verified against the live March-2026 database, not assumed
from table names. Several of these contradict what the schema *looks* like --
that is exactly why they are written down.
"""

DOMAIN_NOTES = """
EAD DOMAIN RULES (verified against this database -- follow them exactly):

CANONICAL TABLES -- pick the right one among look-alikes
- Donor <-> project funding: use `project_to_foreigncecomponents`
  (donor_id <-> project_id). This is THE donor-to-project link.
  Do NOT use `project_to_foreigndetails` for "which/how many projects did
  donor X fund" -- it is a per-tranche sub-breakdown with far fewer rows and
  will undercount (World Bank shows 9 there vs the true 60). Only use
  project_to_foreigndetails when the question is explicitly about individual
  loan/grant tranches or their terms.
- Project cost / spend: use `project_to_financials.projectcost_usd`
  (one row per project, millions USD). This is THE cost table.
  Do NOT use `wq_piplineprojects` for project cost -- it holds only 3
  pipeline-stage rows and is not the project portfolio. Use it ONLY when the
  question explicitly asks about the pipeline / planned / upcoming projects.

MINIMAL JOINS
- Join a table ONLY if you select a column from it, filter on it, or need it
  to reach another required table. Do not add extra junctions "just in case".
- One join that satisfies the filter is enough. Example: to count projects
  approved by a named forum, join wq_projects -> project_to_approvalforums ->
  wq_approvalforums and filter the forum name. Do NOT also join
  project_to_issues or any other unrelated junction -- each extra join
  silently drops rows (ECNEC collapsed from 111 to 7 this way).

COUNTING ACROSS JOINS
- Junction tables often hold duplicate rows per entity, so COUNT(*) over a
  join OVER-COUNTS. When counting projects (or donors/agencies) reached
  through a junction, use COUNT(DISTINCT project_id) -- not COUNT(*).
  Verified: active projects in Punjab is 36 distinct projects, but COUNT(*)
  through project_to_executingencies returns 39.
- Likewise use COUNT(DISTINCT donor_id) / COUNT(DISTINCT executingagency_id)
  when counting those entities across a join.

FISCAL YEAR
- Pakistan's fiscal year runs 1 July - 30 June. FY2023-24 = 2023-07-01 .. 2024-06-30.
- `wq_timeperiods` does NOT contain fiscal years. It contains disbursement
  FREQUENCIES (Quarterly, Bi-Annually, Annually, Monthly, 'Since date of
  signing', 'Fully Disbursed in One Tranche'). Never join it to get a fiscal year.
- Derive the fiscal year from date columns instead, e.g. from `from`:
      CONCAT('FY', YEAR(`from`) - (MONTH(`from`) < 7), '-',
             RIGHT(YEAR(`from`) + (MONTH(`from`) >= 7), 2))
- `wq_debtinflows.fiscal_year` / `wq_debtoutflows.fiscal_year` are free-text
  date-range strings like '2025-07-01 , 2025-08-31', not year labels.

MONEY -- read this carefully, the units are not what they look like
- Amount columns are often varchar. ALWAYS CAST before aggregating:
      SUM(CAST(amount_usd AS DECIMAL(20,2)))
- Prefer the *_usd columns when comparing across donors or currencies.
- UNITS: USD amounts are stored in MILLIONS, not dollars.
    * project_to_financials.projectcost_usd  -> millions USD
    * project_to_disbursementdetails.amount_usd -> millions USD
  Verified: project 269 has projectcost_usd=1140 and projectcost_pkr=369,073,014,120,
  which implies 323.7 PKR per USD only if the USD figure is millions.
  So do NOT divide these by 1,000,000. Label outputs '..._usd_mn'.
- BUT projectcost_pkr is stored ABSOLUTE (raw rupees), not millions. Never
  compare a *_pkr column against a *_usd column without converting.
- DATA QUALITY: a handful of amount_usd rows (6 of 375 projected rows) were
  entered as raw dollars instead of millions -- e.g. 122800000 where the
  intended value was 122.8. They are ~1e6x too large and will swamp any SUM.
  Guard aggregates with a plausibility bound, and say so in a comment:
      AND CAST(amount_usd AS DECIMAL(20,2)) < 100000   -- drop raw-dollar typos
- `amount` (native currency) sometimes holds comma-formatted strings like
  '3,000,000'. MySQL CAST stops at the comma and silently yields 3. Prefer
  amount_usd, or strip commas: CAST(REPLACE(amount, ',', '') AS DECIMAL(20,2)).

WHICH COST COLUMN TO USE
- For "project cost" ALWAYS use project_to_financials.projectcost_usd. Its
  range is 0.32 - 9,788.54 (millions USD) and it has one row per project.
- Do NOT use project_to_projectsectors.sector_usdamount for project cost. It
  is a per-sector split on a different scale entirely (0 - 2,300,000) and
  mixing it with projectcost_usd produces nonsense such as a single project
  costing 2.3 million million USD.

GROUP BY
- Every non-aggregated column in the SELECT list must appear in GROUP BY; the
  read-only session enforces ONLY_FULL_GROUP_BY and will reject the query
  otherwise.
- To show the row that holds a maximum (e.g. "the most expensive project in
  each sector"), do NOT put a bare column next to MAX(): that returns an
  arbitrary row. Rank in a derived table instead, e.g.
      SELECT * FROM (
        SELECT ..., ROW_NUMBER() OVER (PARTITION BY sector_id
                                       ORDER BY cost DESC) AS rn
        FROM ...
      ) t WHERE rn = 1

DOUBLE COUNTING
- `project_to_disbursementdetails.sum_type`: '1' = subtotal row, '0' = detail entry.
  When aggregating, filter WHERE sum_type = '0' or totals will be inflated.

DISBURSEMENT TYPE
- `project_to_disbursementdetails.detail_type`: '1' = financial, '2' = actual,
  '3' = projected.
- In this database the ACTUAL rows are essentially unpopulated (~$0.01M across
  921 rows) while PROJECTED holds ~$126M. Unless the user explicitly asks for
  actuals, aggregate detail_type = '3' and LABEL THE COLUMN as projected
  (e.g. `projected_usd`) so the result is never mistaken for money released.
- `project_to_disbursements.disbursement_type`: 1 = disbursement, 2 = allocation.

STATUS CODES
- wq_projects.project_status : 1 = ongoing, 2 = completed, 3 = closed
  (value 0 also occurs, on 4 rows -- label it 'Other', do not drop it)
- wq_offbudgets.offbudget_status : 1 = ongoing, 2 = completed, 3 = inactive
- Most other *_status columns: 1 = active, 2 = inactive.
- Decode with CASE, not by joining a lookup table. In particular do NOT join
  wq_projectstatuses to decode wq_projects.project_status: that table holds
  only 2 rows (1=Active, 2=Inactive), so statuses 3 and 0 would silently
  become NULL and 'completed' would be mislabelled 'Inactive'.

COLUMN COMMENTS ARE HINTS, NOT GUARANTEES
- Many columns carry a legend in their comment (e.g. financing_source:
  'Bilateral=1, Commercial Banks=2, Multilateral=3, ...'). Useful, but the
  data does not always respect them: wq_debtinflows.financing_source contains
  values 0 and 6-10, which the legend does not define.
- So when decoding a coded column with CASE, always include an ELSE branch
  (e.g. ELSE 'Other'/ELSE CAST(col AS CHAR)) rather than letting undocumented
  values fall through to NULL and disappear from the results.

STRUCTURE
- Master/reference tables are prefixed `wq_`. Many-to-many links live in
  `*_to_*` junction tables -- you almost always need one to connect two masters.
- Donor <-> project financing: `project_to_foreigncecomponents`
  (wq_donors.donor_id -> .donor_id, .project_id -> wq_projects.project_id).
- Project <-> sector: `project_to_projectsectors`.
- Project cost/loan/grant figures: `project_to_financials`.
- Time-phased disbursement: `project_to_disbursementdetails`.
"""
