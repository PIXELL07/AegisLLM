import json

from aegis.dashboard.charts import (
    build_category_chart_data,
    build_latency_chart_data,
    build_score_chart_data,
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

    latency_data = build_latency_chart_data(
        summary,
    )

    score_data = build_score_chart_data(
        summary,
    )

    risk_level = get_risk_level(
        summary["risk_score"],
    )

    risk_class = risk_level.lower()

    summary_json = json.dumps(
        summary,
        indent=2,
    )

    max_latency = max(
        (
            item["latency_ms"]
            for item in latency_data
        ),
        default=0.0,
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

.risk-level.low {{
    color:#4ade80;
}}

.risk-level.medium {{
    color:#facc15;
}}

.risk-level.high {{
    color:#ff6b6b;
}}

.risk-score {{
    margin-top:8px;
    font-size:14px;
    color:#9ca3af;
}}

.download-button {{
    display:inline-block;
    padding:10px 16px;
    background:#2563eb;
    color:white;
    text-decoration:none;
    border-radius:6px;
    font-weight:bold;
    margin-bottom:20px;
}}

.summary-grid {{
    display:grid;
    grid-template-columns:repeat(3, 1fr);
    gap:16px;
}}

.summary-item {{
    background:#111827;
    padding:18px;
    border-radius:8px;
}}

.summary-label {{
    font-size:15px;
    color:#9ca3af;
    margin-bottom:8px;
}}

.summary-value {{
    font-size:24px;
    font-weight:bold;
    color:#4ade80;
}}

.summary-value.model {{
    font-size:20px;
}}

table {{
    width:100%;
    border-collapse:collapse;
    table-layout:fixed;
}}

th,
td {{
    padding:14px 16px;
    border-bottom:1px solid #333;
    text-align:left !important;
    vertical-align:top !important;
    line-height:1.5;
}}

th {{
    font-weight:bold;
}}

th:nth-child(1),
td:nth-child(1) {{
    width:18%;
}}

th:nth-child(2),
td:nth-child(2) {{
    width:16%;
}}

th:nth-child(3),
td:nth-child(3) {{
    width:10%;
}}

th:nth-child(4),
td:nth-child(4) {{
    width:14%;
}}

th:nth-child(5),
td:nth-child(5) {{
    width:12%;
}}

th:nth-child(6),
td:nth-child(6) {{
    width:30%;
}}

.response {{
    text-align:left !important;
    vertical-align:top !important;
    word-break:break-word;
    overflow-wrap:anywhere;
    white-space:normal;
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

.latency-row {{
    margin-bottom:20px;
}}

.latency-label {{
    display:flex;
    justify-content:space-between;
    margin-bottom:6px;
}}

.latency-background {{
    width:100%;
    height:20px;
    background:#374151;
    border-radius:10px;
    overflow:hidden;
}}

.latency-bar {{
    height:100%;
    background:#60a5fa;
}}

.score-row {{
    margin-bottom:20px;
}}

.score-label {{
    display:flex;
    justify-content:space-between;
    margin-bottom:6px;
}}

.score-background {{
    width:100%;
    height:20px;
    background:#374151;
    border-radius:10px;
    overflow:hidden;
}}

.score-bar {{
    height:100%;
    background:#f59e0b;
}}

.results-table {{
    overflow-x:auto;
}}

@media (max-width:900px) {{

    .summary-grid {{
        grid-template-columns:1fr;
    }}

}}

</style>

</head>

<body>

<h1>AegisLLM Security Dashboard</h1>


<a
    class="download-button"
    href="data:application/json;charset=utf-8,{summary_json}"
    download="dashboard-summary.json"
>
    Download JSON
</a>


<div class="card">

<h2>Dashboard Summary</h2>

<div class="summary-grid">

    <div class="summary-item">

        <div class="summary-label">
            Model
        </div>

        <div class="summary-value model">
            {summary["model"]}
        </div>

    </div>


    <div class="summary-item">

        <div class="summary-label">
            Total Attacks
        </div>

        <div class="summary-value">
            {summary["total_attacks"]}
        </div>

    </div>


    <div class="summary-item">

        <div class="summary-label">
            Successful Attacks
        </div>

        <div class="summary-value">
            {summary["successful_attacks"]}
        </div>

    </div>


    <div class="summary-item">

        <div class="summary-label">
            Attack Success Rate
        </div>

        <div class="summary-value">
            {summary["attack_success_rate"]:.2%}
        </div>

    </div>


    <div class="summary-item">

        <div class="summary-label">
            Average Latency
        </div>

        <div class="summary-value">
            {summary["average_latency_ms"]:.2f} ms
        </div>

    </div>


    <div class="summary-item">

        <div class="summary-label">
            Risk Level
        </div>

        <div class="summary-value">
            {risk_level}
        </div>

        <div class="risk-score">
            Risk Score: {summary["risk_score"]:.2f}
        </div>

    </div>

</div>

</div>


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

<h2>Successful Attacks</h2>

<div class="metric">
{summary["successful_attacks"]}
</div>

</div>


<div class="card">

<h2>Average Latency</h2>

<div class="metric">
{summary["average_latency_ms"]:.2f} ms
</div>

</div>


<div class="card">

<h2>Risk Score</h2>

<div class="metric">
{summary["risk_score"]:.2f}
</div>

<div class="risk-level {risk_class}">
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

<h2>Attack Latency</h2>

{
    "".join(
        f"""
        <div class="latency-row">

            <div class="latency-label">
                <span>{item["attack"]}</span>
                <span>{item["latency_ms"]:.2f} ms</span>
            </div>

            <div class="latency-background">

                <div
                    class="latency-bar"
                    style="width:{
                        (
                            item["latency_ms"]
                            / max_latency
                            * 100
                            if max_latency
                            else 0
                        )
                    }%"
                ></div>

            </div>

        </div>
        """
        for item in latency_data
    )
}

</div>


<div class="card">

<h2>Attack Score</h2>

{
    "".join(
        f"""
        <div class="score-row">

            <div class="score-label">
                <span>{item["attack"]}</span>
                <span>{item["score"]:.2f}</span>
            </div>

            <div class="score-background">

                <div
                    class="score-bar"
                    style="width:{item["score"] * 100}%"
                ></div>

            </div>

        </div>
        """
        for item in score_data
    )
}

</div>


<div class="card">

<h2>Attack Results</h2>

<div class="results-table">

<table>

<thead>

<tr>
    <th>Attack</th>
    <th>Category</th>
    <th>Score</th>
    <th>Latency</th>
    <th>Successful</th>
    <th>Response</th>
</tr>

</thead>

<tbody>

{
    "".join(
        f"""
        <tr>

            <td>
                {result.get("attack", "unknown")}
            </td>

            <td>
                {result.get("category", "unknown")}
            </td>

            <td>
                {result.get("score", 0.0):.2f}
            </td>

            <td>
                {result.get("latency_ms", 0.0):.2f} ms
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

            <td class="response">
                {result.get("response", "N/A")}
            </td>

        </tr>
        """
        for result in summary.get(
            "results",
            [],
        )
    )
}

</tbody>

</table>

</div>

</div>


</body>

</html>
"""