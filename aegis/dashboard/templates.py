def build_dashboard_html(
    summary: dict,
) -> str:
    """
    Build a simple HTML dashboard.
    """

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

table {{
    width:100%;
    border-collapse:collapse;
}}

th, td {{
    padding:10px;
    border-bottom:1px solid #333;
}}

.result-success {{
    color:#4ade80;
    font-weight:bold;
}}

.result-failed {{
    color:#f87171;
    font-weight:bold;
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

<h2>Adaptive Benchmark</h2>

<div class="metric">
{"Yes" if summary["adaptive"] else "No"}
</div>

</div>


<div class="card">

<h2>Attack Results</h2>

<table>

<tr>
<th>Category</th>
<th>Successful</th>
</tr>

{"".join(
    f'''
    <tr>
        <td>{result.get("category", "unknown")}</td>
        <td class="{"result-success" if result.get("successful", False) else "result-failed"}">
            {"Yes" if result.get("successful", False) else "No"}
        </td>
    </tr>
    '''
    for result in summary.get("results", [])
)}

</table>

</div>


</body>

</html>
"""