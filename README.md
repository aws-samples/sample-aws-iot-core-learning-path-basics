# AWS IoT Core - Basics

A comprehensive Python toolkit for learning AWS IoT Core basic concepts through hands-on exploration. Interactive scripts demonstrate device management, security, API operations, and MQTT communication with detailed explanations.

## 🚀 TL;DR - Complete Learning Path

```bash
# 1. Setup environment
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 2. Configure AWS credentials
export AWS_ACCESS_KEY_ID=<your-key>
export AWS_SECRET_ACCESS_KEY=<your-secret>
export AWS_DEFAULT_REGION=us-east-1

# 3. Complete learning sequence
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

## Table of Contents

- 🚀 [Quick Start](#-tldr---get-started-in-5-minutes)
- ⚙️ [Installation & Setup](#️-installation--setup)
- 📚 [Learning Scripts](#-learning-scripts)
- 🧹 [Resource Cleanup](#resource-cleanup)
- 🛠️ [Troubleshooting](#troubleshooting)
- 📖 [Advanced Documentation](#-advanced-documentation)

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.7+
- AWS account with IoT permissions
- Terminal/command line access
- OpenSSL (for certificate features)

<details>
<summary>💰 <strong>AWS Cost Details</strong></summary>

**This project creates real AWS resources that will incur charges (~$0.17 total).**

| Service | Usage | Estimated Cost (USD) |
|---------|-------|---------------------|
| **AWS IoT Core** | ~100 messages, 20 devices | $0.10 |
| **IoT Device Shadow** | ~30 shadow operations | $0.04 |
| **IoT Rules Engine** | ~50 rule executions | $0.01 |
| **Certificate Storage** | 20 certificates for 1 day | $0.01 |
| **CloudWatch Logs** | Basic logging | $0.01 |
| **Total Estimated** | **Complete learning session** | **~$0.17** |

**Cost Management:**
- ✅ Automatic cleanup scripts provided
- ✅ Minimal resource creation
- ✅ Short-lived resources (single session)
- ⚠️ **Your responsibility** to run cleanup scripts

**📊 Monitor costs:** [AWS Billing Dashboard](https://console.aws.amazon.com/billing/)

</details>

### Quick Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure AWS credentials
export AWS_ACCESS_KEY_ID=<your-access-key>
export AWS_SECRET_ACCESS_KEY=<your-secret-key>
export AWS_DEFAULT_REGION=us-east-1
```

<details>
<summary>🔧 <strong>Detailed Installation Steps</strong></summary>

**Install OpenSSL:**

**macOS:** `brew install openssl`
**Ubuntu/Debian:** `sudo apt-get install openssl`
**Windows:** Download from [Win32/Win64 OpenSSL](https://slproweb.com/products/Win32OpenSSL.html)

**Virtual Environment (Recommended):**
```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

**AWS Credentials:**
```bash
export AWS_ACCESS_KEY_ID=<your-access-key>
export AWS_SECRET_ACCESS_KEY=<your-secret-key>
export AWS_SESSION_TOKEN=<your-session-token>  # Optional
export AWS_DEFAULT_REGION=us-east-1
```

**Alternative:** Use AWS CLI configuration or IAM roles.

</details>

## 📚 Learning Scripts

**Recommended Learning Path:**
1. `scripts/setup_sample_data.py` - Create sample IoT resources
2. `scripts/iot_registry_explorer.py` - Explore AWS IoT APIs
3. `scripts/certificate_manager.py` - Learn IoT security
4. `scripts/mqtt_client_explorer.py` - Real-time MQTT communication
5. `scripts/device_shadow_explorer.py` - Device state synchronization
6. `scripts/iot_rules_explorer.py` - Message routing and processing
7. `scripts/cleanup_sample_data.py` - Clean up resources

**What You'll Learn:**
- **Device Management**: Things, Thing Types, Thing Groups
- **Security**: X.509 certificates, IoT policies, authentication
- **APIs**: Complete HTTP request/response details
- **MQTT**: Real-time messaging with certificates and WebSockets
- **Best Practices**: Resource lifecycle management

**📚 Reference**: [AWS IoT Core Developer Guide](https://docs.aws.amazon.com/iot/latest/developerguide/)

<details>
<summary>📊 <strong>Sample Data Setup</strong></summary>

### Purpose
Creates realistic IoT resources for hands-on learning without requiring real devices.

### Usage
```bash
python scripts/setup_sample_data.py
python scripts/setup_sample_data.py --debug  # See detailed API calls
```

<details>
<summary>📋 Interactive Experience</summary>

When you run the script, you'll see:
1. **Confirmation prompt** - Review what will be created
2. **Step-by-step creation** - Watch each resource being built
3. **Real-time feedback** - See success/error messages
4. **API learning** - Understand which AWS APIs are called
5. **Summary report** - Final count of created resources

</details>

<details>
<summary>📦 What Gets Created</summary>

**Thing Types (3 vehicle categories):**
- **SedanVehicle** - For passenger sedan vehicles
- **SUVVehicle** - For sport utility vehicles
- **TruckVehicle** - For commercial truck vehicles

**Thing Groups (4 fleet categories):**
- **CustomerFleet** - Customer-owned vehicles
- **TestFleet** - Vehicles for testing and validation
- **MaintenanceFleet** - Vehicles undergoing service
- **DealerFleet** - Dealer inventory vehicles

**Things (20 simulated vehicles):**
- **Naming**: Vehicle-VIN-001 through Vehicle-VIN-020
- **Realistic attributes** with random but meaningful data
- **Automatic assignment** to Thing Types and Groups

</details>

**📚 Learn More**: [Managing Things with AWS IoT](https://docs.aws.amazon.com/iot/latest/developerguide/thing-management.html)

<details>
<summary>📊 Sample Data Structure</summary>

Each Thing includes these attributes:

| Attribute | Description | Example Values |
|-----------|-------------|----------------|
| **customerId** | UUID v4 for customer identification | `a1b2c3d4-e5f6-7890-abcd-ef1234567890` |
| **country** | Random country for global simulation | USA, Germany, Japan, Canada, Brazil, UK, France, Australia, India, Mexico |
| **manufacturingDate** | Random date within the last year | `2024-03-15`, `2024-07-22` |
| **thingType** | Randomly assigned vehicle category | SedanVehicle, SUVVehicle, TruckVehicle |
| **thingGroup** | Random fleet assignment | CustomerFleet, TestFleet, MaintenanceFleet, DealerFleet |

</details>

### Learning Benefits
- **Realistic data patterns** - Understand how IoT devices are organized
- **Attribute usage** - See how metadata enhances device management
- **Hierarchical structure** - Learn Thing Types and Groups relationships
- **API exposure** - Watch AWS IoT Registry APIs in action

### Debug Mode Details
Debug mode shows:
- **HTTP method and path** for each API call
- **Request parameters** sent to AWS
- **Response data** received from AWS
- **Timing information** for each operation
- **Error details** if any issues occur

</details>

<details>
<summary>🔍 <strong>IoT Registry API Explorer</strong></summary>

### Purpose
Interactive tool for learning AWS IoT Registry APIs through real API calls with detailed explanations. This script teaches you the Control Plane operations used to manage IoT devices, certificates, and policies.

**Note**: AWS IoT Core provides many APIs across device management and security. This explorer focuses on 8 core Registry APIs that are essential for understanding IoT device lifecycle management. For complete API details, see the [AWS IoT Registry API Reference](https://docs.aws.amazon.com/iot/latest/apireference/API_Operations_AWS_IoT.html).

### How to Run

**Basic Usage:**
```bash
python scripts/iot_registry_explorer.py
```

**With Debug Mode (enhanced API details):**
```bash
python scripts/iot_registry_explorer.py --debug
```

<details>
<summary>📋 Interactive Menu System</summary>

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

</details>

<details>
<summary>🔍 Supported APIs with Learning Details</summary>

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

</details>

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

**📚 Learn More**: [AWS IoT API Reference](https://docs.aws.amazon.com/iot/latest/apireference/) | [Error Handling Best Practices](https://docs.aws.amazon.com/iot/latest/developerguide/iot-errors.html)

</details>

<details>
<summary>🔐 <strong>Certificate & Policy Manager</strong></summary>

### Purpose
Learn AWS IoT security concepts through hands-on certificate and policy management. This script teaches the complete security model: device identity (certificates) and authorization (policies).

### How to Run

**Basic Usage:**
```bash
python scripts/certificate_manager.py
```

**With Debug Mode (detailed API logging):**
```bash
python scripts/certificate_manager.py --debug
```

<details>
<summary>📋 Interactive Main Menu</summary>

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

</details>

### Key Learning Areas

**Certificate Management:**
- X.509 certificate creation and lifecycle
- Certificate-Thing attachment for device identity
- Local file storage and organization
- Security best practices

**Policy Management:**
- IoT policy creation with templates
- Policy attachment to certificates
- Permission control concepts
- Production security considerations

**⚠️ Production Security Note**: The policy templates use `"Resource": "*"` for demonstration purposes. In production, use specific resource ARNs and policy variables like `${iot:Connection.Thing.ThingName}` to restrict device access to only their specific resources. Policy variables are beyond the scope of this basic learning path.

**📚 Learn More**: [AWS IoT Security Best Practices](https://docs.aws.amazon.com/iot/latest/developerguide/security-best-practices.html) | [AWS IoT Policies](https://docs.aws.amazon.com/iot/latest/developerguide/iot-policies.html)

</details>

<details>
<summary>📡 <strong>MQTT Communication</strong></summary>

### Purpose
Experience real-time IoT communication using the MQTT protocol. Learn how devices connect to AWS IoT Core and exchange messages securely.

### Two MQTT Options Available

#### Option A: Certificate-Based MQTT (Recommended for Learning)
**File**: `scripts/mqtt_client_explorer.py`
**Authentication**: X.509 certificates (mutual TLS)
**Best for**: Understanding production IoT security

#### Option B: WebSocket MQTT (Alternative Method)
**File**: `scripts/mqtt_websocket_explorer.py`  
**Authentication**: AWS IAM credentials (SigV4)
**Best for**: Web applications and firewall-friendly connections

**⚠️ Production Note**: This example uses AWS credentials directly for demonstration purposes. In production web applications, you would typically use JWT tokens or other identity tokens with AWS IoT Custom Authorizers for secure authentication. Custom Authorizers are beyond the scope of this basic learning path.

### Certificate-Based MQTT Client

#### How to Run

**Basic Usage:**
```bash
python scripts/mqtt_client_explorer.py
```

**With Debug Mode (connection diagnostics):**
```bash
python scripts/mqtt_client_explorer.py --debug
```

#### Prerequisites
- **Certificates must exist** - Run [`certificate_manager.py`](#certificate--policy-manager) first
- **Policy attached** - Certificate needs IoT permissions
- **Thing association** - Certificate must be attached to a Thing

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

<details>
<summary>📝 Interactive Commands</summary>

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

</details>

**📚 Learn More**: [MQTT Protocol Guide](https://docs.aws.amazon.com/iot/latest/developerguide/mqtt.html) | [Device Authentication](https://docs.aws.amazon.com/iot/latest/developerguide/client-authentication.html)

</details>

<details>
<summary>🌟 <strong>Device Shadow Explorer</strong></summary>

### Purpose
Learn AWS IoT Device Shadow service through hands-on exploration of device state synchronization. This script teaches the complete shadow lifecycle: desired state, reported state, and delta processing.

### How to Run

**Basic Usage:**
```bash
python scripts/device_shadow_explorer.py
```

**With Debug Mode (detailed shadow message analysis):**
```bash
python scripts/device_shadow_explorer.py --debug
```

### Prerequisites
- **Certificates must exist** - Run [`certificate_manager.py`](#certificate--policy-manager) first
- **Policy with shadow permissions** - Certificate needs IoT shadow permissions
- **Thing association** - Certificate must be attached to a Thing

### Key Learning Features

#### Shadow Document Structure
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

**📚 Learn More**: [AWS IoT Device Shadow](https://docs.aws.amazon.com/iot/latest/developerguide/iot-device-shadows.html) | [Shadow MQTT Topics](https://docs.aws.amazon.com/iot/latest/developerguide/device-shadow-mqtt.html)

</details>

<details>
<summary>⚙️ <strong>IoT Rules Engine Explorer</strong></summary>

### Purpose
Learn AWS IoT Rules Engine through hands-on rule creation and management. This script teaches message routing, SQL-based filtering, and action configuration with automatic IAM role setup.

### How to Run

**Basic Usage:**
```bash
python scripts/iot_rules_explorer.py
```

**With Debug Mode (detailed API and IAM operations):**
```bash
python scripts/iot_rules_explorer.py --debug
```

### Prerequisites
- **AWS Credentials** - IAM permissions for IoT Rules and IAM role management
- **No certificates needed** - Rules Engine operates at the service level

### Key Learning Features

#### Rule Creation Workflow
**Step-by-Step Guided Creation:**
1. **Rule Naming** - Learn naming conventions and uniqueness requirements
2. **Event Type Selection** - Choose from common IoT event types or custom
3. **SQL Statement Building** - Interactive SELECT, FROM, WHERE clause construction
4. **Action Configuration** - Set up republish targets with proper IAM roles
5. **Automatic IAM Setup** - Script creates and configures necessary permissions

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

### Automatic IAM Configuration

#### IAM Role Creation
**Automatic Setup:**
- Creates `IoTRulesEngineRole` if it doesn't exist
- Configures trust policy for `iot.amazonaws.com`
- Attaches necessary permissions for republish actions
- Handles IAM eventual consistency delays

**📚 Learn More**: [AWS IoT Rules Engine](https://docs.aws.amazon.com/iot/latest/developerguide/iot-rules.html) | [Rules Engine SQL Reference](https://docs.aws.amazon.com/iot/latest/developerguide/iot-sql-reference.html)

</details>

## Resource Cleanup

### Purpose
Properly clean up AWS resources to avoid charges and maintain a tidy account. The cleanup script only removes resources created by this learning project.

### How to Run

**Basic Usage:**
```bash
python scripts/cleanup_sample_data.py
```

**With Debug Mode (see detailed API operations):**
```bash
python scripts/cleanup_sample_data.py --debug
```

### Interactive Cleanup Process

When you run the script:
1. **Safety Confirmation** - Reviews what will be deleted
2. **Resource Discovery** - Finds all sample resources
3. **Step-by-step Removal** - Deletes in proper order
4. **Progress Feedback** - Shows success/error for each operation
5. **Final Summary** - Reports what was cleaned up

### What Gets Cleaned (Safe Targets Only)

**✅ Sample Things:**
- Vehicle-VIN-001 through Vehicle-VIN-020
- Only Things matching the sample naming pattern
- Preserves any existing Things you created separately

**✅ Associated Certificates:**
- Certificates attached to sample Things
- Certificate-policy detachments
- Certificate deactivation and deletion
- Local certificate files in `./certificates/`

**✅ Sample Thing Types:**
- SedanVehicle, SUVVehicle, TruckVehicle
- Only types created by the sample data script
- Handles AWS 5-minute deprecation requirement

**✅ Sample Thing Groups:**
- CustomerFleet, TestFleet, MaintenanceFleet, DealerFleet
- Only groups created by the sample data script
- Preserves existing groups

**✅ Local Files:**
- Certificate files in `./certificates/` folder
- Only removes files for deleted Things
- Preserves certificates for remaining devices

### What's Protected (Never Deleted)

**❌ Existing Resources:**
- Things not matching Device-### pattern
- Thing Types not in the sample list
- Thing Groups not in the sample list
- Certificates attached to non-sample Things

**❌ Policies:**
- IoT policies require manual review
- May be shared across multiple certificates
- Script provides guidance on policy cleanup

### Cleanup Order (Important for Dependencies)

1. **Certificate Detachment** - Remove certificate-Thing associations
2. **Policy Detachment** - Remove certificate-policy associations  
3. **Certificate Deletion** - Delete certificates (after deactivation)
4. **Thing Deletion** - Remove Things (after certificate cleanup)
5. **Thing Group Deletion** - Remove groups (after Things removed)
6. **Thing Type Deprecation** - Mark types as deprecated
7. **Thing Type Deletion** - Delete types (after 5-minute wait)
8. **Local File Cleanup** - Remove certificate files

### Special Handling: Thing Types

AWS IoT requires a 5-minute waiting period between deprecating and deleting Thing Types:

**Options provided:**
- **Wait and Delete** - Script waits 5 minutes then deletes
- **Skip Deletion** - Deprecate only, delete manually later
- **Try Immediate** - Attempt deletion (may fail due to timing)

### Debug Mode Benefits

Debug mode shows:
- **API calls being made** - Which AWS APIs are used
- **Request/response details** - Complete API interactions
- **Timing information** - How long each operation takes
- **Error diagnostics** - Detailed error messages and solutions
- **Dependency resolution** - Why operations happen in specific order

### Error Handling and Recovery

**Common scenarios handled:**
- **Resource not found** - Already deleted or never existed
- **Dependency conflicts** - Resources still in use
- **Permission errors** - Insufficient IAM permissions
- **Timing issues** - AWS eventual consistency delays

**Recovery guidance:**
- **Partial cleanup** - Script can be run multiple times safely
- **Manual intervention** - Clear instructions for manual cleanup
- **AWS Console verification** - How to check cleanup success

## 🛠️ Troubleshooting

<details>
<summary>🔧 Common Issues</summary>

#### AWS Credentials
```bash
# Verify credentials are set
aws sts get-caller-identity

# Check region
echo $AWS_DEFAULT_REGION
```

#### Virtual Environment
```bash
# Verify venv is active
which python
# Should show: /path/to/your/project/venv/bin/python

# Reactivate if needed
source venv/bin/activate
```

#### Dependencies
```bash
# Reinstall if needed
pip install --upgrade -r requirements.txt
```

#### Region Error
If you get "You must specify a region" error:
```bash
export AWS_DEFAULT_REGION=us-east-1
```

#### Permissions
Ensure your AWS credentials have these permissions:
- `iot:*` (for learning environments)
- Or specific permissions: `iot:CreateThing`, `iot:ListThings`, `iot:CreateCertificate`, etc.

#### Certificate Issues
- **Certificate not found**: Run [certificate_manager.py](#certificate--policy-manager) first
- **Policy attachment failed**: Check certificate is active and attached to Thing
- **File not found**: Check certificates/ folder exists and has correct permissions

</details>

<details>
<summary>📡 MQTT Connection Issues</summary>

```bash
# Verify certificate files exist
ls -la certificates/Vehicle-VIN-001/

# Check certificate is attached to Thing
python scripts/iot_registry_explorer.py
# Select option 5 (Describe Thing) and verify certificates

# Test basic connectivity
openssl s_client -connect <your-endpoint>:8883 -cert certificates/Vehicle-VIN-001/<cert-id>.crt -key certificates/Vehicle-VIN-001/<cert-id>.key
```

#### MQTT Troubleshooting Commands
If you get subscription or publish failures:

```bash
# Use debug mode for detailed error information
python scripts/mqtt_client_explorer.py --debug

# Run connection diagnostics within MQTT client
📡 MQTT> debug
📡 MQTT> status
```

**Common MQTT Error Solutions:**
- **Subscription/Publish Failed**: Certificate not active, not attached to Thing, or policy not attached
- **Connection Timeout**: Network connectivity or incorrect endpoint
- **Invalid Topic**: Topic format doesn't follow AWS IoT naming rules
- **Authentication Failed**: Certificate files corrupted or wrong Thing selected

**Need certificates?** Go back to [Certificate & Policy Manager](#certificate--policy-manager)

</details>

#### WebSocket MQTT Issues
```bash
# Verify AWS credentials
aws sts get-caller-identity

# Check IAM permissions
aws iam get-user-policy --user-name <your-username> --policy-name <policy-name>
```

**Required IAM Permissions for WebSocket MQTT:**
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "iot:Connect",
      "iot:Publish", 
      "iot:Subscribe",
      "iot:Receive"
    ],
    "Resource": "*"
  }]
}
```

**⚠️ Production Security Note**: This example uses `"Resource": "*"` for demonstration purposes. In production, use specific resource ARNs and policy variables to restrict access to only necessary topics and client IDs.

### Getting Help

1. **Run with debug mode** - Add `--debug` flag to see detailed API calls and diagnostics
2. **Check AWS IoT Console** - Verify resources were created correctly
3. **Review error messages** - Most errors include specific guidance and solutions
4. **Test connectivity** - Use built-in diagnostic commands in MQTT clients
5. **Start fresh** - Run cleanup script and start over if needed
6. **Check logs** - Enable AWS IoT logging in CloudWatch for production debugging

## 📖 Advanced Documentation

### Detailed Documentation

- **[📚 Detailed Script Documentation](docs/DETAILED_SCRIPTS.md)** - Comprehensive guides for each learning script
- **[🛠️ Troubleshooting Guide](docs/TROUBLESHOOTING.md)** - Solutions for common issues and errors
- **[📋 Usage Examples](docs/EXAMPLES.md)** - Complete workflows and interactive examples

### Project Structure

```
├── scripts/
│   ├── setup_sample_data.py          # Creates sample IoT resources
│   ├── iot_registry_explorer.py      # Interactive API explorer
│   ├── certificate_manager.py        # Certificate and policy management
│   ├── mqtt_client_explorer.py       # Certificate-based MQTT client
│   ├── mqtt_websocket_explorer.py    # WebSocket MQTT client
│   ├── device_shadow_explorer.py     # Device Shadow learning tool
│   ├── iot_rules_explorer.py         # IoT Rules Engine learning tool
│   └── cleanup_sample_data.py        # Safe cleanup of sample resources
├── requirements.txt                   # Python dependencies
├── certificates/                      # Local certificate storage (auto-created)
└── README.md                          # This file
```

### Learning Outcomes

After completing this tutorial, you'll understand:

#### Core Concepts
- **Things**: Digital representations of IoT devices
- **Thing Types**: Templates defining device categories
- **Thing Groups**: Hierarchical organization for device management
- **Certificates**: X.509 certificates for device identity
- **Policies**: JSON documents defining device permissions
- **Device Shadows**: JSON documents storing device state (desired, reported, delta)

#### Security Model
- How certificates provide device identity
- The relationship between certificates, Things, and policies
- Proper certificate lifecycle management
- Authorization vs authentication in IoT

#### API Operations
- Complete HTTP request/response patterns
- Input parameters and expected outputs
- Error handling and status codes
- Best practices for API usage

#### MQTT Protocol
- Connection establishment and keep-alive mechanisms
- Topic hierarchies and wildcard subscriptions
- QoS levels and delivery guarantees
- Message publishing and subscription patterns
- Real-time communication and protocol timing

#### Device Shadow Service
- Shadow document structure and lifecycle
- Desired vs reported state synchronization
- Delta message processing and conflict resolution
- Shadow MQTT topics and message patterns
- Local device state simulation and management

### Complete Learning Workflow

**Recommended sequence for comprehensive learning:**

```bash
# 1. Setup your environment
source venv/bin/activate
export AWS_ACCESS_KEY_ID=<your-key>
export AWS_SECRET_ACCESS_KEY=<your-secret>
export AWS_DEFAULT_REGION=us-east-1

# 2. Create sample IoT resources
python scripts/setup_sample_data.py

# 3. Explore the AWS IoT Registry APIs
python scripts/iot_registry_explorer.py

# 4. Learn security with certificates and policies
python scripts/certificate_manager.py

# 5. Experience real-time MQTT communication
python scripts/mqtt_client_explorer.py
# OR
python scripts/mqtt_websocket_explorer.py

# 6. Learn device state synchronization with shadows
python scripts/device_shadow_explorer.py

# 7. Master message routing with Rules Engine
python scripts/iot_rules_explorer.py

# 8. Clean up when done learning
python scripts/cleanup_sample_data.py
```

**Apart from the initial setup script, all other scripts can be run independently based on your learning interests.**