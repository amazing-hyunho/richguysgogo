from __future__ import annotations

import json
import sqlite3
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
DB_PATH = ROOT_DIR / "data" / "investment.db"
RUNS_DIR = ROOT_DIR / "runs"
OUTPUT_PATH = ROOT_DIR / "docs" / "dashboard.html"


def fetch_rows(conn: sqlite3.Connection, query: str) -> list[dict[str, object]]:
    conn.row_factory = sqlite3.Row
    return [dict(row) for row in conn.execute(query).fetchall()]


def load_committee_history() -> list[dict[str, object]]:
    history: list[dict[str, object]] = []
    for path in sorted(RUNS_DIR.glob("*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue

        committee = payload.get("committee_result", {})
        guidance = committee.get("ops_guidance", [])
        history.append(
            {
                "market_date": payload.get("market_date", path.stem),
                "consensus": committee.get("consensus", ""),
                "ok_count": sum(1 for item in guidance if item.get("level") == "OK"),
                "caution_count": sum(1 for item in guidance if item.get("level") == "CAUTION"),
                "avoid_count": sum(1 for item in guidance if item.get("level") == "AVOID"),
            }
        )
    return history


def load_latest_stances() -> dict[str, object]:
    latest_path = max(RUNS_DIR.glob("*.json"), default=None)
    if latest_path is None:
        return {"market_date": "-", "stances": []}

    try:
        payload = json.loads(latest_path.read_text(encoding="utf-8"))
    except Exception:
        return {"market_date": latest_path.stem, "stances": []}

    stances = []
    for stance in payload.get("stances", []):
        stances.append(
            {
                "agent_name": stance.get("agent_name", "-"),
                "regime_tag": stance.get("regime_tag", "-"),
                "confidence": stance.get("confidence", "-"),
                "korean_comment": stance.get("korean_comment", ""),
                "core_claims": stance.get("core_claims", []),
            }
        )

    return {
        "market_date": payload.get("market_date", latest_path.stem),
        "stances": stances,
    }



def load_latest_committee() -> dict[str, object]:
    latest_path = max(RUNS_DIR.glob("*.json"), default=None)
    if latest_path is None:
        return {"market_date": "-", "consensus": "-", "key_points": [], "ops_guidance": []}

    try:
        payload = json.loads(latest_path.read_text(encoding="utf-8"))
    except Exception:
        return {"market_date": latest_path.stem, "consensus": "-", "key_points": [], "ops_guidance": []}

    committee = payload.get("committee_result", {}) or {}
    key_points = [item.get("point", "") for item in committee.get("key_points", []) if item.get("point")]
    ops_guidance = [
        {
            "level": item.get("level", ""),
            "text": item.get("text", ""),
        }
        for item in committee.get("ops_guidance", [])
        if isinstance(item, dict)
    ]
    return {
        "market_date": payload.get("market_date", latest_path.stem),
        "consensus": committee.get("consensus", ""),
        "key_points": key_points[:3],
        "ops_guidance": ops_guidance[:3],
    }

def build_dashboard_html(data: dict[str, object]) -> str:
    data_json = json.dumps(data, ensure_ascii=False)
    return f"""<!doctype html>
<html lang=\"ko\">
<head>
  <meta charset=\"UTF-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
  <title>AI 투자위원회 데이터 대시보드</title>
  <script src=\"https://cdn.jsdelivr.net/npm/chart.js\"></script>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; background:#0f172a; color:#e2e8f0; }}
    .container {{ max-width: 1200px; margin: 0 auto; padding: 24px; }}
    h1 {{ margin: 0 0 20px 0; }}
    .cards {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:12px; margin-bottom:20px; }}
    .card {{ background:#1e293b; border-radius:12px; padding:14px; }}
    .card .label {{ font-size:12px; color:#94a3b8; }}
    .card .value {{ margin-top:6px; font-size:24px; font-weight:700; }}
    .chart-grid {{ display:grid; grid-template-columns:1fr 1fr; gap:16px; }}
    .panel {{ background:#1e293b; border-radius:12px; padding:14px; }}
    .panel h2 {{ margin-top:0; font-size:16px; }}
    table {{ width:100%; border-collapse:collapse; font-size:13px; }}
    th, td {{ border-bottom:1px solid #334155; padding:8px 6px; text-align:left; vertical-align:top; }}
    .full {{ margin-top:16px; }}
    .badge {{ display:inline-block; margin-left:8px; font-size:12px; color:#93c5fd; }}
    .agent-table td ul {{ margin:6px 0 0 16px; padding:0; }}
    .agent-table td li {{ margin-bottom:2px; }}
    .help-box {{ margin-top:10px; padding:10px 12px; border-radius:10px; background:#0b1220; border:1px solid #334155; font-size:12px; line-height:1.5; color:#cbd5e1; }}
    .help-box strong {{ color:#e2e8f0; }}
    @media (max-width: 900px) {{ .chart-grid {{ grid-template-columns:1fr; }} }}
  </style>
</head>
<body>
  <div class=\"container\">
    <h1>📊 AI 투자위원회 누적 데이터 대시보드</h1>
    <div class=\"cards\" id=\"summary-cards\"></div>

    <div class=\"chart-grid\">
      <div class=\"panel\">
        <h2>주요 지수 일간 변화율 (%)</h2>
        <canvas id=\"marketChart\"></canvas>
      </div>
      <div class=\"panel\">
        <h2>거시 지표 (VIX / USDKRW)</h2>
        <canvas id=\"macroChart\"></canvas>
      </div>
      <div class=\"panel\">
        <h2>외국인 순매수 추이</h2>
        <canvas id=\"flowChart\"></canvas>
      </div>
      <div class=\"panel\">
        <h2>위원회 운영 가이던스 횟수</h2>
        <canvas id="guidanceChart"></canvas>
        <div class="help-box">
          <div><strong>가이던스 3단계 의미</strong></div>
          <div>• <strong>유지(OK)</strong>: 현재 전략 유지(기존 비중 중심)</div>
          <div>• <strong>주의(CAUTION)</strong>: 신규 진입/추가 매수는 신중, 리스크 한도 강화</div>
          <div>• <strong>회피(AVOID)</strong>: 해당 행동·자산은 당분간 피하기</div>
        </div>
      </div>
    </div>

    <div class=\"panel full\">
      <h2>최근 의장 의견 <span class=\"badge\" id=\"chairDate\"></span></h2>
      <div id=\"chairConsensus\">-</div>
      <ul id=\"chairKeyPoints\"></ul>
      <ul id=\"chairGuidance\"></ul>
    </div>

    <div class=\"panel full\">
      <h2>최근 회의 합의 내역</h2>
      <table>
        <thead><tr><th>날짜</th><th>의장 합의</th><th>유지(OK)</th><th>주의(CAUTION)</th><th>회피(AVOID)</th></tr></thead>
        <tbody id=\"committeeTable\"></tbody>
      </table>
    </div>

    <div class=\"panel full\">
      <h2>최근 에이전트 의견 <span class=\"badge\" id=\"stanceDate\"></span></h2>
      <table class=\"agent-table\">
        <thead><tr><th>에이전트</th><th>국면 태그</th><th>신뢰도</th><th>의견</th><th>핵심 주장</th></tr></thead>
        <tbody id=\"stanceTable\"></tbody>
      </table>
    </div>
  </div>

<script>
const data = {data_json};

const LABEL_BY_LEVEL = {{
  OK: '유지',
  CAUTION: '주의',
  AVOID: '회피',
}};

const REGIME_LABELS = {{
  RISK_ON: 'RISK_ON (비중 확대)',
  RISK_OFF: 'RISK_OFF (비중 축소)',
  NEUTRAL: 'NEUTRAL (중립 비중)',
}};

const CHAIR_TEXT_MAP = {{
  'Committee agrees on a neutral stance with selective monitoring.': '위원회는 선별적 모니터링 하에 중립 스탠스를 유지합니다.',
  'Committee maintains a neutral posture with selective positioning.': '위원회는 선별적 포지셔닝을 전제로 중립적 입장을 유지합니다.',
  'Committee adopts a defensive posture and reduces risk exposure.': '위원회는 방어적 입장을 채택하고 위험 노출을 축소합니다.',
  'Committee supports risk-on positioning with disciplined risk controls.': '위원회는 엄격한 리스크 통제를 전제로 위험자산 비중 확대를 지지합니다.',
  'Majority regime tag: RISK_ON.': '다수 국면 태그: RISK_ON (비중 확대).',
  'Majority regime tag: RISK_OFF.': '다수 국면 태그: RISK_OFF (비중 축소).',
  'Majority regime tag: NEUTRAL.': '다수 국면 태그: NEUTRAL (중립 비중).',
  'Shared evidence focus: snapshot.news_headlines.': '공통 근거: snapshot.news_headlines.',
  'Shared evidence focus: snapshot.market_summary.note.': '공통 근거: snapshot.market_summary.note.',
  'Maintain balanced exposure.': '균형 비중을 유지합니다.',
  'Keep risk limits tight.': '리스크 한도를 엄격히 유지합니다.',
  'Avoid aggressive leverage.': '과도한 레버리지는 피합니다.',
  'Lean into confirmed momentum leaders.': '검증된 모멘텀 주도주 중심으로 대응합니다.',
  'Size positions with volatility limits.': '변동성 한도 내에서 포지션 규모를 조절합니다.',
  'Avoid chasing overstretched breakouts.': '과열된 돌파 구간 추격 매수는 피합니다.',
  'Keep exposure focused on resilience.': '방어력이 높은 자산 중심으로 노출을 유지합니다.',
  'Favor defensive positioning.': '방어적인 포지셔닝을 우선합니다.',
  'Avoid high-beta risk assets.': '고베타 위험자산은 피합니다.',
}};

function formatRegimeTag(tag) {{
  return REGIME_LABELS[tag] || tag || '-';
}}

function toKoreanChairText(text) {{
  return CHAIR_TEXT_MAP[text] || text || '-';
}}

function formatGuidanceLevel(level) {{
  return LABEL_BY_LEVEL[level] ? `${{level}} · ${{LABEL_BY_LEVEL[level]}}` : (level || '-');
}}

function latest(rows, key) {{
  if (!rows.length) return '-';
  const value = rows[rows.length - 1][key];
  return value ?? '-';
}}

const cards = [
  {{ label: '최근 KOSPI(%)', value: latest(data.market_daily, 'kospi_pct') }},
  {{ label: '최근 NASDAQ(%)', value: latest(data.market_daily, 'nasdaq_pct') }},
  {{ label: '최근 VIX', value: latest(data.daily_macro, 'vix') }},
  {{ label: '최근 USD/KRW', value: latest(data.daily_macro, 'usdkrw') }},
  {{ label: '누적 회의일', value: data.committee_history.length }},
];

const cardWrap = document.getElementById('summary-cards');
cardWrap.innerHTML = cards.map(c => `<div class=\"card\"><div class=\"label\">${{c.label}}</div><div class=\"value\">${{c.value}}</div></div>`).join('');

const marketLabels = data.market_daily.map(r => r.date);
new Chart(document.getElementById('marketChart'), {{
  type: 'line',
  data: {{ labels: marketLabels, datasets: [
    {{ label:'KOSPI', data:data.market_daily.map(r=>r.kospi_pct), borderColor:'#22d3ee' }},
    {{ label:'KOSDAQ', data:data.market_daily.map(r=>r.kosdaq_pct), borderColor:'#f97316' }},
    {{ label:'S&P500', data:data.market_daily.map(r=>r.sp500_pct), borderColor:'#a3e635' }},
  ]}},
}});

new Chart(document.getElementById('macroChart'), {{
  type:'line',
  data: {{ labels:data.daily_macro.map(r=>r.date), datasets:[
    {{ label:'VIX', data:data.daily_macro.map(r=>r.vix), borderColor:'#f43f5e', yAxisID:'y' }},
    {{ label:'USD/KRW', data:data.daily_macro.map(r=>r.usdkrw), borderColor:'#38bdf8', yAxisID:'y1' }}
  ]}},
  options: {{ scales: {{ y: {{ position:'left' }}, y1: {{ position:'right', grid: {{ drawOnChartArea:false }} }} }} }}
}});

new Chart(document.getElementById('flowChart'), {{
  type:'bar',
  data: {{ labels:data.market_flow_daily.map(r=>r.date), datasets:[
    {{ label:'Foreign Net', data:data.market_flow_daily.map(r=>r.foreign_net), backgroundColor:'#c084fc' }}
  ]}}
}});

new Chart(document.getElementById('guidanceChart'), {{
  type:'bar',
  data: {{ labels:data.committee_history.map(r=>r.market_date), datasets:[
    {{ label:'유지(OK)', data:data.committee_history.map(r=>r.ok_count), backgroundColor:'#22c55e' }},
    {{ label:'주의(CAUTION)', data:data.committee_history.map(r=>r.caution_count), backgroundColor:'#f59e0b' }},
    {{ label:'회피(AVOID)', data:data.committee_history.map(r=>r.avoid_count), backgroundColor:'#ef4444' }},
  ]}},
  options: {{ responsive:true, scales: {{ x: {{ stacked:true }}, y: {{ stacked:true }} }} }}
}});


const chair = data.latest_committee || {{}};
const chairDate = document.getElementById('chairDate');
const chairConsensus = document.getElementById('chairConsensus');
const chairKeyPoints = document.getElementById('chairKeyPoints');
const chairGuidance = document.getElementById('chairGuidance');

chairDate.textContent = chair.market_date ? `(${{chair.market_date}})` : '';
chairConsensus.textContent = toKoreanChairText(chair.consensus);
chairKeyPoints.innerHTML = (chair.key_points || []).map(point => `<li>${{toKoreanChairText(point)}}</li>`).join('') || '<li>-</li>';
chairGuidance.innerHTML = (chair.ops_guidance || [])
  .map(item => `<li>[${{formatGuidanceLevel(item.level)}}] ${{toKoreanChairText(item.text)}}</li>`)
  .join('') || '<li>-</li>';

const table = document.getElementById('committeeTable');
table.innerHTML = data.committee_history.slice().reverse().map(r => `
  <tr>
    <td>${{r.market_date}}</td>
    <td>${{toKoreanChairText(r.consensus)}}</td>
    <td>${{r.ok_count}}</td>
    <td>${{r.caution_count}}</td>
    <td>${{r.avoid_count}}</td>
  </tr>
`).join('');

const stanceDate = document.getElementById('stanceDate');
const stanceTable = document.getElementById('stanceTable');
stanceDate.textContent = data.latest_stances.market_date ? `(${{data.latest_stances.market_date}})` : '';
stanceTable.innerHTML = (data.latest_stances.stances || []).map(s => `
  <tr>
    <td>${{s.agent_name}}</td>
    <td>${{formatRegimeTag(s.regime_tag)}}</td>
    <td>${{s.confidence}}</td>
    <td>${{s.korean_comment || '-'}}</td>
    <td><ul>${{(s.core_claims || []).map(claim => `<li>${{claim}}</li>`).join('')}}</ul></td>
  </tr>
`).join('');
</script>
</body>
</html>
"""


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    try:
        dashboard_data = {
            "market_daily": fetch_rows(conn, "SELECT date, kospi_pct, kosdaq_pct, sp500_pct, nasdaq_pct, dow_pct FROM market_daily ORDER BY date"),
            "market_flow_daily": fetch_rows(conn, "SELECT date, foreign_net, foreign_20d, foreign_60d FROM market_flow_daily ORDER BY date"),
            "daily_macro": fetch_rows(conn, "SELECT date, us10y, us2y, spread_2_10, vix, dxy, usdkrw FROM daily_macro ORDER BY date"),
            "monthly_macro": fetch_rows(conn, "SELECT date, unemployment_rate, cpi_yoy, core_cpi_yoy, pce_yoy, pmi, wage_yoy FROM monthly_macro ORDER BY date"),
            "quarterly_macro": fetch_rows(conn, "SELECT date, real_gdp, gdp_qoq_annualized FROM quarterly_macro ORDER BY date"),
            "committee_history": load_committee_history(),
            "latest_stances": load_latest_stances(),
            "latest_committee": load_latest_committee(),
        }
    finally:
        conn.close()

    OUTPUT_PATH.write_text(build_dashboard_html(dashboard_data), encoding="utf-8")
    print(f"Dashboard generated: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
