# 使用示例和工作流程

本文档为 AWS IoT Core - 基础学习项目提供详细的示例和完整的工作流程。

## 目录

- [完整学习工作流程](#完整学习工作流程)
  - [推荐学习序列](#推荐学习序列)
- [示例数据设置示例](#示例数据设置示例)
  - [交互式体验演练](#交互式体验演练)
  - [调试模式示例](#调试模式示例)
- [IoT Registry API 探索器示例](#iot-registry-api-探索器示例)
  - [交互式菜单导航](#交互式菜单导航)
  - [List Things 示例](#list-things-示例)
  - [Describe Thing 示例](#describe-thing-示例)
- [证书管理器示例](#证书管理器示例)
  - [完整证书工作流程](#完整证书工作流程)
  - [外部证书注册示例](#外部证书注册示例)
- [MQTT 通信示例](#mqtt-通信示例)
  - [基于证书的 MQTT 会话](#基于证书的-mqtt-会话)
  - [WebSocket MQTT 会话](#websocket-mqtt-会话)
- [Device Shadow 示例](#device-shadow-示例)
  - [影子状态同步](#影子状态同步)
- [Rules Engine 示例](#rules-engine-示例)
  - [规则创建工作流程](#规则创建工作流程)
  - [规则测试示例](#规则测试示例)
- [清理示例](#清理示例)
  - [安全资源清理](#安全资源清理)
- [错误处理示例](#错误处理示例)
  - [常见错误场景](#常见错误场景)

## 完整学习工作流程

### 推荐学习序列

**完整的端到端学习路径:**

```bash
# 1. 环境设置
source venv/bin/activate
export AWS_ACCESS_KEY_ID=<your-key>
export AWS_SECRET_ACCESS_KEY=<your-secret>
export AWS_DEFAULT_REGION=us-east-1

# 2. 创建示例 IoT 资源
python setup_sample_data.py

# 3. 探索 AWS IoT Registry API
python iot_registry_explorer.py

# 4. 通过证书和策略学习安全性
python certificate_manager.py

# 5. 体验实时 MQTT 通信
python mqtt_client_explorer.py
# 或
python mqtt_websocket_explorer.py

# 6. 使用影子学习设备状态同步
python device_shadow_explorer.py

# 7. 通过 Rules Engine 掌握消息路由
python iot_rules_explorer.py

# 8. 学习完成后清理
python cleanup_sample_data.py
```

**除了初始设置脚本外，其他脚本可以根据学习兴趣独立运行。**

## 示例数据设置示例

### 交互式体验演练

**运行 `python setup_sample_data.py` 时，您将看到:**

```
🚀 AWS IoT 示例数据设置
============================
此脚本将为学习创建示例 IoT 资源:
• 3个 Thing Types（车辆类别）
• 4个 Thing Groups（车队类别）  
• 20个 Things（模拟车辆）

⚠️  这将创建真实的 AWS 资源并产生费用。
预估费用: Thing 存储约 $0.05

继续吗？ (y/N): y

🔄 步骤1: 创建 Thing Types
✅ Thing Type 创建完成: SedanVehicle
✅ Thing Type 创建完成: SUVVehicle  
✅ Thing Type 创建完成: TruckVehicle

🔄 步骤2: 创建 Thing Groups
✅ Thing Group 创建完成: CustomerFleet
✅ Thing Group 创建完成: TestFleet
✅ Thing Group 创建完成: MaintenanceFleet
✅ Thing Group 创建完成: DealerFleet

🔄 步骤3: 创建 20个 Things 及属性
📱 创建 Thing: Vehicle-VIN-001
   客户 ID: 12345678-1234-1234-1234-123456789012
   国家: 美国
   制造日期: 2023-01-15
   Thing Type: SedanVehicle

📱 创建 Thing: Vehicle-VIN-002
   客户 ID: 87654321-4321-4321-4321-210987654321
   国家: 加拿大
   制造日期: 2023-02-20
   Thing Type: SUVVehicle

... [继续创建其他 18个 Things]

🔄 步骤4: 将 Things 添加到 Thing Groups
✅ 将 Vehicle-VIN-001 添加到 CustomerFleet
✅ 将 Vehicle-VIN-002 添加到 TestFleet
... [继续分配其他 Things]

📊 创建的资源:
• Things: 20
• Thing Types: 3  
• Thing Groups: 4

🎯 示例 Thing 名称:
• Vehicle-VIN-001, Vehicle-VIN-002, Vehicle-VIN-003
... 还有 17个

🎉 设置完成！您现在可以使用 iot_registry_explorer.py 来探索数据。
```

### 调试模式示例

**使用 `python setup_sample_data.py --debug` 运行时:**

```
🔍 调试模式已启用
• 将显示详细的 API 请求和响应
• 执行较慢，有延长的暂停
• 完整的错误详细信息和堆栈跟踪

🔍 调试: 创建 Thing Type: SedanVehicle
📤 API 调用: CreateThingType
📥 输入参数:
{
  "thingTypeName": "SedanVehicle",
  "thingTypeProperties": {
    "description": "乘用轿车车辆"
  }
}

📤 API 响应:
{
  "thingTypeName": "SedanVehicle",
  "thingTypeId": "12345678-1234-1234-1234-123456789012",
  "thingTypeArn": "arn:aws:iot:us-east-1:123456789012:thingtype/SedanVehicle"
}

按 Enter 继续...
```

## IoT Registry API 探索器示例

### 交互式菜单导航

**运行 `python iot_registry_explorer.py` 时:**

```
🔍 AWS IoT Registry API 探索器
============================
📍 AWS 配置:
• 账户 ID: 123456789012
• 区域: us-east-1

📋 可用操作:
1. 列出 Things
2. 列出证书
3. 列出 Thing Groups
4. 列出 Thing Types
5. 描述 Thing
6. 描述 Thing Group
7. 描述 Thing Type
8. 描述端点
9. 退出

选择操作 (1-9): 1
```

### List Things 示例

**选择选项 1 (列出 Things) 时:**

```
📋 列出 Things 选项:
1. 基本列表（显示所有 Things）
2. 分页列表（指定每页最大结果数）

选择选项 (1-2): 1

🔄 调用 AWS IoT API: ListThings

📤 API 响应:
{
  "things": [
    {
      "thingName": "Vehicle-VIN-001",
      "thingTypeName": "SedanVehicle",
      "attributes": {
        "customerId": "12345678-1234-1234-1234-123456789012",
        "country": "美国",
        "manufacturingDate": "2023-01-15"
      },
      "version": 1
    },
    {
      "thingName": "Vehicle-VIN-002", 
      "thingTypeName": "SUVVehicle",
      "attributes": {
        "customerId": "87654321-4321-4321-4321-210987654321",
        "country": "加拿大",
        "manufacturingDate": "2023-02-20"
      },
      "version": 1
    }
    ... [显示其他 18个 Things]
  ]
}

💡 学习要点:
• ListThings API 检索您账户中的所有 IoT 设备
• 每个 Thing 都有名称、可选类型和自定义属性
• 属性是键值对，用于存储设备元数据
• 版本号跟踪 Thing 配置更改

找到 20个 Things
按 Enter 继续...
```

### Describe Thing 示例

**选择选项 5 (描述 Thing) 时:**

```
🔍 可用的 Things:
1. Vehicle-VIN-001 (SedanVehicle)
2. Vehicle-VIN-002 (SUVVehicle)
3. Vehicle-VIN-003 (TruckVehicle)
... [显示所有 20个 Things]

选择要描述的 Thing (1-20): 1

🔄 调用 AWS IoT API: DescribeThing
📥 Thing 名称: Vehicle-VIN-001

📤 API 响应:
{
  "defaultClientId": "Vehicle-VIN-001",
  "thingName": "Vehicle-VIN-001",
  "thingId": "12345678-1234-1234-1234-123456789012",
  "thingArn": "arn:aws:iot:us-east-1:123456789012:thing/Vehicle-VIN-001",
  "thingTypeName": "SedanVehicle",
  "attributes": {
    "customerId": "12345678-1234-1234-1234-123456789012",
    "country": "美国",
    "manufacturingDate": "2023-01-15"
  },
  "version": 1
}

💡 学习要点:
• DescribeThing 提供特定设备的完整详细信息
• thingId 是 AWS 生成的唯一标识符
• thingArn 是 AWS 资源名称，用于策略和权限
• defaultClientId 是 MQTT 连接的默认客户端 ID
• 属性存储设备特定的元数据

按 Enter 继续...
```

## 证书管理器示例

### 完整证书工作流程

**运行 `python certificate_manager.py` 并选择选项 1:**

```
🔐 证书和策略管理选项:
1. 完整证书工作流程（创建 + 附加策略）
2. 注册外部证书
3. 将策略附加到证书
4. 从证书分离策略
5. 管理证书状态（激活/停用）
6. 退出

选择选项 (1-6): 1

🔐 完整证书工作流程
==================

🔄 步骤1: 选择 Thing 进行证书创建
可用的 Things:
1. Vehicle-VIN-001
2. Vehicle-VIN-002
3. Vehicle-VIN-003
... [显示所有 Things]

选择 Thing (1-20): 1

🔄 步骤2: 创建证书和密钥对
🔄 调用 AWS IoT API: CreateKeysAndCertificate

📤 API 响应:
{
  "certificateArn": "arn:aws:iot:us-east-1:123456789012:cert/abc123def456...",
  "certificateId": "abc123def456789012345678901234567890abcd",
  "certificatePem": "-----BEGIN CERTIFICATE-----\nMIIDQTCCAimgAwIBAgI...\n-----END CERTIFICATE-----",
  "keyPair": {
    "PublicKey": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0B...\n-----END PUBLIC KEY-----",
    "PrivateKey": "-----BEGIN...."
  }
}

✅ 证书文件已保存:
• certificates/Vehicle-VIN-001/abc123def456.crt
• certificates/Vehicle-VIN-001/abc123def456.key  
• certificates/Vehicle-VIN-001/abc123def456.pub

🔄 步骤3: 创建 IoT 策略
策略名称: Vehicle-VIN-001-Policy

策略文档:
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
      "Resource": "*"
    }
  ]
}

🔄 调用 AWS IoT API: CreatePolicy
✅ 策略创建成功

🔄 步骤4: 将策略附加到证书
🔄 调用 AWS IoT API: AttachPolicy
✅ 策略附加成功

🔄 步骤5: 激活证书
🔄 调用 AWS IoT API: UpdateCertificate
✅ 证书已激活

🎉 完整证书工作流程完成！
• 证书 ID: abc123def456789012345678901234567890abcd
• 策略名称: Vehicle-VIN-001-Policy
• 状态: 活动
• 文件位置: certificates/Vehicle-VIN-001/

💡 学习要点:
• X.509 证书用于设备认证
• 私钥必须保持安全且不共享
• IoT 策略定义设备权限
• 证书必须激活才能使用
• 策略必须附加到证书才能生效

按 Enter 继续...
```

### 外部证书注册示例

**选择选项 2 (注册外部证书):**

```
🔐 外部证书注册
================

此选项演示如何注册外部生成的证书（例如使用 OpenSSL）。

🔄 步骤1: 使用 OpenSSL 生成证书
正在运行: openssl req -x509 -newkey rsa:2048 -keyout sample.key -out sample.crt -days 365 -nodes -subj "/C=US/ST=WA/L=Seattle/O=AWS/CN=sample-device"

✅ 外部证书已生成:
• sample.crt (证书)
• sample.key (私钥)

🔄 步骤2: 读取证书内容
证书 PEM:
-----BEGIN CERTIFICATE-----
MIIDQTCCAimgAwIBAgIJAK1234567890...
-----END CERTIFICATE-----

🔄 步骤3: 在 AWS IoT 中注册证书
🔄 调用 AWS IoT API: RegisterCertificate

📤 API 响应:
{
  "certificateArn": "arn:aws:iot:us-east-1:123456789012:cert/def456abc789...",
  "certificateId": "def456abc789012345678901234567890efgh"
}

✅ 外部证书注册成功！
• 证书 ID: def456abc789012345678901234567890efgh
• 状态: 待激活

💡 学习要点:
• 外部证书必须是有效的 X.509 格式
• 注册的证书最初处于非活动状态
• 您可以使用任何 CA 或自签名证书
• 注册后，证书的管理方式与 AWS 生成的证书相同

按 Enter 继续...
```

## MQTT 通信示例

### 基于证书的 MQTT 会话

**运行 `python mqtt_client_explorer.py`:**

```
📡 MQTT 客户端探索器
==================
📍 AWS IoT 端点: a1b2c3d4e5f6g7-ats.iot.us-east-1.amazonaws.com

🔐 可用证书:
1. Vehicle-VIN-001 (证书 ID: abc123def456...)
2. Vehicle-VIN-002 (证书 ID: def456abc789...)

选择证书 (1-2): 1

📡 MQTT 客户端选项:
1. 连接并订阅主题
2. 发布消息到主题
3. 查看连接详细信息
4. 断开连接
5. 退出

选择选项 (1-5): 1

🔄 连接到 MQTT 代理...
✅ MQTT 连接成功！
• 客户端 ID: Vehicle-VIN-001
• 端点: a1b2c3d4e5f6g7-ats.iot.us-east-1.amazonaws.com:8883
• 协议: MQTT over TLS

📡 订阅主题:
输入要订阅的主题（支持通配符 + 和 #）: vehicles/+/telemetry

🔄 订阅主题: vehicles/+/telemetry
✅ 订阅成功！

🎧 监听消息... (按 Ctrl+C 停止)

[等待消息...]
```

**在另一个终端中发布消息时:**

```
📡 MQTT 客户端选项:
1. 连接并订阅主题
2. 发布消息到主题
3. 查看连接详细信息
4. 断开连接
5. 退出

选择选项 (1-5): 2

📤 发布消息到主题:
输入主题: vehicles/001/telemetry

输入消息有效负载（JSON 格式）:
{
  "temperature": 25.5,
  "humidity": 60.2,
  "speed": 65,
  "location": {
    "lat": 47.6062,
    "lon": -122.3321
  },
  "timestamp": "2023-12-01T10:30:00Z"
}

🔄 发布消息...
✅ 消息发布成功！

💡 学习要点:
• MQTT 使用发布/订阅模式
• 主题是分层的，使用 / 分隔符
• + 通配符匹配单个级别
• # 通配符匹配多个级别
• QoS 0 = 最多一次传递
• QoS 1 = 至少一次传递

按 Enter 继续...
```

**订阅终端接收消息:**

```
📨 收到消息:
• 主题: vehicles/001/telemetry
• QoS: 0
• 有效负载:
{
  "temperature": 25.5,
  "humidity": 60.2,
  "speed": 65,
  "location": {
    "lat": 47.6062,
    "lon": -122.3321
  },
  "timestamp": "2023-12-01T10:30:00Z"
}

💡 消息分析:
• 主题匹配订阅模式 vehicles/+/telemetry
• + 通配符匹配 "001"
• 有效负载是有效的 JSON
• 消息包含遥测数据（温度、湿度、速度、位置）

[继续监听消息...]
```

### WebSocket MQTT 会话

**运行 `python mqtt_websocket_explorer.py`:**

```
🌐 WebSocket MQTT 客户端探索器
============================
📍 AWS IoT 端点: a1b2c3d4e5f6g7-ats.iot.us-east-1.amazonaws.com

🔐 使用 AWS 凭证进行认证:
• 访问密钥 ID: AKIA...
• 区域: us-east-1

📡 WebSocket MQTT 客户端选项:
1. 连接并订阅主题
2. 发布消息到主题
3. 查看连接详细信息
4. 断开连接
5. 退出

选择选项 (1-5): 1

🔄 建立 WebSocket 连接...
🔄 执行 AWS SigV4 签名...
✅ WebSocket MQTT 连接成功！
• 协议: MQTT over WebSocket
• 认证: AWS SigV4
• 端点: wss://a1b2c3d4e5f6g7-ats.iot.us-east-1.amazonaws.com/mqtt

📡 订阅主题:
输入要订阅的主题: $aws/events/presence/+

🔄 订阅主题: $aws/events/presence/+
✅ 订阅成功！

🎧 监听连接事件... (按 Ctrl+C 停止)

💡 学习要点:
• WebSocket MQTT 使用 AWS 凭证而不是证书
• 适用于 Web 应用程序和浏览器
• 使用 AWS SigV4 签名进行认证
• 支持所有标准 MQTT 功能
• $aws/events 主题提供系统事件

[等待事件...]
```

## Device Shadow 示例

### 影子状态同步

**运行 `python device_shadow_explorer.py`:**

```
🌟 Device Shadow 探索器
=====================

🔍 可用的 Things:
1. Vehicle-VIN-001
2. Vehicle-VIN-002
3. Vehicle-VIN-003

选择 Thing (1-3): 1

🌟 Device Shadow 选项:
1. 获取设备影子
2. 更新设备影子
3. 删除设备影子
4. 查看影子历史
5. 模拟设备更新
6. 退出

选择选项 (1-6): 2

📝 更新设备影子
==============

当前影子状态:
{
  "state": {},
  "metadata": {},
  "version": 1,
  "timestamp": 1701432000
}

输入期望状态（JSON 格式）:
{
  "temperature": 22,
  "humidity": 45,
  "engineStatus": "running",
  "fuelLevel": 75
}

🔄 更新设备影子...
🔄 调用 AWS IoT API: UpdateThingShadow

📤 API 响应:
{
  "state": {
    "desired": {
      "temperature": 22,
      "humidity": 45,
      "engineStatus": "running",
      "fuelLevel": 75
    }
  },
  "metadata": {
    "desired": {
      "temperature": {
        "timestamp": 1701432060
      },
      "humidity": {
        "timestamp": 1701432060
      },
      "engineStatus": {
        "timestamp": 1701432060
      },
      "fuelLevel": {
        "timestamp": 1701432060
      }
    }
  },
  "version": 2,
  "timestamp": 1701432060
}

✅ 影子更新成功！

💡 学习要点:
• 期望状态表示设备应该达到的状态
• 元数据包含每个属性的时间戳
• 版本号在每次更新时递增
• 设备将接收增量消息以同步状态

按 Enter 继续...
```

**选择选项 5 (模拟设备更新):**

```
🤖 模拟设备更新
==============

模拟设备报告其当前状态...

输入报告状态（JSON 格式）:
{
  "temperature": 21,
  "humidity": 47,
  "engineStatus": "running",
  "fuelLevel": 73
}

🔄 设备报告状态...
🔄 调用 AWS IoT API: UpdateThingShadow

📤 更新后的影子:
{
  "state": {
    "desired": {
      "temperature": 22,
      "humidity": 45,
      "engineStatus": "running",
      "fuelLevel": 75
    },
    "reported": {
      "temperature": 21,
      "humidity": 47,
      "engineStatus": "running",
      "fuelLevel": 73
    },
    "delta": {
      "temperature": 22,
      "humidity": 45,
      "fuelLevel": 75
    }
  },
  "metadata": {
    "desired": {
      "temperature": {"timestamp": 1701432060},
      "humidity": {"timestamp": 1701432060},
      "engineStatus": {"timestamp": 1701432060},
      "fuelLevel": {"timestamp": 1701432060}
    },
    "reported": {
      "temperature": {"timestamp": 1701432120},
      "humidity": {"timestamp": 1701432120},
      "engineStatus": {"timestamp": 1701432120},
      "fuelLevel": {"timestamp": 1701432120}
    }
  },
  "version": 3,
  "timestamp": 1701432120
}

💡 学习要点:
• 报告状态表示设备的当前实际状态
• 增量显示期望状态和报告状态之间的差异
• engineStatus 没有增量，因为期望值和报告值匹配
• 设备应该处理增量以达到期望状态

按 Enter 继续...
```

## Rules Engine 示例

### 规则创建工作流程

**运行 `python iot_rules_explorer.py`:**

```
⚙️ IoT Rules Engine 探索器
========================

⚙️ IoT Rules Engine 选项:
1. 创建新规则
2. 列出现有规则
3. 查看规则详细信息
4. 测试规则 SQL
5. 删除规则
6. 退出

选择选项 (1-6): 1

📝 创建新规则
============

输入规则名称: HighTemperatureAlert

输入规则描述: 检测高温读数并发送警报

📝 SQL 语句配置:
输入 SQL 语句（例如: SELECT * FROM 'topic/+' WHERE temperature > 25）:
SELECT *, topic(2) as deviceId FROM 'vehicles/+/telemetry' WHERE temperature > 30

🔄 验证 SQL 语句...
✅ SQL 语句有效！

⚙️ 规则操作配置:
可用操作:
1. CloudWatch 日志
2. SNS 通知
3. SQS 队列
4. Lambda 函数

选择操作 (1-4): 1

📝 CloudWatch 日志配置:
日志组名称: /aws/iot/rules/HighTemperatureAlert
IAM 角色: iot-rules-role

🔄 创建 IAM 角色...
🔄 调用 AWS IAM API: CreateRole

IAM 角色文档:
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "iot.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}

✅ IAM 角色创建成功！

🔄 附加策略到角色...
✅ 策略附加成功！

🔄 创建 IoT 规则...
🔄 调用 AWS IoT API: CreateTopicRule

规则配置:
{
  "ruleName": "HighTemperatureAlert",
  "topicRulePayload": {
    "sql": "SELECT *, topic(2) as deviceId FROM 'vehicles/+/telemetry' WHERE temperature > 30",
    "description": "检测高温读数并发送警报",
    "actions": [
      {
        "cloudwatchLogs": {
          "logGroupName": "/aws/iot/rules/HighTemperatureAlert",
          "roleArn": "arn:aws:iam::123456789012:role/iot-rules-role"
        }
      }
    ],
    "ruleDisabled": false
  }
}

✅ 规则创建成功！

💡 学习要点:
• IoT 规则使用类似 SQL 的语法过滤消息
• topic() 函数提取主题的特定部分
• WHERE 子句过滤满足条件的消息
• 操作定义如何处理匹配的消息
• IAM 角色授予规则执行操作的权限

按 Enter 继续...
```

### 规则测试示例

**选择选项 4 (测试规则 SQL):**

```
🧪 测试规则 SQL
==============

输入要测试的 SQL 语句:
SELECT *, topic(2) as deviceId FROM 'vehicles/+/telemetry' WHERE temperature > 30

📝 测试消息配置:
输入测试主题: vehicles/001/telemetry

输入测试消息（JSON 格式）:
{
  "temperature": 35.5,
  "humidity": 65.2,
  "speed": 70,
  "location": {
    "lat": 47.6062,
    "lon": -122.3321
  },
  "timestamp": "2023-12-01T10:30:00Z"
}

🔄 执行 SQL 测试...

✅ SQL 匹配成功！

📤 SQL 输出:
{
  "temperature": 35.5,
  "humidity": 65.2,
  "speed": 70,
  "location": {
    "lat": 47.6062,
    "lon": -122.3321
  },
  "timestamp": "2023-12-01T10:30:00Z",
  "deviceId": "001"
}

💡 分析:
• 消息匹配主题模式 'vehicles/+/telemetry'
• WHERE 条件满足 (temperature 35.5 > 30)
• topic(2) 函数提取 "001" 作为 deviceId
• 所有原始字段都包含在输出中

🧪 测试不匹配的消息:
输入测试消息（温度较低）:
{
  "temperature": 25.0,
  "humidity": 55.0,
  "speed": 60
}

🔄 执行 SQL 测试...

❌ SQL 不匹配
原因: WHERE 条件不满足 (temperature 25.0 <= 30)

💡 学习要点:
• SQL 测试帮助验证规则逻辑
• 可以测试匹配和不匹配的场景
• topic() 函数从主题路径提取值
• WHERE 子句必须评估为 true 才能匹配

按 Enter 继续...
```

## 清理示例

### 安全资源清理

**运行 `python cleanup_sample_data.py`:**

```
🧹 AWS IoT 示例数据清理
=====================

⚠️  这将删除所有示例学习资源。
此操作无法撤销！

将要删除的资源:
• 所有示例 Things (Vehicle-VIN-*)
• 关联的证书和策略
• Thing Types 和 Thing Groups
• 本地证书文件
• 任何创建的 IoT 规则

确认删除所有示例资源？ (yes/no): yes

🔄 步骤1: 清理 Things 和证书
🔍 查找示例 Things...
找到 20个示例 Things

🔄 处理 Vehicle-VIN-001...
🔍 查找附加的证书...
找到证书: abc123def456789012345678901234567890abcd

🔄 分离策略: Vehicle-VIN-001-Policy
✅ 策略分离成功

🔄 停用证书...
✅ 证书停用成功

🔄 删除证书...
✅ 证书删除成功

🔄 删除策略: Vehicle-VIN-001-Policy
✅ 策略删除成功

🔄 删除 Thing: Vehicle-VIN-001
✅ Thing 删除成功

🗂️ 删除本地证书文件...
✅ 删除: certificates/Vehicle-VIN-001/

... [对所有 20个 Things 重复此过程]

🔄 步骤2: 清理 Thing Groups
🔄 删除 Thing Group: CustomerFleet
✅ Thing Group 删除成功

🔄 删除 Thing Group: TestFleet
✅ Thing Group 删除成功

🔄 删除 Thing Group: MaintenanceFleet
✅ Thing Group 删除成功

🔄 删除 Thing Group: DealerFleet
✅ Thing Group 删除成功

🔄 步骤3: 清理 Thing Types
🔄 弃用 Thing Type: SedanVehicle
✅ Thing Type 弃用成功

🔄 删除 Thing Type: SedanVehicle
✅ Thing Type 删除成功

🔄 弃用 Thing Type: SUVVehicle
✅ Thing Type 弃用成功

🔄 删除 Thing Type: SUVVehicle
✅ Thing Type 删除成功

🔄 弃用 Thing Type: TruckVehicle
✅ Thing Type 弃用成功

🔄 删除 Thing Type: TruckVehicle
✅ Thing Type 删除成功

🔄 步骤4: 清理本地文件
🗂️ 删除证书目录...
✅ 删除: certificates/

📊 清理摘要:
✅ Things 删除: 20
✅ 证书删除: 20
✅ 策略删除: 20
✅ Thing Groups 删除: 4
✅ Thing Types 删除: 3
✅ 本地文件清理: 完成

🎉 清理完成！所有示例资源已删除。
💰 这应该停止所有相关的 AWS 费用。

💡 学习要点:
• 资源删除有依赖关系顺序
• 证书必须先停用再删除
• 策略必须先分离再删除
• Thing Types 必须先弃用再删除
• 本地文件也需要清理

按 Enter 继续...
```

## 错误处理示例

### 常见错误场景

#### 凭证错误示例

```
❌ AWS API 错误: NoCredentialsError
详细信息: Unable to locate credentials

💡 故障排除步骤:
1. 检查环境变量:
   export AWS_ACCESS_KEY_ID=<your-key>
   export AWS_SECRET_ACCESS_KEY=<your-secret>
   export AWS_DEFAULT_REGION=us-east-1

2. 或配置 AWS CLI:
   aws configure

3. 验证凭证:
   aws sts get-caller-identity

按 Enter 继续...
```

#### 权限错误示例

```
❌ AWS API 错误: AccessDeniedException
详细信息: User: arn:aws:iam::123456789012:user/testuser is not authorized to perform: iot:CreateThing

💡 故障排除步骤:
1. 检查 IAM 权限
2. 确保用户有 IoT 权限:
   {
     "Effect": "Allow",
     "Action": "iot:*",
     "Resource": "*"
   }

3. 联系您的 AWS 管理员

按 Enter 继续...
```

#### 网络错误示例

```
❌ 连接错误: EndpointConnectionError
详细信息: Could not connect to the endpoint URL

💡 故障排除步骤:
1. 检查网络连接
2. 验证区域设置: echo $AWS_DEFAULT_REGION
3. 检查防火墙设置
4. 测试连接: ping iot.us-east-1.amazonaws.com

按 Enter 继续...
```

#### MQTT 连接错误示例

```
❌ MQTT 连接失败: 错误代码 5 (未授权)

💡 故障排除步骤:
1. 检查证书是否处于活动状态
2. 验证策略是否附加到证书
3. 检查策略权限:
   {
     "Effect": "Allow",
     "Action": [
       "iot:Connect",
       "iot:Publish",
       "iot:Subscribe",
       "iot:Receive"
     ],
     "Resource": "*"
   }

4. 使用调试模式获取更多详细信息:
   python mqtt_client_explorer.py --debug

按 Enter 继续...
```

---

## 总结

这些示例演示了 AWS IoT Core 基础学习项目的完整功能。每个脚本都提供：

- **交互式学习体验**
- **详细的 API 响应**
- **教育性解释**
- **实际用例场景**
- **错误处理和故障排除**

### 关键学习成果

完成这些示例后，您将掌握：

1. **设备管理**: 创建和管理 IoT Things、Types 和 Groups
2. **安全性**: X.509 证书和 IoT 策略管理
3. **通信**: MQTT 发布/订阅模式
4. **状态同步**: Device Shadow 操作
5. **消息处理**: Rules Engine 和 SQL 过滤
6. **最佳实践**: 资源生命周期管理

### 后续步骤

- 探索高级 IoT 功能（Jobs、Fleet Provisioning）
- 与其他 AWS 服务集成（Lambda、DynamoDB、SNS）
- 构建端到端 IoT 解决方案
- 实施生产就绪的安全实践
- 优化成本和性能