# トラブルシューティングガイド

このドキュメントは、Amazon Web Services (AWS) IoT Core - 基礎学習プロジェクトの包括的なトラブルシューティングガイダンスを提供します。

## 目次

- [よくある問題](#よくある問題)
  - [AWS認証情報](#aws認証情報)
  - [仮想環境の問題](#仮想環境の問題)
  - [依存関係の問題](#依存関係の問題)
  - [権限の問題](#権限の問題)
  - [証明書の問題](#証明書の問題)
- [MQTT接続の問題](#mqtt接続の問題)
  - [証明書ベースMQTTの問題](#証明書ベースmqttの問題)
  - [WebSocket MQTTの問題](#websocket-mqttの問題)
- [Device Shadowの問題](#device-shadowの問題)
  - [Shadow接続の問題](#shadow接続の問題)
  - [Shadow状態ファイルの問題](#shadow状態ファイルの問題)
- [Rules Engineの問題](#rules-engineの問題)
  - [ルール作成の問題](#ルール作成の問題)
  - [ルールテストの問題](#ルールテストの問題)
- [OpenSSLの問題](#opensslの問題)
  - [インストールの問題](#インストールの問題)
  - [証明書生成の問題](#証明書生成の問題)
- [ネットワークと接続の問題](#ネットワークと接続の問題)
  - [ファイアウォールとプロキシの問題](#ファイアウォールとプロキシの問題)
  - [DNS解決の問題](#dns解決の問題)
- [パフォーマンスとタイミングの問題](#パフォーマンスとタイミングの問題)
  - [APIレート制限](#apiレート制限)
  - [接続タイムアウト](#接続タイムアウト)
- [追加ヘルプの取得](#追加ヘルプの取得)
  - [デバッグモードの使用](#デバッグモードの使用)
  - [AWS IoTコンソール確認](#aws-iotコンソール確認)
  - [CloudWatchログ](#cloudwatchログ)
  - [一般的な解決手順](#一般的な解決手順)
  - [サポートリソース](#サポートリソース)

## よくある問題

### AWS認証情報

#### 認証情報が設定されているか確認
```bash
# 認証情報が設定されているか確認
aws sts get-caller-identity

# 現在のリージョンを確認
echo $AWS_DEFAULT_REGION

# 環境変数をリスト
env | grep AWS
```

#### よくある認証情報の問題

**問題: "Unable to locate credentials"**
```bash
# 解決策1: 環境変数を設定
export AWS_ACCESS_KEY_ID=<your-access-key>
export AWS_SECRET_ACCESS_KEY=<your-secret-key>
export AWS_DEFAULT_REGION=us-east-1

# 解決策2: AWS CLI設定を使用
aws configure

# 解決策3: 既存の設定を確認
aws configure list
```

**問題: "You must specify a region"**
```bash
# デフォルトリージョンを設定
export AWS_DEFAULT_REGION=us-east-1

# またはAWS CLI設定で指定
aws configure set region us-east-1
```

**問題: "The security token included in the request is invalid"**
- **原因**: 期限切れの一時認証情報または不正なセッショントークン
- **解決策**: 認証情報を更新するか、期限切れのセッショントークンを削除
```bash
unset AWS_SESSION_TOKEN
# その後、新しい認証情報を設定
```

### 仮想環境の問題

#### 仮想環境を確認
```bash
# venvがアクティブか確認
which python
# 表示されるべき: /path/to/your/project/venv/bin/python

# Pythonバージョンを確認
python --version
# 3.7以上である必要があります

# インストール済みパッケージをリスト
pip list
```

#### 仮想環境の作成と有効化
```bash
# 新しい仮想環境を作成
python -m venv venv

# 仮想環境を有効化
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# 依存関係をインストール
pip install -r requirements.txt
```

### 依存関係の問題

#### 必要なパッケージの確認
```bash
# requirements.txtの内容を確認
cat requirements.txt

# 特定のパッケージがインストールされているか確認
pip show boto3
pip show awsiotsdk

# すべての依存関係を再インストール
pip install -r requirements.txt --upgrade
```

#### よくある依存関係エラー

**問題: "ModuleNotFoundError: No module named 'boto3'"**
```bash
# 解決策: boto3をインストール
pip install boto3>=1.26.0

# または全依存関係を再インストール
pip install -r requirements.txt
```

**問題: "ModuleNotFoundError: No module named 'awsiotsdk'"**
```bash
# 解決策: AWS IoT SDKをインストール
pip install awsiotsdk>=1.11.0
```

### 権限の問題

#### 必要なIAM権限
学習スクリプトには以下のIAM権限が必要です:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "iot:*",
        "iam:CreateRole",
        "iam:AttachRolePolicy",
        "iam:PassRole",
        "sts:GetCallerIdentity"
      ],
      "Resource": "*"
    }
  ]
}
```

#### 権限エラーの診断
```bash
# 現在のユーザー/ロールを確認
aws sts get-caller-identity

# 特定のアクションをテスト
aws iot list-things --max-results 1
aws iot describe-endpoint --endpoint-type iot:Data-ATS
```

**問題: "AccessDeniedException"**
- **原因**: 不十分なIAM権限
- **解決策**: IAMユーザーまたはロールに適切な権限を付与

### 証明書の問題

#### 証明書ファイルの確認
```bash
# 証明書ディレクトリの存在確認
ls -la certificates/

# 特定のThing用証明書ファイルを確認
ls -la certificates/Vehicle-VIN-001/

# 証明書ファイルの内容を確認
openssl x509 -in certificates/Vehicle-VIN-001/cert.crt -text -noout
```

#### よくある証明書エラー

**問題: "Certificate files not found"**
```bash
# 解決策: certificate_manager.pyを実行して証明書を作成
python certificate_manager.py
# オプション1を選択して新しい証明書を作成
```

**問題: "Certificate is not active"**
```bash
# 解決策: 証明書をアクティブ化
python certificate_manager.py
# 証明書を選択してアクティブ化
```

## MQTT接続の問題

### 証明書ベースMQTTの問題

#### 接続診断
```bash
# デバッグモードでMQTTクライアントを実行
python mqtt_client_explorer.py --debug

# 証明書ファイルの権限を確認
ls -la certificates/*/
```

#### よくあるMQTT接続エラー

**問題: "SSL: CERTIFICATE_VERIFY_FAILED"**
- **原因**: 無効または期限切れの証明書
- **解決策**: 新しい証明書を作成し、適切なポリシーをアタッチ

**問題: "Connection refused"**
- **原因**: 不正なエンドポイントまたはポート
- **解決策**: エンドポイントを確認
```bash
aws iot describe-endpoint --endpoint-type iot:Data-ATS
```

**問題: "MQTT connection timeout"**
- **原因**: ネットワーク問題またはファイアウォール
- **解決策**: ポート8883（MQTT over TLS）が開いていることを確認

### WebSocket MQTTの問題

#### WebSocket接続診断
```bash
# デバッグモードでWebSocket MQTTクライアントを実行
python mqtt_websocket_explorer.py --debug

# AWS認証情報を確認
aws sts get-caller-identity
```

#### よくあるWebSocket MQTTエラー

**問題: "WebSocket connection failed"**
- **原因**: 無効なAWS認証情報または権限
- **解決策**: 認証情報を確認し、IoT権限を付与

**問題: "Signature mismatch"**
- **原因**: 時刻同期の問題
- **解決策**: システム時刻を同期
```bash
# macOS
sudo sntp -sS time.apple.com

# Linux
sudo ntpdate -s time.nist.gov
```

## Device Shadowの問題

### Shadow接続の問題

#### Shadow操作の診断
```bash
# デバッグモードでShadowエクスプローラーを実行
python device_shadow_explorer.py --debug

# 手動でShadowを確認
aws iot-data get-thing-shadow --thing-name Vehicle-VIN-001 shadow.json
cat shadow.json | python -m json.tool
```

#### よくあるShadowエラー

**問題: "ResourceNotFoundException: No shadow exists for the specified thing"**
- **原因**: Shadowがまだ作成されていない
- **解決策**: 希望する状態または報告された状態を更新してShadowを作成

**問題: "InvalidRequestException: Invalid JSON"**
- **原因**: 不正なJSON形式
- **解決策**: JSON構文を確認
```bash
# JSONを検証
echo '{"state":{"desired":{"temp":22}}}' | python -m json.tool
```

### Shadow状態ファイルの問題

**問題: Shadow更新が反映されない**
- **原因**: バージョン競合または権限問題
- **解決策**: 最新のShadowを取得してからバージョンを確認

## Rules Engineの問題

### ルール作成の問題

#### ルール診断
```bash
# デバッグモードでRules Engineエクスプローラーを実行
python iot_rules_explorer.py --debug

# 手動でルールを確認
aws iot get-topic-rule --rule-name YourRuleName
```

#### よくあるルールエラー

**問題: "InvalidRequestException: Invalid SQL"**
- **原因**: 不正なSQL構文
- **解決策**: SQL構文を確認
```sql
-- 正しい例
SELECT * FROM 'topic/+' WHERE temperature > 25

-- 間違った例
SELECT * FROM topic/+ WHERE temperature > 25  -- クォートなし
```

**問題: "Rule action failed"**
- **原因**: 不十分なIAM権限
- **解決策**: ルール実行ロールに適切な権限を付与

### ルールテストの問題

**問題: ルールがトリガーされない**
- **原因**: トピックパターンの不一致
- **解決策**: トピックパターンとメッセージトピックを確認
```bash
# ルールSQL: SELECT * FROM 'device/+/temperature'
# メッセージトピック: device/sensor1/temperature  ✅ 一致
# メッセージトピック: sensor/device1/temp        ❌ 不一致
```

## OpenSSLの問題

### インストールの問題

#### OpenSSLの確認
```bash
# OpenSSLがインストールされているか確認
openssl version

# OpenSSLのパスを確認
which openssl
```

#### プラットフォーム別インストール

**macOS:**
```bash
# Homebrewを使用
brew install openssl

# パスを確認
echo 'export PATH="/usr/local/opt/openssl/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install openssl libssl-dev
```

**Windows:**
- [OpenSSL公式サイト](https://www.openssl.org/)からダウンロード
- またはChocolateyを使用: `choco install openssl`

### 証明書生成の問題

**問題: "openssl: command not found"**
- **解決策**: OpenSSLをインストールし、PATHに追加

**問題: 証明書形式エラー**
```bash
# 証明書形式を確認
openssl x509 -in certificate.crt -text -noout

# PEM形式に変換（必要に応じて）
openssl x509 -in certificate.der -inform DER -out certificate.pem -outform PEM
```

## ネットワークと接続の問題

### ファイアウォールとプロキシの問題

#### 必要なポート
- **MQTT over TLS**: 8883
- **HTTPS**: 443
- **WebSocket**: 443

#### ファイアウォール設定
```bash
# macOS - ファイアウォール状態を確認
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate

# Linux - iptablesルールを確認
sudo iptables -L

# 特定のポートをテスト
telnet your-iot-endpoint.iot.us-east-1.amazonaws.com 8883
```

#### プロキシ設定
```bash
# HTTPプロキシ設定
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=http://proxy.company.com:8080

# プロキシをバイパス
export NO_PROXY=localhost,127.0.0.1,.amazonaws.com
```

### DNS解決の問題

#### DNS診断
```bash
# IoTエンドポイントのDNS解決をテスト
nslookup your-endpoint.iot.us-east-1.amazonaws.com

# 代替DNSサーバーを試す
nslookup your-endpoint.iot.us-east-1.amazonaws.com 8.8.8.8
```

## パフォーマンスとタイミングの問題

### APIレート制限

#### レート制限の診断
```bash
# デバッグモードでスクリプトを実行してレート制限を確認
python setup_sample_data.py --debug
```

**問題: "ThrottlingException"**
- **原因**: APIレート制限に達した
- **解決策**: リクエスト間に遅延を追加、またはバッチサイズを削減

### 接続タイムアウト

#### タイムアウト設定の調整
```python
# MQTTクライアントのタイムアウト設定例
mqtt_connection = mqtt_connection_builder.mtls_from_path(
    endpoint=endpoint,
    cert_filepath=cert_path,
    pri_key_filepath=key_path,
    ca_filepath=ca_path,
    client_id=client_id,
    clean_session=False,
    keep_alive_secs=30,  # キープアライブ間隔を調整
    http_proxy_options=None
)
```

## 追加ヘルプの取得

### デバッグモードの使用

すべてのスクリプトは詳細なデバッグ情報を提供します:
```bash
python script_name.py --debug
```

デバッグモードでは以下が表示されます:
- 完全なAPIリクエスト/レスポンス
- 詳細なエラーメッセージ
- 接続診断情報
- タイミング情報

### AWS IoTコンソール確認

AWS IoTコンソールで以下を確認:
1. **Things**: 作成されたデバイスの確認
2. **Certificates**: 証明書のステータス確認
3. **Policies**: ポリシーの内容確認
4. **Rules**: ルールの設定確認
5. **Logs**: CloudWatchログの確認

### CloudWatchログ

AWS IoT関連のログを確認:
```bash
# AWS CLIでログを確認
aws logs describe-log-groups --log-group-name-prefix /aws/iot

# 特定のログストリームを確認
aws logs get-log-events --log-group-name /aws/iot/rules --log-stream-name your-rule-name
```

### 一般的な解決手順

問題が発生した場合の一般的な手順:

1. **環境確認**
   ```bash
   python --version
   pip list
   aws --version
   ```

2. **認証情報確認**
   ```bash
   aws sts get-caller-identity
   aws configure list
   ```

3. **デバッグモード実行**
   ```bash
   python script_name.py --debug
   ```

4. **リソース状態確認**
   ```bash
   aws iot list-things
   aws iot list-certificates
   ```

5. **ログ確認**
   - スクリプトの出力
   - AWS IoTコンソール
   - CloudWatchログ

### サポートリソース

#### 公式ドキュメント
- [AWS IoT Core Developer Guide](https://docs.aws.amazon.com/iot/latest/developerguide/)
- [AWS IoT Device SDK](https://docs.aws.amazon.com/iot/latest/developerguide/iot-sdks.html)
- [AWS CLI Reference](https://docs.aws.amazon.com/cli/latest/reference/iot/)

#### コミュニティリソース
- [AWS IoT Forum](https://forums.aws.amazon.com/forum.jspa?forumID=210)
- [Stack Overflow - AWS IoT](https://stackoverflow.com/questions/tagged/aws-iot)
- [GitHub Issues](https://github.com/aws/aws-iot-device-sdk-python-v2/issues)

#### AWS サポート
- [AWS Support Center](https://console.aws.amazon.com/support/)
- [AWS Trusted Advisor](https://console.aws.amazon.com/trustedadvisor/)

---

このトラブルシューティングガイドで問題が解決しない場合は、デバッグモードの出力とエラーメッセージを含めて、上記のサポートリソースに問い合わせてください。