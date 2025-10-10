#!/usr/bin/env python3
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

"""
AWS IoT MQTT Client Explorer
Educational MQTT client for learning AWS IoT Core communication patterns.
"""
import json
import os
import sys
import threading
import time
import uuid
from datetime import datetime

# Add i18n to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "i18n"))

import boto3
from awscrt import mqtt
from awsiot import mqtt_connection_builder

try:
    from awsiot import mqtt5_connection_builder

    MQTT5_AVAILABLE = True
except ImportError:
    MQTT5_AVAILABLE = False

from language_selector import get_language
from loader import load_messages

# Global variables
USER_LANG = "en"
messages = {}
DEBUG_MODE = False


def get_message(key, *args):
    """Get localized message with optional formatting"""
    msg = messages.get(key, key)
    if args:
        return msg.format(*args)
    return msg


def display_aws_context():
    """Display current AWS account and region information"""
    try:
        sts = boto3.client("sts")
        iot = boto3.client("iot")
        identity = sts.get_caller_identity()

        print(f"\n{get_message('aws_context_info')}")
        print(f"   {get_message('account_id')}: {identity['Account']}")
        print(f"   {get_message('region')}: {iot.meta.region_name}")
    except Exception as e:
        print(f"\n{get_message('aws_context_error')} {str(e)}")
        print(get_message("aws_credentials_reminder"))
    print()


def interactive_messaging(mqtt_client):
    """Interactive command-line interface for MQTT operations"""
    if not mqtt_client.connected:
        print(get_message("not_connected_iot"))
        return

    print(f"\n{get_message('step_interactive_messaging')}")
    print("=" * 50)

    # Show available commands
    print(f"\n{get_message('interactive_commands')}")
    for command in get_message("command_list"):
        print(command)

    print(f"\n{get_message('mqtt_topic_guidelines')}")
    for guideline in get_message("topic_guidelines"):
        print(guideline)

    print("\n" + "=" * 50)

    while True:
        try:
            command_input = input("\n📡 MQTT> ").strip()

            if not command_input:
                continue

            parts = command_input.split()
            command = parts[0].lower()

            if command in ["quit", "exit"]:
                print(get_message("exiting_interactive"))
                mqtt_client.cleanup_connection_state()
                break

            elif command == "help":
                print(f"\n{get_message('interactive_commands')}")
                for cmd in get_message("command_list"):
                    print(cmd)

            elif command == "status":
                print(f"\n{get_message('connection_status')}")
                if mqtt_client.connected:
                    print(get_message("connected_status"))
                else:
                    print(get_message("disconnected_status"))

                print(f"\n{get_message('active_subscriptions')}")
                if mqtt_client.subscriptions:
                    for topic, info in mqtt_client.subscriptions.items():
                        print(f"   • {topic} (QoS {info['qos']})")
                else:
                    print(get_message("no_subscriptions"))

            elif command == "messages":
                print(f"\n{get_message('message_history')}")
                if mqtt_client.received_messages:
                    for i, msg in enumerate(mqtt_client.received_messages[-10:], 1):
                        timestamp = msg.get("Timestamp", "Unknown")
                        topic = msg.get("Topic", "Unknown")
                        payload = str(msg.get("Payload", ""))[:100]
                        print(f"   {i}. [{timestamp}] {topic}: {payload}...")
                else:
                    print(get_message("no_messages_received"))

            elif command == "debug":
                print(f"\n{get_message('connection_diagnostics')}")
                print(f"   {get_message('endpoint_label')}: {mqtt_client.endpoint or get_message('not_set')}")
                print(f"   {get_message('thing_name_label')}: {mqtt_client.thing_name or get_message('not_set')}")
                print(f"   {get_message('connected_label')}: {mqtt_client.connected}")
                print(f"   {get_message('subscriptions_label')}: {len(mqtt_client.subscriptions)}")
                print(f"   {get_message('messages_received_label')}: {len(mqtt_client.received_messages)}")

            elif command == "sub":
                if len(parts) < 2:
                    print("Usage: sub <topic>")
                    continue
                topic = parts[1]
                mqtt_client.subscribe_to_topic(topic, 0, DEBUG_MODE)

            elif command == "sub1":
                if len(parts) < 2:
                    print("Usage: sub1 <topic>")
                    continue
                topic = parts[1]
                mqtt_client.subscribe_to_topic(topic, 1, DEBUG_MODE)

            elif command == "unsub":
                if len(parts) < 2:
                    print("Usage: unsub <topic>")
                    continue
                topic = parts[1]
                if hasattr(mqtt_client, "unsubscribe_from_topic"):
                    mqtt_client.unsubscribe_from_topic(topic, DEBUG_MODE)
                else:
                    print("Unsubscribe functionality not implemented yet")

            elif command == "pub":
                if len(parts) < 3:
                    print("Usage: pub <topic> <message>")
                    continue
                topic = parts[1]
                message = "".join(parts[2:]).strip("'\"")
                mqtt_client.publish_message(topic, message, 0)

            elif command == "pub1":
                if len(parts) < 3:
                    print("Usage: pub1 <topic> <message>")
                    continue
                topic = parts[1]
                message = "".join(parts[2:]).strip("'\"")
                mqtt_client.publish_message(topic, message, 1)

            elif command == "json":
                if len(parts) < 3:
                    print("Usage: json <topic> key=val key2=val2...")
                    continue
                topic = parts[1]
                # Parse key=value pairs into JSON
                json_data = {}
                for pair in parts[2:]:
                    if "=" in pair:
                        key, value = pair.split("=", 1)
                        # Try to parse as number or boolean
                        if value.lower() == "true":
                            json_data[key] = True
                        elif value.lower() == "false":
                            json_data[key] = False
                        elif value.isdigit():
                            json_data[key] = int(value)
                        else:
                            try:
                                json_data[key] = float(value)
                            except ValueError:
                                json_data[key] = value
                mqtt_client.publish_message(topic, json_data, 0)

            elif command == "test":
                # Send a test message
                test_topic = f"test/{getattr(mqtt_client, 'thing_name', 'device')}/message"
                test_message = {
                    "timestamp": time.time(),
                    "message": "Hello from MQTT Client Explorer!",
                    "device": getattr(mqtt_client, "thing_name", "unknown"),
                }
                mqtt_client.publish_message(test_topic, test_message, 0)

            else:
                print(get_message("invalid_command"))

        except KeyboardInterrupt:
            print(f"\n{get_message('exiting_interactive')}")
            mqtt_client.cleanup_connection_state()
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            if DEBUG_MODE:
                import traceback

                traceback.print_exc()


class MQTTClientExplorer:
    def __init__(self):
        self.connection = None
        self.connected = False
        self.received_messages = []
        self.sent_messages = []
        self.subscriptions = {}
        self.message_lock = threading.Lock()
        self.message_count = 0
        self.endpoint = None
        self.thing_name = None

    def cleanup_connection_state(self):
        """Clean up connection state when disconnecting or reconnecting"""
        self.connected = False
        self.received_messages = []
        self.sent_messages = []
        self.subscriptions = {}
        self.message_count = 0
        if self.connection:
            try:
                self.connection.disconnect()
            except Exception:
                pass
        self.connection = None

    def print_header(self, title):
        """Print formatted header"""
        print(f"\n📡 {title}")
        print("=" * 60)

    def print_step(self, step, description):
        """Print step with formatting"""
        print(f"\n🔧 Step {step}: {description}")
        print("-" * 50)

    def print_mqtt_details(self, message_type, details):
        """Print detailed MQTT protocol information"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"\n📊 MQTT {message_type} Details [{timestamp}]")
        print("-" * 40)

        for key, value in details.items():
            if isinstance(value, dict):
                print(f"   {key}:")
                for sub_key, sub_value in value.items():
                    print(f"      {sub_key}: {sub_value}")
            else:
                print(f"   {key}: {value}")

    def validate_client_id(self, client_id):
        """Validate MQTT Client ID according to AWS IoT requirements"""
        if not client_id:
            return False

        # Length check: 1-128 characters
        if len(client_id) < 1 or len(client_id) > 128:
            return False

        # Character check: alphanumeric, hyphens, and underscores only
        import re

        if not re.match(r"^[a-zA-Z0-9_-]+$", client_id):
            return False

        return True

    def get_client_id(self, thing_name):
        """Get client ID from user input or generate automatically"""
        print(f"\n{get_message('client_id_guidelines')}")
        for rule in get_message("client_id_rules"):
            print(f"   {rule}")

        while True:
            try:
                custom_id = input(f"\n{get_message('client_id_prompt')}").strip()

                if not custom_id:
                    # Auto-generate client ID
                    client_id = f"{thing_name}-{uuid.uuid4().hex[:8]}"
                    print(f"   {get_message('client_id_auto_generated')}: {client_id}")
                    return client_id
                else:
                    # Validate custom client ID
                    if self.validate_client_id(custom_id):
                        print(f"   {get_message('client_id_custom')}: {custom_id}")
                        return custom_id
                    else:
                        print(f"   {get_message('client_id_invalid')}")
                        continue

            except KeyboardInterrupt:
                print(f"\n{get_message('operation_cancelled')}")
                return None

    def select_mqtt_version(self):
        """Allow user to select MQTT version"""
        # AWS IoT Device SDK v2 supports both MQTT 3.1.1 and MQTT 5.0
        print(f"\n{get_message('mqtt_version_selection')}")
        print(f"   1. MQTT 3.1.1 ({get_message('mqtt311_description')})")
        print(f"   2. MQTT 5.0 ({get_message('mqtt5_description')})")

        while True:
            try:
                choice = input(f"\n{get_message('select_mqtt_version')}").strip()
                if choice == "1":
                    print(f"   {get_message('selected_mqtt311')}")
                    return "3.1.1"
                elif choice == "2":
                    print(f"   {get_message('selected_mqtt5')}")
                    return "5.0"
                else:
                    print(get_message("invalid_mqtt_version"))
            except KeyboardInterrupt:
                print(f"\n{get_message('operation_cancelled')}")
                return None

    def get_iot_endpoint(self, debug=False):
        """Get AWS IoT endpoint for the account"""
        try:
            iot = boto3.client("iot")

            if debug:
                print(get_message("debug_calling_api"))
                print(f"{get_message('debug_input_params')} {{'endpointType': 'iot:Data-ATS'}}")

            response = iot.describe_endpoint(endpointType="iot:Data-ATS")
            endpoint = response["endpointAddress"]

            if debug:
                print(f"{get_message('debug_api_response')} {json.dumps(response, indent=2, default=str)}")

            print(get_message("iot_endpoint_discovery"))
            print(f"   {get_message('endpoint_type_label')}: {get_message('endpoint_type_recommended')}")
            print(f"   {get_message('endpoint_url_label')}: {endpoint}")
            print(f"   {get_message('port_label')}: {get_message('port_mqtt_tls')}")

            return endpoint
        except Exception as e:
            print(f"{get_message('error_getting_endpoint')} {str(e)}")
            if debug:
                import traceback

                print(get_message("debug_full_traceback"))
                traceback.print_exc()
            return None

    def select_device_and_certificate(self, debug=False):
        """Select a device and its certificate for MQTT connection"""
        try:
            iot = boto3.client("iot")

            # Get all Things
            if debug:
                print(get_message("debug_calling_list_things"))
                print(get_message("debug_input_params_none"))

            things_response = iot.list_things()
            things = things_response.get("things", [])

            if debug:
                print(get_message("debug_api_response_found_things").format(len(things)))
                print(f"{get_message('debug_thing_names')} {[t['thingName'] for t in things]}")

            if not things:
                print(get_message("no_things_found"))
                return None, None, None

            print(get_message("available_devices").format(len(things)))
            for i, thing in enumerate(things, 1):
                print(f"   {i}. {thing['thingName']} (Type: {thing.get('thingTypeName', 'None')})")

            while True:
                try:
                    choice = int(input(f"\n{get_message('select_device').format(len(things))} ")) - 1
                    if 0 <= choice < len(things):
                        selected_thing = things[choice]["thingName"]
                        break
                    else:
                        print(get_message("invalid_selection").format(len(things)))
                except ValueError:
                    print(get_message("enter_valid_number"))
                except KeyboardInterrupt:
                    print(f"\n{get_message('operation_cancelled')}")
                    return None, None, None

            print(f"{get_message('selected_device')} {selected_thing}")

            # Get certificates for the selected Thing
            if debug:
                print(get_message("debug_calling_list_principals"))
                print(f"{get_message('debug_input_params_thing')} {{'thingName': '{selected_thing}'}}")

            principals_response = iot.list_thing_principals(thingName=selected_thing)
            principals = principals_response.get("principals", [])
            cert_arns = [p for p in principals if "cert/" in p]

            if debug:
                print(get_message("debug_api_response_principals").format(len(principals), len(cert_arns)))
                print(f"{get_message('debug_certificate_arns')} {cert_arns}")

            if not cert_arns:
                print(get_message("no_certificates_found").format(selected_thing))
                print(get_message("run_certificate_manager"))
                return None, None, None

            # Select certificate if multiple
            if len(cert_arns) == 1:
                selected_cert_arn = cert_arns[0]
                cert_id = selected_cert_arn.split("/")[-1]
                print(f"{get_message('using_certificate')} {cert_id}")
            else:
                print(f"\n{get_message('multiple_certificates_found')}")
                for i, cert_arn in enumerate(cert_arns, 1):
                    cert_id = cert_arn.split("/")[-1]
                    print(f"   {i}. {cert_id}")

                while True:
                    try:
                        choice = int(input(get_message("select_certificate").format(len(cert_arns)))) - 1
                        if 0 <= choice < len(cert_arns):
                            selected_cert_arn = cert_arns[choice]
                            cert_id = selected_cert_arn.split("/")[-1]
                            break
                        else:
                            print(get_message("invalid_selection"))
                    except ValueError:
                        print(get_message("enter_valid_number"))
                    except KeyboardInterrupt:
                        print(f"\n{get_message('operation_cancelled')}")
                        return None, None, None

            # Find certificate files
            cert_dir = os.path.join(os.getcwd(), "certificates", selected_thing)
            if not os.path.exists(cert_dir):
                print(f"{get_message('cert_dir_not_found')} {cert_dir}")
                print(get_message("run_cert_manager_files"))
                return None, None, None

            cert_file = None
            key_file = None

            for file in os.listdir(cert_dir):
                if cert_id in file:
                    if file.endswith(".crt"):
                        cert_file = os.path.join(cert_dir, file)
                    elif file.endswith(".key"):
                        key_file = os.path.join(cert_dir, file)

            if not cert_file or not key_file:
                print(get_message("cert_files_not_found").format(cert_dir))
                print(get_message("looking_for_files").format(cert_id))
                return None, None, None

            print(get_message("cert_files_found"))
            print(f"   {get_message('certificate_label')}: {cert_file}")
            print(f"   {get_message('private_key_label')}: {key_file}")

            return selected_thing, cert_file, key_file

        except Exception as e:
            print(f"{get_message('error_selecting_device')} {str(e)}")
            return None, None, None

    def on_connection_interrupted(self, connection, error, **kwargs):
        """Callback for connection interruption"""
        self.print_mqtt_details(
            get_message("connection_interrupted"),
            {
                get_message("error_label"): str(error),
                get_message("timestamp_label"): datetime.now().isoformat(),
                get_message("auto_reconnect_label"): get_message("auto_reconnect_msg"),
            },
        )
        self.connected = False

    def on_connection_resumed(self, connection, return_code, session_present, **kwargs):
        """Callback for connection resumption"""
        self.print_mqtt_details(
            get_message("connection_resumed"),
            {
                get_message("return_code_label"): return_code,
                get_message("session_present_label"): session_present,
                get_message("timestamp_label"): datetime.now().isoformat(),
                get_message("status_label"): get_message("connection_restored"),
            },
        )
        self.connected = True

        # Re-subscribe to all topics if session not present
        if not session_present and self.subscriptions:
            print(get_message("resubscribing_topics").format(len(self.subscriptions)))
            topics_to_resubscribe = list(self.subscriptions.items())
            for topic, info in topics_to_resubscribe:
                try:
                    qos = info["qos"] if isinstance(info, dict) else info
                    mqtt_qos = mqtt.QoS.AT_MOST_ONCE if qos == 0 else mqtt.QoS.AT_LEAST_ONCE
                    subscribe_future, _ = self.connection.subscribe(
                        topic=topic, qos=mqtt_qos, callback=self.on_message_received
                    )
                    subscribe_future.result()
                    print(get_message("resubscribed_to_topic").format(topic, qos))
                except Exception as e:
                    print(f"{get_message('failed_resubscribe').format(topic)} {str(e)}")
                    # Remove failed subscription from tracking
                    self.subscriptions.pop(topic, None)

    def on_message_received(self, topic, payload, dup, qos, retain, **kwargs):
        """Callback for received messages with comprehensive MQTT metadata"""
        try:
            # Try to parse as JSON, fallback to string
            try:
                message_data = json.loads(payload.decode("utf-8"))
                payload_display = json.dumps(message_data, indent=2)
                is_json = True
            except (json.JSONDecodeError, UnicodeDecodeError):
                payload_display = payload.decode("utf-8")
                is_json = False

            # Extract additional MQTT properties from kwargs
            user_properties = kwargs.get("user_properties", [])
            content_type = kwargs.get("content_type", None)
            correlation_data = kwargs.get("correlation_data", None)
            message_expiry_interval = kwargs.get("message_expiry_interval", None)
            response_topic = kwargs.get("response_topic", None)
            payload_format_indicator = kwargs.get("payload_format_indicator", None)

            message_info = {
                "Direction": "RECEIVED",
                "Topic": topic,
                "QoS": qos,
                "Duplicate": dup,
                "Retain": retain,
                "Payload Size": f"{len(payload)} bytes",
                "Timestamp": datetime.now().isoformat(),
                "Payload": payload_display,
                "User Properties": user_properties,
                "Content Type": content_type,
                "Correlation Data": correlation_data,
                "Message Expiry": message_expiry_interval,
                "Response Topic": response_topic,
                "Payload Format": payload_format_indicator,
            }

            with self.message_lock:
                self.received_messages.append(message_info)
                self.message_count += 1

            # Immediate visual notification with enhanced formatting
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            print("\n" + "=" * 70)
            print(get_message("incoming_message").format(self.message_count, timestamp))
            print("=" * 70)

            # Core MQTT Properties
            print(f"{get_message('topic_label')} {topic}")
            qos_desc = (
                get_message("qos_at_most_once")
                if qos == 0
                else get_message("qos_at_least_once")
                if qos == 1
                else get_message("qos_exactly_once")
            )
            print(f"{get_message('qos_label')} {qos} ({qos_desc})")
            print(f"{get_message('payload_size_label')} {len(payload)} bytes")

            # MQTT Flags
            flags = []
            if dup:
                flags.append(get_message("duplicate_flag"))
            if retain:
                flags.append(get_message("retain_flag"))
            if flags:
                print(f"{get_message('flags_label')} {', '.join(flags)}")

            # MQTT5 Properties (if available)
            mqtt5_props = []
            if content_type:
                mqtt5_props.append(f"{get_message('content_type_prop')} {content_type}")
            if correlation_data:
                mqtt5_props.append(f"{get_message('correlation_data_prop')} {correlation_data}")
            if message_expiry_interval:
                mqtt5_props.append(f"{get_message('message_expiry_prop')} {message_expiry_interval}s")
            if response_topic:
                mqtt5_props.append(f"{get_message('response_topic_prop')} {response_topic}")
            if payload_format_indicator is not None:
                format_desc = get_message("utf8_string") if payload_format_indicator == 1 else get_message("bytes_format")
                mqtt5_props.append(f"{get_message('payload_format_prop')} {format_desc}")
            if user_properties:
                mqtt5_props.append(
                    f"{get_message('user_properties_prop')} {get_message('properties_count').format(len(user_properties))}"
                )
                for prop in user_properties:
                    mqtt5_props.append(f"   • {prop[0]}: {prop[1]}")

            if mqtt5_props:
                print(get_message("mqtt5_properties"))
                for prop in mqtt5_props:
                    print(f"   {prop}")

            # Payload Display
            print(get_message("message_payload"))
            if is_json:
                print(get_message("json_format"))
                for line in payload_display.split("\n"):
                    print(f"   {line}")
            else:
                print(f"{get_message('text_format')} {payload_display}")

            print("=" * 70)
            print(get_message("mqtt_prompt"), end="", flush=True)  # Restore prompt

        except Exception as e:
            print(f"\n{get_message('error_processing_message')} {str(e)}")
            print(get_message("mqtt_prompt"), end="", flush=True)

    def connect_to_aws_iot(self, thing_name, cert_file, key_file, endpoint, debug=False):
        """Establish MQTT connection to AWS IoT Core"""
        # Clean up any previous connection state
        self.cleanup_connection_state()

        # Store connection details
        self.endpoint = endpoint
        self.thing_name = thing_name

        self.print_step(1, get_message("step_establishing_connection"))

        if debug:
            print(get_message("mqtt_connection_setup"))
            print(f"   {get_message('thing_name_label')}: {thing_name}")
            print(f"   {get_message('certificate_file_label')}: {cert_file}")
            print(f"   {get_message('private_key_file_label')}: {key_file}")
            print(f"   {get_message('endpoint_label')}: {endpoint}")

        try:
            # Get client ID from user or auto-generate
            client_id = self.get_client_id(thing_name)
            if not client_id:
                return False

            # Select MQTT version
            mqtt_version = self.select_mqtt_version()
            if not mqtt_version:
                return False

            # Display connection parameters
            print(f"\n{get_message('connection_parameters')}")
            print(f"   {get_message('client_id_label')}: {client_id}")
            print(f"   {get_message('endpoint_label')}: {endpoint}")
            print(f"   {get_message('port_label')}: 8883")
            print(f"   {get_message('protocol_label')}: MQTT {mqtt_version} over TLS")
            print(f"   {get_message('authentication_label')}: X.509 Certificate")
            print(f"   {get_message('certificate_file_label')}: {cert_file}")
            print(f"   {get_message('private_key_file_label')}: {key_file}")

            # Build MQTT connection using appropriate SDK v2 builder
            if mqtt_version == "5.0" and MQTT5_AVAILABLE:
                try:
                    self.connection = mqtt5_connection_builder.mtls_from_path(
                        endpoint=endpoint,
                        port=8883,
                        cert_filepath=cert_file,
                        pri_key_filepath=key_file,
                        client_id=client_id,
                        clean_session=True,
                        keep_alive_secs=30,
                        on_connection_interrupted=self.on_connection_interrupted,
                        on_connection_resumed=self.on_connection_resumed,
                    )
                except Exception as mqtt5_error:
                    print(f"⚠️  MQTT 5.0 connection failed: {str(mqtt5_error)}")
                    print(f"🔄 {get_message('falling_back_mqtt311')}")
                    mqtt_version = "3.1.1"

            if mqtt_version == "3.1.1" or not MQTT5_AVAILABLE:
                self.connection = mqtt_connection_builder.mtls_from_path(
                    endpoint=endpoint,
                    port=8883,
                    cert_filepath=cert_file,
                    pri_key_filepath=key_file,
                    client_id=client_id,
                    clean_session=True,
                    keep_alive_secs=30,
                    on_connection_interrupted=self.on_connection_interrupted,
                    on_connection_resumed=self.on_connection_resumed,
                )

            print(f"\n{get_message('connecting_to_iot')}")
            connect_future = self.connection.connect()
            connection_result = connect_future.result()  # Wait for connection

            if debug:
                print(f"{get_message('connection_result_debug')} {connection_result}")

            self.connected = True

            self.print_mqtt_details(
                get_message("connection_established"),
                {
                    get_message("status_label"): get_message("connection_status_success"),
                    get_message("client_id_label"): client_id,
                    get_message("endpoint_label"): endpoint,
                    get_message("mqtt_version_label"): mqtt_version,
                    get_message("clean_session_label"): True,
                    get_message("keep_alive_label"): "30 seconds",
                    get_message("tls_version_label"): "1.2",
                    get_message("cert_auth_label"): "X.509 mutual TLS",
                },
            )

            # Test basic connectivity with a simple operation
            if debug:
                print(get_message("testing_connection_stability"))
                try:
                    # Try a simple operation to verify the connection is fully functional
                    import time

                    time.sleep(1)
                    print(get_message("connection_stable"))
                except Exception as test_e:
                    print(f"{get_message('connection_unstable')} {str(test_e)}")

            return True

        except Exception as e:
            print(f"{get_message('connection_failed')} {str(e)}")
            return False

    def subscribe_to_topic(self, topic, qos=0, debug=False):
        """Subscribe to an MQTT topic with enhanced error handling"""
        if not self.connected:
            print(get_message("not_connected_iot"))
            return False

        try:
            print(f"\n{get_message('subscribing_to_topic')}")
            print(f"   Topic: {topic}")
            qos_desc = get_message("qos_at_most_once") if qos == 0 else get_message("qos_at_least_once")
            print(f"   QoS: {qos} ({qos_desc})")

            if debug:
                print(get_message("debug_subscribe_operation"))
                print(f"{get_message('connection_status_debug')} {self.connected}")
                print(f"{get_message('connection_object_debug')} {self.connection}")
                print(f"{get_message('topic_pattern_debug')} {topic}")
                print(f"{get_message('requested_qos_debug')} {qos}")

            # Convert QoS to proper enum
            mqtt_qos = mqtt.QoS.AT_MOST_ONCE if qos == 0 else mqtt.QoS.AT_LEAST_ONCE

            if debug:
                print(f"{get_message('converted_qos_debug')} {mqtt_qos}")
                print(f"{get_message('callback_function_debug')} {self.on_message_received}")

            subscribe_future, packet_id = self.connection.subscribe(
                topic=topic, qos=mqtt_qos, callback=self.on_message_received
            )

            if debug:
                print(get_message("subscribe_request_sent"))
                print(f"{get_message('packet_id_debug')} {packet_id}")

            # Wait for subscription result
            subscribe_result = subscribe_future.result()

            if debug:
                print(get_message("subscribe_result_received"))
                print(f"{get_message('result_debug')} {subscribe_result}")
                print(f"{get_message('result_type_debug')} {type(subscribe_result)}")

            # Extract QoS from result - the result format may vary
            granted_qos = qos  # Default fallback
            if hasattr(subscribe_result, "qos"):
                granted_qos = subscribe_result.qos
            elif isinstance(subscribe_result, dict) and "qos" in subscribe_result:
                granted_qos = subscribe_result["qos"]

            self.subscriptions[topic] = {
                "qos": qos,
                "granted_qos": granted_qos,
                "packet_id": packet_id,
                "subscribed_at": datetime.now().isoformat(),
            }

            self.print_mqtt_details(
                get_message("subscription_established"),
                {
                    "Topic": topic,
                    get_message("qos_requested_label"): qos,
                    get_message("qos_granted_label"): granted_qos,
                    get_message("packet_id_label"): packet_id,
                    get_message("status_label"): get_message("status_subscribed"),
                    get_message("wildcard_support"): get_message("wildcard_support_msg"),
                },
            )

            return True

        except Exception as e:
            print(f"{get_message('subscription_failed')} {str(e)}")
            print(get_message("detailed_error_info"))
            print(f"{get_message('error_type_label')} {type(e).__name__}")
            print(f"{get_message('error_message_label')} {str(e)}")

            # Check for common issues
            error_str = str(e).lower()
            if "timeout" in error_str:
                print(get_message("troubleshooting_timeout"))
                for reason in get_message("timeout_reasons"):
                    print(reason)
            elif "not authorized" in error_str or "forbidden" in error_str or "access denied" in error_str:
                print(get_message("troubleshooting_auth"))
                for reason in get_message("auth_reasons"):
                    print(reason)
            elif "invalid topic" in error_str or "malformed" in error_str:
                print(get_message("troubleshooting_invalid_topic"))
                for reason in get_message("invalid_topic_reasons"):
                    print(reason)
            elif "connection" in error_str or "disconnected" in error_str:
                print(get_message("troubleshooting_connection"))
                for reason in get_message("connection_reasons"):
                    print(reason)
            else:
                print(get_message("troubleshooting_unknown"))
                for reason in get_message("unknown_reasons"):
                    print(reason.format(topic))

            if debug:
                import traceback

                print(get_message("debug_full_traceback"))
                traceback.print_exc()

            return False

    def publish_message(self, topic, message, qos=0, **mqtt_properties):
        """Publish a message to an MQTT topic with optional MQTT5 properties"""
        if not self.connected:
            print(get_message("not_connected_iot"))
            return False

        try:
            # Prepare payload
            if isinstance(message, dict):
                payload = json.dumps(message)
                content_type = "application/json"
            else:
                payload = str(message)
                # Auto-detect JSON content type
                try:
                    json.loads(payload)
                    content_type = "application/json"
                except (json.JSONDecodeError, ValueError):
                    content_type = "text/plain"

            # Extract MQTT5 properties
            user_properties = mqtt_properties.get("user_properties", [])
            correlation_data = mqtt_properties.get("correlation_data", None)
            message_expiry_interval = mqtt_properties.get("message_expiry_interval", None)
            response_topic = mqtt_properties.get("response_topic", None)

            print(f"\n{get_message('publishing_message')}")
            print(f"   Topic: {topic}")
            qos_desc = (
                get_message("qos_at_most_once")
                if qos == 0
                else get_message("qos_at_least_once")
                if qos == 1
                else get_message("qos_exactly_once")
            )
            print(f"   QoS: {qos} ({qos_desc})")
            print(f"   Payload Size: {len(payload)} bytes")
            print(f"   {get_message('content_type_label')}: {content_type}")

            # Show MQTT5 properties if any
            if user_properties or correlation_data or message_expiry_interval or response_topic:
                print(f"   {get_message('mqtt5_properties_label')}")
                if correlation_data:
                    print(f"      {get_message('correlation_data_prop')} {correlation_data}")
                if message_expiry_interval:
                    print(f"      {get_message('message_expiry_prop')} {message_expiry_interval}s")
                if response_topic:
                    print(f"      {get_message('response_topic_prop')} {response_topic}")
                if user_properties:
                    print(f"      {get_message('user_properties_prop')}")
                    for prop in user_properties:
                        print(f"         • {prop[0]}: {prop[1]}")

            # Prepare publish parameters
            publish_params = {"topic": topic, "payload": payload, "qos": qos}

            # Prepare publish parameters
            publish_params = {"topic": topic, "payload": payload, "qos": qos}

            # Convert QoS to proper enum
            mqtt_qos = mqtt.QoS.AT_MOST_ONCE if qos == 0 else mqtt.QoS.AT_LEAST_ONCE
            publish_params["qos"] = mqtt_qos

            # Debug publish parameters
            debug_mode = getattr(self, "debug_mode", False)
            if debug_mode:
                print("🔍 DEBUG: Publish parameters:")
                print(f"   Topic: {publish_params['topic']}")
                print(f"   QoS: {publish_params['qos']}")
                print(f"   Payload length: {len(publish_params['payload'])}")

            publish_future, packet_id = self.connection.publish(**publish_params)

            # Wait for publish to complete
            publish_future.result()

            message_info = {
                "Direction": "SENT",
                "Topic": topic,
                "QoS": qos,
                "Packet ID": packet_id,
                "Payload Size": f"{len(payload)} bytes",
                "Timestamp": datetime.now().isoformat(),
                "Payload": payload,
                "Content Type": content_type,
                "User Properties": user_properties,
                "Correlation Data": correlation_data,
                "Message Expiry": message_expiry_interval,
                "Response Topic": response_topic,
            }

            with self.message_lock:
                self.sent_messages.append(message_info)

            # Enhanced publish confirmation with protocol details
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            print(get_message("published_timestamp").format(timestamp))
            print(f"   📤 Topic: {topic}")
            print(f"   🏷️  QoS: {qos} | Packet ID: {packet_id}")
            print(f"   📊 Size: {len(payload)} bytes | Type: {content_type}")
            if qos > 0:
                print(f"   {get_message('delivery_ack_required').format(qos)}")
            else:
                print(f"   {get_message('delivery_fire_forget')}")

            return True

        except Exception as e:
            print(f"{get_message('publish_failed')} {str(e)}")
            print(get_message("detailed_error_info"))
            print(f"{get_message('error_type_label')} {type(e).__name__}")
            print(f"{get_message('error_message_label')} {str(e)}")

            # Check for common issues
            error_str = str(e).lower()
            if "timeout" in error_str:
                print(get_message("troubleshooting_publish_timeout"))
                for reason in get_message("timeout_reasons"):
                    print(reason)
            elif "not authorized" in error_str or "forbidden" in error_str or "access denied" in error_str:
                print(get_message("troubleshooting_auth"))
                for reason in get_message("auth_reasons"):
                    print(reason)
            elif "invalid topic" in error_str or "malformed" in error_str:
                print(get_message("troubleshooting_invalid_topic"))
                for reason in get_message("invalid_topic_reasons"):
                    print(reason)
            elif "payload too large" in error_str:
                print(get_message("troubleshooting_payload_large"))
                print(get_message("payload_limit_msg"))
                print(get_message("current_payload_size").format(len(payload)))
            elif "connection" in error_str or "disconnected" in error_str:
                print(get_message("troubleshooting_connection"))
                for reason in get_message("connection_reasons"):
                    print(reason)
            else:
                print(get_message("troubleshooting_unknown"))
                for reason in get_message("unknown_reasons"):
                    print(reason.format(topic))

            return False


def main():
    """Main function"""
    global USER_LANG, messages, DEBUG_MODE

    # Parse command line arguments
    if len(sys.argv) > 1 and sys.argv[1] in ["--debug", "-d"]:
        DEBUG_MODE = True

    # Get user's preferred language
    USER_LANG = get_language()
    messages = load_messages("mqtt_client_explorer", USER_LANG)

    # Display header
    print(f"\n{get_message('title')}")
    print(get_message("separator"))

    print(f"\n{get_message('description_intro')}")
    for concept in get_message("mqtt_concepts"):
        print(concept)

    if DEBUG_MODE:
        print(f"\n{get_message('debug_enabled')}")
        for feature in get_message("debug_features"):
            print(feature)
    else:
        print(f"\n{get_message('tip')}")

    # Display AWS context
    display_aws_context()

    # Initialize MQTT client
    mqtt_client = MQTTClientExplorer()

    try:
        while True:
            print(f"\n{get_message('main_menu')}")
            for option in get_message("menu_options"):
                print(option)

            try:
                choice = input(f"\n{get_message('select_option')}").strip()

                if choice == "1":
                    # Connect to AWS IoT Core and start interactive mode
                    endpoint = mqtt_client.get_iot_endpoint(DEBUG_MODE)
                    if endpoint:
                        thing_name, cert_file, key_file = mqtt_client.select_device_and_certificate(DEBUG_MODE)
                        if thing_name and cert_file and key_file:
                            if mqtt_client.connect_to_aws_iot(thing_name, cert_file, key_file, endpoint, DEBUG_MODE):
                                # Automatically start interactive messaging after successful connection
                                interactive_messaging(mqtt_client)

                elif choice == "2":
                    print(f"\n{get_message('goodbye')}")
                    break

                else:
                    print(get_message("invalid_choice"))

                # No need for press enter since we only have connect and exit

            except KeyboardInterrupt:
                print(f"\n\n{get_message('goodbye')}")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")
                if DEBUG_MODE:
                    import traceback

                    traceback.print_exc()

    finally:
        # Clean up connection
        if mqtt_client.connected and mqtt_client.connection:
            try:
                mqtt_client.connection.disconnect()
            except Exception:
                pass


if __name__ == "__main__":
    main()
