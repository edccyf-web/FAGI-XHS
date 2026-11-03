"""只读取 XLSX 存储值，不执行公式、宏、外链或单元格中的指令。"""
import csv
import json
import math
import posixpath
import re
import zipfile
from datetime import datetime, timedelta
from xml.etree import ElementTree as ET

NS = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'


def xlsx_rows(path, sheet=None, warnings=None):
    with zipfile.ZipFile(path) as z:
        book = ET.fromstring(z.read('xl/workbook.xml'))
        sheets = book.find(NS + 'sheets')
        selected = next((s for s in sheets if s.get('name') == sheet), None) if sheet else sheets[0]
        if selected is None:
            raise ValueError(f'工作表不存在：{sheet}')
        rid = selected.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
        rels = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
        target = next(r.get('Target') for r in rels if r.get('Id') == rid)
        member = target.lstrip('/') if target.startswith('/') else posixpath.normpath('xl/' + target)
        strings = []
        if 'xl/sharedStrings.xml' in z.namelist():
            with z.open('xl/sharedStrings.xml') as f:
                for _, el in ET.iterparse(f, events=('end',)):
                    if el.tag == NS + 'si':
                        strings.append(''.join(t.text or '' for t in el.iter(NS + 't')))
                        el.clear()
        formats = {}
        styles = []
        if 'xl/styles.xml' in z.namelist():
            root = ET.fromstring(z.read('xl/styles.xml'))
            formats = {int(e.get('numFmtId')): e.get('formatCode', '') for e in root.iter(NS + 'numFmt')}
            styles = [int(e.get('numFmtId', '0')) for e in root.find(NS + 'cellXfs')]
        props = book.find(NS + 'workbookPr')
        epoch = datetime(1904, 1, 1) if props is not None and props.get('date1904') in ('1', 'true') else datetime(1899, 12, 30)
        with z.open(member) as f:
            for _, el in ET.iterparse(f, events=('end',)):
                if el.tag != NS + 'row':
                    continue
                cells = []
                for c in el.findall(NS + 'c'):
                    col = 0
                    for char in re.match(r'[A-Z]+', c.get('r')).group():
                        col = col * 26 + ord(char) - 64
                    while len(cells) < col:
                        cells.append(None)
                    kind, raw = c.get('t'), c.findtext(NS + 'v')
                    value = raw
                    if kind == 's' and raw is not None:
                        value = strings[int(raw)]
                    elif kind == 'inlineStr':
                        value = ''.join(t.text or '' for t in c.iter(NS + 't'))
                    elif kind == 'e':
                        raise ValueError(f'Excel 错误值：{selected.get("name")}!{c.get("r")}={raw}')
                    elif kind == 'b':
                        value = raw == '1'
                    elif kind not in ('str', 'd') and raw is not None:
                        value = float(raw)
                        style = int(c.get('s', '0'))
                        fid = styles[style] if style < len(styles) else 0
                        fmt = re.sub(r'"[^"]*"|\\.', '', formats.get(fid, '')).lower()
                        if 14 <= fid <= 22 or 45 <= fid <= 47 or re.search(r'[yd]|h.*[ms]', fmt):
                            value = (epoch + timedelta(days=value)).isoformat(sep=' ')
                    if c.find(NS + 'f') is not None:
                        if warnings is not None:
                            warnings.append({'cell': f'{selected.get("name")}!{c.get("r")}',
                                             'issue': '公式缺少缓存值' if raw is None else '使用公式缓存值，需确认已在 Excel 重算'})
                    cells[col - 1] = value
                yield int(el.get('r')), cells
                el.clear()


def load_table(path, aliases, sheet=None, ctr_unit='fraction'):
    warnings = []
    if str(path).lower().endswith('.json'):
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
        notes = data.get('notes', []) if isinstance(data, dict) else data
        headers = list(dict.fromkeys(k for n in notes for k in n if not k.startswith('_')))
        # Different keys across records must not shift columns.
        rows = ((i + 2, [n.get(h) for h in headers]) for i, n in enumerate(notes))
    else:
        if str(path).lower().endswith('.xlsx'):
            rows = xlsx_rows(path, sheet, warnings)
        elif str(path).lower().endswith('.csv'):
            def csv_rows():
                with open(path, encoding='utf-8-sig', newline='') as f:
                    yield from enumerate(csv.reader(f), 1)
            rows = csv_rows()
        else:
            raise ValueError('仅支持 XLSX / UTF-8 CSV / JSON')
        headers = None
        for _, candidate in rows:
            names = {str(v).strip().lower() for v in candidate if v is not None}
            if names.intersection(aliases['title']) and names.intersection(aliases['exp'] + aliases['view'] + ['exp', 'view']):
                headers = candidate
                break
        if headers is None:
            raise ValueError('找不到笔记表头；请检查工作表或提供明确列名')
    mapping = {}
    for key, names in aliases.items():
        matches = [i for i, h in enumerate(headers) if str(h).strip().lower() in names + [key]]
        if len(matches) > 1:
            raise ValueError(f'{key} 对应多个列，请先消除列名歧义')
        if matches:
            mapping[key] = matches[0]
    notes = []
    for row_id, row in rows:
        if not any(v not in (None, '') for v in row):
            continue
        rec = {'_row': row_id}
        for key, idx in mapping.items():
            value = row[idx] if idx < len(row) else None
            if isinstance(value, str):
                value = value.strip()
            if key not in ('title', 'date', 'fmt') and value not in (None, '', '—', '--', '-'):
                raw = value
                try:
                    pct = isinstance(value, str) and value.endswith('%')
                    value = float(str(value).replace(',', '').rstrip('%'))
                    if pct or (key == 'ctr' and ctr_unit == 'percent'):
                        value /= 100
                    if not math.isfinite(value) or value < 0 or (key == 'ctr' and value > 1):
                        raise ValueError()
                except (ValueError, TypeError):
                    warnings.append({'row': row_id, 'field': key, 'value': raw, 'issue': '无效数值或单位待确认'})
                    value = None
            elif value in ('', '—', '--', '-'):
                value = None
            rec[key] = value
        if not rec.get('title'):
            warnings.append({'row': row_id, 'issue': '无标题行，未计入笔记'})
            continue
        notes.append(rec)
    return notes, {'columns': {k: headers[v] for k, v in mapping.items()}, 'warnings': warnings,
                   'sheet': sheet or '首张工作表', 'ctr_unit': ctr_unit}
