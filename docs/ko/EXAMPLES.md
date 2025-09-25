# 사용 예제 및 워크플로우

이 문서는 AWS IoT Core - 기초 학습 프로젝트에 대한 자세한 예제와 완전한 워크플로우를 제공합니다.

## 목차

- [완전한 학습 워크플로우](#완전한-학습-워크플로우)
  - [권장 학습 순서](#권장-학습-순서)
- [샘플 데이터 설정 예제](#샘플-데이터-설정-예제)
  - [대화형 경험 안내](#대화형-경험-안내)
  - [디버그 모드 예제](#디버그-모드-예제)
- [IoT 레지스트리 API 탐색기 예제](#iot-레지스트리-api-탐색기-예제)
  - [대화형 메뉴 탐색](#대화형-메뉴-탐색)
  - [Things 목록 예제](#things-목록-예제)
  - [Thing 설명 예제](#thing-설명-예제)
- [인증서 관리자 예제](#인증서-관리자-예제)
  - [완전한 인증서 워크플로우](#완전한-인증서-워크플로우)
  - [외부 인증서 등록 예제](#외부-인증서-등록-예제)
- [MQTT 통신 예제](#mqtt-통신-예제)
  - [인증서 기반 MQTT 세션](#인증서-기반-mqtt-세션)
  - [WebSocket MQTT 세션](#websocket-mqtt-세션)
- [Device Shadow 예제](#device-shadow-예제)
  - [Shadow 상태 동기화](#shadow-상태-동기화)
- [Rules Engine 예제](#rules-engine-예제)
  - [규칙 생성 워크플로우](#규칙-생성-워크플로우)
  - [규칙 테스트 예제](#규칙-테스트-예제)
- [정리 예제](#정리-예제)
  - [안전한 리소스 정리](#안전한-리소스-정리)
- [오류 처리 예제](#오류-처리-예제)
  - [일반적인 오류 시나리오](#일반적인-오류-시나리오)

## 완전한 학습 워크플로우

### 권장 학습 순서

**완전한 종단 간 학습 경로:**

```bash
# 1. 환경 설정
source venv/bin/activate
export AWS_ACCESS_KEY_ID=<your-key>
export AWS_SECRET_ACCESS_KEY=<your-secret>
export AWS_DEFAULT_REGION=us-east-1

# 2. 샘플 IoT 리소스 생성
python setup_sample_data.py

# 3. AWS IoT 레지스트리 API 탐색
python iot_registry_explorer.py

# 4. 인증서 및 정책으로 보안 학습
python certificate_manager.py

# 5. 실시간 MQTT 통신 경험
python mqtt_client_explorer.py
# 또는
python mqtt_websocket_explorer.py

# 6. Shadow를 통한 디바이스 상태 동기화 학습
python device_shadow_explorer.py

# 7. Rules Engine으로 메시지 라우팅 마스터
python iot_rules_explorer.py

# 8. 학습 완료 후 정리
python cleanup_sample_data.py
```

**초기 설정 스크립트를 제외하고, 다른 모든 스크립트는 학습 관심사에 따라 독립적으로 실행할 수 있습니다.**

## 샘플 데이터 설정 예제

### 대화형 경험 안내

**`python setup_sample_data.py`를 실행하면 다음이 표시됩니다:**

```
🚀 AWS IoT 샘플 데이터 설정
============================
이 스크립트는 학습을 위한 샘플 IoT 리소스를 생성합니다:
• 3개 Thing Types (차량 카테고리)
• 4개 Thing Groups (플릿 카테고리)  
• 20개 Things (시뮬레이션된 차량)

⚠️  실제 AWS 리소스를 생성하여 요금이 발생합니다.
예상 비용: Thing 저장소에 대해 ~$0.05

계속하시겠습니까? (y/N): y

🔄 1단계: Thing Types 생성
✅ Thing Type 생성됨: SedanVehicle
✅ Thing Type 생성됨: SUVVehicle  
✅ Thing Type 생성됨: TruckVehicle

🔄 2단계: Thing Groups 생성
✅ Thing Group 생성됨: CustomerFleet
✅ Thing Group 생성됨: TestFleet
✅ Thing Group 생성됨: MaintenanceFleet
✅ Thing Group 생성됨: DealerFleet

🔄 3단계: Things 생성 (20개 차량)
✅ Thing 생성됨: Vehicle-VIN-001 (SedanVehicle → CustomerFleet)
✅ Thing 생성됨: Vehicle-VIN-002 (SUVVehicle → TestFleet)
...
✅ Thing 생성됨: Vehicle-VIN-020 (TruckVehicle → DealerFleet)

📊 요약:
   Thing Types: 3개 생성됨
   Thing Groups: 4개 생성됨  
   Things: 20개 생성됨
   
🎉 샘플 데이터 설정 완료!
```

### 디버그 모드 예제

**`python setup_sample_data.py --debug`로:**

```
🔍 DEBUG: Thing Type 'SedanVehicle' 생성 중
📥 API 호출: create_thing_type
📤 요청: {
  "thingTypeName": "SedanVehicle",
  "thingTypeProperties": {
    "description": "승용 세단 차량",
    "searchableAttributes": ["customerId", "country", "manufacturingDate"]
  }
}
📨 응답: {
  "thingTypeName": "SedanVehicle",
  "thingTypeArn": "arn:aws:iot:us-east-1:123456789012:thingtype/SedanVehicle"
}
⏱️  소요 시간: 0.45초
```

## IoT 레지스트리 API 탐색기 예제

### 대화형 메뉴 탐색

**메인 메뉴:**
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

작업 선택 (1-9): 1
```

### Things 목록 예제

**기본 목록:**
```
🔄 API 호출: list_things
🌐 HTTP 요청: GET https://iot.us-east-1.amazonaws.com/things
ℹ️  설명: AWS 계정의 모든 IoT Things를 검색합니다
📥 입력 매개변수: 없음 (기본 목록)
💡 응답 설명: 이름, 유형 및 속성이 포함된 Thing 객체 배열을 반환합니다

📤 응답 페이로드:
20개 Things 발견:
1. Vehicle-VIN-001 (유형: SedanVehicle)
   속성: customerId=a1b2c3d4-e5f6-7890, country=US, manufacturingDate=2024-03-15
2. Vehicle-VIN-002 (유형: SUVVehicle)  
   속성: customerId=b2c3d4e5-f6g7-8901, country=Germany, manufacturingDate=2024-07-22
...
```

**페이지네이션 사용:**
```
📋 페이지네이션 옵션:
1. 모든 Things 표시
2. 페이지당 최대 결과 설정
3. 뒤로 가기

옵션 선택 (1-3): 2
페이지당 최대 결과 입력 (1-250): 5

🔄 API 호출: list_things  
📥 입력 매개변수: {"maxResults": 5}
📤 응답: 5개 Things 반환됨 (1페이지)

다음 페이지로 계속? (y/N): y
```

**Thing Type별 필터:**
```
📋 필터 옵션:
1. 필터 없음 (모두 표시)
2. Thing Type별 필터
3. 속성별 필터
4. 뒤로 가기

옵션 선택 (1-4): 2

사용 가능한 Thing Types:
1. SedanVehicle
2. SUVVehicle  
3. TruckVehicle

Thing Type 선택 (1-3): 1

🔄 API 호출: list_things
📥 입력 매개변수: {"thingTypeName": "SedanVehicle"}
📤 응답: 7개 SedanVehicle Things 발견
```

### Thing 설명 예제

**Thing 선택:**
```
Thing 이름 입력: Vehicle-VIN-001

🔄 API 호출: describe_thing
🌐 HTTP 요청: GET https://iot.us-east-1.amazonaws.com/things/Vehicle-VIN-001
📥 입력 매개변수: {"thingName": "Vehicle-VIN-001"}

📤 응답 페이로드:
{
  "thingName": "Vehicle-VIN-001",
  "thingId": "12345678-1234-1234-1234-123456789012",
  "thingArn": "arn:aws:iot:us-east-1:123456789012:thing/Vehicle-VIN-001",
  "thingTypeName": "SedanVehicle",
  "attributes": {
    "customerId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "country": "US", 
    "manufacturingDate": "2024-03-15"
  },
  "version": 1
}
```

## 인증서 관리자 예제

### 완전한 인증서 워크플로우

**옵션 1: AWS IoT 인증서 생성 및 Thing에 연결**

```
📋 메인 메뉴:
1. AWS IoT 인증서 생성 및 Thing에 연결 (+ 선택적 정책)
2. 외부 인증서 등록 및 Thing에 연결 (+ 선택적 정책)  
3. 기존 인증서에 정책 연결
4. 인증서에서 정책 분리
5. 인증서 활성화/비활성화
6. 종료

옵션 선택 (1-6): 1

📚 학습 순간: 인증서 생성 및 Thing 연결
AWS IoT 인증서를 생성하면 디바이스에 대한 고유한 디지털 신원이 설정됩니다...

계속하려면 Enter를 누르세요...

📱 사용 가능한 Things (20개 발견):
   1. Vehicle-VIN-001 (유형: SedanVehicle)
   2. Vehicle-VIN-002 (유형: SUVVehicle)
   ...
   10. Vehicle-VIN-010 (유형: TruckVehicle)
   ... 그리고 10개 더

📋 옵션:
   • 번호 입력 (1-20)으로 Thing 선택
   • 'all' 입력하여 모든 Things 보기  
   • 'manual' 입력하여 Thing 이름 수동 입력

선택: 1
✅ 선택된 Thing: Vehicle-VIN-001
```

**인증서 생성 프로세스:**
```
🔐 1단계: X.509 인증서 생성
--------------------------------------------------
ℹ️  X.509 인증서는 AWS IoT에서 디바이스 인증에 사용됩니다
ℹ️  각 인증서에는 공개/개인 키 쌍이 포함됩니다

🔍 API 세부사항:
   작업: create_keys_and_certificate
   HTTP 메서드: POST
   API 경로: /keys-and-certificate
   설명: 공개/개인 키 쌍으로 새 X.509 인증서를 생성합니다
   입력 매개변수: setAsActive: true (인증서를 즉시 활성화)
   예상 출력: certificateArn, certificateId, certificatePem, keyPair

🔄 인증서 및 키 쌍 생성 중...
📥 입력: {"setAsActive": true}
✅ 인증서 및 키 쌍 생성이 성공적으로 완료되었습니다

📋 인증서 세부사항:
   인증서 ID: abc123def456789ghi012jkl345mno678pqr901stu234vwx567yz890
   인증서 ARN: arn:aws:iot:us-east-1:123456789012:cert/abc123def456789ghi012jkl345mno678pqr901stu234vwx567yz890
   상태: ACTIVE

   📄 인증서: certificates/Vehicle-VIN-001/abc123def456789ghi012jkl345mno678pqr901stu234vwx567yz890.crt
   🔐 개인 키: certificates/Vehicle-VIN-001/abc123def456789ghi012jkl345mno678pqr901stu234vwx567yz890.key
   🔑 공개 키: certificates/Vehicle-VIN-001/abc123def456789ghi012jkl345mno678pqr901stu234vwx567yz890.pub

💾 인증서 파일이 다음에 저장됨: certificates/Vehicle-VIN-001

🔑 생성된 인증서 구성 요소:
   • 공개 키 (AWS IoT용)
   • 개인 키 (디바이스에서 보안 유지)
   • 인증서 PEM (디바이스 인증용)
```

**인증서-Thing 연결:**
```
🔐 2단계: 인증서를 Thing에 연결
--------------------------------------------------
ℹ️  인증서는 디바이스 인증을 위해 Things에 연결되어야 합니다
ℹ️  이는 인증서와 IoT 디바이스 간의 보안 관계를 생성합니다
ℹ️  인증서가 다음에 연결됩니다: Vehicle-VIN-001

🔗 인증서를 Thing에 연결 중: Vehicle-VIN-001

🔍 API 세부사항:
   작업: attach_thing_principal
   HTTP 메서드: PUT
   API 경로: /things/Vehicle-VIN-001/principals
   설명: 인증을 위해 인증서(주체)를 Thing에 연결합니다
   입력 매개변수: thingName: Vehicle-VIN-001, principal: arn:aws:iot:...
   예상 출력: 성공 시 빈 응답

🔄 인증서를 Vehicle-VIN-001에 연결 중...
✅ Vehicle-VIN-001에 인증서 연결 완료
✅ 인증서가 Vehicle-VIN-001에 성공적으로 연결되었습니다
   ℹ️  Thing이 이제 이 인증서를 인증에 사용할 수 있습니다
```

**정책 생성:**
```
🔐 3단계: IoT 정책 관리
--------------------------------------------------
ℹ️  IoT 정책은 인증서가 수행할 수 있는 작업을 정의합니다
ℹ️  새 정책을 생성하거나 기존 정책을 사용할 수 있습니다

📝 기존 정책을 찾을 수 없습니다. 새 정책을 생성합니다...

새 정책 이름 입력: BasicDevicePolicy
✅ 정책 이름 'BasicDevicePolicy'를 사용할 수 있습니다

📝 정책 템플릿:
1. 기본 디바이스 정책 (연결, 게시, 구독)
2. 읽기 전용 정책 (연결, 구독만)
3. 사용자 정의 정책 (자체 JSON 입력)

정책 템플릿 선택 (1-3): 1

⚠️  프로덕션 보안 참고:
   이 정책은 시연 목적으로 'Resource': '*'를 사용합니다.
   프로덕션에서는 특정 리소스 ARN과 정책 변수를
   ${iot:Connection.Thing.ThingName}과 같이 사용하여 디바이스 액세스를
   특정 리소스로만 제한하세요. 정책 변수는
   이 기본 학습 경로의 범위를 벗어납니다.

📄 생성될 정책:
   이름: BasicDevicePolicy
   문서: {
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

🔄 정책 'BasicDevicePolicy' 생성 중...
✅ 정책 'BasicDevicePolicy'가 성공적으로 생성되었습니다
```

**정책 연결:**
```
🔐 4단계: 인증서에 정책 연결
--------------------------------------------------
ℹ️  정책은 권한을 부여하기 위해 인증서에 연결되어야 합니다
ℹ️  정책 없이는 인증서가 IoT 작업을 수행할 수 없습니다

🔗 정책 'BasicDevicePolicy'를 인증서에 연결 중

🔄 정책을 인증서에 연결 중...
✅ 정책 'BasicDevicePolicy'가 인증서에 연결되었습니다
   ℹ️  인증서가 이제 정책에 정의된 권한을 갖습니다
```

**최종 요약:**
```
🔐 5단계: 설정 완료! 🎉
--------------------------------------------------
📊 생성된 항목 요약:
   🔐 인증서 ID: abc123def456789ghi012jkl345mno678pqr901stu234vwx567yz890
   📱 연결된 Thing: Vehicle-VIN-001
   📄 연결된 정책: BasicDevicePolicy

🔍 이제 탐색할 수 있는 것:
   • iot_registry_explorer.py를 사용하여 인증서 보기
   • Thing을 확인하여 연결된 인증서 보기
   • 정책 권한 검토

💡 주요 학습 포인트:
   • 인증서는 디바이스 신원과 인증을 제공합니다
   • Things는 AWS에서 IoT 디바이스를 나타냅니다
   • 정책은 인증서가 수행할 수 있는 작업을 정의합니다
   • 세 가지 모두 안전한 IoT 통신을 위해 함께 작동합니다
```

### 외부 인증서 등록 예제

**OpenSSL 인증서 생성:**
```
📜 외부 인증서 등록 워크플로우
==================================================

📋 인증서 옵션:
1. 기존 인증서 파일 사용
2. OpenSSL로 샘플 인증서 생성

옵션 선택 (1-2): 2

🔐 OpenSSL 단계: OpenSSL로 샘플 인증서 생성
--------------------------------------------------
ℹ️  학습 목적으로 자체 서명 인증서를 생성합니다
ℹ️  프로덕션에서는 신뢰할 수 있는 인증 기관의 인증서를 사용하세요

인증서 이름 입력 [기본값: sample-device]: my-test-device

🔑 인증서 파일 생성:
   개인 키: sample-certs/my-test-device.key
   인증서: sample-certs/my-test-device.crt

🔄 OpenSSL 명령 실행 중...
📥 명령: openssl req -x509 -newkey rsa:2048 -keyout sample-certs/my-test-device.key -out sample-certs/my-test-device.crt -days 365 -nodes -subj /CN=my-test-device/O=AWS IoT Learning/C=US

✅ 인증서가 성공적으로 생성되었습니다

📊 인증서 세부사항:
   • 유형: 자체 서명 X.509
   • 키 크기: 2048비트 RSA
   • 유효성: 365일
   • 주체: CN=my-test-device, O=AWS IoT Learning, C=US
```

## MQTT 통신 예제

### 인증서 기반 MQTT 세션

**디바이스 선택:**
```
🔍 인증서가 있는 Things 검색 중...
📋 인증서가 있는 3개 Things 발견:
   1. Vehicle-VIN-001 → 인증서: abc123def456...
   2. Vehicle-VIN-002 → 인증서: def456ghi789...
   3. Vehicle-VIN-003 → 인증서: ghi789jkl012...

Thing 선택 (1-3): 1
✅ 선택됨: Vehicle-VIN-001

🔍 인증서 검증:
   📄 인증서 파일: ✅ 발견됨
   🔐 개인 키 파일: ✅ 발견됨
   📱 Thing 연결: ✅ 확인됨
```

**연결 설정:**
```
🔐 1단계: Shadow 작업을 위한 MQTT 연결 설정
--------------------------------------------------
🔗 Shadow 연결 매개변수:
   클라이언트 ID: Vehicle-VIN-001-mqtt-a1b2c3d4
   Thing 이름: Vehicle-VIN-001
   엔드포인트: a1b2c3d4e5f6g7-ats.iot.us-east-1.amazonaws.com
   포트: 8883
   프로토콜: TLS를 통한 MQTT 3.1.1
   인증: X.509 인증서
   Shadow 유형: 클래식 Shadow

🔄 AWS IoT Core에 연결 중...
✅ AWS IoT Core에 성공적으로 연결되었습니다

======================================================================
🔔 SHADOW 연결 설정됨 [14:30:10.123]
======================================================================
상태: AWS IoT Core에 성공적으로 연결됨
클라이언트 ID: Vehicle-VIN-001-mqtt-a1b2c3d4
Thing 이름: Vehicle-VIN-001
엔드포인트: a1b2c3d4e5f6g7-ats.iot.us-east-1.amazonaws.com
Shadow 유형: 클래식 Shadow
클린 세션: True
Keep Alive: 30초
TLS 버전: 1.2
인증서 인증: X.509 상호 TLS
======================================================================
```

**대화형 MQTT 명령:**
```
📡 MQTT 클라이언트 연결됨 - 명령을 보려면 'help' 입력

📡 MQTT> help
사용 가능한 명령:
  sub <topic>              - 주제 구독 (QoS 0)
  sub1 <topic>             - 주제 구독 (QoS 1)
  unsub <topic>            - 주제 구독 해제
  pub <topic> <message>    - 메시지 게시 (QoS 0)
  pub1 <topic> <message>   - 메시지 게시 (QoS 1)
  json <topic> key=val...  - JSON 메시지 게시
  test                     - 테스트 메시지 전송
  status                   - 연결 상태 표시
  messages                 - 메시지 기록 표시
  debug                    - 연결 진단
  quit                     - 클라이언트 종료

📡 MQTT> sub device/+/temperature
✅ [14:30:15.456] device/+/temperature 구독됨 (QoS: 0)

📡 MQTT> pub device/sensor/temperature 23.5
✅ [14:30:20.789] 게시됨
   📤 주제: device/sensor/temperature
   🏷️  QoS: 0 | 패킷 ID: 1
   📊 크기: 4바이트

======================================================================
🔔 수신 메시지 #1 [14:30:20.890]
======================================================================
📥 주제: device/sensor/temperature
🏷️  QoS: 0 (최대 한 번)
📊 페이로드 크기: 4바이트
💬 메시지: 23.5
======================================================================

📡 MQTT> json device/data temperature=25.0 humidity=60 status=online
✅ [14:30:25.123] JSON 게시됨
   📤 주제: device/data
   🏷️  QoS: 0 | 패킷 ID: 2
   📊 크기: 52바이트
   💬 JSON: {"temperature": 25.0, "humidity": 60, "status": "online"}

📡 MQTT> status
🔍 연결 상태:
   📡 상태: 연결됨
   🏷️  클라이언트 ID: Vehicle-VIN-001-mqtt-a1b2c3d4
   🌐 엔드포인트: a1b2c3d4e5f6g7-ats.iot.us-east-1.amazonaws.com
   📊 게시된 메시지: 2
   📥 수신된 메시지: 1
   📋 활성 구독: 1
      • device/+/temperature (QoS: 0)
```

### WebSocket MQTT 세션

**자격 증명 검증:**
```
🌐 WebSocket MQTT 클라이언트
========================
🔍 AWS 자격 증명 검증 중...
✅ AWS 자격 증명이 검증되었습니다
   계정 ID: 123456789012
   리전: us-east-1

🔗 WebSocket 연결 매개변수:
   엔드포인트: wss://a1b2c3d4e5f6g7-ats.iot.us-east-1.amazonaws.com/mqtt
   인증: AWS SigV4
   클라이언트 ID: websocket-client-a1b2c3d4
   프로토콜: WebSocket을 통한 MQTT

🔄 WebSocket 연결 설정 중...
✅ WebSocket MQTT 연결이 설정되었습니다

📡 WebSocket MQTT> sub alerts/#
✅ [14:35:10.123] alerts/# 구독됨 (QoS: 0)

📡 WebSocket MQTT> pub alerts/temperature "높은 온도가 감지되었습니다"
✅ [14:35:15.456] 게시됨
   📤 주제: alerts/temperature
   💬 메시지: 높은 온도가 감지되었습니다
```

## Device Shadow 예제

### Shadow 상태 동기화

**초기 Shadow 설정:**
```
🌟 Device Shadow 탐색기
=========================
🔍 인증서가 있는 Things 검색 중...
✅ 선택된 Thing: Vehicle-VIN-001

📱 로컬 디바이스 상태 설정:
   📄 상태 파일: certificates/Vehicle-VIN-001/device_state.json
   📊 초기 상태: {
     "temperature": 22.5,
     "humidity": 45.0,
     "status": "online",
     "firmware_version": "1.0.0"
   }

🔄 섀도우 작업을 위해 AWS IoT에 연결 중...
✅ Shadow 연결이 설정되었습니다

🌟 2단계: Shadow 주제 구독
--------------------------------------------------
📋 클래식 Shadow 주제:
   ✅ $aws/things/Vehicle-VIN-001/shadow/get/accepted
   ✅ $aws/things/Vehicle-VIN-001/shadow/get/rejected
   ✅ $aws/things/Vehicle-VIN-001/shadow/update/accepted
   ✅ $aws/things/Vehicle-VIN-001/shadow/update/rejected
   ✅ $aws/things/Vehicle-VIN-001/shadow/update/delta

✅ 모든 5개 섀도우 주제에 성공적으로 구독되었습니다

📖 Shadow 주제 설명:
   • get/accepted - Shadow 문서 검색 성공
   • get/rejected - Shadow 문서 검색 실패
   • update/accepted - Shadow 업데이트 성공
   • update/rejected - Shadow 업데이트 실패
   • update/delta - 원하는 상태 ≠ 보고된 상태 (조치 필요)
```

**Shadow 작업:**
```
🌟 Shadow> get
🔄 현재 섀도우 문서 요청 중...

======================================================================
🌟 SHADOW 메시지 수신됨 [14:40:10.123]
======================================================================
✅ SHADOW GET 승인됨
   📊 버전: 1
   ⏰ 타임스탬프: 1642248610
   📡 현재 Shadow: {
     "state": {
       "reported": {
         "temperature": 22.5,
         "humidity": 45.0,
         "status": "online"
       }
     },
     "metadata": {
       "reported": {
         "temperature": {"timestamp": 1642248500},
         "humidity": {"timestamp": 1642248500},
         "status": {"timestamp": 1642248500}
       }
     },
     "version": 1,
     "timestamp": 1642248610
   }
======================================================================

🌟 Shadow> desire temperature=25.0 status=active
🔄 원하는 상태 설정 중 (클라우드/앱 요청 시뮬레이션)...

======================================================================
🌟 SHADOW 메시지 수신됨 [14:40:15.456]
======================================================================
🔄 SHADOW 델타 수신됨
   📝 설명: 원하는 상태가 보고된 상태와 다릅니다
   📊 버전: 2
   🔄 필요한 변경사항: {
     "temperature": 25.0,
     "status": "active"
   }

🔍 상태 비교:
   📱 로컬 상태: {
     "temperature": 22.5,
     "status": "online"
   }
   🔄 델타: {
     "temperature": 25.0,
     "status": "active"
   }

⚠️  차이점 발견:
   • temperature: 22.5 → 25.0
   • status: online → active

이러한 변경사항을 로컬 디바이스에 적용하시겠습니까? (y/N): y
✅ 로컬 상태가 성공적으로 업데이트되었습니다
📡 업데이트된 상태를 섀도우에 자동으로 보고 중...

======================================================================
🌟 SHADOW 메시지 수신됨 [14:40:18.789]
======================================================================
✅ SHADOW 업데이트 승인됨
   📊 새 버전: 3
   ⏰ 타임스탬프: 1642248618
   📡 업데이트된 보고됨: {
     "temperature": 25.0,
     "humidity": 45.0,
     "status": "active",
     "firmware_version": "1.0.0"
   }
======================================================================
```

**대화형 상태 편집:**
```
🌟 Shadow> edit
📝 로컬 상태 편집기
현재 상태: {
  "temperature": 25.0,
  "humidity": 45.0,
  "status": "active",
  "firmware_version": "1.0.0"
}

옵션:
1. 개별 값 편집
2. 전체 상태를 JSON으로 교체
3. 취소

옵션 선택 (1-3): 1

현재 값:
   1. temperature: 25.0
   2. humidity: 45.0
   3. status: active
   4. firmware_version: 1.0.0
   5. 새 키 추가
   6. 편집 완료

편집할 항목 선택 (1-6): 2

'humidity' 편집 중 (현재: 45.0)
새 값 (또는 현재 값을 유지하려면 Enter): 50.0
✅ humidity = 50.0으로 업데이트됨

편집할 항목 선택 (1-6): 6
✅ 편집 완료

🌟 Shadow> report
🔄 로컬 상태를 섀도우에 보고 중...

======================================================================
🌟 SHADOW 메시지 수신됨 [14:40:25.123]
======================================================================
✅ SHADOW 업데이트 승인됨
   📊 새 버전: 4
   📡 업데이트된 보고됨: {
     "temperature": 25.0,
     "humidity": 50.0,
     "status": "active",
     "firmware_version": "1.0.0"
   }
======================================================================
```

## Rules Engine 예제

### 규칙 생성 워크플로우

**규칙 생성 메뉴:**
```
⚙️ IoT Rules Engine 탐색기
============================
📋 메인 메뉴:
1. 모든 IoT Rules 목록
2. 특정 IoT Rule 설명
3. 새 IoT Rule 생성
4. IoT Rule 관리 (활성화/비활성화/삭제)
5. MQTT로 IoT Rule 테스트
6. 종료

옵션 선택 (1-6): 3

🔧 규칙 생성 마법사
======================
규칙 이름 입력: TemperatureAlert
✅ 규칙 이름 'TemperatureAlert'를 사용할 수 있습니다

📊 이벤트 유형 선택:
1. temperature - 온도 센서 읽기
2. humidity - 습도 측정
3. pressure - 압력 센서 데이터
4. motion - 동작 감지 이벤트
5. door - 도어 센서 상태
6. alarm - 알람 시스템 이벤트
7. status - 일반 디바이스 상태
8. battery - 배터리 레벨 보고
9. Custom - 사용자 정의 이벤트 유형

이벤트 유형 선택 (1-9): 1
✅ 선택된 이벤트 유형: temperature
```

**SQL 문 구축:**
```
🔧 SQL 문 빌더
=======================
📥 주제 패턴: testRulesEngineTopic/+/temperature

📝 SELECT 절 옵션:
1. SELECT * (모든 속성)
2. SELECT deviceId, timestamp, value (특정 속성)
3. SELECT deviceId, timestamp, temperature, humidity (다중 센서)
4. 사용자 정의 SELECT 절

옵션 선택 (1-4): 2
✅ SELECT 절: deviceId, timestamp, value

🔍 WHERE 절 (선택사항):
WHERE 조건 입력 (또는 필터 없음은 Enter): value > 30
✅ WHERE 절: value > 30

📝 완전한 SQL 문:
SELECT deviceId, timestamp, value 
FROM 'testRulesEngineTopic/+/temperature' 
WHERE value > 30

🎯 액션 구성:
📤 재게시 대상 주제: processed/temperature
🔑 IAM 역할: IoTRulesEngineRole (필요한 경우 생성됨)

규칙 생성을 확인하시겠습니까? (y/N): y
```

**자동 IAM 설정:**
```
🔧 Rules Engine용 IAM 역할 설정 중...
🔍 역할 'IoTRulesEngineRole'이 존재하는지 확인 중...
❌ 역할을 찾을 수 없습니다. 새 역할을 생성합니다...

🔄 IAM 역할 'IoTRulesEngineRole' 생성 중...
✅ IAM 역할이 성공적으로 생성되었습니다

🔄 역할에 정책 연결 중...
✅ 정책이 성공적으로 연결되었습니다

⏳ IAM 최종 일관성 대기 중 (5초)...

🔄 IoT Rule 'TemperatureAlert' 생성 중...
✅ 규칙 'TemperatureAlert'가 성공적으로 생성되었습니다!

📊 규칙 요약:
   이름: TemperatureAlert
   상태: 활성화됨
   SQL: SELECT deviceId, timestamp, value FROM 'testRulesEngineTopic/+/temperature' WHERE value > 30
   액션: 1개 (processed/temperature로 재게시)
```

### 규칙 테스트 예제

**테스트 설정:**
```
📋 메인 메뉴:
5. MQTT로 IoT Rule 테스트

옵션 선택 (1-6): 5

🧪 규칙 테스트 모드
===================
📋 사용 가능한 규칙:
1. TemperatureAlert - 활성화됨
2. BatteryMonitor - 비활성화됨

테스트할 규칙 선택 (1-2): 1
✅ 선택된 규칙: TemperatureAlert

📖 규칙 분석:
   SQL: SELECT deviceId, timestamp, value FROM 'testRulesEngineTopic/+/temperature' WHERE value > 30
   📥 주제 패턴: testRulesEngineTopic/+/temperature
   🔍 WHERE 조건: value > 30
   📤 출력 주제: processed/temperature

🔗 테스트를 위한 MQTT 연결 설정 중...
✅ 인증서 인증으로 AWS IoT에 연결되었습니다
✅ 출력 주제에 구독됨: processed/temperature
```

**대화형 메시지 테스트:**
```
🧪 테스트 메시지 생성기
========================
🧪 테스트 메시지 #1

📥 주제 패턴: testRulesEngineTopic/+/temperature
이 메시지가 주제 패턴과 일치해야 합니까? (y/n): y

🔍 WHERE 조건: value > 30
이 메시지가 WHERE 조건과 일치해야 합니까? (y/n): y

📝 생성된 테스트 메시지:
📡 주제: testRulesEngineTopic/device123/temperature
💬 페이로드: {
  "deviceId": "test-device-123",
  "timestamp": 1642248600000,
  "value": 35.0,
  "unit": "celsius"
}

🔮 예측: 규칙이 트리거되어야 함 (주제 일치 AND value > 30)

📤 테스트 메시지 게시 중...
⏳ 규칙 처리를 위해 3초 대기 중...

======================================================================
🔔 규칙 출력 수신됨 [14:45:10.123]
======================================================================
📤 출력 주제: processed/temperature
💬 처리된 메시지: {
  "deviceId": "test-device-123",
  "timestamp": 1642248600000,
  "value": 35.0
}
✅ 규칙 'TemperatureAlert'가 메시지를 처리하고 전달했습니다!
======================================================================

🧪 테스트 메시지 #2

📥 주제 패턴: testRulesEngineTopic/+/temperature
이 메시지가 주제 패턴과 일치해야 합니까? (y/n): y

🔍 WHERE 조건: value > 30
이 메시지가 WHERE 조건과 일치해야 합니까? (y/n): n

📝 생성된 테스트 메시지:
📡 주제: testRulesEngineTopic/sensor456/temperature
💬 페이로드: {
  "deviceId": "test-sensor-456",
  "timestamp": 1642248605000,
  "value": 25.0,
  "unit": "celsius"
}

🔮 예측: 규칙이 트리거되지 않아야 함 (주제 일치하지만 value <= 30)

📤 테스트 메시지 게시 중...
⏳ 규칙 처리를 위해 3초 대기 중...

❌ 규칙 출력이 수신되지 않음 (예상대로 - WHERE 조건이 충족되지 않음)
✅ 규칙이 메시지를 올바르게 필터링했습니다!
```

## 정리 예제

### 안전한 리소스 정리

**정리 확인:**
```
🧹 AWS IoT 샘플 데이터 정리
==============================
이 스크립트는 setup_sample_data.py로 생성된 샘플 리소스만 안전하게 제거합니다:

✅ 삭제해도 안전함:
   • 20개 Things: Vehicle-VIN-001부터 Vehicle-VIN-020까지
   • 3개 Thing Types: SedanVehicle, SUVVehicle, TruckVehicle
   • 4개 Thing Groups: CustomerFleet, TestFleet, MaintenanceFleet, DealerFleet
   • 연결된 인증서 및 로컬 파일

❌ 삭제하지 않음:
   • 기존 Things, Thing Types 또는 Thing Groups
   • 샘플이 아닌 Things에 연결된 인증서
   • IoT 정책 (수동 검토 필요)

⚠️  이 작업은 되돌릴 수 없습니다.
계속하시겠습니까? (y/N): y
```

**정리 프로세스:**
```
🔍 1단계: 샘플 리소스 검색 중...
📋 발견된 리소스:
   Things: 20개 샘플 Things 발견
   Thing Types: 3개 샘플 Thing Types 발견
   Thing Groups: 4개 샘플 Thing Groups 발견
   인증서: 샘플 Things에 연결된 15개 인증서

🧹 2단계: 인증서 정리...
🔄 Thing 처리 중: Vehicle-VIN-001
   🔍 연결된 1개 인증서 발견
   🔓 인증서 abc123def456에서 정책 분리 중...
   🔗 Thing에서 인증서 분리 중...
   🔴 인증서 비활성화 중...
   🗑️  인증서 삭제 중...
   📁 로컬 인증서 파일 제거 중...
   ✅ 인증서 정리 완료

🧹 3단계: Thing 정리...
🔄 Thing 삭제 중: Vehicle-VIN-001...
✅ Thing이 성공적으로 삭제되었습니다
...
✅ 모든 20개 Things가 성공적으로 삭제되었습니다

🧹 4단계: Thing Group 정리...
🔄 Thing Group 삭제 중: CustomerFleet...
✅ Thing Group이 성공적으로 삭제되었습니다
...
✅ 모든 4개 Thing Groups가 성공적으로 삭제되었습니다

🧹 5단계: Thing Type 정리...
⚠️  AWS는 Thing Types 삭제 전 5분 대기를 요구합니다
📋 옵션:
1. 5분 대기 후 자동 삭제
2. 삭제 건너뛰기 (사용 중단만)
3. 즉시 삭제 시도 (실패할 수 있음)

옵션 선택 (1-3): 1

🔄 Thing Type 사용 중단 중: SedanVehicle...
✅ Thing Type이 사용 중단되었습니다
⏳ AWS 전파를 위해 5분 대기 중...
🔄 Thing Type 삭제 중: SedanVehicle...
✅ Thing Type이 성공적으로 삭제되었습니다
...

📊 정리 요약:
   ✅ Things 삭제됨: 20개
   ✅ 인증서 삭제됨: 15개
   ✅ Thing Groups 삭제됨: 4개
   ✅ Thing Types 삭제됨: 3개
   ✅ 로컬 파일 제거됨: 45개

🎉 정리 완료! 모든 샘플 리소스가 제거되었습니다.
💡 AWS 계정이 이제 깨끗하며 이러한 리소스에 대한 요금이 더 이상 발생하지 않습니다.
```

## 오류 처리 예제

### 일반적인 오류 시나리오

**인증서를 찾을 수 없음 오류:**
```
❌ MQTT 연결 설정 오류
Thing에 대한 인증서 파일을 찾을 수 없음: Vehicle-VIN-001

💡 해결책:
1. 먼저 certificate_manager.py 실행
2. 이 Thing에 인증서를 생성하고 연결
3. certificates/Vehicle-VIN-001/에 인증서 파일이 존재하는지 확인

🔍 디버그 단계:
   ls -la certificates/Vehicle-VIN-001/
   python certificate_manager.py
```

**권한 거부 오류:**
```
❌ 오류: AccessDeniedException - 사용자가 iot:CreateThing 수행 권한이 없습니다

💡 해결책:
AWS 자격 증명에 IoT 권한이 필요합니다. IAM 사용자에 이 정책을 추가하세요:
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": "iot:*",
    "Resource": "*"
  }]
}

🔍 현재 권한 확인:
   aws sts get-caller-identity
   aws iam list-attached-user-policies --user-name <your-username>
```

**MQTT 연결 시간 초과:**
```
❌ MQTT 연결 실패: 연결 시간 초과

💡 문제 해결 단계:
1. 네트워크 연결 확인:
   ping a1b2c3d4e5f6g7-ats.iot.us-east-1.amazonaws.com

2. 인증서가 활성화되어 있는지 확인:
   python iot_registry_explorer.py
   # 옵션 2 선택 (인증서 목록)

3. 방화벽 확인 (포트 8883이 열려 있어야 함):
   telnet a1b2c3d4e5f6g7-ats.iot.us-east-1.amazonaws.com 8883

4. 인증서-Thing 연결 확인:
   python iot_registry_explorer.py
   # 옵션 5 선택 (Thing 설명)
```

이러한 예제는 설정부터 정리까지의 완전한 학습 여정을 보여주며, 스크립트를 사용할 때 볼 수 있는 실제 상호작용과 출력을 보여줍니다.