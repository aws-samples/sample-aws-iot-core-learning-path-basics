# Detailed Script Documentation

This document provides comprehensive documentation for all learning scripts in the AWS IoT Core - Basics project.

## Table of Contents

- [IoT Registry API Explorer](#iot-registry-api-explorer)
  - [Purpose](#purpose)
  - [How to Run](#how-to-run)
  - [Interactive Menu System](#interactive-menu-system)
  - [Supported APIs with Learning Details](#supported-apis-with-learning-details)
  - [Learning Features](#learning-features)
  - [Error Learning](#error-learning)
- [Certificate & Policy Manager](#certificate--policy-manager)
  - [Purpose](#purpose-1)
  - [How to Run](#how-to-run-1)
  - [Interactive Main Menu](#interactive-main-menu)
  - [Option 1: Complete Certificate Workflow](#option-1-complete-certificate-workflow)
  - [Option 2: External Certificate Registration](#option-2-external-certificate-registration)
  - [Option 3: Policy Attachment Workflow](#option-3-policy-attachment-workflow)
  - [Option 4: Policy Detachment Workflow](#option-4-policy-detachment-workflow)
  - [Option 5: Certificate Status Management](#option-5-certificate-status-management)
  - [Certificate Management Deep Dive](#certificate-management-deep-dive)
  - [Policy Management Deep Dive](#policy-management-deep-dive)
  - [API Learning Features](#api-learning-features)
  - [Certificate Options Explained](#certificate-options-explained)
  - [Error Learning Scenarios](#error-learning-scenarios)
- [MQTT Communication](#mqtt-communication)
  - [Purpose](#purpose-2)
  - [Two MQTT Options Available](#two-mqtt-options-available)
  - [Certificate-Based MQTT Client](#certificate-based-mqtt-client)
  - [WebSocket MQTT Client](#websocket-mqtt-client)
  - [MQTT Protocol Learning](#mqtt-protocol-learning)
- [Device Shadow Explorer](#device-shadow-explorer)
  - [Purpose](#purpose-3)
  - [How to Run](#how-to-run-2)
  - [Prerequisites](#prerequisites)
  - [Interactive Device Shadow Learning](#interactive-device-shadow-learning)
  - [Key Learning Features](#key-learning-features)
  - [Shadow Message Analysis](#shadow-message-analysis)
  - [Learning Scenarios](#learning-scenarios)
  - [Required IAM Permissions](#required-iam-permissions)
- [IoT Rules Engine Explorer](#iot-rules-engine-explorer)
  - [Purpose](#purpose-4)
  - [How to Run](#how-to-run-3)
  - [Prerequisites](#prerequisites-1)
  - [Interactive Rules Engine Learning](#interactive-rules-engine-learning)
  - [Key Learning Features](#key-learning-features-1)
  - [Rule Management Features](#rule-management-features)
  - [Automatic IAM Configuration](#automatic-iam-configuration)
  - [Testing Your Rules](#testing-your-rules)
  - [Learning Scenarios](#learning-scenarios-1)
  - [Required IAM Permissions](#required-iam-permissions-1)

## IoT Registry API Explorer

### Purpose
Interactive tool for learning AWS IoT Registry APIs through real API calls with detailed explanations. This script teaches you the Control Plane operations used to manage IoT devices, certificates, and policies.

**Note**: AWS IoT Core provides many APIs across device management and security. This explorer focuses on 8 core Registry APIs that are essential for understanding IoT device lifecycle management. For complete API details, see the [AWS IoT Registry API Reference](https://docs.aws.amazon.com/iot/latest/apireference/API_Operations_AWS_IoT.html).

### How to Run

**Basic Usage:**
```bash
python iot_registry_explorer.py
```

**With Debug Mode (enhanced API details):**
```bash
python iot_registry_explorer.py --debug
```

### Interactive Menu System

When you run the script, you'll see:
```
📋 Available Operations:
1. List Things
2. List Certificates
3. List Thing Groups
4. List Thing Types
5. Describe Thing
6. Describe Thing Group
7. Describe Thing Type
8. Describe Endpoint
9. Exit

Select operation (1-9):
```

### Supported APIs with Learning Details

#### 1. List Things
- **Purpose**: Retrieve all IoT devices in your account
- **HTTP**: `GET /things`
- **Learn**: Device discovery with pagination and filtering options
- **Options Available**:
  - **Basic listing**: Shows all Things
  - **Pagination**: Retrieve Things in smaller batches (specify max results per page)
  - **Filter by Thing Type**: Find vehicles of specific categories (e.g., SedanVehicle)
  - **Filter by Attribute**: Find vehicles with specific attributes (e.g., country=USA)
- **Output**: Array of Thing objects with names, types, attributes
- **📚 API Reference**: [ListThings](https://docs.aws.amazon.com/iot/latest/apireference/API_ListThings.html)

#### 2. List Certificates
- **Purpose**: View all X.509 certificates for device authentication
- **HTTP**: `GET /certificates`
- **Learn**: Certificate lifecycle, status management
- **Output**: Certificate IDs, ARNs, creation dates, status
- **📚 API Reference**: [ListCertificates](https://docs.aws.amazon.com/iot/latest/apireference/API_ListCertificates.html)

#### 3. List Thing Groups
- **Purpose**: See device organization and hierarchies
- **HTTP**: `GET /thing-groups`
- **Learn**: Device grouping strategies, management at scale
- **Output**: Group names, ARNs, descriptions
- **📚 API Reference**: [ListThingGroups](https://docs.aws.amazon.com/iot/latest/apireference/API_ListThingGroups.html)

#### 4. List Thing Types
- **Purpose**: View device templates and categories
- **HTTP**: `GET /thing-types`
- **Learn**: Device classification, attribute schemas
- **Output**: Type names, descriptions, searchable attributes
- **📚 API Reference**: [ListThingTypes](https://docs.aws.amazon.com/iot/latest/apireference/API_ListThingTypes.html)

#### 5. Describe Thing
- **Purpose**: Get detailed information about a specific device
- **HTTP**: `GET /things/{thingName}`
- **Input Required**: Thing name (e.g., "Vehicle-VIN-001")
- **Learn**: Device metadata, attributes, relationships
- **Output**: Complete Thing details, version, ARN
- **📚 API Reference**: [DescribeThing](https://docs.aws.amazon.com/iot/latest/apireference/API_DescribeThing.html)

#### 6. Describe Thing Group
- **Purpose**: View group details and properties
- **HTTP**: `GET /thing-groups/{thingGroupName}`
- **Input Required**: Group name (e.g., "CustomerFleet")
- **Learn**: Group hierarchies, policies, attributes
- **Output**: Group properties, parent/child relationships
- **📚 API Reference**: [DescribeThingGroup](https://docs.aws.amazon.com/iot/latest/apireference/API_DescribeThingGroup.html)

#### 7. Describe Thing Type
- **Purpose**: See type specifications and templates
- **HTTP**: `GET /thing-types/{thingTypeName}`
- **Input Required**: Type name (e.g., "SedanVehicle")
- **Learn**: Type definitions, searchable attributes
- **Output**: Type properties, creation metadata
- **📚 API Reference**: [DescribeThingType](https://docs.aws.amazon.com/iot/latest/apireference/API_DescribeThingType.html)

#### 8. Describe Endpoint
- **Purpose**: Get IoT endpoint URLs for your account
- **HTTP**: `GET /endpoint`
- **Input Options**: Endpoint type (iot:Data-ATS, iot:Data, iot:CredentialProvider, iot:Jobs)
- **Learn**: Different endpoint types and their purposes
- **Output**: HTTPS endpoint URL for device connections
- **📚 API Reference**: [DescribeEndpoint](https://docs.aws.amazon.com/iot/latest/apireference/API_DescribeEndpoint.html)

### Learning Features

**For each API call, you'll see:**
- 🔄 **API Call name** and description
- 🌐 **HTTP Request** method and full path
- ℹ️ **Operation explanation** - what it does and why
- 📥 **Input Parameters** - what data you're sending
- 💡 **Response Explanation** - what the output means
- 📤 **Response Payload** - actual JSON data returned

**Example Output:**
```
🔄 API Call: describe_thing
🌐 HTTP Request: GET https://iot.<region>.amazonaws.com/things/Vehicle-VIN-001
ℹ️  Description: Retrieves detailed information about a specific IoT Thing
📥 Input Parameters: {"thingName": "Vehicle-VIN-001"}
💡 Response Explanation: Returns complete Thing details including attributes, type, version, and ARN
📤 Response Payload: {
  "thingName": "Vehicle-VIN-001",
  "thingTypeName": "SedanVehicle",
  "attributes": {
    "customerId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "country": "USA",
    "manufacturingDate": "2024-03-15"
  },
  "version": 1
}
```

### Error Learning
The script handles and explains common errors:
- **ResourceNotFoundException** - When Things/Groups don't exist
- **InvalidRequestException** - When parameters are malformed
- **ThrottlingException** - When API rate limits are exceeded
- **UnauthorizedException** - When permissions are insufficient

## Certificate & Policy Manager

### Purpose
Learn AWS IoT security concepts through hands-on certificate and policy management. This script teaches the complete security model: device identity (certificates) and authorization (policies).

### How to Run

**Basic Usage:**
```bash
python certificate_manager.py
```

**With Debug Mode (detailed API logging):**
```bash
python certificate_manager.py --debug
```

### Interactive Main Menu

When you run the script, you'll see:
```
🔐 AWS IoT Certificate & Policy Manager
==================================================
This script teaches you AWS IoT security concepts:
• X.509 certificates for device authentication
• Certificate-to-Thing attachment
• IoT policies for authorization
• Policy attachment and detachment
• External certificate registration
• Complete API details for each operation
==================================================

📋 Main Menu:
1. Create AWS IoT Certificate & Attach to Thing (+ Optional Policy)
2. Register External Certificate & Attach to Thing (+ Optional Policy)
3. Attach Policy to Existing Certificate
4. Detach Policy from Certificate
5. Enable/Disable Certificate
6. Exit

Select option (1-6):
```

### Option 1: Complete Certificate Workflow

**What this teaches:**
- End-to-end certificate lifecycle
- Device identity establishment
- Security best practices

**Step-by-step process:**

#### Step 1: Thing Selection
- **Interactive device picker** with multiple options:
  - Select from numbered list (first 10 shown)
  - Type `all` to see complete device list
  - Type `manual` to enter Thing name directly
- **Validation** - Confirms Thing exists before proceeding
- **Learning**: Device discovery and selection patterns

#### Step 2: Certificate Creation
- **API Call**: `create_keys_and_certificate`
- **HTTP**: `POST /keys-and-certificate`
- **What happens**: AWS generates X.509 certificate + key pair
- **Learning**: Certificate components and their purposes
- **Output**: Certificate ARN, ID, PEM data, public/private keys

#### Step 3: Local File Storage
- **Automatic folder creation**: `certificates/{thing-name}/`
- **Files saved**:
  - `{cert-id}.crt` - Certificate PEM (for AWS IoT)
  - `{cert-id}.key` - Private key (keep secure!)
  - `{cert-id}.pub` - Public key (for reference)
- **Learning**: Certificate file management and security

#### Step 4: Certificate-Thing Attachment
- **Existing certificate check** - Warns if Thing already has certificates
- **Cleanup option** - Remove old certificates if desired
- **API Call**: `attach_thing_principal`
- **HTTP**: `PUT /things/{thingName}/principals`
- **Learning**: Device identity binding

#### Step 5: Policy Management (Optional)
- **Choice**: Use existing policy, create new policy, or skip
- **Existing Policy Selection**: Choose from available policies in your account
- **New Policy Creation**: Templates available or custom JSON input
- **Learning**: Authorization vs authentication, policy reuse strategies

### Option 2: External Certificate Registration

**What this teaches:**
- Bring Your Own Certificate (BYOC) workflow
- Self-signed certificate integration
- OpenSSL certificate generation
- External PKI infrastructure integration

### Option 3: Policy Attachment Workflow

**What this teaches:**
- Policy management without certificate creation
- Working with existing certificates
- Permission troubleshooting

### Option 4: Policy Detachment Workflow

**What this teaches:**
- Policy removal from certificates
- Finding devices by policy attachment
- Certificate-policy relationship management
- Permission revocation scenarios

**Step-by-step process:**

#### Step 1: Policy Selection
- **Interactive policy picker** from all available policies
- **Policy validation** - Confirms policy exists
- **Learning**: Policy discovery and selection patterns

#### Step 2: Certificate Discovery
- **API Call**: `list_targets_for_policy`
- **HTTP**: `POST /targets-for-policy/{policyName}`
- **What happens**: Finds all certificates with the selected policy attached
- **Learning**: Policy-to-certificate relationship mapping
- **Output**: Certificate ARNs with policy attachments

#### Step 3: Device Association
- **API Call**: `list_principal_things` for each certificate
- **HTTP**: `GET /principal-things`
- **What happens**: Maps certificates to their associated Things (devices)
- **Learning**: Certificate-Thing relationships and device identification
- **Display**: Certificate ID → Thing name mapping for easy selection

#### Step 4: Certificate Selection
- **Enhanced display** - Shows certificate ID → Thing name for context
- **Device context** - Clear visibility of which device will be affected
- **Impact assessment** - Understanding permission changes
- **Learning**: Certificate selection with device awareness

#### Step 5: Policy Detachment
- **API Call**: `detach_policy`
- **HTTP**: `POST /target-policies/{policyName}`
- **What happens**: Removes policy from selected certificate
- **Learning**: Policy detachment process and immediate effects
- **Impact**: Device loses specific permissions defined in the policy

**Use Cases:**
- **Permission revocation** - Remove specific permissions from devices
- **Role changes** - Modify device capabilities by changing policies
- **Security incidents** - Quickly remove compromised policy permissions
- **Policy updates** - Detach old policy before attaching updated version
- **Troubleshooting** - Remove problematic policies to isolate issues

### Option 5: Certificate Status Management

**What this teaches:**
- Certificate lifecycle management
- Enable/disable operations for security control
- Impact of certificate status on device connectivity
- Certificate status troubleshooting

**Step-by-step process:**

#### Step 1: Certificate Discovery
- **API Call**: `list_certificates` + `list_principal_things`
- **HTTP**: `GET /certificates` + `GET /principal-things`
- **What happens**: Lists all certificates with status and associated Thing names
- **Learning**: Certificate inventory, status monitoring, and Thing relationships
- **Output**: Certificate IDs, Thing associations, status (ACTIVE/INACTIVE), creation dates

#### Step 2: Certificate Selection
- **Enhanced display** - Shows certificate ID → Thing name for easy identification
- **Device context** - Clear visibility of which device each certificate controls
- **Status indicators** - 🟢 ACTIVE or 🔴 INACTIVE with Thing name
- **Learning**: Certificate-Thing relationships and impact assessment

**Example Display:**
```
📋 Found 3 certificate(s):
   1. abc123def456... → Vehicle-VIN-001 - 🟢 ACTIVE
   2. xyz789uvw012... → Vehicle-VIN-002 - 🔴 INACTIVE
   3. def456ghi789... (No Thing attached) - 🟢 ACTIVE
```

#### Step 3: Status Toggle
- **API Call**: `update_certificate`
- **HTTP**: `PUT /certificates/{certificateId}`
- **What happens**: Changes certificate status between ACTIVE/INACTIVE
- **Learning**: Certificate lifecycle control and security implications
- **Impact**: Immediate effect on device connectivity

**Use Cases:**
- **Disable compromised certificates** - Immediately revoke device access
- **Temporary device suspension** - Disable without deleting
- **Certificate rotation** - Disable old certificates after deploying new ones
- **Security incident response** - Quick certificate deactivation
- **Testing connectivity** - Verify certificate dependency

### Certificate Management Deep Dive

**X.509 Certificate Creation:**
- **Public Key Infrastructure (PKI)** concepts
- **Certificate Authority (CA)** role in AWS IoT
- **Key pair generation** and cryptographic principles
- **Certificate lifecycle** - creation, activation, rotation, revocation

**Local File Storage Strategy:**
```
certificates/
├── Vehicle-VIN-001/               # One folder per Thing
│   ├── abc123def456.crt          # Certificate PEM
│   ├── abc123def456.key          # Private key (NEVER share)
│   └── abc123def456.pub          # Public key (reference)
├── Vehicle-VIN-002/
│   ├── xyz789uvw012.crt
│   ├── xyz789uvw012.key
│   └── xyz789uvw012.pub
└── MyCustomDevice/
    └── ...

sample-certs/                    # OpenSSL generated certificates
├── sample-device.crt            # Sample certificate
└── sample-device.key            # Sample private key
```

**Security Best Practices:**
- **Private key protection** - Never transmit or share
- **Certificate organization** - One folder per device
- **File permissions** - Restrict access to certificate files
- **Backup strategies** - Secure certificate storage

### Policy Management Deep Dive

**Policy Templates Explained:**

**1. Basic Device Policy:**
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "iot:Connect",     # Connect to AWS IoT
      "iot:Publish",     # Send messages
      "iot:Subscribe",   # Listen to topics
      "iot:Receive"      # Receive messages
    ],
    "Resource": "*"      # All resources (broad permissions)
  }]
}
```

**2. Read-Only Policy:**
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "iot:Connect",     # Connect only
      "iot:Subscribe",   # Listen only
      "iot:Receive"      # Receive only (no publishing)
    ],
    "Resource": "*"
  }]
}
```

**3. Custom Policy:**
- **Interactive JSON editor** with validation
- **Error handling** for malformed JSON
- **Learning**: Policy syntax and structure

**Permission Control Concepts:**
- **Principle of least privilege** - Grant minimum necessary permissions
- **Resource-based restrictions** - Limit access to specific topics/clients
- **Action-based controls** - Allow/deny specific operations
- **Policy versioning** - Manage policy changes over time

**⚠️ Production Security Note**: The policy templates shown use `"Resource": "*"` for demonstration purposes to simplify learning. In production applications, you should use more restrictive resource ARNs and policy variables like `${iot:Connection.Thing.ThingName}` to limit device access to only their specific resources. Policy variables and advanced resource restrictions are beyond the scope of this basic learning path.

### API Learning Features

**For every API operation, you'll see:**

🔍 **API Details:**
- **Operation name** (e.g., `create_keys_and_certificate`)
- **HTTP method** (GET, POST, PUT, DELETE)
- **API path** (e.g., `/keys-and-certificate`)
- **Description** of what the API accomplishes
- **Input parameters** with actual values
- **Expected output** structure and meaning

📥 **Request Details:**
- **Complete input JSON** with all parameters
- **Parameter explanations** - what each field does
- **Validation rules** - required vs optional fields

📤 **Response Analysis:**
- **Full response JSON** (truncated if very long)
- **Key fields explanation** - what each response field means
- **Success indicators** - how to know the operation worked
- **Error scenarios** - common failure modes and solutions

### Certificate Options Explained

#### AWS IoT Certificates (Option 1)
- **Generated by AWS** - AWS creates the public/private key pair
- **API Used**: `create_keys_and_certificate`
- **Best for**: Production IoT devices
- **Key Management**: AWS handles certificate authority functions

#### External Certificates (Option 2)
- **Bring Your Own Certificate** - Use existing or self-generated certificates
- **API Used**: `register_certificate_without_ca` (for self-signed) or `register_certificate` (for CA-signed)
- **Best for**: Existing PKI infrastructure integration or learning with self-signed certificates
- **Key Management**: You control the private key
- **OpenSSL Option**: Generate sample certificates for learning

**Example API Learning Output:**
```
🔍 API Details:
   Operation: create_keys_and_certificate
   HTTP Method: POST
   API Path: /keys-and-certificate
   Description: Creates a new X.509 certificate with public/private key pair
   Input Parameters: setAsActive: true (activates certificate immediately)
   Expected Output: certificateArn, certificateId, certificatePem, keyPair

🔄 Creating certificate and key pair...
📥 Input: {"setAsActive": true}
✅ Creating certificate and key pair completed successfully
📤 Output: {
  "certificateArn": "arn:aws:iot:us-east-1:123456789012:cert/abc123...",
  "certificateId": "abc123def456789...",
  "certificatePem": "-----BEGIN CERTIFICATE-----\n...",
  "keyPair": {
    "PublicKey": "-----BEGIN PUBLIC KEY-----\n...",
    "PrivateKey": "..."
  }
}
```

### Error Learning Scenarios

The script handles and explains common security errors:
- **Certificate already exists** - How to handle duplicates
- **Thing not found** - Device discovery issues
- **Policy name conflicts** - Naming strategy solutions
- **Permission denied** - IAM permission troubleshooting
- **Invalid policy JSON** - Syntax error resolution

## MQTT Communication

### Purpose
Experience real-time IoT communication using the MQTT protocol. Learn how devices connect to AWS IoT Core and exchange messages securely.

### Two MQTT Options Available

#### Option A: Certificate-Based MQTT (Recommended for Learning)
**File**: `mqtt_client_explorer.py`
**Authentication**: X.509 certificates (mutual TLS)
**Best for**: Understanding production IoT security

#### Option B: WebSocket MQTT (Alternative Method)
**File**: `mqtt_websocket_explorer.py`  
**Authentication**: AWS IAM credentials (SigV4)
**Best for**: Web applications and firewall-friendly connections

**⚠️ Production Note**: This example uses AWS credentials directly for demonstration purposes. In production web applications, you would typically use JWT tokens or other identity tokens with AWS IoT Custom Authorizers for secure authentication. Custom Authorizers are beyond the scope of this basic learning path.

### Certificate-Based MQTT Client

#### How to Run

**Basic Usage:**
```bash
python mqtt_client_explorer.py
```

**With Debug Mode (connection diagnostics):**
```bash
python mqtt_client_explorer.py --debug
```

#### Prerequisites
- **Certificates must exist** - Run `certificate_manager.py` first
- **Policy attached** - Certificate needs IoT permissions
- **Thing association** - Certificate must be attached to a Thing

#### Interactive Device Selection

When you run the script:
1. **Device Discovery** - Automatically finds Things with certificates
2. **Certificate Validation** - Checks certificate files exist locally
3. **Interactive Selection** - Choose which device to simulate
4. **Connection Setup** - Configures MQTT client with certificates

#### MQTT Learning Features

**Connection Process:**
- **Endpoint Discovery** - Gets your account's IoT endpoint
- **TLS Configuration** - Sets up mutual TLS with certificates
- **MQTT Protocol** - Establishes MQTT over TLS connection
- **Keep-Alive** - Maintains persistent connection

**Topic Management:**
- **Subscription** - Listen to MQTT topics with wildcards
- **QoS Levels** - Quality of Service (0 = at most once, 1 = at least once)
- **Topic Patterns** - Use `+` (single level) and `#` (multi-level) wildcards

**Message Publishing:**
- **Text Messages** - Send plain text to any topic
- **JSON Messages** - Structured data with automatic formatting
- **QoS Options** - Choose delivery guarantees
- **Real-time Feedback** - See publish confirmations

#### Interactive Commands

Once connected, use these commands:

```bash
# Topic Subscription
📡 MQTT> sub device/+/temperature                  # Subscribe with QoS 0
📡 MQTT> sub1 device/alerts/#                      # Subscribe with QoS 1
📡 MQTT> unsub device/+/temperature               # Unsubscribe from topic

# Message Publishing
📡 MQTT> pub device/sensor/temperature 23.5        # Publish with QoS 0
📡 MQTT> pub1 device/alert "High temp!"            # Publish with QoS 1
📡 MQTT> json device/data temp=23.5 humidity=65    # Publish JSON object

# Utility Commands
📡 MQTT> test                                      # Send test message
📡 MQTT> status                                    # Show connection info
📡 MQTT> messages                                  # Show message history
📡 MQTT> debug                                     # Connection diagnostics
📡 MQTT> help                                      # Show all commands
📡 MQTT> quit                                      # Exit client
```

#### Example MQTT Session

```
📡 MQTT> sub device/+/temperature                  # Subscribe to temperature topics
✅ [14:30:10.123] SUBSCRIBED to device/+/temperature (QoS: 0)

📡 MQTT> pub device/sensor/temperature 23.5        # Publish temperature reading
✅ [14:30:15.456] PUBLISHED
   📤 Topic: device/sensor/temperature
   🏷️  QoS: 0 | Packet ID: 1
   📊 Size: 4 bytes

======================================================================
🔔 INCOMING MESSAGE #1 [14:30:15.789]
======================================================================
📥 Topic: device/sensor/temperature
🏷️  QoS: 0 (At most once)
📊 Payload Size: 4 bytes
💬 Message: 23.5
======================================================================
```

### WebSocket MQTT Client

#### How to Run

**Basic Usage:**
```bash
python mqtt_websocket_explorer.py
```

**With Debug Mode (SigV4 auth details):**
```bash
python mqtt_websocket_explorer.py --debug
```

#### Prerequisites
- **AWS Credentials** - Access Key and Secret Key configured
- **IAM Permissions** - IoT connect, publish, subscribe permissions
- **No certificates needed** - Uses IAM authentication instead

**⚠️ Production Note**: Direct AWS credential usage shown here is for learning purposes only. Production web applications should use Custom Authorizers with JWT/identity tokens instead of exposing AWS credentials to client applications.

#### Key Differences from Certificate MQTT

**Authentication Method:**
- **SigV4 Signing** - Uses AWS Access Key/Secret Key (demonstration only)
- **WebSocket Protocol** - MQTT over WebSocket (port 443)
- **Firewall Friendly** - Works through corporate firewalls
- **IAM Integration** - Uses standard AWS permissions
- **⚠️ Production Alternative** - Use Custom Authorizers with JWT/identity tokens

**Connection Process:**
- **Credential Validation** - Checks AWS credentials
- **SigV4 URL Generation** - Creates signed WebSocket URL
- **WebSocket Handshake** - Establishes WebSocket connection
- **MQTT over WebSocket** - Runs MQTT protocol over WebSocket

**Same MQTT Features:**
- **Topic subscriptions** with wildcards and QoS selection
- **Message publishing** with QoS options
- **Interactive commands** (sub, sub1, unsub, pub, pub1, json, etc.)
- **Real-time messaging** and feedback
- **Dynamic subscription management** during active sessions

### MQTT Protocol Learning

#### Core Concepts

**Topics and Hierarchies:**
- **Topic Structure**: `device/sensor/temperature`
- **Wildcards**: `device/+/temperature` (single level), `device/#` (multi-level)
- **Best Practices**: Hierarchical naming, avoid spaces

**Quality of Service (QoS):**
- **QoS 0 (At most once)**: Fire and forget, fastest
- **QoS 1 (At least once)**: Guaranteed delivery, may duplicate
- **QoS 2 (Exactly once)**: Not supported by AWS IoT

**Connection Management:**
- **Keep-Alive**: Periodic ping to maintain connection
- **Clean Session**: Start fresh vs resume previous session
- **Last Will**: Message sent if client disconnects unexpectedly

#### Security Models Compared

**Certificate-Based (Production Recommended):**
- ✅ **Device Identity** - Each device has unique certificate
- ✅ **Mutual TLS** - Both client and server authenticate
- ✅ **Offline Capable** - No internet needed for auth
- ✅ **Scalable** - Millions of devices supported
- ❌ **Complex Setup** - Certificate management required

**WebSocket/IAM (Development/Web Apps):**
- ✅ **Simple Setup** - Uses existing AWS credentials
- ✅ **Firewall Friendly** - Standard HTTPS port
- ✅ **IAM Integration** - Familiar AWS permissions
- ❌ **Internet Required** - Needs AWS API access
- ❌ **Less Scalable** - IAM user limits apply

## Device Shadow Explorer

### Purpose
Learn AWS IoT Device Shadow service through hands-on exploration of device state synchronization. This script teaches the complete shadow lifecycle: desired state, reported state, and delta processing.

### How to Run

**Basic Usage:**
```bash
python device_shadow_explorer.py
```

**With Debug Mode (detailed shadow message analysis):**
```bash
python device_shadow_explorer.py --debug
```

### Prerequisites
- **Certificates must exist** - Run `certificate_manager.py` first
- **Policy with shadow permissions** - Certificate needs IoT shadow permissions
- **Thing association** - Certificate must be attached to a Thing

### Interactive Device Shadow Learning

#### Device Selection and Setup
When you run the script:
1. **Device Discovery** - Automatically finds Things with certificates
2. **Certificate Validation** - Checks certificate files exist locally
3. **Local State Setup** - Creates device state simulation file
4. **Shadow Connection** - Establishes MQTT connection for shadow operations

#### Shadow Topic Subscriptions
Automatically subscribes to all shadow topics:
- **`$aws/things/{thing}/shadow/get/accepted`** - Shadow retrieval success
- **`$aws/things/{thing}/shadow/get/rejected`** - Shadow retrieval failure
- **`$aws/things/{thing}/shadow/update/accepted`** - Shadow update success
- **`$aws/things/{thing}/shadow/update/rejected`** - Shadow update failure
- **`$aws/things/{thing}/shadow/update/delta`** - Desired ≠ Reported (action needed)

#### Local Device State Simulation
**State File Structure:**
```json
{
  "temperature": 22.5,
  "humidity": 45.0,
  "status": "online",
  "firmware_version": "1.0.0",
  "last_updated": "2024-01-15T10:30:00.000Z"
}
```

**File Location:** `certificates/{thing-name}/device_state.json`

#### Interactive Commands

Once connected, use these commands:

```bash
# Shadow Operations
🌟 Shadow> get                                    # Request current shadow document
🌟 Shadow> report                                 # Report local state to shadow
🌟 Shadow> desire temperature=25.0 status=active # Set desired state (simulate cloud)

# Local Device Management
🌟 Shadow> local                                  # Show current local device state
🌟 Shadow> edit                                   # Edit local device state interactively

# Utility Commands
🌟 Shadow> status                                 # Show connection and shadow status
🌟 Shadow> messages                               # Show shadow message history
🌟 Shadow> debug                                  # Connection diagnostics
🌟 Shadow> help                                   # Show all commands
🌟 Shadow> quit                                   # Exit explorer
```

### Key Learning Features

#### Shadow Document Structure

**Complete Shadow Document:**
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

#### Automatic State Synchronization
**Delta Processing:**
1. **Delta Detection** - Script automatically detects when desired ≠ reported
2. **User Notification** - Shows differences and prompts for action
3. **Local Update** - Applies changes to local device state file
4. **Shadow Reporting** - Reports updated state back to AWS IoT

**Example Delta Flow:**
```
🔄 SHADOW DELTA RECEIVED
   📝 Description: Desired state differs from reported state
   📊 Version: 15
   🔄 Changes Needed: {
     "temperature": 25.0,
     "status": "active"
   }

🔍 State Comparison:
   📱 Local State: {
     "temperature": 22.5,
     "status": "online"
   }
   🔄 Delta: {
     "temperature": 25.0,
     "status": "active"
   }

⚠️  Differences Found:
   • temperature: 22.5 → 25.0
   • status: online → active

Apply these changes to local device? (y/N):
```

#### Interactive State Editor

**Edit Options:**
1. **Individual Value Editing** - Modify specific keys one by one
2. **JSON Replacement** - Replace entire state with new JSON
3. **Type Conversion** - Automatic conversion of strings to numbers/booleans

**Example Edit Session:**
```
📝 Local State Editor
Current state: {
  "temperature": 22.5,
  "humidity": 45.0,
  "status": "online"
}

Options:
1. Edit individual values
2. Replace entire state with JSON
3. Cancel

Select option (1-3): 1

Current values:
   1. temperature: 22.5
   2. humidity: 45.0
   3. status: online
   4. Add new key
   5. Done editing

Select item to edit (1-5): 1

Editing 'temperature' (current: 22.5)
New value (or press Enter to keep current): 24.0
✅ Updated temperature = 24.0
```

### Shadow Message Analysis

**Real-time Message Display:**
```
======================================================================
🌟 SHADOW MESSAGE RECEIVED [14:30:15.789]
======================================================================
✅ SHADOW UPDATE ACCEPTED
   📊 New Version: 16
   ⏰ Timestamp: 1642248615
   📡 Updated Reported: {
     "temperature": 24.0,
     "humidity": 45.0,
     "status": "online"
   }
======================================================================
```

### Learning Scenarios

#### Scenario 1: Cloud-to-Device Communication
1. Use `desire` command to simulate cloud/app setting desired state
2. Observe delta message generation
3. Apply changes to local device
4. Report updated state back to shadow

#### Scenario 2: Device-to-Cloud Communication
1. Use `edit` command to modify local device state
2. Use `report` command to update shadow
3. Observe shadow update acceptance

#### Scenario 3: State Synchronization
1. Create differences between desired and reported states
2. Observe automatic delta processing
3. Learn about conflict resolution

### Required IAM Permissions

**Shadow Policy Example:**
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

**⚠️ Production Security Note**: This policy uses `"Resource": "*"` for learning simplicity. Production policies should use specific resource ARNs and policy variables like `${iot:Connection.Thing.ThingName}` to restrict shadow access to only the device's own shadow.

## IoT Rules Engine Explorer

### Purpose
Learn AWS IoT Rules Engine through hands-on rule creation and management. This script teaches message routing, SQL-based filtering, and action configuration with automatic IAM role setup.

### How to Run

**Basic Usage:**
```bash
python iot_rules_explorer.py
```

**With Debug Mode (detailed API and IAM operations):**
```bash
python iot_rules_explorer.py --debug
```

### Prerequisites
- **AWS Credentials** - IAM permissions for IoT Rules and IAM role management
- **No certificates needed** - Rules Engine operates at the service level

### Interactive Rules Engine Learning

#### Main Menu Options
When you run the script:
1. **List all IoT Rules** - View existing rules with status and actions
2. **Describe specific IoT Rule** - Detailed rule analysis and SQL breakdown
3. **Create new IoT Rule** - Guided rule creation with SQL builder
4. **Manage IoT Rule** - Enable, disable, or delete rules

### Key Learning Features

#### Rule Creation Workflow
**Step-by-Step Guided Creation:**
1. **Rule Naming** - Learn naming conventions and uniqueness requirements
2. **Event Type Selection** - Choose from common IoT event types or custom
3. **SQL Statement Building** - Interactive SELECT, FROM, WHERE clause construction
4. **Action Configuration** - Set up republish targets with proper IAM roles
5. **Automatic IAM Setup** - Script creates and configures necessary permissions

#### SQL Statement Builder

**Topic Pattern:**
```
testRulesEngineTopic/+/<eventType>
```

**Event Type Options:**
- `temperature` - Temperature sensor readings
- `humidity` - Humidity measurements
- `pressure` - Pressure sensor data
- `motion` - Motion detection events
- `door` - Door sensor status
- `alarm` - Alarm system events
- `status` - General device status
- `battery` - Battery level reports
- `Custom` - User-defined event type

**SELECT Clause Options:**
```sql
-- All attributes
SELECT * FROM 'testRulesEngineTopic/+/temperature'

-- Specific attributes
SELECT deviceId, timestamp, value FROM 'testRulesEngineTopic/+/temperature'

-- Multiple sensor data
SELECT deviceId, timestamp, temperature, humidity FROM 'testRulesEngineTopic/+/temperature'

-- Status and battery
SELECT deviceId, value, status, battery FROM 'testRulesEngineTopic/+/status'
```

**WHERE Clause Examples:**
```sql
-- Temperature threshold
WHERE temperature > 25

-- Status filtering
WHERE status = 'active'

-- Battery alerts
WHERE level < 20

-- Time-based filtering
WHERE timestamp > timestamp() - 3600000
```

#### Rule Testing Features

**Interactive Testing Process**
**Prerequisites:**
- **Existing IoT Rule** - Create a rule first using option 3
- **Certificates** - Run `certificate_manager.py` first
- **MQTT Connection** - Script automatically connects using available certificates

**Testing Workflow:**
1. **Rule Selection** - Choose from available rules
2. **Rule Analysis** - View SQL statement, topic pattern, and WHERE conditions
3. **MQTT Setup** - Automatic connection to AWS IoT with certificate authentication
4. **Target Subscription** - Subscribe to rule output topics to see results
5. **Interactive Message Creation** - Generate test messages based on your learning goals

#### Learning-Focused Message Generation
**For each test message, you choose:**
- **Topic Matching**: Should the message topic match the rule's FROM clause?
- **WHERE Condition**: Should the message content satisfy the WHERE clause?
- **Expected Outcome**: Rule should trigger (both match) or not trigger

**Example Testing Session:**
```
🧪 Test Message #1
📥 Topic Pattern: testRulesEngineTopic/+/temperature
Should this message MATCH the topic pattern? (y/n): y
🔍 WHERE Condition: temperature > 25
Should this message MATCH the WHERE condition? (y/n): y

📝 Test Message:
📡 Topic: testRulesEngineTopic/device123/temperature
💬 Payload: {
  "deviceId": "test-device-123",
  "timestamp": 1642248600000,
  "temperature": 30.0
}

🔮 Prediction: Rule SHOULD trigger
📤 Publishing test message...
⏳ Waiting 3 seconds for rule processing...

🔔 RULE OUTPUT RECEIVED [14:30:15.789]
📤 Topic: processed/temperature
💬 Message: {"deviceId":"test-device-123","temperature":30.0}
✅ Rule 'temperature-monitor' processed and forwarded the message!
```

#### Smart Message Generation
**Event-Type Specific Messages:**
- **Temperature events**: Generates realistic temperature values based on WHERE conditions
- **Battery events**: Creates appropriate battery level data
- **Status events**: Uses relevant status values (active, offline, maintenance)
- **Motion events**: Includes detection boolean and location data

**Condition-Aware Generation:**
- **Numeric comparisons**: `temperature > 25` → generates 30.0 (matching) or 20.0 (non-matching)
- **String comparisons**: `status = 'active'` → generates 'active' (matching) or 'inactive' (non-matching)
- **Complex conditions**: Handles multiple operators and data types

#### Real-Time Learning Feedback
**Immediate Results:**
- **Rule Output Detection** - See messages forwarded to target topics
- **Timing Analysis** - Understand rule processing latency
- **Prediction Validation** - Compare expected vs actual behavior
- **Error Scenarios** - Learn from unexpected outcomes

**Educational Benefits:**
- **Topic Pattern Understanding** - Learn wildcard matching (`+`, `#`)
- **WHERE Clause Logic** - Practice SQL-like filtering conditions
- **Message Routing** - Observe how rules transform and forward messages
- **Debugging Skills** - Identify why rules don't trigger as expected

#### Complete SQL Examples
**Temperature Monitoring:**
```sql
SELECT deviceId, timestamp, value 
FROM 'testRulesEngineTopic/+/temperature' 
WHERE value > 30
```

**Battery Alerts:**
```sql
SELECT deviceId, battery, status 
FROM 'testRulesEngineTopic/+/battery' 
WHERE battery < 15
```

**Motion Detection:**
```sql
SELECT * 
FROM 'testRulesEngineTopic/+/motion' 
WHERE value = 'detected'
```

### Rule Management Features

#### List Rules
**Comprehensive Rule Overview:**
- Rule names and creation dates
- Enable/disable status indicators
- SQL statements and action counts
- Action types and target destinations

**Example Output:**
```
📋 Found 3 IoT Rules:

1. TemperatureAlert - 🟢 ENABLED
   📅 Created: 2024-01-15T10:30:00.000Z
   📝 SQL: SELECT * FROM 'testRulesEngineTopic/+/temperature' WHERE value > 30
   🎯 Actions: 1 configured
      1. Republish to: alerts/temperature

2. BatteryMonitor - 🔴 DISABLED
   📅 Created: 2024-01-15T11:15:00.000Z
   📝 SQL: SELECT deviceId, battery FROM 'testRulesEngineTopic/+/battery' WHERE battery < 20
   🎯 Actions: 1 configured
      1. Republish to: alerts/battery
```

#### Describe Rule
**Detailed Rule Analysis:**
- Complete SQL statement breakdown
- SELECT, FROM, WHERE clause explanation
- Action configuration details
- IAM role and permission information
- Error action configuration (if any)

**SQL Breakdown Example:**
```
📝 SQL Statement:
   SELECT deviceId, timestamp, value FROM 'testRulesEngineTopic/+/temperature' WHERE value > 25

📖 SQL Breakdown:
   🔍 SELECT: deviceId, timestamp, value
   📥 FROM: 'testRulesEngineTopic/+/temperature'
   🔍 WHERE: value > 25

🎯 Actions (1):
   1. Action Type: republish
      📤 Target Topic: processed/temperature
      🔑 Role ARN: arn:aws:iam::123456789012:role/IoTRulesEngineRole
      🏷️  QoS: 1
```

### Automatic IAM Configuration

#### IAM Role Creation
**Automatic Setup:**
- Creates `IoTRulesEngineRole` if it doesn't exist
- Configures trust policy for `iot.amazonaws.com`
- Attaches necessary permissions for republish actions
- Handles IAM eventual consistency delays

**Trust Policy:**
```json
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
```

**Permissions Policy:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "iot:Publish"
      ],
      "Resource": "*"
    }
  ]
}
```

### Testing Your Rules

#### Test Message Examples
**Temperature Event:**
```json
{
  "deviceId": "device123",
  "timestamp": 1642248600000,
  "value": 32.5,
  "unit": "celsius"
}
```

**Battery Alert:**
```json
{
  "deviceId": "sensor456",
  "timestamp": 1642248600000,
  "battery": 15,
  "status": "low_battery"
}
```

**Motion Detection:**
```json
{
  "deviceId": "motion789",
  "timestamp": 1642248600000,
  "value": "detected",
  "location": "front_door"
}
```

#### Testing Workflow
1. **Create Rule** - Use the script to create a rule with specific filtering
2. **Publish Test Message** - Send message to source topic using MQTT client
3. **Subscribe to Target** - Listen to republish target topic
4. **Verify Routing** - Confirm message appears on target topic with correct filtering

### Learning Scenarios

#### Scenario 1: Temperature Monitoring
1. Create rule for temperature events > 30°C
2. Test with various temperature values
3. Observe filtering behavior
4. Monitor republished messages

#### Scenario 2: Multi-Attribute Selection
1. Create rule selecting specific attributes
2. Compare input vs output message structure
3. Understand data transformation

#### Scenario 3: Complex Filtering
1. Create rule with WHERE clause
2. Test edge cases and boundary conditions
3. Learn SQL operator behavior

### Required IAM Permissions

**For the Script User:**
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