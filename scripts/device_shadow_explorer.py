#!/usr/bin/env python3
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

"""
AWS IoT Device Shadow Explorer
Educational tool for learning AWS IoT Device Shadow service through hands-on exploration.
"""
import json
import os
import re
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


def get_learning_moment(moment_key):
    """Get localized learning moment"""
    return messages.get("learning_moments", {}).get(moment_key, {})


def print_learning_moment(moment_key):
    """Print a formatted learning moment"""
    moment = get_learning_moment(moment_key)
    if not moment:
        return

    print(f"\n{moment.get('title', '')}")
    print(moment.get("content", ""))
    print(f"\n🔄 NEXT: {moment.get('next', '')}")
    print(f"\n{get_message('press_enter')}")
    try:
        input()
    except KeyboardInterrupt:
        print(f"\n{get_message('goodbye')}")
        sys.exit(0)


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


class DeviceShadowExplorer:
    def __init__(self):
        self.connection = None
        self.connected = False
        self.thing_name = None
        self.shadow_name = None  # Classic shadow uses None
        self.local_state_file = None
        self.received_messages = []
        self.message_lock = threading.Lock()
        self.debug_mode = DEBUG_MODE
        self.last_shadow_response = None

    def print_header(self, title):
        """Print formatted header"""
        print(f"\n🌟 {title}")
        print("=" * 60)

    def print_step(self, step, description):
        """Print step with formatting"""
        print(f"\n🔧 Step {step}: {description}")
        print("-" * 50)

    def print_shadow_details(self, message_type, details):
        """Print detailed Shadow protocol information"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"\n📊 Shadow {message_type} [{timestamp}]")
        print("-" * 40)

        for key, value in details.items():
            if isinstance(value, dict):
                print(f"   {key}:")
                for sub_key, sub_value in value.items():
                    print(f"      {sub_key}: {sub_value}")
            else:
                print(f"   {key}: {value}")

    def get_iot_endpoint(self, debug=False):
        """Get AWS IoT endpoint for the account"""
        try:
            iot = boto3.client("iot")

            if debug:
                print(get_message("debug_calling_describe_endpoint"))
                print(get_message("debug_input_parameters"))

            response = iot.describe_endpoint(endpointType="iot:Data-ATS")
            endpoint = response["endpointAddress"]

            if debug:
                print(get_message("debug_api_response").format(json.dumps(response, indent=2, default=str)))

            print(get_message("iot_endpoint_discovery"))
            print(f"   {get_message('endpoint_type')}: {get_message('endpoint_type_ats')}")
            print(f"   {get_message('endpoint_url')}: {endpoint}")
            print(f"   {get_message('port_mqtt_tls')}")
            print(f"   {get_message('protocol_mqtt')}")

            return endpoint
        except Exception as e:
            print(f"{get_message('error_getting_endpoint')} {str(e)}")
            if debug:
                import traceback

                print(get_message("debug_full_traceback"))
                traceback.print_exc()
            return None

    def select_device_and_certificate(self, debug=False):
        """Select a device and its certificate for Shadow operations"""
        try:
            iot = boto3.client("iot")

            # Get all Things
            if debug:
                print(get_message("debug_calling_list_things"))
                print(get_message("debug_input_params_none"))

            things_response = iot.list_things()
            things = things_response.get("things", [])

            if debug:
                print(get_message("debug_found_things", len(things)))
                print(get_message("debug_thing_names", [t["thingName"] for t in things]))

            if not things:
                print(get_message("no_things_found"))
                return None, None, None

            print(f"\n{get_message('available_devices', len(things))}")
            for i, thing in enumerate(things, 1):
                print(
                    f"   {i}. {thing['thingName']} ({get_message('type')}: {thing.get('thingTypeName', get_message('none'))})"
                )

            while True:
                try:
                    choice = int(input(f"\n{get_message('select_option').replace('(1-7)', f'(1-{len(things)})')}: ")) - 1
                    if 0 <= choice < len(things):
                        selected_thing = things[choice]["thingName"]
                        break
                    else:
                        print(get_message("invalid_selection", len(things)))
                except ValueError:
                    print(get_message("enter_valid_number"))
                except KeyboardInterrupt:
                    print(f"\n{get_message('operation_cancelled')}")
                    return None, None, None

            print(f"{get_message('selected_device')} {selected_thing}")

            # Get certificates for the selected Thing
            if debug:
                print(get_message("debug_calling_list_principals"))
                print(get_message("debug_input_thing_name").format(selected_thing))

            principals_response = iot.list_thing_principals(thingName=selected_thing)
            principals = principals_response.get("principals", [])
            cert_arns = [p for p in principals if "cert/" in p]

            if debug:
                print(get_message("debug_found_principals", len(principals), len(cert_arns)))
                print(get_message("debug_cert_arns", cert_arns))

            if not cert_arns:
                print(get_message("no_certificates_found", selected_thing))
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
                        choice = int(input(get_message("select_certificate", len(cert_arns)))) - 1
                        if 0 <= choice < len(cert_arns):
                            selected_cert_arn = cert_arns[choice]
                            cert_id = selected_cert_arn.split("/")[-1]
                            break
                        else:
                            print(get_message("invalid_selection_cert"))
                    except ValueError:
                        print(get_message("enter_valid_number"))

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
                print(get_message("cert_files_not_found", cert_dir))
                print(f"   {get_message('looking_for_files', cert_id)}")
                return None, None, None

            print(get_message("certificate_files_found"))
            print(f"   {get_message('certificate')}: {cert_file}")
            print(f"   {get_message('private_key')}: {key_file}")

            return selected_thing, cert_file, key_file

        except Exception as e:
            print(f"{get_message('error_selecting_device')} {str(e)}")
            return None, None, None

    def setup_local_state_file(self, thing_name, debug=False):
        """Setup local state file for device shadow simulation"""
        # Validate thing_name to prevent path traversal
        if not re.match(r"^[a-zA-Z0-9_-]+$", thing_name):
            print(f"{get_message('invalid_thing_name')} {thing_name}")
            return None

        cert_dir = os.path.join(os.getcwd(), "certificates", thing_name)
        # Validate the constructed path stays within certificates directory
        if not os.path.abspath(cert_dir).startswith(os.path.abspath(os.path.join(os.getcwd(), "certificates"))):
            print(f"{get_message('unsafe_path_detected')} {thing_name}")
            return None

        state_file = os.path.join(cert_dir, "device_state.json")

        if debug:
            print(get_message("debug_setting_up_state", state_file))
            print(get_message("debug_cert_directory", cert_dir))
            print(get_message("debug_file_exists", os.path.exists(state_file)))

        # Create default state if file doesn't exist
        if not os.path.exists(state_file):
            default_state = {
                "temperature": 22.5,
                "humidity": 45.0,
                "status": "online",
                "firmware_version": "1.0.0",
                "last_updated": datetime.now().isoformat(),
            }

            with open(state_file, "w", encoding="utf-8") as f:
                json.dump(default_state, f, indent=2)

            print(f"{get_message('created_default_state')} {state_file}")
            print(f"{get_message('default_state')} {json.dumps(default_state, indent=2)}")
            if debug:
                print(get_message("debug_created_new_state", len(default_state)))
        else:
            print(f"{get_message('using_existing_state')} {state_file}")
            with open(state_file, "r", encoding="utf-8") as f:
                current_state = json.load(f)
            print(f"{get_message('current_local_state')} {json.dumps(current_state, indent=2)}")
            if debug:
                print(get_message("debug_loaded_existing_state", len(current_state)))
                print(get_message("debug_file_size", os.path.getsize(state_file)))

        self.local_state_file = state_file
        return state_file

    def load_local_state(self):
        """Load current local device state"""
        try:
            with open(self.local_state_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"{get_message('local_state_not_found')} {self.local_state_file}")
            return {}
        except json.JSONDecodeError as e:
            print(f"{get_message('invalid_json_state')} {str(e)}")
            return {}
        except PermissionError:
            print(f"{get_message('permission_denied_state')} {self.local_state_file}")
            return {}
        except Exception as e:
            print(f"{get_message('unexpected_error_loading')} {str(e)}")
            return {}

    def save_local_state(self, state):
        """Save device state to local file"""
        try:
            state["last_updated"] = datetime.now().isoformat()
            with open(self.local_state_file, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2)
            print(f"{get_message('local_state_saved')} {self.local_state_file}")
            return True
        except PermissionError:
            print(f"{get_message('permission_denied_writing')} {self.local_state_file}")
            return False
        except OSError as e:
            print(f"{get_message('filesystem_error_saving')} {str(e)}")
            return False
        except TypeError as e:
            print(f"{get_message('invalid_state_data')} {str(e)}")
            return False
        except Exception as e:
            print(f"{get_message('unexpected_error_saving')} {str(e)}")
            return False

    def on_connection_interrupted(self, connection, error, **kwargs):
        """Callback for connection interruption"""
        self.print_shadow_details(
            get_message("connection_interrupted"),
            {
                get_message("error"): str(error),
                get_message("timestamp"): datetime.now().isoformat(),
                get_message("auto_reconnect"): get_message("sdk_will_reconnect"),
            },
        )
        self.connected = False

    def on_connection_resumed(self, connection, return_code, session_present, **kwargs):
        """Callback for connection resumption"""
        self.print_shadow_details(
            get_message("connection_resumed"),
            {
                get_message("return_code"): return_code,
                get_message("session_present"): session_present,
                get_message("timestamp"): datetime.now().isoformat(),
                get_message("status"): get_message("connection_restored"),
            },
        )
        self.connected = True

    def on_shadow_message_received(self, topic, payload, dup, qos, retain, **kwargs):
        """Callback for Shadow messages with comprehensive analysis"""
        try:
            # Parse shadow message
            try:
                shadow_data = json.loads(payload.decode("utf-8"))
                payload_display = json.dumps(shadow_data, indent=2)
            except (json.JSONDecodeError, UnicodeDecodeError):
                payload_display = payload.decode("utf-8")
                shadow_data = {}

            message_info = {
                get_message("direction"): get_message("received"),
                get_message("topic"): topic,
                get_message("qos"): qos,
                get_message("payload_size"): f"{len(payload)} bytes",
                get_message("timestamp"): datetime.now().isoformat(),
                get_message("shadow_data"): shadow_data,
            }

            with self.message_lock:
                self.received_messages.append(message_info)
                # Store last response for shadow existence checking
                self.last_shadow_response = shadow_data

            # Immediate visual notification
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            print("\n" + "=" * 70)
            print(f"{get_message('shadow_message_received')} [{timestamp}]")
            print("=" * 70)

            if self.debug_mode:
                print(get_message("debug_raw_topic").format(topic))
                print(get_message("debug_qos_duplicate").format(qos, dup, retain))
                print(get_message("debug_payload_size").format(len(payload)))
                print(get_message("debug_message_count").format(len(self.received_messages)))

            # Analyze topic to determine message type
            if "get" in topic and "accepted" in topic:
                self.handle_shadow_get_accepted(shadow_data)
            elif "get" in topic and "rejected" in topic:
                self.handle_shadow_get_rejected(shadow_data)
            elif "update" in topic and "accepted" in topic:
                self.handle_shadow_update_accepted(shadow_data)
            elif "update" in topic and "rejected" in topic:
                self.handle_shadow_update_rejected(shadow_data)
            elif "update" in topic and "delta" in topic:
                self.handle_shadow_delta(shadow_data)
            else:
                print(f"📥 {get_message('topic')}: {topic}")
                print(f"🏷️  {get_message('qos')}: {qos}")
                print(f"📊 Payload: {payload_display}")
                if self.debug_mode:
                    print(get_message("debug_unrecognized_topic"))

            print("=" * 70)

        except Exception as e:
            print(f"\n{get_message('error_processing_message')} {str(e)}")

    def handle_shadow_get_accepted(self, shadow_data):
        """Handle shadow get accepted response"""
        print(get_message("shadow_get_accepted"))
        if self.debug_mode:
            print(f"   📝 {get_message('topic')}: $aws/things/{self.thing_name}/shadow/get/accepted")
        print(get_message("shadow_document_retrieved"))

        state = shadow_data.get("state", {})
        desired = state.get("desired", {})
        reported = state.get("reported", {})
        version = shadow_data.get("version", "Unknown")

        print(f"   📊 {get_message('version')}: {version}")
        print(f"   🎯 {get_message('desired_state')}: {json.dumps(desired, indent=6) if desired else get_message('none')}")
        print(f"   📡 {get_message('reported_state')}: {json.dumps(reported, indent=6) if reported else get_message('none')}")

        # Compare with local state
        if desired:
            if self.debug_mode:
                print(get_message("debug_comparing_desired"))
                print(get_message("debug_desired_keys").format(list(desired.keys())))
            self.compare_and_prompt_update(desired)
        elif self.debug_mode:
            print(get_message("debug_no_desired_state"))

    def handle_shadow_get_rejected(self, shadow_data):
        """Handle shadow get rejected response"""
        print(get_message("shadow_get_rejected"))
        if self.debug_mode:
            print(f"   📝 {get_message('topic')}: $aws/things/{self.thing_name}/shadow/get/rejected")
        error_code = shadow_data.get("code", "Unknown")
        error_message = shadow_data.get("message", "No message")
        print(f"   🚫 {get_message('error_code')}: {error_code}")
        print(f"   📝 {get_message('message')}: {error_message}")

        # Store error code for shadow existence checking
        with self.message_lock:
            self.last_shadow_response = {
                "error_code": error_code,
                "error_message": error_message,
            }

        if error_code == 404:
            print(f"   💡 {get_message('shadow_doesnt_exist')}")
            if self.debug_mode:
                print(get_message("debug_normal_for_new"))
        elif self.debug_mode:
            print(get_message("debug_error_code_indicates").format(error_code, error_message))

    def handle_shadow_update_accepted(self, shadow_data):
        """Handle shadow update accepted response"""
        print(get_message("shadow_update_accepted"))
        if self.debug_mode:
            print(f"   📝 {get_message('topic')}: $aws/things/{self.thing_name}/shadow/update/accepted")
        state = shadow_data.get("state", {})
        version = shadow_data.get("version", "Unknown")
        timestamp = shadow_data.get("timestamp", "Unknown")

        print(f"   📊 {get_message('new_version')}: {version}")
        print(f"   ⏰ {get_message('timestamp')}: {timestamp}")
        if "desired" in state:
            print(f"   🎯 {get_message('updated_desired')}: {json.dumps(state['desired'], indent=6)}")
        if "reported" in state:
            print(f"   📡 {get_message('updated_reported')}: {json.dumps(state['reported'], indent=6)}")

    def handle_shadow_update_rejected(self, shadow_data):
        """Handle shadow update rejected response"""
        print(get_message("shadow_update_rejected"))
        if self.debug_mode:
            print(f"   📝 {get_message('topic')}: $aws/things/{self.thing_name}/shadow/update/rejected")
        error_code = shadow_data.get("code", "Unknown")
        error_message = shadow_data.get("message", "No message")
        print(f"   🚫 {get_message('error_code')}: {error_code}")
        print(f"   📝 {get_message('message')}: {error_message}")

    def handle_shadow_delta(self, shadow_data):
        """Handle shadow delta message (desired != reported)"""
        print(get_message("shadow_delta_received"))
        if self.debug_mode:
            print(f"   📝 {get_message('topic')}: $aws/things/{self.thing_name}/shadow/update/delta")
        print(f"   📝 {get_message('description')}: {get_message('desired_differs_reported')}")

        state = shadow_data.get("state", {})
        version = shadow_data.get("version", "Unknown")
        timestamp = shadow_data.get("timestamp", "Unknown")

        print(f"   📊 {get_message('version')}: {version}")
        print(f"   ⏰ {get_message('timestamp')}: {timestamp}")
        print(f"   🔄 {get_message('changes_needed')}: {json.dumps(state, indent=6)}")

        # Prompt user to apply changes
        if self.debug_mode:
            print(get_message("debug_processing_delta").format(len(state)))
            print(get_message("debug_delta_keys").format(list(state.keys())))
        self.compare_and_prompt_update(state, is_delta=True)

    def compare_and_prompt_update(self, desired_state, is_delta=False):
        """Compare desired state with local state and prompt for updates"""
        local_state = self.load_local_state()

        if self.debug_mode:
            print(get_message("debug_loaded_local_state").format(len(local_state)))
            print(get_message("debug_comparing_properties").format(len(desired_state)))

        print(f"\n{get_message('state_comparison')}")
        print(f"   📱 {get_message('local_state')}: {json.dumps(local_state, indent=6)}")
        print(f"   {get_message('delta') if is_delta else get_message('desired')}: {json.dumps(desired_state, indent=6)}")

        # Find differences
        differences = {}
        for key, desired_value in desired_state.items():
            local_value = local_state.get(key)
            if local_value != desired_value:
                differences[key] = {"local": local_value, "desired": desired_value}

        if differences:
            if self.debug_mode:
                print(get_message("debug_differences_found").format(len(differences), len(desired_state)))
            print(f"\n{get_message('differences_found')}")
            for key, diff in differences.items():
                print(f"   • {key}: {diff['local']} → {diff['desired']}")
                if self.debug_mode:
                    print(
                        get_message("debug_type_change").format(type(diff["local"]).__name__, type(diff["desired"]).__name__)
                    )

            apply_changes = input(f"\n{get_message('apply_changes_prompt')}").strip().lower()
            if apply_changes == "y":
                time.sleep(0.1)  # nosemgrep: arbitrary-sleep
                # Update local state
                for key, desired_value in desired_state.items():
                    local_state[key] = desired_value

                if self.save_local_state(local_state):
                    if self.debug_mode:
                        print(get_message("debug_updated_properties").format(len(desired_state)))
                        print(get_message("debug_new_state_size").format(len(local_state)))
                    print(get_message("local_state_updated"))

                    # Automatically report back to shadow (required for proper synchronization)
                    print(get_message("automatically_reporting"))
                    self.update_shadow_reported(local_state)
                    time.sleep(1.5)  # nosemgrep: arbitrary-sleep
                else:
                    print(get_message("failed_update_local"))
            else:
                print(get_message("changes_not_applied"))
        else:
            if self.debug_mode:
                print(get_message("debug_all_match").format(len(desired_state)))
            print(get_message("local_matches_desired"))

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
        rules = get_message("client_id_rules")
        if isinstance(rules, list):
            for rule in rules:
                print(f"   {rule}")
        else:
            print(f"   {rules}")

        while True:
            try:
                custom_id = input(f"\n{get_message('client_id_prompt')}").strip()

                if not custom_id:
                    # Auto-generate client ID
                    client_id = f"{thing_name}-shadow-{uuid.uuid4().hex[:8]}"
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

    def connect_to_aws_iot(self, thing_name, cert_file, key_file, endpoint, debug=False):
        """Establish MQTT connection to AWS IoT Core for Shadow operations"""
        self.print_step(1, get_message("step_establishing_connection"))

        if debug:
            print(get_message("debug_shadow_connection_setup"))
            print(get_message("debug_thing_name").format(thing_name))
            print(get_message("debug_cert_file").format(cert_file))
            print(get_message("debug_private_key_file").format(key_file))
            print(get_message("debug_endpoint").format(endpoint))

        try:
            # Get client ID from user or auto-generate
            client_id = self.get_client_id(thing_name)
            if not client_id:
                return False

            print(get_message("shadow_connection_params"))
            print(f"   {get_message('client_id')}: {client_id}")
            print(f"   {get_message('thing_name')}: {thing_name}")
            print(f"   {get_message('endpoint')}: {endpoint}")
            print(f"   {get_message('port')}: 8883")
            print(f"   {get_message('protocol')}: MQTT 3.1.1 over TLS")
            print(f"   {get_message('authentication')}: X.509 Certificate")
            print(f"   {get_message('shadow_type')}: {get_message('shadow_type_classic')}")

            # Build MQTT connection
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
            connection_result = connect_future.result()

            if debug:
                print(get_message("debug_connection_result").format(connection_result))

            self.connected = True
            self.thing_name = thing_name

            self.print_shadow_details(
                get_message("connection_established"),
                {
                    get_message("status"): get_message("connection_status"),
                    get_message("client_id"): client_id,
                    get_message("thing_name"): thing_name,
                    get_message("endpoint"): endpoint,
                    get_message("shadow_type"): get_message("shadow_type_classic"),
                    get_message("clean_session"): True,
                    get_message("keep_alive"): "30 seconds",
                    get_message("tls_version"): "1.2",
                    get_message("certificate_auth"): "X.509 mutual TLS",
                },
            )

            return True

        except Exception as e:
            print(f"{get_message('shadow_connection_failed')} {str(e)}")
            return False

    def subscribe_to_shadow_topics(self, debug=False):
        """Subscribe to all relevant shadow topics"""
        self.print_step(2, get_message("step_subscribing_topics"))

        if not self.connected:
            print(get_message("not_connected"))
            return False

        # Shadow topic patterns for classic shadow
        shadow_topics = [
            f"$aws/things/{self.thing_name}/shadow/get/accepted",
            f"$aws/things/{self.thing_name}/shadow/get/rejected",
            f"$aws/things/{self.thing_name}/shadow/update/accepted",
            f"$aws/things/{self.thing_name}/shadow/update/rejected",
            f"$aws/things/{self.thing_name}/shadow/update/delta",
        ]

        print(f"{get_message('shadow_topics_for_thing')} {self.thing_name}")
        print(get_message("classic_shadow_topics"))

        success_count = 0
        for topic in shadow_topics:
            try:
                if debug:
                    print(get_message("debug_subscribing_topic").format(topic))

                subscribe_future, packet_id = self.connection.subscribe(
                    topic=topic,
                    qos=mqtt.QoS.AT_LEAST_ONCE,
                    callback=self.on_shadow_message_received,
                )

                subscribe_future.result()

                print(f"   ✅ {topic}")
                success_count += 1

                if debug:
                    print(get_message("debug_subscription_successful").format(packet_id))

            except Exception as e:
                print(f"   ❌ {topic} - Error: {str(e)}")

        if success_count == len(shadow_topics):
            print(f"\n{get_message('subscription_successful').format(success_count)}")

            print(f"\n{get_message('shadow_topic_explanations')}")
            print(f"   {get_message('topic_get_accepted')}")
            print(f"   {get_message('topic_get_rejected')}")
            print(f"   {get_message('topic_update_accepted')}")
            print(f"   {get_message('topic_update_rejected')}")
            print(f"   {get_message('topic_update_delta')}")

            return True
        else:
            print(get_message("subscription_partial").format(success_count, len(shadow_topics)))
            return False

    def get_shadow_document(self, debug=False, wait_for_response=False):
        """Request the current shadow document"""
        if not self.connected:
            print(get_message("not_connected"))
            return False

        try:
            get_topic = f"$aws/things/{self.thing_name}/shadow/get"

            print(f"\n{get_message('requesting_shadow_document')}")
            print(f"   {get_message('topic')}: {get_topic}")
            print(f"   {get_message('thing')}: {self.thing_name}")
            print(f"   {get_message('shadow_type')}: {get_message('shadow_type_classic')}")

            if debug:
                print(get_message("debug_publishing_shadow_get"))
                print(get_message("debug_topic").format(get_topic))
                print(get_message("debug_payload_empty"))

            # Shadow get requests have empty payload
            publish_future, packet_id = self.connection.publish(topic=get_topic, payload="", qos=mqtt.QoS.AT_LEAST_ONCE)

            # Non-blocking publish - don't wait for result
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            print(f"{get_message('shadow_get_request_sent')} [{timestamp}]")
            print(f"   📤 {get_message('topic')}: {get_topic}")
            print(f"   🏷️  {get_message('qos')}: 1 | {get_message('packet_id')}: {packet_id}")
            print(f"   {get_message('waiting_for_response')}")

            return True

        except Exception as e:
            print(f"{get_message('failed_request_shadow')} {str(e)}")
            return False

    def update_shadow_reported(self, reported_state, debug=False):
        """Update the reported state in the shadow"""
        if not self.connected:
            print(get_message("not_connected"))
            return False

        try:
            update_topic = f"$aws/things/{self.thing_name}/shadow/update"

            print(f"\n{get_message('updating_shadow_reported')}")
            print(f"\n{get_message('reported_state_update')}")
            print(f"   {get_message('current_local_state_label')}: {json.dumps(reported_state, indent=2)}")

            # Create shadow update payload
            shadow_update = {"state": {"reported": reported_state}}

            print(f"   {get_message('shadow_update_payload')}: {json.dumps(shadow_update, indent=2)}")

            payload = json.dumps(shadow_update)

            if debug:
                print(get_message("debug_publishing_shadow_update"))
                print(get_message("debug_topic").format(update_topic))
                print(get_message("debug_payload_json").format(json.dumps(shadow_update, indent=2)))
                print(get_message("debug_update_type").format("reported"))

            publish_future, packet_id = self.connection.publish(
                topic=update_topic, payload=payload, qos=mqtt.QoS.AT_LEAST_ONCE
            )

            # Non-blocking publish - don't wait for result
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            print(f"{get_message('shadow_update_sent')} [{timestamp}]")
            print(f"   📤 {get_message('topic')}: {update_topic}")
            print(f"   🏷️  {get_message('qos')}: 1 | {get_message('packet_id')}: {packet_id}")
            print(f"   {get_message('waiting_for_response')}")

            return True

        except Exception as e:
            print(f"{get_message('failed_update_reported')} {str(e)}")
            return False

    def update_shadow_desired(self, desired_state, debug=False):
        """Update the desired state in the shadow (simulates cloud/app request)"""
        if not self.connected:
            print(get_message("not_connected"))
            return False

        try:
            update_topic = f"$aws/things/{self.thing_name}/shadow/update"

            print(f"\n{get_message('updating_shadow_desired')}")
            print(f"\n{get_message('desired_state_update')}")
            print(f"   {get_message('desired_state_to_set')}: {json.dumps(desired_state, indent=2)}")

            # Create shadow update payload
            shadow_update = {"state": {"desired": desired_state}}

            payload = json.dumps(shadow_update)

            print(f"   {get_message('shadow_update_payload')}: {json.dumps(shadow_update, indent=2)}")
            print(f"   {get_message('topic')}: {update_topic}")
            print(f"   {get_message('thing')}: {self.thing_name}")
            if debug:
                print(get_message("debug_publishing_shadow_update"))
                print(get_message("debug_topic", update_topic))
                print(get_message("debug_payload_json", json.dumps(shadow_update, indent=2)))
                print(get_message("debug_update_type", "desired"))

            publish_future, packet_id = self.connection.publish(
                topic=update_topic, payload=payload, qos=mqtt.QoS.AT_LEAST_ONCE
            )

            # Non-blocking publish - don't wait for result
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            print(f"{get_message('shadow_update_desired_sent')} [{timestamp}]")
            print(f"   📤 {get_message('topic')}: {update_topic}")
            print(f"   🏷️  {get_message('qos')}: 1 | {get_message('packet_id')}: {packet_id}")
            print(f"   {get_message('waiting_for_response')}")

            return True

        except Exception as e:
            print(f"{get_message('failed_update_desired')} {str(e)}")
            return False

    def run_interactive_menu(self):
        """Run the interactive menu system"""
        connected = False
        start_time = time.time()

        while True:
            try:
                print(f"\n{get_message('main_menu')}")
                for option in get_message("menu_options"):
                    print(f"   {option}")

                choice = input(f"\n{get_message('select_option')}")

                if choice == "1":
                    if not connected:
                        print_learning_moment("shadow_connection")

                        # Get IoT endpoint
                        endpoint = self.get_iot_endpoint(debug=self.debug_mode)
                        if not endpoint:
                            continue

                        # Select device and certificate
                        (
                            thing_name,
                            cert_file,
                            key_file,
                        ) = self.select_device_and_certificate(debug=self.debug_mode)
                        if not thing_name:
                            continue

                        # Setup local state file
                        self.setup_local_state_file(thing_name, debug=self.debug_mode)

                        # Connect to AWS IoT
                        if self.connect_to_aws_iot(
                            thing_name,
                            cert_file,
                            key_file,
                            endpoint,
                            debug=self.debug_mode,
                        ):
                            # Subscribe to shadow topics
                            if self.subscribe_to_shadow_topics(debug=self.debug_mode):
                                connected = True
                                start_time = time.time()
                                print(f"\n✅ {get_message('connection_established')}")
                            else:
                                print("\n❌ Failed to subscribe to shadow topics")
                        else:
                            print("\n❌ Failed to connect to AWS IoT")
                    else:
                        print("\n✅ Already connected to AWS IoT Core")

                elif choice == "2":
                    if not connected:
                        print(f"\n❌ {get_message('not_connected')}")
                        print("💡 Please connect first (option 1)")
                        continue

                    print_learning_moment("shadow_document")
                    self.get_shadow_document(debug=self.debug_mode)

                elif choice == "3":
                    if not connected:
                        print(f"\n❌ {get_message('not_connected')}")
                        print("💡 Please connect first (option 1)")
                        continue

                    print_learning_moment("reported_state")
                    local_state = self.load_local_state()
                    self.update_shadow_reported(local_state, debug=self.debug_mode)

                elif choice == "4":
                    if not connected:
                        print(f"\n❌ {get_message('not_connected')}")
                        print("💡 Please connect first (option 1)")
                        continue

                    print_learning_moment("desired_state")
                    self.update_shadow_desired_interactive()

                elif choice == "5":
                    if not connected:
                        print(f"\n❌ {get_message('not_connected')}")
                        print("💡 Please connect first (option 1)")
                        continue

                    print_learning_moment("state_simulation")
                    self.simulate_device_state_changes()

                elif choice == "6":
                    if not connected:
                        print(f"\n❌ {get_message('not_connected')}")
                        print("💡 Please connect first (option 1)")
                        continue

                    self.view_shadow_message_history()

                elif choice == "7":
                    if connected:
                        self.disconnect_and_summarize(start_time)
                    print(f"\n{get_message('goodbye')}")
                    break

                else:
                    print(get_message("invalid_choice"))

            except KeyboardInterrupt:
                print(f"\n\n{get_message('operation_cancelled')}")
                if connected:
                    self.disconnect_and_summarize(start_time)
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")
                if self.debug_mode:
                    import traceback

                    traceback.print_exc()

    def run_auto_connect_and_interactive(self):
        """Auto-connect and run interactive shadow management"""
        print_learning_moment("shadow_connection")

        # Get IoT endpoint
        endpoint = self.get_iot_endpoint(debug=self.debug_mode)
        if not endpoint:
            print("❌ Failed to get IoT endpoint")
            return

        # Select device and certificate
        thing_name, cert_file, key_file = self.select_device_and_certificate(debug=self.debug_mode)
        if not thing_name:
            print("❌ Failed to select device and certificate")
            return

        # Setup local state file
        self.setup_local_state_file(thing_name, debug=self.debug_mode)

        # Connect to AWS IoT
        if not self.connect_to_aws_iot(thing_name, cert_file, key_file, endpoint, debug=self.debug_mode):
            print("❌ Failed to connect to AWS IoT")
            return

        # Subscribe to shadow topics
        if not self.subscribe_to_shadow_topics(debug=self.debug_mode):
            print("❌ Failed to subscribe to shadow topics")
            return

        print(f"\n✅ {get_message('connection_established')}")

        # Check if shadow exists, create if it doesn't
        self.ensure_shadow_exists()

        # Go directly into interactive shadow management
        self.interactive_shadow_management()

    def ensure_shadow_exists(self):
        """Ensure shadow exists by creating it if necessary"""
        print(f"\n🔍 {get_message('checking_shadow_exists').format(self.thing_name)}")

        # Try to get the shadow first
        shadow_exists = False

        try:
            # Send get request and wait for response
            self.get_shadow_document(debug=self.debug_mode, wait_for_response=True)

            # Wait a moment for the response
            time.sleep(2)  # nosemgrep: arbitrary-sleep

            # Check if we got a successful response
            if hasattr(self, "last_shadow_response") and self.last_shadow_response:
                if "error_code" not in self.last_shadow_response or self.last_shadow_response.get("error_code") != 404:
                    shadow_exists = True

        except Exception as e:
            print(f"⚠️ Error checking shadow existence: {str(e)}")

        if not shadow_exists:
            print(f"📝 {get_message('creating_initial_shadow')}")
            print(f"💡 {get_message('shadow_creation_normal')}")

            # Report current local state to create the shadow
            try:
                # Load local state and report it to create the shadow
                local_state = self.load_local_state()
                if local_state:
                    self.update_shadow_reported(local_state, debug=self.debug_mode)
                else:
                    # Create a basic initial state if no local state exists
                    initial_state = {
                        "temperature": 22.5,
                        "humidity": 45.0,
                        "status": "online",
                        "firmware_version": "1.0.0",
                    }
                    self.update_shadow_reported(initial_state, debug=self.debug_mode)
                print(f"✅ {get_message('initial_shadow_created')}")

                # Wait a moment for the shadow to be created
                time.sleep(3)  # nosemgrep: arbitrary-sleep

                # Now get the shadow to confirm it exists
                print(f"🔄 {get_message('retrieving_new_shadow')}")
                self.get_shadow_document(debug=self.debug_mode)

            except Exception as e:
                print(f"❌ Error creating initial shadow: {str(e)}")
        else:
            print(f"✅ {get_message('shadow_already_exists')}")

    def update_shadow_desired_interactive(self):
        """Interactive desired state update"""
        print(f"\n{get_message('updating_shadow_desired')}")

        property_name = input(get_message("enter_property_name")).strip()
        if not property_name:
            print(get_message("property_name_required"))
            return

        property_value = input(get_message("enter_property_value")).strip()
        if not property_value:
            print(get_message("property_value_required"))
            return

        # Try to convert to appropriate type
        try:
            if property_value.lower() in ["true", "false"]:
                property_value = property_value.lower() == "true"
            elif property_value.isdigit():
                property_value = int(property_value)
            elif "." in property_value and property_value.replace(".", "").isdigit():
                property_value = float(property_value)
        except (ValueError, TypeError):
            pass  # Keep as string

        desired_state = {property_name: property_value}

        print(f"\n{get_message('desired_state_to_set')}:")
        print(f"   {get_message('property')}: {property_name}")
        print(f"   {get_message('value')}: {property_value}")

        self.update_shadow_desired(desired_state, debug=self.debug_mode)

    def simulate_device_state_changes(self):
        """Simulate device state changes"""
        print(f"\n{get_message('simulating_device_changes')}")
        print(f"\n{get_message('simulation_options')}")

        options = [
            get_message("temperature_change"),
            get_message("humidity_change"),
            get_message("status_toggle"),
            get_message("firmware_update"),
            get_message("custom_property"),
        ]

        for option in options:
            print(f"   {option}")

        while True:
            try:
                choice = int(input(f"\n{get_message('select_simulation')}"))
                if 1 <= choice <= 5:
                    break
                else:
                    print(get_message("invalid_simulation"))
            except ValueError:
                print(get_message("enter_valid_number"))
            except KeyboardInterrupt:
                print(f"\n{get_message('operation_cancelled')}")
                return

        local_state = self.load_local_state()
        old_state = local_state.copy()

        if choice == 1:  # Temperature change
            import random

            old_temp = local_state.get("temperature", 22.5)
            new_temp = round(old_temp + random.uniform(-5, 5), 1)
            local_state["temperature"] = new_temp
            print(get_message("temperature_changed").format(old_temp, new_temp))

        elif choice == 2:  # Humidity change
            import random

            old_humidity = local_state.get("humidity", 45.0)
            new_humidity = round(max(0, min(100, old_humidity + random.uniform(-10, 10))), 1)
            local_state["humidity"] = new_humidity
            print(get_message("humidity_changed").format(old_humidity, new_humidity))

        elif choice == 3:  # Status toggle
            old_status = local_state.get("status", "online")
            new_status = "offline" if old_status == "online" else "online"
            local_state["status"] = new_status
            print(get_message("status_changed").format(old_status, new_status))

        elif choice == 4:  # Firmware update
            old_version = local_state.get("firmware_version", "1.0.0")
            version_parts = old_version.split(".")
            if len(version_parts) >= 3:
                patch = int(version_parts[2]) + 1
                new_version = f"{version_parts[0]}.{version_parts[1]}.{patch}"
            else:
                new_version = "1.0.1"
            local_state["firmware_version"] = new_version
            print(get_message("firmware_updated").format(old_version, new_version))

        elif choice == 5:  # Custom property
            prop_name = input(get_message("enter_property_name")).strip()
            if not prop_name:
                print(get_message("property_name_required"))
                return

            prop_value = input(get_message("enter_property_value")).strip()
            if not prop_value:
                print(get_message("property_value_required"))
                return

            old_value = local_state.get(prop_name, "None")
            local_state[prop_name] = prop_value
            print(get_message("custom_property_changed").format(prop_name, old_value, prop_value))

        # Show summary
        print(f"\n{get_message('state_change_summary')}")
        for key in local_state:
            if key in old_state and old_state[key] != local_state[key]:
                print(f"   • {key}: {old_state[key]} → {local_state[key]}")

        # Save and report
        if self.save_local_state(local_state):
            print(get_message("local_state_updated_sim"))
            print(get_message("reporting_to_shadow"))
            self.update_shadow_reported(local_state, debug=self.debug_mode)
            print(get_message("simulation_complete"))

    def view_shadow_message_history(self):
        """View shadow message history"""
        print(f"\n{get_message('viewing_message_history')}")

        with self.message_lock:
            if not self.received_messages:
                print(get_message("no_messages_received"))
                print(get_message("try_other_operations"))
                return

            print(f"\n{get_message('message_history').format(len(self.received_messages))}")

            for i, msg in enumerate(self.received_messages[-10:], 1):  # Show last 10
                timestamp = msg.get("Timestamp", "").split("T")[1][:8] if "T" in msg.get("Timestamp", "") else "Unknown"
                topic = msg.get("Topic", "Unknown")
                topic_type = topic.split("/")[-1] if "/" in topic else topic

                print(f"\n   {i}. [{timestamp}] {topic_type}")
                print(f"      {get_message('topic')}: {topic}")
                print(f"      {get_message('direction')}: {msg.get('Direction', 'Unknown')}")

                if msg.get("Shadow Data"):
                    shadow_data = str(msg["Shadow Data"])
                    if len(shadow_data) > 100:
                        shadow_data = shadow_data[:100] + "..."
                    print(f"      {get_message('shadow_data')}: {shadow_data}")

        # Ask if user wants to clear history
        clear_choice = input(f"\n{get_message('clear_history_prompt')}").strip().lower()
        if clear_choice == "y":
            with self.message_lock:
                self.received_messages.clear()
            print(get_message("history_cleared"))
        else:
            print(get_message("history_not_cleared"))

    def disconnect_and_summarize(self, start_time):
        """Disconnect and show session summary"""
        print(f"\n{get_message('disconnecting_from_iot')}")

        if self.connection and self.connected:
            try:
                disconnect_future = self.connection.disconnect()
                disconnect_future.result()
                self.connected = False
            except Exception as e:
                print(f"❌ Error during disconnect: {str(e)}")

        print(get_message("disconnection_complete"))

        # Show session summary
        duration = int(time.time() - start_time)
        minutes = duration // 60
        seconds = duration % 60

        print(f"\n{get_message('session_summary')}")
        print(f"   {get_message('total_messages')}: {len(self.received_messages)}")
        print(f"   {get_message('connection_duration')}: {minutes}m {seconds}s")
        print(f"   {get_message('shadow_operations')}: Multiple")

        print(f"\n{get_message('thank_you_message')}")
        print(f"\n{get_message('next_steps_suggestions')}")
        for suggestion in [
            get_message("explore_iot_rules"),
            get_message("try_mqtt_client"),
            get_message("check_registry"),
        ]:
            print(f"   {suggestion}")

    def interactive_shadow_management(self):
        """Interactive shadow management interface"""
        self.print_step(3, get_message("step_simulating_changes"))

        print(f"💡 {get_message('shadow_concepts')[0].replace('•', '').strip()}:")
        print(f"   • {get_message('desired_state')} represents what the device should be")
        print(f"   • {get_message('reported_state')} represents what the device currently is")
        print(
            f"   • {get_message('topic_update_delta').replace('• update/delta - ', '').replace(' (action needed)', '')} occur when desired ≠ reported"
        )
        print("   • Local file simulates actual device state")

        # Initial shadow get
        print("\n🔄 Getting initial shadow state...")
        self.get_shadow_document(debug=self.debug_mode)

        # Interactive loop
        print("\n🎮 Interactive Shadow Management Mode")
        print("💡 Shadow messages will appear immediately when received!")

        print("\nCommands:")
        print("   • 'get' - Request current shadow document")
        print("   • 'local' - Show current local device state")
        print("   • 'edit' - Edit local device state")
        print("   • 'report' - Report current local state to shadow")
        print("   • 'desire <key=value> [key=value...]' - Set desired state (simulate cloud)")
        print("   • 'status' - Show connection and shadow status")
        print("   • 'messages' - Show shadow message history")
        print("   • 'debug' - Show connection diagnostics")
        print("   • 'help' - Show this help")
        print("   • 'quit' - Exit")
        print("\n" + "=" * 60)

        while True:
            try:
                command = input(f"\n{get_message('shadow_command_prompt')}").strip()

                if not command:
                    continue

                parts = command.split(" ", 1)
                cmd = parts[0].lower()

                if cmd == "quit":
                    break

                elif cmd == "help":
                    print(f"\n{get_message('available_commands')}")
                    print(get_message("get_command"))
                    print(get_message("local_command"))
                    print(get_message("edit_command"))
                    print(get_message("report_command"))
                    print(get_message("desire_command"))
                    print(get_message("status_command"))
                    print(get_message("messages_command"))
                    print(get_message("debug_command"))
                    print(get_message("quit_command"))
                    print(f"\n{get_message('example_desire')}")

                elif cmd == "get":
                    print("\n📚 LEARNING MOMENT: Shadow Document Retrieval")
                    print(
                        "Getting the shadow document retrieves the complete JSON state including desired, reported, and metadata. This shows the current synchronization status between your application's intentions (desired) and the device's actual state (reported). The version number helps track changes."
                    )
                    print("\n🔄 NEXT: Retrieving the current shadow document...")
                    time.sleep(1)  # Brief pause instead of blocking input  # nosemgrep: arbitrary-sleep

                    self.get_shadow_document(debug=self.debug_mode)
                    time.sleep(0.5)  # nosemgrep: arbitrary-sleep

                elif cmd == "local":
                    local_state = self.load_local_state()
                    print(f"\n{get_message('current_local_device_state')}")
                    print(f"{json.dumps(local_state, indent=2)}")

                elif cmd == "edit":
                    self.edit_local_state()

                elif cmd == "report":
                    print("\n📚 LEARNING MOMENT: Device State Reporting")
                    print(
                        "Reporting state updates the shadow's 'reported' section with the device's current status. This is how devices communicate their actual state to applications. The shadow service automatically calculates deltas when reported state differs from desired state."
                    )
                    print("\n🔄 NEXT: Reporting local device state to the shadow...")
                    time.sleep(1)  # Brief pause instead of blocking input  # nosemgrep: arbitrary-sleep

                    local_state = self.load_local_state()
                    print("\n📡 Reporting local state to shadow...")
                    self.update_shadow_reported(local_state, debug=self.debug_mode)
                    time.sleep(0.5)  # nosemgrep: arbitrary-sleep

                elif cmd == "desire":
                    if len(parts) < 2:
                        print(f"   {get_message('usage_desire')}")
                        print(f"   {get_message('example_desire_usage')}")
                    else:
                        print("\n📚 LEARNING MOMENT: Desired State Management")
                        print(
                            "Setting desired state simulates how applications or cloud services request changes to device configuration. The shadow service stores these requests and notifies devices through delta messages when desired state differs from reported state. This enables remote device control."
                        )
                        print("\n🔄 NEXT: Setting desired state to trigger device changes...")
                        time.sleep(1)  # Brief pause instead of blocking input  # nosemgrep: arbitrary-sleep

                    # Parse key=value pairs
                    desired_updates = {}
                    for pair in parts[1].split():
                        if "=" in pair:
                            key, value = pair.split("=", 1)
                            # Try to convert to appropriate type
                            try:
                                if value.lower() in ["true", "false"]:
                                    desired_updates[key] = value.lower() == "true"
                                elif value.isdigit():
                                    desired_updates[key] = int(value)
                                elif "." in value and value.replace(".", "").isdigit():
                                    desired_updates[key] = float(value)
                                else:
                                    desired_updates[key] = value
                            except (ValueError, TypeError):
                                desired_updates[key] = value

                    if desired_updates:
                        print(get_message("setting_desired_state").format(json.dumps(desired_updates, indent=2)))
                        self.update_shadow_desired(desired_updates, debug=self.debug_mode)
                        time.sleep(0.5)  # nosemgrep: arbitrary-sleep
                    else:
                        print(f"   {get_message('no_valid_pairs')}")

                elif cmd == "status":
                    print(f"\n{get_message('shadow_connection_status')}")
                    print(f"   {get_message('connected')}: {get_message('yes') if self.connected else get_message('no')}")
                    print(f"   {get_message('thing_name')}: {self.thing_name}")
                    print(f"   {get_message('shadow_type')}: {get_message('shadow_type_classic')}")
                    print(f"   Local State File: {self.local_state_file}")
                    print(f"   Messages Received: {len(self.received_messages)}")

                elif cmd == "messages":
                    print(f"\n{get_message('shadow_message_history')}")
                    with self.message_lock:
                        for msg in self.received_messages[-10:]:  # Show last 10 messages
                            timestamp = msg["Timestamp"].split("T")[1][:8]
                            topic_type = msg["Topic"].split("/")[-1]
                            print(f"   📥 [{timestamp}] {topic_type}")
                            if msg.get("Shadow Data"):
                                shadow_summary = str(msg["Shadow Data"])[:100]
                                print(f"      {shadow_summary}{'...' if len(str(msg['Shadow Data'])) > 100 else ''}")

                elif cmd == "debug":
                    self.show_shadow_diagnostics()

                else:
                    print(get_message("unknown_command").format(cmd))

            except KeyboardInterrupt:
                print("\n\n🛑 Interrupted by user")
                break
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")

    def edit_local_state(self):
        """Interactive local state editor"""
        local_state = self.load_local_state()

        print(f"\n{get_message('edit_local_state_title')}")
        print(f"{get_message('current_state')} {json.dumps(local_state, indent=2)}")
        print(f"\n{get_message('options')}")
        print(get_message("edit_individual_values"))
        print(get_message("replace_entire_state"))
        print(get_message("cancel"))

        while True:
            choice = input(f"\n{get_message('select_option_1_3')}").strip()

            if choice == "1":
                # Edit individual values
                print(f"\n{get_message('current_values')}")
                keys = list(local_state.keys())
                for i, key in enumerate(keys, 1):
                    print(f"   {i}. {key}: {local_state[key]}")

                print(f"   {len(keys) + 1}. {get_message('add_new_key')}")
                print(f"   {len(keys) + 2}. {get_message('done_editing')}")

                while True:
                    try:
                        edit_choice = int(input(f"\n{get_message('select_item_to_edit').format(len(keys) + 2)}"))

                        if 1 <= edit_choice <= len(keys):
                            # Edit existing key
                            key = keys[edit_choice - 1]
                            current_value = local_state[key]
                            print(f"\n{get_message('editing_key').format(key, current_value)}")
                            new_value = input(get_message("new_value_prompt")).strip()

                            if new_value:
                                # Try to convert to appropriate type
                                try:
                                    if new_value.lower() in ["true", "false"]:
                                        local_state[key] = new_value.lower() == "true"
                                    elif new_value.isdigit():
                                        local_state[key] = int(new_value)
                                    elif "." in new_value and new_value.replace(".", "").isdigit():
                                        local_state[key] = float(new_value)
                                    else:
                                        local_state[key] = new_value
                                    print(get_message("updated_key").format(key, local_state[key]))
                                except (ValueError, TypeError):
                                    local_state[key] = new_value
                                    print(get_message("updated_key").format(key, local_state[key]))

                        elif edit_choice == len(keys) + 1:
                            # Add new key
                            new_key = input(get_message("new_key_name")).strip()
                            if new_key:
                                new_value = input(get_message("value_for_key").format(new_key)).strip()
                                # Try to convert to appropriate type
                                try:
                                    if new_value.lower() in ["true", "false"]:
                                        local_state[new_key] = new_value.lower() == "true"
                                    elif new_value.isdigit():
                                        local_state[new_key] = int(new_value)
                                    elif "." in new_value and new_value.replace(".", "").isdigit():
                                        local_state[new_key] = float(new_value)
                                    else:
                                        local_state[new_key] = new_value
                                    print(get_message("added_new_key").format(new_key, local_state[new_key]))
                                    keys.append(new_key)  # Update keys list
                                except (ValueError, TypeError):
                                    local_state[new_key] = new_value
                                    print(get_message("added_new_key").format(new_key, local_state[new_key]))
                                    keys.append(new_key)

                        elif edit_choice == len(keys) + 2:
                            # Done editing
                            break

                        else:
                            print(get_message("invalid_selection_cert"))

                    except ValueError:
                        print(get_message("enter_valid_number"))

                break

            elif choice == "2":
                # Replace with JSON
                print(f"\n{get_message('enter_json_prompt')}")
                json_lines = []
                while True:
                    line = input()
                    if line == "" and json_lines and json_lines[-1] == "":
                        break
                    json_lines.append(line)

                try:
                    json_text = "\n".join(json_lines[:-1])  # Remove last empty line
                    new_state = json.loads(json_text)
                    local_state = new_state
                    print(get_message("state_updated_from_json"))
                    break
                except json.JSONDecodeError as e:
                    print(get_message("invalid_json").format(str(e)))
                    continue

            elif choice == "3":
                print(f"❌ {get_message('operation_cancelled')}")
                return

            else:
                print(get_message("invalid_choice"))

        # Save updated state
        if self.save_local_state(local_state):
            print(f"\n{get_message('local_state_updated_sim')}")
            print(f"📊 {get_message('current_state')} {json.dumps(local_state, indent=2)}")

            # Ask if user wants to report to shadow
            report = input(f"\n{get_message('report_updated_state')}").strip().lower()
            if report == "y":
                self.update_shadow_reported(local_state, debug=self.debug_mode)
        else:
            print(get_message("failed_update_local"))

    def show_shadow_diagnostics(self):
        """Show detailed shadow connection and state diagnostics"""
        print("\n🔍 Shadow Connection Diagnostics")
        print("=" * 60)

        print("📡 Connection Status:")
        print(f"   • Connected: {'✅ Yes' if self.connected else '❌ No'}")
        print(f"   • Thing Name: {self.thing_name}")
        print("   • Shadow Type: Classic Shadow")
        print(f"   • Messages Received: {len(self.received_messages)}")

        if self.local_state_file:
            print("\n📱 Local Device State:")
            print(f"   • State File: {self.local_state_file}")
            print(f"   • File Exists: {'✅ Yes' if os.path.exists(self.local_state_file) else '❌ No'}")

            if os.path.exists(self.local_state_file):
                try:
                    local_state = self.load_local_state()
                    print(f"   • Current State: {json.dumps(local_state, indent=6)}")
                except Exception as e:
                    print(f"   • Error reading state: {str(e)}")

        print("\n🌟 Shadow Topics:")
        shadow_topics = [
            f"$aws/things/{self.thing_name}/shadow/get",
            f"$aws/things/{self.thing_name}/shadow/get/accepted",
            f"$aws/things/{self.thing_name}/shadow/get/rejected",
            f"$aws/things/{self.thing_name}/shadow/update",
            f"$aws/things/{self.thing_name}/shadow/update/accepted",
            f"$aws/things/{self.thing_name}/shadow/update/rejected",
            f"$aws/things/{self.thing_name}/shadow/update/delta",
        ]

        for topic in shadow_topics:
            if "get" in topic and topic.endswith("/get"):
                print(f"   📤 {topic} (publish to request shadow)")
            elif "update" in topic and topic.endswith("/update"):
                print(f"   📤 {topic} (publish to update shadow)")
            else:
                print(f"   📥 {topic} (subscribed)")

        print("\n🔧 Troubleshooting:")
        print("1. Verify certificate is ACTIVE and attached to Thing")
        print("2. Check policy allows shadow operations (iot:GetThingShadow, iot:UpdateThingShadow)")
        print("3. Ensure Thing name matches exactly")
        print("4. Check AWS IoT logs in CloudWatch (if enabled)")

    def disconnect(self):
        """Disconnect from AWS IoT Core"""
        if self.connection and self.connected:
            print(f"\n{get_message('disconnecting_from_iot')}")

            try:
                disconnect_future = self.connection.disconnect()
                disconnect_future.result()

                self.print_shadow_details(
                    "SHADOW DISCONNECTION",
                    {
                        get_message("status"): get_message("disconnection_complete"),
                        get_message("thing_name"): self.thing_name,
                        get_message("total_messages"): len(self.received_messages),
                        "Session Duration": "Connection closed cleanly",
                    },
                )

            except Exception as e:
                print(f"   ❌ Error during disconnect: {str(e)}")

            self.connected = False


def main():
    global USER_LANG, DEBUG_MODE, messages

    try:
        # Initialize language support
        USER_LANG = get_language()
        messages = load_messages("device_shadow_explorer", USER_LANG)

        # Check for debug flag
        debug_mode = "--debug" in sys.argv or "-d" in sys.argv
        DEBUG_MODE = debug_mode

        print(get_message("title"))
        print(get_message("separator"))

        # Display AWS context first
        display_aws_context()

        print(get_message("description_intro"))
        for concept in get_message("shadow_concepts"):
            print(concept)

        # Show learning moment
        print_learning_moment("shadow_foundation")

        if debug_mode:
            print(f"\n{get_message('debug_enabled')}")
            for feature in get_message("debug_features"):
                print(feature)
        else:
            print(f"\n{get_message('tip')}")

        print(get_message("separator"))

        explorer = DeviceShadowExplorer()
        explorer.debug_mode = debug_mode

        try:
            # Auto-connect and go into interactive mode
            explorer.run_auto_connect_and_interactive()

        except KeyboardInterrupt:
            print(f"\n\n{get_message('operation_cancelled')}")
        except (ConnectionError, TimeoutError) as e:
            print(f"\n❌ Connection error: {str(e)}")
            if debug_mode:
                import traceback

                traceback.print_exc()
        except (FileNotFoundError, PermissionError) as e:
            print(f"\n❌ File access error: {str(e)}")
            if debug_mode:
                import traceback

                traceback.print_exc()
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            print(f"\n❌ Data format error: {str(e)}")
            if debug_mode:
                import traceback

                traceback.print_exc()
        except Exception as e:
            print(f"\n❌ Unexpected error: {str(e)}")
            if debug_mode:
                import traceback

                traceback.print_exc()
        finally:
            # Always disconnect cleanly
            explorer.disconnect()
            print(f"\n{get_message('thank_you_message')}")

    except KeyboardInterrupt:
        print(f"\n\n{get_message('operation_cancelled')}")
        print(get_message("goodbye"))


if __name__ == "__main__":
    main()
