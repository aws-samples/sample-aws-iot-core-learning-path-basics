#!/usr/bin/env python3
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

"""
AWS IoT Rules Engine Explorer
Educational tool for learning AWS IoT Rules Engine through hands-on rule creation and management.
"""
import json
import os
import sys
import time
from datetime import datetime

import boto3
from awscrt import io, mqtt
from awsiot import mqtt_connection_builder
from botocore.exceptions import ClientError

# Internationalization support
def load_messages(lang="en"):
    """Load messages from i18n files"""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        i18n_path = os.path.join(script_dir, "..", "i18n", lang, "iot_rules_explorer.json")
        with open(i18n_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        # Fallback to English
        if lang != "en":
            return load_messages("en")
        return {}


def get_language():
    """Get user's preferred language"""
    env_lang = os.getenv("AWS_IOT_LANG", "").lower()
    if env_lang in ["es", "spanish", "español"]:
        return "es"
    elif env_lang in ["ja", "japanese", "日本語", "jp"]:
        return "ja"
    elif env_lang in ["zh-cn", "chinese", "中文", "zh"]:
        return "zh-CN"
    elif env_lang in ["pt-br", "portuguese", "português", "pt"]:
        return "pt-BR"
    elif env_lang in ["ko", "korean", "한국어", "kr"]:
        return "ko"
    elif env_lang in ["en", "english"]:
        return "en"

    # Interactive selection
    print("🌍 Language Selection / Selección de Idioma / 言語選択 / 语言选择 / Seleção de Idioma / 언어 선택")
    print("=" * 80)
    print("1. English")
    print("2. Español (Spanish)")
    print("3. 日本語 (Japanese)")
    print("4. 中文 (Chinese)")
    print("5. Português (Portuguese)")
    print("6. 한국어 (Korean)")

    while True:
        try:
            choice = input("Select language (1-6): ").strip()
            if choice == "1":
                return "en"
            elif choice == "2":
                return "es"
            elif choice == "3":
                return "ja"
            elif choice == "4":
                return "zh-CN"
            elif choice == "5":
                return "pt-BR"
            elif choice == "6":
                return "ko"
            else:
                print("Invalid choice. Please select 1-6.")
        except KeyboardInterrupt:
            print("\nGoodbye!")
            sys.exit(0)


# Global variables
USER_LANG = get_language()
MESSAGES = load_messages(USER_LANG)


def get_message(key, **kwargs):
    """Get localized message"""
    message = MESSAGES.get(key, key)
    if kwargs:
        try:
            return message.format(**kwargs)
        except (KeyError, ValueError):
            return message
    return message


class IoTRulesExplorer:
    def __init__(self, debug=False):
        self.iot = boto3.client("iot")
        self.iam = boto3.client("iam")
        self.debug_mode = debug
        self.rule_role_name = "IoTRulesEngineRole"

    def safe_operation(self, func, operation_name, **kwargs):
        """Execute operation with error handling"""
        try:
            if self.debug_mode:
                print(get_message("debug_operation", operation=operation_name))
                print(get_message("debug_input", input=json.dumps(kwargs, indent=2, default=str)))

            response = func(**kwargs)

            if self.debug_mode:
                print(get_message("debug_completed", operation=operation_name))
                if response:
                    output_str = json.dumps(response, indent=2, default=str)
                    truncated_output = output_str[:500] + ("..." if len(output_str) > 500 else "")
                    print(get_message("debug_output", output=truncated_output))

            return response, True
        except ClientError as e:
            print(get_message("operation_failed", operation=operation_name, error=e.response["Error"]["Message"]))
            if self.debug_mode:
                print(get_message("debug_error_code", code=e.response["Error"]["Code"]))
            return None, False
        except Exception as e:
            print(get_message("operation_failed", operation=operation_name, error=str(e)))
            return None, False

    def validate_sql_clause(self, clause, clause_type):
        """Validate SQL clause input"""
        if not clause:
            return ""

        import re

        if clause_type == "SELECT":
            allowed_pattern = r"^[a-zA-Z0-9_\s,.*()=<>!+'-]+$"
        elif clause_type == "WHERE":
            allowed_pattern = r'^[a-zA-Z0-9_\s=<>!()\'".,\-]+$'
        else:
            allowed_pattern = r"^[a-zA-Z0-9_\s]+$"

        if not re.match(allowed_pattern, clause):
            raise ValueError(get_message("invalid_characters_clause", clause_type=clause_type))

        dangerous_patterns = ["--", "/*", "*/", ";", "DROP", "DELETE", "INSERT", "UPDATE", "EXEC"]
        clause_upper = clause.upper()
        for pattern in dangerous_patterns:
            if pattern in clause_upper:
                raise ValueError(get_message("dangerous_pattern_detected", pattern=pattern, clause_type=clause_type))

        return clause.strip()

    def validate_topic_pattern(self, topic):
        """Validate IoT topic pattern"""
        if not topic:
            return ""

        import re

        allowed_pattern = r"^[a-zA-Z0-9_/+-]+$"

        if not re.match(allowed_pattern, topic):
            raise ValueError(get_message("invalid_characters_topic"))

        return topic.strip()

    def list_rules(self):
        """List all IoT rules"""
        print(f"\n{get_message('list_rules_title')}")
        print(get_message("header_separator"))

        response, success = self.safe_operation(self.iot.list_topic_rules, get_message("list_rules_title"))
        if not success:
            return

        rules = response.get("rules", [])
        if not rules:
            print(get_message("no_rules_found"))
            print(get_message("create_first_rule"))
            return

        print(get_message("found_rules", count=len(rules)))
        print()

        for i, rule in enumerate(rules, 1):
            rule_name = rule["ruleName"]
            created_at = rule.get("createdAt", "Unknown")
            rule_disabled = rule.get("ruleDisabled", False)
            status = get_message("rule_status_disabled") if rule_disabled else get_message("rule_status_enabled")

            print(f"{i}. {rule_name} - {status}")
            print(f"   {get_message('created_label', date=created_at)}")

            if self.debug_mode:
                print(f"   {get_message('debug_rule_arn', arn=rule.get('ruleArn', 'N/A'))}")

            rule_response, rule_success = self.safe_operation(
                self.iot.get_topic_rule, f"Get rule details for {rule_name}", ruleName=rule_name
            )

            if rule_success and rule_response:
                rule_payload = rule_response.get("rule", {})
                sql = rule_payload.get("sql", "N/A")
                actions = rule_payload.get("actions", [])

                print(f"   {get_message('sql_label', sql=sql)}")
                print(f"   {get_message('actions_count', count=len(actions))}")

                for j, action in enumerate(actions, 1):
                    if "republish" in action:
                        topic = action["republish"].get("topic", "N/A")
                        print(f"      {j}. {get_message('action_republish', topic=topic)}")
                    elif "s3" in action:
                        bucket = action["s3"].get("bucketName", "N/A")
                        print(f"      {j}. {get_message('action_s3', bucket=bucket)}")
                    elif "lambda" in action:
                        function_arn = action["lambda"].get("functionArn", "N/A")
                        function_name = function_arn.split(":")[-1] if ":" in function_arn else function_arn
                        print(f"      {j}. {get_message('action_lambda', function=function_name)}")
                    else:
                        action_type = list(action.keys())[0] if action else "Unknown"
                        print(f"      {j}. {action_type}")
            print()

    def describe_rule(self):
        """Describe a specific IoT rule"""
        print(f"\n{get_message('describe_rule_title')}")
        print(get_message("header_separator"))

        response, success = self.safe_operation(self.iot.list_topic_rules, get_message("list_rules_for_selection"))
        if not success:
            return

        rules = response.get("rules", [])
        if not rules:
            print(get_message("no_rules_found"))
            return

        print(get_message("available_rules"))
        for i, rule in enumerate(rules, 1):
            status = (
                get_message("rule_status_disabled") if rule.get("ruleDisabled", False) else get_message("rule_status_enabled")
            )
            print(f"   {i}. {rule['ruleName']} - {status}")

        while True:
            try:
                choice = int(input(f"\n{get_message('select_rule_describe', count=len(rules))}")) - 1
                if 0 <= choice < len(rules):
                    selected_rule = rules[choice]["ruleName"]
                    break
                else:
                    print(get_message("invalid_selection_range", count=len(rules)))
            except ValueError:
                print(get_message("enter_valid_number"))

        rule_response, rule_success = self.safe_operation(
            self.iot.get_topic_rule, f"Get detailed rule information for {selected_rule}", ruleName=selected_rule
        )

        if not rule_success:
            return

        rule_payload = rule_response.get("rule", {})

        print(f"\n{get_message('rule_details_title', name=selected_rule)}")
        print(get_message("rule_separator"))

        print(get_message("sql_statement_label"))
        print(f"   {rule_payload.get('sql', 'N/A')}")

        print(f"\n{get_message('sql_breakdown_label')}")
        sql = rule_payload.get("sql", "")
        if "SELECT" in sql.upper():
            select_part = sql.split("FROM")[0].replace("SELECT", "").strip()
            print(f"   {get_message('select_clause', clause=select_part)}")

        if "FROM" in sql.upper():
            from_part = (
                sql.split("FROM")[1].split("WHERE")[0].strip() if "WHERE" in sql.upper() else sql.split("FROM")[1].strip()
            )
            print(f"   {get_message('from_clause', clause=from_part)}")

        if "WHERE" in sql.upper():
            where_part = sql.split("WHERE")[1].strip()
            print(f"   {get_message('where_clause', clause=where_part)}")

        actions = rule_payload.get("actions", [])
        print(f"\n{get_message('actions_title', count=len(actions))}")

        for i, action in enumerate(actions, 1):
            action_type = list(action.keys())[0] if action else "Unknown"
            print(f"   {i}. {get_message('action_type', type=action_type)}")

            if "republish" in action:
                republish = action["republish"]
                print(f"      {get_message('target_topic', topic=republish.get('topic', 'N/A'))}")
                print(f"      {get_message('role_arn', arn=republish.get('roleArn', 'N/A'))}")
                if "qos" in republish:
                    print(f"      {get_message('qos_label', qos=republish['qos'])}")

        error_action = rule_payload.get("errorAction")
        if error_action:
            print(f"\n{get_message('error_action_title')}")
            error_type = list(error_action.keys())[0] if error_action else "Unknown"
            print(f"   {get_message('error_action_type', type=error_type)}")

        print(f"\n{get_message('rule_metadata_title')}")
        status = (
            get_message("rule_status_disabled")
            if rule_payload.get("ruleDisabled", False)
            else get_message("rule_status_enabled")
        )
        print(f"   {get_message('rule_status', status=status)}")
        print(f"   {get_message('rule_created', date=rule_payload.get('createdAt', 'N/A'))}")

        if self.debug_mode:
            print(f"\n{get_message('debug_complete_payload')}")
            print(json.dumps(rule_payload, indent=2, default=str))

    def create_rule(self):
        """Interactive rule creation"""
        print(f"\n{get_message('create_rule_title')}")
        print(get_message("header_separator"))

        print(get_message("create_learning_objectives"))
        print(get_message("objective_sql_syntax"))
        print(get_message("objective_topic_filtering"))
        print(get_message("objective_sql_clauses"))
        print(get_message("objective_republish_actions"))
        print()

        # Rule name
        while True:
            rule_name = input(get_message("enter_rule_name")).strip()
            if rule_name and rule_name.replace("_", "").isalnum():
                break
            else:
                print(get_message("invalid_rule_name"))

        print(get_message("rule_name_confirmed", name=rule_name))

        # Rule description
        rule_description = input(get_message("enter_rule_description")).strip()
        if not rule_description:
            rule_description = get_message("default_rule_description")

        print(get_message("rule_description_confirmed", description=rule_description))

        # Build SQL statement
        print(f"\n{get_message('building_sql_title')}")
        print(get_message("sql_template"))

        # Topic pattern configuration
        print(f"\n{get_message('topic_configuration_title')}")
        print(get_message("topic_option_template"))
        print(get_message("topic_option_custom"))

        while True:
            try:
                topic_choice = int(input(f"\n{get_message('select_topic_option')}"))
                if topic_choice in [1, 2]:
                    break
                else:
                    print(get_message("invalid_choice"))
            except ValueError:
                print(get_message("enter_valid_number"))

        if topic_choice == 1:
            event_types = ["temperature", "humidity", "pressure", "motion", "door", "alarm", "status", "battery"]

            print(f"\n{get_message('available_event_types')}")
            for i, event_type in enumerate(event_types, 1):
                print(f"   {i}. {event_type}")
            print(f"   {len(event_types) + 1}. {get_message('custom_event_type')}")

            while True:
                try:
                    choice = int(input(f"\n{get_message('select_event_type', count=len(event_types) + 1)}"))
                    if 1 <= choice <= len(event_types):
                        selected_event_type = event_types[choice - 1]
                        break
                    elif choice == len(event_types) + 1:
                        selected_event_type = input(get_message("enter_custom_event_type")).strip()
                        if selected_event_type:
                            break
                        else:
                            print(get_message("event_type_empty"))
                    else:
                        print(get_message("invalid_event_selection"))
                except ValueError:
                    print(get_message("enter_valid_number"))

            topic_pattern = f"testRulesEngineTopic/+/{selected_event_type}"
        else:
            print(f"\n{get_message('custom_topic_examples')}")
            while True:
                topic_pattern = input(f"\n{get_message('enter_custom_topic')}").strip()
                if topic_pattern:
                    selected_event_type = "custom"
                    break
                else:
                    print(get_message("custom_topic_empty"))

        print(get_message("topic_pattern_confirmed", pattern=topic_pattern))

        # SELECT clause
        print(f"\n{get_message('select_clause_title', event_type=selected_event_type)}")

        event_attributes = {
            "temperature": ["*", "deviceId, timestamp, temperature", "deviceId, temperature, location"],
            "humidity": ["*", "deviceId, timestamp, humidity", "deviceId, humidity, location"],
            "pressure": ["*", "deviceId, timestamp, pressure", "deviceId, pressure, altitude"],
            "motion": ["*", "deviceId, timestamp, detected", "deviceId, detected, location"],
            "door": ["*", "deviceId, timestamp, status", "deviceId, status, location"],
            "alarm": ["*", "deviceId, timestamp, alertType", "deviceId, alertType, severity"],
            "status": ["*", "deviceId, timestamp, status", "deviceId, status, uptime"],
            "battery": ["*", "deviceId, timestamp, level", "deviceId, level, voltage"],
            "custom": ["*", "deviceId, timestamp, value", "deviceId, value, status"],
        }

        available_attributes = event_attributes.get(
            selected_event_type, ["*", "deviceId, timestamp, value", "deviceId, value, status"]
        )
        available_attributes.append(get_message("custom_selection"))

        for i, attr in enumerate(available_attributes, 1):
            print(f"   {i}. {attr}")

        while True:
            try:
                choice = int(input(f"\n{get_message('select_attributes', count=len(available_attributes))}"))
                if 1 <= choice <= len(available_attributes) - 1:
                    select_clause = available_attributes[choice - 1]
                    break
                elif choice == len(available_attributes):
                    select_clause = input(get_message("enter_custom_select")).strip()
                    if select_clause:
                        break
                    else:
                        print(get_message("select_clause_empty"))
                else:
                    print(get_message("invalid_event_selection"))
            except ValueError:
                print(get_message("enter_valid_number"))

        print(get_message("select_clause_confirmed", clause=select_clause))

        # WHERE clause
        print(f"\n{get_message('where_clause_title', event_type=selected_event_type)}")

        where_examples = {
            "temperature": ["temperature > 25", "temperature < 0", "location = 'warehouse'"],
            "humidity": ["humidity > 80", "humidity < 30", "location = 'greenhouse'"],
            "pressure": ["pressure > 1013", "pressure < 950", "altitude > 1000"],
            "motion": ["detected = true", "location = 'entrance'", "timestamp > timestamp() - 300000"],
            "door": ["status = 'open'", "status = 'closed'", "location = 'main_entrance'"],
            "alarm": ["alertType = 'fire'", "severity = 'high'", "alertType = 'intrusion'"],
            "status": ["status = 'offline'", "uptime < 3600", "status = 'maintenance'"],
            "battery": ["level < 20", "level < 10", "voltage < 3.0"],
        }

        examples = where_examples.get(
            selected_event_type, ["value > 25", "status = 'active'", "timestamp > timestamp() - 3600000"]
        )
        print(get_message("where_examples_title", event_type=selected_event_type))
        for example in examples:
            print(f"   • {example}")

        add_where = input(f"\n{get_message('add_where_condition')}").strip().lower()
        where_clause = ""

        if add_where == "y":
            where_clause = input(get_message("enter_where_condition")).strip()
            if where_clause:
                print(get_message("where_clause_confirmed", clause=where_clause))
            else:
                print(get_message("empty_where_warning"))

        # Build SQL with validation
        try:
            safe_select_clause = self.validate_sql_clause(select_clause, "SELECT")
            safe_topic_pattern = self.validate_topic_pattern(topic_pattern)
            safe_where_clause = self.validate_sql_clause(where_clause, "WHERE") if where_clause else ""

            sql_statement = "SELECT {} FROM '{}'".format(safe_select_clause, safe_topic_pattern)
            if safe_where_clause:
                sql_statement += " WHERE {}".format(safe_where_clause)
        except ValueError as e:
            print(get_message("input_validation_error", error=str(e)))
            print(get_message("validation_tip"))
            return

        print(f"\n{get_message('complete_sql_title')}")
        print(f"   {sql_statement}")

        # Configure republish action
        print(f"\n{get_message('republish_config_title')}")

        target_topic = input(get_message("enter_target_topic")).strip()
        if not target_topic:
            target_topic = f"processed/{selected_event_type}"
            print(get_message("default_target_topic", topic=target_topic))

        # Create/verify IAM role
        print(f"\n{get_message('iam_role_setup')}")
        role_arn = self.ensure_iot_rule_role()

        if not role_arn:
            print(get_message("iam_role_failed"))
            return

        # Create the rule
        print(f"\n{get_message('creating_rule')}")

        rule_payload = {
            "sql": sql_statement,
            "description": rule_description,
            "actions": [{"republish": {"topic": target_topic, "roleArn": role_arn, "qos": 1}}],
            "ruleDisabled": False,
        }

        if self.debug_mode:
            print(get_message("debug_rule_payload"))
            print(json.dumps(rule_payload, indent=2))

        # Try creating with retry for IAM propagation
        max_retries = 3
        for attempt in range(max_retries):
            response, success = self.safe_operation(
                self.iot.create_topic_rule,
                get_message("create_rule_attempt", name=rule_name, attempt=attempt + 1, max_attempts=max_retries),
                ruleName=rule_name,
                topicRulePayload=rule_payload,
            )

            if success:
                break
            elif attempt < max_retries - 1:
                print(get_message("iam_propagation_wait"))
                time.sleep(10)
            else:
                print(get_message("create_rule_failed", attempts=max_retries))
                return

        if success:
            print(f"\n{get_message('rule_created_success', name=rule_name)}")
            print(f"\n{get_message('rule_summary_title')}")
            print(f"   {get_message('summary_name', name=rule_name)}")
            print(f"   {get_message('summary_source_topic', topic=topic_pattern)}")
            print(f"   {get_message('summary_target_topic', topic=target_topic)}")
            print(f"   {get_message('summary_sql', sql=sql_statement)}")
            print(f"   {get_message('summary_role', role=role_arn)}")

            print(f"\n{get_message('testing_rule_title')}")
            example_source_topic = topic_pattern.replace("+", "device123")
            print(f"   {get_message('testing_step_1', source_topic=example_source_topic)}")
            print(f"   {get_message('testing_step_2', target_topic=target_topic)}")
            print(f"   {get_message('testing_step_3')}")

            print(f"\n{get_message('example_test_message')}")
            example_message = self.generate_example_message(selected_event_type, sql_statement)
            print(f"   {json.dumps(example_message, indent=2)}")

    def generate_example_message(self, event_type, sql_statement):
        """Generate example message based on event type and SQL"""
        base_message = {"deviceId": "device123", "timestamp": int(time.time() * 1000)}

        if event_type == "temperature":
            base_message["temperature"] = 30.0 if "temperature >" in sql_statement else 25.5
        elif event_type == "humidity":
            base_message["humidity"] = 85.0 if "humidity >" in sql_statement else 65.0
        elif event_type == "pressure":
            base_message["pressure"] = 1020.0 if "pressure >" in sql_statement else 1013.25
        elif event_type == "motion":
            base_message["detected"] = True
        elif event_type == "door":
            base_message["status"] = "open"
        elif event_type == "alarm":
            base_message.update({"alertType": "fire", "severity": "high"})
        elif event_type == "status":
            base_message.update({"status": "active", "uptime": 3600})
        elif event_type == "battery":
            base_message.update({"level": 15 if "level <" in sql_statement else 85, "voltage": 3.2})
        else:
            base_message.update({"value": 25.5, "status": "active"})

        return base_message

    def ensure_iot_rule_role(self):
        """Create or verify IAM role for IoT Rules Engine"""
        try:
            response = self.iam.get_role(RoleName=self.rule_role_name)
            role_arn = response["Role"]["Arn"]

            if self.debug_mode:
                print(get_message("debug_existing_role", arn=role_arn))

            print(get_message("using_existing_role", name=self.rule_role_name))
            return role_arn

        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchEntity":
                print(get_message("creating_iam_role", name=self.rule_role_name))
                return self.create_iot_rule_role()
            else:
                print(get_message("error_checking_role", error=e.response["Error"]["Message"]))
                return None

    def create_iot_rule_role(self):
        """Create IAM role with necessary permissions"""
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [{"Effect": "Allow", "Principal": {"Service": "iot.amazonaws.com"}, "Action": "sts:AssumeRole"}],
        }

        response, success = self.safe_operation(
            self.iam.create_role,
            get_message("create_iam_role_operation", name=self.rule_role_name),
            RoleName=self.rule_role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description="IAM role for AWS IoT Rules Engine learning exercises",
        )

        if not success:
            return None

        role_arn = response["Role"]["Arn"]

        policy_document = {
            "Version": "2012-10-17",
            "Statement": [{"Effect": "Allow", "Action": ["iot:Publish"], "Resource": "*"}],
        }

        policy_name = "IoTRulesEnginePolicy"

        policy_response, policy_success = self.safe_operation(
            self.iam.create_policy,
            get_message("create_iam_policy_operation", name=policy_name),
            PolicyName=policy_name,
            PolicyDocument=json.dumps(policy_document),
            Description="Policy for IoT Rules Engine to publish messages",
        )

        if policy_success:
            policy_arn = policy_response["Policy"]["Arn"]

            attach_response, attach_success = self.safe_operation(
                self.iam.attach_role_policy,
                get_message("attach_policy_operation"),
                RoleName=self.rule_role_name,
                PolicyArn=policy_arn,
            )

            if attach_success:
                print(get_message("iam_role_created_success"))
                print(get_message("iam_role_propagation"))
                time.sleep(10)
                return role_arn

        return None

    def manage_rule(self):
        """Enable, disable, or delete rules"""
        print(f"\n{get_message('manage_rule_title')}")
        print(get_message("header_separator"))

        response, success = self.safe_operation(self.iot.list_topic_rules, get_message("list_rules_for_management"))
        if not success:
            return

        rules = response.get("rules", [])
        if not rules:
            print(get_message("no_rules_found"))
            return

        print(get_message("available_rules"))
        for i, rule in enumerate(rules, 1):
            status = (
                get_message("rule_status_disabled") if rule.get("ruleDisabled", False) else get_message("rule_status_enabled")
            )
            print(f"   {i}. {rule['ruleName']} - {status}")

        while True:
            try:
                choice = int(input(f"\n{get_message('select_rule_manage', count=len(rules))}")) - 1
                if 0 <= choice < len(rules):
                    selected_rule = rules[choice]
                    break
                else:
                    print(get_message("invalid_selection_range", count=len(rules)))
            except ValueError:
                print(get_message("enter_valid_number"))

        rule_name = selected_rule["ruleName"]
        is_disabled = selected_rule.get("ruleDisabled", False)

        print(f"\n{get_message('managing_rule', name=rule_name)}")
        current_status = get_message("rule_status_disabled") if is_disabled else get_message("rule_status_enabled")
        print(f"{get_message('current_status', status=current_status)}")

        print(f"\n{get_message('management_options')}")
        if is_disabled:
            print(f"   {get_message('enable_rule')}")
        else:
            print(f"   {get_message('disable_rule')}")
        print(f"   {get_message('delete_rule')}")
        print(f"   {get_message('cancel_management')}")

        while True:
            try:
                action = int(input(f"\n{get_message('select_action')}"))
                if action in [1, 2, 3]:
                    break
                else:
                    print(get_message("invalid_action_selection"))
            except ValueError:
                print(get_message("enter_valid_number"))

        if action == 1:
            # Enable/Disable rule
            new_disabled_status = not is_disabled
            action_name = (
                get_message("enable_rule_operation", name=rule_name)
                if is_disabled
                else get_message("disable_rule_operation", name=rule_name)
            )

            rule_response, rule_success = self.safe_operation(
                self.iot.get_topic_rule, get_message("get_current_rule_settings"), ruleName=rule_name
            )

            if rule_success:
                current_rule = rule_response["rule"]

                clean_payload = {
                    "sql": current_rule.get("sql", 'SELECT * FROM "temp"'),
                    "ruleDisabled": new_disabled_status,
                    "actions": current_rule.get("actions", []),
                }

                if "description" in current_rule:
                    clean_payload["description"] = current_rule["description"]
                if "awsIotSqlVersion" in current_rule:
                    clean_payload["awsIotSqlVersion"] = current_rule["awsIotSqlVersion"]
                if "errorAction" in current_rule:
                    clean_payload["errorAction"] = current_rule["errorAction"]

                response, success = self.safe_operation(
                    self.iot.replace_topic_rule, action_name, ruleName=rule_name, topicRulePayload=clean_payload
                )

                if success:
                    status_text = (
                        get_message("rule_status_enabled") if not new_disabled_status else get_message("rule_status_disabled")
                    )
                    print(get_message("rule_status_updated", name=rule_name, status=status_text))
            else:
                print(get_message("failed_get_rule_settings", name=rule_name))

        elif action == 2:
            # Delete rule
            confirm = input(get_message("confirm_delete_rule", name=rule_name)).strip().lower()

            if confirm == "y":
                response, success = self.safe_operation(
                    self.iot.delete_topic_rule, get_message("delete_rule_operation", name=rule_name), ruleName=rule_name
                )

                if success:
                    print(get_message("rule_deleted_success", name=rule_name))
            else:
                print(get_message("rule_deletion_cancelled"))

        elif action == 3:
            print(get_message("management_cancelled"))

    def test_rule(self):
        """Test IoT rules with sample messages"""
        print(f"\n{get_message('test_rule_title')}")
        print(get_message("header_separator"))

        print(get_message("test_learning_objectives"))
        print(get_message("test_objective_1"))
        print(get_message("test_objective_2"))
        print(get_message("test_objective_3"))
        print(get_message("test_objective_4"))
        print()

        response, success = self.safe_operation(self.iot.list_topic_rules, get_message("list_rules_for_testing"))
        if not success:
            return

        rules = response.get("rules", [])
        if not rules:
            print(get_message("no_rules_for_testing"))
            print(get_message("create_rule_first"))
            return

        print(get_message("available_rules"))
        for i, rule in enumerate(rules, 1):
            status = (
                get_message("rule_status_disabled") if rule.get("ruleDisabled", False) else get_message("rule_status_enabled")
            )
            print(f"   {i}. {rule['ruleName']} - {status}")

        while True:
            try:
                choice = int(input(f"\n{get_message('select_rule_test', count=len(rules))}")) - 1
                if 0 <= choice < len(rules):
                    selected_rule = rules[choice]
                    break
                else:
                    print(get_message("invalid_selection_range", count=len(rules)))
            except ValueError:
                print(get_message("enter_valid_number"))

        rule_name = selected_rule["ruleName"]

        rule_response, rule_success = self.safe_operation(
            self.iot.get_topic_rule, get_message("get_rule_details_testing"), ruleName=rule_name
        )

        if not rule_success:
            return

        rule_payload = rule_response.get("rule", {})
        sql_statement = rule_payload.get("sql", "")

        print(f"\n{get_message('testing_rule', name=rule_name)}")
        print(get_message("sql_display", sql=sql_statement))

        topic_pattern = self.extract_topic_from_sql(sql_statement)
        where_condition = self.extract_where_from_sql(sql_statement)

        if topic_pattern:
            print(get_message("source_topic_pattern", pattern=topic_pattern))
        if where_condition:
            print(get_message("where_condition_display", condition=where_condition))

        actions = rule_payload.get("actions", [])
        target_topics = []
        for action in actions:
            if "republish" in action:
                target_topics.append(action["republish"].get("topic", "unknown"))

        if target_topics:
            print(get_message("target_topics_display", topics=", ".join(target_topics)))

        selected_device = self.select_device_with_certificates()
        if not selected_device:
            return

        endpoint_response, endpoint_success = self.safe_operation(
            self.iot.describe_endpoint, get_message("get_iot_endpoint"), endpointType="iot:Data-ATS"
        )

        if not endpoint_success:
            print(get_message("cannot_get_endpoint"))
            return

        endpoint = endpoint_response["endpointAddress"]
        self.run_rule_testing(endpoint, selected_device, rule_name, topic_pattern, where_condition, target_topics)

    def extract_topic_from_sql(self, sql):
        """Extract topic pattern from SQL FROM clause"""
        try:
            if "FROM" in sql.upper():
                from_part = (
                    sql.split("FROM")[1].split("WHERE")[0].strip() if "WHERE" in sql.upper() else sql.split("FROM")[1].strip()
                )
                topic = from_part.strip("'\"")
                return topic
        except (IndexError, AttributeError):
            pass
        return None

    def extract_where_from_sql(self, sql):
        """Extract WHERE condition from SQL"""
        try:
            if "WHERE" in sql.upper():
                where_part = sql.split("WHERE")[1].strip()
                return where_part
        except (IndexError, AttributeError):
            pass
        return None

    def select_device_with_certificates(self):
        """Select device with certificates"""
        print(f"\n{get_message('finding_devices_certificates')}")

        cert_dir = "certificates"
        if not os.path.exists(cert_dir):
            print(get_message("no_certificates_directory"))
            print(get_message("run_certificate_manager"))
            return None

        available_devices = []
        for thing_dir in os.listdir(cert_dir):
            thing_path = os.path.join(cert_dir, thing_dir)
            if os.path.isdir(thing_path):
                cert_files = [f for f in os.listdir(thing_path) if f.endswith(".crt")]
                if cert_files:
                    cert_id = cert_files[0].replace(".crt", "")
                    cert_path = os.path.join(thing_path, f"{cert_id}.crt")
                    key_path = os.path.join(thing_path, f"{cert_id}.key")
                    if os.path.exists(key_path):
                        available_devices.append(
                            {"thing_name": thing_dir, "cert_path": cert_path, "key_path": key_path, "cert_id": cert_id}
                        )

        if not available_devices:
            print(get_message("no_devices_certificates"))
            print(get_message("run_certificate_manager"))
            return None

        print(get_message("found_devices_certificates", count=len(available_devices)))
        for i, device in enumerate(available_devices, 1):
            print(f"   {i}. {device['thing_name']}")

        if len(available_devices) == 1:
            selected_device = available_devices[0]
            print(get_message("using_device", name=selected_device["thing_name"]))
        else:
            while True:
                try:
                    choice = int(input(f"\n{get_message('select_device', count=len(available_devices))}")) - 1
                    if 0 <= choice < len(available_devices):
                        selected_device = available_devices[choice]
                        print(get_message("selected_device", name=selected_device["thing_name"]))
                        break
                    else:
                        print(get_message("invalid_device_selection"))
                except ValueError:
                    print(get_message("enter_valid_number"))

        return selected_device

    def run_rule_testing(self, endpoint, device_info, rule_name, topic_pattern, where_condition, target_topics):
        """Run interactive rule testing with AWS IoT SDK"""
        print(f"\n{get_message('interactive_testing_title')}")
        print(get_message("connecting_to_endpoint", endpoint=endpoint))
        print(get_message("using_device_info", device=device_info["thing_name"]))

        event_loop_group = io.EventLoopGroup(1)
        host_resolver = io.DefaultHostResolver(event_loop_group)
        client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)

        messages_received = []

        def on_message_received(topic, payload, dup, qos, retain, **kwargs):
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            message_data = {"timestamp": timestamp, "topic": topic, "payload": payload.decode("utf-8")}
            messages_received.append(message_data)
            print(f"\n{get_message('rule_output_received', timestamp=timestamp)}")
            print(get_message("message_topic", topic=topic))
            print(get_message("message_content", message=payload.decode("utf-8")))
            print(get_message("rule_processed_forwarded", name=rule_name))

        mqtt_connection = mqtt_connection_builder.mtls_from_path(
            endpoint=endpoint,
            cert_filepath=device_info["cert_path"],
            pri_key_filepath=device_info["key_path"],
            client_bootstrap=client_bootstrap,
            client_id=f"rule-tester-{device_info['thing_name']}",
            clean_session=False,
            keep_alive_secs=30,
            on_connection_interrupted=lambda connection, error, **kwargs: print(
                get_message("connection_interrupted", error=error)
            ),
            on_connection_resumed=lambda connection, return_code, session_present, **kwargs: print(
                get_message("connection_resumed")
            ),
        )

        try:
            print(get_message("connecting_aws_iot"))
            connect_future = mqtt_connection.connect()
            connect_future.result(timeout=10)
            print(get_message("connected_aws_iot"))

            for topic in target_topics:
                subscribe_future, _ = mqtt_connection.subscribe(
                    topic=topic, qos=mqtt.QoS.AT_LEAST_ONCE, callback=on_message_received
                )
                subscribe_future.result(timeout=10)
                print(get_message("subscribed_target_topic", topic=topic))

            print(f"\n{get_message('rule_testing_instructions')}")
            print(get_message("instruction_1"))
            print(get_message("instruction_2"))
            print(get_message("instruction_3"))
            print(get_message("instruction_4"))
            print(get_message("instruction_5"))

            test_count = 0
            while True:
                test_count += 1
                print(f"\n{get_message('header_separator')}")
                print(get_message("test_message_header", count=test_count))
                print(f"{get_message('header_separator')}")

                pattern_display = topic_pattern or get_message("no_specific_pattern")
                print(f"\n{get_message('topic_pattern_display', pattern=pattern_display)}")
                topic_should_match = input(get_message("should_match_topic")).strip().lower()

                if topic_should_match == "quit":
                    break

                test_topic = (
                    self.generate_matching_topic(topic_pattern)
                    if topic_should_match == "y"
                    else self.generate_non_matching_topic(topic_pattern)
                )
                print(get_message("generated_topic", topic=test_topic))

                where_should_match = "y"
                if where_condition:
                    print(f"\n{get_message('where_condition_label', condition=where_condition)}")
                    where_should_match = input(get_message("should_match_where")).strip().lower()

                test_message = self.generate_test_message(where_condition, where_should_match == "y")

                print(f"\n{get_message('test_message_display')}")
                print(get_message("topic_label", topic=test_topic))
                print(get_message("payload_label", payload=json.dumps(test_message, indent=2)))

                should_trigger = (topic_should_match == "y") and (where_should_match == "y")
                prediction_msg = (
                    get_message("prediction_should_trigger")
                    if should_trigger
                    else get_message("prediction_should_not_trigger")
                )
                print(f"\n{prediction_msg}")

                print(f"\n{get_message('publishing_test_message')}")
                publish_future, _ = mqtt_connection.publish(
                    topic=test_topic, payload=json.dumps(test_message), qos=mqtt.QoS.AT_LEAST_ONCE
                )
                publish_future.result(timeout=10)

                print(get_message("waiting_rule_processing"))
                time.sleep(3)

                recent_count = len([msg for msg in messages_received[-3:]])

                if should_trigger and recent_count == 0:
                    print(get_message("expected_trigger_no_output"))
                elif not should_trigger and recent_count > 0:
                    print(get_message("unexpected_trigger"))
                elif should_trigger:
                    print(get_message("rule_triggered_expected"))
                else:
                    print(get_message("rule_correctly_not_triggered"))

                input(f"\n{get_message('press_enter_next_test')}")

        except Exception as e:
            print(get_message("testing_error", error=str(e)))
        finally:
            print(f"\n{get_message('disconnecting_aws_iot')}")
            disconnect_future = mqtt_connection.disconnect()
            disconnect_future.result(timeout=10)
            print(get_message("disconnected_aws_iot"))

    def generate_matching_topic(self, topic_pattern):
        """Generate a topic that matches the pattern"""
        if not topic_pattern:
            return "testRulesEngineTopic/device123/temperature"
        return topic_pattern.replace("+", "device123")

    def generate_non_matching_topic(self, topic_pattern):
        """Generate a topic that doesn't match the pattern"""
        if not topic_pattern:
            return "different/topic/structure"
        return "nonmatching/topic/path"

    def generate_test_message(self, where_condition, should_match):
        """Generate test message based on WHERE condition"""
        base_message = {"deviceId": "test-device-123", "timestamp": int(time.time() * 1000)}

        if not where_condition:
            base_message.update({"temperature": 23.5, "humidity": 45.0, "status": "active"})
            return base_message

        condition_lower = where_condition.lower()

        if "temperature" in condition_lower:
            if should_match:
                if ">" in condition_lower:
                    try:
                        threshold = float(condition_lower.split(">")[1].strip())
                        base_message["temperature"] = threshold + 5
                    except (ValueError, IndexError):
                        base_message["temperature"] = 30.0
                elif "<" in condition_lower:
                    try:
                        threshold = float(condition_lower.split("<")[1].strip())
                        base_message["temperature"] = threshold - 5
                    except (ValueError, IndexError):
                        base_message["temperature"] = 15.0
                else:
                    base_message["temperature"] = 25.0
            else:
                if ">" in condition_lower:
                    try:
                        threshold = float(condition_lower.split(">")[1].strip())
                        base_message["temperature"] = threshold - 5
                    except (ValueError, IndexError):
                        base_message["temperature"] = 20.0
                elif "<" in condition_lower:
                    try:
                        threshold = float(condition_lower.split("<")[1].strip())
                        base_message["temperature"] = threshold + 5
                    except (ValueError, IndexError):
                        base_message["temperature"] = 30.0

        elif "humidity" in condition_lower:
            base_message["humidity"] = 85.0 if should_match and ">" in condition_lower else 40.0

        elif "status" in condition_lower:
            if should_match:
                if "'active'" in condition_lower or '"active"' in condition_lower:
                    base_message["status"] = "active"
                elif "'offline'" in condition_lower or '"offline"' in condition_lower:
                    base_message["status"] = "offline"
                else:
                    base_message["status"] = "active"
            else:
                base_message["status"] = "inactive"

        elif "level" in condition_lower or "battery" in condition_lower:
            base_message["level"] = 15 if should_match and "<" in condition_lower else 50

        else:
            base_message.update({"value": 30.0 if should_match else 15.0, "status": "active" if should_match else "inactive"})

        return base_message


def main():
    try:
        debug_mode = "--debug" in sys.argv or "-d" in sys.argv

        print(get_message("main_title"))
        print(get_message("header_separator"))

        try:
            sts = boto3.client("sts")
            iot = boto3.client("iot")
            identity = sts.get_caller_identity()

            print(get_message("aws_config_title"))
            print(f"   {get_message('account_id')}: {identity['Account']}")
            print(f"   {get_message('region')}: {iot.meta.region_name}")
            print()

        except Exception as e:
            print(get_message("aws_context_error", error=str(e)))
            print(f"   {get_message('aws_credentials_check')}")
            print()

        print(get_message("main_description"))
        print(get_message("main_features"))
        print(get_message("feature_sql_syntax"))
        print(get_message("feature_topic_filtering"))
        print(get_message("feature_republish_actions"))
        print(get_message("feature_lifecycle"))

        print(f"\n{get_message('learning_moment_title')}")
        print(get_message("learning_moment_description"))
        print(f"\n{get_message('next_action')}")
        input(get_message("press_enter_continue"))

        if debug_mode:
            print(f"\n{get_message('debug_mode_enabled')}")
            print(get_message("debug_features"))
            print(get_message("debug_features_2"))
            print(get_message("debug_features_3"))
        else:
            print(f"\n{get_message('debug_tip')}")

        print(get_message("header_separator"))

        explorer = IoTRulesExplorer(debug=debug_mode)

        try:
            while True:
                print(f"\n{get_message('menu_title')}")
                print(get_message("menu_option_1"))
                print(get_message("menu_option_2"))
                print(get_message("menu_option_3"))
                print(get_message("menu_option_4"))
                print(get_message("menu_option_5"))
                print(get_message("menu_option_6"))

                choice = input(f"\n{get_message('select_option')}").strip()

                if choice == "1":
                    print(f"\n{get_message('learning_moment_inventory')}")
                    print(get_message("learning_moment_inventory_desc"))
                    print(f"\n{get_message('next_list_rules')}")
                    input(get_message("press_enter_continue"))

                    explorer.list_rules()
                    input(f"\n{get_message('press_enter_menu')}")
                elif choice == "2":
                    print(f"\n{get_message('learning_moment_analysis')}")
                    print(get_message("learning_moment_analysis_desc"))
                    print(f"\n{get_message('next_examine_rule')}")
                    input(get_message("press_enter_continue"))

                    explorer.describe_rule()
                    input(f"\n{get_message('press_enter_menu')}")
                elif choice == "3":
                    print(f"\n{get_message('learning_moment_creation')}")
                    print(get_message("learning_moment_creation_desc"))
                    print(f"\n{get_message('next_create_rule')}")
                    input(get_message("press_enter_continue"))

                    explorer.create_rule()
                    input(f"\n{get_message('press_enter_menu')}")
                elif choice == "4":
                    print(f"\n{get_message('learning_moment_testing')}")
                    print(get_message("learning_moment_testing_desc"))
                    print(f"\n{get_message('next_test_rule')}")
                    input(get_message("press_enter_continue"))

                    explorer.test_rule()
                    input(f"\n{get_message('press_enter_menu')}")
                elif choice == "5":
                    print(f"\n{get_message('learning_moment_lifecycle')}")
                    print(get_message("learning_moment_lifecycle_desc"))
                    print(f"\n{get_message('next_manage_rule')}")
                    input(get_message("press_enter_continue"))

                    explorer.manage_rule()
                    input(f"\n{get_message('press_enter_menu')}")
                elif choice == "6":
                    print(get_message("goodbye"))
                    break
                else:
                    print(get_message("invalid_choice"))
                    input(f"\n{get_message('press_enter_menu')}")

        except KeyboardInterrupt:
            print(f"\n\n{get_message('interrupted_by_user')}")
        except Exception as e:
            print(get_message("unexpected_error", error=str(e)))
            if debug_mode:
                import traceback

                traceback.print_exc()

    except KeyboardInterrupt:
        print(f"\n\n{get_message('goodbye')}")


if __name__ == "__main__":
    main()
