# 使用例とワークフロー

このドキュメントは、AWS IoT Core - 基礎学習プロジェクトの詳細な例と完全なワークフローを提供します。

## 目次

- [完全学習ワークフロー](#完全学習ワークフロー)
  - [推奨学習シーケンス](#推奨学習シーケンス)
- [サンプルデータセットアップ例](#サンプルデータセットアップ例)
  - [インタラクティブ体験ウォークスルー](#インタラクティブ体験ウォークスルー)
  - [デバッグモード例](#デバッグモード例)
- [IoT Registry API エクスプローラー例](#iot-registry-api-エクスプローラー例)
  - [インタラクティブメニューナビゲーション](#インタラクティブメニューナビゲーション)
  - [List Things例](#list-things例)
  - [Describe Thing例](#describe-thing例)
- [証明書マネージャー例](#証明書マネージャー例)
  - [完全証明書ワークフロー](#完全証明書ワークフロー)
  - [外部証明書登録例](#外部証明書登録例)
- [MQTT通信例](#mqtt通信例)
  - [証明書ベースMQTTセッション](#証明書ベースmqttセッション)
  - [WebSocket MQTTセッション](#websocket-mqttセッション)
- [Device Shadow例](#device-shadow例)
  - [シャドウ状態同期](#シャドウ状態同期)
- [Rules Engine例](#rules-engine例)
  - [ルール作成ワークフロー](#ルール作成ワークフロー)
  - [ルールテスト例](#ルールテスト例)
- [クリーンアップ例](#クリーンアップ例)
  - [安全なリソースクリーンアップ](#安全なリソースクリーンアップ)
- [エラーハンドリング例](#エラーハンドリング例)
  - [一般的なエラーシナリオ](#一般的なエラーシナリオ)

## 完全学習ワークフロー

### 推奨学習シーケンス

**完全なエンドツーエンド学習パス:**

```bash
# 1. 環境セットアップ
source venv/bin/activate
export AWS_ACCESS_KEY_ID=<your-key>
export AWS_SECRET_ACCESS_KEY=<your-secret>
export AWS_DEFAULT_REGION=us-east-1

# 2. サンプルIoTリソースを作成
python setup_sample_data.py

# 3. AWS IoT Registry APIを探索
python iot_registry_explorer.py

# 4. 証明書とポリシーでセキュリティを学習
python certificate_manager.py

# 5. リアルタイムMQTT通信を体験
python mqtt_client_explorer.py
# または
python mqtt_websocket_explorer.py

# 6. シャドウを使用したデバイス状態同期を学習
python device_shadow_explorer.py

# 7. Rules Engineでメッセージルーティングをマスター
python iot_rules_explorer.py

# 8. 学習完了後にクリーンアップ
python cleanup_sample_data.py
```

**初期セットアップスクリプト以外は、学習の興味に基づいて独立して実行できます。**

## サンプルデータセットアップ例

### インタラクティブ体験ウォークスルー

**`python setup_sample_data.py`を実行すると、以下が表示されます:**

```
🚀 AWS IoT サンプルデータセットアップ
============================
このスクリプトは学習用のサンプルIoTリソースを作成します:
• 3個のThing Types（車両カテゴリ）
• 4個のThing Groups（フリートカテゴリ）  
• 20個のThings（シミュレートされた車両）

⚠️  これは実際のAWSリソースを作成し、料金が発生します。
推定コスト: Thing保存で約$0.05

続行しますか？ (y/N): y

🔄 ステップ1: Thing Typesを作成中
✅ Thing Type作成完了: SedanVehicle
✅ Thing Type作成完了: SUVVehicle  
✅ Thing Type作成完了: TruckVehicle

🔄 ステップ2: Thing Groupsを作成中
✅ Thing Group作成完了: CustomerFleet
✅ Thing Group作成完了: TestFleet
✅ Thing Group作成完了: MaintenanceFleet
✅ Thing Group作成完了: DealerFleet

🔄 ステップ3: 20個のThingsを属性付きで作成中
📱 Thing作成中: Vehicle-VIN-001
   顧客ID: 12345678-1234-1234-1234-123456789012
   国: JP
   製造日: 2023-03-15
   Thing Type: SedanVehicle
✅ Thing作成完了: Vehicle-VIN-001

📱 Thing作成中: Vehicle-VIN-002
   顧客ID: 87654321-4321-4321-4321-210987654321
   国: US
   製造日: 2023-05-22
   Thing Type: SUVVehicle
✅ Thing作成完了: Vehicle-VIN-002

... (18個のThingsが続く)

🔄 ステップ4: ThingsをThing Groupsに追加中
✅ Vehicle-VIN-001をCustomerFleetに追加
✅ Vehicle-VIN-002をTestFleetに追加
... (すべてのThingsがランダムにグループに割り当て)

📊 セットアップ概要:
Things: 20
Thing Types: 3
Thing Groups: 4

🎯 サンプルThing名:
• Vehicle-VIN-001
• Vehicle-VIN-002
• Vehicle-VIN-003
... その他17個

🎉 セットアップ完了！iot_registry_explorer.pyを使用してデータを探索できます。
```

### デバッグモード例

**`python setup_sample_data.py --debug`を実行すると、詳細なAPI情報が表示されます:**

```
🔍 デバッグモード有効
• 詳細なAPIリクエストとレスポンスを表示
• 拡張ポーズによる実行速度の低下
• 完全なエラー詳細とトレースバック

🔍 デバッグ: Thing Type作成中: SedanVehicle
📤 API呼び出し: CreateThingType
📥 入力パラメータ:
{
  "thingTypeName": "SedanVehicle",
  "thingTypeProperties": {
    "description": "Sedan vehicle type for passenger cars"
  }
}

📤 APIレスポンス:
{
  "thingTypeName": "SedanVehicle",
  "thingTypeArn": "arn:aws:iot:us-east-1:123456789012:thingtype/SedanVehicle",
  "thingTypeId": "12345678-1234-1234-1234-123456789012"
}
✅ Thing Type作成完了: SedanVehicle

Enterキーを押して続行...
```

## IoT Registry API エクスプローラー例

### インタラクティブメニューナビゲーション

**`python iot_registry_explorer.py`を実行すると:**

```
🚀 AWS IoT Registry API エクスプローラー
========================================
📍 AWS設定:
アカウントID: 123456789012
リージョン: us-east-1

詳細な説明付きのAWS IoT Registry APIのインタラクティブ探索。

📚 学習ポイント: AWS IoT Registry APIs - デバイス管理
AWS IoT Registryは、IoTデバイス（Things）、その組織（Thing Groups）、デバイステンプレート（Thing Types）、セキュリティ証明書に関する情報を格納する中央データベースです。これらのAPIにより、IoTデバイスフリート全体をプログラムで管理できます。

🔄 次: 詳細な説明付きで8つのコアRegistry APIを探索します

Enterキーを押して続行...

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

操作を選択 (1-9): 1
```

### List Things例

**オプション1を選択すると:**

```
📚 学習ポイント: List Things - デバイス発見
list_things APIは、アカウント内のすべてのIoTデバイス（Things）を取得します。これは、デバイスインベントリ管理、フリートサイズの監視、属性によるデバイス発見に不可欠です。

🔄 次: 異なるオプションでlist_things APIを呼び出します

Enterキーを押して続行...

🔄 ページネーション付きでThingsをリスト中（ページあたり最大10）...

📊 ページ1概要: 10個のThingsを取得
1. Vehicle-VIN-001 (タイプ: SedanVehicle)
2. Vehicle-VIN-002 (タイプ: SUVVehicle)
3. Vehicle-VIN-003 (タイプ: TruckVehicle)
4. Vehicle-VIN-004 (タイプ: SedanVehicle)
5. Vehicle-VIN-005 (タイプ: SUVVehicle)
6. Vehicle-VIN-006 (タイプ: TruckVehicle)
7. Vehicle-VIN-007 (タイプ: SedanVehicle)
8. Vehicle-VIN-008 (タイプ: SUVVehicle)
9. Vehicle-VIN-009 (タイプ: TruckVehicle)
10. Vehicle-VIN-010 (タイプ: SedanVehicle)

次のページに続行しますか？ (y/N): y

📊 ページ2概要: 10個のThingsを取得
11. Vehicle-VIN-011 (タイプ: SUVVehicle)
12. Vehicle-VIN-012 (タイプ: TruckVehicle)
... (残りのThings)

🏁 ページネーション完了: 2ページにわたって合計20個のThingsが見つかりました
```

### Describe Thing例

**オプション5を選択し、Thing名を入力すると:**

```
📚 学習ポイント: Describe Thing - 詳細なデバイス情報
describe_thing APIは、特定のIoTデバイスの完全な詳細を提供します。これには、属性、Thing Type、Thing Group メンバーシップ、バージョン情報が含まれます。

🔄 次: 特定のThingの詳細情報を取得します

Thing名を入力: Vehicle-VIN-001

🔍 Thing 'Vehicle-VIN-001'の詳細を取得中...

📊 Thing詳細:
名前: Vehicle-VIN-001
Thing Type: SedanVehicle
バージョン: 1
作成日: 2024-01-15T10:30:00.000Z

属性:
• customerId: 12345678-1234-1234-1234-123456789012
• country: JP
• manufacturingDate: 2023-03-15

Thing Groups:
• CustomerFleet
```

## 証明書マネージャー例

### 完全証明書ワークフロー

**`python certificate_manager.py`を実行し、オプション1を選択:**

```
🔐 AWS IoT 証明書・ポリシーマネージャー
=============================================
📍 AWS設定:
アカウントID: 123456789012
リージョン: us-east-1

X.509証明書とIoTポリシーを使用したAWS IoTセキュリティの学習。

📚 学習ポイント: IoTセキュリティ - 証明書とポリシー
AWS IoTセキュリティは、X.509証明書（デバイス認証用）とIoTポリシー（認可用）に基づいています。証明書はデバイスのアイデンティティを確立し、ポリシーは許可されるアクションを定義します。

🔄 次: 証明書とポリシーの作成、管理、セキュリティベストプラクティスを探索します

Enterキーを押して続行...

📋 利用可能な操作:
1. 新しい証明書を作成
2. 既存の証明書をリスト
3. 証明書の詳細を表示
4. IoTポリシーを作成
5. 証明書にポリシーをアタッチ
6. 外部証明書を登録
7. 証明書を非アクティブ化
8. 終了

操作を選択 (1-8): 1

📚 学習ポイント: X.509証明書作成
X.509証明書は、IoTデバイスの一意のアイデンティティを提供します。AWS IoTは、証明書、秘密鍵、公開鍵を生成し、デバイス認証に使用します。

🔄 次: 新しいX.509証明書を作成し、そのセキュリティプロパティを調査します

🔐 新しいX.509証明書を作成中...

✅ 証明書が正常に作成されました
証明書ID: 1234567890abcdef1234567890abcdef12345678
証明書ARN: arn:aws:iot:us-east-1:123456789012:cert/1234567890abcdef1234567890abcdef12345678

💾 証明書ファイルを保存中...
✅ 証明書ファイルが保存されました:
証明書ファイル: certificates/Vehicle-VIN-001/1234567890abcdef1234567890abcdef12345678.crt
秘密鍵ファイル: certificates/Vehicle-VIN-001/1234567890abcdef1234567890abcdef12345678.key
公開鍵ファイル: certificates/Vehicle-VIN-001/1234567890abcdef1234567890abcdef12345678.pub
```

### 外部証明書登録例

**オプション6を選択:**

```
📚 学習ポイント: 外部証明書登録
外部で生成された証明書をAWS IoTに登録できます。これにより、既存のPKIインフラストラクチャを活用し、企業の証明書管理ポリシーに準拠できます。

🔄 次: 外部証明書を登録し、既存のPKIとの統合を学習します

証明書PEMを入力:
-----BEGIN CERTIFICATE-----
MIIDQTCCAimgAwIBAgITBmyfz5m/jAo54vB4ikPmljZbyjANBgkqhkiG9w0BAQsF
ADA5MQswCQYDVQQGEwJVUzEPMA0GA1UEChMGQW1hem9uMRkwFwYDVQQDExBBbWF6
... (証明書内容)
-----END CERTIFICATE-----

📝 外部証明書を登録中...

✅ 証明書が正常に登録されました
証明書ID: abcdef1234567890abcdef1234567890abcdef12
証明書ARN: arn:aws:iot:us-east-1:123456789012:cert/abcdef1234567890abcdef1234567890abcdef12
```

## MQTT通信例

### 証明書ベースMQTTセッション

**`python mqtt_client_explorer.py`を実行:**

```
📡 AWS IoT MQTT クライアントエクスプローラー
=============================================
📍 AWS設定:
アカウントID: 123456789012
リージョン: us-east-1

証明書ベースの認証を使用したリアルタイムMQTT通信の学習。

📚 学習ポイント: MQTT通信 - リアルタイムメッセージング
MQTTは、IoTデバイス間のリアルタイム通信を可能にする軽量メッセージングプロトコルです。AWS IoT Coreは、X.509証明書を使用した安全なMQTT接続を提供します。

🔄 次: 証明書ベースのMQTT接続を確立し、メッセージングを探索します

🔐 証明書選択
利用可能な証明書:
1. 1234567890abcdef1234567890abcdef12345678 (ACTIVE)
2. abcdef1234567890abcdef1234567890abcdef12 (ACTIVE)

証明書を選択 (1-2): 1

✅ 選択された証明書: 1234567890abcdef1234567890abcdef12345678

🔍 証明書ファイルを確認中...
✅ 見つかりました: certificates/Vehicle-VIN-001/1234567890abcdef1234567890abcdef12345678.crt
✅ 見つかりました: certificates/Vehicle-VIN-001/1234567890abcdef1234567890abcdef12345678.key
✅ 見つかりました: certificates/Vehicle-VIN-001/1234567890abcdef1234567890abcdef12345678.pub
✅ すべての証明書ファイルが準備完了

🌐 IoTエンドポイントを取得中...
✅ エンドポイント: a1b2c3d4e5f6g7-ats.iot.us-east-1.amazonaws.com

🔌 MQTTクライアントに接続中...
✅ MQTTに接続されました！

📋 利用可能な操作:
1. トピックを購読
2. メッセージを公開
3. 接続状態を表示
4. 切断して終了

操作を選択 (1-4): 1

📚 学習ポイント: MQTTトピック購読
トピック購読により、特定のトピックに公開されたメッセージをリアルタイムで受信できます。MQTTはワイルドカード（+は単一レベル、#は複数レベル）をサポートし、複数のトピックを効率的に監視できます。

🔄 次: トピックを購読し、リアルタイムメッセージを受信します

購読するトピックを入力: device/+/temperature

📡 トピック 'device/+/temperature' を購読中...
✅ トピック 'device/+/temperature' の購読に成功しました

操作を選択 (1-4): 2

📚 学習ポイント: MQTTメッセージ公開
メッセージ公開により、特定のトピックにデータを送信し、そのトピックを購読しているすべてのクライアントに配信できます。

🔄 次: トピックにメッセージを公開し、リアルタイム配信を確認します

公開するトピックを入力: device/sensor1/temperature
メッセージを入力: {"temperature": 25.5, "humidity": 60, "timestamp": 1609459200}

📤 メッセージを公開中...
✅ メッセージが公開されました

📨 メッセージ受信
トピック: device/sensor1/temperature
メッセージ: {"temperature": 25.5, "humidity": 60, "timestamp": 1609459200}
タイムスタンプ: 2024-01-15 10:45:30
```

### WebSocket MQTTセッション

**`python mqtt_websocket_explorer.py`を実行:**

```
🌐 AWS IoT MQTT WebSocket エクスプローラー
==================================================
📍 AWS設定:
アカウントID: 123456789012
リージョン: us-east-1

WebSocket接続を使用したブラウザフレンドリーなMQTT通信の学習。

📚 学習ポイント: MQTT WebSocket - ブラウザフレンドリー通信
MQTT over WebSocketsにより、ウェブアプリケーションがAWS IoT Coreと直接通信できます。X.509証明書の代わりにAWS認証情報を使用し、ブラウザベースのIoTアプリケーションに最適です。

🔄 次: WebSocket接続を確立し、ブラウザフレンドリーなメッセージングを探索します

🌐 IoT WebSocketエンドポイントを取得中...
✅ エンドポイント: a1b2c3d4e5f6g7-ats.iot.us-east-1.amazonaws.com

🔐 AWS認証情報を作成中...
✅ 認証情報が作成されました

🔌 WebSocket MQTTクライアントに接続中...
✅ WebSocket MQTTに接続されました！

📋 利用可能な操作:
1. トピックを購読
2. メッセージを公開
3. 接続状態を表示
4. 切断して終了

操作を選択 (1-4): 3

🔌 接続状態
✅ 接続済み
WebSocketエンドポイント: a1b2c3d4e5f6g7-ats.iot.us-east-1.amazonaws.com
認証方法: AWS認証情報（WebSocket）
アクティブな購読: なし
```

## Device Shadow例

### シャドウ状態同期

**`python device_shadow_explorer.py`を実行:**

```
🌟 AWS IoT Device Shadow エクスプローラー
=============================================
📍 AWS設定:
アカウントID: 123456789012
リージョン: us-east-1

Device Shadowを使用したデバイス状態同期の学習。

📚 学習ポイント: Device Shadow - デバイス状態同期
AWS IoT Device Shadowは、デバイスの現在の状態と希望する状態を同期するサービスです。デバイスがオフラインでも状態を保持し、再接続時に同期を行います。

🔄 次: Device Shadowの操作を探索し、状態管理を学習します

📱 Thing選択
利用可能なThings:
1. Vehicle-VIN-001
2. Vehicle-VIN-002
3. Vehicle-VIN-003
... (20個のThingsをリスト)

Thingを選択 (1-20): 1

✅ 選択されたThing: Vehicle-VIN-001

📋 利用可能な操作:
1. Shadowを取得
2. 希望する状態を更新
3. 報告された状態を更新
4. Shadowを削除
5. 別のThingを選択
6. 終了

操作を選択 (1-6): 1

📚 学習ポイント: Shadow取得
Shadow取得により、デバイスの現在の状態、希望する状態、および差分（delta）を確認できます。これは、デバイスの現在の設定を理解し、同期が必要な変更を特定するために重要です。

🔄 次: Shadowドキュメントを取得し、その構造を調査します

🔍 Thing 'Vehicle-VIN-001'のShadowを取得中...
📭 Shadowが見つかりません（まだ作成されていません）

操作を選択 (1-6): 2

📚 学習ポイント: 希望する状態の更新
希望する状態の更新により、デバイスが達成すべき目標設定を定義できます。デバイスは、この希望する状態と現在の報告された状態の差分を受信し、必要な変更を適用します。

🔄 次: 希望する状態を更新し、デバイス同期を開始します

希望する状態をJSON形式で入力:
例: {"temperature": 22, "humidity": 45}
{"temperature": 22, "mode": "auto", "fanSpeed": 3}

🔄 希望する状態を更新中...
✅ 希望する状態が更新されました

操作を選択 (1-6): 1

🔍 Thing 'Vehicle-VIN-001'のShadowを取得中...
✅ Shadow取得成功

📊 Shadow構造:
状態:
  希望する状態:
    • temperature: 22
    • mode: "auto"
    • fanSpeed: 3
  
  報告された状態: なし
  
  差分（Delta）:
    • temperature: 22
    • mode: "auto"
    • fanSpeed: 3

メタデータ:
  バージョン: 1
  タイムスタンプ: 2024-01-15T10:50:00.000Z
```

## Rules Engine例

### ルール作成ワークフロー

**`python iot_rules_explorer.py`を実行:**

```
⚙️ AWS IoT Rules Engine エクスプローラー
=============================================
📍 AWS設定:
アカウントID: 123456789012
リージョン: us-east-1

IoT Rules Engineを使用したメッセージルーティングと処理の学習。

📚 学習ポイント: IoT Rules Engine - メッセージルーティング
AWS IoT Rules Engineは、IoTメッセージを他のAWSサービスにルーティングし、リアルタイムで処理するサービスです。SQLライクな構文を使用してメッセージをフィルタリング、変換し、Lambda、DynamoDB、S3などに送信できます。

🔄 次: IoTルールを作成し、メッセージルーティングを探索します

📋 利用可能な操作:
1. 既存のルールをリスト
2. 新しいルールを作成
3. ルールの詳細を表示
4. ルールを削除
5. 終了

操作を選択 (1-5): 2

📚 学習ポイント: IoTルール作成
IoTルール作成には、SQL文（メッセージフィルタリング用）とアクション（処理されたデータの送信先）の定義が含まれます。SQLを使用してトピック、ペイロード、メタデータに基づいてメッセージを選択し、変換できます。

🔄 次: 新しいIoTルールを作成し、メッセージルーティングを設定します

ルール名を入力: HighTemperatureAlert
ルールの説明を入力: Alert when temperature exceeds 30 degrees
ルールのSQL文を入力:
例: SELECT * FROM 'topic/+' WHERE temperature > 25
SELECT temperature, deviceId, timestamp FROM 'device/+/temperature' WHERE temperature > 30

⚙️ ルール 'HighTemperatureAlert'を作成中...
✅ ルールが正常に作成されました

ルール名: HighTemperatureAlert
ルールARN: arn:aws:iot:us-east-1:123456789012:rule/HighTemperatureAlert
```

### ルールテスト例

**MQTTクライアントでルールをテスト:**

```bash
# 別のターミナルでMQTTクライアントを起動
python mqtt_client_explorer.py

# 高温度メッセージを公開してルールをトリガー
トピック: device/sensor1/temperature
メッセージ: {"temperature": 35, "deviceId": "sensor1", "timestamp": 1609459200}

# ルールが実行され、設定されたアクション（SNS、Lambda等）が呼び出される
```

## クリーンアップ例

### 安全なリソースクリーンアップ

**`python cleanup_sample_data.py`を実行:**

```
🧹 AWS IoT サンプルデータクリーンアップ
========================================
📍 AWS設定:
アカウントID: 123456789012
リージョン: us-east-1

学習セッション後のサンプルIoTリソースの安全なクリーンアップ。

⚠️  重要な警告
このスクリプトは以下のサンプルリソースを削除します:
• Vehicle-VIN-* パターンのThings
• 関連する証明書とポリシー
• SedanVehicle、SUVVehicle、TruckVehicle Thing Types
• CustomerFleet、TestFleet、MaintenanceFleet、DealerFleet Thing Groups
• ローカル証明書ファイル

🛡️  安全性: 本番リソースは保護されています（サンプルパターンのみ削除）

続行しますか？ (y/N): y

🔄 ステップ1: Thingsとその証明書をクリーンアップ中
🔍 サンプルThingsをスキャン中...
📊 20個のサンプルThingsが見つかりました

🔄 Thing処理中: Vehicle-VIN-001
📋 Thing Vehicle-VIN-001の証明書: 1234567890abcdef1234567890abcdef12345678
🔗 ポリシーAllowAllを証明書1234567890abcdef1234567890abcdef12345678から切り離し中
✅ ポリシーが切り離されました
🔄 証明書1234567890abcdef1234567890abcdef12345678を非アクティブに更新中
✅ 証明書が非アクティブになりました
🗑️  証明書削除中: 1234567890abcdef1234567890abcdef12345678
✅ 証明書が削除されました
🔗 Thing Vehicle-VIN-001をすべてのグループから削除中
✅ Thingがグループから削除されました
🗑️  Thing削除中: Vehicle-VIN-001
✅ Thingが削除されました

... (19個のThingsが続く)

🔄 ステップ2: Thing Typesをクリーンアップ中
🔍 サンプルThing Typesをスキャン中...
📊 3個のサンプルThing Typesが見つかりました
🗑️  Thing Type削除中: SedanVehicle
✅ Thing Typeが削除されました
🗑️  Thing Type削除中: SUVVehicle
✅ Thing Typeが削除されました
🗑️  Thing Type削除中: TruckVehicle
✅ Thing Typeが削除されました

🔄 ステップ3: Thing Groupsをクリーンアップ中
🔍 サンプルThing Groupsをスキャン中...
📊 4個のサンプルThing Groupsが見つかりました
🗑️  Thing Group削除中: CustomerFleet
✅ Thing Groupが削除されました
🗑️  Thing Group削除中: TestFleet
✅ Thing Groupが削除されました
🗑️  Thing Group削除中: MaintenanceFleet
✅ Thing Groupが削除されました
🗑️  Thing Group削除中: DealerFleet
✅ Thing Groupが削除されました

🔄 ステップ4: ローカル証明書ファイルをクリーンアップ中
🧹 ローカル証明書ファイルをクリーンアップ中...
🗑️  証明書ディレクトリをクリーンアップ中: certificates/
✅ 証明書ディレクトリがクリーンアップされました

📊 クリーンアップ概要:
Things削除済み: 20
証明書削除済み: 20
Thing Types削除済み: 3
Thing Groups削除済み: 4
ローカルファイル削除済み: はい

🎉 クリーンアップ完了！すべてのサンプルリソースが削除されました。
```

## エラーハンドリング例

### 一般的なエラーシナリオ

#### 認証情報エラー

```bash
python setup_sample_data.py

❌ 無効なAWS認証情報
AWS認証情報をエクスポートしてください:
export AWS_ACCESS_KEY_ID=<your-access-key>
export AWS_SECRET_ACCESS_KEY=<your-secret-key>
export AWS_SESSION_TOKEN=<your-session-token>  # 一時認証情報の場合はオプション
```

#### リージョン設定エラー

```bash
python iot_registry_explorer.py

❌ AWSリージョンが設定されていません
以下のいずれかの方法でAWSリージョンを設定してください:
1. 環境変数を設定: export AWS_DEFAULT_REGION=us-east-1
2. AWS CLIを設定: aws configure
3. AWS認証情報ファイルでリージョンを設定
```

#### 権限エラー

```bash
python certificate_manager.py

❌ AWS APIエラー: AccessDeniedException
An error occurred (AccessDeniedException) when calling the CreateKeysAndCertificate operation: User: arn:aws:iam::123456789012:user/testuser is not authorized to perform: iot:CreateKeysAndCertificate on resource: *

解決策: IAMユーザーまたはロールに適切なIoT権限を付与してください。
```

#### リソース不足エラー

```bash
python device_shadow_explorer.py

❌ Thingsが見つかりません。setup_sample_data.pyを実行してサンプルデータを作成してください。

解決策:
1. python setup_sample_data.py を実行
2. サンプルThingsが作成されるまで待機
3. このスクリプトを再実行
```

#### 証明書ファイルエラー

```bash
python mqtt_client_explorer.py

❌ 証明書ファイルが不完全です。certificate_manager.pyを実行してください。

見つからないファイル:
• certificates/Vehicle-VIN-001/1234567890abcdef1234567890abcdef12345678.crt
• certificates/Vehicle-VIN-001/1234567890abcdef1234567890abcdef12345678.key

解決策:
1. python certificate_manager.py を実行
2. 新しい証明書を作成
3. 証明書ファイルが正しく保存されることを確認
```

---

これらの例は、各スクリプトの実際の使用体験を示しています。実際の出力は、AWS環境、作成されたリソース、選択したオプションによって異なる場合があります。各スクリプトのインタラクティブガイダンスに従って、最適な学習体験を得てください。