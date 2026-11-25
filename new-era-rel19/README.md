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
