"""Point-in-time guarded Korean macro evidence shared by UI and agents."""
from datetime import date, datetime, time, timedelta, timezone
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
KST = timezone(timedelta(hours=9))
GUIDANCE = (
    "한국 월별 경제지표는 중기 경기 배경으로 반영하고 일별 시장·수급 신호와 구분한다. "
    "각 근거의 기준월과 비교 기준을 명시하고 미국 지표와 혼동하지 않는다. "
    "제외 지표는 판단 근거로 사용하지 않는다. 경기·생산·심리 지표의 상관관계를 고려해 "
    "개별 긍정/부정 개수를 매수·매도 점수로 합산하지 않는다. 물가는 방향만으로 호재·악재를 단정하지 않는다. "
    "서로 상충하는 신호를 모두 설명하며 이 자료만으로 시장 전망이나 현금 비중을 확정하지 않는다."
)


def month_offset(period, offset):
    year, month = divmod(int(period[:4]) * 12 + int(period[4:]) - 1 + offset, 12)
    return f'{year:04d}{month + 1:02d}'


def build_context(payload, as_of=None):
    now = as_of or datetime.now(KST)
    if isinstance(now, date) and not isinstance(now, datetime):
        now = min(datetime.combine(now, time.max, KST), datetime.now(KST))
    if now.tzinfo is None:
        now = now.replace(tzinfo=KST)
    current = now.astimezone(KST).strftime('%Y%m')
    catalog = json.loads((ROOT / 'config/korea_macro_indicators.json').read_text(encoding='utf-8'))
    entries = {s.get('id'): s for s in payload.get('indicators', []) if isinstance(s, dict)}
    evidence, excluded = [], []
    for spec in catalog:
        row = entries.get(spec['id'], {})
        try:
            if row.get('error'):
                raise ValueError('수집 실패')
            stamp = datetime.fromisoformat(row['succeeded_at'])
            if stamp.tzinfo is None or stamp > now:
                raise ValueError('분석 시점 이후 수집 자료')
            if now - stamp > timedelta(days=3):
                raise ValueError('수집 확인 필요')
            values = {r['period']: float(r['value']) for r in row['history']}
            if not values or not all(math.isfinite(v) for v in values.values()):
                raise ValueError('유효값 부족')
            latest = max(values)
            if latest > current or latest < month_offset(current, -spec['lag_months']):
                raise ValueError('기준월 지연 또는 미래 자료')
            offset = -12 if spec['comparison'] == 'yoy' else -1
            previous = values.get(month_offset(latest, offset))
            value = values[latest]
            if previous is None or (previous == 0 and spec['comparison'] != 'delta'):
                raise ValueError('비교월 자료 부족')
            change = value - previous if spec['comparison'] == 'delta' else (value / previous - 1) * 100
            label = '맥락 확인' if not spec['direction'] else '보합' if abs(change) < .005 else '긍정' if change * spec['direction'] > 0 else '부정'
            evidence.append({k: spec[k] for k in ['id', 'name', 'group', 'unit', 'comparison', 'note']} | {
                'period': latest, 'value': value, 'change': round(change, 4), 'signal': label,
                'change_unit': ('%p' if spec['unit'] == '%' else 'p') if spec['comparison'] == 'delta' else '%',
                'collected_at': row['succeeded_at'], 'source': '한국은행 ECOS'})
        except (KeyError, TypeError, ValueError, OverflowError) as exc:
            reason = str(exc) if isinstance(exc, ValueError) and str(exc) in {
                '수집 실패', '분석 시점 이후 수집 자료', '수집 확인 필요', '유효값 부족',
                '기준월 지연 또는 미래 자료', '비교월 자료 부족'} else '자료 없음 또는 형식 오류'
            excluded.append({'id': spec['id'], 'name': spec['name'], 'reason': reason})
    groups = []
    for group in dict.fromkeys(s['group'] for s in catalog):
        items = [s for s in evidence if s['group'] == group]
        signs = {s['signal'] for s in items if s['signal'] in ['긍정', '부정']}
        tone = '혼조' if len(signs) == 2 else next(iter(signs)) if signs else '방향 판단 유보'
        if any(s['signal'] == '맥락 확인' for s in items):
            tone += ' / 물가는 별도 판단'
        groups.append({'name': group, 'tone': tone, 'indicators': [s['id'] for s in items]})
    summary = ' · '.join(f"{g['name']} {g['tone']}" for g in groups)
    return {'as_of': now.isoformat(), 'available': len(evidence), 'total': len(catalog),
            'summary': summary if evidence else '한국 경제지표 유효 근거 부족 · 판단 유보',
            'groups': groups, 'evidence': evidence, 'excluded': excluded, 'guidance': GUIDANCE}


def load_context(as_of=None):
    try:
        payload = json.loads((ROOT / 'runs/korea_macro/latest.json').read_text(encoding='utf-8'))
        if not isinstance(payload, dict):
            payload = {}
    except (OSError, ValueError):
        payload = {}
    return build_context(payload, as_of)
