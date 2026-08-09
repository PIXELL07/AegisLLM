from aegis.dashboard.charts import (
    build_category_chart_data,
    get_risk_level,
)


def build_dashboard_html(
    summary: dict,
) -> str:
    """
    Build a simple HTML dashboard.
    """

    chart_data = build_category_chart_data(
        summary,
    )

    risk_level = get_risk_level(
        summary["risk_score"],
    )

    return f"""
<!DOCTYPE html>
<html lang="en">

<head>

<meta charset="UTF-8">

<title>AegisLLM Dashboard</title>

<style>

body {{
    font-family: Arial, Helvetica, sans-serif;
    background:#111827;
    color:white;
    margin:40px;
}}

.card {{
    background:#1f2937;
    padding:20px;
    border-radius:10px;
    margin-bottom:20px;
}}

.metric {{
    font-size:32px;
    font-weight:bold;
    color:#4ade80;
}}

.risk-level {{
    font-size:24px;
    font-weight:bold;
    margin-top:10px;
}}

table {{
    width:100%;
    border-collapse:collapse;
    table-layout:fixed;
}}

th, td {{
    padding:12px 16px;
    border-bottom:1px solid #333;
    text-align:left;
}}

th:first-child,
td:first-child {{
    width:50%;
}}

th:last-child,
td:last-child {{
    width:50%;
}}

.success {{
    color:#4ade80;
    font-weight:bold;
}}

.failure {{
    color:#ff6b6b;
    font-weight:bold;
}}

.chart-row {{
    margin-bottom:20px;
}}

.chart-label {{
    display:flex;
    justify-content:space-between;
    margin-bottom:6px;
}}

.chart-background {{
    width:100%;
    height:20px;
    background:#374151;
    border-radius:10px;
    overflow:hidden;
}}

.chart-bar {{
    height:100%;
    background:#4ade80;
}}

</style>

</head>

<body>

<h1>AegisLLM Security Dashboard</h1>


<div class="card">

<h2>Model</h2>

<div class="metric">
{summary["model"]}
</div>

</div>


<div class="card">

<h2>Attack Success Rate</h2>

<div class="metric">
{summary["attack_success_rate"]:.2%}
</div>

</div>


<div class="card">

<h2>Total Attacks</h2>

<div class="metric">
{summary["total_attacks"]}
</div>

</div>


<div class="card">

<h2>Risk Score</h2>

<div class="metric">
{summary["risk_score"]:.2f}
</div>

<div class="risk-level">
Risk Level: {risk_level}
</div>

</div>


<div class="card">

<h2>Adaptive Benchmark</h2>

<div class="metric">
{"Yes" if summary["adaptive"] else "No"}
</div>

</div>


<div class="card">

<h2>Attack Success Rate by Category</h2>

{
    "".join(
        f"""
        <div class="chart-row">

            <div class="chart-label">
                <span>{item["category"]}</span>
                <span>{item["attack_success_rate"]:.2%}</span>
            </div>

            <div class="chart-background">

                <div
                    class="chart-bar"
                    style="width:{item["attack_success_rate"] * 100}%"
                ></div>

            </div>

        </div>
        """
        for item in chart_data
    )
}

</div>


<div class="card">

<h2>Attack Results</h2>

<table>

<tr>
    <th>Category</th>
    <th>Successful</th>
</tr>

{
    "".join(
        f"""
        <tr>

            <td>
                {result.get("category", "unknown")}
            </td>

            <td class="{
                "success"
                if result.get("successful", False)
                else "failure"
            }">

                {
                    "Yes"
                    if result.get("successful", False)
                    else "No"
                }

            </td>

        </tr>
        """
        for result in summary.get("results", [])
    )
}

</table>

</div>


</body>

</html>
"""