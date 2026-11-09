"""把 知識庫/ 各資料夾的 .md 檔合併成少數幾個大檔，方便上傳到 NotebookLM。

用法（在專案根目錄執行）：
    python3 工具/合併來源檔.py

輸出在 輸出/ 資料夾。單一檔案超過 MAX_CHARS 字會自動切成多個部分。
"""

from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "知識庫"
OUT = ROOT / "輸出"
MAX_CHARS = 300_000  # NotebookLM 單一來源上限約 50 萬字，留些餘裕


def main() -> None:
    OUT.mkdir(exist_ok=True)
    for old in OUT.glob("*.md"):
        old.unlink()

    for folder in sorted(p for p in SRC.iterdir() if p.is_dir()):
        files = sorted(folder.rglob("*.md"))
        if not files:
            print(f"略過（沒有檔案）：{folder.name}")
            continue

        header = f"# {folder.name}\n\n合併日期：{date.today().isoformat()}\n\n"
        parts: list[str] = []
        current = header
        for f in files:
            body = f.read_text(encoding="utf-8").strip()
            section = f"\n\n---\n\n<!-- 來源檔案：{f.relative_to(SRC)} -->\n\n{body}\n"
            if len(current) + len(section) > MAX_CHARS and current != header:
                parts.append(current)
                current = header
            current += section
        parts.append(current)

        for i, text in enumerate(parts, 1):
            name = folder.name if len(parts) == 1 else f"{folder.name}_第{i}部"
            (OUT / f"{name}.md").write_text(text, encoding="utf-8")
        print(f"{folder.name}：{len(files)} 個檔案 → {len(parts)} 個輸出檔")

    print(f"完成，請上傳 {OUT} 裡的檔案。")


if __name__ == "__main__":
    main()
