r"""Independent, fail-closed numerical audit for the DMart golden-set logs.

Run from project root: py eval\grounding_audit.py
Does not import agent code or trust agent-reported ungrounded_numbers.
"""
import csv
import json
import re
import statistics
from collections import Counter, defaultdict
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'data'
EVAL = ROOT / 'eval'
NUMBER = re.compile(r'(?<![\w.])(?:INR\s*)?-?\d+(?:\.\d+)?(?:%|\s*mm)?(?!\w|\.\d)')
DATE = re.compile(r'\b\d{4}-\d{2}-\d{2}\b')


def rows(filename):
    with (DATA / filename).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def fmt(value, places=2):
    quantum = Decimal('1').scaleb(-places)
    return str(Decimal(str(value)).quantize(quantum, rounding=ROUND_HALF_UP))


def numeric_tokens(text):
    # Exclude ISO dates and comparison ranking ordinals (1. through 5.).
    text = DATE.sub(' ', text)
    text = re.sub(r'(?m)^\s*[1-5]\.\s+', '', text)
    return [re.sub(r'^(?:INR\s*)', '', m.group()).strip().rstrip('%').removesuffix(' mm').strip()
            for m in NUMBER.finditer(text)]


def same_numeric(a, b):
    try:
        return Decimal(a) == Decimal(b)
    except Exception:
        return False


def check(case, run, daily, inventory, feedback):
    cid = case['case_id']
    answer = run.get('answer_text', run.get('answer', ''))
    evidence = run.get('evidence', [])
    grounded = run.get('grounded_values', [])
    status = run.get('status')
    if not isinstance(evidence, list) or not isinstance(grounded, list):
        raise ValueError('evidence/grounded_values must be lists')
    if status not in ('Answered', 'Drafted'):
        if grounded:
            raise ValueError('Non-answer status has numerical grounded values')
        return 0
    if not evidence:
        raise ValueError('Answered case has no evidence')

    claims = []  # (value, label); values independently recomputed from sources
    if run.get('intent') == 'comparison':
        if cid == 'A10':
            start, end, reverse = '2026-05-01', '2026-05-31', True
        elif cid == 'A11':
            start, end, reverse = '2026-06-10', '2026-06-10', False
        elif cid == 'R01':
            start, end, reverse = min(r['date'] for r in daily), max(r['date'] for r in daily), False
        else:
            raise ValueError('Unrecognized comparison period; audit fails closed')
        groups = defaultdict(list)
        for r in daily:
            if start <= r['date'] <= end:
                groups[r['store']].append(Decimal(r['revenue_inr']))
        ranking = sorted(((store, fmt(sum(v) / len(v))) for store, v in groups.items()),
                         key=lambda item: Decimal(item[1]), reverse=reverse)
        if not ranking:
            raise ValueError('No source rows for comparison')
        for rank, (store, value) in enumerate(ranking, 1):
            if not re.search(rf'(?m)^\s*{rank}\.\s+{re.escape(store)}:\s+INR\s+{re.escape(value)}\b', answer):
                raise ValueError(f'Incorrect ranking entry: {rank}. {store} INR {value}')
            claims.append((value, f'{store} mean revenue'))
        if not any(e.get('source') == 'data/store_daily_clean.csv' and 'revenue_inr' in e.get('fields', []) for e in evidence):
            raise ValueError('Missing comparison CSV evidence')

    elif run.get('intent') == 'inventory':
        if not any(e.get('source') == 'data/inventory.csv' for e in evidence):
            raise ValueError('Missing inventory evidence')
        product = 'Amul Milk 1L' if 'amul milk' in case['question'].lower() else None
        selected = [r for r in inventory if (not product or r['product'] == product)
                    and (not 'below' in case['question'].lower() or int(r['stock_units']) < int(r['reorder_threshold']))]
        if not selected:
            raise ValueError('Inventory source rows not found')
        for r in selected:
            fragment = f"{r['store']} - {r['product']}: {r['stock_units']} units, threshold {r['reorder_threshold']}"
            if fragment not in answer:
                raise ValueError(f'Inventory answer mismatch: {fragment}')
            claims += [(r['stock_units'], 'stock units'), (r['reorder_threshold'], 'reorder threshold')]

    elif run.get('intent') == 'feedback':
        ev = next((e for e in evidence if e.get('source') == 'data/feedback.csv'), None)
        if not ev or not ev.get('store'):
            raise ValueError('Feedback store/source evidence missing')
        relevant = [r for r in feedback if r['store'] == ev['store']]
        ratings = [Decimal(r['rating']) for r in relevant if r['rating'].strip()]
        if not relevant or not ratings:
            raise ValueError('No feedback data')
        avg, rated, total = fmt(sum(ratings) / len(ratings)), str(len(ratings)), str(len(relevant))
        themes = Counter(r['theme'] for r in relevant if r['theme'].strip())
        theme = themes.most_common(1)[0][0]
        for fragment in [f'average rating {avg}', f'rated records {rated}', f'total feedback {total}', f'most frequent theme {theme}']:
            if fragment not in answer:
                raise ValueError(f'Feedback answer mismatch: {fragment}')
        claims += [(avg, 'average rating'), (rated, 'rated records'), (total, 'total feedback')]

    else:
        for e in evidence:
            source = e.get('source')
            if source == 'data/store_daily_clean.csv':
                store, day = e.get('store'), e.get('date')
                if not store or not day:
                    raise ValueError('Store/date evidence missing')
                matches = [r for r in daily if r['store'] == store and r['date'] == day]
                if len(matches) != 1:
                    raise ValueError('Store/date source row not unique')
                r = matches[0]
                for field in e.get('fields', []):
                    if field in ('revenue_inr', 'daily_target_inr', 'footfall', 'stockout_hours', 'discount_pct', 'achievement_pct'):
                        claims.append((fmt(r[field]), field))
                    elif field == 'performance_band':
                        if r[field] not in answer:
                            raise ValueError('Performance band mismatch')
                    else:
                        raise ValueError(f'Unsupported numeric field: {field}')
            elif source == 'Deterministic offline weather stub':
                # Independent expected stub values: do not call get_weather().
                stub = {
                    ('Mumbai', '2026-05-15'): ('26.0', '43.0', '10.0', '0.0'),
                    ('Pune', '2026-05-16'): ('25.0', '88.0', '11.0', '6.5'),
                    ('Hyderabad', '2026-04-01'): ('30.0', '58.0', '6.0', '0.0'),
                }
                key = (e.get('city'), e.get('date'))
                if key not in stub:
                    raise ValueError('Weather stub date not independently audited')
                for value, field in zip(stub[key], ('temperature', 'humidity', 'wind speed', 'rainfall')):
                    claims.append((value, field))
            else:
                raise ValueError(f'Unknown source: {source}')

    if not claims:
        raise ValueError('Answered case has no independently verified claims')
    # Check each numeric grounded value against source-backed claims (with multiplicity).
    expected = Counter(Decimal(str(v)) for v, _ in claims)
    actual = Counter()
    for item in grounded:
        nums = numeric_tokens(str(item))
        if len(nums) != 1:
            raise ValueError(f'Invalid grounded value: {item}')
        actual[Decimal(nums[0])] += 1
    if actual != expected:
        raise ValueError(f'Grounded values differ from sources: {actual} != {expected}')
    # Every numeric claim in answer must appear in the verified source multiset.
    # Dates and ranking ordinals are excluded as metadata, not data claims.
    answer_nums = Counter(Decimal(n) for n in numeric_tokens(answer))
    if answer_nums != expected:
        raise ValueError(f'Answer numbers differ from sources: {answer_nums} != {expected}')
    return len(claims)


def main():
    daily = rows('store_daily_clean.csv')
    inventory = rows('inventory.csv')
    feedback = rows('feedback.csv')
    with (EVAL / 'golden_set.csv').open(encoding='utf-8-sig', newline='') as f:
        cases = list(csv.DictReader(f))
    with (EVAL / 'eval_runs.jsonl').open(encoding='utf-8') as f:
        logs = [json.loads(line) for line in f if line.strip()]
    if len(cases) != len(logs) or len(cases) < 34:
        raise SystemExit('FAIL: Golden set and evaluation logs do not align')
    failures = []
    checked = 0
    for case, run in zip(cases, logs):
        try:
            if case['question'] != run.get('question') or case['session_id'] != run.get('session_id'):
                raise ValueError('Golden case does not match evaluation log')
            count = check(case, run, daily, inventory, feedback)
            checked += count
            print(f"{case['case_id']}: PASS ({count} independently checked values)")
        except Exception as exc:
            failures.append((case['case_id'], str(exc)))
            print(f"{case['case_id']}: FAIL ({exc})")
    print('=' * 50)
    print(f'INDEPENDENT AUDIT: {len(cases)-len(failures)}/{len(cases)} cases')
    print(f'NUMERIC VALUES CHECKED: {checked}')
    print('AUDIT DECISION:', 'PASS' if not failures else 'FAIL')
    report = EVAL / 'grounding_audit_report.md'
    report.write_text('# Independent Grounding Audit\n\n'
                      + f'- Cases: {len(cases)}\n- Failures: {len(failures)}\n- Numeric values checked: {checked}\n'
                      + '- Method: independent CSV recomputation and explicitly documented fixed offline weather fixtures; answer/evidence/grounded-value comparison.\n'
                      + '- Scope: golden-set evaluation only, not a guarantee for arbitrary future queries.\n\n'
                      + '## Failures\n' + ('\n'.join(f'- {c}: {reason}' for c, reason in failures) or 'None') + '\n', encoding='utf-8')
    if failures:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
