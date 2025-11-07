# 详细脚本文档

本文档为 AWS IoT Core - 基础项目的所有学习脚本提供全面的文档。

## 目录

- [IoT Registry API 探索器](#iot-registry-api-探索器)
  - [目的](#目的)
  - [运行方法](#运行方法)
  - [交互式菜单系统](#交互式菜单系统)
  - [支持的 API 及学习详情](#支持的-api-及学习详情)
  - [学习功能](#学习功能)
  - [错误学习](#错误学习)
- [证书和策略管理器](#证书和策略管理器)
  - [目的](#目的-1)
  - [运行方法](#运行方法-1)
  - [交互式主菜单](#交互式主菜单)
  - [选项1: 完整证书工作流程](#选项1-完整证书工作流程)
  - [选项2: 外部证书注册](#选项2-外部证书注册)
  - [选项3: 策略附加工作流程](#选项3-策略附加工作流程)
  - [选项4: 策略分离工作流程](#选项4-策略分离工作流程)
  - [选项5: 证书状态管理](#选项5-证书状态管理)
  - [证书管理详情](#证书管理详情)
  - [策略管理详情](#策略管理详情)
  - [API 学习功能](#api-学习功能)
  - [证书选项说明](#证书选项说明)
  - [错误学习场景](#错误学习场景)
- [MQTT 通信](#mqtt-通信)
  - [目的](#目的-2)
  - [可用的两个 MQTT 选项](#可用的两个-mqtt-选项)
  - [基于证书的 MQTT 客户端](#基于证书的-mqtt-客户端)
  - [WebSocket MQTT 客户端](#websocket-mqtt-客户端)
  - [MQTT 协议学习](#mqtt-协议学习)
- [AWS IoT Device Shadow service 探索器](#device-shadow-探索器)
  - [目的](#目的-3)
  - [运行方法](#运行方法-2)
  - [先决条件](#先决条件)
  - [交互式 AWS IoT Device Shadow service 学习](#交互式-device-shadow-学习)
  - [主要学习功能](#主要学习功能)
  - [影子消息分析](#影子消息分析)
  - [学习场景](#学习场景)
  - [所需的 AWS IAM 权限](#所需的-iam-权限)
- [IoT Rules Engine 探索器](#iot-rules-engine-探索器)
  - [目的](#目的-4)
  - [运行方法](#运行方法-3)
  - [先决条件](#先决条件-1)
  - [交互式 Rules Engine 学习](#交互式-rules-engine-学习)
  - [主要学习功能](#主要学习功能-1)
  - [规则管理功能](#规则管理功能)
  - [自动 AWS IAM 设置](#自动-iam-设置)
  - [规则测试](#规则测试)
  - [学习场景](#学习场景-1)
  - [所需的 AWS IAM 权限](#所需的-iam-权限-1)

## IoT Registry API 探索器

### 目的
通过详细说明的实际 API 调用学习 AWS IoT Registry API 的交互式工具。此脚本教授用于管理 IoT 设备、证书和策略的控制平面操作。

**注意**: AWS IoT Core 提供了许多跨设备管理和安全的 API。此探索器专注于理解 IoT 设备生命周期管理所必需的 8 个核心 Registry API。有关完整的 API 详细信息，请参阅 [AWS IoT Registry API 参考](https://docs.aws.amazon.com/iot/latest/apireference/API_Operations_AWS_IoT.html)。

### 运行方法

**基本用法:**
```bash
python iot_registry_explorer.py
```

**带调试模式（增强的 API 详细信息）:**
```bash
python iot_registry_explorer.py --debug
```

### 交互式菜单系统

运行脚本时，您将看到：
```
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

选择操作 (1-9):
```

### 支持的 API 及学习详情

#### 1. List Things
- **目的**: 检索您账户中的所有 IoT 设备
- **HTTP**: `GET /things`
- **学习内容**: 使用分页和过滤选项进行设备发现
- **可用选项**:
  - **基本列表**: 显示所有 Things
  - **分页**: 以较小批次检索 Things（指定每页最大结果数）

#### 2. List Certificates
- **目的**: 检索您账户中的所有 X.509 证书
- **HTTP**: `GET /certificates`
- **学习内容**: 证书发现和状态管理
- **可用选项**:
  - **基本列表**: 显示所有证书
  - **按状态过滤**: 仅显示活动、非活动或已撤销的证书
  - **分页**: 控制返回的结果数量

#### 3. List Thing Groups
- **目的**: 检索您账户中的所有 Thing Groups
- **HTTP**: `GET /thing-groups`
- **学习内容**: 设备组织和层次结构管理
- **可用选项**:
  - **基本列表**: 显示所有 Thing Groups
  - **递归列表**: 显示具有层次结构的 Thing Groups
  - **分页**: 控制返回的结果数量

#### 4. List Thing Types
- **目的**: 检索您账户中的所有 Thing Types
- **HTTP**: `GET /thing-types`
- **学习内容**: 设备类型定义和模板
- **可用选项**:
  - **基本列表**: 显示所有 Thing Types
  - **分页**: 控制返回的结果数量

#### 5. Describe Thing
- **目的**: 获取特定 Thing 的详细信息
- **HTTP**: `GET /things/{thingName}`
- **学习内容**: 设备属性、类型关联和组成员身份
- **交互式功能**:
  - 从可用 Things 列表中选择
  - 查看完整的设备配置
  - 了解属性结构

#### 6. Describe Thing Group
- **目的**: 获取特定 Thing Group 的详细信息
- **HTTP**: `GET /thing-groups/{thingGroupName}`
- **学习内容**: 组属性、策略和层次结构
- **交互式功能**:
  - 从可用 Thing Groups 列表中选择
  - 查看组配置和属性
  - 了解组层次结构

#### 7. Describe Thing Type
- **目的**: 获取特定 Thing Type 的详细信息
- **HTTP**: `GET /thing-types/{thingTypeName}`
- **学习内容**: 类型定义、属性和描述
- **交互式功能**:
  - 从可用 Thing Types 列表中选择
  - 查看类型配置
  - 了解设备模板

#### 8. Describe Endpoint
- **目的**: 获取您账户的 AWS IoT 端点信息
- **HTTP**: `GET /endpoint`
- **学习内容**: 连接端点和协议支持
- **端点类型**:
  - **iot:Data-ATS**: 用于设备通信的数据端点
  - **iot:CredentialProvider**: 用于凭证提供程序的端点
  - **iot:Jobs**: 用于 AWS IoT Jobs service 的端点

### 学习功能

#### API 请求/响应详细信息
每个 API 调用都显示：
- **HTTP 方法和端点**
- **请求参数**（如果适用）
- **完整的 JSON 响应**
- **响应字段的解释**

#### 调试模式增强功能
使用 `--debug` 标志时：
- **详细的 API 日志记录**: 查看完整的请求/响应周期
- **错误详细信息**: 增强的错误消息和故障排除提示
- **性能指标**: API 调用时间和响应大小

#### 教育内容
- **学习时刻**: 每个 API 调用后的上下文解释
- **最佳实践**: 有效使用每个 API 的建议
- **用例示例**: 何时以及为什么使用每个操作

### 错误学习

脚本故意包含错误学习场景：
- **无效参数**: 了解 API 验证
- **权限错误**: 了解 AWS IAM 要求
- **资源未找到**: 了解错误处理
- **限制错误**: 了解 API 限制

## 证书和策略管理器

### 目的
通过证书和策略管理学习 AWS IoT 安全的综合工具。此脚本教授 X.509 证书生命周期、策略附加和 IoT 安全最佳实践。

### 运行方法

**基本用法:**
```bash
python certificate_manager.py
```

**带调试模式:**
```bash
python certificate_manager.py --debug
```

### 交互式主菜单

```
🔐 证书和策略管理选项:
1. 完整证书工作流程（创建 + 附加策略）
2. 注册外部证书
3. 将策略附加到证书
4. 从证书分离策略
5. 管理证书状态（激活/停用）
6. 退出

选择选项 (1-6):
```

### 选项1: 完整证书工作流程

**目的**: 演示完整的证书创建和策略附加过程

**步骤**:
1. **证书创建**: 生成新的 X.509 证书和密钥对
2. **本地存储**: 将证书文件保存到 `certificates/` 目录
3. **策略创建**: 创建基本的 IoT 策略
4. **策略附加**: 将策略附加到证书
5. **激活**: 激活证书以供使用

**学习内容**:
- 证书生成过程
- 策略文档结构
- 证书-策略关系
- 安全最佳实践

### 选项2: 外部证书注册

**目的**: 学习如何注册外部生成的证书

**步骤**:
1. **OpenSSL 证书生成**: 使用 OpenSSL 创建证书
2. **证书验证**: 验证证书格式和有效性
3. **AWS 注册**: 将证书注册到 AWS IoT
4. **状态管理**: 激活注册的证书

**学习内容**:
- 外部证书要求
- 证书验证过程
- 注册与创建的区别
- 证书格式标准

### 选项3: 策略附加工作流程

**目的**: 学习如何将策略附加到现有证书

**步骤**:
1. **证书选择**: 从可用证书中选择
2. **策略选择**: 选择要附加的策略
3. **附加操作**: 执行策略附加
4. **验证**: 确认附加成功

**学习内容**:
- 策略附加机制
- 多策略支持
- 权限累积
- 附加验证

### 选项4: 策略分离工作流程

**目的**: 学习如何从证书分离策略

**步骤**:
1. **证书选择**: 选择具有附加策略的证书
2. **策略选择**: 选择要分离的策略
3. **分离操作**: 执行策略分离
4. **验证**: 确认分离成功

**学习内容**:
- 策略分离过程
- 权限撤销
- 安全影响
- 分离验证

### 选项5: 证书状态管理

**目的**: 学习证书生命周期管理

**可用操作**:
- **激活证书**: 启用证书以供设备使用
- **停用证书**: 暂时禁用证书
- **撤销证书**: 永久撤销证书

**学习内容**:
- 证书状态转换
- 安全影响
- 最佳实践
- 撤销与停用的区别

### 证书管理详情

#### 本地证书存储
证书存储在结构化目录中：
```
certificates/
├── Vehicle-VIN-001/
│   ├── abc123.crt    # 证书 PEM
│   ├── abc123.key    # 私钥（安全！）
│   └── abc123.pub    # 公钥（参考）
└── Vehicle-VIN-002/
    └── ...
```

#### 证书文件格式
- **`.crt`**: PEM 格式的 X.509 证书
- **`.key`**: PEM 格式的私钥（保持安全！）
- **`.pub`**: PEM 格式的公钥（参考）

### 策略管理详情

#### 基本 IoT 策略结构
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
      "Resource": "*"
    }
  ]
}
```

#### 策略最佳实践
- **最小权限原则**: 仅授予必要的权限
- **资源特定性**: 使用特定的资源 ARN
- **定期审查**: 定期审查和更新策略

### API 学习功能

#### 涵盖的 API 操作
- `CreateKeysAndCertificate`: 生成新证书
- `RegisterCertificate`: 注册外部证书
- `AttachPolicy`: 将策略附加到证书
- `DetachPolicy`: 从证书分离策略
- `UpdateCertificate`: 更新证书状态
- `CreatePolicy`: 创建新的 IoT 策略

#### 调试模式功能
- **完整的 API 请求/响应**: 查看所有 API 交互
- **证书详细信息**: 查看证书内容和元数据
- **策略文档**: 查看完整的策略 JSON
- **错误详细信息**: 详细的错误消息和故障排除

### 证书选项说明

#### 证书创建选项
1. **AWS 生成**: AWS IoT 生成证书和密钥对
2. **外部生成**: 使用 OpenSSL 或其他工具生成

#### 证书状态
- **ACTIVE**: 证书可用于设备连接
- **INACTIVE**: 证书暂时禁用
- **REVOKED**: 证书永久撤销

### 错误学习场景

脚本包含教育性错误场景：
- **无效证书格式**: 学习证书验证
- **策略语法错误**: 学习策略结构
- **权限错误**: 学习 AWS IAM 要求
- **证书状态冲突**: 学习状态管理

## MQTT 通信

### 目的
使用 MQTT 协议体验实时 IoT 通信。这些脚本教授 MQTT 概念、主题结构和消息模式，通过实际的发布/订阅交互。

### 可用的两个 MQTT 选项

#### 1. 基于证书的 MQTT 客户端（推荐）
- **文件**: `mqtt_client_explorer.py`
- **认证**: X.509 证书
- **用例**: 生产类似的设备通信
- **安全性**: 高（相互 TLS）

#### 2. WebSocket MQTT 客户端
- **文件**: `mqtt_websocket_explorer.py`
- **认证**: AWS 凭证（SigV4）
- **用例**: Web 应用程序集成
- **安全性**: 高（AWS IAM）

### 基于证书的 MQTT 客户端

#### 运行方法
```bash
python mqtt_client_explorer.py
```

#### 先决条件
- 活动的 X.509 证书（来自 certificate_manager.py）
- 附加的 IoT 策略，具有 MQTT 权限
- 证书文件在 `certificates/` 目录中

#### 交互式 MQTT 学习

**主菜单**:
```
📡 MQTT 客户端选项:
1. 连接并订阅主题
2. 发布消息到主题
3. 查看连接详细信息
4. 断开连接
5. 退出

选择选项 (1-5):
```

#### 主要学习功能

##### 1. 主题订阅
- **交互式主题输入**: 输入自定义主题模式
- **通配符支持**: 学习 `+` 和 `#` 通配符
- **实时消息**: 查看传入的消息
- **消息分析**: 了解消息结构

##### 2. 消息发布
- **主题选择**: 发布到特定主题
- **自定义有效负载**: 创建 JSON 或文本消息
- **QoS 级别**: 学习服务质量选项
- **发布确认**: 确认消息传递

##### 3. 连接管理
- **连接状态**: 监控连接健康状况
- **重连逻辑**: 学习连接恢复
- **错误处理**: 了解连接问题

#### MQTT 概念学习

##### 主题结构
- **层次结构**: 使用 `/` 分隔符的主题层次
- **通配符**: `+` 用于单级，`#` 用于多级
- **最佳实践**: 主题命名约定

##### QoS 级别
- **QoS 0**: 最多一次传递
- **QoS 1**: 至少一次传递
- **QoS 2**: 恰好一次传递（AWS IoT 不支持）

##### 保留消息
- **保留标志**: 消息持久性
- **最后已知值**: 新订阅者接收最后的消息
- **用例**: 状态更新和配置

### WebSocket MQTT 客户端

#### 运行方法
```bash
python mqtt_websocket_explorer.py
```

#### 先决条件
- 配置的 AWS 凭证
- 具有 IoT 权限的 AWS IAM 策略
- 网络访问 AWS IoT 端点

#### WebSocket 特定功能

##### 认证
- **AWS SigV4**: 使用 AWS 凭证进行签名
- **临时凭证**: 支持 STS 令牌
- **AWS IAM 策略**: 基于策略的访问控制

##### Web 集成
- **浏览器兼容**: 可在 Web 应用程序中使用
- **CORS 支持**: 跨源资源共享
- **JavaScript 友好**: 易于 Web 集成

### MQTT 协议学习

#### 协议功能
- **轻量级**: 为受限设备设计
- **发布/订阅**: 解耦的消息传递模式
- **持久连接**: 长期连接以实现实时通信
- **遗嘱消息**: 意外断开连接处理

#### AWS IoT MQTT 扩展
- **设备影子**: 设备状态同步
- **作业**: 设备管理和更新
- **规则引擎**: 消息路由和处理
- **生命周期事件**: 连接状态通知

## AWS IoT Device Shadow service 探索器

### 目的
使用 AWS IoT Device Shadow 学习设备状态同步。此脚本教授影子概念、状态管理和设备-云同步模式。

### 运行方法

**基本用法:**
```bash
python device_shadow_explorer.py
```

**带调试模式:**
```bash
python device_shadow_explorer.py --debug
```

### 先决条件
- 现有的 IoT Things（来自 setup_sample_data.py）
- 配置的 AWS 凭证
- 具有 AWS IoT Device Shadow service 权限的 AWS IAM 策略

### 交互式 AWS IoT Device Shadow service 学习

**主菜单**:
```
🌟 AWS IoT Device Shadow service 选项:
1. 获取设备影子
2. 更新设备影子
3. 删除设备影子
4. 查看影子历史
5. 模拟设备更新
6. 退出

选择选项 (1-6):
```

### 主要学习功能

#### 1. 影子检索
- **获取当前状态**: 检索设备的当前影子
- **状态分析**: 了解影子文档结构
- **版本控制**: 学习影子版本管理
- **元数据**: 查看时间戳和版本信息

#### 2. 影子更新
- **期望状态**: 设置设备的期望状态
- **增量更新**: 仅更新特定属性
- **版本冲突**: 学习并发更新处理
- **更新确认**: 确认更新成功

#### 3. 影子删除
- **完整删除**: 删除整个影子文档
- **安全确认**: 防止意外删除
- **清理**: 重置设备状态

#### 4. 历史跟踪
- **状态变化**: 跟踪影子更新历史
- **时间线**: 查看状态变化时间线
- **差异分析**: 比较状态变化

#### 5. 设备模拟
- **报告状态**: 模拟设备报告其当前状态
- **状态同步**: 演示期望与报告状态的同步
- **增量处理**: 学习增量消息处理

### 影子消息分析

#### 影子文档结构
```json
{
  "state": {
    "desired": {
      "temperature": 22,
      "humidity": 60
    },
    "reported": {
      "temperature": 20,
      "humidity": 55
    },
    "delta": {
      "temperature": 22
    }
  },
  "metadata": {
    "desired": {
      "temperature": {
        "timestamp": 1609459200
      }
    }
  },
  "version": 1,
  "timestamp": 1609459200
}
```

#### 状态类型
- **Desired**: 设备的期望状态（云到设备）
- **Reported**: 设备的当前状态（设备到云）
- **Delta**: 期望和报告状态之间的差异

#### 元数据
- **时间戳**: 每个属性的最后更新时间
- **版本**: 影子文档版本号
- **客户端令牌**: 更新跟踪标识符

### 学习场景

#### 场景1: 温度控制
- **期望温度**: 云设置目标温度
- **当前温度**: 设备报告实际温度
- **增量**: 需要调整的差异

#### 场景2: 设备配置
- **配置更新**: 云推送新配置
- **配置应用**: 设备应用配置
- **状态确认**: 设备确认配置应用

#### 场景3: 固件更新
- **更新请求**: 云请求固件更新
- **更新进度**: 设备报告更新进度
- **完成确认**: 设备确认更新完成

### 所需的 AWS IAM 权限

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

## IoT Rules Engine 探索器

### 目的
使用 IoT Rules Engine 学习消息路由和处理。此脚本教授规则创建、SQL 过滤和消息转换。

### 运行方法

**基本用法:**
```bash
python iot_rules_explorer.py
```

**带调试模式:**
```bash
python iot_rules_explorer.py --debug
```

### 先决条件
- 现有的 IoT Things（来自 setup_sample_data.py）
- 配置的 AWS 凭证
- 具有 Rules Engine 权限的 AWS IAM 策略

### 交互式 Rules Engine 学习

**主菜单**:
```
⚙️ IoT Rules Engine 选项:
1. 创建新规则
2. 列出现有规则
3. 查看规则详细信息
4. 测试规则 SQL
5. 删除规则
6. 退出

选择选项 (1-6):
```

### 主要学习功能

#### 1. 规则创建
- **SQL 语句**: 创建消息过滤 SQL
- **操作配置**: 设置规则操作（Amazon CloudWatch、Amazon SNS 等）
- **AWS IAM 角色**: 自动创建所需的 AWS IAM 角色
- **规则验证**: 验证规则语法和配置

#### 2. 规则管理
- **规则列表**: 查看所有现有规则
- **规则详细信息**: 查看完整的规则配置
- **规则状态**: 启用/禁用规则
- **规则删除**: 安全删除规则

#### 3. SQL 测试
- **交互式 SQL**: 测试 SQL 语句
- **消息模拟**: 使用示例消息测试过滤
- **结果预览**: 查看 SQL 过滤结果
- **语法验证**: 验证 SQL 语法

### 规则管理功能

#### SQL 语句示例
```sql
-- 基本过滤
SELECT * FROM 'topic/+/data' WHERE temperature > 25

-- 字段选择
SELECT temperature, humidity, timestamp() as ts FROM 'sensors/+/data'

-- 条件过滤
SELECT * FROM 'alerts/+' WHERE severity = 'HIGH'

-- 函数使用
SELECT *, topic(2) as device_id FROM 'devices/+/telemetry'
```

#### 支持的操作
- **Amazon CloudWatch**: 发送指标到 Amazon CloudWatch
- **Amazon SNS**: 发送通知到 Amazon SNS 主题
- **Amazon SQS**: 发送消息到 Amazon SQS 队列
- **AWS Lambda**: 调用 AWS Lambda 函数
- **Amazon DynamoDB**: 写入 Amazon DynamoDB 表

### 自动 AWS IAM 设置

脚本自动创建所需的 AWS IAM 角色：

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    }
  ]
}
```

### 规则测试

#### 测试消息示例
```json
{
  "deviceId": "sensor-001",
  "temperature": 28.5,
  "humidity": 65.2,
  "timestamp": "2023-01-01T12:00:00Z",
  "location": {
    "lat": 37.7749,
    "lon": -122.4194
  }
}
```

#### SQL 测试场景
- **温度阈值**: 过滤高温读数
- **设备过滤**: 选择特定设备
- **时间窗口**: 基于时间的过滤
- **地理过滤**: 基于位置的过滤

### 学习场景

#### 场景1: 温度监控
- **规则**: 检测高温读数
- **SQL**: `SELECT * FROM 'sensors/+/data' WHERE temperature > 30`
- **操作**: 发送 Amazon SNS 警报

#### 场景2: 设备健康监控
- **规则**: 监控设备连接状态
- **SQL**: `SELECT * FROM '$aws/events/presence/+' WHERE eventType = 'disconnected'`
- **操作**: 记录到 Amazon CloudWatch

#### 场景3: 数据聚合
- **规则**: 聚合传感器数据
- **SQL**: `SELECT avg(temperature) as avg_temp FROM 'sensors/+/data'`
- **操作**: 存储到 Amazon DynamoDB

### 所需的 AWS IAM 权限

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "iot:CreateTopicRule",
        "iot:ListTopicRules",
        "iot:GetTopicRule",
        "iot:DeleteTopicRule",
        "iot:EnableTopicRule",
        "iot:DisableTopicRule"
      ],
      "Resource": "*"
    },
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

## 总结

这些脚本提供了 AWS IoT Core 基本概念的全面学习体验。每个脚本都专注于 IoT 开发的特定方面，从设备管理到实时通信和消息处理。

### 推荐学习顺序
1. **设置示例数据** - 创建学习资源
2. **IoT Registry 探索** - 学习设备管理 API
3. **证书管理** - 学习 IoT 安全
4. **MQTT 通信** - 学习实时消息传递
5. **AWS IoT Device Shadow service** - 学习状态同步
6. **Rules Engine** - 学习消息处理
7. **清理** - 清理学习资源

### 学习成果
完成所有脚本后，您将了解：
- AWS IoT Core 架构和组件
- 设备注册和管理
- X.509 证书和 IoT 策略
- MQTT 协议和实时通信
- 设备状态同步
- 消息路由和处理
- IoT 安全最佳实践

### 后续步骤
- 探索高级 IoT 功能（AWS IoT Jobs、Fleet Provisioning）
- 集成其他 AWS 服务（AWS Lambda、Amazon DynamoDB）
- 构建端到端 IoT 解决方案
- 实施生产就绪的安全实践