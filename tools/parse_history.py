# 把歷史法規文字檔轉成 docs/laws_history.js（已廢止的法規，供沿革查考）。
# 用法：python3 tools/parse_history.py <文字檔資料夾> docs/laws_history.js
# 各檔案設定在 SRC：(代號, 名稱, 檔名, 發布, 狀態)
import re, json, sys
D, OUT = sys.argv[1], sys.argv[2]
SRC = [
    ('h建物平面圖測繪辦法', '統一規定建物平面圖測繪辦法', '08.txt', '臺灣省政府46年5月3日（四六）府民地甲字第1780號令', '63年6月28日臺灣省土地建物複丈規則訂定時廢止'),
    ('h土地建物複丈規則', '臺灣省土地建物複丈規則', '01.txt', '臺灣省政府63年6月28日訂定', '已廢止（被71年土地複丈辦法、建物測量辦法取代）'),
    ('h土地複丈辦法', '土地複丈辦法', '05.txt', '71年8月12日訂定（依地籍測量實施規則第218條）', '79年6月27日廢止'),
    ('h建物測量辦法', '建物測量辦法', '09.txt', '71年8月12日訂定（依地籍測量實施規則第219條）', '79年6月27日廢止'),
]
CN = {c: i for i, c in enumerate('零一二三四五六七八九')}
def cn2int(s):
    n, cur = 0, 0
    for ch in s:
        if ch in CN: cur = CN[ch]
        elif ch == '十': n += (cur or 1) * 10; cur = 0
        elif ch == '百': n += (cur or 1) * 100; cur = 0
    return n + cur
ART = re.compile(r'^第\s*([0-9]+|[一二三四五六七八九十百]+)\s*條\s*(.*)$')
CH = re.compile(r'^第\s*([一二三四五六七八九十]+)\s*章\s*(.*)$')
SKIP = re.compile(r'^(【附錄|法規名稱|廢止日期|訂定「)')
out = []
for lid, name, fn, issued, status in SRC:
    lines = [l.replace('﻿', '').strip() for l in open(f'{D}/{fn}', encoding='utf-8')]
    lines = [l for l in lines if l and not SKIP.match(l) and l != name]
    arts, ch = [], ''
    for l in lines:
        m = CH.match(l)
        if m: ch = f'第{m.group(1)}章 {m.group(2).strip()}'; continue
        m = ART.match(l)
        if m:
            n = m.group(1); n = n if n.isdigit() else str(cn2int(n))
            prev = int(arts[-1]['號']) if arts and arts[-1]['號'].isdigit() else 0
            if not (prev < int(n) <= prev + 20):
                arts[-1]['內容'].append(l); continue
            arts.append({'號': n, '章': ch, '標題': '', '內容': [m.group(2)] if m.group(2) else []}); continue
        if arts: arts[-1]['內容'].append(l)
        else: arts.append({'號': '全文', '章': '', '標題': '', '內容': [l]})
    for a in arts: a['內容'] = '\n'.join(a['內容'])
    out.append({'id': lid, '名稱': name, '版本': issued, '狀態': status, '歷史': True, '條': arts})
    print(name, len(arts), file=sys.stderr)
with open(OUT, 'w', encoding='utf-8') as f:
    f.write('/* 歷史法規全文（已廢止，供沿革查考）：由 tools/parse_history.py 轉出，請勿手動修改。 */\n')
    f.write('const 歷史法規全文 = ' + json.dumps(out, ensure_ascii=False, indent=0) + ';\n')
