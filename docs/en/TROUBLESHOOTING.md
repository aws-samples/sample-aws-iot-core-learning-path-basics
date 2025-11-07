# Troubleshooting Guide

This document provides comprehensive troubleshooting guidance for the Amazon Web Services (AWS) AWS IoT Core - Basics learning project.

## Table of Contents

- [Common Issues](#common-issues)
  - [AWS Credentials](#aws-credentials)
  - [Virtual Environment Issues](#virtual-environment-issues)
  - [Dependency Issues](#dependency-issues)
  - [Permission Issues](#permission-issues)
  - [Certificate Issues](#certificate-issues)
- [MQTT Connection Issues](#mqtt-connection-issues)
  - [Certificate-Based MQTT Problems](#certificate-based-mqtt-problems)
  - [WebSocket MQTT Problems](#websocket-mqtt-problems)
- [AWS IoT Device Shadow service Issues](#device-shadow-issues)
  - [Shadow Connection Problems](#shadow-connection-problems)
  - [Shadow State File Issues](#shadow-state-file-issues)
- [Rules Engine Issues](#rules-engine-issues)
  - [Rule Creation Problems](#rule-creation-problems)
  - [Rule Testing Problems](#rule-testing-problems)
- [OpenSSL Issues](#openssl-issues)
  - [Installation Problems](#installation-problems)
  - [Certificate Generation Issues](#certificate-generation-issues)
- [Network and Connectivity Issues](#network-and-connectivity-issues)
  - [Firewall and Proxy Issues](#firewall-and-proxy-issues)
  - [DNS Resolution Issues](#dns-resolution-issues)
- [Performance and Timing Issues](#performance-and-timing-issues)
  - [API Rate Limiting](#api-rate-limiting)
  - [Connection Timeouts](#connection-timeouts)
- [Getting Additional Help](#getting-additional-help)
  - [Debug Mode Usage](#debug-mode-usage)
  - [AWS IoT Console Verification](#aws-iot-console-verification)
  - [Amazon CloudWatch Logs](#cloudwatch-logs)
  - [Common Resolution Steps](#common-resolution-steps)
  - [Support Resources](#support-resources)

## Common Issues

### AWS Credentials

#### Verify Credentials Are Set
```bash
# Check if credentials are configured
aws sts get-caller-identity

# Check current region
echo $AWS_DEFAULT_REGION

# List environment variables
env | grep AWS
```

#### Common Credential Issues

**Issue: "Unable to locate credentials"**
```bash
# Solution 1: Set environment variables
export AWS_ACCESS_KEY_ID=<your-access-key>
export AWS_SECRET_ACCESS_KEY=<your-secret-key>
export AWS_DEFAULT_REGION=us-east-1

# Solution 2: Use AWS CLI configuration
aws configure

# Solution 3: Check existing configuration
aws configure list
```

**Issue: "You must specify a region"**
```bash
# Set default region
export AWS_DEFAULT_REGION=us-east-1

# Or specify in AWS CLI config
aws configure set region us-east-1
```

**Issue: "The security token included in the request is invalid"**
- **Cause**: Expired temporary credentials or incorrect session token
- **Solution**: Refresh your credentials or remove expired session token
```bash
unset AWS_SESSION_TOKEN
# Then set new credentials
```

### Virtual Environment Issues

#### Verify Virtual Environment
```bash
# Check if venv is active
which python
# Should show: /path/to/your/project/venv/bin/python

# Check Python version
python --version
# Should be 3.7 or higher

# List installed packages
pip list
```

#### Virtual Environment Problems

**Issue: Virtual environment not activated**
```bash
# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# Verify activation
which python
```

**Issue: Wrong Python version**
```bash
# Create new venv with specific Python version
python3.9 -m venv venv
# or
python3 -m venv venv

# Activate and verify
source venv/bin/activate
python --version
```

**Issue: Package installation fails**
```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# If still failing, try individual packages
pip install boto3
pip install awsiotsdk
```

### Dependency Issues

#### Reinstall Dependencies
```bash
# Upgrade all packages
pip install --upgrade -r requirements.txt

# Force reinstall
pip install --force-reinstall -r requirements.txt

# Clear pip cache and reinstall
pip cache purge
pip install -r requirements.txt
```

#### Common Dependency Errors

**Issue: "No module named 'boto3'"**
```bash
# Ensure venv is activated and install
pip install boto3

# Verify installation
python -c "import boto3; print(boto3.__version__)"
```

**Issue: "No module named 'awsiot'"**
```bash
# Install AWS IoT SDK
pip install awsiotsdk

# Verify installation
python -c "import awsiot; print('AWS IoT SDK installed')"
```

**Issue: SSL/TLS certificate errors**
```bash
# On macOS, update certificates
/Applications/Python\ 3.x/Install\ Certificates.command

# Or install certificates package
pip install --upgrade certifi
```

### Permission Issues

#### AWS Identity and Access Management (AWS IAM) Permissions

**Required Permissions for Learning Scripts:**
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

**Minimal Permissions (if iot:* is too broad):**
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

**Common Permission Errors:**

**Issue: "User is not authorized to perform: iot:CreateThing"**
- **Cause**: Insufficient AWS IAM permissions
- **Solution**: Add IoT permissions to your AWS IAM user/role

**Issue: "Access Denied" when creating AWS IAM roles**
- **Cause**: Missing AWS IAM permissions for Rules Engine
- **Solution**: Add AWS IAM permissions or use existing role

### Certificate Issues

#### Certificate File Problems

**Issue: Certificate files not found**
```bash
# Check if certificates directory exists
ls -la certificates/

# Check specific Thing certificates
ls -la certificates/Vehicle-VIN-001/

# Verify certificate files
openssl x509 -in certificates/Vehicle-VIN-001/cert-id.crt -text -noout
```

**Issue: Certificate not attached to Thing**
```bash
# Run registry explorer to check
python iot_registry_explorer.py
# Select option 5 (Describe Thing) and verify certificates are listed
```

**Issue: Policy not attached to certificate**
```bash
# Use certificate manager to attach policy
python certificate_manager.py
# Select option 3 (Attach Policy to Existing Certificate)
```

#### Certificate Status Issues

**Issue: Certificate is INACTIVE**
```bash
# Use certificate manager to activate
python certificate_manager.py
# Select option 5 (Enable/Disable Certificate)
```

**Issue: Certificate validation fails**
```bash
# Check certificate format
head -5 certificates/Vehicle-VIN-001/cert-id.crt
# Should start with: -----BEGIN CERTIFICATE-----

# Validate certificate
openssl x509 -in certificates/Vehicle-VIN-001/cert-id.crt -noout
# No output means valid, error means invalid
```

## MQTT Connection Issues

### Certificate-Based MQTT Problems

#### Connection Diagnostics
```bash
# Use debug mode for detailed error information
python mqtt_client_explorer.py --debug

# Test basic connectivity with OpenSSL
openssl s_client -connect <your-endpoint>:8883 \
  -cert certificates/Vehicle-VIN-001/<cert-id>.crt \
  -key certificates/Vehicle-VIN-001/<cert-id>.key
```

#### Common MQTT Errors

**Issue: "Connection timeout"**
- **Causes**: Network connectivity, incorrect endpoint, firewall
- **Solutions**:
  ```bash
  # Check endpoint
  python iot_registry_explorer.py
  # Select option 8 (Describe Endpoint)
  
  # Test network connectivity
  ping your-iot-endpoint.amazonaws.com
  
  # Check firewall (port 8883 must be open)
  telnet your-iot-endpoint.amazonaws.com 8883
  ```

**Issue: "Authentication failed"**
- **Causes**: Certificate issues, policy problems, Thing not attached
- **Solutions**:
  1. Verify certificate is ACTIVE
  2. Check certificate is attached to Thing
  3. Verify policy is attached to certificate
  4. Check policy permissions include iot:Connect

**Issue: "Subscription/Publish failed"**
- **Causes**: Policy restrictions, invalid topic format
- **Solutions**:
  ```bash
  # Check policy permissions
  # Policy must include: iot:Subscribe, iot:Publish, iot:Receive
  
  # Verify topic format (no spaces, valid characters)
  # Valid: device/sensor/temperature
  # Invalid: device sensor temperature
  ```

#### MQTT Troubleshooting Commands

**Within MQTT Client:**
```bash
📡 MQTT> debug                    # Show connection diagnostics
📡 MQTT> status                   # Display connection info
📡 MQTT> messages                 # Show message history
```

**Debug Output Example:**
```
🔍 Connection Diagnostics:
   Endpoint: a1b2c3d4e5f6g7-ats.iot.us-east-1.amazonaws.com
   Port: 8883
   Client ID: Vehicle-VIN-001-mqtt-12345678
   Certificate: certificates/Vehicle-VIN-001/abc123.crt
   Private Key: certificates/Vehicle-VIN-001/abc123.key
   Connection Status: CONNECTED
   Keep Alive: 30 seconds
   Clean Session: True
```

### WebSocket MQTT Problems

#### WebSocket Diagnostics
```bash
# Verify AWS credentials
aws sts get-caller-identity

# Check AWS IAM permissions
aws iam get-user-policy --user-name <your-username> --policy-name <policy-name>

# Use debug mode
python mqtt_websocket_explorer.py --debug
```

#### Common WebSocket Errors

**Issue: "Credential validation failed"**
- **Cause**: Missing or invalid AWS credentials
- **Solution**: Set proper AWS credentials
  ```bash
  export AWS_ACCESS_KEY_ID=<your-key>
  export AWS_SECRET_ACCESS_KEY=<your-secret>
  export AWS_DEFAULT_REGION=us-east-1
  ```

**Issue: "WebSocket connection failed"**
- **Causes**: Network issues, proxy settings, firewall
- **Solutions**:
  ```bash
  # Test HTTPS connectivity
  curl -I https://your-endpoint.amazonaws.com
  
  # Check proxy settings
  echo $HTTP_PROXY
  echo $HTTPS_PROXY
  ```

**Issue: "SigV4 signing error"**
- **Cause**: Clock skew, invalid credentials
- **Solutions**:
  ```bash
  # Sync system clock
  sudo ntpdate -s time.nist.gov  # Linux/macOS
  
  # Verify credentials are not expired
  aws sts get-caller-identity
  ```

### AWS IoT Device Shadow service Issues

#### Shadow Connection Problems

**Issue: Shadow operations fail**
- **Causes**: Missing shadow permissions, certificate issues
- **Solutions**:
  1. Verify policy includes shadow permissions:
     ```json
     {
       "Action": [
         "iot:GetThingShadow",
         "iot:UpdateThingShadow"
       ]
     }
     ```
  2. Check certificate is attached to correct Thing
  3. Verify Thing name matches shadow operations

**Issue: Delta messages not received**
- **Causes**: Subscription issues, topic permissions
- **Solutions**:
  ```bash
  # Check shadow topic subscriptions
  🌟 Shadow> status
  
  # Verify policy allows shadow topic subscriptions
  # Topics: $aws/things/{thingName}/shadow/update/delta
  ```

#### Shadow State File Issues

**Issue: Local state file not found**
- **Cause**: File creation permissions, path issues
- **Solution**:
  ```bash
  # Check certificates directory permissions
  ls -la certificates/
  
  # Create state file manually if needed
  echo '{"temperature": 20.0, "status": "online"}' > certificates/Vehicle-VIN-001/device_state.json
  ```

**Issue: Invalid JSON in state file**
- **Cause**: Manual editing errors
- **Solution**:
  ```bash
  # Validate JSON format
  python -m json.tool certificates/Vehicle-VIN-001/device_state.json
  
  # Fix or recreate file
  ```

### Rules Engine Issues

#### Rule Creation Problems

**Issue: AWS IAM role creation fails**
- **Causes**: Insufficient AWS IAM permissions, role already exists
- **Solutions**:
  ```bash
  # Check if role exists
  aws iam get-role --role-name IoTRulesEngineRole
  
  # Create role manually if needed
  aws iam create-role --role-name IoTRulesEngineRole --assume-role-policy-document file://trust-policy.json
  ```

**Issue: SQL syntax errors**
- **Causes**: Invalid SQL format, unsupported functions
- **Solutions**:
  - Use simple SELECT, FROM, WHERE clauses
  - Avoid complex SQL functions
  - Test with basic rules first

#### Rule Testing Problems

**Issue: Rule doesn't trigger**
- **Causes**: Topic mismatch, WHERE clause issues, rule disabled
- **Solutions**:
  1. Verify topic pattern matches published topic
  2. Check WHERE clause logic
  3. Ensure rule is ENABLED
  4. Test with simple rule first

**Issue: No rule output received**
- **Causes**: Subscription issues, action configuration
- **Solutions**:
  ```bash
  # Check rule actions
  python iot_rules_explorer.py
  # Select option 2 (Describe Rule)
  
  # Verify subscription to output topic
  # Subscribe to: processed/* or alerts/*
  ```

## OpenSSL Issues

### Installation Problems

**macOS:**
```bash
# Install via Homebrew
brew install openssl

# Add to PATH if needed
export PATH="/usr/local/opt/openssl/bin:$PATH"
```

**Ubuntu/Debian:**
```bash
# Update package list and install
sudo apt-get update
sudo apt-get install openssl

# Verify installation
openssl version
```

**Windows:**
```bash
# Download from: https://slproweb.com/products/Win32OpenSSL.html
# Or use Windows Subsystem for Linux (WSL)

# In WSL:
sudo apt-get install openssl
```

### Certificate Generation Issues

**Issue: OpenSSL command not found**
- **Solution**: Install OpenSSL or add to PATH

**Issue: Permission denied creating certificate files**
- **Solution**: Check directory permissions or run with appropriate privileges

**Issue: Invalid certificate format**
- **Solution**: Verify OpenSSL command syntax and parameters

## Network and Connectivity Issues

### Firewall and Proxy Issues

**Required Ports:**
- **MQTT over TLS**: 8883
- **WebSocket MQTT**: 443
- **HTTPS (API calls)**: 443

**Corporate Firewall:**
```bash
# Test port connectivity
telnet your-iot-endpoint.amazonaws.com 8883
telnet your-iot-endpoint.amazonaws.com 443

# Check proxy settings
echo $HTTP_PROXY
echo $HTTPS_PROXY
echo $NO_PROXY
```

**Proxy Configuration:**
```bash
# Set proxy for HTTPS
export HTTPS_PROXY=http://proxy.company.com:8080

# Bypass proxy for AWS endpoints
export NO_PROXY=amazonaws.com,.amazonaws.com
```

### DNS Resolution Issues

**Issue: Cannot resolve IoT endpoint**
```bash
# Test DNS resolution
nslookup your-iot-endpoint.amazonaws.com

# Use alternative DNS
export AWS_IOT_ENDPOINT=$(dig +short your-iot-endpoint.amazonaws.com)
```

## Performance and Timing Issues

### API Rate Limiting

**Issue: ThrottlingException**
- **Cause**: Too many API calls too quickly
- **Solution**: Add delays between operations or reduce concurrency

**Issue: Eventual consistency delays**
- **Cause**: AWS services need time to propagate changes
- **Solution**: Add wait times after resource creation

### Connection Timeouts

**Issue: MQTT keep-alive timeouts**
- **Cause**: Network instability, long idle periods
- **Solutions**:
  - Reduce keep-alive interval
  - Implement connection retry logic
  - Check network stability

## Getting Additional Help

### Debug Mode Usage

**Enable debug mode for all scripts:**
```bash
python script_name.py --debug
```

**Debug mode provides:**
- Detailed API request/response logging
- Connection diagnostics
- Error stack traces
- Timing information

### AWS IoT Console Verification

**Check resources in AWS Console:**
1. **Things**: AWS IoT Core → Manage → Things
2. **Certificates**: AWS IoT Core → Secure → Certificates
3. **Policies**: AWS IoT Core → Secure → Policies
4. **Rules**: AWS IoT Core → Act → Rules

### Amazon Amazon CloudWatch Logs

**Enable IoT logging for production debugging:**
1. Go to AWS IoT Core → Settings
2. Enable logging with appropriate log level
3. Check Amazon CloudWatch Logs for detailed error information

### Common Resolution Steps

**When all else fails:**
1. **Start fresh**: Run cleanup script and begin again
2. **Check AWS status**: Visit AWS Service Health Dashboard
3. **Verify account limits**: Check AWS service quotas
4. **Test with minimal setup**: Use simplest possible configuration
5. **Compare with working examples**: Use provided sample data

### Support Resources

- **AWS IoT Documentation**: https://docs.aws.amazon.com/iot/
- **AWS IoT Developer Guide**: https://docs.aws.amazon.com/iot/latest/developerguide/
- **AWS Support**: https://aws.amazon.com/support/
- **AWS Forums**: https://forums.aws.amazon.com/forum.jspa?forumID=210