# 문제 해결 가이드

이 문서는 Amazon Web Services (AWS) AWS IoT Core - 기초 학습 프로젝트에 대한 포괄적인 문제 해결 지침을 제공합니다.

## 목차

- [일반적인 문제](#일반적인-문제)
  - [AWS 자격 증명](#aws-자격-증명)
  - [가상 환경 문제](#가상-환경-문제)
  - [종속성 문제](#종속성-문제)
  - [권한 문제](#권한-문제)
  - [인증서 문제](#인증서-문제)
- [MQTT 연결 문제](#mqtt-연결-문제)
  - [인증서 기반 MQTT 문제](#인증서-기반-mqtt-문제)
  - [WebSocket MQTT 문제](#websocket-mqtt-문제)
- [AWS IoT Device Shadow service 문제](#device-shadow-문제)
  - [Shadow 연결 문제](#shadow-연결-문제)
  - [Shadow 상태 파일 문제](#shadow-상태-파일-문제)
- [Rules Engine 문제](#rules-engine-문제)
  - [규칙 생성 문제](#규칙-생성-문제)
  - [규칙 테스트 문제](#규칙-테스트-문제)
- [OpenSSL 문제](#openssl-문제)
  - [설치 문제](#설치-문제)
  - [인증서 생성 문제](#인증서-생성-문제)
- [네트워크 및 연결 문제](#네트워크-및-연결-문제)
  - [방화벽 및 프록시 문제](#방화벽-및-프록시-문제)
  - [DNS 해결 문제](#dns-해결-문제)
- [성능 및 타이밍 문제](#성능-및-타이밍-문제)
  - [API 속도 제한](#api-속도-제한)
  - [연결 시간 초과](#연결-시간-초과)
- [추가 도움 받기](#추가-도움-받기)
  - [디버그 모드 사용법](#디버그-모드-사용법)
  - [AWS IoT 콘솔 확인](#aws-iot-콘솔-확인)
  - [Amazon CloudWatch 로그](#cloudwatch-로그)
  - [일반적인 해결 단계](#일반적인-해결-단계)
  - [지원 리소스](#지원-리소스)

## 일반적인 문제

### AWS 자격 증명

#### 자격 증명 설정 확인
```bash
# 자격 증명이 구성되어 있는지 확인
aws sts get-caller-identity

# 현재 리전 확인
echo $AWS_DEFAULT_REGION

# 환경 변수 목록
env | grep AWS
```

#### 일반적인 자격 증명 문제

**문제: "자격 증명을 찾을 수 없습니다"**
```bash
# 해결책 1: 환경 변수 설정
export AWS_ACCESS_KEY_ID=<your-access-key>
export AWS_SECRET_ACCESS_KEY=<your-secret-key>
export AWS_DEFAULT_REGION=us-east-1

# 해결책 2: AWS CLI 구성 사용
aws configure

# 해결책 3: 기존 구성 확인
aws configure list
```

**문제: "리전을 지정해야 합니다"**
```bash
# 기본 리전 설정
export AWS_DEFAULT_REGION=us-east-1

# 또는 AWS CLI 구성에서 지정
aws configure set region us-east-1
```

**문제: "요청에 포함된 보안 토큰이 유효하지 않습니다"**
- **원인**: 만료된 임시 자격 증명 또는 잘못된 세션 토큰
- **해결책**: 자격 증명을 새로 고치거나 만료된 세션 토큰 제거
```bash
unset AWS_SESSION_TOKEN
# 그 다음 새 자격 증명 설정
```

### 가상 환경 문제

#### 가상 환경 확인
```bash
# venv가 활성화되어 있는지 확인
which python
# 다음과 같이 표시되어야 함: /path/to/your/project/venv/bin/python

# Python 버전 확인
python --version
# 3.7 이상이어야 함

# 설치된 패키지 목록
pip list
```

#### 가상 환경 문제

**문제: 가상 환경이 활성화되지 않음**
```bash
# 가상 환경 활성화
# macOS/Linux에서:
source venv/bin/activate

# Windows에서:
venv\Scripts\activate

# 활성화 확인
which python
```

**문제: 잘못된 Python 버전**
```bash
# 특정 Python 버전으로 새 venv 생성
python3.9 -m venv venv
# 또는
python3 -m venv venv

# 활성화 및 확인
source venv/bin/activate
python --version
```

**문제: 패키지 설치 실패**
```bash
# 먼저 pip 업그레이드
python -m pip install --upgrade pip

# requirements 설치
pip install -r requirements.txt

# 여전히 실패하면 개별 패키지 시도
pip install boto3
pip install awsiotsdk
```

### 종속성 문제

#### 종속성 재설치
```bash
# 모든 패키지 업그레이드
pip install --upgrade -r requirements.txt

# 강제 재설치
pip install --force-reinstall -r requirements.txt

# pip 캐시 지우고 재설치
pip cache purge
pip install -r requirements.txt
```

#### 일반적인 종속성 오류

**문제: "'boto3' 모듈을 찾을 수 없습니다"**
```bash
# venv가 활성화되어 있는지 확인하고 설치
pip install boto3

# 설치 확인
python -c "import boto3; print(boto3.__version__)"
```

**문제: "'awsiot' 모듈을 찾을 수 없습니다"**
```bash
# AWS IoT SDK 설치
pip install awsiotsdk

# 설치 확인
python -c "import awsiot; print('AWS IoT SDK installed')"
```

**문제: SSL/TLS 인증서 오류**
```bash
# macOS에서 인증서 업데이트
/Applications/Python\ 3.x/Install\ Certificates.command

# 또는 인증서 패키지 설치
pip install --upgrade certifi
```

### 권한 문제

#### AWS Identity and Access Management (AWS IAM) 권한

**학습 스크립트에 필요한 권한:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "iot:*",
        "iam:CreateRole",
        "iam:CreatePolicy",
        "iam:AttachRolePolicy",
        "iam:GetRole",
        "iam:PassRole"
      ],
      "Resource": "*"
    }
  ]
}
```

**최소 권한 (iot:*가 너무 광범위한 경우):**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "iot:CreateThing",
        "iot:ListThings",
        "iot:DescribeThing",
        "iot:DeleteThing",
        "iot:CreateThingType",
        "iot:ListThingTypes",
        "iot:DescribeThingType",
        "iot:DeleteThingType",
        "iot:CreateThingGroup",
        "iot:ListThingGroups",
        "iot:DescribeThingGroup",
        "iot:DeleteThingGroup",
        "iot:CreateKeysAndCertificate",
        "iot:ListCertificates",
        "iot:DescribeCertificate",
        "iot:UpdateCertificate",
        "iot:DeleteCertificate",
        "iot:CreatePolicy",
        "iot:ListPolicies",
        "iot:GetPolicy",
        "iot:AttachPolicy",
        "iot:DetachPolicy",
        "iot:AttachThingPrincipal",
        "iot:DetachThingPrincipal",
        "iot:ListThingPrincipals",
        "iot:ListPrincipalThings",
        "iot:Connect",
        "iot:Publish",
        "iot:Subscribe",
        "iot:Receive",
        "iot:GetThingShadow",
        "iot:UpdateThingShadow",
        "iot:CreateTopicRule",
        "iot:ListTopicRules",
        "iot:GetTopicRule",
        "iot:DeleteTopicRule"
      ],
      "Resource": "*"
    }
  ]
}
```

**일반적인 권한 오류:**

**문제: "사용자가 iot:CreateThing 수행 권한이 없습니다"**
- **원인**: AWS IAM 권한 부족
- **해결책**: AWS IAM 사용자/역할에 IoT 권한 추가

**문제: AWS IAM 역할 생성 시 "액세스 거부됨"**
- **원인**: Rules Engine용 AWS IAM 권한 누락
- **해결책**: AWS IAM 권한 추가 또는 기존 역할 사용

### 인증서 문제

#### 인증서 파일 문제

**문제: 인증서 파일을 찾을 수 없음**
```bash
# certificates 디렉토리가 존재하는지 확인
ls -la certificates/

# 특정 Thing 인증서 확인
ls -la certificates/Vehicle-VIN-001/

# 인증서 파일 확인
openssl x509 -in certificates/Vehicle-VIN-001/cert-id.crt -text -noout
```

**문제: 인증서가 Thing에 연결되지 않음**
```bash
# 레지스트리 탐색기를 실행하여 확인
python iot_registry_explorer.py
# 옵션 5 (Thing 설명) 선택하고 인증서가 나열되는지 확인
```

**문제: 정책이 인증서에 연결되지 않음**
```bash
# 인증서 관리자를 사용하여 정책 연결
python certificate_manager.py
# 옵션 3 (기존 인증서에 정책 연결) 선택
```

#### 인증서 상태 문제

**문제: 인증서가 비활성 상태**
```bash
# 인증서 관리자를 사용하여 활성화
python certificate_manager.py
# 옵션 5 (인증서 활성화/비활성화) 선택
```

**문제: 인증서 검증 실패**
```bash
# 인증서 형식 확인
head -5 certificates/Vehicle-VIN-001/cert-id.crt
# 다음으로 시작해야 함: -----BEGIN CERTIFICATE-----

# 인증서 검증
openssl x509 -in certificates/Vehicle-VIN-001/cert-id.crt -noout
# 출력 없음은 유효함을 의미, 오류는 무효함을 의미
```

## MQTT 연결 문제

### 인증서 기반 MQTT 문제

#### 연결 진단
```bash
# 자세한 오류 정보를 위해 디버그 모드 사용
python mqtt_client_explorer.py --debug

# OpenSSL로 기본 연결 테스트
openssl s_client -connect <your-endpoint>:8883 \
  -cert certificates/Vehicle-VIN-001/<cert-id>.crt \
  -key certificates/Vehicle-VIN-001/<cert-id>.key
```

#### 일반적인 MQTT 오류

**문제: "연결 시간 초과"**
- **원인**: 네트워크 연결, 잘못된 엔드포인트, 방화벽
- **해결책**:
  ```bash
  # 엔드포인트 확인
  python iot_registry_explorer.py
  # 옵션 8 (엔드포인트 설명) 선택
  
  # 네트워크 연결 테스트
  ping your-iot-endpoint.amazonaws.com
  
  # 방화벽 확인 (포트 8883이 열려 있어야 함)
  telnet your-iot-endpoint.amazonaws.com 8883
  ```

**문제: "인증 실패"**
- **원인**: 인증서 문제, 정책 문제, Thing이 연결되지 않음
- **해결책**:
  1. 인증서가 활성 상태인지 확인
  2. 인증서가 Thing에 연결되어 있는지 확인
  3. 정책이 인증서에 연결되어 있는지 확인
  4. 정책 권한에 iot:Connect가 포함되어 있는지 확인

**문제: "구독/게시 실패"**
- **원인**: 정책 제한, 잘못된 주제 형식
- **해결책**:
  ```bash
  # 정책 권한 확인
  # 정책에 다음이 포함되어야 함: iot:Subscribe, iot:Publish, iot:Receive
  
  # 주제 형식 확인 (공백 없음, 유효한 문자)
  # 유효함: device/sensor/temperature
  # 무효함: device sensor temperature
  ```

#### MQTT 문제 해결 명령

**MQTT 클라이언트 내에서:**
```bash
📡 MQTT> debug                    # 연결 진단 표시
📡 MQTT> status                   # 연결 정보 표시
📡 MQTT> messages                 # 메시지 기록 표시
```

**디버그 출력 예시:**
```
🔍 연결 진단:
   엔드포인트: a1b2c3d4e5f6g7-ats.iot.us-east-1.amazonaws.com
   포트: 8883
   클라이언트 ID: Vehicle-VIN-001-mqtt-12345678
   인증서: certificates/Vehicle-VIN-001/abc123.crt
   개인 키: certificates/Vehicle-VIN-001/abc123.key
   연결 상태: 연결됨
   Keep Alive: 30초
   클린 세션: True
```

### WebSocket MQTT 문제

#### WebSocket 진단
```bash
# AWS 자격 증명 확인
aws sts get-caller-identity

# IAM 권한 확인
aws iam get-user-policy --user-name <your-username> --policy-name <policy-name>

# 디버그 모드 사용
python mqtt_websocket_explorer.py --debug
```

#### 일반적인 WebSocket 오류

**문제: "자격 증명 검증 실패"**
- **원인**: AWS 자격 증명 누락 또는 무효
- **해결책**: 적절한 AWS 자격 증명 설정
  ```bash
  export AWS_ACCESS_KEY_ID=<your-key>
  export AWS_SECRET_ACCESS_KEY=<your-secret>
  export AWS_DEFAULT_REGION=us-east-1
  ```

**문제: "WebSocket 연결 실패"**
- **원인**: 네트워크 문제, 프록시 설정, 방화벽
- **해결책**:
  ```bash
  # HTTPS 연결 테스트
  curl -I https://your-endpoint.amazonaws.com
  
  # 프록시 설정 확인
  echo $HTTP_PROXY
  echo $HTTPS_PROXY
  ```

**문제: "SigV4 서명 오류"**
- **원인**: 시계 오차, 잘못된 자격 증명
- **해결책**:
  ```bash
  # 시스템 시계 동기화
  sudo ntpdate -s time.nist.gov  # Linux/macOS
  
  # 자격 증명이 만료되지 않았는지 확인
  aws sts get-caller-identity
  ```

### AWS IoT Device Shadow service 문제

#### Shadow 연결 문제

**문제: Shadow 작업 실패**
- **원인**: Shadow 권한 누락, 인증서 문제
- **해결책**:
  1. 정책에 shadow 권한이 포함되어 있는지 확인:
     ```json
     {
       "Action": [
         "iot:GetThingShadow",
         "iot:UpdateThingShadow"
       ]
     }
     ```
  2. 인증서가 올바른 Thing에 연결되어 있는지 확인
  3. Thing 이름이 shadow 작업과 일치하는지 확인

**문제: 델타 메시지가 수신되지 않음**
- **원인**: 구독 문제, 주제 권한
- **해결책**:
  ```bash
  # shadow 주제 구독 확인
  🌟 Shadow> status
  
  # 정책이 shadow 주제 구독을 허용하는지 확인
  # 주제: $aws/things/{thingName}/shadow/update/delta
  ```

#### Shadow 상태 파일 문제

**문제: 로컬 상태 파일을 찾을 수 없음**
- **원인**: 파일 생성 권한, 경로 문제
- **해결책**:
  ```bash
  # certificates 디렉토리 권한 확인
  ls -la certificates/
  
  # 필요한 경우 상태 파일 수동 생성
  echo '{"temperature": 20.0, "status": "online"}' > certificates/Vehicle-VIN-001/device_state.json
  ```

**문제: 상태 파일의 잘못된 JSON**
- **원인**: 수동 편집 오류
- **해결책**:
  ```bash
  # JSON 형식 검증
  python -m json.tool certificates/Vehicle-VIN-001/device_state.json
  
  # 파일 수정 또는 재생성
  ```

### Rules Engine 문제

#### 규칙 생성 문제

**문제: AWS IAM 역할 생성 실패**
- **원인**: AWS IAM 권한 부족, 역할이 이미 존재함
- **해결책**:
  ```bash
  # 역할이 존재하는지 확인
  aws iam get-role --role-name IoTRulesEngineRole
  
  # 필요한 경우 수동으로 역할 생성
  aws iam create-role --role-name IoTRulesEngineRole --assume-role-policy-document file://trust-policy.json
  ```

**문제: SQL 구문 오류**
- **원인**: 잘못된 SQL 형식, 지원되지 않는 함수
- **해결책**:
  - 간단한 SELECT, FROM, WHERE 절 사용
  - 복잡한 SQL 함수 피하기
  - 먼저 기본 규칙으로 테스트

#### 규칙 테스트 문제

**문제: 규칙이 트리거되지 않음**
- **원인**: 주제 불일치, WHERE 절 문제, 규칙 비활성화
- **해결책**:
  1. 주제 패턴이 게시된 주제와 일치하는지 확인
  2. WHERE 절 논리 확인
  3. 규칙이 활성화되어 있는지 확인
  4. 먼저 간단한 규칙으로 테스트

**문제: 규칙 출력이 수신되지 않음**
- **원인**: 구독 문제, 액션 구성
- **해결책**:
  ```bash
  # 규칙 액션 확인
  python iot_rules_explorer.py
  # 옵션 2 (규칙 설명) 선택
  
  # 출력 주제 구독 확인
  # 구독: processed/* 또는 alerts/*
  ```

## OpenSSL 문제

### 설치 문제

**macOS:**
```bash
# Homebrew를 통해 설치
brew install openssl

# 필요한 경우 PATH에 추가
export PATH="/usr/local/opt/openssl/bin:$PATH"
```

**Ubuntu/Debian:**
```bash
# 패키지 목록 업데이트 및 설치
sudo apt-get update
sudo apt-get install openssl

# 설치 확인
openssl version
```

**Windows:**
```bash
# 다음에서 다운로드: https://slproweb.com/products/Win32OpenSSL.html
# 또는 Windows Subsystem for Linux (WSL) 사용

# WSL에서:
sudo apt-get install openssl
```

### 인증서 생성 문제

**문제: OpenSSL 명령을 찾을 수 없음**
- **해결책**: OpenSSL 설치 또는 PATH에 추가

**문제: 인증서 파일 생성 시 권한 거부됨**
- **해결책**: 디렉토리 권한 확인 또는 적절한 권한으로 실행

**문제: 잘못된 인증서 형식**
- **해결책**: OpenSSL 명령 구문 및 매개변수 확인

## 네트워크 및 연결 문제

### 방화벽 및 프록시 문제

**필요한 포트:**
- **TLS를 통한 MQTT**: 8883
- **WebSocket MQTT**: 443
- **HTTPS (API 호출)**: 443

**기업 방화벽:**
```bash
# 포트 연결 테스트
telnet your-iot-endpoint.amazonaws.com 8883
telnet your-iot-endpoint.amazonaws.com 443

# 프록시 설정 확인
echo $HTTP_PROXY
echo $HTTPS_PROXY
echo $NO_PROXY
```

**프록시 구성:**
```bash
# HTTPS용 프록시 설정
export HTTPS_PROXY=http://proxy.company.com:8080

# AWS 엔드포인트에 대한 프록시 우회
export NO_PROXY=amazonaws.com,.amazonaws.com
```

### DNS 해결 문제

**문제: IoT 엔드포인트를 해결할 수 없음**
```bash
# DNS 해결 테스트
nslookup your-iot-endpoint.amazonaws.com

# 대체 DNS 사용
export AWS_IOT_ENDPOINT=$(dig +short your-iot-endpoint.amazonaws.com)
```

## 성능 및 타이밍 문제

### API 속도 제한

**문제: ThrottlingException**
- **원인**: 너무 빠르게 너무 많은 API 호출
- **해결책**: 작업 간 지연 추가 또는 동시성 감소

**문제: 최종 일관성 지연**
- **원인**: AWS 서비스가 변경사항을 전파하는 데 시간 필요
- **해결책**: 리소스 생성 후 대기 시간 추가

### 연결 시간 초과

**문제: MQTT keep-alive 시간 초과**
- **원인**: 네트워크 불안정, 긴 유휴 기간
- **해결책**:
  - keep-alive 간격 줄이기
  - 연결 재시도 로직 구현
  - 네트워크 안정성 확인

## 추가 도움 받기

### 디버그 모드 사용법

**모든 스크립트에 대해 디버그 모드 활성화:**
```bash
python script_name.py --debug
```

**디버그 모드 제공 사항:**
- 자세한 API 요청/응답 로깅
- 연결 진단
- 오류 스택 추적
- 타이밍 정보

### AWS IoT 콘솔 확인

**AWS 콘솔에서 리소스 확인:**
1. **Things**: AWS IoT Core → 관리 → Things
2. **인증서**: AWS IoT Core → 보안 → 인증서
3. **정책**: AWS IoT Core → 보안 → 정책
4. **규칙**: AWS IoT Core → 작업 → 규칙

### Amazon CloudWatch 로그

**프로덕션 디버깅을 위한 IoT 로깅 활성화:**
1. AWS IoT Core → 설정으로 이동
2. 적절한 로그 레벨로 로깅 활성화
3. 자세한 오류 정보는 Amazon CloudWatch 로그 확인

### 일반적인 해결 단계

**다른 모든 방법이 실패할 때:**
1. **새로 시작**: 정리 스크립트를 실행하고 다시 시작
2. **AWS 상태 확인**: AWS 서비스 상태 대시보드 방문
3. **계정 제한 확인**: AWS 서비스 할당량 확인
4. **최소 설정으로 테스트**: 가능한 가장 간단한 구성 사용
5. **작동하는 예제와 비교**: 제공된 샘플 데이터 사용

### 지원 리소스

- **AWS IoT 문서**: https://docs.aws.amazon.com/iot/
- **AWS IoT 개발자 가이드**: https://docs.aws.amazon.com/iot/latest/developerguide/
- **AWS 지원**: https://aws.amazon.com/support/
- **AWS 포럼**: https://forums.aws.amazon.com/forum.jspa?forumID=210