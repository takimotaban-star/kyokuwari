# 曲割（Kyokuwari）Windows 11 x64 ベータ版

曲割は、長い音声ファイルの無音区間から曲の区切り候補を見つけ、曲ごとのMP3に分割するWindowsアプリです。分割したファイルには、AcoustIDで見つかった曲名をタグとして書き込みます。

これは**ベータ版**です。正式な対応環境は **Windows 11 x64** のみです。

## 使い方

1. ZIPを**すべて展開**します。ZIPの中から直接起動しないでください。
2. 展開した `kyokuwari` フォルダの `kyokuwari.exe` を起動します。現在のベータ版では、ウィンドウのタイトルは「音楽分割プログラム」と表示されます。
3. `kyokuwari.exe` と `_internal` フォルダは同じ場所に置いたままにします。

FFmpeg、FFprobe、fpcalc は同梱しているため、別途インストールする必要はありません。

`kyokuwari.exe` にはコード署名がないため、Windowsの警告が表示される場合があります。入手元が正しいGitHub Releaseであること、ZIPのSHA-256がReleaseの `SHA256SUMS.txt` と一致することを確認してください。

## 起動しないとき

このベータ版には Microsoft Visual C++ ランタイムを同梱していません。`VCRUNTIME140.dll` や `VCRUNTIME140_1.dll` が見つからないというエラーが出る場合や、起動せずに終了する場合は、Microsoft公式の x64 版をインストールしてから再度起動してください。

<https://aka.ms/vc14/vc_redist.x64.exe>

Visual C++ ランタイムが未導入のPCでの動作は、まだ十分に検証していません。インストール後も起動しない場合は、不具合として報告してください。

## AcoustID への送信

曲割は、**分割した各MP3について自動で**、音声から作った指紋（フィンガープリント）と曲の長さを AcoustID Webサービス（`api.acoustid.org`）へ送信し、曲名を検索します。音声ファイルそのものは送信しません。現在のベータ版には、この送信を無効にする設定はありません。送信を望まない場合は、分割を実行しないでください。インターネットに接続していない場合、曲名は取得できません。

AcoustID の無料APIは**非商用利用**を対象とし、**1秒あたり3リクエストまで**です。多くの通信が見込まれる場合は事前の連絡が必要です。曲割のソースコードのMITライセンスは、AcoustIDサービスの商用利用を許可するものではありません。商用で利用する場合は、AcoustID の公式案内を確認してください。 <https://acoustid.org/webservice>

## 不具合の報告

このソフトを入手したGitHubリポジトリの **Issues** に、次の内容を書いてください。

- Windowsのバージョン（例: Windows 11 24H2 x64）
- 操作の手順と、表示されたエラー文
- 音声の形式とおおよその長さ

著作権のある音声ファイルは添付しないでください。

## ライセンスとソースコード

- 作者が作成したPythonソースは **MIT License**（`Copyright (c) 2026 Ben Takimoto`）です。`LICENSE` を参照してください。
- `kyokuwari.exe` は GPL-2.0-or-later の Mutagen 1.48.1 を含むため、この実行ファイルの組み合わせは **GNU GPL version 3** の条件で配布します。`DISTRIBUTION_LICENSE.md` を参照してください。
- FFmpeg / FFprobe は **LGPL version 3 以降**の BtbN Windows x64 静的ビルドです。`FFMPEG_BUILD_NOTICE.md` を参照してください。
- fpcalc（Chromaprint 1.6.2）とその他の第三者コンポーネントの条件は `THIRD_PARTY_NOTICES.md` と `LICENSES/` にあります。
- 対応ソースと改変・再リンク用の資料は、このZIPと同じGitHub Releaseの Assets から、追加費用なしで取得できます。一覧は `SOURCE_OFFER.md` にあります。

アイコンは ChatGPT で生成した画像で、作者が曲割への同梱と配布を許可しています。
