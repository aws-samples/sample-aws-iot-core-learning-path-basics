#!/usr/bin/env python3
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

"""
AWS IoT MQTT over WebSocket Explorer
Educational MQTT client using WebSocket connection with SigV4 authentication.
"""
import json
import os
import sys
import threading
import traceback
import uuid
from datetime import datetime

# Add i18n to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "i18n"))

import boto3
from awscrt import auth, mqtt
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


class MQTTWebSocketExplorer:
    def __init__(self):
        self.connection = None
        self.connected = False
        self.received_messages = []
        self.sent_messages = []
        self.subscriptions = {}
        self.message_lock = threading.Lock()
        self.message_count = 0
        self.debug_mode = False

    def get_iot_endpoint(self, debug=False):
        """Get AWS IoT endpoint for WebSocket connections"""
        try:
            iot = boto3.client("iot")

            if debug:
                print(get_message("debug_calling_api"))
                print(f"📥 {get_message('debug_input_params')}: {{'endpointType': 'iot:Data-ATS'}}")

            response = iot.describe_endpoint(endpointType="iot:Data-ATS")
            endpoint = response["endpointAddress"]

            if debug:
                print(f"📤 {get_message('debug_api_response')}: {json.dumps(response, indent=2, default=str)}")

            print(get_message("websocket_endpoint_discovery"))
            print(f"   {get_message('endpoint_type')}")
            print(f"   {get_message('endpoint_url')}: {endpoint}")
            print(f"   {get_message('port')}")
            print(f"   {get_message('protocol')}")

            return endpoint
        except Exception as e:
            print(f"{get_message('error_getting_endpoint')} {str(e)}")
            if debug:
                print(get_message("debug_full_traceback"))
                traceback.print_exc()
            return None

    def get_aws_credentials(self, debug=False):
        """Get AWS credentials for SigV4 authentication"""
        try:
            session = boto3.Session()
            credentials = session.get_credentials()

            if not credentials:
                print(get_message("no_aws_credentials"))
                print(get_message("credentials_help"))
                for method in get_message("credentials_methods"):
                    print(f"   {method}")
                return None, None, None, None

            access_key = credentials.access_key
            secret_key = credentials.secret_key
            session_token = credentials.token
            region = session.region_name or os.getenv("AWS_DEFAULT_REGION", "us-east-1")

            if debug:
                print("🔍 DEBUG: AWS Credentials Retrieved")
                print(f"   Access Key: {access_key[:10]}..." if access_key else "   Access Key: None")
                print(f"   Secret Key: {'*' * 20}" if secret_key else "   Secret Key: None")
                print(f"   Session Token: {'Present' if session_token else 'None'}")
                print(f"   Region: {region}")

            print(get_message("aws_credentials_sigv4"))
            print(
                f"   {get_message('access_key')}: {access_key[:10]}..."
                if access_key
                else f"   {get_message('access_key')}: None"
            )
            print(f"   {get_message('region')}: {region}")
            print(
                f"   {get_message('session_token')}: {get_message('present') if session_token else get_message('not_present')}"
            )

            return access_key, secret_key, session_token, region

        except Exception as e:
            print(f"{get_message('error_getting_credentials')} {str(e)}")
            if debug:
                print(get_message("debug_full_traceback"))
                traceback.print_exc()
            return None, None, None, None

    def get_client_id(self):
        """Get client ID from user input or generate automatically"""
        print(f"\n{get_message('client_id_guidelines')}")
        for rule in get_message("client_id_rules"):
            print(f"   {rule}")

        while True:
            try:
                custom_id = input(f"\n{get_message('client_id_prompt')}").strip()

                if not custom_id:
                    client_id = f"websocket-client-{uuid.uuid4().hex[:8]}"
                    print(f"   {get_message('client_id_auto_generated')}: {client_id}")
                    return client_id
                else:
                    if self.validate_client_id(custom_id):
                        print(f"   {get_message('client_id_custom')}: {custom_id}")
                        return custom_id
                    else:
                        print(f"   {get_message('client_id_invalid')}")
                        continue

            except KeyboardInterrupt:
                print(f"\n{get_message('operation_cancelled')}")
                return None

    def validate_client_id(self, client_id):
        """Validate MQTT Client ID according to AWS IoT requirements"""
        if not client_id or len(client_id) < 1 or len(client_id) > 128:
            return False
        import re

        return bool(re.match(r"^[a-zA-Z0-9_-]+$", client_id))

    def select_mqtt_version(self):
        """Allow user to select MQTT version"""
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

    def connect_to_aws_iot_websocket(
        self,
        client_id,
        access_key,
        secret_key,
        session_token,
        region,
        endpoint,
        mqtt_version="3.1.1",
        debug=False,
    ):
        """Establish MQTT over WebSocket connection to AWS IoT Core using SigV4"""
        print(f"\n🔧 Step 1: {get_message('establishing_connection')}")
        print("-" * 50)

        try:
            print(get_message("websocket_connection_params"))
            print(f"   {get_message('client_id')}: {client_id}")
            print(f"   {get_message('endpoint')}: {endpoint}")
            print(f"   {get_message('port_443')}")
            print(f"   {get_message('protocol_label')}: MQTT {mqtt_version} over WebSocket")
            print(f"   {get_message('authentication')}")
            print(f"   {get_message('region')}: {region}")

            credentials_provider = auth.AwsCredentialsProvider.new_static(
                access_key_id=access_key,
                secret_access_key=secret_key,
                session_token=session_token,
            )

            # Build MQTT connection using appropriate WebSocket builder
            if mqtt_version == "5.0" and MQTT5_AVAILABLE:
                try:
                    self.connection = mqtt5_connection_builder.websockets_with_default_aws_signing(
                        endpoint=endpoint,
                        region=region,
                        credentials_provider=credentials_provider,
                        client_id=client_id,
                        clean_session=True,
                        keep_alive_secs=30,
                        on_connection_interrupted=self.on_connection_interrupted,
                        on_connection_resumed=self.on_connection_resumed,
                    )
                except Exception as mqtt5_error:
                    print(f"⚠️  MQTT 5.0 WebSocket connection failed: {str(mqtt5_error)}")
                    print(f"🔄 {get_message('falling_back_mqtt311')}")
                    mqtt_version = "3.1.1"

            if mqtt_version == "3.1.1" or not MQTT5_AVAILABLE:
                self.connection = mqtt_connection_builder.websockets_with_default_aws_signing(
                    endpoint=endpoint,
                    region=region,
                    credentials_provider=credentials_provider,
                    client_id=client_id,
                    clean_session=True,
                    keep_alive_secs=30,
                    on_connection_interrupted=self.on_connection_interrupted,
                    on_connection_resumed=self.on_connection_resumed,
                )

            print(f"\n{get_message('connecting_websocket')}")
            connect_future = self.connection.connect()
            connect_future.result()

            self.connected = True

            print(f"\n📊 {get_message('websocket_connection_established')} [{datetime.now().strftime('%H:%M:%S')}]")
            print("-" * 40)
            print(f"   {get_message('connection_status')}")
            print(f"   {get_message('client_id')}: {client_id}")
            print(f"   {get_message('endpoint')}: {endpoint}")
            print(f"   Transport: MQTT {mqtt_version} over WebSocket (port 443)")
            print("   Authentication: AWS SigV4")
            print(f"   {get_message('region')}: {region}")
            print(f"   {get_message('mqtt_version_label')}: {mqtt_version}")

            return True

        except Exception as e:
            print(f"{get_message('websocket_connection_failed')} {str(e)}")
            if debug:
                traceback.print_exc()
            return False

    def on_connection_interrupted(self, connection, error, **kwargs):
        """Callback for connection interruption"""
        print(f"\n{get_message('connection_interrupted')}")
        print(f"   {get_message('error')}: {str(error)}")
        print(f"   {get_message('timestamp')}: {datetime.now().isoformat()}")
        print(f"   {get_message('auto_reconnect')}")
        self.connected = False

    def on_connection_resumed(self, connection, return_code, session_present, **kwargs):
        """Callback for connection resumption"""
        print(f"\n{get_message('connection_resumed')}")
        print(f"   {get_message('return_code')}: {return_code}")
        print(f"   {get_message('session_present')}: {session_present}")
        print(f"   {get_message('status')}")
        self.connected = True

    def on_message_received(self, topic, payload, dup, qos, retain, **kwargs):
        """Callback for received messages"""
        try:
            try:
                message_data = json.loads(payload.decode("utf-8"))
                payload_display = json.dumps(message_data, indent=2)
                is_json = True
            except (json.JSONDecodeError, UnicodeDecodeError):
                payload_display = payload.decode("utf-8")
                is_json = False

            with self.message_lock:
                self.message_count += 1

            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            print("\n" + "=" * 70)
            print(f"{get_message('incoming_message', self.message_count, timestamp)}")
            print("=" * 70)

            print(f"{get_message('topic')}: {topic}")
            qos_desc = get_message("qos_descriptions").get(qos, f"QoS {qos}")
            print(f"{get_message('qos')}: {qos} ({qos_desc})")
            print(f"{get_message('payload_size')}: {len(payload)} {get_message('bytes')}")
            print(get_message("transport"))

            print(get_message("message_payload"))
            if is_json:
                print(f"   {get_message('json_format')}")
                for line in payload_display.split("\n"):
                    print(f"   {line}")
            else:
                print(f"   {get_message('text_format')} {payload_display}")

            print("=" * 70)

        except Exception as e:
            print(f"\n{get_message('error_processing_message')} {str(e)}")

    def interactive_messaging(self):
        """Interactive messaging interface for WebSocket MQTT"""
        print(f"\n🔧 Step 2: {get_message('interactive_messaging')}")
        print("-" * 50)

        print(get_message("mqtt_topic_guidelines"))
        for guideline in get_message("topic_guidelines"):
            print(f"   {guideline}")

        # Get subscription topic
        while True:
            sub_topic = input(f"\n{get_message('enter_subscribe_topic')}").strip()
            if sub_topic.lower() == "skip":
                sub_topic = None
                break
            elif sub_topic:
                while True:
                    qos_choice = input(f"   {get_message('qos_level_prompt')}").strip()
                    if qos_choice == "" or qos_choice == "0":
                        sub_qos = 0
                        break
                    elif qos_choice == "1":
                        sub_qos = 1
                        break
                    else:
                        print(f"   {get_message('invalid_qos')}")

                if self.subscribe_to_topic(sub_topic, sub_qos):
                    break
                else:
                    print(f"   {get_message('subscription_failed_retry')}")
            else:
                print(f"   {get_message('topic_cannot_be_empty')}")

        # Interactive messaging loop
        print(f"\n{get_message('interactive_websocket_mode')}")
        print(get_message("messages_appear_immediately"))

        print(f"\n{get_message('commands')}")
        for command in get_message("command_list"):
            print(f"   {command}")
        print("\n" + "=" * 60)

        while True:
            try:
                command = input(f"\n{get_message('mqtt_ws_prompt')}").strip()

                if not command:
                    continue

                parts = command.split(" ", 2)
                cmd = parts[0].lower()

                if cmd == "quit":
                    break
                elif cmd == "help":
                    print("\n📖 Available Commands:")
                    for command_help in get_message("command_list"):
                        print(f"   {command_help}")
                elif cmd == "status":
                    print(f"\n📊 {get_message('connection_status_label')}:")
                    print(f"   {get_message('connected')}: {'✅ Yes' if self.connected else '❌ No'}")
                    print("   Transport: WebSocket with SigV4")
                    print(f"   {get_message('subscriptions_count', len(self.subscriptions))}")
                elif cmd in ["sub", "sub1"]:
                    if len(parts) < 2:
                        print("   ❌ Usage: sub <topic>")
                        continue
                    topic = parts[1]
                    qos = 1 if cmd == "sub1" else 0
                    if self.subscribe_to_topic(topic, qos):
                        print(f"   ✅ Successfully subscribed to {topic} with QoS {qos}")
                elif cmd in ["pub", "pub1"]:
                    if len(parts) < 3:
                        print("   ❌ Usage: pub <topic> <message>")
                        continue
                    topic = parts[1]
                    message = " ".join(parts[2:]).strip("'\"")
                    qos = 1 if cmd == "pub1" else 0
                    self.publish_message(topic, message, qos)
                elif cmd == "json":
                    if len(parts) < 3:
                        print("   ❌ Usage: json <topic> key=val key2=val2...")
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
                    self.publish_message(topic, json_data, 0)
                elif cmd == "unsub":
                    if len(parts) < 2:
                        print("   ❌ Usage: unsub <topic>")
                        continue
                    topic = parts[1]
                    print(f"   ℹ️  Unsubscribe functionality not yet implemented for WebSocket")
                elif cmd == "test":
                    # Send a test message
                    test_topic = f"test/websocket/message"
                    test_message = {
                        "timestamp": datetime.now().isoformat(),
                        "message": "Hello from WebSocket MQTT Explorer!",
                        "transport": "WebSocket with SigV4",
                    }
                    self.publish_message(test_topic, test_message, 0)
                elif cmd == "messages":
                    print(f"\n📊 {get_message('message_history')}")
                    if self.received_messages:
                        for i, msg in enumerate(self.received_messages[-10:], 1):
                            print(f"   {i}. {msg}")
                    else:
                        print("   No messages received yet")
                elif cmd == "debug":
                    if len(parts) > 1:
                        topic = parts[1]
                        print(f"\n🔍 Debug info for topic: {topic}")
                        if topic in self.subscriptions:
                            print(f"   Subscription exists: {self.subscriptions[topic]}")
                        else:
                            print(f"   Not subscribed to {topic}")
                    else:
                        print(f"\n🔍 {get_message('connection_diagnostics')}")
                        print(f"   Connected: {self.connected}")
                        print(f"   Subscriptions: {len(self.subscriptions)}")
                        print(f"   Messages received: {len(self.received_messages)}")
                elif cmd == "clear":
                    print("\n" * 50)
                    print(get_message("clear_screen"))
                else:
                    print(f"   {get_message('invalid_command')}")

            except KeyboardInterrupt:
                print("\n\n🛑 Interrupted by user")
                break

    def subscribe_to_topic(self, topic, qos=0):
        """Subscribe to an MQTT topic over WebSocket"""
        if not self.connected:
            print(get_message("not_connected"))
            return False

        try:
            print(f"\n{get_message('subscribing_topic_websocket')}")
            print(f"   {get_message('topic')}: {topic}")
            qos_desc = get_message("qos_descriptions").get(qos, f"QoS {qos}")
            print(f"   QoS: {qos} ({qos_desc})")

            mqtt_qos = mqtt.QoS.AT_MOST_ONCE if qos == 0 else mqtt.QoS.AT_LEAST_ONCE
            subscribe_future, packet_id = self.connection.subscribe(
                topic=topic, qos=mqtt_qos, callback=self.on_message_received
            )
            subscribe_future.result()

            self.subscriptions[topic] = {
                "qos": qos,
                "packet_id": packet_id,
                "subscribed_at": datetime.now().isoformat(),
            }

            print(f"\n📊 {get_message('websocket_subscription_established')} [{datetime.now().strftime('%H:%M:%S')}]")
            print("-" * 40)
            print(f"   {get_message('topic')}: {topic}")
            print(f"   QoS: {qos}")
            print(f"   Packet ID: {packet_id}")
            print("   Transport: WebSocket with SigV4")

            return True

        except Exception as e:
            print(f"{get_message('websocket_subscription_failed')} {str(e)}")
            return False

    def publish_message(self, topic, message, qos=0):
        """Publish a message to an MQTT topic over WebSocket"""
        if not self.connected:
            print(get_message("not_connected"))
            return False

        try:
            if isinstance(message, dict):
                payload = json.dumps(message)
            else:
                payload = str(message)

            print(f"\n{get_message('publishing_message_websocket')}")
            print(f"   {get_message('topic')}: {topic}")
            print(f"   QoS: {qos}")
            print(f"   {get_message('payload_size')}: {len(payload)} {get_message('bytes')}")

            publish_future, packet_id = self.connection.publish(
                topic=topic,
                payload=payload,
                qos=mqtt.QoS.AT_MOST_ONCE if qos == 0 else mqtt.QoS.AT_LEAST_ONCE,
            )
            publish_future.result()

            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            print(f"{get_message('published_websocket', timestamp)}")

            return True

        except Exception as e:
            print(f"{get_message('websocket_publish_failed')} {str(e)}")
            return False

    def disconnect(self):
        """Disconnect from AWS IoT Core WebSocket"""
        if self.connection and self.connected:
            print("\n🔌 Disconnecting from AWS IoT Core WebSocket...")
            try:
                disconnect_future = self.connection.disconnect()
                disconnect_future.result()
                print("✅ Successfully disconnected")
            except Exception as e:
                print(f"❌ Error during disconnect: {str(e)}")
            self.connected = False


def main():
    global USER_LANG, messages, DEBUG_MODE

    try:
        USER_LANG = get_language()
        messages = load_messages("mqtt_websocket_explorer", USER_LANG)

        debug_mode = "--debug" in sys.argv or "-d" in sys.argv
        DEBUG_MODE = debug_mode

        print(get_message("title"))
        print(get_message("separator"))

        try:
            sts = boto3.client("sts")
            iot = boto3.client("iot")
            identity = sts.get_caller_identity()

            print("📍 AWS Configuration:")
            print(f"   Account ID: {identity['Account']}")
            print(f"   Region: {iot.meta.region_name}")
            print()

        except Exception as e:
            print(f"⚠️ Could not retrieve AWS context: {str(e)}")
            print("   Make sure AWS credentials are configured")
            print()

        print(get_message("description_intro"))

        if debug_mode:
            print(f"\n{get_message('debug_enabled')}")
            for feature in get_message("debug_features"):
                print(feature)
        else:
            print(f"\n{get_message('tip')}")

        print(get_message("separator"))

        client = MQTTWebSocketExplorer()
        client.debug_mode = debug_mode

        try:
            endpoint = client.get_iot_endpoint(debug=debug_mode)
            if not endpoint:
                return

            access_key, secret_key, session_token, region = client.get_aws_credentials(debug=debug_mode)
            if not access_key or not secret_key:
                return

            client_id = client.get_client_id()
            if not client_id:
                return

            mqtt_version = client.select_mqtt_version()
            if not mqtt_version:
                return

            if not client.connect_to_aws_iot_websocket(
                client_id,
                access_key,
                secret_key,
                session_token,
                region,
                endpoint,
                mqtt_version,
                debug=debug_mode,
            ):
                return

            client.interactive_messaging()

        except KeyboardInterrupt:
            print("\n\n🛑 Interrupted by user")
        except Exception as e:
            print(f"\n❌ Unexpected error: {str(e)}")
            if debug_mode:
                traceback.print_exc()
        finally:
            client.disconnect()
            print("\n👋 WebSocket MQTT Client Explorer session ended")

    except KeyboardInterrupt:
        print(f"\n\n{get_message('goodbye')}")


if __name__ == "__main__":
    main()
