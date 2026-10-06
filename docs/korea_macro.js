/* Monthly economic indicators: exact calendar comparisons; no missing=zero. */
function krShift(period, offset) {
  const d = new Date(Date.UTC(Number(period.slice(0, 4)), Number(period.slice(4)) - 1 + offset, 1));
  return String(d.getUTCFullYear()) + String(d.getUTCMonth() + 1).padStart(2, '0');
}
function krChanges(history, row) {
  const values = new Map(history.map(r => [r.period, r.value]));
  const previous = values.get(krShift(row.period, -1));
  const annual = values.get(krShift(row.period, -12));
  return {
    delta: Number.isFinite(previous) ? row.value - previous : null,
    mom: Number.isFinite(previous) && previous !== 0 ? (row.value / previous - 1) * 100 : null,
    yoy: Number.isFinite(annual) && annual !== 0 ? (row.value / annual - 1) * 100 : null
  };
}
function krSignal(spec, changes) {
  const value = changes[spec.comparison];
  if (value === null || !Number.isFinite(value)) return {label:'비교 자료 부족', color:'#94a3b8'};
  if (!spec.direction) return {label:'맥락 확인', color:'#c4b5fd'};
  if (Math.abs(value) < 0.005) return {label:'→ 보합', color:'#fbbf24'};
  return value * spec.direction > 0 ? {label:'＋ 긍정 신호', color:'#4ade80'} : {label:'− 부정 신호', color:'#fb7185'};
}
function krStatus(spec, now = new Date()) {
  if (spec.error) return '수집 실패 · 기존 자료 유지';
  if (!spec.history.length) return '자료 없음';
  const age = (now - new Date(spec.succeeded_at)) / 86400000;
  if (!Number.isFinite(age) || age > 3 || age < -1) return '수집 확인 필요';
  const kst = new Date(now.getTime() + 9 * 3600000);
  const period = String(kst.getUTCFullYear()) + String(kst.getUTCMonth() + 1).padStart(2, '0');
  if (spec.history.at(-1).period < krShift(period, -spec.lag_months)) return '자료 지연 확인 필요';
  return '정상 · 다음 발표 대기';
}
function renderKoreaMacro(payload) {
  const root = document.getElementById('kr-macro-cards');
  if (!root) return;
  const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const number = value => Number.isFinite(value) ? value.toLocaleString('ko-KR', {maximumFractionDigits:2}) : '—';
  const signed = value => Number.isFinite(value) ? (value > 0 ? '+' : '') + number(value) : '—';
  const month = period => period.slice(0, 4) + '.' + period.slice(4);
  const stamp = value => value ? new Date(value).toLocaleString('ko-KR', {timeZone:'Asia/Seoul'}) + ' KST' : '없음';
  const indicators = payload.indicators || [];
  const status = document.getElementById('kr-macro-status');
  if (!indicators.length) { status.textContent = payload.error || '아직 수집된 한국 경제지표가 없습니다.'; return; }
  const normal = indicators.filter(s => krStatus(s).startsWith('정상')).length;
  status.textContent = `${indicators.length}개 지표 · 정상 ${normal}개 · 확인 필요 ${indicators.length - normal}개 · 마지막 실행 ${stamp(payload.generated_at)}`;
  root.innerHTML = indicators.map(spec => {
    const row = spec.history.at(-1);
    const changes = row ? krChanges(spec.history, row) : {delta:null,mom:null,yoy:null};
    const signal = krSignal(spec, changes);
    const compare = spec.comparison === 'delta' ? `전월 ${signed(changes.delta)}${spec.unit === '%' ? '%p' : 'p'}` : spec.comparison === 'mom' ? `전월 대비 ${signed(changes.mom)}%` : `전년 동월 대비 ${signed(changes.yoy)}%`;
    return `<button type="button" class="kr-macro-card" data-kr-id="${esc(spec.id)}" aria-label="${esc(spec.name)} 추이 보기">
      <span class="muted">${esc(spec.group)}</span><h3>${esc(spec.name)}</h3>
      <div class="kr-macro-value">${row ? number(row.value) : '—'} <small>${esc(spec.unit)}</small></div>
      <p>기준월 ${row ? month(row.period) : '없음'} · ${compare}</p>
      <strong style="color:${signal.color}">${signal.label}</strong>
      <p class="kr-macro-health">${esc(krStatus(spec))}</p><span class="muted">추이 보기 ↗</span></button>`;
  }).join('');
  const select = document.getElementById('kr-macro-select');
  const range = document.getElementById('kr-macro-range');
  select.innerHTML = indicators.map(s => `<option value="${esc(s.id)}">${esc(s.name)}</option>`).join('');
  function detail() {
    const spec = indicators.find(s => s.id === select.value);
    if (!spec) return;
    const rows = spec.history.slice(-Number(range.value));
    document.getElementById('kr-macro-chart-title').textContent = `${spec.name} · ${spec.unit}`;
    document.getElementById('kr-macro-note').textContent = `${spec.note} 출처 통계표 ${spec.table} / ${spec.items.join(', ')}. 마지막 성공 ${stamp(spec.succeeded_at)} · 마지막 시도 ${stamp(spec.attempted_at)}. ${krStatus(spec)}`;
    const chart = document.getElementById('kr-macro-chart');
    if (!rows.length) chart.textContent = '표시할 이력이 없습니다.';
    else {
      const min = Math.min(...rows.map(r => r.value)), max = Math.max(...rows.map(r => r.value));
      const span = max - min || 1;
      const x = i => 65 + i * 820 / Math.max(rows.length - 1, 1);
      const y = v => 235 - (v - min) / span * 200;
      const points = rows.map((r, i) => `${x(i)},${y(r.value)}`).join(' ');
      chart.innerHTML = `<svg viewBox="0 0 920 280" role="img" aria-label="${esc(spec.name)} ${month(rows[0].period)}부터 ${month(rows.at(-1).period)}까지 추이" style="width:100%;max-height:340px">
        <line x1="65" y1="235" x2="885" y2="235" stroke="#475569"/><text x="5" y="40" fill="#cbd5e1">${number(max)}</text><text x="5" y="235" fill="#cbd5e1">${number(min)}</text>
        <polyline points="${points}" fill="none" stroke="#38bdf8" stroke-width="3"/>
        ${rows.map((r,i) => `<circle cx="${x(i)}" cy="${y(r.value)}" r="4" fill="#38bdf8"><title>${month(r.period)}: ${number(r.value)} ${esc(spec.unit)}</title></circle>`).join('')}
        <text x="65" y="268" fill="#cbd5e1">${month(rows[0].period)}</text><text x="885" y="268" text-anchor="end" fill="#cbd5e1">${month(rows.at(-1).period)}</text></svg>`;
    }
    document.getElementById('kr-macro-history').innerHTML = [...rows].reverse().map(row => {
      const c = krChanges(spec.history, row);
      const m = spec.comparison === 'delta' ? `${signed(c.delta)}${spec.unit === '%' ? '%p' : 'p'}` : `${signed(c.mom)}%`;
      return `<tr><td>${month(row.period)}</td><td>${number(row.value)}</td><td>${m}</td><td>${signed(c.yoy)}%</td></tr>`;
    }).join('');
    root.querySelectorAll('button').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.krId === spec.id)));
  }
  root.querySelectorAll('button').forEach(b => b.addEventListener('click', () => { select.value = b.dataset.krId; detail(); document.querySelector('.kr-macro-detail').scrollIntoView({behavior:'smooth',block:'start'}); }));
  select.addEventListener('change', detail);
  range.addEventListener('change', detail);
  detail();
}
