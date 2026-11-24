# 把法規 Word 檔轉成 docs/laws.js。
# 用法：先用 LibreOffice 把各法規 .doc 轉成 UTF-8 文字檔（土地法.txt、施行法.txt、地測.txt、基本.txt）放在同一資料夾，
#   python3 tools/parse_laws.py <文字檔資料夾> docs/laws.js
# 新增其他法規時，在 SRC 加一行 (代號, 法規名稱, 檔名)。
# 全國法規資料庫／農業部網站列印的 PDF（pdftotext -layout 轉出，「第 8-1 條」格式），放在 SRC2。
import re, json, sys
D = sys.argv[1]; OUT = sys.argv[2]
SRC = [('土地法', '土地法', '土地法.txt'), ('施行法', '土地法施行法', '施行法.txt'),
       ('地測', '地籍測量實施規則', '地測.txt'), ('基本', '基本測量實施規則', '基本.txt')]
ART = re.compile(r'^第\s*(\d+(?:\.\d+)?)\s*[條點]\s*(.*)$')
HEAD = re.compile(r'^(第[一二三四五六七八九十]+[編章節])、\s*(.*?)\s*》?\s*$')
laws = []
for lid, name, fn in SRC:
    lines = [l.replace('﻿', '').rstrip() for l in open(f'{D}/{fn}', encoding='utf-8')]
    version = next((l.strip() for l in lines[:4] if l.strip().startswith('中華民國')), '')
    arts, bian, zhang, intent, in_intent, pending_caption, skip_dup = [], "", "", [], False, "", False
    for i, raw in enumerate(lines):
        l = raw.strip()
        if not l or '符合條件的條文' in l or l == name or l.startswith('中華民國') and not arts or l.startswith('►'):
            continue
        m = HEAD.match(l)
        if m:
            t = m.group(1) + ' ' + m.group(2).replace('　', '').replace(' ', '')
            if '編' in m.group(1): bian, zhang = t, ''
            else: zhang = t
            in_intent = False
            continue
        if l.startswith('立法意旨'):
            in_intent = True; intent = [l.split('：', 1)[1].strip()] if '：' in l else []
            continue
        if l.isdigit():
            continue
        m = ART.match(l)
        if m:
            num = tuple(int(x) for x in m.group(1).split('.')) + (0,)
            prev = arts[-1]['_n'] if arts else (0, 0)
            rest = m.group(2)
            if num < prev or num[0] > prev[0] + 50 or re.match(r'^(第\s*\d+\s*[項款]|至|及|、|或|之規定|規定|準用)', rest):
                if num[0] > prev[0] + 50 and not rest:
                    continue
                m = None
        if m and arts and num == prev:
            nxt = rest or next((x.strip() for x in lines[i+1:] if x.strip()), '')
            if nxt.strip() == '（刪除）':
                skip_dup = True
                continue
            note = arts.pop()
            intent = [x for x in [note.get('立法意旨', '')] + note['內容'] if x]
        if m:
            skip_dup = False
            caption = ''
            if not m.group(2) and arts and arts[-1]['內容']:
                last = arts[-1]['內容'][-1]
                if len(last) <= 25 and '。' not in last and '：' not in last:
                    caption = arts[-1]['內容'].pop()
            elif not m.group(2) and not arts and pending_caption:
                caption = pending_caption
            a = {'_n': num, '號': m.group(1), '章': ' > '.join(x for x in (bian, zhang) if x), '標題': caption,
                 '內容': [m.group(2)] if m.group(2) else []}
            if intent: a['立法意旨'] = '\n'.join(x for x in intent if x)
            intent, in_intent = [], False
            arts.append(a); pending_caption = ''
            continue
        if in_intent:
            intent.append(l); continue
        if skip_dup:
            skip_dup = False
            if l == '（刪除）':
                continue
        if arts: arts[-1]['內容'].append(l)
        else: pending_caption = l
    for a in arts:
        a['內容'] = '\n'.join(a['內容']); del a['_n']
    laws.append({'id': lid, '名稱': name, '版本': version, '條': arts})
    nums = [a['號'] for a in arts]
    print(name, len(arts), 'dup' if len(nums) != len(set(nums)) else '', version[:40], file=sys.stderr)
# ---- 第二種格式：全國法規資料庫等網頁列印 PDF ----
SRC2 = [('農發', '農業發展條例', '農發.txt'), ('農發細則', '農業發展條例施行細則', '農發細則.txt')]
ART2 = re.compile(r'^第\s*(\d+)(?:\s*-\s*(\d+))?\s*條\s*(.*)$')
CH2 = re.compile(r'^第\s*([一二三四五六七八九十]+)\s*章\s*(.*)$')
import os
for lid, name, fn in SRC2:
    if not os.path.exists(f'{D}/{fn}'):
        continue
    lines = [l.replace('\ufeff', '').rstrip() for l in open(f'{D}/{fn}', encoding='utf-8')]
    version = ''
    for l in lines[:40]:
        m = re.search(r'修正日期：\s*(民國.*日)', l)
        if m: version = '修正日期：' + m.group(1).replace(' ', ''); break
    if not version:
        vs = [l.strip() for l in lines if l.strip().startswith('中華民國') and '令' in l]
        version = vs[-1] if vs else ''
    arts, ch, started = [], '', False
    for raw in lines:
        l = raw.strip()
        if not l: continue
        m = CH2.match(l)
        if m: ch = f'第{m.group(1)}章 {m.group(2).strip()}'; continue
        m = ART2.match(l)
        if m:
            n = m.group(1) + ('.' + m.group(2) if m.group(2) else '')
            arts.append({'號': n, '章': ch, '標題': '', '內容': [m.group(3).strip()] if m.group(3).strip() else []}); started = True; continue
        if not started: continue
        if re.search(r'版權所有|服務時間|瀏覽人次|地址：|政府網站資料開放', l): started = False; continue
        newpara = bool(re.match(r'^\d+\s+', l))
        l = re.sub(r'^\d+\s+', '', l)
        item = bool(re.match(r'^[一二三四五六七八九十]+、', l))
        c = arts[-1]['內容']
        if c and not newpara and not item and not (lid == '農發細則' and c[-1].endswith(('。', '：'))):
            c[-1] += l
        else:
            c.append(l)
    for a in arts: a['內容'] = '\n'.join(a['內容'])
    laws.append({'id': lid, '名稱': name, '版本': version, '條': arts})
    print(name, len(arts), version, file=sys.stderr)

with open(OUT, 'w', encoding='utf-8') as f:
    f.write('/* 法規全文：由使用者提供的法規 Word 檔自動轉出。\n   請勿手動修改；法規修正時請提供新版檔案重新轉檔。正式條文以全國法規資料庫為準。 */\n')
    f.write('const 法規全文 = ' + json.dumps(laws, ensure_ascii=False, indent=0) + ';\n')
