# AWS IoT Core - 학습 경로 - 기초

> 🌍 **사용 가능한 언어** | **Available Languages** | **Idiomas Disponibles** | **利用可能な言語** | **可用语言**
> 
> - [English](README.md) | [Español](README.es.md) | [中文](README.zh-CN.md) | [日本語](README.ja.md) | [Português](README.pt-BR.md) | **한국어** (현재)
> - **문서**: [English](docs/en/) | [Español](docs/es/) | [中文](docs/zh-CN/) | [日本語](docs/ja/) | [Português](docs/pt-BR/) | [한국어](docs/ko/)

실습을 통해 Amazon Web Services (AWS) AWS IoT Core 기본 개념을 학습할 수 있는 포괄적인 Python 툴킷입니다. 대화형 스크립트는 디바이스 관리, 보안, API 작업 및 MQTT 통신을 자세한 설명과 함께 시연합니다.

## 🚀 빠른 시작 - 완전한 학습 경로

```bash
# 1. 클론 및 설정
git clone https://github.com/aws-samples/sample-aws-iot-core-learning-path-basics.git
cd sample-aws-iot-core-learning-path-basics

# 2. 환경 설정
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 3. AWS 자격 증명 구성
export AWS_ACCESS_KEY_ID=<your-key>
export AWS_SECRET_ACCESS_KEY=<your-secret>
export AWS_DEFAULT_REGION=<your-region (예: us-east-1)>

# 4. 선택사항: 언어 설정
export AWS_IOT_LANG=ko  # 'en' 영어, 'es' 스페인어, 'ja' 일본어, 'zh-CN' 중국어, 'pt-BR' 포르투갈어

# 5. 완전한 학습 순서
python scripts/setup_sample_data.py          # 샘플 IoT 리소스 생성
python scripts/iot_registry_explorer.py      # AWS IoT API 탐색
python scripts/certificate_manager.py        # IoT 보안 학습
python scripts/mqtt_client_explorer.py       # 실시간 MQTT 통신
python scripts/device_shadow_explorer.py     # 디바이스 상태 동기화
python scripts/iot_rules_explorer.py         # 메시지 라우팅 및 처리
python scripts/cleanup_sample_data.py        # 리소스 정리 (중요!)
```

**⚠️ 비용 경고**: 실제 AWS 리소스를 생성합니다 (총 ~$0.17). 완료 후 정리를 실행하세요!

## 대상 사용자

**주요 대상**: AWS IoT Core를 처음 접하는 클라우드 개발자, 솔루션 아키텍트, DevOps 엔지니어

**전제 조건**: 기본 AWS 지식, Python 기초, 명령줄 사용법

**학습 수준**: 실습 접근 방식의 어소시에이트 레벨

## 🔧 AWS SDK로 구축

이 프로젝트는 공식 AWS SDK를 활용하여 진정한 AWS IoT Core 경험을 제공합니다:

### **Boto3 - Python용 AWS SDK**
- **목적**: 모든 AWS IoT 레지스트리 작업, 인증서 관리 및 규칙 엔진 상호작용을 지원
- **버전**: `>=1.26.0`
- **문서**: [Boto3 문서](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- **AWS IoT Core API**: [Boto3 IoT 클라이언트](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/iot.html)

### **Python용 AWS IoT 디바이스 SDK**
- **목적**: X.509 인증서를 사용하여 AWS IoT Core와 진정한 MQTT 통신 가능
- **버전**: `>=1.11.0`
- **문서**: [Python용 AWS IoT 디바이스 SDK v2](https://aws.github.io/aws-iot-device-sdk-python-v2/)
- **GitHub**: [aws-iot-device-sdk-python-v2](https://github.com/aws/aws-iot-device-sdk-python-v2)

**이러한 SDK가 중요한 이유:**
- **프로덕션 준비**: 실제 IoT 애플리케이션에서 사용되는 동일한 SDK
- **보안**: AWS IoT 보안 모범 사례에 대한 내장 지원
- **신뢰성**: 포괄적인 오류 처리를 갖춘 AWS 공식 유지 관리 라이브러리
- **학습 가치**: 진정한 AWS IoT 개발 패턴 경험

## 목차

- 🚀 [빠른 시작](#-빠른-시작---완전한-학습-경로)
- ⚙️ [설치 및 설정](#️-설치-및-설정)
- 📚 [학습 스크립트](#-학습-스크립트)
- 🧹 [리소스 정리](#-리소스-정리)
- 🛠️ [문제 해결](#-문제-해결)
- 📖 [고급 문서](#-고급-문서)

## ⚙️ 설치 및 설정

### 전제 조건
- Python 3.10+
- IoT 권한이 있는 AWS 계정
- 터미널/명령줄 액세스
- OpenSSL (인증서 기능용)

**⚠️ 중요한 안전 참고사항**: 전용 개발/학습 AWS 계정을 사용하세요. 프로덕션 IoT 리소스가 포함된 계정에서는 이러한 스크립트를 실행하지 마세요. 정리 스크립트에 여러 안전 메커니즘이 있지만, 학습 활동에는 격리된 환경을 사용하는 것이 모범 사례입니다.

### 비용 정보

**이 프로젝트는 요금이 발생하는 실제 AWS 리소스를 생성합니다 (총 ~$0.17).**

| 서비스 | 사용량 | 예상 비용 (USD) |
|---------|-------|---------------------|
| **AWS IoT Core** | ~100개 메시지, 20개 디바이스 | $0.10 |
| **AWS IoT Device Shadow service** | ~30개 섀도우 작업 | $0.04 |
| **IoT Rules Engine** | ~50개 규칙 실행 | $0.01 |
| **인증서 저장소** | 1일간 20개 인증서 | $0.01 |
| **Amazon CloudWatch Logs** | 기본 로깅 | $0.01 |
| **총 예상** | **완전한 학습 세션** | **~$0.17** |

**⚠️ 중요**: 지속적인 요금을 피하기 위해 완료 후 항상 정리 스크립트를 실행하세요.

### 자세한 설치

**1. 저장소 클론:**
```bash
git clone https://github.com/aws-samples/sample-aws-iot-core-learning-path-basics.git
cd sample-aws-iot-core-learning-path-basics
```

**2. OpenSSL 설치:**
- **macOS:** `brew install openssl`
- **Ubuntu/Debian:** `sudo apt-get install openssl`
- **Windows:** [OpenSSL 웹사이트](https://www.openssl.org/)에서 다운로드

**3. 가상 환경 (권장):**
```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

**4. 언어 구성 (선택사항):**
```bash
# 모든 스크립트에 대한 언어 설정
export AWS_IOT_LANG=ko     # 한국어
export AWS_IOT_LANG=en     # 영어 (기본값)
export AWS_IOT_LANG=es     # 스페인어
export AWS_IOT_LANG=ja     # 일본어
export AWS_IOT_LANG=zh-CN  # 중국어
export AWS_IOT_LANG=pt-BR  # 포르투갈어

# 대안: 설정되지 않은 경우 스크립트가 언어를 묻습니다
```

**지원되는 언어:**
- **한국어** (`ko`, `korean`, `한국어`, `kr`) - 완전한 번역 제공
- **영어** (`en`, `english`) - 기본값
- **스페인어** (`es`, `spanish`, `español`) - 완전한 번역 제공
- **일본어** (`ja`, `japanese`, `日本語`, `jp`) - 완전한 번역 제공
- **중국어** (`zh-CN`, `chinese`, `中文`, `zh`) - 완전한 번역 제공
- **포르투갈어** (`pt-BR`, `portuguese`, `português`, `pt`) - 완전한 번역 제공

## 🌍 다국어 지원

모든 학습 스크립트는 영어, 스페인어, 일본어, 중국어, 포르투갈어, 한국어 인터페이스를 지원합니다. 언어는 다음에 영향을 줍니다:

**✅ 번역되는 것:**
- 환영 메시지 및 교육 콘텐츠
- 메뉴 옵션 및 사용자 프롬프트
- 학습 순간 및 설명
- 오류 메시지 및 확인
- 진행 표시기 및 상태 메시지

**❌ 원래 언어로 유지되는 것:**
- AWS API 응답 (JSON 데이터)
- 기술적 매개변수 이름 및 값
- HTTP 메서드 및 엔드포인트
- 디버그 정보 및 로그
- AWS 리소스 이름 및 식별자

**사용 옵션:**

**옵션 1: 환경 변수 (권장)**
```bash
# 모든 스크립트에 대한 언어 설정
export AWS_IOT_LANG=ko     # 한국어
export AWS_IOT_LANG=en     # 영어
export AWS_IOT_LANG=es     # 스페인어
export AWS_IOT_LANG=ja     # 일본어
export AWS_IOT_LANG=zh-CN  # 중국어
export AWS_IOT_LANG=pt-BR  # 포르투갈어

# 스크립트 실행 - 언어가 자동으로 적용됩니다
python scripts/iot_registry_explorer.py
```

**옵션 2: 대화형 선택**
```bash
# 환경 변수 없이 실행 - 스크립트가 언어를 묻습니다
python scripts/setup_sample_data.py

# 출력 예시:
# 🌍 Language Selection / Selección de Idioma / 言語選択 / 语言选择 / Seleção de Idioma / 언어 선택
# 1. English
# 2. Español (Spanish)
# 3. 日本語 (Japanese)
# 4. 中文 (Chinese)
# 5. Português (Portuguese)
# 6. 한국어 (Korean)
# Select language (1-6): 6
```

**지원되는 스크립트:**
- ✅ `setup_sample_data.py` - 샘플 데이터 생성
- ✅ `iot_registry_explorer.py` - API 탐색
- ✅ `certificate_manager.py` - 인증서 관리
- ✅ `mqtt_client_explorer.py` - MQTT 통신
- ✅ `mqtt_websocket_explorer.py` - WebSocket MQTT
- ✅ `device_shadow_explorer.py` - AWS IoT Device Shadow service 작업
- ✅ `iot_rules_explorer.py` - Rules Engine 탐색
- ✅ `cleanup_sample_data.py` - 리소스 정리

## 📚 학습 스크립트

**권장 학습 경로:**

### 1. 📊 샘플 데이터 설정
**파일**: `scripts/setup_sample_data.py`
**목적**: 실습 학습을 위한 현실적인 IoT 리소스 생성
**생성**: 20개 Things, 3개 Thing Types, 4개 Thing Groups

### 2. 🔍 IoT 레지스트리 API 탐색기
**파일**: `scripts/iot_registry_explorer.py`
**목적**: AWS IoT 레지스트리 API 학습을 위한 대화형 도구
**기능**: 자세한 설명과 실제 API 호출이 포함된 8개 핵심 API

### 3. 🔐 인증서 및 정책 관리자
**파일**: `scripts/certificate_manager.py`
**목적**: 인증서 및 정책 관리를 통한 AWS IoT 보안 학습
**기능**: 인증서 생성, 정책 연결, 외부 인증서 등록

### 4. 📡 MQTT 통신
**파일**: 
- `scripts/mqtt_client_explorer.py` (인증서 기반, 권장)
- `scripts/mqtt_websocket_explorer.py` (WebSocket 기반 대안)

**목적**: MQTT 프로토콜을 사용한 실시간 IoT 통신 경험
**기능**: 대화형 명령줄 인터페이스, 주제 구독, 메시지 게시

### 5. 🌟 AWS IoT Device Shadow service 탐색기
**파일**: `scripts/device_shadow_explorer.py`
**목적**: AWS IoT Device Shadow를 사용한 디바이스 상태 동기화 학습
**기능**: 대화형 섀도우 관리, 상태 업데이트, 델타 처리

### 6. ⚙️ IoT Rules Engine 탐색기
**파일**: `scripts/iot_rules_explorer.py`
**목적**: IoT Rules Engine을 사용한 메시지 라우팅 및 처리 학습
**기능**: 규칙 생성, SQL 필터링, 자동 AWS IAM 설정

### 7. 🧹 샘플 데이터 정리
**파일**: `scripts/cleanup_sample_data.py`
**목적**: 요금을 피하기 위해 모든 학습 리소스 정리
**기능**: 종속성 처리를 통한 안전한 정리

## 🧹 리소스 정리

**⚠️ 중요**: 지속적인 AWS 요금을 피하기 위해 학습 완료 후 항상 정리를 실행하세요.

```bash
python scripts/cleanup_sample_data.py
```

**정리되는 것:**
- ✅ 샘플 Things (Vehicle-VIN-001, Vehicle-VIN-002 등)
- ✅ 연결된 인증서 및 정책
- ✅ Thing Types 및 Thing Groups
- ✅ 로컬 인증서 파일
- ✅ IoT Rules (생성된 경우)

**보호되는 것:**
- ❌ 기존 프로덕션 IoT 리소스
- ❌ 샘플이 아닌 인증서 및 정책
- ❌ 학습 스크립트로 생성되지 않은 리소스

## 🛠️ 문제 해결

### 일반적인 문제

**AWS 자격 증명:**
```bash
# 자격 증명 설정
export AWS_ACCESS_KEY_ID=<your-key>
export AWS_SECRET_ACCESS_KEY=<your-secret>
export AWS_DEFAULT_REGION=us-east-1
```

**Python 종속성:**
```bash
pip install -r requirements.txt
```

**OpenSSL 문제:**
- **macOS**: `brew install openssl`
- **Ubuntu**: `sudo apt-get install openssl`

### 디버그 모드

모든 스크립트는 자세한 API 로깅을 위한 디버그 모드를 지원합니다:
```bash
python scripts/<script_name>.py --debug
```

## 📖 고급 문서

### 자세한 문서
- **[자세한 스크립트 가이드](docs/ko/DETAILED_SCRIPTS.md)** - 심층 스크립트 문서
- **[완전한 예제](docs/ko/EXAMPLES.md)** - 전체 워크플로우 및 샘플 출력
- **[문제 해결 가이드](docs/ko/TROUBLESHOOTING.md)** - 일반적인 문제 및 해결책

### 학습 리소스

#### AWS IoT Core 문서
- **[AWS IoT Core 개발자 가이드](https://docs.aws.amazon.com/iot/latest/developerguide/)**
- **[AWS IoT Core API 참조](https://docs.aws.amazon.com/iot/latest/apireference/)**

#### 이 프로젝트에서 사용된 AWS SDK
- **[Boto3 문서](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)** - 완전한 Python SDK 문서
- **[Boto3 IoT 클라이언트 참조](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/iot.html)** - IoT 특정 API 메서드
- **[Python용 AWS IoT 디바이스 SDK v2](https://aws.github.io/aws-iot-device-sdk-python-v2/)** - MQTT 클라이언트 문서
- **[AWS IoT 디바이스 SDK GitHub](https://github.com/aws/aws-iot-device-sdk-python-v2)** - 소스 코드 및 예제

#### 프로토콜 및 표준
- **[MQTT 프로토콜 사양](https://mqtt.org/)** - 공식 MQTT 문서
- **[X.509 인증서 표준](https://tools.ietf.org/html/rfc5280)** - 인증서 형식 사양

## 🤝 기여

이것은 교육 프로젝트입니다. 학습 경험을 개선하는 기여를 환영합니다:

- 스크립트 문제에 대한 **버그 수정**
- 더 나은 현지화를 위한 **번역 개선**
- 명확성을 위한 **문서 개선**
- 기본 수준에 맞는 **추가 학습 시나리오**

## 📄 라이선스

이 프로젝트는 MIT-0 라이선스에 따라 라이선스가 부여됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 🏷️ 태그

`aws-iot` `iot-core` `mqtt` `device-shadow` `certificates` `python` `learning` `tutorial` `hands-on` `interactive`