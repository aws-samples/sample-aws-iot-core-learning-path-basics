# AWS IoT Core - 学习路径 - 基础

> 🌍 **可用语言** | **Available Languages** | **Idiomas Disponibles** | **利用可能な言語**
> 
> - [English](README.md) | [Español](README.es.md) | **中文** (当前) | [日本語](README.ja.md) | [Português](README.pt-BR.md)
> - **文档**: [English](docs/en/) | [Español](docs/es/) | **中文** (docs/zh-CN/) | [日本語](docs/ja/) | [Português](docs/pt-BR/)

通过动手探索学习 Amazon Web Services (AWS) IoT Core 基本概念的综合 Python 工具包。交互式脚本演示设备管理、安全性、API 操作和 MQTT 通信，并提供详细说明。

## 🚀 快速开始 - 完整学习路径

```bash
# 1. 克隆和设置
git clone https://github.com/aws-samples/sample-aws-iot-core-learning-path-basics.git
cd sample-aws-iot-core-learning-path-basics

# 2. 环境设置
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 3. 配置 AWS 凭证
export AWS_ACCESS_KEY_ID=<your-key>
export AWS_SECRET_ACCESS_KEY=<your-secret>
export AWS_DEFAULT_REGION=<your-region (例如: us-east-1)>

# 4. 可选：设置语言偏好
export AWS_IOT_LANG=zh-CN  # 'en' 英语, 'es' 西班牙语, 'ja' 日语

# 5. 完整学习序列
python scripts/setup_sample_data.py          # 创建示例 IoT 资源
python scripts/iot_registry_explorer.py      # 探索 AWS IoT API
python scripts/certificate_manager.py        # 学习 IoT 安全
python scripts/mqtt_client_explorer.py       # 实时 MQTT 通信
python scripts/device_shadow_explorer.py     # 设备状态同步
python scripts/iot_rules_explorer.py         # 消息路由和处理
python scripts/cleanup_sample_data.py        # 清理资源（重要！）
```

**⚠️ 费用警告**: 这将创建真实的 AWS 资源（总计约 $0.17）。完成后请运行清理脚本！

## 目标受众

**主要受众**: 初次接触 AWS IoT Core 的云开发者、解决方案架构师、DevOps 工程师

**先决条件**: 基本的 AWS 知识、Python 基础、命令行使用经验

**学习级别**: 通过动手实践的助理级别方法

## 🔧 使用 AWS SDK 构建

此项目利用官方 AWS SDK 提供真实的 AWS IoT Core 体验：

### **Boto3 - AWS SDK for Python**
- **目的**: 支持所有 AWS IoT Registry 操作、证书管理和 Rules Engine 交互
- **版本**: `>=1.26.0`
- **文档**: [Boto3 文档](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- **IoT Core API**: [Boto3 IoT 客户端](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/iot.html)

### **AWS IoT Device SDK for Python**
- **目的**: 使用 X.509 证书实现与 AWS IoT Core 的真实 MQTT 通信
- **版本**: `>=1.11.0`
- **文档**: [AWS IoT Device SDK for Python v2](https://aws.github.io/aws-iot-device-sdk-python-v2/)
- **GitHub**: [aws-iot-device-sdk-python-v2](https://github.com/aws/aws-iot-device-sdk-python-v2)

**为什么这些 SDK 很重要:**
- **生产就绪**: 与真实 IoT 应用程序中使用的相同 SDK
- **安全性**: 内置支持 AWS IoT 安全最佳实践
- **可靠性**: AWS 官方维护的库，具有全面的错误处理
- **学习价值**: 体验真实的 AWS IoT 开发模式

## 目录

- 🚀 [快速开始](#-快速开始---完整学习路径)
- ⚙️ [安装和设置](#️-安装和设置)
- 📚 [学习脚本](#-学习脚本)
- 🧹 [资源清理](#-资源清理)
- 🛠️ [故障排除](#-故障排除)
- 📖 [高级文档](#-高级文档)

## ⚙️ 安装和设置

### 先决条件
- Python 3.10+
- 具有 IoT 权限的 AWS 账户
- 终端/命令行访问
- OpenSSL（用于证书功能）

### 费用信息

**此项目创建真实的 AWS 资源，将产生费用（总计约 $0.17）。**

| 服务 | 使用量 | 预估费用 (USD) |
|---------|-------|---------------------|
| **AWS IoT Core** | 约100条消息，20个设备 | $0.10 |
| **IoT Device Shadow** | 约30次影子操作 | $0.04 |
| **IoT Rules Engine** | 约50次规则执行 | $0.01 |
| **证书存储** | 20个证书存储1天 | $0.01 |
| **Amazon CloudWatch Logs** | 基本日志记录 | $0.01 |
| **总计预估** | **完整学习会话** | **约 $0.17** |

**⚠️ 重要**: 完成后务必运行清理脚本以避免持续费用。



### 详细安装

**1. 克隆仓库:**
```bash
git clone https://github.com/aws-samples/sample-aws-iot-core-learning-path-basics.git
cd sample-aws-iot-core-learning-path-basics
```

**2. 安装 OpenSSL:**
- **macOS:** `brew install openssl`
- **Ubuntu/Debian:** `sudo apt-get install openssl`
- **Windows:** 从 [OpenSSL 网站](https://www.openssl.org/) 下载

**3. 虚拟环境（推荐）:**
```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

**4. 语言配置（可选）:**
```bash
# 为所有脚本设置语言偏好
export AWS_IOT_LANG=zh-CN  # 中文
export AWS_IOT_LANG=en     # 英语（默认）
export AWS_IOT_LANG=es     # 西班牙语
export AWS_IOT_LANG=ja     # 日语

# 替代方案：如果未设置，脚本将提示选择语言
```

**支持的语言:**
- **英语** (`en`, `english`) - 默认
- **西班牙语** (`es`, `spanish`, `español`) - 完整翻译可用
- **日语** (`ja`, `japanese`, `日本語`, `jp`) - 完整翻译可用
- **中文** (`zh-CN`, `chinese`, `中文`, `zh`) - 完整翻译可用

## 🌍 多语言支持

所有学习脚本都支持英语、西班牙语、日语和中文界面。语言影响：

**✅ 翻译的内容:**
- 欢迎消息和教育内容
- 菜单选项和用户提示
- 学习要点和解释
- 错误消息和确认
- 进度指示器和状态消息

**❌ 保持原语言:**
- AWS API 响应（JSON 数据）
- 技术参数名称和值
- HTTP 方法和端点
- 调试信息和日志
- AWS 资源名称和标识符

**使用选项:**

**选项1: 环境变量（推荐）**
```bash
# 为所有脚本设置语言偏好
export AWS_IOT_LANG=zh-CN  # 中文
export AWS_IOT_LANG=en     # 英语
export AWS_IOT_LANG=es     # 西班牙语
export AWS_IOT_LANG=ja     # 日语

# 运行任何脚本 - 语言将自动应用
python scripts/iot_registry_explorer.py
```

**选项2: 交互式选择**
```bash
# 不使用环境变量运行 - 脚本将提示选择语言
python scripts/setup_sample_data.py

# 输出示例:
# 🌍 Language Selection / Selección de Idioma / 言語選択 / 语言选择
# 1. English
# 2. Español (Spanish)
# 3. 日本語 (Japanese)
# 4. 中文 (Chinese)
# Select language (1-4): 4
```

**支持的脚本:**
- ✅ `setup_sample_data.py` - 示例数据创建
- ✅ `iot_registry_explorer.py` - API 探索
- ✅ `certificate_manager.py` - 证书管理
- ✅ `mqtt_client_explorer.py` - MQTT 通信
- ✅ `mqtt_websocket_explorer.py` - WebSocket MQTT
- ✅ `device_shadow_explorer.py` - Device Shadow 操作
- ✅ `iot_rules_explorer.py` - Rules Engine 探索
- ✅ `cleanup_sample_data.py` - 资源清理

## 📚 学习脚本

**推荐学习路径:**

### 1. 📊 示例数据设置
**文件**: `scripts/setup_sample_data.py`
**目的**: 为动手学习创建真实的 IoT 资源
**创建**: 20个 Things、3个 Thing Types、4个 Thing Groups

### 2. 🔍 IoT Registry API 探索器
**文件**: `scripts/iot_registry_explorer.py`
**目的**: 学习 AWS IoT Registry API 的交互式工具
**功能**: 8个核心 API，包含详细说明和真实 API 调用

### 3. 🔐 证书和策略管理器
**文件**: `scripts/certificate_manager.py`
**目的**: 通过证书和策略管理学习 AWS IoT 安全
**功能**: 证书创建、策略附加、外部证书注册

### 4. 📡 MQTT 通信
**文件**: 
- `scripts/mqtt_client_explorer.py` (基于证书，推荐)
- `scripts/mqtt_websocket_explorer.py` (基于 WebSocket 的替代方案)

**目的**: 使用 MQTT 协议体验实时 IoT 通信
**功能**: 交互式命令行界面、主题订阅、消息发布

### 5. 🌟 Device Shadow 探索器
**文件**: `scripts/device_shadow_explorer.py`
**目的**: 使用 AWS IoT Device Shadow 学习设备状态同步
**功能**: 交互式影子管理、状态更新、增量处理

### 6. ⚙️ IoT Rules Engine 探索器
**文件**: `scripts/iot_rules_explorer.py`
**目的**: 使用 IoT Rules Engine 学习消息路由和处理
**功能**: 规则创建、SQL 过滤、自动 IAM 设置

### 7. 🧹 示例数据清理
**文件**: `scripts/cleanup_sample_data.py`
**目的**: 清理所有学习资源以避免费用
**功能**: 具有依赖关系处理的安全清理

## 🧹 资源清理

**⚠️ 重要**: 学习完成后务必运行清理以避免持续的 AWS 费用。

```bash
python scripts/cleanup_sample_data.py
```

**清理的内容:**
- ✅ 示例 Things (Vehicle-VIN-001、Vehicle-VIN-002 等)
- ✅ 关联的证书和策略
- ✅ Thing Types 和 Thing Groups
- ✅ 本地证书文件
- ✅ IoT 规则（如果创建了）

**受保护的内容:**
- ❌ 现有的生产 IoT 资源
- ❌ 非示例证书和策略
- ❌ 非学习脚本创建的资源

## 🛠️ 故障排除

### 常见问题

**AWS 凭证:**
```bash
# 设置凭证
export AWS_ACCESS_KEY_ID=<your-key>
export AWS_SECRET_ACCESS_KEY=<your-secret>
export AWS_DEFAULT_REGION=us-east-1
```

**Python 依赖项:**
```bash
pip install -r requirements.txt
```

**OpenSSL 问题:**
- **macOS**: `brew install openssl`
- **Ubuntu**: `sudo apt-get install openssl`

### 调试模式

所有脚本都支持详细 API 日志记录的调试模式:
```bash
python scripts/<script_name>.py --debug
```

## 📖 高级文档

### 详细文档
- **[详细脚本指南](docs/zh-CN/DETAILED_SCRIPTS.md)** - 深入的脚本文档
- **[完整示例](docs/zh-CN/EXAMPLES.md)** - 完整的工作流程和示例输出
- **[故障排除指南](docs/zh-CN/TROUBLESHOOTING.md)** - 常见问题和解决方案

### 学习资源
- **[AWS IoT Core 文档](https://docs.aws.amazon.com/iot/)**
- **[AWS IoT Device SDK](https://docs.aws.amazon.com/iot/latest/developerguide/iot-sdks.html)**
- **[MQTT 协议规范](https://mqtt.org/)**

## 🤝 贡献

这是一个教育项目。欢迎改善学习体验的贡献：

- **错误修复** 针对脚本问题
- **翻译改进** 为了更好的本地化
- **文档增强** 为了清晰度
- **额外学习场景** 适合基础级别的

### 学习资源

#### AWS IoT Core 文档
- **[AWS IoT Core 开发者指南](https://docs.aws.amazon.com/iot/latest/developerguide/)** - 完整的开发者指南
- **[AWS IoT Core API 参考](https://docs.aws.amazon.com/iot/latest/apireference/)** - API 文档

#### 此项目中使用的 AWS SDK
- **[Boto3 文档](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)** - 完整的 Python SDK 文档
- **[Boto3 IoT 客户端参考](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/iot.html)** - IoT 特定的 API 方法
- **[AWS IoT Device SDK for Python v2](https://aws.github.io/aws-iot-device-sdk-python-v2/)** - MQTT 客户端文档
- **[AWS IoT Device SDK GitHub](https://github.com/aws/aws-iot-device-sdk-python-v2)** - 源代码和示例

#### 协议和标准
- **[MQTT 协议规范](https://mqtt.org/)** - 官方 MQTT 文档
- **[X.509 证书标准](https://tools.ietf.org/html/rfc5280)** - 证书格式规范

## 📄 许可证

此项目在 MIT-0 许可证下授权 - 详情请参阅 [LICENSE](LICENSE) 文件。

## 🏷️ 标签

`aws-iot` `iot-core` `mqtt` `device-shadow` `certificates` `python` `learning` `tutorial` `hands-on` `interactive` `chinese` `中文`