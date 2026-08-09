import json
from datetime import datetime
from urllib.parse import quote

from aegis.dashboard.builder import (
    build_results_csv,
)

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

    generated_at = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    summary_json = json.dumps(
        summary,
        indent=2,
    )

    encoded_json = quote(
        summary_json,
    )

    results_csv = build_results_csv(
        summary,
    )

    encoded_csv = quote(
        results_csv,
    )

    max_latency = max(
        (
            item["latency_ms"]
            for item in latency_data
        ),
        default=0.0,
    )

    categories = sorted(
        {
            result.get(
                "category",
                "unknown",
            )
            for result in summary.get(
                "results",
                [],
            )
        }
    )

    return f"""
<!DOCTYPE html>
<html lang="en">

<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
>

<title>AegisLLM Dashboard</title>

<style>

body {{
    font-family: Arial, Helvetica, sans-serif;
    background:#111827;
    color:white;
    margin:40px;
}}

".dashboard-nav {{
    position:sticky;
    top:0;
    z-index:1000;
    display:flex;
    gap:8px;
    flex-wrap:wrap;
    padding:12px;
    margin-bottom:20px;
    background:#1f2937;
    border:1px solid #374151;
    border-radius:10px;
}}

.dashboard-nav a {{
    padding:8px 14px;
    border-radius:6px;
    background:#111827;
    color:white;
    text-decoration:none;
    font-size:14px;
    font-weight:bold;
}}

.dashboard-nav a:hover {{
    background:#2563eb;
}}

html {{
    scroll-behavior:smooth;
}}

h2 {{
    scroll-margin-top:80px;
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

.generated-at {{
    font-size:14px;
    color:#9ca3af;
    margin-top:8px;
}}

.risk-banner {{
    padding:18px 20px;
    border-radius:10px;
    margin-bottom:20px;
    font-size:20px;
    font-weight:bold;
}}

.risk-banner.low {{
    background:#14532d;
    color:#86efac;
    border:1px solid #22c55e;
}}

.risk-banner.medium {{
    background:#713f12;
    color:#fde047;
    border:1px solid #eab308;
}}

.risk-banner.high {{
    background:#7f1d1d;
    color:#fca5a5;
    border:1px solid #ef4444;
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
    margin-right:8px;
}}

.download-button.csv {{
    background:#059669;
}}

.benchmark-metadata {{
    display:grid;
    grid-template-columns:repeat(4, 1fr);
    gap:16px;
    margin-bottom:20px;
}}

.metadata-item {{
    background:#111827;
    padding:16px;
    border-radius:8px;
}}

.metadata-label {{
    font-size:14px;
    color:#9ca3af;
    margin-bottom:6px;
}}

.metadata-value {{
    font-size:18px;
    font-weight:bold;
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

.empty-state {{
    text-align:center;
    padding:30px 20px;
    color:#9ca3af;
    font-size:16px;
    background:#111827;
    border-radius:8px;
}}

.chart-controls {{
    display:flex;
    align-items:center;
    gap:10px;
    flex-wrap:wrap;
    margin-bottom:20px;
}}

.chart-control-button {{
    padding:8px 14px;
    border:1px solid #4b5563;
    border-radius:6px;
    background:#111827;
    color:white;
    cursor:pointer;
    font-weight:bold;
}}

.chart-control-button:hover {{
    background:#374151;
}}

.chart-control-button.active {{
    background:#2563eb;
    border-color:#2563eb;
}}

.chart-select {{
    padding:8px 12px;
    border:1px solid #4b5563;
    border-radius:6px;
    background:#111827;
    color:white;
    cursor:pointer;
}}

.filter-controls {{
    display:flex;
    align-items:center;
    gap:10px;
    flex-wrap:wrap;
    margin-bottom:15px;
}}

.filter-label {{
    color:#9ca3af;
    font-weight:bold;
}}

.filter-select {{
    padding:8px 12px;
    border:1px solid #4b5563;
    border-radius:6px;
    background:#111827;
    color:white;
    cursor:pointer;
}}

.filter-button {{
    padding:8px 14px;
    border:1px solid #4b5563;
    border-radius:6px;
    background:#2563eb;
    color:white;
    cursor:pointer;
    font-weight:bold;
}}

.filter-button:hover {{
    background:#1d4ed8;
}}

.filter-count {{
    margin-bottom:15px;
    color:#9ca3af;
    font-size:14px;
}}

.search-controls {{
    display:flex;
    align-items:center;
    gap:10px;
    margin-bottom:15px;
}}

.search-input {{
    flex:1;
    padding:10px 12px;
    border:1px solid #4b5563;
    border-radius:6px;
    background:#111827;
    color:white;
    font-size:15px;
}}

.search-input::placeholder {{
    color:#9ca3af;
}}

.search-input:focus {{
    outline:none;
    border-color:#2563eb;
}}

.search-button {{
    padding:10px 16px;
    border:1px solid #2563eb;
    border-radius:6px;
    background:#2563eb;
    color:white;
    cursor:pointer;
    font-weight:bold;
}}

.search-button:hover {{
    background:#1d4ed8;
}}

.no-filter-results {{
    display:none;
    text-align:center;
    padding:30px 20px;
    color:#9ca3af;
    background:#111827;
    border-radius:8px;
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
    -webkit-overflow-scrolling:touch;
}}


@media (max-width:900px) {{

    body {{
        margin:20px;
    }}

    .summary-grid {{
        grid-template-columns:repeat(2, minmax(0, 1fr));
    }}

    .benchmark-metadata {{
        grid-template-columns:repeat(2, minmax(0, 1fr));
    }}

    .card {{
        padding:18px;
    }}

    table {{
        font-size:14px;
    }}

    th,
    td {{
        padding:10px 12px;
    }}

}}


@media (max-width:600px) {{

    body {{
        margin:12px;
    }}

    h1 {{
        font-size:28px;
    }}

    h2 {{
        font-size:22px;
    }}

    .summary-grid {{
        grid-template-columns:1fr;
    }}

    .benchmark-metadata {{
        grid-template-columns:1fr;
    }}

    .card {{
        padding:16px;
        margin-bottom:14px;
    }}

    .metric {{
        font-size:26px;
    }}

    .results-table {{
        overflow-x:auto;
        -webkit-overflow-scrolling:touch;
    }}

    table {{
        min-width:700px;
    }}

    th,
    td {{
        padding:10px;
        white-space:nowrap;
    }}

    .response {{
        white-space:normal;
        word-break:break-word;
        overflow-wrap:anywhere;
    }}

    .download-button {{
        width:100%;
        box-sizing:border-box;
        text-align:center;
        margin-right:0;
    }}

    .chart-controls,
    .filter-controls,
    .search-controls {{
        align-items:stretch;
        flex-direction:column;
    }}

    .chart-control-button,
    .chart-select,
    .filter-select,
    .filter-button,
    .search-input,
    .search-button {{
        width:100%;
        box-sizing:border-box;
    }}

    .risk-banner {{
        font-size:18px;
        padding:16px;
    }}

}}

</style>

</head>

<body>

<nav class="dashboard-nav">

    <a href="#summary">
        Summary
    </a>

    <a href="#category-analysis">
        Categories
    </a>

    <a href="#latency-analysis">
        Latency
    </a>

    <a href="#score-analysis">
        Scores
    </a>

    <a href="#attack-results">
        Attack Results
    </a>

</nav>

<h1>AegisLLM Security Dashboard</h1>


<div class="risk-banner {risk_class}">

    Overall Risk:
    {risk_level}

    &nbsp; | &nbsp;

    Risk Score:
    {summary["risk_score"]:.2f}

</div>


<div class="card">

<h2>Benchmark Information</h2>

<div class="benchmark-metadata">

    <div class="metadata-item">

        <div class="metadata-label">
            Model
        </div>

        <div class="metadata-value">
            {summary["model"]}
        </div>

    </div>


    <div class="metadata-item">

        <div class="metadata-label">
            Adaptive Mode
        </div>

        <div class="metadata-value">
            {"Enabled" if summary["adaptive"] else "Disabled"}
        </div>

    </div>


    <div class="metadata-item">

        <div class="metadata-label">
            Total Attacks
        </div>

        <div class="metadata-value">
            {summary["total_attacks"]}
        </div>

    </div>


    <div class="metadata-item">

        <div class="metadata-label">
            Generated At
        </div>

        <div class="metadata-value">
            {generated_at}
        </div>

    </div>

</div>

</div>


<a
    class="download-button"
    href="data:application/json;charset=utf-8,{encoded_json}"
    download="dashboard-summary.json"
>
    Download JSON
</a>


<a
    class="download-button csv"
    href="data:text/csv;charset=utf-8,{encoded_csv}"
    download="attack-results.csv"
>
    Download CSV
</a>


<div class="card">

<h2 id="summary">Dashboard Summary</h2>

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

<div class="generated-at">
    Generated At: {generated_at}
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

<h2 id="category-analysis">Attack Success Rate by Category</h2>

<div class="chart-controls">

    <span>
        Category View:
    </span>

    <button
        id="categoryRateButton"
        class="chart-control-button active"
        onclick="toggleCategoryView('rate')"
    >
        Percentage
    </button>

    <button
        id="categoryCountButton"
        class="chart-control-button"
        onclick="toggleCategoryView('count')"
    >
        Count
    </button>

</div>


<div id="categoryChart">

{
    (
        "".join(
            f"""
            <div
                class="chart-row"
                data-rate="{item["attack_success_rate"]}"
                data-total="{item["total"]}"
                data-successful="{item["successful"]}"
            >

                <div class="chart-label">

                    <span>
                        {item["category"]}
                    </span>

                    <span class="category-value">
                        {item["attack_success_rate"]:.2%}
                    </span>

                </div>

                <div class="chart-background">

                    <div
                        class="chart-bar category-bar"
                        style="width:{item["attack_success_rate"] * 100}%"
                    ></div>

                </div>

            </div>
            """
            for item in chart_data
        )
        if chart_data
        else """
        <div class="empty-state">
            No attack category data available.
        </div>
        """
    )
}

</div>

</div>


<div class="card">

<h2 id="latency-analysis">Attack Latency</h2>

<div class="chart-controls">

    <label for="latencySort">
        Latency Sort:
    </label>

    <select
        id="latencySort"
        class="chart-select"
        onchange="sortLatency(this.value)"
    >

        <option value="original">
            Original Order
        </option>

        <option value="ascending">
            Lowest First
        </option>

        <option value="descending">
            Highest First
        </option>

    </select>

</div>


<div id="latencyChart">

{
    (
        "".join(
            f"""
            <div
                class="latency-row"
                data-latency="{item["latency_ms"]}"
            >

                <div class="latency-label">

                    <span>
                        {item["attack"]}
                    </span>

                    <span>
                        {item["latency_ms"]:.2f} ms
                    </span>

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
        if latency_data
        else """
        <div class="empty-state">
            No attack latency data available.
        </div>
        """
    )
}

</div>

</div>


<div class="card">

<h2 id="score-analysis">Attack Score</h2>

<div class="chart-controls">

    <label for="scoreSort">
        Score Sort:
    </label>

    <select
        id="scoreSort"
        class="chart-select"
        onchange="sortScores(this.value)"
    >

        <option value="original">
            Original Order
        </option>

        <option value="ascending">
            Lowest First
        </option>

        <option value="descending">
            Highest First
        </option>

    </select>

</div>


<div id="scoreChart">

{
    (
        "".join(
            f"""
            <div
                class="score-row"
                data-score="{item["score"]}"
            >

                <div class="score-label">

                    <span>
                        {item["attack"]}
                    </span>

                    <span>
                        {item["score"]:.2f}
                    </span>

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
        if score_data
        else """
        <div class="empty-state">
            No attack score data available.
        </div>
        """
    )
}

</div>

</div>


<div class="card">

<h2 id="attack-results">Attack Results</h2>


<div class="search-controls">

    <label for="attackSearch">
        Search
    </label>

    <input
        id="attackSearch"
        class="search-input"
        type="search"
        placeholder="Search attack, category, or response..."
        oninput="filterAttackResults()"
    >

    <button
        class="search-button"
        onclick="clearAttackSearch()"
    >
        Clear Search
    </button>

</div>


<div class="filter-controls">

    <span class="filter-label">
        Filters:
    </span>

    <label for="categoryFilter">
        Category
    </label>

    <select
        id="categoryFilter"
        class="filter-select"
        onchange="filterAttackResults()"
    >

        <option value="all">
            All Categories
        </option>

        {
            "".join(
                f"""
                <option value="{category}">
                    {category}
                </option>
                """
                for category in categories
            )
        }

    </select>


    <label for="resultFilter">
        Result
    </label>

    <select
        id="resultFilter"
        class="filter-select"
        onchange="filterAttackResults()"
    >

        <option value="all">
            All Results
        </option>

        <option value="successful">
            Successful
        </option>

        <option value="failed">
            Failed
        </option>

    </select>


    <button
        class="filter-button"
        onclick="clearAttackFilters()"
    >
        Clear Filters
    </button>

</div>


<div
    id="filterCount"
    class="filter-count"
>
    Showing {len(summary.get("results", []))}
    of {len(summary.get("results", []))}
    attacks
</div>


{
    (
        f"""
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

        <tbody id="attackResultsBody">

        {
            "".join(
                f"""
                <tr
                    data-category="{result.get("category", "unknown")}"
                    data-successful="{
                        "true"
                        if result.get("successful", False)
                        else "false"
                    }"
                    data-search="{
                        (
                            str(result.get("attack", "unknown"))
                            + " "
                            + str(result.get("category", "unknown"))
                            + " "
                            + str(result.get("response", "N/A"))
                        ).lower()
                    }"
                >

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
        """
        if summary.get("results", [])
        else """
        <div class="empty-state">
            No attack results available.
        </div>
        """
    )
}


<div
    id="noFilterResults"
    class="no-filter-results"
>
    No attacks match the selected filters.
</div>

</div>


<script>

function toggleCategoryView(view) {{

    const rows = document.querySelectorAll(
        "#categoryChart .chart-row"
    );

    const rateButton = document.getElementById(
        "categoryRateButton"
    );

    const countButton = document.getElementById(
        "categoryCountButton"
    );

    rows.forEach(function(row) {{

        const valueElement = row.querySelector(
            ".category-value"
        );

        const rate = parseFloat(
            row.dataset.rate
        );

        const total = parseFloat(
            row.dataset.total
        );

        const successful = parseFloat(
            row.dataset.successful
        );

        const barElement = row.querySelector(
            ".category-bar"
        );

        if (view === "count") {{

            valueElement.textContent =
                successful + " / " + total;

            const width =
                total > 0
                    ? (successful / total) * 100
                    : 0;

            barElement.style.width =
                width + "%";

        }} else {{

            valueElement.textContent =
                (rate * 100).toFixed(2) + "%";

            barElement.style.width =
                (rate * 100) + "%";
        }}

    }});

    rateButton.classList.toggle(
        "active",
        view === "rate"
    );

    countButton.classList.toggle(
        "active",
        view === "count"
    );
}}


function sortLatency(order) {{

    const container = document.getElementById(
        "latencyChart"
    );

    const rows = Array.from(
        container.querySelectorAll(
            ".latency-row"
        )
    );

    if (order === "ascending") {{

        rows.sort(function(a, b) {{
            return (
                parseFloat(a.dataset.latency)
                -
                parseFloat(b.dataset.latency)
            );
        }});

    }} else if (order === "descending") {{

        rows.sort(function(a, b) {{
            return (
                parseFloat(b.dataset.latency)
                -
                parseFloat(a.dataset.latency)
            );
        }});

    }}

    rows.forEach(function(row) {{
        container.appendChild(row);
    }});
}}


function sortScores(order) {{

    const container = document.getElementById(
        "scoreChart"
    );

    const rows = Array.from(
        container.querySelectorAll(
            ".score-row"
        )
    );

    if (order === "ascending") {{

        rows.sort(function(a, b) {{
            return (
                parseFloat(a.dataset.score)
                -
                parseFloat(b.dataset.score)
            );
        }});

    }} else if (order === "descending") {{

        rows.sort(function(a, b) {{
            return (
                parseFloat(b.dataset.score)
                -
                parseFloat(a.dataset.score)
            );
        }});

    }}

    rows.forEach(function(row) {{
        container.appendChild(row);
    }});
}}


function filterAttackResults() {{

    const categoryFilter =
        document.getElementById(
            "categoryFilter"
        ).value;

    const resultFilter =
        document.getElementById(
            "resultFilter"
        ).value;

    const searchInput =
        document.getElementById(
            "attackSearch"
        );

    const searchTerm =
        searchInput
            ? searchInput.value
                .trim()
                .toLowerCase()
            : "";

    const rows = document.querySelectorAll(
        "#attackResultsBody tr"
    );

    let visibleCount = 0;

    rows.forEach(function(row) {{

        const category =
            row.dataset.category;

        const successful =
            row.dataset.successful === "true";

        const searchableText =
            row.dataset.search || "";

        const categoryMatches =
            categoryFilter === "all"
            ||
            category === categoryFilter;

        const resultMatches =
            resultFilter === "all"
            ||
            (
                resultFilter === "successful"
                && successful
            )
            ||
            (
                resultFilter === "failed"
                && !successful
            );

        const searchMatches =
            searchTerm === ""
            ||
            searchableText.includes(
                searchTerm
            );

        const visible =
            categoryMatches
            &&
            resultMatches
            &&
            searchMatches;

        row.style.display =
            visible
                ? ""
                : "none";

        if (visible) {{
            visibleCount++;
        }}

    }});

    const totalCount = rows.length;

    document.getElementById(
        "filterCount"
    ).textContent =
        "Showing "
        + visibleCount
        + " of "
        + totalCount
        + " attacks";

    document.getElementById(
        "noFilterResults"
    ).style.display =
        visibleCount === 0
            ? "block"
            : "none";
}}


function clearAttackFilters() {{

    document.getElementById(
        "categoryFilter"
    ).value = "all";

    document.getElementById(
        "resultFilter"
    ).value = "all";

    const searchInput =
        document.getElementById(
            "attackSearch"
        );

    if (searchInput) {{
        searchInput.value = "";
    }}

    filterAttackResults();
}}


function clearAttackSearch() {{

    const searchInput =
        document.getElementById(
            "attackSearch"
        );

    if (searchInput) {{
        searchInput.value = "";
    }}

    filterAttackResults();

    if (searchInput) {{
        searchInput.focus();
    }}
}}

</script>


</body>

</html>
"""