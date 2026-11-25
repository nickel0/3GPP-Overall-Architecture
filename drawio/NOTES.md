# 複合盤 draw.io 版 設計メモ（全面描き直し）

対象ファイル：
- `composite-diagram-drawio-master.drawio` — 原図（Rel-17まで）の draw.io 再現（マスター）
- `composite-diagram-drawio.drawio` — 複合盤（マスター＋Rel-18／Rel-19 追加分を本図内に統合）
- `composite-diagram-drawio.pdf` — 複合盤を draw.io 本体（CLI）で書き出した PDF（後述の縮尺注意あり）

複合盤の定義は v0 と同じ：小川さんの原図に Rel-18／Rel-19 の差分を累積追加した全部入り最新版。主根拠は `../rel18-19-diff-list.md`、TS 23.501 V19.9.0、TS 23.369 V19.5.0、TS 38.300。
v0 の合成（オーバーレイ）方式は卒業し、本版は**原図の全図形を draw.io の編集可能なセルとして再現した単一ファイル**が正本。

## 方式：pptx 機械抽出 → mxGraph XML 変換パイプライン（手作業の描き写しなし）

生成物はすべてスクリプトから再生成できる。再生成手順：

```
.venv/bin/python composite/work/extract_full.py   # pptx -> work/shapes_full.json
.venv/bin/python composite/work/gen_drawio.py     # json -> .drawio x2 + 検証 + SVGプレビュー
```

- `work/extract_full.py`：pptx の slide1 XML を直接解析。グループ変換を平坦化し、全図形の絶対座標・サイズ・preset 形状・塗り・線（色／太さ／破線／矢印）・テキストラン（サイズ・太字・色）・回転・反転・コネクタの接続参照（stCxn/endCxn＋接続点 idx）・フリーフォームの custGeom パスを抽出。色は schemeClr／prstClr／sysClr をテーマ色（Office Theme）に解決し、lumMod／lumOff／tint／shade も適用。
- `work/gen_drawio.py`：抽出 JSON から mxGraph XML を生成。座標系は draw.io 単位＝pt、ページは **A0 横向き実寸（3370×2384 pt）**。原図スライド（554.5×311.9mm）は幅いっぱいに拡大（×2.145、フォント・線幅も同率で拡大）し、上部にタイトル帯（120 units）を確保。
- PDF 書き出しは draw.io デスクトップ版 CLI（`xvfb-run drawio -x -f pdf`）で実施できた。**注意：CLI 書き出しの PDF は 2426×1716 pt に縮小された（ページ実寸の約0.72倍）。印刷用に A0 実寸で出す場合は、draw.io の Export で scale を調整すること。** .drawio 自体のページ設定は A0 実寸。

## 再現の検証結果

- 抽出図形は **801個**（sp 555＋cxnSp 246）で、全数が draw.io セルに 1:1 変換された（マスターの original 由来セル＝801）。
- **テキスト欠落ゼロ**：テキストを持つ図形 518件すべてについて、pptx 側テキストと .drawio 側セル値が（空白正規化後）完全一致することを自動検証した。マスター・複合盤の両方で不一致 0件。
- 配置・色分けは自前 SVG レンダラのプレビューと draw.io 本体の PDF 書き出しの両方で目視確認し、原図 PDF と大まかな配置・色（黒／緑 00B050／青 0070C0／グレー 404040）が一致することを確認した。

### 変換の近似・割り切り（マスターの既知の差異）

1. **コネクタの接続点**：pptx の接続点 idx を draw.io の exitX/exitY（辺中央）に写像した。原図と異なる辺に付く場合があり、draw.io 側の再ルーティングで線の形は原図と同一にはならない（接続先の対応は保持）。
2. **フリーフォーム 10件**（大きな枠線・斜め区切り線）：draw.io に任意多角形の頂点シェイプが無いため、始点・終点＋中間点を持つ**フリーエッジ（折れ線）**として再現した。編集は可能だが「1図形」ではなく「線」として扱われる。
3. **ブラケット 11件**（leftBracket／rightBracket）：draw.io の `mxgraph.basic.l_bracket`／`r_bracket` シェイプ名で出力した。ステンシル名の実在は draw.io 本体の書き出しで致命的エラーにならないことまでしか確認しておらず、開いた環境で要確認（違えば四角に化ける）。
4. **円弧 1件・エルボーコネクタ形状 6件**：折れ線エッジで近似した。
5. 回転テキスト 2件（斜めラベル）は rotation 属性で再現。グループ図形は平坦化したため、原図のグループ構造は復元されない（見た目と編集可能性を優先）。
6. マスターにも識別用のヘッダー（タイトル＋「faithful reproduction」注記）だけは追加した。これが原図に無い唯一の追加要素。

## 追加分（Rel-18／Rel-19）の統合

**原図要素の移動はゼロ**（全セルが pptx 座標のまま）。追加は新規セルのみ：頂点 +14、エッジ +22。

### 新規ボックス 6件の配置（すべて本図内）

配置は「枠・塗りのある図形との重なりゼロ」をハード条件に、線の貫通と接続先までの距離でスコアリングする自動配置（生成スクリプト内）＋一部手動固定で行った。

| 要素 | 色 | 配置（スライドmm座標） | 置き場所の理由 |
|---|---|---|---|
| AIoT Device | 青 | (328.3, 239.5) 16.5×5.8 | 5GC 枠右辺（x=329.2）と右側パネル群（x≧347）の間の縦ストリップ。CHF の東、Release-17 Enhancements パネルの西 |
| AIOTF | 青 | (328.3, 247.5) 16.5×5.8 | 同ストリップ、AIoT Device の下（AIOT1 で直結） |
| ADM | 青 | (328.3, 255.5) 17.0×5.8 | 同ストリップ、AIOTF の下（AIOT6 で直結） |
| EIF | 青 | (328.3, 266.5) 16.5×5.8 | 同ストリップ最下段。PCF／PGW-C(A-)SMF／AF に最も近い空き |
| NCR | 緑 | (107.0, 277.0) 13.8×5.8 | AMF の南西下、NG-RAN 枠の東隣。N3 の太線（ユーザープレーン）を避けた位置を自動配置で選択 |
| NR Femto | 青 | (150.0, 272.0) 13.8×5.8 | AMF と NSACF の間、N3 線の北側 |

### 線 22件（すべて draw.io コネクタ＝エルボー＋ラインジャンプ有効で実線化）

- **EIF**：N110（AF）／N111（NEF）／N112（UDM）／N113（PCF）／N114（PGW-C (A-)SMF）の5件を実線。キャプション「29.566 Neif (SBI)」を EIF 直下に配置
- **Ambient IoT**：AIOT1（Device–AIOTF、論理参照点のため破線）／AIOT2（AIOTF–NG-RAN）／AIOT3（AIOTF–AMF）／AIOT4（AIOTF–NEF）／AIOT5（AIOTF–NRF）／AIOT6（AIOTF–ADM）／AIOT7（ADM–UDR）／AIOT8（ADM–NEF）の8件を実線。キャプション「Naiotf (SBI) / Nadm (SBI)」を ADM 直下に配置
- **Rel-18**：N89（TSCTSF–AMF）／N96（TSCTSF–NRF）を実線化（v0 では注記のみだったもの。TSCTSF は Release-17 Enhancements パネル内の既存セルに接続）。N97／N99 は NSACF 右辺に短い実線＋チップ文字（other PLMN／same PLMN）で表現。Nupf は PGW-U (PSA-)UPF 上辺に緑チップ「Nupf」を密着配置
- **Rel-19**：N116（SCP–NWDAF）／N117（SCP–DCCF、DCCF はパネル内セルに接続）を実線化。NR Femto は N2（AMF）／N3（PGW-U (PSA-)UPF）を実線。NCR は NG-RAN へ「gNB control」の実線
- 機能節レベルの追加（Rel-18：§5.20b–d／§5.28a／§5.35A／§5.43–5.46／eRedCap／DetNet／XR 等、Rel-19：§4.2.18／§5.48／§5.49／§5.51／§5.52／サイドリンク multi-hop／LP-WUS・WUR／SBFD／AI/ML 等）は、ページ下帯の Release-18／Release-19 Enhancements 一覧テキストに収録

### 色の意味の衝突への対処

- 原図内では緑＝Rel-16・青＝Rel-17 として既に使われており、追加分の緑＝Rel-18・青＝Rel-19 と二重の意味になる（v0 からの引き継ぎ論点）。
- 対処（実装済み）：(1) ページ下帯に色の衝突を明示する注記（Colour note）を置いた。(2) 追加要素は全件このメモと下帯一覧に列挙し、追加セルの ID を `add_` 接頭辞で機械的に区別できるようにした。(3) 追加ボックスは白塗り＋色枠＋色文字で統一し、原図の既存 NF（多くは無塗り）との見分けが付くようにした。
- 根本対処（色相をずらす等）は小川さんレビューでの確認事項として残す。

## fork への配置提案（コミット／push は別作業）

正本は小川さんの repo（nickel0/3GPP-Overall-Architecture）の **fork を本拠**にする方針（ユーザー決定 2026-11-25）。fork 内では以下の構成を提案する。

```
drawio/
  3gpp-overall-architecture.drawio                 <- マスター（原図の draw.io 再現）
  3gpp-overall-architecture-rel19-composite.drawio <- 複合盤（マスターからの派生）
  README.md                                        <- 位置づけ・再生成手順・色の衝突の注記
  tools/
    extract_full.py                                <- pptx 抽出
    gen_drawio.py                                  <- .drawio 生成＋検証
```

- ローカルファイルとの対応：`composite-diagram-drawio-master.drawio` → `drawio/3gpp-overall-architecture.drawio`、`composite-diagram-drawio.drawio` → `drawio/3gpp-overall-architecture-rel19-composite.drawio`、`composite/work/extract_full.py` と `composite/work/gen_drawio.py` → `drawio/tools/`。
- 命名の考え方：**マスター＝原図の draw.io 再現**（ファイル名に release を付けず、原図 repo の既存ファイル `3GPP_Overall_Architecture_and_Specifications.pptx` と対になる名前）、**複合盤＝そこからの派生**（`-rel19-composite` サフィックスで派生関係を明示）。New ERA版を draw.io 化する場合も同じ規則で `3gpp-overall-architecture-new-era.drawio` のように派生として並べる。
- ブランチ提案：マスター用に `drawio/master`、複合盤用に `drawio/master` から分岐した `drawio/rel19-composite` の2段構成。上流への PR は「マスター再現のみ」の PR を先に出し（原図の編集可能化という単独で意味のある変更）、複合盤はその上に重ねる PR とするのが取り込み判断を分けやすい。既存の PR #11（New ERA）とは独立に進める。
- pptx は fork 内に原典として残し、draw.io 版が正本（編集先）という関係を `drawio/README.md` に明記する。

## 残件

- ブラケットのステンシル名（`mxgraph.basic.l_bracket` 等）が diagrams.net 現行版で正しいかの実機確認
- 追加エッジの自動ルーティングは交差が多い（特に AIOT2／AIOT3、N89／N96、N116／N117 の長距離線）。完成図の段で waypoints の手調整が要る
- 接続点 idx の写像近似により、一部の原図コネクタが原図と違う辺に付く。気になる線から exit/entry を手で詰める作業が残る
- PDF 書き出しの縮尺（A0 実寸で出すための Export 設定の確定）
- フォントは Arial 前提で出力（原図の和文フォント Noto Sans JP 指定は draw.io 側で未再現）
- CHF／BSF は差分対象外のため原図のまま（変更なし）。ライセンス表記（原図の CC BY-NC-SA）は原図セルのまま残っており、販売版での整理は別途必要
