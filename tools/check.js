// 參照檢查：在 docs/ 資料夾內執行  node ../tools/check.js
const fs = require('fs');
eval(fs.readFileSync('data.js', 'utf8') + fs.readFileSync('laws.js', 'utf8') + `
const ids = new Set(法規函釋.map(x => x.id)), bids = new Set(業務.map(x => x.id)), bad = [];
for (const b of 業務) {
  for (const l of b.法規 || []) if (!ids.has(l)) bad.push(b.id + ' 法規 ' + l);
  for (const r of b.相關業務 || []) if (!bids.has(r)) bad.push(b.id + ' 相關 ' + r);
  for (const r of b.條文 || []) { const [lid, n] = r.split(':'); const L = 法規全文.find(x => x.id === lid); if (!L || !L.條.find(a => a.號 === n)) bad.push(b.id + ' 條文 ' + r); }
}
if (ids.size !== 法規函釋.length || bids.size !== 業務.length) bad.push('duplicate id');
console.log('業務', 業務.length, '法規函釋', 法規函釋.length, '法規全文', 法規全文.map(l => l.名稱 + l.條.length).join(' '), 'problems', bad);`);
