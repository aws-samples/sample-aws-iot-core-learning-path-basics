#!/usr/bin/env python3
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

"""
AWS IoT Device Shadow Explorer
Educational tool for learning AWS IoT Device Shadow service through hands-on exploration.
"""
import boto3
import json
import os
import sys
import time
import threading
from datetime import datetime
from botocore.exceptions import ClientError
from awscrt import mqtt, io, auth, http
from awsiot import mqtt_connection_builder

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
import uuid

class DeviceShadowExplorer:
    def __init__(self):
        self.connection = None
        self.connected = False
        self.thing_name = None
        self.shadow_name = None  # Classic shadow uses None
        self.local_state_file = None
        self.received_messages = []
        self.message_lock = threading.Lock()
        self.debug_mode = False
        
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
        """Select a device and its certificate for Shadow operations"""
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
    
    def setup_local_state_file(self, thing_name, debug=False):
        """Setup local state file for device shadow simulation"""
        cert_dir = os.path.join(os.getcwd(), 'certificates', thing_name)
        state_file = os.path.join(cert_dir, 'device_state.json')
        
        if debug:
            print(f"🔍 DEBUG: Setting up local state file: {state_file}")
            print(f"🔍 DEBUG: Certificate directory: {cert_dir}")
            print(f"🔍 DEBUG: File exists: {os.path.exists(state_file)}")
        
        # Create default state if file doesn't exist
        if not os.path.exists(state_file):
            default_state = {
                "temperature": 22.5,
                "humidity": 45.0,
                "status": "online",
                "firmware_version": "1.0.0",
                "last_updated": datetime.now().isoformat()
            }
            
            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(default_state, f, indent=2)
            
            print(f"📄 Created default local state file: {state_file}")
            print(f"📊 Default state: {json.dumps(default_state, indent=2)}")
            if debug:
                print(f"🔍 DEBUG: Created new state file with {len(default_state)} properties")
        else:
            print(f"📄 Using existing local state file: {state_file}")
            with open(state_file, 'r', encoding='utf-8') as f:
                current_state = json.load(f)
            print(f"📊 Current local state: {json.dumps(current_state, indent=2)}")
            if debug:
                print(f"🔍 DEBUG: Loaded existing state file with {len(current_state)} properties")
                print(f"🔍 DEBUG: File size: {os.path.getsize(state_file)} bytes")
        
        self.local_state_file = state_file
        return state_file
    
    def load_local_state(self):
        """Load current local device state"""
        try:
            with open(self.local_state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error loading local state: {str(e)}")
            return {}
    
    def save_local_state(self, state):
        """Save device state to local file"""
        try:
            state['last_updated'] = datetime.now().isoformat()
            with open(self.local_state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2)
            print(f"💾 Local state saved to: {self.local_state_file}")
            return True
        except Exception as e:
            print(f"❌ Error saving local state: {str(e)}")
            return False
    
    def on_connection_interrupted(self, connection, error, **kwargs):
        """Callback for connection interruption"""
        self.print_shadow_details("CONNECTION INTERRUPTED", {
            "Error": str(error),
            "Timestamp": datetime.now().isoformat(),
            "Auto Reconnect": "AWS IoT SDK will attempt to reconnect automatically"
        })
        self.connected = False
    
    def on_connection_resumed(self, connection, return_code, session_present, **kwargs):
        """Callback for connection resumption"""
        self.print_shadow_details("CONNECTION RESUMED", {
            "Return Code": return_code,
            "Session Present": session_present,
            "Timestamp": datetime.now().isoformat(),
            "Status": "Connection restored successfully"
        })
        self.connected = True
    
    def on_shadow_message_received(self, topic, payload, dup, qos, retain, **kwargs):
        """Callback for Shadow messages with comprehensive analysis"""
        try:
            # Parse shadow message
            try:
                shadow_data = json.loads(payload.decode('utf-8'))
                payload_display = json.dumps(shadow_data, indent=2)
            except:
                payload_display = payload.decode('utf-8')
                shadow_data = {}
            
            message_info = {
                "Direction": "RECEIVED",
                "Topic": topic,
                "QoS": qos,
                "Payload Size": f"{len(payload)} bytes",
                "Timestamp": datetime.now().isoformat(),
                "Shadow Data": shadow_data
            }
            
            with self.message_lock:
                self.received_messages.append(message_info)
            
            # Immediate visual notification
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            print(f"\n" + "="*70)
            print(f"🌟 SHADOW MESSAGE RECEIVED [{timestamp}]")
            print(f"="*70)
            
            if self.debug_mode:
                print(f"🔍 DEBUG: Raw topic: {topic}")
                print(f"🔍 DEBUG: QoS: {qos}, Duplicate: {dup}, Retain: {retain}")
                print(f"🔍 DEBUG: Payload size: {len(payload)} bytes")
                print(f"🔍 DEBUG: Message count: {len(self.received_messages) + 1}")
            
            # Analyze topic to determine message type
            topic_parts = topic.split('/')
            if 'get' in topic and 'accepted' in topic:
                self.handle_shadow_get_accepted(shadow_data)
            elif 'get' in topic and 'rejected' in topic:
                self.handle_shadow_get_rejected(shadow_data)
            elif 'update' in topic and 'accepted' in topic:
                self.handle_shadow_update_accepted(shadow_data)
            elif 'update' in topic and 'rejected' in topic:
                self.handle_shadow_update_rejected(shadow_data)
            elif 'update' in topic and 'delta' in topic:
                self.handle_shadow_delta(shadow_data)
            else:
                print(f"📥 Topic: {topic}")
                print(f"🏷️  QoS: {qos}")
                print(f"📊 Payload: {payload_display}")
                if self.debug_mode:
                    print(f"🔍 DEBUG: Unrecognized shadow topic pattern")
            
            print(f"="*70)
            
        except Exception as e:
            print(f"\n❌ Error processing shadow message: {str(e)}")
    
    def handle_shadow_get_accepted(self, shadow_data):
        """Handle shadow get accepted response"""
        print(f"✅ SHADOW GET ACCEPTED")
        if self.debug_mode:
            print(f"   📝 Topic: $aws/things/{self.thing_name}/shadow/get/accepted")
        print(f"📋 Shadow Document Retrieved:")
        
        state = shadow_data.get('state', {})
        desired = state.get('desired', {})
        reported = state.get('reported', {})
        metadata = shadow_data.get('metadata', {})
        version = shadow_data.get('version', 'Unknown')
        
        print(f"   📊 Version: {version}")
        print(f"   🎯 Desired State: {json.dumps(desired, indent=6) if desired else 'None'}")
        print(f"   📡 Reported State: {json.dumps(reported, indent=6) if reported else 'None'}")
        
        # Compare with local state
        if desired:
            if self.debug_mode:
                print(f"🔍 DEBUG: Comparing desired state with local state")
                print(f"🔍 DEBUG: Desired keys: {list(desired.keys())}")
            self.compare_and_prompt_update(desired)
        elif self.debug_mode:
            print(f"🔍 DEBUG: No desired state in shadow document")
    
    def handle_shadow_get_rejected(self, shadow_data):
        """Handle shadow get rejected response"""
        print(f"❌ SHADOW GET REJECTED")
        if self.debug_mode:
            print(f"   📝 Topic: $aws/things/{self.thing_name}/shadow/get/rejected")
        error_code = shadow_data.get('code', 'Unknown')
        error_message = shadow_data.get('message', 'No message')
        print(f"   🚫 Error Code: {error_code}")
        print(f"   📝 Message: {error_message}")
        
        if error_code == 404:
            print(f"   💡 Shadow doesn't exist yet - will create one on next update")
            if self.debug_mode:
                print(f"🔍 DEBUG: This is normal for new devices - shadow created on first update")
        elif self.debug_mode:
            print(f"🔍 DEBUG: Error code {error_code} indicates: {error_message}")
    
    def handle_shadow_update_accepted(self, shadow_data):
        """Handle shadow update accepted response"""
        print(f"✅ SHADOW UPDATE ACCEPTED")
        if self.debug_mode:
            print(f"   📝 Topic: $aws/things/{self.thing_name}/shadow/update/accepted")
        state = shadow_data.get('state', {})
        version = shadow_data.get('version', 'Unknown')
        timestamp = shadow_data.get('timestamp', 'Unknown')
        
        print(f"   📊 New Version: {version}")
        print(f"   ⏰ Timestamp: {timestamp}")
        if 'desired' in state:
            print(f"   🎯 Updated Desired: {json.dumps(state['desired'], indent=6)}")
        if 'reported' in state:
            print(f"   📡 Updated Reported: {json.dumps(state['reported'], indent=6)}")
    
    def handle_shadow_update_rejected(self, shadow_data):
        """Handle shadow update rejected response"""
        print(f"❌ SHADOW UPDATE REJECTED")
        if self.debug_mode:
            print(f"   📝 Topic: $aws/things/{self.thing_name}/shadow/update/rejected")
        error_code = shadow_data.get('code', 'Unknown')
        error_message = shadow_data.get('message', 'No message')
        print(f"   🚫 Error Code: {error_code}")
        print(f"   📝 Message: {error_message}")
    
    def handle_shadow_delta(self, shadow_data):
        """Handle shadow delta message (desired != reported)"""
        print(f"🔄 SHADOW DELTA RECEIVED")
        if self.debug_mode:
            print(f"   📝 Topic: $aws/things/{self.thing_name}/shadow/update/delta")
        print(f"   📝 Description: Desired state differs from reported state")
        
        state = shadow_data.get('state', {})
        version = shadow_data.get('version', 'Unknown')
        timestamp = shadow_data.get('timestamp', 'Unknown')
        
        print(f"   📊 Version: {version}")
        print(f"   ⏰ Timestamp: {timestamp}")
        print(f"   🔄 Changes Needed: {json.dumps(state, indent=6)}")
        
        # Prompt user to apply changes
        if self.debug_mode:
            print(f"🔍 DEBUG: Processing delta with {len(state)} changed properties")
            print(f"🔍 DEBUG: Delta keys: {list(state.keys())}")
        self.compare_and_prompt_update(state, is_delta=True)
    
    def compare_and_prompt_update(self, desired_state, is_delta=False):
        """Compare desired state with local state and prompt for updates"""
        local_state = self.load_local_state()
        
        if self.debug_mode:
            print(f"\n🔍 DEBUG: Loaded local state with {len(local_state)} properties")
            print(f"🔍 DEBUG: Comparing {len(desired_state)} desired properties")
        
        print(f"\n🔍 State Comparison:")
        print(f"   📱 Local State: {json.dumps(local_state, indent=6)}")
        print(f"   {'🔄 Delta' if is_delta else '🎯 Desired'}: {json.dumps(desired_state, indent=6)}")
        
        # Find differences
        differences = {}
        for key, desired_value in desired_state.items():
            local_value = local_state.get(key)
            if local_value != desired_value:
                differences[key] = {
                    'local': local_value,
                    'desired': desired_value
                }
        
        if differences:
            if self.debug_mode:
                print(f"\n🔍 DEBUG: Found {len(differences)} differences out of {len(desired_state)} desired properties")
            print(f"\n⚠️  Differences Found:")
            for key, diff in differences.items():
                print(f"   • {key}: {diff['local']} → {diff['desired']}")
                if self.debug_mode:
                    print(f"     🔍 DEBUG: Type change: {type(diff['local']).__name__} → {type(diff['desired']).__name__}")
            
            apply_changes = input(f"\nApply these changes to local device? (y/N): ").strip().lower()
            if apply_changes == 'y':
                time.sleep(0.1)  # nosemgrep: arbitrary-sleep
                # Update local state
                for key, desired_value in desired_state.items():
                    local_state[key] = desired_value
                
                if self.save_local_state(local_state):
                    if self.debug_mode:
                        print(f"🔍 DEBUG: Updated {len(desired_state)} properties in local state")
                        print(f"🔍 DEBUG: New local state size: {len(local_state)} properties")
                    print(f"✅ Local state updated successfully")
                    
                    # Automatically report back to shadow (required for proper synchronization)
                    print(f"📡 Automatically reporting updated state to shadow...")
                    self.update_shadow_reported(local_state)
                    time.sleep(1.5)  # nosemgrep: arbitrary-sleep
                else:
                    print(f"❌ Failed to update local state")
            else:
                print(f"⏭️  Changes not applied to local device")
        else:
            if self.debug_mode:
                print(f"🔍 DEBUG: All {len(desired_state)} desired properties match local state")
            print(f"✅ Local state matches desired state - no changes needed")
    
    def connect_to_aws_iot(self, thing_name, cert_file, key_file, endpoint, debug=False):
        """Establish MQTT connection to AWS IoT Core for Shadow operations"""
        self.print_step(1, "Establishing MQTT Connection for Shadow Operations")
        
        if debug:
            print(f"🔍 DEBUG: Shadow MQTT Connection Setup")
            print(f"   Thing Name: {thing_name}")
            print(f"   Certificate File: {cert_file}")
            print(f"   Private Key File: {key_file}")
            print(f"   Endpoint: {endpoint}")
        
        try:
            # Create client ID
            client_id = f"{thing_name}-shadow-{uuid.uuid4().hex[:8]}"
            
            print(f"🔗 Shadow Connection Parameters:")
            print(f"   Client ID: {client_id}")
            print(f"   Thing Name: {thing_name}")
            print(f"   Endpoint: {endpoint}")
            print(f"   Port: 8883")
            print(f"   Protocol: MQTT 3.1.1 over TLS")
            print(f"   Authentication: X.509 Certificate")
            print(f"   Shadow Type: Classic Shadow")
            
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
                on_connection_resumed=self.on_connection_resumed
            )
            
            print(f"\n🔄 Connecting to AWS IoT Core...")
            connect_future = self.connection.connect()
            connection_result = connect_future.result()
            
            if debug:
                print(f"🔍 DEBUG: Connection result: {connection_result}")
            
            self.connected = True
            self.thing_name = thing_name
            
            self.print_shadow_details("SHADOW CONNECTION ESTABLISHED", {
                "Status": "Successfully connected to AWS IoT Core",
                "Client ID": client_id,
                "Thing Name": thing_name,
                "Endpoint": endpoint,
                "Shadow Type": "Classic Shadow",
                "Clean Session": True,
                "Keep Alive": "30 seconds",
                "TLS Version": "1.2",
                "Certificate Authentication": "X.509 mutual TLS"
            })
            
            return True
            
        except Exception as e:
            print(f"❌ Shadow connection failed: {str(e)}")
            return False
    
    def subscribe_to_shadow_topics(self, debug=False):
        """Subscribe to all relevant shadow topics"""
        self.print_step(2, "Subscribing to Shadow Topics")
        
        if not self.connected:
            print("❌ Not connected to AWS IoT Core")
            return False
        
        # Shadow topic patterns for classic shadow
        shadow_topics = [
            f"$aws/things/{self.thing_name}/shadow/get/accepted",
            f"$aws/things/{self.thing_name}/shadow/get/rejected", 
            f"$aws/things/{self.thing_name}/shadow/update/accepted",
            f"$aws/things/{self.thing_name}/shadow/update/rejected",
            f"$aws/things/{self.thing_name}/shadow/update/delta"
        ]
        
        print(f"🌟 Shadow Topics for Thing: {self.thing_name}")
        print(f"📋 Classic Shadow Topics:")
        
        success_count = 0
        for topic in shadow_topics:
            try:
                if debug:
                    print(f"🔍 DEBUG: Subscribing to shadow topic: {topic}")
                
                subscribe_future, packet_id = self.connection.subscribe(
                    topic=topic,
                    qos=mqtt.QoS.AT_LEAST_ONCE,
                    callback=self.on_shadow_message_received
                )
                
                subscribe_result = subscribe_future.result()
                
                print(f"   ✅ {topic}")
                success_count += 1
                
                if debug:
                    print(f"🔍 DEBUG: Subscription successful, packet ID: {packet_id}")
                
            except Exception as e:
                print(f"   ❌ {topic} - Error: {str(e)}")
        
        if success_count == len(shadow_topics):
            print(f"\n✅ Successfully subscribed to all {success_count} shadow topics")
            
            print(f"\n📖 Shadow Topic Explanations:")
            print(f"   • get/accepted - Shadow document retrieval success")
            print(f"   • get/rejected - Shadow document retrieval failure")
            print(f"   • update/accepted - Shadow update success")
            print(f"   • update/rejected - Shadow update failure")
            print(f"   • update/delta - Desired ≠ Reported (action needed)")
            
            return True
        else:
            print(f"⚠️  Only {success_count}/{len(shadow_topics)} subscriptions successful")
            return False
    
    def get_shadow_document(self, debug=False):
        """Request the current shadow document"""
        if not self.connected:
            print("❌ Not connected to AWS IoT Core")
            return False
        
        try:
            get_topic = f"$aws/things/{self.thing_name}/shadow/get"
            
            print(f"\n📥 Requesting Shadow Document")
            print(f"   Topic: {get_topic}")
            print(f"   Thing: {self.thing_name}")
            print(f"   Shadow Type: Classic")
            
            if debug:
                print(f"🔍 DEBUG: Publishing shadow get request")
                print(f"   Topic: {get_topic}")
                print(f"   Payload: Empty (shadow get requests have no payload)")
            
            # Shadow get requests have empty payload
            publish_future, packet_id = self.connection.publish(
                topic=get_topic,
                payload="",
                qos=mqtt.QoS.AT_LEAST_ONCE
            )
            
            # Non-blocking publish - don't wait for result
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            print(f"✅ [{timestamp}] Shadow GET request sent")
            print(f"   📤 Topic: {get_topic}")
            print(f"   🏷️  QoS: 1 | Packet ID: {packet_id}")
            print(f"   ⏳ Waiting for response on get/accepted or get/rejected...")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to request shadow document: {str(e)}")
            return False
    
    def update_shadow_reported(self, reported_state, debug=False):
        """Update the reported state in the shadow"""
        if not self.connected:
            print("❌ Not connected to AWS IoT Core")
            return False
        
        try:
            update_topic = f"$aws/things/{self.thing_name}/shadow/update"
            
            # Create shadow update payload
            shadow_update = {
                "state": {
                    "reported": reported_state
                }
            }
            
            payload = json.dumps(shadow_update)
            
            print(f"\n📤 Updating Shadow Reported State")
            print(f"   Topic: {update_topic}")
            print(f"   Thing: {self.thing_name}")
            print(f"   Update Type: Reported State")
            print(f"   Payload: {json.dumps(shadow_update, indent=6)}")
            
            if debug:
                print(f"🔍 DEBUG: Publishing shadow update")
                print(f"   Topic: {update_topic}")
                print(f"   Payload size: {len(payload)} bytes")
            
            publish_future, packet_id = self.connection.publish(
                topic=update_topic,
                payload=payload,
                qos=mqtt.QoS.AT_LEAST_ONCE
            )
            
            # Non-blocking publish - don't wait for result
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            print(f"✅ [{timestamp}] Shadow UPDATE sent")
            print(f"   📤 Topic: {update_topic}")
            print(f"   🏷️  QoS: 1 | Packet ID: {packet_id}")
            print(f"   ⏳ Waiting for response on update/accepted or update/rejected...")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to update shadow: {str(e)}")
            return False
    
    def update_shadow_desired(self, desired_state, debug=False):
        """Update the desired state in the shadow (simulates cloud/app request)"""
        if not self.connected:
            print("❌ Not connected to AWS IoT Core")
            return False
        
        try:
            update_topic = f"$aws/things/{self.thing_name}/shadow/update"
            
            # Create shadow update payload
            shadow_update = {
                "state": {
                    "desired": desired_state
                }
            }
            
            payload = json.dumps(shadow_update)
            
            print(f"\n📤 Updating Shadow Desired State")
            print(f"   Topic: {update_topic}")
            print(f"   Thing: {self.thing_name}")
            print(f"   Update Type: Desired State (simulating cloud/app request)")
            print(f"   Payload: {json.dumps(shadow_update, indent=6)}")
            
            if debug:
                print(f"🔍 DEBUG: Publishing shadow desired update")
                print(f"   Topic: {update_topic}")
                print(f"   Payload size: {len(payload)} bytes")
            
            publish_future, packet_id = self.connection.publish(
                topic=update_topic,
                payload=payload,
                qos=mqtt.QoS.AT_LEAST_ONCE
            )
            
            # Non-blocking publish - don't wait for result
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            print(f"✅ [{timestamp}] Shadow DESIRED UPDATE sent")
            print(f"   📤 Topic: {update_topic}")
            print(f"   🏷️  QoS: 1 | Packet ID: {packet_id}")
            print(f"   ⏳ Waiting for response and potential delta message...")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to update shadow desired state: {str(e)}")
            return False
    
    def interactive_shadow_management(self):
        """Interactive shadow management interface"""
        self.print_step(3, "Interactive Shadow Management")
        
        print(f"💡 Device Shadow Guidelines:")
        print(f"   • Desired state represents what the device should be")
        print(f"   • Reported state represents what the device currently is")
        print(f"   • Delta messages occur when desired ≠ reported")
        print(f"   • Local file simulates actual device state")
        
        # Initial shadow get
        print(f"\n🔄 Getting initial shadow state...")
        self.get_shadow_document(debug=self.debug_mode)
        
        # Interactive loop
        print(f"\n🎮 Interactive Shadow Management Mode")
        print(f"💡 Shadow messages will appear immediately when received!")
        
        print(f"\nCommands:")
        print(f"   • 'get' - Request current shadow document")
        print(f"   • 'local' - Show current local device state")
        print(f"   • 'edit' - Edit local device state")
        print(f"   • 'report' - Report current local state to shadow")
        print(f"   • 'desire <key=value> [key=value...]' - Set desired state (simulate cloud)")
        print(f"   • 'status' - Show connection and shadow status")
        print(f"   • 'messages' - Show shadow message history")
        print(f"   • 'debug' - Show connection diagnostics")
        print(f"   • 'help' - Show this help")
        print(f"   • 'quit' - Exit")
        print(f"\n" + "="*60)
        
        while True:
            try:
                command = input(f"\n🌟 Shadow> ").strip()
                
                if not command:
                    continue
                
                parts = command.split(' ', 1)
                cmd = parts[0].lower()
                
                if cmd == 'quit':
                    break
                
                elif cmd == 'help':
                    print(f"\n📖 Available Commands:")
                    print(f"   get                       - Request shadow document")
                    print(f"   local                     - Show local device state")
                    print(f"   edit                      - Edit local device state")
                    print(f"   report                    - Report local state to shadow")
                    print(f"   desire key=val [key=val]  - Set desired state")
                    print(f"   status                    - Connection status")
                    print(f"   messages                  - Shadow message history")
                    print(f"   debug                     - Connection diagnostics")
                    print(f"   quit                      - Exit")
                    print(f"\n💡 Example: desire temperature=25.0 status=active")
                
                elif cmd == 'get':
                    print("\n📚 LEARNING MOMENT: Shadow Document Retrieval")
                    print("Getting the shadow document retrieves the complete JSON state including desired, reported, and metadata. This shows the current synchronization status between your application's intentions (desired) and the device's actual state (reported). The version number helps track changes.")
                    print("\n🔄 NEXT: Retrieving the current shadow document...")
                    time.sleep(1)  # Brief pause instead of blocking input
                    
                    self.get_shadow_document(debug=self.debug_mode)
                    time.sleep(0.5)  # nosemgrep: arbitrary-sleep
                
                elif cmd == 'local':
                    local_state = self.load_local_state()
                    print(f"\n📱 Current Local Device State:")
                    print(f"{json.dumps(local_state, indent=2)}")
                
                elif cmd == 'edit':
                    self.edit_local_state()
                
                elif cmd == 'report':
                    print("\n📚 LEARNING MOMENT: Device State Reporting")
                    print("Reporting state updates the shadow's 'reported' section with the device's current status. This is how devices communicate their actual state to applications. The shadow service automatically calculates deltas when reported state differs from desired state.")
                    print("\n🔄 NEXT: Reporting local device state to the shadow...")
                    time.sleep(1)  # Brief pause instead of blocking input
                    
                    local_state = self.load_local_state()
                    print(f"\n📡 Reporting local state to shadow...")
                    self.update_shadow_reported(local_state, debug=self.debug_mode)
                    time.sleep(0.5)  # nosemgrep: arbitrary-sleep
                
                elif cmd == 'desire':
                    if len(parts) < 2:
                        print("   ❌ Usage: desire key=value [key=value...]")
                        print("   💡 Example: desire temperature=25.0 status=active")
                    else:
                        print("\n📚 LEARNING MOMENT: Desired State Management")
                        print("Setting desired state simulates how applications or cloud services request changes to device configuration. The shadow service stores these requests and notifies devices through delta messages when desired state differs from reported state. This enables remote device control.")
                        print("\n🔄 NEXT: Setting desired state to trigger device changes...")
                        time.sleep(1)  # Brief pause instead of blocking input
                    
                    # Parse key=value pairs
                    desired_updates = {}
                    for pair in parts[1].split():
                        if '=' in pair:
                            key, value = pair.split('=', 1)
                            # Try to convert to appropriate type
                            try:
                                if value.lower() in ['true', 'false']:
                                    desired_updates[key] = value.lower() == 'true'
                                elif value.isdigit():
                                    desired_updates[key] = int(value)
                                elif '.' in value and value.replace('.', '').isdigit():
                                    desired_updates[key] = float(value)
                                else:
                                    desired_updates[key] = value
                            except:
                                desired_updates[key] = value
                    
                    if desired_updates:
                        print(f"\n🎯 Setting desired state: {json.dumps(desired_updates, indent=2)}")
                        self.update_shadow_desired(desired_updates, debug=self.debug_mode)
                        time.sleep(0.5)  # nosemgrep: arbitrary-sleep
                    else:
                        print("   ❌ No valid key=value pairs found")
                
                elif cmd == 'status':
                    print(f"\n📊 Shadow Connection Status:")
                    print(f"   Connected: {'✅ Yes' if self.connected else '❌ No'}")
                    print(f"   Thing Name: {self.thing_name}")
                    print(f"   Shadow Type: Classic")
                    print(f"   Local State File: {self.local_state_file}")
                    print(f"   Messages Received: {len(self.received_messages)}")
                
                elif cmd == 'messages':
                    print(f"\n📨 Shadow Message History:")
                    with self.message_lock:
                        for msg in self.received_messages[-10:]:  # Show last 10 messages
                            timestamp = msg['Timestamp'].split('T')[1][:8]
                            topic_type = msg['Topic'].split('/')[-1]
                            print(f"   📥 [{timestamp}] {topic_type}")
                            if msg.get('Shadow Data'):
                                shadow_summary = str(msg['Shadow Data'])[:100]
                                print(f"      {shadow_summary}{'...' if len(str(msg['Shadow Data'])) > 100 else ''}")
                
                elif cmd == 'debug':
                    self.show_shadow_diagnostics()
                
                else:
                    print(f"   ❌ Unknown command: {cmd}. Type 'help' for available commands.")
            
            except KeyboardInterrupt:
                print(f"\n\n🛑 Interrupted by user")
                break
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
    
    def edit_local_state(self):
        """Interactive local state editor"""
        local_state = self.load_local_state()
        
        print(f"\n📝 Local State Editor")
        print(f"Current state: {json.dumps(local_state, indent=2)}")
        print(f"\nOptions:")
        print(f"1. Edit individual values")
        print(f"2. Replace entire state with JSON")
        print(f"3. Cancel")
        
        while True:
            choice = input("\nSelect option (1-3): ").strip()
            
            if choice == '1':
                # Edit individual values
                print(f"\nCurrent values:")
                keys = list(local_state.keys())
                for i, key in enumerate(keys, 1):
                    print(f"   {i}. {key}: {local_state[key]}")
                
                print(f"   {len(keys) + 1}. Add new key")
                print(f"   {len(keys) + 2}. Done editing")
                
                while True:
                    try:
                        edit_choice = int(input(f"\nSelect item to edit (1-{len(keys) + 2}): "))
                        
                        if 1 <= edit_choice <= len(keys):
                            # Edit existing key
                            key = keys[edit_choice - 1]
                            current_value = local_state[key]
                            print(f"\nEditing '{key}' (current: {current_value})")
                            new_value = input(f"New value (or press Enter to keep current): ").strip()
                            
                            if new_value:
                                # Try to convert to appropriate type
                                try:
                                    if new_value.lower() in ['true', 'false']:
                                        local_state[key] = new_value.lower() == 'true'
                                    elif new_value.isdigit():
                                        local_state[key] = int(new_value)
                                    elif '.' in new_value and new_value.replace('.', '').isdigit():
                                        local_state[key] = float(new_value)
                                    else:
                                        local_state[key] = new_value
                                    print(f"✅ Updated {key} = {local_state[key]}")
                                except:
                                    local_state[key] = new_value
                                    print(f"✅ Updated {key} = {local_state[key]}")
                        
                        elif edit_choice == len(keys) + 1:
                            # Add new key
                            new_key = input("New key name: ").strip()
                            if new_key:
                                new_value = input(f"Value for '{new_key}': ").strip()
                                # Try to convert to appropriate type
                                try:
                                    if new_value.lower() in ['true', 'false']:
                                        local_state[new_key] = new_value.lower() == 'true'
                                    elif new_value.isdigit():
                                        local_state[new_key] = int(new_value)
                                    elif '.' in new_value and new_value.replace('.', '').isdigit():
                                        local_state[new_key] = float(new_value)
                                    else:
                                        local_state[new_key] = new_value
                                    print(f"✅ Added {new_key} = {local_state[new_key]}")
                                    keys.append(new_key)  # Update keys list
                                except:
                                    local_state[new_key] = new_value
                                    print(f"✅ Added {new_key} = {local_state[new_key]}")
                                    keys.append(new_key)
                        
                        elif edit_choice == len(keys) + 2:
                            # Done editing
                            break
                        
                        else:
                            print("❌ Invalid selection")
                    
                    except ValueError:
                        print("❌ Please enter a valid number")
                
                break
            
            elif choice == '2':
                # Replace with JSON
                print(f"\nEnter new state as JSON (press Enter twice when done):")
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
                    print(f"✅ State updated from JSON")
                    break
                except json.JSONDecodeError as e:
                    print(f"❌ Invalid JSON: {str(e)}")
                    continue
            
            elif choice == '3':
                print("❌ Edit cancelled")
                return
            
            else:
                print("❌ Invalid choice. Please select 1-3.")
        
        # Save updated state
        if self.save_local_state(local_state):
            print(f"\n✅ Local state updated and saved")
            print(f"📊 New state: {json.dumps(local_state, indent=2)}")
            
            # Ask if user wants to report to shadow
            report = input("\nReport updated state to shadow? (y/N): ").strip().lower()
            if report == 'y':
                self.update_shadow_reported(local_state, debug=self.debug_mode)
        else:
            print(f"❌ Failed to save local state")
    
    def show_shadow_diagnostics(self):
        """Show detailed shadow connection and state diagnostics"""
        print(f"\n🔍 Shadow Connection Diagnostics")
        print(f"=" * 60)
        
        print(f"📡 Connection Status:")
        print(f"   • Connected: {'✅ Yes' if self.connected else '❌ No'}")
        print(f"   • Thing Name: {self.thing_name}")
        print(f"   • Shadow Type: Classic Shadow")
        print(f"   • Messages Received: {len(self.received_messages)}")
        
        if self.local_state_file:
            print(f"\n📱 Local Device State:")
            print(f"   • State File: {self.local_state_file}")
            print(f"   • File Exists: {'✅ Yes' if os.path.exists(self.local_state_file) else '❌ No'}")
            
            if os.path.exists(self.local_state_file):
                try:
                    local_state = self.load_local_state()
                    print(f"   • Current State: {json.dumps(local_state, indent=6)}")
                except Exception as e:
                    print(f"   • Error reading state: {str(e)}")
        
        print(f"\n🌟 Shadow Topics:")
        shadow_topics = [
            f"$aws/things/{self.thing_name}/shadow/get",
            f"$aws/things/{self.thing_name}/shadow/get/accepted",
            f"$aws/things/{self.thing_name}/shadow/get/rejected",
            f"$aws/things/{self.thing_name}/shadow/update",
            f"$aws/things/{self.thing_name}/shadow/update/accepted",
            f"$aws/things/{self.thing_name}/shadow/update/rejected",
            f"$aws/things/{self.thing_name}/shadow/update/delta"
        ]
        
        for topic in shadow_topics:
            if 'get' in topic and topic.endswith('/get'):
                print(f"   📤 {topic} (publish to request shadow)")
            elif 'update' in topic and topic.endswith('/update'):
                print(f"   📤 {topic} (publish to update shadow)")
            else:
                print(f"   📥 {topic} (subscribed)")
        
        print(f"\n🔧 Troubleshooting:")
        print(f"1. Verify certificate is ACTIVE and attached to Thing")
        print(f"2. Check policy allows shadow operations (iot:GetThingShadow, iot:UpdateThingShadow)")
        print(f"3. Ensure Thing name matches exactly")
        print(f"4. Check AWS IoT logs in CloudWatch (if enabled)")
    
    def disconnect(self):
        """Disconnect from AWS IoT Core"""
        if self.connection and self.connected:
            print(f"\n🔌 Disconnecting from AWS IoT Core...")
            
            try:
                disconnect_future = self.connection.disconnect()
                disconnect_future.result()
                
                self.print_shadow_details("SHADOW DISCONNECTION", {
                    "Status": "Successfully disconnected from AWS IoT Core",
                    "Thing Name": self.thing_name,
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
        
        print("🌟 AWS IoT Device Shadow Explorer")
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
        
        print("Learn AWS IoT Device Shadow service through hands-on exploration.")
        print("This tool demonstrates:")
        print("• Shadow document structure (desired, reported, delta)")
        print("• Shadow MQTT topics and message patterns")
        print("• Local device state simulation and synchronization")
        print("• Interactive shadow management and troubleshooting")
        
        print("\n📚 LEARNING MOMENT: Device Shadow Service")
        print("AWS IoT Device Shadow is a JSON document that stores and retrieves current state information for a device. It acts as a bridge between your device and applications, enabling state synchronization even when devices are offline. Shadows contain desired state (what you want), reported state (current status), and delta (differences to resolve).")
        print("\n🔄 NEXT: We will explore shadow operations with a real device simulation")
        input("Press Enter to continue...")
        
        if debug_mode:
            print(f"\n🔍 DEBUG MODE ENABLED")
            print(f"• Enhanced AWS IoT API logging")
            print(f"• Detailed shadow message analysis")
            print(f"• Extended error diagnostics")
        else:
            print(f"\n💡 Tip: Use --debug or -d flag for enhanced logging")
        
        print("=" * 60)
        
        explorer = DeviceShadowExplorer()
        explorer.debug_mode = debug_mode
        
        try:
            # Get IoT endpoint
            endpoint = explorer.get_iot_endpoint(debug=debug_mode)
            if not endpoint:
                return
            
            # Select device and certificate
            thing_name, cert_file, key_file = explorer.select_device_and_certificate(debug=debug_mode)
            if not thing_name:
                return
            
            # Setup local state file
            explorer.setup_local_state_file(thing_name, debug=debug_mode)
            
            # Connect to AWS IoT
            if not explorer.connect_to_aws_iot(thing_name, cert_file, key_file, endpoint, debug=debug_mode):
                return
            
            # Subscribe to shadow topics
            if not explorer.subscribe_to_shadow_topics(debug=debug_mode):
                return
            
            # Interactive shadow management
            explorer.interactive_shadow_management()
            
        except KeyboardInterrupt:
            print(f"\n\n🛑 Interrupted by user")
        except Exception as e:
            print(f"\n❌ Unexpected error: {str(e)}")
            if debug_mode:
                import traceback
                traceback.print_exc()
        finally:
            # Always disconnect cleanly
            explorer.disconnect()
            print(f"\n👋 Device Shadow Explorer session ended")
    
    except KeyboardInterrupt:
        print(f"\n\n🛑 Interrupted by user")
        print(f"👋 Device Shadow Explorer session ended")

if __name__ == "__main__":
    main()