# New ERA Edition — 5G SA Architecture Diagram (Release-19) / Draft

このフォルダは、小川宗明さんの「3GPP Overall Architecture and Specifications」
（Release-17 まで）の続編として作成した、**Release-19 ベースの 5G SA
（Standalone）専用アーキテクチャ図の下書き**です。

This folder contains a **draft** of a 5G Standalone (SA) architecture diagram
based on Release-19, created as a sequel to Muneaki Ogawa's "3GPP Overall
Architecture and Specifications" (up to Release-17).

## ファイル / Files

- `new-era-diagram-v3.svg` — 図（SVG、テキスト編集可能）
- `new-era-diagram-v3.pdf` — 図（PDF、A0 横向き 1189×841mm）
- `new-era-v3-notes.md` — 設計メモ（配置対応表・参照点対応表・残件）
- v3 は、カテゴリゾーンの背景塗りを外して線とラベルを最前面にしたうえで、
  **法的傍受（LI、TS 33.127）を追加した版**です（ADMF／MDF2／MDF3、
  LI_X1／X2／X3 等を描画）
  (v3 removes the category-zone fills, brings the interface lines/labels
  to the front layer, and adds Lawful Interception (LI, TS 33.127):
  ADMF, MDF2/MDF3, LI_X1/X2/X3, etc.)

## 描き方 / Approach

- ノードの相対配置は原図（Rel-17 図）の 5GC 部分の骨格を踏襲し、
  レガシー（CS / GERAN・UTRAN / EPC / 世代間インターワーク）を除いて再構成
- 参照点は SBA バスで省略せず、点対点で描画。TS 23.501 §4.2 の参照点
  70 件中 69 件を描画（SA 範囲外の N26 のみ除外、理由は notes に記載）
- 線には参照点番号を添え、定まるものはプロトコル／サービス名を併記
  （例：N2 = NGAP、N3/N9 = GTP-U、SBI は「29.518 Namf」の形式で箱下に併記）
- 色分けは原図の流儀を継承（黒 = 〜Rel-17 / 緑 = Rel-18 / 青 = Rel-19）

## 根拠仕様 / Basis specifications

- TS 23.501 V19.9.0 (Release-19) — 5GS アーキテクチャ、NF 一覧（§6.2）、参照点（§4.2）
- TS 33.127 V19.8.0 — 法的傍受（LI）アーキテクチャ（ADMF／MDF、LI_X1／X2／X3）
- TS 23.369 V19.5.0 — Ambient IoT（AIOTF = Ambient IoT Function、
  ADM = AIoT Data Management、参照点 AIOT1〜AIOT8）
- TS 38.300 — NG-RAN の構成
- TR 21.918 / TR 21.919 — Release-18 / 19 の差分確認

## 状態と残件 / Status and open items

- あくまで下書き（Draft）です。完成図ではありません
- Nmb5 は TS 23.247 の原典定義と未照合（要取得・照合）
- N70 / N71（SBA in IMS）は相手先未照合のため線を引かず注記のみ
- 中心部のラベル近接など、レイアウト調整は継続中

Prepared by RE-X K.K. (Powered by RE-X) — poster project for Ogawa's diagram.

## draw.io 版 / draw.io version

- `new-era-diagram.drawio` — **正本（マスター）**。diagrams.net / draw.io
  デスクトップで編集できます。線はエルボーコネクタで引き、交差部には
  ラインジャンプを使う draw.io の流儀で再構成した版です
  (The master file. Editable in diagrams.net / draw.io Desktop.
  Edges use elbow connectors and line jumps.)
- `new-era-diagram-drawio.pdf` / `new-era-diagram-drawio.svg` —
  上記 `.drawio` からの書き出しです
  (Exports from the .drawio master.)
- `new-era-drawio-notes.md` — draw.io 化の設計メモ
- SVG 直描き版（`new-era-diagram-v3.svg` / `.pdf`）は比較用として
  残しています

**注意 / Note**：CLI で書き出した PDF は実寸の 0.72 倍
（1141.6×807.6mm）で出力されます。A0（1189×841mm）で印刷する際は
スケール調整が必要です。
(The CLI-exported PDF comes out at 0.72x actual size
(1141.6 x 807.6 mm); rescale when printing at A0, 1189 x 841 mm.)

**更新（v6）/ Update (v6)**：正本を v6 に更新しました。バッジは
「New ERA · SA Only · Release-19」、カテゴリは CORE — 5GC の内側に
サブカテゴリを入れる二段構えに細分化し、ポスターのタイトル帯・
クレジット帯（3GPP ロゴ、© 表記、QR、Powered by RE-X）と
「New ERA — The Standalone Era」の説明文を追加しています。
詳細は `new-era-drawio-notes.md` を参照してください。
(The master is now v6: badge "New ERA · SA Only · Release-19",
two-level category zones inside CORE — 5GC, poster title/credit
bands, and a short "New ERA — The Standalone Era" note.
See `new-era-drawio-notes.md` for details.)

**更新（v7）/ Update (v7)**：正本を v7 に更新しました。変更はゾーン
見出しタブの幅計算の修正のみです。実フォントの文字幅から幅を求める
ようにし、はみ出していた4つのタブ（SBA COMMON／PUBLIC WARNING／
CORE — CONTROL／NON-3GPP ACCESS）を解消しました。ノードの配置・
配線・本文は v6 から不変です。詳細は `new-era-drawio-notes.md` を
参照してください。
(The master is now v7. The only change is the zone-tab chip width
calculation, now based on real glyph widths; the four overflowing
tabs (SBA COMMON / PUBLIC WARNING / CORE — CONTROL /
NON-3GPP ACCESS) are fixed. Layout, routing and content are
unchanged from v6. See `new-era-drawio-notes.md` for details.)
