"""
Generates a self-contained HTML evaluation report from results.json.
"""

import json
from pathlib import Path


def _badge(value: float, thresholds=(0.6, 0.4)) -> str:
    """Return a coloured HTML badge for a 0-1 score."""
    if value >= thresholds[0]:
        color = "#22c55e"   # green
        label = "Good"
    elif value >= thresholds[1]:
        color = "#eab308"   # yellow
        label = "Fair"
    else:
        color = "#ef4444"   # red
        label = "Poor"
    return (
        f'<span style="background:{color};color:#fff;padding:2px 8px;'
        f'border-radius:12px;font-size:12px;font-weight:600">'
        f'{value:.2f} {label}</span>'
    )


def generate_report(results_path: str = "evaluation/results.json",
                    output_path: str = "evaluation/report.html") -> None:
    with open(results_path, encoding="utf-8") as f:
        data = json.load(f)

    summary = data["summary"]
    results = data["results"]

    # Build metric rows
    rows_html = ""
    for r in results:
        m = r["metrics"]
        err_cell = f'<td style="color:#ef4444">{r["error"]}</td>' if r["error"] else "<td>—</td>"
        conf_color = {"high": "#22c55e", "medium": "#eab308", "low": "#ef4444"}.get(r["confidence"], "#64748b")
        rows_html += f"""
        <tr>
          <td><strong>{r['id']}</strong><br><small style="color:#94a3b8">{r['question'][:70]}...</small></td>
          <td style="text-align:center">{_badge(m['faithfulness'])}</td>
          <td style="text-align:center">{_badge(m['answer_relevance'])}</td>
          <td style="text-align:center">{_badge(m['context_precision'])}</td>
          <td style="text-align:center">{_badge(m['reference_coverage'])}</td>
          <td style="text-align:center"><strong>{_badge(m['overall'])}</strong></td>
          <td style="text-align:center">{r['latency_s']}s</td>
          <td style="text-align:center;color:{conf_color}">{r['confidence']}</td>
          {err_cell}
        </tr>"""

    avg = summary.get("avg_metrics", {})
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>RegulatorIQ — Evaluation Report</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
          background:#0f172a; color:#e2e8f0; margin:0; padding:24px }}
  h1   {{ color:#fff; margin-bottom:4px }}
  h2   {{ color:#94a3b8; font-weight:500; font-size:14px; margin-bottom:32px }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(160px,1fr));
           gap:16px; margin-bottom:40px }}
  .card {{ background:#1e293b; border:1px solid #334155; border-radius:12px;
           padding:20px }}
  .card .val {{ font-size:28px; font-weight:700; color:#fff }}
  .card .lbl {{ font-size:12px; color:#64748b; margin-top:4px }}
  table {{ width:100%; border-collapse:collapse; background:#1e293b;
           border-radius:12px; overflow:hidden; font-size:13px }}
  th    {{ background:#0f172a; color:#94a3b8; padding:12px 8px;
           text-align:left; font-weight:600; font-size:11px;
           text-transform:uppercase; letter-spacing:.05em }}
  td    {{ padding:12px 8px; border-bottom:1px solid #334155; vertical-align:middle }}
  tr:last-child td {{ border-bottom:none }}
  tr:hover td {{ background:#0f172a }}
</style>
</head>
<body>
<h1>RegulatorIQ — Evaluation Report</h1>
<h2>Local RAG quality metrics · SEBI + RBI · phi3 + BAAI/bge-small-en-v1.5 · Qdrant</h2>

<div class="grid">
  <div class="card">
    <div class="val">{summary['total_questions']}</div>
    <div class="lbl">Total questions</div>
  </div>
  <div class="card">
    <div class="val">{summary['successful']}</div>
    <div class="lbl">Successful</div>
  </div>
  <div class="card">
    <div class="val">{summary['avg_latency_s']}s</div>
    <div class="lbl">Avg latency</div>
  </div>
  <div class="card">
    <div class="val">{int(summary['grounded_rate'] * 100)}%</div>
    <div class="lbl">Grounded rate</div>
  </div>
  <div class="card">
    <div class="val">{avg.get('faithfulness', 0):.2f}</div>
    <div class="lbl">Avg faithfulness</div>
  </div>
  <div class="card">
    <div class="val">{avg.get('overall', 0):.2f}</div>
    <div class="lbl">Avg overall score</div>
  </div>
</div>

<table>
  <thead>
    <tr>
      <th>Question</th>
      <th>Faithfulness</th>
      <th>Ans Relevance</th>
      <th>Ctx Precision</th>
      <th>Ref Coverage</th>
      <th>Overall</th>
      <th>Latency</th>
      <th>Confidence</th>
      <th>Error</th>
    </tr>
  </thead>
  <tbody>
    {rows_html}
  </tbody>
</table>

<p style="margin-top:24px;font-size:11px;color:#475569">
  Faithfulness: answer tokens in retrieved context |
  Answer relevance: question keywords in answer |
  Context precision: on-topic chunks retrieved |
  Reference coverage: key terms from eval dataset found in answer
</p>
</body>
</html>"""

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"HTML report saved to {output_path}")
