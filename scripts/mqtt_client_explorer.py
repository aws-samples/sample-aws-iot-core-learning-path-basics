#!/usr/bin/env python3
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

"""
AWS IoT MQTT Client Explorer
Educational MQTT client for learning AWS IoT Core communication patterns.
"""
import boto3
import json
import os
import sys
import time
import threading
import subprocess
from datetime import datetime
from botocore.exceptions import ClientError
from awscrt import mqtt, io, auth, http
from awsiot import mqtt_connection_builder
import uuid

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

class MQTTClientExplorer:
    def __init__(self):
        self.connection = None
        self.connected = False
        self.received_messages = []
        self.sent_messages = []
        self.subscriptions = {}
        self.message_lock = threading.Lock()
        self.message_count = 0
        
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
    
    def get_iot_endpoint(self, debug=False):
        """Get AWS IoT endpoint for the account"""
        try:
            iot = boto3.client('iot')
            
            if debug:
                print(f"🔍 DEBUG: Calling describe_endpoint API")
                print(f"📥 Input Parameters: {{'endpointType': 'iot:Data-ATS'}}")
            
            response = iot.describe_endpoint(endpointType='iot:Data-ATS')
            endpoint = response['endpointAddress']
            
            if debug:
                print(f"📤 API Response: {json.dumps(response, indent=2, default=str)}")
            
            print(f"🌐 AWS IoT Endpoint Discovery")
            print(f"   Endpoint Type: iot:Data-ATS (recommended)")
            print(f"   Endpoint URL: {endpoint}")
            print(f"   Port: 8883 (MQTT over TLS)")
            print(f"   Protocol: MQTT 3.1.1 over TLS")
            
            return endpoint
        except Exception as e:
            print(f"❌ Error getting IoT endpoint: {str(e)}")
            if debug:
                import traceback
                print(f"🔍 DEBUG: Full traceback:")
                traceback.print_exc()
            return None
    
    def select_device_and_certificate(self, debug=False):
        """Select a device and its certificate for MQTT connection"""
        try:
            iot = boto3.client('iot')
            
            # Get all Things
            if debug:
                print(f"🔍 DEBUG: Calling list_things API")
                print(f"📥 Input Parameters: None")
            
            things_response = iot.list_things()
            things = things_response.get('things', [])
            
            if debug:
                print(f"📤 API Response: Found {len(things)} Things")
                print(f"📊 Thing Names: {[t['thingName'] for t in things]}")
            
            if not things:
                print("❌ No Things found. Please run setup_sample_data.py first")
                return None, None, None
            
            print(f"\n📱 Available Devices ({len(things)} found):")
            for i, thing in enumerate(things, 1):
                print(f"   {i}. {thing['thingName']} (Type: {thing.get('thingTypeName', 'None')})")
            
            while True:
                try:
                    choice = int(input(f"\nSelect device (1-{len(things)}): ")) - 1
                    if 0 <= choice < len(things):
                        selected_thing = things[choice]['thingName']
                        break
                    else:
                        print(f"❌ Invalid selection. Please enter 1-{len(things)}")
                except ValueError:
                    print("❌ Please enter a valid number")
                except KeyboardInterrupt:
                    print(f"\n🛑 Operation cancelled")
                    return None, None, None
            
            print(f"✅ Selected device: {selected_thing}")
            
            # Get certificates for the selected Thing
            if debug:
                print(f"🔍 DEBUG: Calling list_thing_principals API")
                print(f"📥 Input Parameters: {{'thingName': '{selected_thing}'}}")
            
            principals_response = iot.list_thing_principals(thingName=selected_thing)
            principals = principals_response.get('principals', [])
            cert_arns = [p for p in principals if 'cert/' in p]
            
            if debug:
                print(f"📤 API Response: Found {len(principals)} principals, {len(cert_arns)} certificates")
                print(f"📊 Certificate ARNs: {cert_arns}")
            
            if not cert_arns:
                print(f"❌ No certificates found for device '{selected_thing}'")
                print("💡 Run certificate_manager.py to create and attach a certificate")
                return None, None, None
            
            # Select certificate if multiple
            if len(cert_arns) == 1:
                selected_cert_arn = cert_arns[0]
                cert_id = selected_cert_arn.split('/')[-1]
                print(f"✅ Using certificate: {cert_id}")
            else:
                print(f"\n🔐 Multiple certificates found:")
                for i, cert_arn in enumerate(cert_arns, 1):
                    cert_id = cert_arn.split('/')[-1]
                    print(f"   {i}. {cert_id}")
                
                while True:
                    try:
                        choice = int(input(f"Select certificate (1-{len(cert_arns)}): ")) - 1
                        if 0 <= choice < len(cert_arns):
                            selected_cert_arn = cert_arns[choice]
                            cert_id = selected_cert_arn.split('/')[-1]
                            break
                        else:
                            print("❌ Invalid selection")
                    except ValueError:
                        print("❌ Please enter a valid number")
                    except KeyboardInterrupt:
                        print(f"\n🛑 Operation cancelled")
                        return None, None, None
            
            # Find certificate files
            cert_dir = os.path.join(os.getcwd(), 'certificates', selected_thing)
            if not os.path.exists(cert_dir):
                print(f"❌ Certificate directory not found: {cert_dir}")
                print("💡 Run certificate_manager.py to create certificate files")
                return None, None, None
            
            cert_file = None
            key_file = None
            
            for file in os.listdir(cert_dir):
                if cert_id in file:
                    if file.endswith('.crt'):
                        cert_file = os.path.join(cert_dir, file)
                    elif file.endswith('.key'):
                        key_file = os.path.join(cert_dir, file)
            
            if not cert_file or not key_file:
                print(f"❌ Certificate files not found in {cert_dir}")
                print(f"   Looking for: {cert_id}.crt and {cert_id}.key")
                return None, None, None
            
            print(f"✅ Certificate files found:")
            print(f"   Certificate: {cert_file}")
            print(f"   Private Key: {key_file}")
            
            return selected_thing, cert_file, key_file
            
        except Exception as e:
            print(f"❌ Error selecting device: {str(e)}")
            return None, None, None
    
    def on_connection_interrupted(self, connection, error, **kwargs):
        """Callback for connection interruption"""
        self.print_mqtt_details("CONNECTION INTERRUPTED", {
            "Error": str(error),
            "Timestamp": datetime.now().isoformat(),
            "Auto Reconnect": "AWS IoT SDK will attempt to reconnect automatically"
        })
        self.connected = False
    
    def on_connection_resumed(self, connection, return_code, session_present, **kwargs):
        """Callback for connection resumption"""
        self.print_mqtt_details("CONNECTION RESUMED", {
            "Return Code": return_code,
            "Session Present": session_present,
            "Timestamp": datetime.now().isoformat(),
            "Status": "Connection restored successfully"
        })
        self.connected = True
        
        # Re-subscribe to all topics if session not present
        if not session_present and self.subscriptions:
            print(f"\n🔄 Re-subscribing to {len(self.subscriptions)} topics after reconnection...")
            topics_to_resubscribe = list(self.subscriptions.items())
            for topic, qos in topics_to_resubscribe:
                try:
                    subscribe_future, _ = self.connection.subscribe(
                        topic=topic,
                        qos=mqtt.QoS(qos),
                        callback=self.on_message_received
                    )
                    subscribe_future.result()
                    print(f"   ✅ Re-subscribed to {topic} (QoS {qos})")
                except Exception as e:
                    print(f"   ❌ Failed to re-subscribe to {topic}: {str(e)}")
                    # Remove failed subscription from tracking
                    self.subscriptions.pop(topic, None)
    
    def on_message_received(self, topic, payload, dup, qos, retain, **kwargs):
        """Callback for received messages with comprehensive MQTT metadata"""
        try:
            # Try to parse as JSON, fallback to string
            try:
                message_data = json.loads(payload.decode('utf-8'))
                payload_display = json.dumps(message_data, indent=2)
                is_json = True
            except:
                payload_display = payload.decode('utf-8')
                is_json = False
            
            # Extract additional MQTT properties from kwargs
            user_properties = kwargs.get('user_properties', [])
            content_type = kwargs.get('content_type', None)
            correlation_data = kwargs.get('correlation_data', None)
            message_expiry_interval = kwargs.get('message_expiry_interval', None)
            response_topic = kwargs.get('response_topic', None)
            payload_format_indicator = kwargs.get('payload_format_indicator', None)
            
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
                "Payload Format": payload_format_indicator
            }
            
            with self.message_lock:
                self.received_messages.append(message_info)
                self.message_count += 1
            
            # Immediate visual notification with enhanced formatting
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            print(f"\n" + "="*70)
            print(f"🔔 INCOMING MESSAGE #{self.message_count} [{timestamp}]")
            print(f"="*70)
            
            # Core MQTT Properties
            print(f"📥 Topic: {topic}")
            print(f"🏷️  QoS: {qos} ({'At most once' if qos == 0 else 'At least once' if qos == 1 else 'Exactly once'})")
            print(f"📊 Payload Size: {len(payload)} bytes")
            
            # MQTT Flags
            flags = []
            if dup:
                flags.append("🔄 DUPLICATE (retransmitted)")
            if retain:
                flags.append("📌 RETAIN (stored by broker)")
            if flags:
                print(f"🚩 Flags: {', '.join(flags)}")
            
            # MQTT5 Properties (if available)
            mqtt5_props = []
            if content_type:
                mqtt5_props.append(f"📄 Content-Type: {content_type}")
            if correlation_data:
                mqtt5_props.append(f"🔗 Correlation-Data: {correlation_data}")
            if message_expiry_interval:
                mqtt5_props.append(f"⏰ Message-Expiry: {message_expiry_interval}s")
            if response_topic:
                mqtt5_props.append(f"↩️  Response-Topic: {response_topic}")
            if payload_format_indicator is not None:
                format_desc = "UTF-8 String" if payload_format_indicator == 1 else "Bytes"
                mqtt5_props.append(f"📝 Payload-Format: {format_desc}")
            if user_properties:
                mqtt5_props.append(f"🏷️  User-Properties: {len(user_properties)} properties")
                for prop in user_properties:
                    mqtt5_props.append(f"   • {prop[0]}: {prop[1]}")
            
            if mqtt5_props:
                print(f"🔧 MQTT5 Properties:")
                for prop in mqtt5_props:
                    print(f"   {prop}")
            
            # Payload Display
            print(f"💬 Message Payload:")
            if is_json:
                print(f"   📋 JSON Format:")
                for line in payload_display.split('\n'):
                    print(f"   {line}")
            else:
                print(f"   📝 Text: {payload_display}")
            
            print(f"="*70)
            print(f"📡 MQTT> ", end="", flush=True)  # Restore prompt
            
        except Exception as e:
            print(f"\n❌ Error processing received message: {str(e)}")
            print(f"📡 MQTT> ", end="", flush=True)
    
    def connect_to_aws_iot(self, thing_name, cert_file, key_file, endpoint, debug=False):
        """Establish MQTT connection to AWS IoT Core"""
        self.print_step(1, "Establishing MQTT Connection")
        
        if debug:
            print(f"🔍 DEBUG: MQTT Connection Setup")
            print(f"   Thing Name: {thing_name}")
            print(f"   Certificate File: {cert_file}")
            print(f"   Private Key File: {key_file}")
            print(f"   Endpoint: {endpoint}")
        
        try:
            # Create client ID
            client_id = f"{thing_name}-{uuid.uuid4().hex[:8]}"
            
            print(f"🔗 Connection Parameters:")
            print(f"   Client ID: {client_id}")
            print(f"   Endpoint: {endpoint}")
            print(f"   Port: 8883")
            print(f"   Protocol: MQTT 3.1.1 over TLS 1.2")
            print(f"   Authentication: X.509 Certificate")
            print(f"   Certificate File: {cert_file}")
            print(f"   Private Key File: {key_file}")
            
            # Build MQTT connection
            self.connection = mqtt_connection_builder.mtls_from_path(
                endpoint=endpoint,
                port=8883,
                cert_filepath=cert_file,
                pri_key_filepath=key_file,
                client_id=client_id,
                clean_session=True,  # Use clean session for better reliability
                keep_alive_secs=30,
                on_connection_interrupted=self.on_connection_interrupted,
                on_connection_resumed=self.on_connection_resumed
            )
            
            print(f"\n🔄 Connecting to AWS IoT Core...")
            connect_future = self.connection.connect()
            connection_result = connect_future.result()  # Wait for connection
            
            if debug:
                print(f"🔍 DEBUG: Connection result: {connection_result}")
            
            self.connected = True
            
            self.print_mqtt_details("CONNECTION ESTABLISHED", {
                "Status": "Successfully connected to AWS IoT Core",
                "Client ID": client_id,
                "Endpoint": endpoint,
                "Clean Session": False,
                "Keep Alive": "30 seconds",
                "TLS Version": "1.2",
                "Certificate Authentication": "X.509 mutual TLS"
            })
            
            # Test basic connectivity with a simple operation
            if debug:
                print(f"🔍 DEBUG: Testing MQTT connection stability...")
                try:
                    # Try a simple operation to verify the connection is fully functional
                    import time
                    time.sleep(1)  # nosemgrep: arbitrary-sleep
                    print(f"✅ Connection appears stable and ready for operations")
                except Exception as test_e:
                    print(f"⚠️  Connection established but may be unstable: {str(test_e)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Connection failed: {str(e)}")
            return False
    
    def subscribe_to_topic(self, topic, qos=0, debug=False):
        """Subscribe to an MQTT topic with enhanced error handling"""
        if not self.connected:
            print("❌ Not connected to AWS IoT Core")
            return False
        
        try:
            print(f"\n📥 Subscribing to Topic")
            print(f"   Topic: {topic}")
            print(f"   QoS: {qos} ({'At most once' if qos == 0 else 'At least once'})")
            
            if debug:
                print(f"🔍 DEBUG: MQTT Subscribe Operation")
                print(f"   Connection Status: {self.connected}")
                print(f"   Connection Object: {self.connection}")
                print(f"   Topic Pattern: {topic}")
                print(f"   Requested QoS: {qos}")
            
            # Convert QoS to proper enum
            mqtt_qos = mqtt.QoS.AT_MOST_ONCE if qos == 0 else mqtt.QoS.AT_LEAST_ONCE
            
            if debug:
                print(f"🔍 DEBUG: Converted QoS: {mqtt_qos}")
                print(f"🔍 DEBUG: Callback function: {self.on_message_received}")
            
            subscribe_future, packet_id = self.connection.subscribe(
                topic=topic,
                qos=mqtt_qos,
                callback=self.on_message_received
            )
            
            if debug:
                print(f"🔍 DEBUG: Subscribe request sent, waiting for response...")
                print(f"   Packet ID: {packet_id}")
            
            # Wait for subscription result
            subscribe_result = subscribe_future.result()
            
            if debug:
                print(f"🔍 DEBUG: Subscribe result received:")
                print(f"   Result: {subscribe_result}")
                print(f"   Result type: {type(subscribe_result)}")
            
            # Extract QoS from result - the result format may vary
            granted_qos = qos  # Default fallback
            if hasattr(subscribe_result, 'qos'):
                granted_qos = subscribe_result.qos
            elif isinstance(subscribe_result, dict) and 'qos' in subscribe_result:
                granted_qos = subscribe_result['qos']
            
            self.subscriptions[topic] = {
                'qos': qos,
                'granted_qos': granted_qos,
                'packet_id': packet_id,
                'subscribed_at': datetime.now().isoformat()
            }
            
            self.print_mqtt_details("SUBSCRIPTION ESTABLISHED", {
                "Topic": topic,
                "QoS Requested": qos,
                "QoS Granted": granted_qos,
                "Packet ID": packet_id,
                "Status": "Successfully subscribed",
                "Wildcard Support": "AWS IoT supports + (single level) and # (multi level)"
            })
            
            return True
            
        except Exception as e:
            print(f"❌ Subscription failed: {str(e)}")
            print(f"🔍 Detailed Error Information:")
            print(f"   Error Type: {type(e).__name__}")
            print(f"   Error Message: {str(e)}")
            
            # Check for common issues
            error_str = str(e).lower()
            if 'timeout' in error_str:
                print(f"💡 Troubleshooting: Subscription timeout")
                print(f"   • MQTT connection may be unstable")
                print(f"   • Network connectivity issues")
                print(f"   • AWS IoT endpoint may be unreachable")
            elif 'not authorized' in error_str or 'forbidden' in error_str or 'access denied' in error_str:
                print(f"💡 Troubleshooting: Authorization failed")
                print(f"   • Certificate may not be ACTIVE")
                print(f"   • Certificate may not be attached to Thing")
                print(f"   • Policy may not be attached to certificate")
            elif 'invalid topic' in error_str or 'malformed' in error_str:
                print(f"💡 Troubleshooting: Invalid topic format")
                print(f"   • Topics cannot start with '/' or '$' (unless AWS reserved)")
                print(f"   • Use alphanumeric characters, hyphens, and forward slashes")
                print(f"   • Maximum topic length is 256 characters")
            elif 'connection' in error_str or 'disconnected' in error_str:
                print(f"💡 Troubleshooting: Connection issue")
                print(f"   • MQTT connection may have been lost")
                print(f"   • Certificate files may be corrupted")
                print(f"   • Endpoint URL may be incorrect")
            else:
                print(f"💡 Troubleshooting: Unknown subscription failure")
                print(f"   • Run 'debug {topic}' command for detailed diagnostics")
                print(f"   • Check AWS IoT logs in CloudWatch if enabled")
            
            if debug:
                import traceback
                print(f"🔍 DEBUG: Full traceback:")
                traceback.print_exc()
            
            return False
    
    def publish_message(self, topic, message, qos=0, **mqtt_properties):
        """Publish a message to an MQTT topic with optional MQTT5 properties"""
        if not self.connected:
            print("❌ Not connected to AWS IoT Core")
            return False
        
        try:
            # Prepare payload
            if isinstance(message, dict):
                payload = json.dumps(message)
                content_type = "application/json"
            else:
                payload = str(message)
                content_type = "text/plain"
            
            # Extract MQTT5 properties
            user_properties = mqtt_properties.get('user_properties', [])
            correlation_data = mqtt_properties.get('correlation_data', None)
            message_expiry_interval = mqtt_properties.get('message_expiry_interval', None)
            response_topic = mqtt_properties.get('response_topic', None)
            
            print(f"\n📤 Publishing Message")
            print(f"   Topic: {topic}")
            print(f"   QoS: {qos} ({'At most once' if qos == 0 else 'At least once' if qos == 1 else 'Exactly once'})")
            print(f"   Payload Size: {len(payload)} bytes")
            print(f"   Content-Type: {content_type}")
            
            # Show MQTT5 properties if any
            if user_properties or correlation_data or message_expiry_interval or response_topic:
                print(f"   🔧 MQTT5 Properties:")
                if correlation_data:
                    print(f"      🔗 Correlation-Data: {correlation_data}")
                if message_expiry_interval:
                    print(f"      ⏰ Message-Expiry: {message_expiry_interval}s")
                if response_topic:
                    print(f"      ↩️  Response-Topic: {response_topic}")
                if user_properties:
                    print(f"      🏷️  User-Properties:")
                    for prop in user_properties:
                        print(f"         • {prop[0]}: {prop[1]}")
            
            # Prepare publish parameters
            publish_params = {
                'topic': topic,
                'payload': payload,
                'qos': qos
            }
            
            # Add MQTT5 properties if supported (AWS IoT Core currently uses MQTT 3.1.1)
            # Note: AWS IoT Core doesn't fully support MQTT5 yet, but we show the structure
            
            # Convert QoS to proper enum
            mqtt_qos = mqtt.QoS.AT_MOST_ONCE if qos == 0 else mqtt.QoS.AT_LEAST_ONCE
            publish_params['qos'] = mqtt_qos
            
            # Debug publish parameters
            debug_mode = getattr(self, 'debug_mode', False)
            if debug_mode:
                print(f"🔍 DEBUG: Publish parameters:")
                print(f"   Topic: {publish_params['topic']}")
                print(f"   QoS: {publish_params['qos']}")
                print(f"   Payload length: {len(publish_params['payload'])}")
            
            publish_future, packet_id = self.connection.publish(**publish_params)
            
            # Wait for publish to complete
            publish_result = publish_future.result()
            
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
                "Response Topic": response_topic
            }
            
            with self.message_lock:
                self.sent_messages.append(message_info)
            
            # Enhanced publish confirmation with protocol details
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            print(f"✅ [{timestamp}] PUBLISHED")
            print(f"   📤 Topic: {topic}")
            print(f"   🏷️  QoS: {qos} | Packet ID: {packet_id}")
            print(f"   📊 Size: {len(payload)} bytes | Type: {content_type}")
            if qos > 0:
                print(f"   🔄 Delivery: Acknowledgment required (QoS {qos})")
            else:
                print(f"   🚀 Delivery: Fire-and-forget (QoS 0)")
            
            return True
            
        except Exception as e:
            print(f"❌ Publish failed: {str(e)}")
            print(f"🔍 Detailed Error Information:")
            print(f"   Error Type: {type(e).__name__}")
            print(f"   Error Message: {str(e)}")
            
            # Check for common issues
            error_str = str(e).lower()
            if 'timeout' in error_str:
                print(f"💡 Troubleshooting: Publish timeout")
                print(f"   • MQTT connection may be unstable")
                print(f"   • Network connectivity issues")
                print(f"   • AWS IoT endpoint may be unreachable")
            elif 'not authorized' in error_str or 'forbidden' in error_str or 'access denied' in error_str:
                print(f"💡 Troubleshooting: Authorization failed")
                print(f"   • Certificate may not be ACTIVE")
                print(f"   • Certificate may not be attached to Thing")
                print(f"   • Policy may not be attached to certificate")
            elif 'invalid topic' in error_str or 'malformed' in error_str:
                print(f"💡 Troubleshooting: Invalid topic format")
                print(f"   • Topics cannot start with '/' or '$' (unless AWS reserved)")
                print(f"   • Use alphanumeric characters, hyphens, and forward slashes")
                print(f"   • Maximum topic length is 256 characters")
            elif 'payload too large' in error_str:
                print(f"💡 Troubleshooting: Payload size limit exceeded")
                print(f"   • AWS IoT message size limit is 128 KB")
                print(f"   • Current payload size: {len(payload)} bytes")
            elif 'connection' in error_str or 'disconnected' in error_str:
                print(f"💡 Troubleshooting: Connection issue")
                print(f"   • MQTT connection may have been lost")
                print(f"   • Certificate files may be corrupted")
                print(f"   • Endpoint URL may be incorrect")
            else:
                print(f"💡 Troubleshooting: Unknown publish failure")
                print(f"   • Run 'debug {topic}' command for detailed diagnostics")
                print(f"   • Check AWS IoT logs in CloudWatch if enabled")
            
            return False
    
    def interactive_messaging(self):
        """Interactive messaging interface"""
        self.print_step(2, "Interactive MQTT Messaging")
        
        print(f"💡 MQTT Topic Guidelines:")
        print(f"   • Use forward slashes for hierarchy: device/sensor/temperature")
        print(f"   • Avoid leading slashes: ❌ /device/data ✅ device/data")
        print(f"   • Keep topics descriptive and organized")
        print(f"   • AWS IoT reserved topics start with $aws/")
        
        # Get subscription topic
        while True:
            try:
                sub_topic = input("\n📥 Enter topic to subscribe to (or 'skip'): ").strip()
                if sub_topic.lower() == 'skip':
                    sub_topic = None
                    break
                elif sub_topic:
                    # Ask for QoS
                    while True:
                        try:
                            qos_choice = input("   QoS level (0=At most once, 1=At least once) [0]: ").strip()
                            if qos_choice == '' or qos_choice == '0':
                                sub_qos = 0
                                break
                            elif qos_choice == '1':
                                sub_qos = 1
                                break
                            else:
                                print("   ❌ Please enter 0 or 1")
                        except KeyboardInterrupt:
                            print(f"\n🛑 Operation cancelled")
                            return
                    
                    # Check if debug mode is available (passed from main)
                    debug_mode = getattr(self, 'debug_mode', False)
                    if self.subscribe_to_topic(sub_topic, sub_qos, debug=debug_mode):
                        break
                    else:
                        print("   ❌ Subscription failed, try again")
                        
                        # Offer connection diagnostics
                        try:
                            check_debug = input("   Would you like to run connection diagnostics? (y/N): ").strip().lower()
                            if check_debug == 'y':
                                self.check_connection_details(sub_topic)
                        except KeyboardInterrupt:
                            print(f"\n🛑 Operation cancelled")
                            return
                else:
                    print("   ❌ Topic cannot be empty")
            except KeyboardInterrupt:
                print(f"\n🛑 Operation cancelled")
                return
        
        # Interactive messaging loop
        print(f"\n🎮 Interactive Messaging Mode")
        print(f"💡 Messages will appear immediately when received on subscribed topics!")
        print(f"\nCommands:")
        print(f"   • 'sub <topic>' - Subscribe to topic (QoS 0)")
        print(f"   • 'sub1 <topic>' - Subscribe to topic (QoS 1)")
        print(f"   • 'unsub <topic>' - Unsubscribe from topic")
        print(f"   • 'pub <topic> <message>' - Publish message (QoS 0)")
        print(f"   • 'pub1 <topic> <message>' - Publish with QoS 1")
        print(f"   • 'json <topic> <key=value> [key=value...]' - Publish JSON")
        print(f"   • 'props <topic> <message> [prop=value...]' - Publish with MQTT5 properties")
        print(f"   • 'test' - Send test message to subscribed topics")
        print(f"   • 'status' - Show connection and subscription status")
        print(f"   • 'messages' - Show message history")
        print(f"   • 'debug [topic]' - Show connection diagnostics and troubleshooting")
        print(f"   • 'clear' - Clear screen")
        print(f"   • 'help' - Show this help")
        print(f"   • 'quit' - Exit")
        print(f"\n" + "="*60)
        print(f"\n💡 Tip: Press Ctrl+C at any time to exit gracefully")
        
        while True:
            try:
                command = input(f"\n📡 MQTT> ").strip()
                
                if not command:
                    continue
                
                parts = command.split(' ', 2)
                cmd = parts[0].lower()
                
                if cmd == 'quit':
                    break
                
                elif cmd == 'help':
                    print(f"\n📖 Available Commands:")
                    print(f"   sub <topic>               - Subscribe with QoS 0")
                    print(f"   sub1 <topic>              - Subscribe with QoS 1")
                    print(f"   unsub <topic>             - Unsubscribe from topic")
                    print(f"   pub <topic> <message>     - Publish with QoS 0")
                    print(f"   pub1 <topic> <message>    - Publish with QoS 1")
                    print(f"   json <topic> key=val ...  - Publish JSON object")
                    print(f"   props <topic> <msg> ...   - Publish with MQTT5 properties")
                    print(f"   test                      - Send test message to subscribed topics")
                    print(f"   status                    - Connection status")
                    print(f"   messages                  - Message history")
                    print(f"   debug [topic]             - Show connection diagnostics")
                    print(f"   clear                     - Clear screen")
                    print(f"   quit                      - Exit")
                    print(f"\n💡 MQTT5 Properties (props command):")
                    print(f"   correlation=<data>        - Correlation data for request/response")
                    print(f"   expiry=<seconds>          - Message expiry interval")
                    print(f"   response=<topic>          - Response topic for replies")
                    print(f"   user.<key>=<value>        - User-defined properties")
                
                elif cmd == 'status':
                    print(f"\n📊 Connection Status:")
                    print(f"   Connected: {'✅ Yes' if self.connected else '❌ No'}")
                    print(f"   Subscriptions: {len(self.subscriptions)}")
                    for topic, info in self.subscriptions.items():
                        print(f"      • {topic} (QoS {info['qos']})")
                    print(f"   Messages Sent: {len(self.sent_messages)}")
                    print(f"   Messages Received: {len(self.received_messages)}")
                
                elif cmd == 'messages':
                    print(f"\n📨 Message History:")
                    with self.message_lock:
                        all_messages = self.sent_messages + self.received_messages
                        all_messages.sort(key=lambda x: x['Timestamp'])
                        
                        for msg in all_messages[-10:]:  # Show last 10 messages
                            direction = "📤" if msg['Direction'] == 'SENT' else "📥"
                            timestamp = msg['Timestamp'].split('T')[1][:8]
                            print(f"   {direction} [{timestamp}] {msg['Topic']} (QoS {msg['QoS']})")
                            if len(msg['Payload']) > 50:
                                print(f"      {msg['Payload'][:50]}...")
                            else:
                                print(f"      {msg['Payload']}")
                
                elif cmd in ['sub', 'sub1']:
                    if len(parts) < 2:
                        print("   ❌ Usage: sub <topic>")
                        continue
                    
                    qos = 1 if cmd == 'sub1' else 0
                    print(f"\n📚 LEARNING MOMENT: MQTT Topic Subscription")
                    print(f"Subscribing to MQTT topics allows your device to receive messages published to those topics. QoS {qos} means {'at-least-once delivery' if qos == 1 else 'at-most-once delivery'}. Topic wildcards like + (single level) and # (multi-level) enable flexible message filtering.")
                    print(f"\n🔄 NEXT: Subscribing to topic with QoS {qos}...")
                    try:
                        input("Press Enter to continue...")
                    except KeyboardInterrupt:
                        print(f"\n🛑 Operation cancelled")
                        continue
                    
                    topic = parts[1]
                    
                    debug_mode = getattr(self, 'debug_mode', False)
                    if self.subscribe_to_topic(topic, qos, debug=debug_mode):
                        print(f"   ✅ Successfully subscribed to {topic} with QoS {qos}")
                    else:
                        print(f"   ❌ Failed to subscribe to {topic}")
                
                elif cmd == 'unsub':
                    if len(parts) < 2:
                        print("   ❌ Usage: unsub <topic>")
                        continue
                    
                    topic = parts[1]
                    if topic not in self.subscriptions:
                        print(f"   ⚠️  Not subscribed to {topic}")
                        continue
                    
                    try:
                        unsubscribe_future, packet_id = self.connection.unsubscribe(topic)
                        unsubscribe_future.result()
                        del self.subscriptions[topic]
                        print(f"   ✅ Successfully unsubscribed from {topic}")
                    except Exception as e:
                        print(f"   ❌ Failed to unsubscribe from {topic}: {str(e)}")
                
                elif cmd in ['pub', 'pub1']:
                    if len(parts) < 3:
                        print("   ❌ Usage: pub <topic> <message>")
                        continue
                    
                    qos = 1 if cmd == 'pub1' else 0
                    print(f"\n📚 LEARNING MOMENT: MQTT Message Publishing")
                    print(f"Publishing sends messages to MQTT topics where subscribed clients can receive them. QoS {qos} ensures {'at-least-once delivery' if qos == 1 else 'at-most-once delivery'}. This is how IoT devices send sensor data, status updates, and alerts to applications.")
                    print(f"\n🔄 NEXT: Publishing message with QoS {qos}...")
                    try:
                        input("Press Enter to continue...")
                    except KeyboardInterrupt:
                        print(f"\n🛑 Operation cancelled")
                        continue
                    
                    topic = parts[1]
                    message = parts[2]
                    
                    self.publish_message(topic, message, qos)
                
                elif cmd == 'json':
                    if len(parts) < 3:
                        print("   ❌ Usage: json <topic> key=value [key=value...]")
                        continue
                    
                    topic = parts[1]
                    json_parts = parts[2].split()
                    
                    json_obj = {}
                    for part in json_parts:
                        if '=' in part:
                            key, value = part.split('=', 1)
                            # Try to convert to appropriate type
                            try:
                                if value.lower() in ['true', 'false']:
                                    json_obj[key] = value.lower() == 'true'
                                elif value.isdigit():
                                    json_obj[key] = int(value)
                                elif '.' in value and value.replace('.', '').isdigit():
                                    json_obj[key] = float(value)
                                else:
                                    json_obj[key] = value
                            except:
                                json_obj[key] = value
                    
                    if json_obj:
                        # Add timestamp
                        json_obj['timestamp'] = datetime.now().isoformat()
                        self.publish_message(topic, json_obj)
                    else:
                        print("   ❌ No valid key=value pairs found")
                
                elif cmd == 'props':
                    if len(parts) < 3:
                        print("   ❌ Usage: props <topic> <message> [prop=value...]")
                        print("   💡 Properties: correlation=data, expiry=60, response=topic, user.key=value")
                        continue
                    
                    topic = parts[1]
                    message_parts = parts[2].split()
                    message = message_parts[0]
                    
                    # Parse MQTT5 properties
                    mqtt_props = {
                        'user_properties': [],
                        'correlation_data': None,
                        'message_expiry_interval': None,
                        'response_topic': None
                    }
                    
                    for part in message_parts[1:]:
                        if '=' in part:
                            key, value = part.split('=', 1)
                            if key == 'correlation':
                                mqtt_props['correlation_data'] = value
                            elif key == 'expiry':
                                try:
                                    mqtt_props['message_expiry_interval'] = int(value)
                                except ValueError:
                                    print(f"   ⚠️  Invalid expiry value: {value}")
                            elif key == 'response':
                                mqtt_props['response_topic'] = value
                            elif key.startswith('user.'):
                                user_key = key[5:]  # Remove 'user.' prefix
                                mqtt_props['user_properties'].append((user_key, value))
                    
                    # Clean up None values
                    mqtt_props = {k: v for k, v in mqtt_props.items() if v is not None and v != []}
                    
                    self.publish_message(topic, message, qos=0, **mqtt_props)
                
                elif cmd == 'test':
                    if not self.subscriptions:
                        print("   ⚠️  No active subscriptions. Subscribe to a topic first.")
                    else:
                        test_message = {
                            "message": "Test message from MQTT Explorer",
                            "timestamp": datetime.now().isoformat(),
                            "test_id": uuid.uuid4().hex[:8]
                        }
                        
                        print(f"   🧪 Sending test message to {len(self.subscriptions)} subscribed topic(s):")
                        for topic in self.subscriptions.keys():
                            print(f"      📤 {topic}")
                            self.publish_message(topic, test_message)
                
                elif cmd == 'debug':
                    topic = parts[1] if len(parts) > 1 else None
                    self.check_connection_details(topic)
                
                elif cmd == 'clear':
                    try:
                        if os.name == 'posix':
                            os.system('clear')
                        else:
                            os.system('cls')
                    except Exception:
                        print("\n" * 50)  # Fallback: print newlines to simulate clear
                    print(f"📡 MQTT Client Explorer - Session Active")
                    print(f"Connected: {'✅' if self.connected else '❌'} | Subscriptions: {len(self.subscriptions)} | Messages: {self.message_count}")
                
                else:
                    print(f"   ❌ Unknown command: {cmd}. Type 'help' for available commands.")
            
            except KeyboardInterrupt:
                print(f"\n\n🛑 Interrupted by user")
                break
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
    
    def check_connection_details(self, topic=None):
        """Check and display detailed connection and certificate information"""
        print(f"\n🔍 MQTT Connection Diagnostics")
        print(f"=" * 60)
        
        print(f"📡 Connection Status:")
        print(f"   • Connected: {'✅ Yes' if self.connected else '❌ No'}")
        print(f"   • Active Subscriptions: {len(self.subscriptions)}")
        print(f"   • Messages Sent: {len(self.sent_messages)}")
        print(f"   • Messages Received: {len(self.received_messages)}")
        
        if hasattr(self, 'connection') and self.connection:
            try:
                # Try to get connection details
                print(f"\n🔗 MQTT Connection Details:")
                print(f"   • Client ID: Available")
                print(f"   • Keep Alive: 30 seconds")
                print(f"   • Clean Session: False")
                print(f"   • Protocol: MQTT 3.1.1 over TLS 1.2")
            except:
                print(f"   • Connection object exists but details unavailable")
        
        if topic:
            print(f"\n📝 Topic Analysis: {topic}")
            print(f"   • Length: {len(topic)} characters (max: 256)")
            print(f"   • Valid characters: {'✅' if all(c.isalnum() or c in '/-_' for c in topic) else '❌'}")
            print(f"   • Starts with '/': {'❌ Invalid' if topic.startswith('/') else '✅ Valid'}")
            print(f"   • Contains '$': {'⚠️  Reserved' if '$' in topic else '✅ Valid'}")
        
        print(f"\n🔧 Troubleshooting Steps:")
        print(f"1. Verify certificate is ACTIVE in AWS IoT Console")
        print(f"2. Check certificate is attached to the correct Thing")
        print(f"3. Confirm policy is attached to the certificate")
        print(f"4. Check AWS IoT logs in CloudWatch (if enabled)")
        
        print(f"\n💡 Common Issues:")
        print(f"   • Certificate expired or inactive")
        print(f"   • Certificate not attached to Thing")
        print(f"   • Policy not attached to certificate")
        print(f"   • Network connectivity issues")
        print(f"   • Incorrect endpoint or region")

    def disconnect(self):
        """Disconnect from AWS IoT Core"""
        if self.connection and self.connected:
            print(f"\n🔌 Disconnecting from AWS IoT Core...")
            
            # Unsubscribe from all topics
            for topic in list(self.subscriptions.keys()):
                try:
                    unsubscribe_future, packet_id = self.connection.unsubscribe(topic)
                    unsubscribe_future.result()
                    print(f"   ✅ Unsubscribed from: {topic}")
                except Exception as e:
                    print(f"   ⚠️  Error unsubscribing from {topic}: {str(e)}")
            
            # Disconnect
            try:
                disconnect_future = self.connection.disconnect()
                disconnect_future.result()
                
                self.print_mqtt_details("DISCONNECTION", {
                    "Status": "Successfully disconnected from AWS IoT Core",
                    "Total Messages Sent": len(self.sent_messages),
                    "Total Messages Received": len(self.received_messages),
                    "Session Duration": "Connection closed cleanly"
                })
                
            except Exception as e:
                print(f"   ❌ Error during disconnect: {str(e)}")
            
            self.connected = False

def main():
    import sys
    
    try:
        # Check for debug flag
        debug_mode = '--debug' in sys.argv or '-d' in sys.argv
        
        print("📡 AWS IoT MQTT Client Explorer")
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
        
        print("Learn MQTT communication with AWS IoT Core through hands-on exploration.")
        print("This tool demonstrates:")
        print("• MQTT connection establishment with X.509 certificates")
        print("• Topic subscription and publishing with QoS options")
        print("• Detailed MQTT protocol information for every operation")
        print("• Interactive messaging with real-time feedback")
        
        print("\n📚 LEARNING MOMENT: MQTT Protocol & IoT Communication")
        print("MQTT is a lightweight messaging protocol designed for IoT devices. It uses a publish-subscribe model where devices publish messages to topics and subscribe to receive messages. AWS IoT Core acts as the MQTT broker, handling message routing, QoS guarantees, and device authentication through X.509 certificates.")
        print("\n🔄 NEXT: We will establish an MQTT connection and explore real-time messaging")
        input("Press Enter to continue...")
        
        if debug_mode:
            print(f"\n🔍 DEBUG MODE ENABLED")
            print(f"• Enhanced AWS IoT API logging for device/certificate selection")
            print(f"• Detailed MQTT connection parameters")
            print(f"• Extended error diagnostics")
        else:
            print(f"\n💡 Tip: Use --debug or -d flag for enhanced AWS API logging")
        
        print("=" * 60)
        
        client = MQTTClientExplorer()
        client.debug_mode = debug_mode  # Store debug mode in client
        
        try:
            # Get IoT endpoint
            endpoint = client.get_iot_endpoint(debug=debug_mode)
            if not endpoint:
                return
            
            # Select device and certificate
            thing_name, cert_file, key_file = client.select_device_and_certificate(debug=debug_mode)
            if not thing_name:
                return
            
            # Connect to AWS IoT
            if not client.connect_to_aws_iot(thing_name, cert_file, key_file, endpoint, debug=debug_mode):
                return
            
            # Interactive messaging
            client.interactive_messaging()
            
        except KeyboardInterrupt:
            print(f"\n\n🛑 Interrupted by user")
        except Exception as e:
            print(f"\n❌ Unexpected error: {str(e)}")
        finally:
            # Always disconnect cleanly
            client.disconnect()
            print(f"\n👋 MQTT Client Explorer session ended")
    
    except KeyboardInterrupt:
        print(f"\n\n🛑 Interrupted by user")
        print(f"👋 MQTT Client Explorer session ended")

if __name__ == "__main__":
    main()