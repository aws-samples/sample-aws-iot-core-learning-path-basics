# 詳細スクリプトドキュメント

このドキュメントは、AWS IoT Core - 基礎プロジェクトのすべての学習スクリプトの包括的なドキュメントを提供します。

## 目次

- [IoT Registry API エクスプローラー](#iot-registry-api-エクスプローラー)
  - [目的](#目的)
  - [実行方法](#実行方法)
  - [インタラクティブメニューシステム](#インタラクティブメニューシステム)
  - [学習詳細付きサポートAPI](#学習詳細付きサポートapi)
  - [学習機能](#学習機能)
  - [エラー学習](#エラー学習)
- [証明書・ポリシーマネージャー](#証明書ポリシーマネージャー)
  - [目的](#目的-1)
  - [実行方法](#実行方法-1)
  - [インタラクティブメインメニュー](#インタラクティブメインメニュー)
  - [オプション1: 完全証明書ワークフロー](#オプション1-完全証明書ワークフロー)
  - [オプション2: 外部証明書登録](#オプション2-外部証明書登録)
  - [オプション3: ポリシーアタッチワークフロー](#オプション3-ポリシーアタッチワークフロー)
  - [オプション4: ポリシーデタッチワークフロー](#オプション4-ポリシーデタッチワークフロー)
  - [オプション5: 証明書ステータス管理](#オプション5-証明書ステータス管理)
  - [証明書管理詳細](#証明書管理詳細)
  - [ポリシー管理詳細](#ポリシー管理詳細)
  - [API学習機能](#api学習機能)
  - [証明書オプション説明](#証明書オプション説明)
  - [エラー学習シナリオ](#エラー学習シナリオ)
- [MQTT通信](#mqtt通信)
  - [目的](#目的-2)
  - [利用可能な2つのMQTTオプション](#利用可能な2つのmqttオプション)
  - [証明書ベースMQTTクライアント](#証明書ベースmqttクライアント)
  - [WebSocket MQTTクライアント](#websocket-mqttクライアント)
  - [MQTTプロトコル学習](#mqttプロトコル学習)
- [AWS IoT Device Shadow service エクスプローラー](#device-shadow-エクスプローラー)
  - [目的](#目的-3)
  - [実行方法](#実行方法-2)
  - [前提条件](#前提条件)
  - [インタラクティブDevice Shadow学習](#インタラクティブdevice-shadow学習)
  - [主要学習機能](#主要学習機能)
  - [シャドウメッセージ分析](#シャドウメッセージ分析)
  - [学習シナリオ](#学習シナリオ)
  - [必要なIAM権限](#必要なiam権限)
- [IoT Rules Engine エクスプローラー](#iot-rules-engine-エクスプローラー)
  - [目的](#目的-4)
  - [実行方法](#実行方法-3)
  - [前提条件](#前提条件-1)
  - [インタラクティブRules Engine学習](#インタラクティブrules-engine学習)
  - [主要学習機能](#主要学習機能-1)
  - [ルール管理機能](#ルール管理機能)
  - [自動IAM設定](#自動iam設定)
  - [ルールのテスト](#ルールのテスト)
  - [学習シナリオ](#学習シナリオ-1)
  - [必要なIAM権限](#必要なiam権限-1)

## IoT Registry API エクスプローラー

### 目的
詳細な説明付きの実際のAPI呼び出しを通じてAWS IoT Registry APIを学習するためのインタラクティブツール。このスクリプトは、IoTデバイス、証明書、ポリシーを管理するために使用されるコントロールプレーン操作を教えます。

**注意**: AWS IoT Coreは、デバイス管理とセキュリティにわたって多くのAPIを提供します。このエクスプローラーは、IoTデバイスライフサイクル管理を理解するために不可欠な8つのコアRegistry APIに焦点を当てています。完全なAPI詳細については、[AWS IoT Registry API リファレンス](https://docs.aws.amazon.com/iot/latest/apireference/API_Operations_AWS_IoT.html)を参照してください。

### 実行方法

**基本使用法:**
```bash
python iot_registry_explorer.py
```

**デバッグモード付き（拡張API詳細）:**
```bash
python iot_registry_explorer.py --debug
```

### インタラクティブメニューシステム

スクリプトを実行すると、以下が表示されます:
```
📋 利用可能な操作:
1. Thingsをリスト
2. 証明書をリスト
3. Thing Groupsをリスト
4. Thing Typesをリスト
5. Thingを詳細表示
6. Thing Groupを詳細表示
7. Thing Typeを詳細表示
8. エンドポイントを詳細表示
9. 終了

操作を選択 (1-9):
```

### 学習詳細付きサポートAPI

#### 1. List Things
- **目的**: アカウント内のすべてのIoTデバイスを取得
- **HTTP**: `GET /things`
- **学習内容**: ページネーションとフィルタリングオプションを使用したデバイス発見
- **利用可能なオプション**:
  - **基本リスト**: すべてのThingsを表示
  - **ページネーション**: より小さなバッチでThingsを取得（ページあたりの最大結果数を指定）
  - **Thing Typeフィルタリング**: 特定のThing Typeでフィルタリング
  - **属性フィルタリング**: カスタム属性でフィルタリング

#### 2. List Certificates
- **目的**: アカウント内のすべてのX.509証明書を取得
- **HTTP**: `GET /certificates`
- **学習内容**: セキュリティ監査とライフサイクル管理のための証明書発見
- **表示情報**:
  - 証明書ID
  - ステータス（ACTIVE、INACTIVE、REVOKED）
  - 作成日
  - 有効期限

#### 3. List Thing Groups
- **目的**: 組織階層のためのThing Groupsを取得
- **HTTP**: `GET /thing-groups`
- **学習内容**: デバイス組織とグループベース操作
- **表示情報**:
  - グループ名
  - 説明
  - 作成日
  - 親グループ関係

#### 4. List Thing Types
- **目的**: デバイステンプレートとしてのThing Typesを取得
- **HTTP**: `GET /thing-types`
- **学習内容**: デバイス標準化とテンプレートベース管理
- **表示情報**:
  - タイプ名
  - 説明
  - 属性スキーマ
  - 作成日

#### 5. Describe Thing
- **目的**: 特定のThingの詳細情報を取得
- **HTTP**: `GET /things/{thingName}`
- **学習内容**: 個別デバイス管理と属性分析
- **詳細情報**:
  - Thing属性
  - Thing Type関連付け
  - Thing Group メンバーシップ
  - バージョン情報

#### 6. Describe Thing Group
- **目的**: Thing Groupの詳細設定を取得
- **HTTP**: `GET /thing-groups/{thingGroupName}`
- **学習内容**: グループベース管理とポリシー継承
- **詳細情報**:
  - グループプロパティ
  - 親子関係
  - メンバーデバイス
  - 適用ポリシー

#### 7. Describe Thing Type
- **目的**: Thing Typeの仕様を取得
- **HTTP**: `GET /thing-types/{thingTypeName}`
- **学習内容**: デバイステンプレートとスキーマ管理
- **詳細情報**:
  - 属性スキーマ
  - 説明
  - 作成日
  - 非推奨ステータス

#### 8. Describe Endpoint
- **目的**: IoT接続エンドポイントを取得
- **HTTP**: `GET /endpoint`
- **学習内容**: デバイス接続設定とプロトコル理解
- **エンドポイントタイプ**:
  - iot:Data-ATS（MQTT/HTTPS）
  - iot:CredentialProvider（認証情報プロバイダー）
  - iot:Jobs（AWS IoT Jobs ジョブ管理）

### 学習機能

#### インタラクティブ学習モーメント
各API操作の前に、以下を含む教育コンテンツが表示されます:
- **目的**: APIが解決する問題
- **使用例**: 実際のIoTシナリオ
- **ベストプラクティス**: 効果的な使用方法
- **関連概念**: 関連するIoT概念

#### デバッグモード学習
`--debug`フラグを使用すると、以下が表示されます:
- **完全なHTTPリクエスト**: メソッド、URL、ヘッダー
- **リクエストペイロード**: 送信されるJSONデータ
- **完全なHTTPレスポンス**: ステータスコード、ヘッダー、ボディ
- **エラー詳細**: 失敗時の完全な診断情報

#### ページネーション学習
List操作では、以下を学習できます:
- **ページサイズ制御**: 結果数の制限
- **継続トークン**: 大きなデータセットの処理
- **効率的なデータ取得**: メモリとネットワークの最適化

### エラー学習

スクリプトは、以下の一般的なエラーシナリオを教育目的で処理します:

#### 認証エラー
- **InvalidCredentials**: 無効なAWS認証情報
- **AccessDenied**: 不十分なIAM権限
- **TokenExpired**: 期限切れのセッショントークン

#### リソースエラー
- **ResourceNotFound**: 存在しないThing/Group/Type
- **ResourceAlreadyExists**: 重複リソース作成試行
- **LimitExceeded**: アカウント制限超過

#### 設定エラー
- **InvalidRequest**: 不正なパラメータ
- **MalformedPolicy**: 無効なポリシードキュメント
- **ThrottlingException**: レート制限超過

## 証明書・ポリシーマネージャー

### 目的
X.509証明書とIoTポリシーの作成、管理、アタッチメントを通じてAWS IoTセキュリティを学習するための包括的なツール。このスクリプトは、デバイス認証、認可、セキュリティベストプラクティスを教えます。

### 実行方法

**基本使用法:**
```bash
python certificate_manager.py
```

**デバッグモード付き（拡張セキュリティ詳細）:**
```bash
python certificate_manager.py --debug
```

### インタラクティブメインメニュー

```
📋 利用可能な操作:
1. 新しい証明書を作成
2. 既存の証明書をリスト
3. 証明書の詳細を表示
4. IoTポリシーを作成
5. 証明書にポリシーをアタッチ
6. 外部証明書を登録
7. 証明書を非アクティブ化
8. 終了

操作を選択 (1-8):
```

### オプション1: 完全証明書ワークフロー

#### ステップ1: 新しい証明書を作成
- **API**: `CreateKeysAndCertificate`
- **学習内容**: X.509証明書生成とPKI概念
- **生成されるもの**:
  - 証明書PEM（公開証明書）
  - 秘密鍵PEM（デバイス認証用）
  - 公開鍵PEM（参照用）
  - 証明書ID（AWS内での一意識別子）

#### ステップ2: 証明書ファイル保存
- **場所**: `certificates/{thing-name}/{cert-id}.{ext}`
- **ファイル**:
  - `{cert-id}.crt` - 証明書
  - `{cert-id}.key` - 秘密鍵（セキュア！）
  - `{cert-id}.pub` - 公開鍵

#### ステップ3: 証明書をアクティブ化
- **API**: `UpdateCertificate`
- **学習内容**: 証明書ライフサイクル管理
- **ステータス**: INACTIVE → ACTIVE

### オプション2: 外部証明書登録

#### 既存証明書の登録
- **API**: `RegisterCertificate`
- **学習内容**: 既存PKIインフラストラクチャとの統合
- **要件**:
  - 有効なX.509証明書PEM
  - CA証明書チェーン（必要に応じて）
  - 適切な証明書形式

### オプション3: ポリシーアタッチワークフロー

#### ステップ1: IoTポリシー作成
- **API**: `CreatePolicy`
- **学習内容**: JSON形式のポリシードキュメント設計
- **ポリシー要素**:
  - **Version**: ポリシー言語バージョン
  - **Statement**: 権限ステートメント配列
  - **Effect**: Allow/Deny
  - **Action**: 許可されるIoT操作
  - **Resource**: 対象リソース

#### ステップ2: ポリシーを証明書にアタッチ
- **API**: `AttachPrincipalPolicy`
- **学習内容**: 証明書ベース認可
- **結果**: 証明書を使用するデバイスがポリシー権限を取得

### オプション4: ポリシーデタッチワークフロー

#### ポリシーの切り離し
- **API**: `DetachPrincipalPolicy`
- **学習内容**: 動的権限管理
- **使用例**: セキュリティインシデント対応、権限変更

### オプション5: 証明書ステータス管理

#### 証明書の非アクティブ化
- **API**: `UpdateCertificate`
- **学習内容**: セキュリティライフサイクル管理
- **ステータス**: ACTIVE → INACTIVE
- **影響**: デバイス接続の即座の無効化

### 証明書管理詳細

#### X.509証明書の構造
- **Subject**: 証明書の所有者情報
- **Issuer**: 証明書発行者（AWS IoT CA）
- **Validity**: 有効期間（開始日と終了日）
- **Public Key**: 公開鍵情報
- **Signature**: CA署名

#### 証明書ライフサイクル
1. **作成**: 新しい証明書とキーペアの生成
2. **アクティブ化**: 証明書の使用開始
3. **使用**: デバイス認証での活用
4. **ローテーション**: 定期的な証明書更新
5. **失効**: セキュリティ上の理由による無効化

### ポリシー管理詳細

#### IoTポリシーの構造
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "iot:Connect",
        "iot:Publish",
        "iot:Subscribe",
        "iot:Receive"
      ],
      "Resource": [
        "arn:aws:iot:region:account:client/${iot:Connection.Thing.ThingName}",
        "arn:aws:iot:region:account:topic/device/${iot:Connection.Thing.ThingName}/*"
      ]
    }
  ]
}
```

#### ポリシー変数
- **${iot:Connection.Thing.ThingName}**: 接続デバイスのThing名
- **${iot:ClientId}**: MQTTクライアントID
- **${iot:Certificate.Subject.CommonName}**: 証明書のCN

### API学習機能

#### セキュリティベストプラクティス
- **最小権限の原則**: 必要最小限の権限のみ付与
- **リソース固有権限**: 特定のトピック/デバイスへの制限
- **条件付きアクセス**: 時間、場所、デバイス属性による制限

#### 証明書セキュリティ
- **秘密鍵保護**: 秘密鍵の安全な保存
- **証明書ローテーション**: 定期的な証明書更新
- **失効管理**: 侵害された証明書の迅速な無効化

### 証明書オプション説明

#### AWS生成 vs 外部証明書
- **AWS生成**: 簡単、自動管理、AWS最適化
- **外部証明書**: 既存PKI統合、企業ポリシー準拠、カスタムCA

#### 証明書形式
- **PEM**: Base64エンコードされたDER、テキスト形式
- **DER**: バイナリ形式、コンパクト
- **PKCS#12**: 証明書と秘密鍵のバンドル

### エラー学習シナリオ

#### 証明書エラー
- **CertificateConflictException**: 重複証明書登録
- **CertificateStateException**: 無効な証明書ステータス
- **CertificateValidationException**: 無効な証明書形式

#### ポリシーエラー
- **MalformedPolicyException**: 無効なJSON構文
- **PolicyVersionLimitExceededException**: ポリシーバージョン制限
- **InvalidPolicyDocumentException**: 無効なポリシー構造

## MQTT通信

### 目的
MQTTプロトコルを使用したリアルタイムIoT通信を学習し、証明書ベースとWebSocketベースの両方の認証方法を体験します。

### 利用可能な2つのMQTTオプション

#### 1. 証明書ベースMQTT（推奨）
- **ファイル**: `mqtt_client_explorer.py`
- **認証**: X.509証明書
- **用途**: 本番デバイス、組み込みシステム
- **プロトコル**: MQTT over TLS

#### 2. WebSocket MQTT
- **ファイル**: `mqtt_websocket_explorer.py`
- **認証**: AWS認証情報（SigV4）
- **用途**: ウェブアプリケーション、ブラウザベースクライアント
- **プロトコル**: MQTT over WebSockets

### 証明書ベースMQTTクライアント

#### 前提条件
- 有効なX.509証明書（certificate_manager.pyで作成）
- 適切なIoTポリシーがアタッチされた証明書
- 証明書ファイルがローカルに保存されている

#### 実行方法
```bash
python mqtt_client_explorer.py
```

#### 学習フロー
1. **証明書選択**: 利用可能な証明書から選択
2. **エンドポイント取得**: IoT Data エンドポイントの取得
3. **TLS接続**: 証明書を使用した安全な接続
4. **MQTT操作**: 購読、公開、メッセージ受信

#### 利用可能な操作
```
📋 利用可能な操作:
1. トピックを購読
2. メッセージを公開
3. 接続状態を表示
4. 切断して終了
```

### WebSocket MQTTクライアント

#### 前提条件
- 有効なAWS認証情報
- IoT:* 権限を持つIAMユーザー/ロール

#### 実行方法
```bash
python mqtt_websocket_explorer.py
```

#### 学習フロー
1. **認証情報確認**: AWS認証情報の検証
2. **WebSocketエンドポイント**: IoT WebSocketエンドポイントの取得
3. **SigV4署名**: リクエスト署名の生成
4. **WebSocket接続**: 署名付きWebSocket接続
5. **MQTT操作**: 購読、公開、メッセージ受信

### MQTTプロトコル学習

#### MQTTの基本概念
- **ブローカー**: メッセージルーティングサーバー（AWS IoT Core）
- **クライアント**: メッセージを送受信するデバイス/アプリケーション
- **トピック**: メッセージのルーティングアドレス
- **QoS**: メッセージ配信品質レベル

#### トピック構造
- **階層構造**: `device/sensor/temperature`
- **ワイルドカード**: 
  - `+`: 単一レベル（`device/+/temperature`）
  - `#`: 複数レベル（`device/#`）

#### QoSレベル
- **QoS 0**: 最大1回配信（Fire and Forget）
- **QoS 1**: 最低1回配信（At Least Once）
- **QoS 2**: 正確に1回配信（Exactly Once）- AWS IoT未サポート

## AWS IoT Device Shadow service エクスプローラー

### 目的
AWS IoT Device Shadowサービスを使用したデバイス状態同期を学習し、オフラインデバイス管理とリアルタイム状態更新を体験します。

### 実行方法

**基本使用法:**
```bash
python device_shadow_explorer.py
```

**デバッグモード付き:**
```bash
python device_shadow_explorer.py --debug
```

### 前提条件
- サンプルThings（setup_sample_data.pyで作成）
- 適切なIAM権限（IoT Device Shadow操作用）

### インタラクティブDevice Shadow学習

#### Thing選択
スクリプトは利用可能なThingsを表示し、Shadow操作用に1つを選択させます:
```
📱 Thing選択
利用可能なThings:
1. Vehicle-VIN-001
2. Vehicle-VIN-002
...
Thingを選択 (1-20):
```

#### Shadow操作メニュー
```
📋 利用可能な操作:
1. Shadowを取得
2. 希望する状態を更新
3. 報告された状態を更新
4. Shadowを削除
5. 別のThingを選択
6. 終了
```

### 主要学習機能

#### 1. Shadow取得
- **API**: `GetThingShadow`
- **学習内容**: Shadow構造とメタデータの理解
- **表示内容**:
  - 希望する状態（desired）
  - 報告された状態（reported）
  - 差分（delta）
  - メタデータ（タイムスタンプ、バージョン）

#### 2. 希望する状態の更新
- **API**: `UpdateThingShadow`
- **学習内容**: デバイス設定の目標状態設定
- **JSON例**:
```json
{
  "state": {
    "desired": {
      "temperature": 22,
      "humidity": 45,
      "mode": "auto"
    }
  }
}
```

#### 3. 報告された状態の更新
- **API**: `UpdateThingShadow`
- **学習内容**: デバイスの現在状態報告
- **JSON例**:
```json
{
  "state": {
    "reported": {
      "temperature": 21,
      "humidity": 43,
      "mode": "auto"
    }
  }
}
```

#### 4. Shadow削除
- **API**: `DeleteThingShadow`
- **学習内容**: 状態リセットとクリーンアップ
- **影響**: すべての状態情報の完全削除

### シャドウメッセージ分析

#### Shadow構造
```json
{
  "state": {
    "desired": { /* アプリケーションが設定した目標状態 */ },
    "reported": { /* デバイスが報告した現在状態 */ },
    "delta": { /* desired と reported の差分 */ }
  },
  "metadata": {
    "desired": { /* desired の更新タイムスタンプ */ },
    "reported": { /* reported の更新タイムスタンプ */ }
  },
  "version": 123, /* Shadow バージョン番号 */
  "timestamp": 1609459200 /* 最終更新タイムスタンプ */
}
```

#### 状態同期フロー
1. **アプリケーション**: desired 状態を設定
2. **AWS IoT**: delta を計算（desired - reported）
3. **デバイス**: delta を受信し、変更を適用
4. **デバイス**: 新しい reported 状態を送信
5. **AWS IoT**: delta を再計算（通常は空になる）

### 学習シナリオ

#### シナリオ1: 初期デバイス設定
1. 新しいデバイスのShadowを作成
2. desired 状態で初期設定を定義
3. デバイスが delta を受信し設定を適用
4. デバイスが reported 状態で確認

#### シナリオ2: リモート設定変更
1. アプリケーションが desired 状態を更新
2. オンラインデバイスが即座に delta を受信
3. オフラインデバイスは再接続時に delta を受信
4. デバイスが変更を適用し reported を更新

#### シナリオ3: デバイス状態監視
1. デバイスが定期的に reported 状態を更新
2. アプリケーションが現在状態を監視
3. 異常値検出時にアラートを生成
4. 必要に応じて desired 状態で修正

### 必要なIAM権限

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "iot:GetThingShadow",
        "iot:UpdateThingShadow",
        "iot:DeleteThingShadow"
      ],
      "Resource": "arn:aws:iot:*:*:thing/*"
    }
  ]
}
```

## IoT Rules Engine エクスプローラー

### 目的
AWS IoT Rules Engineを使用したメッセージルーティング、フィルタリング、変換を学習し、IoTデータを他のAWSサービスに統合する方法を体験します。

### 実行方法

**基本使用法:**
```bash
python iot_rules_explorer.py
```

**デバッグモード付き:**
```bash
python iot_rules_explorer.py --debug
```

### 前提条件
- 適切なIAM権限（IoT Rules Engine操作用）
- オプション: 他のAWSサービス（AWS Lambda、Amazon DynamoDB、Amazon S3など）へのアクセス

### インタラクティブRules Engine学習

#### ルール管理メニュー
```
📋 利用可能な操作:
1. 既存のルールをリスト
2. 新しいルールを作成
3. ルールの詳細を表示
4. ルールを削除
5. 終了
```

### 主要学習機能

#### 1. ルールリスト
- **API**: `ListTopicRules`
- **学習内容**: 既存のメッセージ処理パイプラインの理解
- **表示情報**:
  - ルール名
  - 説明
  - SQL文
  - 作成日
  - アクション数

#### 2. ルール作成
- **API**: `CreateTopicRule`
- **学習内容**: SQL文とアクションの定義
- **必要情報**:
  - ルール名
  - 説明
  - SQL文（メッセージフィルタリング用）
  - アクション（処理されたメッセージの送信先）

#### 3. ルール詳細表示
- **API**: `GetTopicRule`
- **学習内容**: ルール設定の詳細分析
- **表示内容**:
  - 完全なSQL文
  - すべてのアクション設定
  - IAMロール情報
  - エラーアクション設定

#### 4. ルール削除
- **API**: `DeleteTopicRule`
- **学習内容**: ルールライフサイクル管理
- **影響**: メッセージルーティングの停止

### ルール管理機能

#### IoT SQL構文
AWS IoT Rules Engineは、標準SQLに似た構文を使用:

```sql
SELECT temperature, humidity, timestamp
FROM 'topic/+/data'
WHERE temperature > 25
```

#### SQL要素
- **SELECT**: 抽出するフィールド
- **FROM**: 監視するトピック（ワイルドカード対応）
- **WHERE**: フィルタリング条件

#### 高度なSQL機能
- **関数**: `upper()`, `lower()`, `substring()`
- **演算子**: `+`, `-`, `*`, `/`, `%`
- **条件**: `AND`, `OR`, `NOT`
- **ネストされたオブジェクト**: `payload.sensor.temperature`

### 自動IAM設定

スクリプトは、ルール実行に必要なIAMロールを自動的に作成・設定します:

#### 作成されるIAMロール
- **ロール名**: `IoTRuleExecutionRole`
- **信頼ポリシー**: IoT Rules Engineサービスを信頼
- **権限**: 指定されたアクションの実行権限

#### サポートされるアクション
- **AWS Lambda**: 関数呼び出し
- **Amazon DynamoDB**: テーブルへの書き込み
- **Amazon S3**: オブジェクトの保存
- **Amazon SNS**: 通知の送信
- **Amazon SQS**: メッセージのキューイング

### ルールのテスト

#### テスト方法
1. **MQTTクライアント**: mqtt_client_explorer.pyを使用
2. **メッセージ公開**: ルールのトピックパターンに一致するメッセージを送信
3. **結果確認**: 対象AWSサービスでの処理結果を確認

#### テスト例
```bash
# ルール作成（温度データをDynamoDBに保存）
# SQL: SELECT * FROM 'device/+/temperature' WHERE temperature > 30

# テストメッセージ公開
python mqtt_client_explorer.py
# トピック: device/sensor1/temperature
# メッセージ: {"temperature": 35, "humidity": 60, "timestamp": 1609459200}
```

### 学習シナリオ

#### シナリオ1: 温度アラート
1. 高温度検出ルールを作成
2. SNSアクションでアラート通知
3. テストメッセージで動作確認

#### シナリオ2: データアーカイブ
1. すべてのセンサーデータをS3に保存するルール
2. 日付ベースのパーティショニング
3. データ形式変換（JSON → Parquet）

#### シナリオ3: リアルタイム処理
1. Lambda関数でのリアルタイムデータ処理
2. 異常検出アルゴリズムの実行
3. 結果の別トピックへの公開

### 必要なIAM権限

#### Rules Engine操作用
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "iot:CreateTopicRule",
        "iot:GetTopicRule",
        "iot:ListTopicRules",
        "iot:DeleteTopicRule",
        "iot:ReplaceTopicRule"
      ],
      "Resource": "*"
    }
  ]
}
```

#### IAMロール管理用
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "iam:CreateRole",
        "iam:AttachRolePolicy",
        "iam:PassRole"
      ],
      "Resource": "*"
    }
  ]
}
```

---

このドキュメントは、各スクリプトの詳細な使用方法と学習目標を提供します。実際の使用時は、各スクリプトのインタラクティブガイダンスに従って進めてください。