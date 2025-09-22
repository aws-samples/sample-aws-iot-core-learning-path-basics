# AWS IoT Core - Learning Path - Basics

> 🌍 **Available Languages** | **Idiomas Disponibles** | **利用可能な言語** | **可用语言**
> 
> - **English** (Current) | [Español](README.es.md) | [中文](README.zh-CN.md) | [日本語](README.ja.md) | [Português](README.pt-BR.md)
> - **Documentation**: [English](docs/en/) | [Español](docs/es/) | [中文](docs/zh-CN/) | [日本語](docs/ja/) | [Português](docs/pt-BR/)

A comprehensive Python toolkit for learning Amazon Web Services (AWS) IoT Core basic concepts through hands-on exploration. Interactive scripts demonstrate device management, security, API operations, and MQTT communication with detailed explanations.

## 🚀 Quick Start - Complete Learning Path

```bash
# 1. Clone and setup
git clone https://github.com/aws-samples/sample-aws-iot-core-learning-path-basics.git
cd sample-aws-iot-core-learning-path-basics

# 2. Setup environment
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 3. Configure AWS credentials
export AWS_ACCESS_KEY_ID=<your-key>
export AWS_SECRET_ACCESS_KEY=<your-secret>
export AWS_DEFAULT_REGION=<your-region (e.g. us-east-1)>

# 4. Optional: Set language preference
export AWS_IOT_LANG=en  # 'es' for Spanish, 'ja' for Japanese, 'zh-CN' for Chinese, 'pt-BR' for Portuguese

# 5. Complete learning sequence
python scripts/setup_sample_data.py          # Create sample IoT resources
python scripts/iot_registry_explorer.py      # Explore AWS IoT APIs
python scripts/certificate_manager.py        # Learn IoT security
python scripts/mqtt_client_explorer.py       # Real-time MQTT communication
python scripts/device_shadow_explorer.py     # Device state synchronization
python scripts/iot_rules_explorer.py         # Message routing and processing
python scripts/cleanup_sample_data.py        # Clean up resources (IMPORTANT!)
```

**⚠️ Cost Warning**: This creates real AWS resources (~$0.17 total). Run cleanup when finished!

## Target Audience

**Primary Audience:** Cloud developers, solution architects, DevOps engineers new to AWS IoT Core

**Prerequisites:** Basic AWS knowledge, Python fundamentals, command line usage

**Learning Level:** Associate level with hands-on approach

## 🔧 Built with AWS SDKs

This project leverages the official AWS SDKs to provide authentic AWS IoT Core experiences:

### **Boto3 - AWS SDK for Python**
- **Purpose**: Powers all AWS IoT Registry operations, certificate management, and Rules Engine interactions
- **Version**: `>=1.26.0`
- **Documentation**: [Boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- **IoT Core APIs**: [Boto3 IoT Client](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/iot.html)

### **AWS IoT Device SDK for Python**
- **Purpose**: Enables authentic MQTT communication with AWS IoT Core using X.509 certificates
- **Version**: `>=1.11.0`
- **Documentation**: [AWS IoT Device SDK for Python v2](https://aws.github.io/aws-iot-device-sdk-python-v2/)
- **GitHub**: [aws-iot-device-sdk-python-v2](https://github.com/aws/aws-iot-device-sdk-python-v2)

**Why These SDKs Matter:**
- **Production-Ready**: Same SDKs used in real IoT applications
- **Security**: Built-in support for AWS IoT security best practices
- **Reliability**: Official AWS-maintained libraries with comprehensive error handling
- **Learning Value**: Experience authentic AWS IoT development patterns

## Table of Contents

- 🚀 [Quick Start](#-quick-start---complete-learning-path)
- ⚙️ [Installation & Setup](#️-installation--setup)
- 📚 [Learning Scripts](#-learning-scripts)
- 🧹 [Resource Cleanup](#-resource-cleanup)
- 🛠️ [Troubleshooting](#-troubleshooting)
- 📖 [Advanced Documentation](#-advanced-documentation)

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.10+
- AWS account with IoT permissions
- Terminal/command line access
- OpenSSL (for certificate features)

**⚠️ IMPORTANT SAFETY NOTE**: Use a dedicated development/learning AWS account. Do not run these scripts in accounts containing production IoT resources. While the cleanup script has multiple safety mechanisms, best practice is to use isolated environments for learning activities.

### Cost Information

**This project creates real AWS resources that will incur charges (~$0.17 total).**

| Service | Usage | Estimated Cost (USD) |
|---------|-------|---------------------|
| **AWS IoT Core** | ~100 messages, 20 devices | $0.10 |
| **IoT Device Shadow** | ~30 shadow operations | $0.04 |
| **IoT Rules Engine** | ~50 rule executions | $0.01 |
| **Certificate Storage** | 20 certificates for 1 day | $0.01 |
| **Amazon CloudWatch Logs** | Basic logging | $0.01 |
| **Total Estimated** | **Complete learning session** | **~$0.17** |

**⚠️ Important**: Always run the cleanup script when finished to avoid ongoing charges.



### Detailed Installation

**1. Clone Repository:**
```bash
git clone https://github.com/aws-samples/sample-aws-iot-core-learning-path-basics.git
cd sample-aws-iot-core-learning-path-basics
```

**2. Install OpenSSL:**
- **macOS:** `brew install openssl`
- **Ubuntu/Debian:** `sudo apt-get install openssl`
- **Windows:** Download from [OpenSSL website](https://www.openssl.org/)

**3. Virtual Environment (Recommended):**
```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

**4. Language Configuration (Optional):**
```bash
# Set language preference for all scripts
export AWS_IOT_LANG=en     # English (default)
export AWS_IOT_LANG=es     # Spanish
export AWS_IOT_LANG=ja     # Japanese
export AWS_IOT_LANG=zh-CN  # Chinese
export AWS_IOT_LANG=pt-BR  # Portuguese

# Alternative: Scripts will prompt for language if not set
```

**Supported Languages:**
- **English** (`en`, `english`) - Default
- **Spanish** (`es`, `spanish`, `español`) - Full translation available
- **Japanese** (`ja`, `japanese`, `日本語`, `jp`) - Full translation available
- **Chinese** (`zh-CN`, `chinese`, `中文`, `zh`) - Full translation available
- **Portuguese** (`pt-BR`, `portuguese`, `português`, `pt`) - Full translation available

## 🌍 Multi-Language Support

All learning scripts support English, Spanish, Japanese, Chinese, and Portuguese interfaces. The language affects:

**✅ What Gets Translated:**
- Welcome messages and educational content
- Menu options and user prompts
- Learning moments and explanations
- Error messages and confirmations
- Progress indicators and status messages

**❌ What Stays in Original Language:**
- AWS API responses (JSON data)
- Technical parameter names and values
- HTTP methods and endpoints
- Debug information and logs
- AWS resource names and identifiers

**Usage Options:**

**Option 1: Environment Variable (Recommended)**
```bash
# Set language preference for all scripts
export AWS_IOT_LANG=en     # English
export AWS_IOT_LANG=es     # Spanish
export AWS_IOT_LANG=ja     # Japanese
export AWS_IOT_LANG=zh-CN  # Chinese
export AWS_IOT_LANG=pt-BR  # Portuguese

# Run any script - language will be applied automatically
python scripts/iot_registry_explorer.py
```

**Option 2: Interactive Selection**
```bash
# Run without environment variable - script will prompt for language
python scripts/setup_sample_data.py

# Output example:
# 🌍 Language Selection / Selección de Idioma / 言語選択 / 语言选择 / Seleção de Idioma
# 1. English
# 2. Español (Spanish)
# 3. 日本語 (Japanese)
# 4. 中文 (Chinese)
# 5. Português (Portuguese)
# Select language (1-5): 5
```

**Supported Scripts:**
- ✅ `setup_sample_data.py` - Sample data creation
- ✅ `iot_registry_explorer.py` - API exploration
- ✅ `certificate_manager.py` - Certificate management
- ✅ `mqtt_client_explorer.py` - MQTT communication
- ✅ `mqtt_websocket_explorer.py` - WebSocket MQTT
- ✅ `device_shadow_explorer.py` - Device Shadow operations
- ✅ `iot_rules_explorer.py` - Rules Engine exploration
- ✅ `cleanup_sample_data.py` - Resource cleanup



## 📚 Learning Scripts

**Recommended Learning Path:**

### 1. 📊 Sample Data Setup
**File**: `scripts/setup_sample_data.py`
**Purpose**: Creates realistic IoT resources for hands-on learning
**Creates**: 20 Things, 3 Thing Types, 4 Thing Groups

### 2. 🔍 IoT Registry API Explorer
**File**: `scripts/iot_registry_explorer.py`
**Purpose**: Interactive tool for learning AWS IoT Registry APIs
**Features**: 8 core APIs with detailed explanations and real API calls

### 3. 🔐 Certificate & Policy Manager
**File**: `scripts/certificate_manager.py`
**Purpose**: Learn AWS IoT security through certificate and policy management
**Features**: Certificate creation, policy attachment, external certificate registration

### 4. 📡 MQTT Communication
**Files**: 
- `scripts/mqtt_client_explorer.py` (Certificate-based, recommended)
- `scripts/mqtt_websocket_explorer.py` (WebSocket-based alternative)

**Purpose**: Experience real-time IoT communication using MQTT protocol
**Features**: Interactive command-line interface, topic subscription, message publishing

### 5. 🌟 Device Shadow Explorer
**File**: `scripts/device_shadow_explorer.py`
**Purpose**: Learn device state synchronization with AWS IoT Device Shadow
**Features**: Interactive shadow management, state updates, delta processing

### 6. ⚙️ IoT Rules Engine Explorer
**File**: `scripts/iot_rules_explorer.py`
**Purpose**: Learn message routing and processing with IoT Rules Engine
**Features**: Rule creation, SQL filtering, automatic IAM setup

### 7. 🧹 Sample Data Cleanup
**File**: `scripts/cleanup_sample_data.py`
**Purpose**: Clean up all learning resources to avoid charges
**Features**: Safe cleanup with dependency handling

## 🧹 Resource Cleanup

**⚠️ IMPORTANT**: Always run cleanup when finished learning to avoid ongoing AWS charges.

```bash
python scripts/cleanup_sample_data.py
```

**What gets cleaned up:**
- ✅ Sample Things (Vehicle-VIN-001, Vehicle-VIN-002, etc.)
- ✅ Associated certificates and policies
- ✅ Thing Types and Thing Groups
- ✅ Local certificate files
- ✅ IoT Rules (if any created)

**What's protected:**
- ❌ Existing production IoT resources
- ❌ Non-sample certificates and policies
- ❌ Resources not created by learning scripts

## 🛠️ Troubleshooting

### Common Issues

**AWS Credentials:**
```bash
# Set credentials
export AWS_ACCESS_KEY_ID=<your-key>
export AWS_SECRET_ACCESS_KEY=<your-secret>
export AWS_DEFAULT_REGION=us-east-1
```

**Python Dependencies:**
```bash
pip install -r requirements.txt
```

**OpenSSL Issues:**
- **macOS**: `brew install openssl`
- **Ubuntu**: `sudo apt-get install openssl`

### Debug Mode

All scripts support debug mode for detailed API logging:
```bash
python scripts/<script_name>.py --debug
```

## 📖 Advanced Documentation

### Detailed Documentation
- **[Detailed Scripts Guide](docs/en/DETAILED_SCRIPTS.md)** - In-depth script documentation
- **[Complete Examples](docs/en/EXAMPLES.md)** - Full workflows and sample outputs
- **[Troubleshooting Guide](docs/en/TROUBLESHOOTING.md)** - Common issues and solutions

### Documentação em Português
- **[Guia Detalhado de Scripts](docs/pt-BR/DETAILED_SCRIPTS.md)** - Documentação aprofundada dos scripts
- **[Exemplos Completos](docs/pt-BR/EXAMPLES.md)** - Fluxos de trabalho completos e saídas de exemplo
- **[Guia de Solução de Problemas](docs/pt-BR/TROUBLESHOOTING.md)** - Problemas comuns e soluções

### 日本語ドキュメント
- **[詳細スクリプトガイド](docs/ja/DETAILED_SCRIPTS.md)** - 詳細なスクリプトドキュメント
- **[完全な例](docs/ja/EXAMPLES.md)** - 完全なワークフローとサンプル出力
- **[トラブルシューティングガイド](docs/ja/TROUBLESHOOTING.md)** - よくある問題と解決策

### 中文文档
- **[详细脚本指南](docs/zh-CN/DETAILED_SCRIPTS.md)** - 每个学习脚本的深入文档
- **[完整示例](docs/zh-CN/EXAMPLES.md)** - 完整的工作流程和实际场景
- **[故障排除指南](docs/zh-CN/TROUBLESHOOTING.md)** - 常见问题和错误的解决方案


### Learning Resources

#### AWS IoT Core Documentation
- **[AWS IoT Core Developer Guide](https://docs.aws.amazon.com/iot/latest/developerguide/)**
- **[AWS IoT Core API Reference](https://docs.aws.amazon.com/iot/latest/apireference/)**

#### AWS SDKs Used in This Project
- **[Boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)** - Complete Python SDK documentation
- **[Boto3 IoT Client Reference](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/iot.html)** - IoT-specific API methods
- **[AWS IoT Device SDK for Python v2](https://aws.github.io/aws-iot-device-sdk-python-v2/)** - MQTT client documentation
- **[AWS IoT Device SDK GitHub](https://github.com/aws/aws-iot-device-sdk-python-v2)** - Source code and examples

#### Protocol and Standards
- **[MQTT Protocol Specification](https://mqtt.org/)** - Official MQTT documentation
- **[X.509 Certificate Standard](https://tools.ietf.org/html/rfc5280)** - Certificate format specification

## 🤝 Contributing

This is an educational project. Contributions that improve the learning experience are welcome:

- **Bug fixes** for script issues
- **Translation improvements** for better localization
- **Documentation enhancements** for clarity
- **Additional learning scenarios** that fit the basic level

## 📄 License

This project is licensed under the MIT-0 License - see the [LICENSE](LICENSE) file for details.

## 🏷️ Tags

`aws-iot` `iot-core` `mqtt` `device-shadow` `certificates` `python` `learning` `tutorial` `hands-on` `interactive`