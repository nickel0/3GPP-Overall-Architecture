# draw.io 版について / About the draw.io version

このフォルダには、原図（`../diagram/3GPP_Overall_Architecture_and_Specifications.pptx`）の draw.io 再現を置きます。
pptx は原典としてそのまま残し、draw.io 版を今後の編集先（正本）とする位置づけです。

- `3gpp-overall-architecture.drawio` — 原図を draw.io で再現した**マスター**。ページは A0 横（1189×841 mm）実寸。
- `export/3gpp-overall-architecture-A0.pdf` — マスターを A0 実寸で書き出した印刷用 PDF（フォント埋め込み済み）。
- `3gpp-overall-architecture-rel19-composite.drawio` — マスターに Release-18／19 の要素を統合した**派生版（複合盤）**。原図セルは動かさず、追加セルのみ（ID は `add_` 接頭辞）。
- `export/3gpp-overall-architecture-rel19-composite-A0.pdf` — 複合盤の A0 実寸 印刷用 PDF。
- `tools/` — 生成パイプライン（手作業の描き写しはしていません）。
  - `extract_full.py` — pptx から全図形・表・コネクタを機械抽出（→ `build/shapes_full.json`）
  - `gen_drawio.py` — 抽出結果を draw.io（mxGraph XML）へ変換し、テキストの一致を自動検証
  - `export_pdf.py` — draw.io デスクトップ版 CLI で A0 実寸の PDF を書き出し
  - `composite_routes.json` — 複合盤の追加線の経路（手で詰めた waypoints）と遠隔参照点のスタブ定義
- `NOTES.md` — 変換方式・検証結果・既知の近似・印刷の注意。

## 再生成 / Regenerate

```sh
python3 drawio/tools/extract_full.py      # pptx -> drawio/build/shapes_full.json
python3 drawio/tools/gen_drawio.py        # -> drawio/*.drawio (+ SVG preview in drawio/build/)
python3 drawio/tools/export_pdf.py drawio/3gpp-overall-architecture.drawio \
        drawio/export/3gpp-overall-architecture-A0.pdf
python3 drawio/tools/export_pdf.py drawio/3gpp-overall-architecture-rel19-composite.drawio \
        drawio/export/3gpp-overall-architecture-rel19-composite-A0.pdf
```

必要なもの：Python 3（`numpy` 不要）、PDF 書き出しには draw.io デスクトップ版（v24 以降）・`xvfb-run`・`pypdf`。

原図に無い要素はヘッダー（タイトル帯）のみです。派生版で追加したセルは `add_` 接頭辞の ID で判別できます。
