#!/usr/bin/env python3
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

"""
AWS IoT Rules Engine Explorer
Educational tool for learning AWS IoT Rules Engine through hands-on rule creation and management.
"""
import boto3
import json
import time
from datetime import datetime
from botocore.exceptions import ClientError
import os
from awsiot import mqtt_connection_builder
from awscrt import io, mqtt
from concurrent.futures import Future

def display_aws_context():
    """Display current AWS account and region information"""
    try:
        sts = boto3.client('sts')
        iot = boto3.client('iot')
        identity = sts.get_caller_identity()
        
        print(f"\n🌍 AWS Context Information:")
        print(f"   Account ID: {identity['Account']}")
        print(f"   Region: {iot.meta.region_name}")
    except Exception as e:
        print(f"\n⚠️ Could not retrieve AWS context: {str(e)}")
        print(f"   Make sure AWS credentials are configured")
    print()

class IoTRulesExplorer:
    def __init__(self, debug=False):
        self.iot = boto3.client('iot')
        self.iam = boto3.client('iam')
        self.debug_mode = debug
        self.rule_role_name = "IoTRulesEngineRole"
        
    def print_header(self, title):
        """Print formatted header"""
        print(f"\n⚙️ {title}")
        print("=" * 60)
    
    def print_step(self, step, description):
        """Print step with formatting"""
        print(f"\n🔧 Step {step}: {description}")
        print("-" * 50)
    
    def validate_sql_clause(self, clause, clause_type):
        """Validate and sanitize SQL clause input"""
        if not clause:
            return ""
        
        # Remove potentially dangerous characters and patterns
        import re
        
        # For IoT Rules Engine SQL, allow alphanumeric, spaces, common operators, and IoT-specific functions
        if clause_type == "SELECT":
            # Allow SELECT clause patterns: *, field names, functions like timestamp()
            allowed_pattern = r'^[a-zA-Z0-9_\s,.*()=<>!+-]+$'
        elif clause_type == "WHERE":
            # Allow WHERE clause patterns: comparisons, logical operators
            allowed_pattern = r'^[a-zA-Z0-9_\s=<>!()\'".,-]+$'
        else:
            allowed_pattern = r'^[a-zA-Z0-9_\s]+$'
        
        if not re.match(allowed_pattern, clause):
            raise ValueError(f"Invalid characters in {clause_type} clause. Only alphanumeric characters, spaces, and basic operators are allowed.")
        
        # Additional validation for common injection patterns
        dangerous_patterns = ['--', '/*', '*/', ';', 'DROP', 'DELETE', 'INSERT', 'UPDATE', 'EXEC']
        clause_upper = clause.upper()
        for pattern in dangerous_patterns:
            if pattern in clause_upper:
                raise ValueError(f"Potentially dangerous pattern '{pattern}' detected in {clause_type} clause.")
        
        return clause.strip()
    
    def validate_topic_pattern(self, topic):
        """Validate IoT topic pattern"""
        if not topic:
            return ""
        
        import re
        # IoT topics allow alphanumeric, hyphens, underscores, forward slashes, and wildcards
        allowed_pattern = r'^[a-zA-Z0-9_/+-]+$'
        
        if not re.match(allowed_pattern, topic):
            raise ValueError("Invalid characters in topic pattern. Only alphanumeric characters, hyphens, underscores, forward slashes, and + wildcards are allowed.")
        
        return topic.strip()
    
    def safe_operation(self, func, operation_name, **kwargs):
        """Execute operation with error handling and debug info"""
        try:
            if self.debug_mode:
                print(f"🔍 DEBUG: {operation_name}")
                print(f"📥 Input: {json.dumps(kwargs, indent=2, default=str)}")
            
            response = func(**kwargs)
            
            if self.debug_mode:
                print(f"✅ {operation_name} completed")
                if response:
                    print(f"📤 Output: {json.dumps(response, indent=2, default=str)[:500]}{'...' if len(str(response)) > 500 else ''}")
            
            return response, True
        except ClientError as e:
            print(f"❌ {operation_name} failed: {e.response['Error']['Message']}")
            if self.debug_mode:
                print(f"🔍 DEBUG: Error code: {e.response['Error']['Code']}")
            return None, False
        except Exception as e:
            print(f"❌ {operation_name} failed: {str(e)}")
            return None, False
    
    def list_rules(self):
        """List all IoT rules with details"""
        self.print_header("List IoT Rules")
        
        response, success = self.safe_operation(
            self.iot.list_topic_rules,
            "List IoT Rules"
        )
        
        if not success:
            return
        
        rules = response.get('rules', [])
        
        if not rules:
            print("📋 No IoT Rules found in your account")
            print("💡 Create your first rule using option 2")
            return
        
        print(f"📋 Found {len(rules)} IoT Rules:")
        print()
        
        for i, rule in enumerate(rules, 1):
            rule_name = rule['ruleName']
            created_at = rule.get('createdAt', 'Unknown')
            rule_disabled = rule.get('ruleDisabled', False)
            status = "🔴 DISABLED" if rule_disabled else "🟢 ENABLED"
            
            print(f"{i}. {rule_name} - {status}")
            print(f"   📅 Created: {created_at}")
            
            if self.debug_mode:
                print(f"   🔍 DEBUG: Rule ARN: {rule.get('ruleArn', 'N/A')}")
            
            # Get rule details
            rule_response, rule_success = self.safe_operation(
                self.iot.get_topic_rule,
                f"Get rule details for {rule_name}",
                ruleName=rule_name
            )
            
            if rule_success and rule_response:
                rule_payload = rule_response.get('rule', {})
                sql = rule_payload.get('sql', 'N/A')
                actions = rule_payload.get('actions', [])
                
                print(f"   📝 SQL: {sql}")
                print(f"   🎯 Actions: {len(actions)} configured")
                
                for j, action in enumerate(actions, 1):
                    if 'republish' in action:
                        topic = action['republish'].get('topic', 'N/A')
                        print(f"      {j}. Republish to: {topic}")
                    elif 's3' in action:
                        bucket = action['s3'].get('bucketName', 'N/A')
                        print(f"      {j}. S3 to bucket: {bucket}")
                    elif 'lambda' in action:
                        function_arn = action['lambda'].get('functionArn', 'N/A')
                        print(f"      {j}. Lambda: {function_arn.split(':')[-1] if ':' in function_arn else function_arn}")
                    else:
                        action_type = list(action.keys())[0] if action else 'Unknown'
                        print(f"      {j}. {action_type}")
            
            print()
    
    def describe_rule(self):
        """Describe a specific IoT rule in detail"""
        self.print_header("Describe IoT Rule")
        
        # List rules first
        response, success = self.safe_operation(
            self.iot.list_topic_rules,
            "List IoT Rules for selection"
        )
        
        if not success:
            return
        
        rules = response.get('rules', [])
        
        if not rules:
            print("📋 No IoT Rules found")
            return
        
        print(f"📋 Available Rules:")
        for i, rule in enumerate(rules, 1):
            status = "🔴 DISABLED" if rule.get('ruleDisabled', False) else "🟢 ENABLED"
            print(f"   {i}. {rule['ruleName']} - {status}")
        
        while True:
            try:
                choice = int(input(f"\nSelect rule to describe (1-{len(rules)}): ")) - 1
                if 0 <= choice < len(rules):
                    selected_rule = rules[choice]['ruleName']
                    break
                else:
                    print(f"❌ Invalid selection. Please enter 1-{len(rules)}")
            except ValueError:
                print("❌ Please enter a valid number")
        
        # Get detailed rule information
        rule_response, rule_success = self.safe_operation(
            self.iot.get_topic_rule,
            f"Get detailed rule information for {selected_rule}",
            ruleName=selected_rule
        )
        
        if not rule_success:
            return
        
        rule_payload = rule_response.get('rule', {})
        
        print(f"\n📋 Rule Details: {selected_rule}")
        print("-" * 40)
        
        # Basic information
        print(f"📝 SQL Statement:")
        print(f"   {rule_payload.get('sql', 'N/A')}")
        
        print(f"\n📖 SQL Breakdown:")
        sql = rule_payload.get('sql', '')
        if 'SELECT' in sql.upper():
            select_part = sql.split('FROM')[0].replace('SELECT', '').strip()
            print(f"   🔍 SELECT: {select_part}")
        
        if 'FROM' in sql.upper():
            from_part = sql.split('FROM')[1].split('WHERE')[0].strip() if 'WHERE' in sql.upper() else sql.split('FROM')[1].strip()
            print(f"   📥 FROM: {from_part}")
        
        if 'WHERE' in sql.upper():
            where_part = sql.split('WHERE')[1].strip()
            print(f"   🔍 WHERE: {where_part}")
        
        # Actions
        actions = rule_payload.get('actions', [])
        print(f"\n🎯 Actions ({len(actions)}):")
        
        for i, action in enumerate(actions, 1):
            print(f"   {i}. Action Type: {list(action.keys())[0] if action else 'Unknown'}")
            
            if 'republish' in action:
                republish = action['republish']
                print(f"      📤 Target Topic: {republish.get('topic', 'N/A')}")
                print(f"      🔑 Role ARN: {republish.get('roleArn', 'N/A')}")
                if 'qos' in republish:
                    print(f"      🏷️  QoS: {republish['qos']}")
            
            elif 's3' in action:
                s3_action = action['s3']
                print(f"      🪣 Bucket: {s3_action.get('bucketName', 'N/A')}")
                print(f"      📁 Key: {s3_action.get('key', 'N/A')}")
                print(f"      🔑 Role ARN: {s3_action.get('roleArn', 'N/A')}")
            
            elif 'lambda' in action:
                lambda_action = action['lambda']
                print(f"      ⚡ Function ARN: {lambda_action.get('functionArn', 'N/A')}")
        
        # Error action
        error_action = rule_payload.get('errorAction')
        if error_action:
            print(f"\n❌ Error Action:")
            error_type = list(error_action.keys())[0] if error_action else 'Unknown'
            print(f"   Type: {error_type}")
            if 'republish' in error_action:
                print(f"   Topic: {error_action['republish'].get('topic', 'N/A')}")
        
        # Rule metadata
        print(f"\n📊 Rule Metadata:")
        print(f"   🔄 Status: {'🔴 DISABLED' if rule_payload.get('ruleDisabled', False) else '🟢 ENABLED'}")
        print(f"   📅 Created: {rule_payload.get('createdAt', 'N/A')}")
        
        if self.debug_mode:
            print(f"\n🔍 DEBUG: Complete Rule Payload:")
            print(json.dumps(rule_payload, indent=2, default=str))
    
    def create_rule(self):
        """Interactive rule creation with guided SQL building"""
        self.print_header("Create IoT Rule")
        
        print("🎓 Learning Objectives:")
        print("• Understand IoT Rules Engine SQL syntax")
        print("• Learn topic filtering and message routing")
        print("• Practice SELECT, FROM, and WHERE clauses")
        print("• Configure republish actions with proper IAM roles")
        print()
        
        # Step 1: Rule name
        while True:
            rule_name = input("📝 Enter rule name (alphanumeric and underscores only): ").strip()
            if rule_name and rule_name.replace('_', '').isalnum():
                break
            else:
                print("❌ Rule name must contain only alphanumeric characters and underscores")
        
        print(f"✅ Rule name: {rule_name}")
        
        # Step 2: Rule description
        rule_description = input("📖 Enter rule description (optional): ").strip()
        if not rule_description:
            rule_description = f"Learning rule for processing IoT messages"
        
        print(f"✅ Rule description: {rule_description}")
        
        # Step 3: Build SQL statement
        print(f"\n📖 Building SQL Statement for IoT Rules Engine")
        print(f"💡 Template: SELECT <attributes> FROM 'testRulesEngineTopic/<deviceId>/<eventType>' WHERE <condition>")
        
        # Event type selection
        event_types = [
            "temperature",
            "humidity", 
            "pressure",
            "motion",
            "door",
            "alarm",
            "status",
            "battery"
        ]
        
        print(f"\n🎯 Available Event Types:")
        for i, event_type in enumerate(event_types, 1):
            print(f"   {i}. {event_type}")
        print(f"   {len(event_types) + 1}. Custom event type")
        
        while True:
            try:
                choice = int(input(f"\nSelect event type (1-{len(event_types) + 1}): "))
                if 1 <= choice <= len(event_types):
                    selected_event_type = event_types[choice - 1]
                    break
                elif choice == len(event_types) + 1:
                    selected_event_type = input("Enter custom event type: ").strip()
                    if selected_event_type:
                        break
                    else:
                        print("❌ Event type cannot be empty")
                else:
                    print(f"❌ Invalid selection")
            except ValueError:
                print("❌ Please enter a valid number")
        
        # Topic pattern
        topic_pattern = f"testRulesEngineTopic/+/{selected_event_type}"
        print(f"✅ Topic pattern: {topic_pattern}")
        
        # SELECT clause based on event type
        print(f"\n🔍 SELECT Clause - Attributes for {selected_event_type} events:")
        
        # Event-specific attributes
        event_attributes = {
            "temperature": ["*", "deviceId, timestamp, temperature", "deviceId, temperature, location"],
            "humidity": ["*", "deviceId, timestamp, humidity", "deviceId, humidity, location"],
            "pressure": ["*", "deviceId, timestamp, pressure", "deviceId, pressure, altitude"],
            "motion": ["*", "deviceId, timestamp, detected", "deviceId, detected, location"],
            "door": ["*", "deviceId, timestamp, status", "deviceId, status, location"],
            "alarm": ["*", "deviceId, timestamp, alertType", "deviceId, alertType, severity"],
            "status": ["*", "deviceId, timestamp, status", "deviceId, status, uptime"],
            "battery": ["*", "deviceId, timestamp, level", "deviceId, level, voltage"]
        }
        
        # Get attributes for selected event type or use generic ones
        available_attributes = event_attributes.get(selected_event_type, ["*", "deviceId, timestamp, value", "deviceId, value, status"])
        available_attributes.append("Custom selection")
        
        for i, attr in enumerate(available_attributes, 1):
            print(f"   {i}. {attr}")
        
        while True:
            try:
                choice = int(input(f"\nSelect attributes (1-{len(available_attributes)}): "))
                if 1 <= choice <= len(available_attributes) - 1:
                    select_clause = available_attributes[choice - 1]
                    break
                elif choice == len(available_attributes):
                    select_clause = input("Enter custom SELECT clause: ").strip()
                    if select_clause:
                        break
                    else:
                        print("❌ SELECT clause cannot be empty")
                else:
                    print(f"❌ Invalid selection")
            except ValueError:
                print("❌ Please enter a valid number")
        
        print(f"✅ SELECT: {select_clause}")
        
        # WHERE clause (optional) with event-specific examples
        print(f"\n🔍 WHERE Clause (Optional) - Filter {selected_event_type} messages:")
        
        # Event-specific WHERE examples
        where_examples = {
            "temperature": ["temperature > 25", "temperature < 0", "location = 'warehouse'"],
            "humidity": ["humidity > 80", "humidity < 30", "location = 'greenhouse'"],
            "pressure": ["pressure > 1013", "pressure < 950", "altitude > 1000"],
            "motion": ["detected = true", "location = 'entrance'", "timestamp > timestamp() - 300000"],
            "door": ["status = 'open'", "status = 'closed'", "location = 'main_entrance'"],
            "alarm": ["alertType = 'fire'", "severity = 'high'", "alertType = 'intrusion'"],
            "status": ["status = 'offline'", "uptime < 3600", "status = 'maintenance'"],
            "battery": ["level < 20", "level < 10", "voltage < 3.0"]
        }
        
        examples = where_examples.get(selected_event_type, ["value > 25", "status = 'active'", "timestamp > timestamp() - 3600000"])
        print(f"💡 Examples for {selected_event_type}:")
        for example in examples:
            print(f"   • {example}")
        
        add_where = input("\nAdd WHERE condition? (y/N): ").strip().lower()
        where_clause = ""
        
        if add_where == 'y':
            where_clause = input("Enter WHERE condition: ").strip()
            if where_clause:
                print(f"✅ WHERE: {where_clause}")
            else:
                print("⚠️ Empty WHERE clause, proceeding without filter")
        
        # Build complete SQL with input validation
        try:
            # Validate and sanitize inputs to prevent injection
            safe_select_clause = self.validate_sql_clause(select_clause, "SELECT")
            safe_topic_pattern = self.validate_topic_pattern(topic_pattern)
            safe_where_clause = self.validate_sql_clause(where_clause, "WHERE") if where_clause else ""
            
            sql_statement = "SELECT {} FROM '{}'".format(safe_select_clause, safe_topic_pattern)
            if safe_where_clause:
                sql_statement += " WHERE {}".format(safe_where_clause)
        except ValueError as e:
            print(f"❌ Input validation error: {e}")
            print("💡 Please use only alphanumeric characters, spaces, and basic operators")
            return
        
        print(f"\n📝 Complete SQL Statement:")
        print(f"   {sql_statement}")
        
        # Step 4: Configure republish action
        print(f"\n📤 Republish Action Configuration")
        
        target_topic = input("Enter target topic for republishing (e.g., 'processed/temperature'): ").strip()
        if not target_topic:
            target_topic = f"processed/{selected_event_type}"
            print(f"✅ Using default target topic: {target_topic}")
        
        # Step 5: Create/verify IAM role
        print(f"\n🔑 Setting up IAM Role for Rule Actions")
        role_arn = self.ensure_iot_rule_role()
        
        if not role_arn:
            print("❌ Failed to create/verify IAM role. Cannot create rule.")
            return
        
        # Step 6: Create the rule
        print(f"\n🔧 Creating IoT Rule...")
        
        rule_payload = {
            'sql': sql_statement,
            'description': rule_description,
            'actions': [
                {
                    'republish': {
                        'topic': target_topic,
                        'roleArn': role_arn,
                        'qos': 1
                    }
                }
            ],
            'ruleDisabled': False
        }
        
        if self.debug_mode:
            print(f"🔍 DEBUG: Rule payload:")
            print(json.dumps(rule_payload, indent=2))
        
        # Try creating the rule with retry for IAM propagation
        max_retries = 3
        for attempt in range(max_retries):
            response, success = self.safe_operation(
                self.iot.create_topic_rule,
                f"Create IoT Rule '{rule_name}' (attempt {attempt + 1}/{max_retries})",
                ruleName=rule_name,
                topicRulePayload=rule_payload
            )
            
            if success:
                break
            elif attempt < max_retries - 1:
                # Check if it's an IAM role propagation issue
                print(f"⏳ IAM role may still be propagating. Waiting 10 seconds before retry...")
                time.sleep(10)  # nosemgrep: arbitrary-sleep
            else:
                print(f"❌ Failed to create rule after {max_retries} attempts")
                return
        
        if success:
            print(f"\n🎉 Rule '{rule_name}' created successfully!")
            print(f"\n📋 Rule Summary:")
            print(f"   📝 Name: {rule_name}")
            print(f"   📥 Source Topic: {topic_pattern}")
            print(f"   📤 Target Topic: {target_topic}")
            print(f"   🔍 SQL: {sql_statement}")
            print(f"   🔑 Role: {role_arn}")
            
            print(f"\n💡 Testing Your Rule:")
            print(f"   1. Publish a message to: testRulesEngineTopic/device123/{selected_event_type}")
            print(f"   2. Subscribe to: {target_topic}")
            print(f"   3. Check if the message is routed correctly")
            
            print(f"\n📖 Example test message:")
            example_message = {
                "deviceId": "device123",
                "timestamp": int(time.time() * 1000),
                "value": 25.5 if selected_event_type in ["temperature", "humidity", "pressure"] else "active"
            }
            print(f"   {json.dumps(example_message, indent=2)}")
    
    def ensure_iot_rule_role(self):
        """Create or verify IAM role for IoT Rules Engine"""
        try:
            # Check if role exists
            response = self.iam.get_role(RoleName=self.rule_role_name)
            role_arn = response['Role']['Arn']
            
            if self.debug_mode:
                print(f"🔍 DEBUG: Using existing IAM role: {role_arn}")
            
            print(f"✅ Using existing IAM role: {self.rule_role_name}")
            return role_arn
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchEntity':
                # Role doesn't exist, create it
                print(f"🔧 Creating IAM role: {self.rule_role_name}")
                return self.create_iot_rule_role()
            else:
                print(f"❌ Error checking IAM role: {e.response['Error']['Message']}")
                return None
    
    def create_iot_rule_role(self):
        """Create IAM role with necessary permissions for IoT Rules"""
        trust_policy = {
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
        
        # Create role
        response, success = self.safe_operation(
            self.iam.create_role,
            f"Create IAM role '{self.rule_role_name}'",
            RoleName=self.rule_role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description="IAM role for AWS IoT Rules Engine learning exercises"
        )
        
        if not success:
            return None
        
        role_arn = response['Role']['Arn']
        
        # Create and attach policy for IoT actions
        policy_document = {
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
        
        policy_name = "IoTRulesEnginePolicy"
        
        # Create policy
        policy_response, policy_success = self.safe_operation(
            self.iam.create_policy,
            f"Create IAM policy '{policy_name}'",
            PolicyName=policy_name,
            PolicyDocument=json.dumps(policy_document),
            Description="Policy for IoT Rules Engine to publish messages"
        )
        
        if policy_success:
            policy_arn = policy_response['Policy']['Arn']
            
            # Attach policy to role
            attach_response, attach_success = self.safe_operation(
                self.iam.attach_role_policy,
                f"Attach policy to role",
                RoleName=self.rule_role_name,
                PolicyArn=policy_arn
            )
            
            if attach_success:
                print(f"✅ IAM role and policy created successfully")
                print(f"⏳ Waiting for IAM role propagation (10 seconds)...")
                # Wait longer for IAM consistency
                time.sleep(10)  # nosemgrep: arbitrary-sleep
                return role_arn
        
        return None
    
    def manage_rule(self):
        """Enable, disable, or delete rules"""
        self.print_header("Manage IoT Rules")
        
        # List rules first
        response, success = self.safe_operation(
            self.iot.list_topic_rules,
            "List IoT Rules for management"
        )
        
        if not success:
            return
        
        rules = response.get('rules', [])
        
        if not rules:
            print("📋 No IoT Rules found")
            return
        
        print(f"📋 Available Rules:")
        for i, rule in enumerate(rules, 1):
            status = "🔴 DISABLED" if rule.get('ruleDisabled', False) else "🟢 ENABLED"
            print(f"   {i}. {rule['ruleName']} - {status}")
        
        while True:
            try:
                choice = int(input(f"\nSelect rule to manage (1-{len(rules)}): ")) - 1
                if 0 <= choice < len(rules):
                    selected_rule = rules[choice]
                    break
                else:
                    print(f"❌ Invalid selection. Please enter 1-{len(rules)}")
            except ValueError:
                print("❌ Please enter a valid number")
        
        rule_name = selected_rule['ruleName']
        is_disabled = selected_rule.get('ruleDisabled', False)
        
        print(f"\n🔧 Managing Rule: {rule_name}")
        print(f"📊 Current Status: {'🔴 DISABLED' if is_disabled else '🟢 ENABLED'}")
        
        print(f"\n📋 Management Options:")
        if is_disabled:
            print(f"   1. 🟢 Enable rule")
        else:
            print(f"   1. 🔴 Disable rule")
        print(f"   2. 🗑️ Delete rule")
        print(f"   3. ↩️ Cancel")
        
        while True:
            try:
                action = int(input(f"\nSelect action (1-3): "))
                if action in [1, 2, 3]:
                    break
                else:
                    print("❌ Invalid selection. Please enter 1-3")
            except ValueError:
                print("❌ Please enter a valid number")
        
        if action == 1:
            # Enable/Disable rule
            new_status = not is_disabled
            action_name = "Enable" if new_status else "Disable"
            
            response, success = self.safe_operation(
                self.iot.replace_topic_rule,
                f"{action_name} rule '{rule_name}'",
                ruleName=rule_name,
                topicRulePayload={
                    'sql': 'SELECT * FROM "temp"',  # Placeholder, will be replaced
                    'ruleDisabled': not new_status,
                    'actions': []
                }
            )
            
            # Get current rule to preserve settings
            rule_response, rule_success = self.safe_operation(
                self.iot.get_topic_rule,
                f"Get current rule settings",
                ruleName=rule_name
            )
            
            if rule_success:
                current_rule = rule_response['rule']
                current_rule['ruleDisabled'] = not new_status
                
                response, success = self.safe_operation(
                    self.iot.replace_topic_rule,
                    f"{action_name} rule '{rule_name}'",
                    ruleName=rule_name,
                    topicRulePayload=current_rule
                )
                
                if success:
                    status_text = "🟢 ENABLED" if new_status else "🔴 DISABLED"
                    print(f"✅ Rule '{rule_name}' is now {status_text}")
        
        elif action == 2:
            # Delete rule
            confirm = input(f"⚠️ Are you sure you want to delete rule '{rule_name}'? (y/N): ").strip().lower()
            
            if confirm == 'y':
                response, success = self.safe_operation(
                    self.iot.delete_topic_rule,
                    f"Delete rule '{rule_name}'",
                    ruleName=rule_name
                )
                
                if success:
                    print(f"✅ Rule '{rule_name}' deleted successfully")
            else:
                print("❌ Rule deletion cancelled")
        
        elif action == 3:
            print("↩️ Management cancelled")
    
    def test_rule(self):
        """Test IoT rules with sample messages"""
        self.print_header("Test IoT Rule")
        
        print("🎓 Learning Objectives:")
        print("• Test rule topic matching and WHERE conditions")
        print("• Understand message routing behavior")
        print("• Practice with matching and non-matching messages")
        print("• Observe real-time rule processing")
        print()
        
        # List rules first
        response, success = self.safe_operation(
            self.iot.list_topic_rules,
            "List IoT Rules for testing"
        )
        
        if not success:
            return
        
        rules = response.get('rules', [])
        
        if not rules:
            print("📋 No IoT Rules found")
            print("💡 Create a rule first using option 3")
            return
        
        print(f"📋 Available Rules:")
        for i, rule in enumerate(rules, 1):
            status = "🔴 DISABLED" if rule.get('ruleDisabled', False) else "🟢 ENABLED"
            print(f"   {i}. {rule['ruleName']} - {status}")
        
        while True:
            try:
                choice = int(input(f"\nSelect rule to test (1-{len(rules)}): ")) - 1
                if 0 <= choice < len(rules):
                    selected_rule = rules[choice]
                    break
                else:
                    print(f"❌ Invalid selection. Please enter 1-{len(rules)}")
            except ValueError:
                print("❌ Please enter a valid number")
        
        rule_name = selected_rule['ruleName']
        
        # Get rule details
        rule_response, rule_success = self.safe_operation(
            self.iot.get_topic_rule,
            f"Get rule details for testing",
            ruleName=rule_name
        )
        
        if not rule_success:
            return
        
        rule_payload = rule_response.get('rule', {})
        sql_statement = rule_payload.get('sql', '')
        
        print(f"\n📋 Testing Rule: {rule_name}")
        print(f"📝 SQL: {sql_statement}")
        
        # Parse SQL to extract topic pattern
        topic_pattern = self.extract_topic_from_sql(sql_statement)
        where_condition = self.extract_where_from_sql(sql_statement)
        
        if topic_pattern:
            print(f"📥 Source Topic Pattern: {topic_pattern}")
        if where_condition:
            print(f"🔍 WHERE Condition: {where_condition}")
        
        # Get republish target topics
        actions = rule_payload.get('actions', [])
        target_topics = []
        for action in actions:
            if 'republish' in action:
                target_topics.append(action['republish'].get('topic', 'unknown'))
        
        if target_topics:
            print(f"📤 Target Topics: {', '.join(target_topics)}")
        
        # Get device selection
        selected_device = self.select_device_with_certificates()
        if not selected_device:
            return
        
        # Get IoT endpoint
        endpoint_response, endpoint_success = self.safe_operation(
            self.iot.describe_endpoint,
            "Get IoT endpoint",
            endpointType='iot:Data-ATS'
        )
        
        if not endpoint_success:
            print("❌ Cannot get IoT endpoint. Testing requires MQTT connection.")
            return
        
        endpoint = endpoint_response['endpointAddress']
        
        # Start interactive testing
        self.run_rule_testing(endpoint, selected_device, rule_name, topic_pattern, where_condition, target_topics)
    
    def extract_topic_from_sql(self, sql):
        """Extract topic pattern from SQL FROM clause"""
        try:
            if 'FROM' in sql.upper():
                from_part = sql.split('FROM')[1].split('WHERE')[0].strip() if 'WHERE' in sql.upper() else sql.split('FROM')[1].strip()
                # Remove quotes
                topic = from_part.strip("'\"")
                return topic
        except:
            pass
        return None
    
    def extract_where_from_sql(self, sql):
        """Extract WHERE condition from SQL"""
        try:
            if 'WHERE' in sql.upper():
                where_part = sql.split('WHERE')[1].strip()
                return where_part
        except:
            pass
        return None
    
    def select_device_with_certificates(self):
        """Select device with certificates like other scripts"""
        print(f"\n🔍 Finding devices with certificates...")
        
        cert_dir = "certificates"
        if not os.path.exists(cert_dir):
            print("❌ No certificates directory found.")
            print("💡 Run certificate_manager.py first to create certificates")
            return None
        
        # Find available devices with certificates
        available_devices = []
        for thing_dir in os.listdir(cert_dir):
            thing_path = os.path.join(cert_dir, thing_dir)
            if os.path.isdir(thing_path):
                cert_files = [f for f in os.listdir(thing_path) if f.endswith('.crt')]
                if cert_files:
                    cert_id = cert_files[0].replace('.crt', '')
                    cert_path = os.path.join(thing_path, f"{cert_id}.crt")
                    key_path = os.path.join(thing_path, f"{cert_id}.key")
                    if os.path.exists(key_path):
                        available_devices.append({
                            'thing_name': thing_dir,
                            'cert_path': cert_path,
                            'key_path': key_path,
                            'cert_id': cert_id
                        })
        
        if not available_devices:
            print("❌ No devices with certificates found.")
            print("💡 Run certificate_manager.py first to create certificates")
            return None
        
        print(f"📋 Found {len(available_devices)} device(s) with certificates:")
        for i, device in enumerate(available_devices, 1):
            print(f"   {i}. {device['thing_name']}")
        
        if len(available_devices) == 1:
            selected_device = available_devices[0]
            print(f"✅ Using device: {selected_device['thing_name']}")
        else:
            while True:
                try:
                    choice = int(input(f"\nSelect device (1-{len(available_devices)}): ")) - 1
                    if 0 <= choice < len(available_devices):
                        selected_device = available_devices[choice]
                        print(f"✅ Selected device: {selected_device['thing_name']}")
                        break
                    else:
                        print(f"❌ Invalid selection")
                except ValueError:
                    print("❌ Please enter a valid number")
        
        return selected_device
    
    def run_rule_testing(self, endpoint, device_info, rule_name, topic_pattern, where_condition, target_topics):
        """Run interactive rule testing with AWS IoT SDK"""
        print(f"\n🧪 Interactive Rule Testing")
        print(f"📡 Connecting to: {endpoint}")
        print(f"📱 Using device: {device_info['thing_name']}")
        
        # Setup event loop and connection
        event_loop_group = io.EventLoopGroup(1)
        host_resolver = io.DefaultHostResolver(event_loop_group)
        client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)
        
        messages_received = []
        
        def on_message_received(topic, payload, dup, qos, retain, **kwargs):
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            message_data = {
                'timestamp': timestamp,
                'topic': topic,
                'payload': payload.decode('utf-8')
            }
            messages_received.append(message_data)
            print(f"\n🔔 RULE OUTPUT RECEIVED [{timestamp}]")
            print(f"📤 Topic: {topic}")
            print(f"💬 Message: {payload.decode('utf-8')}")
            print(f"✅ Rule '{rule_name}' processed and forwarded the message!")
        
        # Create MQTT connection
        mqtt_connection = mqtt_connection_builder.mtls_from_path(
            endpoint=endpoint,
            cert_filepath=device_info['cert_path'],
            pri_key_filepath=device_info['key_path'],
            client_bootstrap=client_bootstrap,
            client_id=f"rule-tester-{device_info['thing_name']}",
            clean_session=False,
            keep_alive_secs=30,
            on_connection_interrupted=lambda connection, error, **kwargs: print(f"⚠️ Connection interrupted: {error}"),
            on_connection_resumed=lambda connection, return_code, session_present, **kwargs: print(f"✅ Connection resumed")
        )
        
        try:
            print(f"🔌 Connecting to AWS IoT...")
            connect_future = mqtt_connection.connect()
            connect_future.result(timeout=10)
            print(f"✅ Connected to AWS IoT")
            
            # Subscribe to target topics
            for topic in target_topics:
                subscribe_future, _ = mqtt_connection.subscribe(
                    topic=topic,
                    qos=mqtt.QoS.AT_LEAST_ONCE,
                    callback=on_message_received
                )
                subscribe_future.result(timeout=10)
                print(f"📡 Subscribed to target topic: {topic}")
            
            print(f"\n🎯 Rule Testing Instructions:")
            print(f"• You'll be asked if each message should match the rule")
            print(f"• Topic matching: Does the topic fit the pattern?")
            print(f"• WHERE condition: Does the message content match the filter?")
            print(f"• Watch for rule output messages on target topics")
            print(f"• Type 'quit' to exit testing")
            
            # Interactive testing loop
            test_count = 0
            while True:
                test_count += 1
                print(f"\n{'='*60}")
                print(f"🧪 Test Message #{test_count}")
                print(f"{'='*60}")
                
                # Ask about topic matching
                print(f"\n📥 Topic Pattern: {topic_pattern or 'No specific pattern'}")
                topic_should_match = input("Should this message MATCH the topic pattern? (y/n/quit): ").strip().lower()
                
                if topic_should_match == 'quit':
                    break
                
                # Generate test topic
                if topic_should_match == 'y':
                    test_topic = self.generate_matching_topic(topic_pattern)
                else:
                    test_topic = self.generate_non_matching_topic(topic_pattern)
                
                print(f"📡 Generated Topic: {test_topic}")
                
                # Ask about WHERE condition
                where_should_match = 'y'  # Default if no WHERE clause
                if where_condition:
                    print(f"\n🔍 WHERE Condition: {where_condition}")
                    where_should_match = input("Should this message MATCH the WHERE condition? (y/n): ").strip().lower()
                
                # Generate test message
                test_message = self.generate_test_message(where_condition, where_should_match == 'y')
                
                print(f"\n📝 Test Message:")
                print(f"📡 Topic: {test_topic}")
                print(f"💬 Payload: {json.dumps(test_message, indent=2)}")
                
                # Predict outcome
                should_trigger = (topic_should_match == 'y') and (where_should_match == 'y')
                print(f"\n🔮 Prediction: Rule {'SHOULD' if should_trigger else 'should NOT'} trigger")
                
                # Publish message
                print(f"\n📤 Publishing test message...")
                publish_future, _ = mqtt_connection.publish(
                    topic=test_topic,
                    payload=json.dumps(test_message),
                    qos=mqtt.QoS.AT_LEAST_ONCE
                )
                publish_future.result(timeout=10)
                
                # Wait for potential rule output
                print(f"⏳ Waiting 3 seconds for rule processing...")
                time.sleep(3)  # nosemgrep: arbitrary-sleep
                
                # Simple check for recent messages
                recent_count = len([msg for msg in messages_received[-3:]])
                
                if should_trigger and recent_count == 0:
                    print(f"⚠️ Expected rule to trigger but no output received")
                elif not should_trigger and recent_count > 0:
                    print(f"⚠️ Rule triggered unexpectedly")
                elif should_trigger:
                    print(f"✅ Rule triggered as expected!")
                else:
                    print(f"✅ Rule correctly did not trigger")
                
                input("\nPress Enter to continue to next test...")
        
        except Exception as e:
            print(f"❌ Testing error: {str(e)}")
        finally:
            print(f"\n🔌 Disconnecting from AWS IoT...")
            disconnect_future = mqtt_connection.disconnect()
            disconnect_future.result(timeout=10)
            print(f"✅ Disconnected from AWS IoT")
    
    def generate_matching_topic(self, topic_pattern):
        """Generate a topic that matches the pattern"""
        if not topic_pattern:
            return "testRulesEngineTopic/device123/temperature"
        
        # Replace + wildcards with actual values
        topic = topic_pattern.replace('+', 'device123')
        return topic
    
    def generate_non_matching_topic(self, topic_pattern):
        """Generate a topic that doesn't match the pattern"""
        if not topic_pattern:
            return "different/topic/structure"
        
        # Create a different structure
        return "nonmatching/topic/path"
    
    def generate_test_message(self, where_condition, should_match):
        """Generate test message based on WHERE condition"""
        base_message = {
            "deviceId": "test-device-123",
            "timestamp": int(time.time() * 1000)
        }
        
        if not where_condition:
            # No WHERE condition, add generic data
            base_message.update({
                "temperature": 23.5,
                "humidity": 45.0,
                "status": "active"
            })
            return base_message
        
        # Parse WHERE condition and generate appropriate data
        condition_lower = where_condition.lower()
        
        if 'temperature' in condition_lower:
            if should_match:
                if '>' in condition_lower:
                    # Extract number and make it higher
                    try:
                        threshold = float(condition_lower.split('>')[1].strip())
                        base_message['temperature'] = threshold + 5
                    except:
                        base_message['temperature'] = 30.0
                elif '<' in condition_lower:
                    try:
                        threshold = float(condition_lower.split('<')[1].strip())
                        base_message['temperature'] = threshold - 5
                    except:
                        base_message['temperature'] = 15.0
                else:
                    base_message['temperature'] = 25.0
            else:
                if '>' in condition_lower:
                    try:
                        threshold = float(condition_lower.split('>')[1].strip())
                        base_message['temperature'] = threshold - 5
                    except:
                        base_message['temperature'] = 20.0
                elif '<' in condition_lower:
                    try:
                        threshold = float(condition_lower.split('<')[1].strip())
                        base_message['temperature'] = threshold + 5
                    except:
                        base_message['temperature'] = 30.0
        
        elif 'humidity' in condition_lower:
            if should_match:
                base_message['humidity'] = 85.0 if '>' in condition_lower else 25.0
            else:
                base_message['humidity'] = 40.0
        
        elif 'status' in condition_lower:
            if should_match:
                if "'active'" in condition_lower or '"active"' in condition_lower:
                    base_message['status'] = 'active'
                elif "'offline'" in condition_lower or '"offline"' in condition_lower:
                    base_message['status'] = 'offline'
                else:
                    base_message['status'] = 'active'
            else:
                base_message['status'] = 'inactive'
        
        elif 'level' in condition_lower or 'battery' in condition_lower:
            if should_match:
                base_message['level'] = 15 if '<' in condition_lower else 85
            else:
                base_message['level'] = 50
        
        else:
            # Generic condition, add some data
            base_message.update({
                "value": 30.0 if should_match else 15.0,
                "status": "active" if should_match else "inactive"
            })
        
        return base_message

def main():
    import sys
    
    try:
        # Check for debug flag
        debug_mode = '--debug' in sys.argv or '-d' in sys.argv
        
        print("⚙️ AWS IoT Rules Engine Explorer")
        print("=" * 60)
        
        # Display AWS context first
        try:
            sts = boto3.client('sts')
            iot = boto3.client('iot')
            identity = sts.get_caller_identity()
            
            print(f"📍 AWS Configuration:")
            print(f"   Account ID: {identity['Account']}")
            print(f"   Region: {iot.meta.region_name}")
            print()
            
        except Exception as e:
            print(f"⚠️ Could not retrieve AWS context: {str(e)}")
            print(f"   Make sure AWS credentials are configured")
            print()
        
        print("Learn AWS IoT Rules Engine through hands-on rule creation and management.")
        print("This tool demonstrates:")
        print("• IoT Rules Engine SQL syntax and message routing")
        print("• Topic filtering with SELECT, FROM, and WHERE clauses")
        print("• Republish actions and IAM role configuration")
        print("• Rule lifecycle management (create, enable, disable, delete)")
        
        print("\n📚 LEARNING MOMENT: IoT Rules Engine")
        print("The AWS IoT Rules Engine processes and routes messages from your devices using SQL-like queries. Rules can filter, transform, and route messages to various AWS services like Lambda, DynamoDB, or S3. This enables real-time data processing, alerting, and integration with your broader AWS architecture without requiring device-side logic changes.")
        print("\n🔄 NEXT: We will create and manage IoT rules for message processing")
        input("Press Enter to continue...")
        
        if debug_mode:
            print(f"\n🔍 DEBUG MODE ENABLED")
            print(f"• Enhanced AWS IoT API logging")
            print(f"• Detailed rule payload and IAM operations")
            print(f"• Extended error diagnostics")
        else:
            print(f"\n💡 Tip: Use --debug or -d flag for enhanced logging")
        
        print("=" * 60)
        
        explorer = IoTRulesExplorer(debug=debug_mode)
        
        try:
            while True:
                print("\n📋 IoT Rules Engine Menu:")
                print("1. List all IoT Rules")
                print("2. Describe specific IoT Rule")
                print("3. Create new IoT Rule")
                print("4. Test IoT Rule with sample messages")
                print("5. Manage IoT Rule (enable/disable/delete)")
                print("6. Exit")
                
                choice = input("\nSelect option (1-6): ").strip()
                
                if choice == '1':
                    print("\n📚 LEARNING MOMENT: Rules Inventory & Management")
                    print("Listing IoT rules shows you all the message processing logic currently active in your account. Each rule has a name, SQL statement, and actions. This inventory helps you understand your data flow, identify unused rules, and manage your IoT message processing pipeline effectively.")
                    print("\n🔄 NEXT: We will list all IoT rules in your account")
                    input("Press Enter to continue...")
                    
                    explorer.list_rules()
                    input("\nPress Enter to return to menu...")
                elif choice == '2':
                    print("\n📚 LEARNING MOMENT: Rule Analysis & Troubleshooting")
                    print("Describing a rule reveals its complete configuration including SQL query, actions, and metadata. This detailed view is essential for troubleshooting message routing issues, understanding rule logic, and verifying that rules are configured correctly for your use case.")
                    print("\n🔄 NEXT: We will examine a specific rule's configuration")
                    input("Press Enter to continue...")
                    
                    explorer.describe_rule()
                    input("\nPress Enter to return to menu...")
                elif choice == '3':
                    print("\n📚 LEARNING MOMENT: Rule Creation & Message Routing")
                    print("Creating IoT rules defines how messages from your devices are processed and routed. Rules use SQL-like syntax to filter and transform messages, then trigger actions like storing data, invoking functions, or sending notifications. This enables real-time data processing without device-side changes.")
                    print("\n🔄 NEXT: We will create a new IoT rule with SQL and actions")
                    input("Press Enter to continue...")
                    
                    explorer.create_rule()
                    input("\nPress Enter to return to menu...")
                elif choice == '4':
                    print("\n📚 LEARNING MOMENT: Rule Testing & Validation")
                    print("Testing rules with sample messages validates your SQL logic and ensures rules behave as expected before deploying to production. This helps catch filtering errors, syntax issues, and logic problems that could cause message processing failures or unexpected behavior.")
                    print("\n🔄 NEXT: We will test a rule with sample MQTT messages")
                    input("Press Enter to continue...")
                    
                    explorer.test_rule()
                    input("\nPress Enter to return to menu...")
                elif choice == '5':
                    print("\n📚 LEARNING MOMENT: Rule Lifecycle Operations")
                    print("Managing rules includes enabling, disabling, and deleting them. Disabling rules stops message processing without losing configuration, while deleting removes them permanently. This lifecycle management is crucial for maintaining, updating, and troubleshooting your IoT data processing pipeline.")
                    print("\n🔄 NEXT: We will manage rule status and lifecycle")
                    input("Press Enter to continue...")
                    
                    explorer.manage_rule()
                    input("\nPress Enter to return to menu...")
                elif choice == '6':
                    print("👋 Goodbye!")
                    break
                else:
                    print("❌ Invalid choice. Please select 1-6.")
                
                input("\nPress Enter to continue...")
        
        except KeyboardInterrupt:
            print(f"\n\n🛑 Interrupted by user")
        except Exception as e:
            print(f"\n❌ Unexpected error: {str(e)}")
            if debug_mode:
                import traceback
                traceback.print_exc()
    
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")

if __name__ == "__main__":
    main()