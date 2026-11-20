// 參照檢查：在 docs/ 資料夾內執行  node ../tools/check.js
const fs = require('fs');
eval(fs.readFileSync('data.js', 'utf8') + fs.readFileSync('laws.js', 'utf8') + fs.readFileSync('laws_history.js', 'utf8') + `
const ids = new Set(法規函釋.map(x => x.id)), bids = new Set(業務.map(x => x.id)), bad = [];
const art = r => { const [lid, n] = r.split(':'); const L = 法規全文.find(x => x.id === lid); return L && (!n || L.條.find(a => a.號 === n)); };
for (const b of 業務) {
  for (const l of b.法規 || []) if (!ids.has(l)) bad.push(b.id + ' 法規 ' + l);
  for (const r of b.相關業務 || []) if (!bids.has(r)) bad.push(b.id + ' 相關 ' + r);
  for (const r of b.條文 || []) if (!art(r)) bad.push(b.id + ' 條文 ' + r);
}
for (const t of 沿革) {
  for (const i of t.項目) if (!ids.has(i)) bad.push('沿革 ' + t.id + ' 項目 ' + i);
  for (const i of t.業務 || []) if (!bids.has(i)) bad.push('沿革 ' + t.id + ' 業務 ' + i);
}
for (const g of 歷史沿革) for (const x of g.項目) {
  if (x.全文 && !歷史法規全文.find(h => h.id === x.全文)) bad.push('歷史 全文 ' + x.全文);
  if (x.現行 && !art(x.現行)) bad.push('歷史 現行 ' + x.現行);
}
for (const l of 法規函釋) if (l.類型 !== '法規' && !l.層級) bad.push('缺層級 ' + l.id);
const orphan = 法規函釋.filter(l => l.類型 !== '法規' && !沿革.some(t => t.項目.includes(l.id))).map(l => l.id);
if (ids.size !== 法規函釋.length || bids.size !== 業務.length || new Set(沿革.map(t => t.id)).size !== 沿革.length) bad.push('duplicate id');
console.log('業務', 業務.length, '函釋', 法規函釋.length, '沿革', 沿革.length, '歷史法規', 歷史法規全文.length);
console.log('未歸入沿革的函釋：', orphan.join('、') || '無');
console.log('problems', bad);`);
