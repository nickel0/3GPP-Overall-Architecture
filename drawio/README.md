# draw.io 版について

このフォルダには、原図（PowerPoint / pptx）の draw.io 再現を置きます。

- `3gpp-overall-architecture.drawio` — 原図を draw.io で再現した**マスター**。編集可能な正本としてここに置きます。今後の図の修正はこのファイルを起点に行います。
- `3gpp-overall-architecture-rel19-composite.drawio` — マスターに Release 18／19 の要素を統合した派生版（複合盤）。
- `tools/` — 生成パイプライン。`extract_full.py` で pptx から全図形を機械抽出し、`gen_drawio.py` で draw.io（mxGraph XML）へ変換します。再実行で同じ図を再生成できます。
- `NOTES.md` — 変換方式・検証結果・既知の近似などの設計メモ。

追加したセルは `add_` 接頭辞の ID で判別できます。色の意味は原図と追加分で異なる場合があるため、`NOTES.md` と図面内の Colour note をあわせて参照してください。
