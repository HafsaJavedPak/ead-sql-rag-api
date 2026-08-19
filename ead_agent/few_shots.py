"""Few-shot exemplars for generate_sql.

The original brief referenced a `smoke_test_queries.sql` that was never
supplied, so these were written against the live schema and each one is
verified to execute and return rows (see tests/test_few_shots.py).

They are chosen to teach the five things the model gets wrong unaided:
  1. junction-table joins (there are no foreign keys to copy from)
  2. CAST on varchar money columns
  3. sum_type = '0' to avoid double counting
  4. fiscal year derived from dates, never from wq_timeperiods
  5. status codes decoded to labels
"""

FEW_SHOTS: list[dict[str, str]] = [
    {
        "question": "Which donors have funded the most projects?",
        "sql": """
SELECT d.donor_name,
       COUNT(DISTINCT f.project_id) AS project_count
FROM wq_donors d
JOIN project_to_foreigncecomponents f ON d.donor_id = f.donor_id
JOIN wq_projects p ON f.project_id = p.project_id
GROUP BY d.donor_id, d.donor_name
ORDER BY project_count DESC
LIMIT 15
""".strip(),
        "note": (
            "Donor->project needs the project_to_foreigncecomponents junction; "
            "there is no direct FK."
        ),
    },
    {
        "question": "How many projects are ongoing versus completed?",
        "sql": """
SELECT CASE p.project_status
         WHEN 1 THEN 'Ongoing'
         WHEN 2 THEN 'Completed'
         WHEN 3 THEN 'Closed'
         ELSE 'Other'
       END AS status,
       COUNT(*) AS project_count
FROM wq_projects p
GROUP BY p.project_status
ORDER BY project_count DESC
""".strip(),
        "note": "Decode the numeric status into a label rather than returning 1/2/3.",
    },
    {
        "question": "How many projects went through the ECNEC approval forum?",
        "sql": """
SELECT COUNT(DISTINCT pa.project_id) AS project_count
FROM project_to_approvalforums pa
JOIN wq_approvalforums a ON pa.approvalforum_id = a.approvalforum_id
WHERE a.approvalforum_name = 'ECNEC'
""".strip(),
        "note": (
            "MINIMAL JOIN. Two tables answer this: the approval-forum junction "
            "and the forum lookup for the name filter. Do NOT add "
            "project_to_issues, wq_projects, or any other junction -- each extra "
            "join silently drops rows (this collapsed 111 to 7). "
            "COUNT(DISTINCT pa.project_id), never COUNT(*)."
        ),
    },
    {
        "question": "How many projects are there in each sector?",
        "sql": """
SELECT s.projectsector_name,
       COUNT(DISTINCT ps.project_id) AS project_count
FROM wq_projectsectors s
JOIN project_to_projectsectors ps ON s.projectsector_id = ps.projectsector_id
GROUP BY s.projectsector_id, s.projectsector_name
ORDER BY project_count DESC
LIMIT 20
""".strip(),
        "note": "Sector->project also goes through a junction table.",
    },
    {
        "question": "Show the projected disbursement trend by fiscal year",
        "sql": """
SELECT CONCAT('FY',
              YEAR(d.`from`) - (MONTH(d.`from`) < 7), '-',
              RIGHT(YEAR(d.`from`) + (MONTH(d.`from`) >= 7), 2)) AS fiscal_year,
       ROUND(SUM(CAST(d.amount_usd AS DECIMAL(20,2))), 2) AS projected_usd_mn
FROM project_to_disbursementdetails d
WHERE d.`from` IS NOT NULL
  AND d.sum_type = '0'                                  -- exclude subtotal rows
  AND d.detail_type = '3'                               -- 3 = projected
  AND CAST(d.amount_usd AS DECIMAL(20,2)) < 100000      -- drop raw-dollar typos
GROUP BY fiscal_year
HAVING SUM(CAST(d.amount_usd AS DECIMAL(20,2))) > 0
ORDER BY fiscal_year
""".strip(),
        "note": (
            "Fiscal year comes from the `from` date (1 Jul-30 Jun), NOT from "
            "wq_timeperiods which holds frequencies. sum_type='0' excludes "
            "subtotal rows. amount_usd is ALREADY in millions -- do not divide. "
            "The <100000 bound drops 6 rows entered as raw dollars."
        ),
    },
    {
        "question": "Compare total project cost against projected disbursement for the top sectors",
        "sql": """
SELECT s.projectsector_name,
       ROUND(cost.total_usd_mn, 2)          AS cost_usd_mn,
       ROUND(COALESCE(disb.projected_usd_mn, 0), 2) AS projected_usd_mn
FROM wq_projectsectors s
JOIN (
    SELECT ps.projectsector_id, SUM(f.projectcost_usd) AS total_usd_mn
    FROM project_to_projectsectors ps
    JOIN project_to_financials f ON ps.project_id = f.project_id
    GROUP BY ps.projectsector_id
) cost ON cost.projectsector_id = s.projectsector_id
LEFT JOIN (
    SELECT ps.projectsector_id,
           SUM(CAST(d.amount_usd AS DECIMAL(20,2))) AS projected_usd_mn
    FROM project_to_projectsectors ps
    JOIN project_to_disbursementdetails d ON ps.project_id = d.project_id
    WHERE d.sum_type = '0' AND d.detail_type = '3'
      AND CAST(d.amount_usd AS DECIMAL(20,2)) < 100000
    GROUP BY ps.projectsector_id
) disb ON disb.projectsector_id = s.projectsector_id
ORDER BY cost_usd_mn DESC
LIMIT 10
""".strip(),
        "note": (
            "Aggregate the disbursements in a subquery FIRST. Joining the detail "
            "table directly fans out the cost rows and inflates SUM(cost). Both "
            "columns are already in millions USD."
        ),
    },
    {
        "question": (
            "Show the top sectors by project cost together with the number of "
            "distinct donors and executing agencies involved"
        ),
        "sql": """
SELECT s.projectsector_name,
       ROUND(cost.total_usd_mn, 2)  AS total_cost_usd_mn,
       COALESCE(don.n_donors, 0)    AS distinct_donor_count,
       COALESCE(ag.n_agencies, 0)   AS distinct_agency_count
FROM wq_projectsectors s
JOIN (
    SELECT ps.projectsector_id, SUM(f.projectcost_usd) AS total_usd_mn
    FROM project_to_projectsectors ps
    JOIN project_to_financials f ON ps.project_id = f.project_id
    GROUP BY ps.projectsector_id
) cost ON cost.projectsector_id = s.projectsector_id
LEFT JOIN (
    SELECT ps.projectsector_id, COUNT(DISTINCT fc.donor_id) AS n_donors
    FROM project_to_projectsectors ps
    JOIN project_to_foreigncecomponents fc ON ps.project_id = fc.project_id
    GROUP BY ps.projectsector_id
) don ON don.projectsector_id = s.projectsector_id
LEFT JOIN (
    SELECT ps.projectsector_id, COUNT(DISTINCT e.executingagency_id) AS n_agencies
    FROM project_to_projectsectors ps
    JOIN project_to_executingencies e ON ps.project_id = e.project_id
    GROUP BY ps.projectsector_id
) ag ON ag.projectsector_id = s.projectsector_id
ORDER BY total_cost_usd_mn DESC
LIMIT 10
""".strip(),
        "note": (
            "SEVERAL MEASURES AT ONE GRAIN -- use this shape. Compute each "
            "measure in its OWN derived table, aggregated to the grouping key "
            "(projectsector_id), then join them. Never join the junctions "
            "side by side in one FROM: each extra one-to-many join multiplies "
            "the cost rows. Verified: this returns Energy = 19,626.90 mn; the "
            "naive single-FROM version returns 30,163.14 (+54%). Note each "
            "derived table GROUPs BY the join key ONLY."
        ),
    },
]


def render(max_examples: int = 5) -> str:
    """Format exemplars for the prompt."""
    out = []
    for ex in FEW_SHOTS[:max_examples]:
        out.append(f"-- Q: {ex['question']}\n-- {ex['note']}\n{ex['sql']}")
    return "\n\n".join(out)
