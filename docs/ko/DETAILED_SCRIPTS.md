# 자세한 스크립트 문서

이 문서는 AWS IoT Core - 기초 프로젝트의 모든 학습 스크립트에 대한 포괄적인 문서를 제공합니다.

## 목차

- [IoT 레지스트리 API 탐색기](#iot-레지스트리-api-탐색기)
  - [목적](#목적)
  - [실행 방법](#실행-방법)
  - [대화형 메뉴 시스템](#대화형-메뉴-시스템)
  - [학습 세부사항이 포함된 지원 API](#학습-세부사항이-포함된-지원-api)
  - [학습 기능](#학습-기능)
  - [오류 학습](#오류-학습)
- [인증서 및 정책 관리자](#인증서-및-정책-관리자)
  - [목적](#목적-1)
  - [실행 방법](#실행-방법-1)
  - [대화형 메인 메뉴](#대화형-메인-메뉴)
  - [옵션 1: 완전한 인증서 워크플로우](#옵션-1-완전한-인증서-워크플로우)
  - [옵션 2: 외부 인증서 등록](#옵션-2-외부-인증서-등록)
  - [옵션 3: 정책 연결 워크플로우](#옵션-3-정책-연결-워크플로우)
  - [옵션 4: 정책 분리 워크플로우](#옵션-4-정책-분리-워크플로우)
  - [옵션 5: 인증서 상태 관리](#옵션-5-인증서-상태-관리)
  - [인증서 관리 심화](#인증서-관리-심화)
  - [정책 관리 심화](#정책-관리-심화)
  - [API 학습 기능](#api-학습-기능)
  - [인증서 옵션 설명](#인증서-옵션-설명)
  - [오류 학습 시나리오](#오류-학습-시나리오)
- [MQTT 통신](#mqtt-통신)
  - [목적](#목적-2)
  - [사용 가능한 두 가지 MQTT 옵션](#사용-가능한-두-가지-mqtt-옵션)
  - [인증서 기반 MQTT 클라이언트](#인증서-기반-mqtt-클라이언트)
  - [WebSocket MQTT 클라이언트](#websocket-mqtt-클라이언트)
  - [MQTT 프로토콜 학습](#mqtt-프로토콜-학습)
- [Device Shadow 탐색기](#device-shadow-탐색기)
  - [목적](#목적-3)
  - [실행 방법](#실행-방법-2)
  - [전제 조건](#전제-조건)
  - [대화형 Device Shadow 학습](#대화형-device-shadow-학습)
  - [주요 학습 기능](#주요-학습-기능)
  - [Shadow 메시지 분석](#shadow-메시지-분석)
  - [학습 시나리오](#학습-시나리오)
  - [필요한 IAM 권한](#필요한-iam-권한)
- [IoT Rules Engine 탐색기](#iot-rules-engine-탐색기)
  - [목적](#목적-4)
  - [실행 방법](#실행-방법-3)
  - [전제 조건](#전제-조건-1)
  - [대화형 Rules Engine 학습](#대화형-rules-engine-학습)
  - [주요 학습 기능](#주요-학습-기능-1)
  - [규칙 관리 기능](#규칙-관리-기능)
  - [자동 IAM 구성](#자동-iam-구성)
  - [규칙 테스트](#규칙-테스트)
  - [학습 시나리오](#학습-시나리오-1)
  - [필요한 IAM 권한](#필요한-iam-권한-1)

## IoT 레지스트리 API 탐색기

### 목적
실제 API 호출과 자세한 설명을 통해 AWS IoT 레지스트리 API를 학습하는 대화형 도구입니다. 이 스크립트는 IoT 디바이스, 인증서 및 정책을 관리하는 데 사용되는 제어 평면 작업을 가르칩니다.

**참고**: AWS IoT Core는 디바이스 관리 및 보안 전반에 걸쳐 많은 API를 제공합니다. 이 탐색기는 IoT 디바이스 수명 주기 관리를 이해하는 데 필수적인 8개의 핵심 레지스트리 API에 중점을 둡니다. 완전한 API 세부사항은 [AWS IoT 레지스트리 API 참조](https://docs.aws.amazon.com/iot/latest/apireference/API_Operations_AWS_IoT.html)를 참조하세요.

### 실행 방법

**기본 사용법:**
```bash
python iot_registry_explorer.py
```

**디버그 모드 (향상된 API 세부사항):**
```bash
python iot_registry_explorer.py --debug
```

### 대화형 메뉴 시스템

스크립트를 실행하면 다음이 표시됩니다:
```
📋 사용 가능한 작업:
1. Things 목록
2. 인증서 목록
3. Thing Groups 목록
4. Thing Types 목록
5. Thing 설명
6. Thing Group 설명
7. Thing Type 설명
8. 엔드포인트 설명
9. 종료

작업 선택 (1-9):
```

### 학습 세부사항이 포함된 지원 API

#### 1. Things 목록
- **목적**: 계정의 모든 IoT 디바이스 검색
- **HTTP**: `GET /things`
- **학습**: 페이지네이션 및 필터링 옵션을 통한 디바이스 검색
- **사용 가능한 옵션**:
  - **기본 목록**: 모든 Things 표시
  - **페이지네이션**: 더 작은 배치로 Things 검색 (페이지당 최대 결과 지정)
  - **Thing Type별 필터**: 특정 카테고리의 차량 찾기 (예: SedanVehicle)
  - **속성별 필터**: 특정 속성을 가진 차량 찾기 (예: country=US)
- **출력**: 이름, 유형, 속성이 포함된 Thing 객체 배열
- **📚 API 참조**: [ListThings](https://docs.aws.amazon.com/iot/latest/apireference/API_ListThings.html)

#### 2. 인증서 목록
- **목적**: 디바이스 인증을 위한 모든 X.509 인증서 보기
- **HTTP**: `GET /certificates`
- **학습**: 인증서 수명 주기, 상태 관리
- **출력**: 인증서 ID, ARN, 생성 날짜, 상태
- **📚 API 참조**: [ListCertificates](https://docs.aws.amazon.com/iot/latest/apireference/API_ListCertificates.html)

#### 3. Thing Groups 목록
- **목적**: 디바이스 조직 및 계층 구조 보기
- **HTTP**: `GET /thing-groups`
- **학습**: 디바이스 그룹화 전략, 대규모 관리
- **출력**: 그룹 이름, ARN, 설명
- **📚 API 참조**: [ListThingGroups](https://docs.aws.amazon.com/iot/latest/apireference/API_ListThingGroups.html)

#### 4. Thing Types 목록
- **목적**: 디바이스 템플릿 및 카테고리 보기
- **HTTP**: `GET /thing-types`
- **학습**: 디바이스 분류, 속성 스키마
- **출력**: 유형 이름, 설명, 검색 가능한 속성
- **📚 API 참조**: [ListThingTypes](https://docs.aws.amazon.com/iot/latest/apireference/API_ListThingTypes.html)

#### 5. Thing 설명
- **목적**: 특정 디바이스에 대한 자세한 정보 가져오기
- **HTTP**: `GET /things/{thingName}`
- **필요한 입력**: Thing 이름 (예: "Vehicle-VIN-001")
- **학습**: 디바이스 메타데이터, 속성, 관계
- **출력**: 완전한 Thing 세부사항, 버전, ARN
- **📚 API 참조**: [DescribeThing](https://docs.aws.amazon.com/iot/latest/apireference/API_DescribeThing.html)

#### 6. Thing Group 설명
- **목적**: 그룹 세부사항 및 속성 보기
- **HTTP**: `GET /thing-groups/{thingGroupName}`
- **필요한 입력**: 그룹 이름 (예: "CustomerFleet")
- **학습**: 그룹 계층, 정책, 속성
- **출력**: 그룹 속성, 부모/자식 관계
- **📚 API 참조**: [DescribeThingGroup](https://docs.aws.amazon.com/iot/latest/apireference/API_DescribeThingGroup.html)

#### 7. Thing Type 설명
- **목적**: 유형 사양 및 템플릿 보기
- **HTTP**: `GET /thing-types/{thingTypeName}`
- **필요한 입력**: 유형 이름 (예: "SedanVehicle")
- **학습**: 유형 정의, 검색 가능한 속성
- **출력**: 유형 속성, 생성 메타데이터
- **📚 API 참조**: [DescribeThingType](https://docs.aws.amazon.com/iot/latest/apireference/API_DescribeThingType.html)

#### 8. 엔드포인트 설명
- **목적**: 계정의 IoT 엔드포인트 URL 가져오기
- **HTTP**: `GET /endpoint`
- **입력 옵션**: 엔드포인트 유형 (iot:Data-ATS, iot:Data, iot:CredentialProvider, iot:Jobs)
- **학습**: 다양한 엔드포인트 유형과 그 목적
- **출력**: 디바이스 연결을 위한 HTTPS 엔드포인트 URL
- **📚 API 참조**: [DescribeEndpoint](https://docs.aws.amazon.com/iot/latest/apireference/API_DescribeEndpoint.html)

### 학습 기능

**각 API 호출에 대해 다음을 볼 수 있습니다:**
- 🔄 **API 호출 이름** 및 설명
- 🌐 **HTTP 요청** 메서드 및 전체 경로
- ℹ️ **작업 설명** - 무엇을 하고 왜 하는지
- 📥 **입력 매개변수** - 전송하는 데이터
- 💡 **응답 설명** - 출력의 의미
- 📤 **응답 페이로드** - 반환된 실제 JSON 데이터

**예시 출력:**
```
🔄 API 호출: describe_thing
🌐 HTTP 요청: GET https://iot.<region>.amazonaws.com/things/Vehicle-VIN-001
ℹ️  설명: 특정 IoT Thing에 대한 자세한 정보를 검색합니다
📥 입력 매개변수: {"thingName": "Vehicle-VIN-001"}
💡 응답 설명: 속성, 유형, 버전 및 ARN을 포함한 완전한 Thing 세부사항을 반환합니다
📤 응답 페이로드: {
  "thingName": "Vehicle-VIN-001",
  "thingTypeName": "SedanVehicle",
  "attributes": {
    "customerId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "country": "US",
    "manufacturingDate": "2024-03-15"
  },
  "version": 1
}
```

### 오류 학습
스크립트는 일반적인 오류를 처리하고 설명합니다:
- **ResourceNotFoundException** - Things/Groups가 존재하지 않을 때
- **InvalidRequestException** - 매개변수가 잘못된 형식일 때
- **ThrottlingException** - API 속도 제한을 초과했을 때
- **UnauthorizedException** - 권한이 부족할 때

## 인증서 및 정책 관리자

### 목적
실습 인증서 및 정책 관리를 통해 AWS IoT 보안 개념을 학습합니다. 이 스크립트는 완전한 보안 모델인 디바이스 신원(인증서)과 권한 부여(정책)를 가르칩니다.

### 실행 방법

**기본 사용법:**
```bash
python certificate_manager.py
```

**디버그 모드 (자세한 API 로깅):**
```bash
python certificate_manager.py --debug
```

### 대화형 메인 메뉴

스크립트를 실행하면 다음이 표시됩니다:
```
🔐 AWS IoT 인증서 및 정책 관리자
==================================================
이 스크립트는 AWS IoT 보안 개념을 가르칩니다:
• 디바이스 인증을 위한 X.509 인증서
• 인증서-Thing 연결
• 권한 부여를 위한 IoT 정책
• 정책 연결 및 분리
• 외부 인증서 등록
• 각 작업에 대한 완전한 API 세부사항
==================================================

📋 메인 메뉴:
1. AWS IoT 인증서 생성 및 Thing에 연결 (+ 선택적 정책)
2. 외부 인증서 등록 및 Thing에 연결 (+ 선택적 정책)
3. 기존 인증서에 정책 연결
4. 인증서에서 정책 분리
5. 인증서 활성화/비활성화
6. 종료

옵션 선택 (1-6):
```

### 옵션 1: 완전한 인증서 워크플로우

**가르치는 내용:**
- 종단 간 인증서 수명 주기
- 디바이스 신원 설정
- 보안 모범 사례

**단계별 프로세스:**

#### 1단계: Thing 선택
- **대화형 디바이스 선택기** 여러 옵션 제공:
  - 번호가 매겨진 목록에서 선택 (처음 10개 표시)
  - `all` 입력하여 전체 디바이스 목록 보기
  - `manual` 입력하여 Thing 이름 직접 입력
- **검증** - 진행하기 전에 Thing이 존재하는지 확인
- **학습**: 디바이스 검색 및 선택 패턴

#### 2단계: 인증서 생성
- **API 호출**: `create_keys_and_certificate`
- **HTTP**: `POST /keys-and-certificate`
- **발생하는 일**: AWS가 X.509 인증서 + 키 쌍 생성
- **학습**: 인증서 구성 요소와 그 목적
- **출력**: 인증서 ARN, ID, PEM 데이터, 공개/개인 키

#### 3단계: 로컬 파일 저장
- **자동 폴더 생성**: `certificates/{thing-name}/`
- **저장된 파일**:
  - `{cert-id}.crt` - 인증서 PEM (AWS IoT용)
  - `{cert-id}.key` - 개인 키 (보안 유지!)
  - `{cert-id}.pub` - 공개 키 (참조용)
- **학습**: 인증서 파일 관리 및 보안

#### 4단계: 인증서-Thing 연결
- **기존 인증서 확인** - Thing에 이미 인증서가 있으면 경고
- **정리 옵션** - 원하는 경우 이전 인증서 제거
- **API 호출**: `attach_thing_principal`
- **HTTP**: `PUT /things/{thingName}/principals`
- **학습**: 디바이스 신원 바인딩

#### 5단계: 정책 관리 (선택사항)
- **선택**: 기존 정책 사용, 새 정책 생성 또는 건너뛰기
- **기존 정책 선택**: 계정의 사용 가능한 정책에서 선택
- **새 정책 생성**: 템플릿 사용 가능 또는 사용자 정의 JSON 입력
- **학습**: 인증 vs 권한 부여, 정책 재사용 전략

### 옵션 2: 외부 인증서 등록

**가르치는 내용:**
- BYOC(Bring Your Own Certificate) 워크플로우
- 자체 서명 인증서 통합
- OpenSSL 인증서 생성
- 외부 PKI 인프라 통합

### 옵션 3: 정책 연결 워크플로우

**가르치는 내용:**
- 인증서 생성 없이 정책 관리
- 기존 인증서 작업
- 권한 문제 해결

### 옵션 4: 정책 분리 워크플로우

**가르치는 내용:**
- 인증서에서 정책 제거
- 정책 연결로 디바이스 찾기
- 인증서-정책 관계 관리
- 권한 취소 시나리오

**단계별 프로세스:**

#### 1단계: 정책 선택
- **대화형 정책 선택기** 모든 사용 가능한 정책에서
- **정책 검증** - 정책이 존재하는지 확인
- **학습**: 정책 검색 및 선택 패턴

#### 2단계: 인증서 검색
- **API 호출**: `list_targets_for_policy`
- **HTTP**: `POST /targets-for-policy/{policyName}`
- **발생하는 일**: 선택된 정책이 연결된 모든 인증서 찾기
- **학습**: 정책-인증서 관계 매핑
- **출력**: 정책 연결이 있는 인증서 ARN

#### 3단계: 디바이스 연결
- **API 호출**: 각 인증서에 대해 `list_principal_things`
- **HTTP**: `GET /principal-things`
- **발생하는 일**: 인증서를 연결된 Things(디바이스)에 매핑
- **학습**: 인증서-Thing 관계 및 디바이스 식별
- **표시**: 쉬운 선택을 위한 인증서 ID → Thing 이름 매핑

#### 4단계: 인증서 선택
- **향상된 표시** - 컨텍스트를 위해 인증서 ID → Thing 이름 표시
- **디바이스 컨텍스트** - 영향을 받을 디바이스의 명확한 가시성
- **영향 평가** - 권한 변경 이해
- **학습**: 디바이스 인식을 통한 인증서 선택

#### 5단계: 정책 분리
- **API 호출**: `detach_policy`
- **HTTP**: `POST /target-policies/{policyName}`
- **발생하는 일**: 선택된 인증서에서 정책 제거
- **학습**: 정책 분리 프로세스 및 즉각적인 효과
- **영향**: 디바이스가 정책에 정의된 특정 권한을 잃음

**사용 사례:**
- **권한 취소** - 디바이스에서 특정 권한 제거
- **역할 변경** - 정책 변경으로 디바이스 기능 수정
- **보안 사고** - 손상된 정책 권한 신속 제거
- **정책 업데이트** - 업데이트된 버전 연결 전 이전 정책 분리
- **문제 해결** - 문제가 있는 정책 제거하여 문제 격리

### 옵션 5: 인증서 상태 관리

**가르치는 내용:**
- 인증서 수명 주기 관리
- 보안 제어를 위한 활성화/비활성화 작업
- 디바이스 연결에 대한 인증서 상태의 영향
- 인증서 상태 문제 해결

### 인증서 관리 심화

**X.509 인증서 생성:**
- **공개 키 인프라(PKI)** 개념
- AWS IoT에서 **인증 기관(CA)** 역할
- **키 쌍 생성** 및 암호화 원리
- **인증서 수명 주기** - 생성, 활성화, 순환, 취소

**로컬 파일 저장 전략:**
```
certificates/
├── Vehicle-VIN-001/               # Thing당 하나의 폴더
│   ├── abc123def456.crt          # 인증서 PEM
│   ├── abc123def456.key          # 개인 키 (절대 공유 금지)
│   └── abc123def456.pub          # 공개 키 (참조)
├── Vehicle-VIN-002/
│   ├── xyz789uvw012.crt
│   ├── xyz789uvw012.key
│   └── xyz789uvw012.pub
└── MyCustomDevice/
    └── ...

sample-certs/                    # OpenSSL 생성 인증서
├── sample-device.crt            # 샘플 인증서
└── sample-device.key            # 샘플 개인 키
```

### 정책 관리 심화

**정책 템플릿 설명:**

**1. 기본 디바이스 정책:**
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "iot:Connect",     # AWS IoT에 연결
      "iot:Publish",     # 메시지 전송
      "iot:Subscribe",   # 주제 수신
      "iot:Receive"      # 메시지 수신
    ],
    "Resource": "*"      # 모든 리소스 (광범위한 권한)
  }]
}
```

**2. 읽기 전용 정책:**
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "iot:Connect",     # 연결만
      "iot:Subscribe",   # 수신만
      "iot:Receive"      # 수신만 (게시 없음)
    ],
    "Resource": "*"
  }]
}
```

### API 학습 기능

**모든 API 작업에 대해 다음을 볼 수 있습니다:**

🔍 **API 세부사항:**
- **작업 이름** (예: `create_keys_and_certificate`)
- **HTTP 메서드** (GET, POST, PUT, DELETE)
- **API 경로** (예: `/keys-and-certificate`)
- **설명** API가 수행하는 작업
- **입력 매개변수** 실제 값 포함
- **예상 출력** 구조 및 의미

### 인증서 옵션 설명

#### AWS IoT 인증서 (옵션 1)
- **AWS에서 생성** - AWS가 공개/개인 키 쌍 생성
- **사용된 API**: `create_keys_and_certificate`
- **최적 용도**: 프로덕션 IoT 디바이스
- **키 관리**: AWS가 인증 기관 기능 처리

#### 외부 인증서 (옵션 2)
- **자체 인증서 가져오기** - 기존 또는 자체 생성 인증서 사용
- **사용된 API**: `register_certificate_without_ca` (자체 서명용) 또는 `register_certificate` (CA 서명용)
- **최적 용도**: 기존 PKI 인프라 통합 또는 자체 서명 인증서로 학습
- **키 관리**: 개인 키를 직접 제어

### 오류 학습 시나리오

스크립트는 일반적인 보안 오류를 처리하고 설명합니다:
- **인증서가 이미 존재함** - 중복 처리 방법
- **Thing을 찾을 수 없음** - 디바이스 검색 문제
- **정책 이름 충돌** - 명명 전략 솔루션
- **권한 거부됨** - IAM 권한 문제 해결
- **잘못된 정책 JSON** - 구문 오류 해결

## MQTT 통신

### 목적
MQTT 프로토콜을 사용하여 실시간 IoT 통신을 경험합니다. 디바이스가 AWS IoT Core에 연결하고 안전하게 메시지를 교환하는 방법을 학습합니다.

### 사용 가능한 두 가지 MQTT 옵션

#### 옵션 A: 인증서 기반 MQTT (학습 권장)
**파일**: `mqtt_client_explorer.py`
**인증**: X.509 인증서 (상호 TLS)
**최적 용도**: 프로덕션 IoT 보안 이해

#### 옵션 B: WebSocket MQTT (대안 방법)
**파일**: `mqtt_websocket_explorer.py`  
**인증**: AWS IAM 자격 증명 (SigV4)
**최적 용도**: 웹 애플리케이션 및 방화벽 친화적 연결

### 인증서 기반 MQTT 클라이언트

#### 실행 방법

**기본 사용법:**
```bash
python mqtt_client_explorer.py
```

**디버그 모드 (연결 진단):**
```bash
python mqtt_client_explorer.py --debug
```

#### 전제 조건
- **인증서가 존재해야 함** - 먼저 `certificate_manager.py` 실행
- **정책 연결됨** - 인증서에 IoT 권한 필요
- **Thing 연결** - 인증서가 Thing에 연결되어야 함

#### MQTT 학습 기능

**연결 프로세스:**
- **엔드포인트 검색** - 계정의 IoT 엔드포인트 가져오기
- **TLS 구성** - 인증서로 상호 TLS 설정
- **MQTT 프로토콜** - TLS를 통한 MQTT 연결 설정
- **Keep-Alive** - 지속적인 연결 유지

**주제 관리:**
- **구독** - 와일드카드로 MQTT 주제 수신
- **QoS 레벨** - 서비스 품질 (0 = 최대 한 번, 1 = 최소 한 번)
- **주제 패턴** - `+` (단일 레벨) 및 `#` (다중 레벨) 와일드카드 사용

#### 대화형 명령

연결 후 다음 명령을 사용하세요:

```bash
# 주제 구독
📡 MQTT> sub device/+/temperature                  # QoS 0으로 구독
📡 MQTT> sub1 device/alerts/#                      # QoS 1로 구독
📡 MQTT> unsub device/+/temperature               # 주제 구독 해제

# 메시지 게시
📡 MQTT> pub device/sensor/temperature 23.5        # QoS 0으로 게시
📡 MQTT> pub1 device/alert "High temp!"            # QoS 1로 게시
📡 MQTT> json device/data temp=23.5 humidity=65    # JSON 객체 게시

# 유틸리티 명령
📡 MQTT> test                                      # 테스트 메시지 전송
📡 MQTT> status                                    # 연결 정보 표시
📡 MQTT> messages                                  # 메시지 기록 표시
📡 MQTT> help                                      # 모든 명령 표시
📡 MQTT> quit                                      # 클라이언트 종료
```

### MQTT 프로토콜 학습

#### 핵심 개념

**주제 및 계층:**
- **주제 구조**: `device/sensor/temperature`
- **와일드카드**: `device/+/temperature` (단일 레벨), `device/#` (다중 레벨)
- **모범 사례**: 계층적 명명, 공백 피하기

**서비스 품질(QoS):**
- **QoS 0 (최대 한 번)**: 발사 후 망각, 가장 빠름
- **QoS 1 (최소 한 번)**: 전달 보장, 중복 가능
- **QoS 2 (정확히 한 번)**: AWS IoT에서 지원되지 않음

## Device Shadow 탐색기

### 목적
디바이스 상태 동기화의 실습 탐색을 통해 AWS IoT Device Shadow 서비스를 학습합니다. 이 스크립트는 완전한 섀도우 수명 주기인 원하는 상태, 보고된 상태 및 델타 처리를 가르칩니다.

### 실행 방법

**기본 사용법:**
```bash
python device_shadow_explorer.py
```

**디버그 모드 (자세한 섀도우 메시지 분석):**
```bash
python device_shadow_explorer.py --debug
```

### 전제 조건
- **인증서가 존재해야 함** - 먼저 `certificate_manager.py` 실행
- **섀도우 권한이 있는 정책** - 인증서에 IoT 섀도우 권한 필요
- **Thing 연결** - 인증서가 Thing에 연결되어야 함

### 대화형 Device Shadow 학습

#### Shadow 문서 구조

**완전한 Shadow 문서:**
```json
{
  "state": {
    "desired": {
      "temperature": 25.0,
      "status": "active"
    },
    "reported": {
      "temperature": 22.5,
      "status": "online",
      "firmware_version": "1.0.0"
    },
    "delta": {
      "temperature": 25.0,
      "status": "active"
    }
  },
  "metadata": {
    "desired": {
      "temperature": {
        "timestamp": 1642248600
      }
    },
    "reported": {
      "temperature": {
        "timestamp": 1642248500
      }
    }
  },
  "version": 15,
  "timestamp": 1642248600
}
```

### 주요 학습 기능

#### 자동 상태 동기화
**델타 처리:**
1. **델타 감지** - 스크립트가 원하는 상태 ≠ 보고된 상태를 자동 감지
2. **사용자 알림** - 차이점을 표시하고 조치를 요청
3. **로컬 업데이트** - 로컬 디바이스 상태 파일에 변경사항 적용
4. **Shadow 보고** - 업데이트된 상태를 AWS IoT에 다시 보고

### Shadow 메시지 분석

**실시간 메시지 표시:**
```
======================================================================
🌟 SHADOW 메시지 수신됨 [14:30:15.789]
======================================================================
✅ SHADOW 업데이트 승인됨
   📊 새 버전: 16
   ⏰ 타임스탬프: 1642248615
   📡 업데이트된 보고됨: {
     "temperature": 24.0,
     "humidity": 45.0,
     "status": "online"
   }
======================================================================
```

### 학습 시나리오

#### 시나리오 1: 클라우드-디바이스 통신
1. `desire` 명령을 사용하여 클라우드/앱이 원하는 상태를 설정하는 것을 시뮬레이션
2. 델타 메시지 생성 관찰
3. 로컬 디바이스에 변경사항 적용
4. 업데이트된 상태를 섀도우에 다시 보고

#### 시나리오 2: 디바이스-클라우드 통신
1. `edit` 명령을 사용하여 로컬 디바이스 상태 수정
2. `report` 명령을 사용하여 섀도우 업데이트
3. 섀도우 업데이트 승인 관찰

### 필요한 IAM 권한

**Shadow 정책 예시:**
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
        "iot:Receive",
        "iot:GetThingShadow",
        "iot:UpdateThingShadow"
      ],
      "Resource": "*"
    }
  ]
}
```

## IoT Rules Engine 탐색기

### 목적
실습 규칙 생성 및 관리를 통해 AWS IoT Rules Engine을 학습합니다. 이 스크립트는 자동 IAM 역할 설정과 함께 메시지 라우팅, SQL 기반 필터링 및 액션 구성을 가르칩니다.

### 실행 방법

**기본 사용법:**
```bash
python iot_rules_explorer.py
```

**디버그 모드 (자세한 API 및 IAM 작업):**
```bash
python iot_rules_explorer.py --debug
```

### 전제 조건
- **AWS 자격 증명** - IoT Rules 및 IAM 역할 관리를 위한 IAM 권한
- **인증서 불필요** - Rules Engine은 서비스 레벨에서 작동

### 대화형 Rules Engine 학습

#### 메인 메뉴 옵션
스크립트를 실행하면:
1. **모든 IoT Rules 목록** - 상태 및 액션과 함께 기존 규칙 보기
2. **특정 IoT Rule 설명** - 자세한 규칙 분석 및 SQL 분석
3. **새 IoT Rule 생성** - SQL 빌더를 통한 안내된 규칙 생성
4. **IoT Rule 관리** - 규칙 활성화, 비활성화 또는 삭제

### 주요 학습 기능

#### 규칙 생성 워크플로우
**단계별 안내 생성:**
1. **규칙 명명** - 명명 규칙 및 고유성 요구사항 학습
2. **이벤트 유형 선택** - 일반적인 IoT 이벤트 유형 또는 사용자 정의에서 선택
3. **SQL 문 구축** - 대화형 SELECT, FROM, WHERE 절 구성
4. **액션 구성** - 적절한 IAM 역할로 재게시 대상 설정
5. **자동 IAM 설정** - 스크립트가 필요한 권한을 생성하고 구성

#### SQL 문 빌더

**주제 패턴:**
```
testRulesEngineTopic/+/<eventType>
```

**이벤트 유형 옵션:**
- `temperature` - 온도 센서 읽기
- `humidity` - 습도 측정
- `pressure` - 압력 센서 데이터
- `motion` - 동작 감지 이벤트
- `door` - 도어 센서 상태
- `alarm` - 알람 시스템 이벤트
- `status` - 일반 디바이스 상태
- `battery` - 배터리 레벨 보고
- `Custom` - 사용자 정의 이벤트 유형

**SELECT 절 옵션:**
```sql
-- 모든 속성
SELECT * FROM 'testRulesEngineTopic/+/temperature'

-- 특정 속성
SELECT deviceId, timestamp, value FROM 'testRulesEngineTopic/+/temperature'

-- 다중 센서 데이터
SELECT deviceId, timestamp, temperature, humidity FROM 'testRulesEngineTopic/+/temperature'

-- 상태 및 배터리
SELECT deviceId, value, status, battery FROM 'testRulesEngineTopic/+/status'
```

### 규칙 관리 기능

#### 규칙 목록
**포괄적인 규칙 개요:**
- 규칙 이름 및 생성 날짜
- 활성화/비활성화 상태 표시기
- SQL 문 및 액션 수
- 액션 유형 및 대상 목적지

### 자동 IAM 구성

#### IAM 역할 생성
**자동 설정:**
- 존재하지 않는 경우 `IoTRulesEngineRole` 생성
- `iot.amazonaws.com`에 대한 신뢰 정책 구성
- 재게시 액션에 필요한 권한 연결
- IAM 최종 일관성 지연 처리

### 규칙 테스트

#### 테스트 메시지 예시
**온도 이벤트:**
```json
{
  "deviceId": "device123",
  "timestamp": 1642248600000,
  "value": 32.5,
  "unit": "celsius"
}
```

**배터리 알림:**
```json
{
  "deviceId": "sensor456",
  "timestamp": 1642248600000,
  "battery": 15,
  "status": "low_battery"
}
```

### 학습 시나리오

#### 시나리오 1: 온도 모니터링
1. 30°C 이상의 온도 이벤트에 대한 규칙 생성
2. 다양한 온도 값으로 테스트
3. 필터링 동작 관찰
4. 재게시된 메시지 모니터링

#### 시나리오 2: 다중 속성 선택
1. 특정 속성을 선택하는 규칙 생성
2. 입력 vs 출력 메시지 구조 비교
3. 데이터 변환 이해

### 필요한 IAM 권한

**스크립트 사용자용:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "iot:ListTopicRules",
        "iot:GetTopicRule",
        "iot:CreateTopicRule",
        "iot:ReplaceTopicRule",
        "iot:DeleteTopicRule",
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