#!/usr/bin/env python3
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import boto3
import json
import time
import os
from botocore.exceptions import ClientError

# Global debug mode flag
DEBUG_MODE = True  # Default to True for educational purposes

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

def print_step(step, description):
    """Print step with formatting"""
    print(f"\n🔐 Step {step}: {description}")
    print("-" * 50)

def print_info(message, indent=0):
    """Print informational message with optional indent"""
    prefix = "   " * indent
    print(f"{prefix}ℹ️  {message}")

def safe_operation(func, operation_name, api_details=None, debug=None, **kwargs):
    """Execute operation with error handling and API details"""
    if debug is None:
        debug = DEBUG_MODE
    """Execute operation with error handling and API details"""
    if api_details and debug:
        print_api_details(*api_details)
    
    try:
        if debug:
            print(f"🔄 {operation_name}...")
            print(f"📥 Input: {json.dumps(kwargs, indent=2, default=str)}")
        else:
            print(f"🔄 {operation_name}...")
        
        response = func(**kwargs)
        
        if debug:
            print(f"✅ {operation_name} completed successfully")
            print(f"📤 Output: {json.dumps(response, indent=2, default=str)[:500]}{'...' if len(str(response)) > 500 else ''}")
        else:
            print(f"✅ {operation_name} completed")
        
        time.sleep(1 if debug else 0.5)  # nosemgrep: arbitrary-sleep
        return response
    except ClientError as e:
        print(f"❌ Error in {operation_name}: {e.response['Error']['Code']} - {e.response['Error']['Message']}")
        if debug:
            print(f"🔍 DEBUG: Full error response:")
            print(json.dumps(e.response, indent=2, default=str))
        time.sleep(0.5)  # nosemgrep: arbitrary-sleep
        return None
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        if debug:
            import traceback
            print(f"🔍 DEBUG: Full traceback:")
            traceback.print_exc()
        time.sleep(0.5)  # nosemgrep: arbitrary-sleep
        return None

def save_certificate_files(thing_name, cert_id, cert_pem, private_key, public_key):
    """Save certificate files to local folder structure"""
    # Create certificates directory structure
    base_dir = os.path.join(os.getcwd(), 'certificates', thing_name)
    os.makedirs(base_dir, exist_ok=True)
    
    # Save certificate files
    cert_file = os.path.join(base_dir, f'{cert_id}.crt')
    key_file = os.path.join(base_dir, f'{cert_id}.key')
    pub_file = os.path.join(base_dir, f'{cert_id}.pub')
    
    with open(cert_file, 'w', encoding='utf-8') as f:
        f.write(cert_pem)
    
    with open(key_file, 'w', encoding='utf-8') as f:
        f.write(private_key)
    
    with open(pub_file, 'w', encoding='utf-8') as f:
        f.write(public_key)
    
    print(f"   📄 Certificate: {cert_file}")
    print(f"   🔐 Private Key: {key_file}")
    print(f"   🔑 Public Key: {pub_file}")
    
    return base_dir

def check_existing_certificates(iot, thing_name):
    """Check if Thing already has certificates attached"""
    try:
        response = iot.list_thing_principals(thingName=thing_name)
        principals = response.get('principals', [])
        
        # Filter for certificate ARNs
        cert_arns = [p for p in principals if 'cert/' in p]
        
        if cert_arns:
            print(f"\n⚠️  Thing '{thing_name}' already has {len(cert_arns)} certificate(s) attached:")
            for i, cert_arn in enumerate(cert_arns, 1):
                cert_id = cert_arn.split('/')[-1]
                print(f"   {i}. Certificate ID: {cert_id}")
            
            return cert_arns
        
        return []
    
    except Exception as e:
        print(f"❌ Error checking existing certificates: {str(e)}")
        return []

def cleanup_certificate(iot, cert_arn, thing_name):
    """Remove certificate association and clean up"""
    cert_id = cert_arn.split('/')[-1]
    print(f"\n🧹 Cleaning up certificate {cert_id}...")
    
    # Detach policies
    try:
        policies = iot.list_attached_policies(target=cert_arn).get('policies', [])
        for policy in policies:
            safe_operation(
                iot.detach_policy,
                f"Detaching policy '{policy['policyName']}'",
                policyName=policy['policyName'],
                target=cert_arn
            )
    except Exception as e:
        print(f"❌ Error detaching policies: {str(e)}")
    
    # Detach from Thing
    safe_operation(
        iot.detach_thing_principal,
        f"Detaching certificate from {thing_name}",
        thingName=thing_name,
        principal=cert_arn
    )
    
    # Deactivate and delete certificate
    safe_operation(
        iot.update_certificate,
        "Deactivating certificate",
        certificateId=cert_id,
        newStatus='INACTIVE'
    )
    
    safe_operation(
        iot.delete_certificate,
        "Deleting certificate",
        certificateId=cert_id
    )
    
    # Remove local files if they exist
    cert_folder = os.path.join(os.getcwd(), 'certificates', thing_name)
    if os.path.exists(cert_folder):
        for file in os.listdir(cert_folder):
            if cert_id in file:
                file_path = os.path.join(cert_folder, file)
                os.remove(file_path)
                print(f"🗑️  Removed local file: {file_path}")
    
    print(f"✅ Certificate {cert_id} cleaned up successfully")

def create_certificate(iot, thing_name=None):
    """Create a new X.509 certificate and save locally"""
    print_step(1, "Creating X.509 Certificate")
    
    print_info("X.509 certificates are used for device authentication in AWS IoT")
    print_info("Each certificate contains a public/private key pair")
    time.sleep(1)  # nosemgrep: arbitrary-sleep
    
    api_details = (
        "create_keys_and_certificate",
        "POST",
        "/keys-and-certificate",
        "Creates a new X.509 certificate with public/private key pair",
        "setAsActive: true (activates certificate immediately)",
        "certificateArn, certificateId, certificatePem, keyPair (public/private keys)"
    )
    
    response = safe_operation(
        iot.create_keys_and_certificate,
        "Creating certificate and key pair",
        api_details,
        setAsActive=True
    )
    
    if response:
        cert_arn = response['certificateArn']
        cert_id = response['certificateId']
        cert_pem = response['certificatePem']
        private_key = response['keyPair']['PrivateKey']
        public_key = response['keyPair']['PublicKey']
        
        print(f"\n📋 Certificate Details:")
        print(f"   Certificate ID: {cert_id}")
        print(f"   Certificate ARN: {cert_arn}")
        print(f"   Status: ACTIVE")
        
        # Save certificate files locally
        if thing_name:
            cert_folder = save_certificate_files(thing_name, cert_id, cert_pem, private_key, public_key)
            print(f"\n💾 Certificate files saved to: {cert_folder}")
        
        print(f"\n🔑 Certificate Components Created:")
        print(f"   • Public Key (for AWS IoT)")
        print(f"   • Private Key (keep secure on device)")
        print(f"   • Certificate PEM (for device authentication)")
        
        return cert_arn, cert_id
    
    return None, None

def select_thing(iot):
    """Select a Thing for certificate creation"""
    print_info("Fetching available Things...")
    
    try:
        response = iot.list_things()
        things = response.get('things', [])
        
        if not things:
            print("❌ No Things found. Please run setup_sample_data.py first")
            return None
        
        while True:
            print(f"\n📱 Available Things ({len(things)} found):")
            
            # Show first 10 things
            display_count = min(len(things), 10)
            for i in range(display_count):
                thing = things[i]
                print(f"   {i+1}. {thing['thingName']} (Type: {thing.get('thingTypeName', 'None')})")
            
            if len(things) > 10:
                print(f"   ... and {len(things) - 10} more")
            
            print(f"\n📋 Options:")
            print(f"   • Enter number (1-{len(things)}) to select Thing")
            print(f"   • Type 'all' to see all Things")
            print(f"   • Type 'manual' to enter Thing name manually")
            
            choice = input("\nYour choice: ").strip()
            
            if choice.lower() == 'all':
                print(f"\n📱 All Things:")
                for i, thing in enumerate(things, 1):
                    print(f"   {i}. {thing['thingName']} (Type: {thing.get('thingTypeName', 'None')})")
                continue
            
            elif choice.lower() == 'manual':
                thing_name = input("Enter Thing name: ").strip()
                if thing_name:
                    # Verify Thing exists
                    try:
                        iot.describe_thing(thingName=thing_name)
                        print(f"✅ Thing '{thing_name}' found")
                        return thing_name
                    except ClientError:
                        print(f"❌ Thing '{thing_name}' not found")
                        continue
                else:
                    print("❌ Thing name cannot be empty")
                    continue
            
            else:
                try:
                    thing_index = int(choice) - 1
                    if 0 <= thing_index < len(things):
                        selected_thing = things[thing_index]['thingName']
                        print(f"✅ Selected Thing: {selected_thing}")
                        return selected_thing
                    else:
                        print(f"❌ Invalid selection. Please enter 1-{len(things)}")
                except ValueError:
                    print("❌ Please enter a valid number, 'all', or 'manual'")
    
    except Exception as e:
        print(f"❌ Error listing Things: {str(e)}")
        return None

def attach_certificate_to_thing(iot, cert_arn, target_thing_name):
    """Attach certificate to the designated Thing"""
    print_step(2, "Attaching Certificate to Thing")
    
    print_info("Certificates must be attached to Things for device authentication")
    print_info("This creates a secure relationship between the certificate and the IoT device")
    print_info(f"Certificate will be attached to: {target_thing_name}")
    time.sleep(1)  # nosemgrep: arbitrary-sleep
    
    # Check for existing certificates
    existing_certs = check_existing_certificates(iot, target_thing_name)
    if existing_certs:
        cleanup_choice = input("\nWould you like to remove existing certificates? (y/N): ").strip().lower()
        if cleanup_choice == 'y':
            for cert_arn_existing in existing_certs:
                cleanup_certificate(iot, cert_arn_existing, target_thing_name)
        else:
            print("Proceeding with multiple certificates attached to the same Thing...")
    
    print(f"\n🔗 Attaching certificate to Thing: {target_thing_name}")
    
    api_details = (
        "attach_thing_principal",
        "PUT",
        f"/things/{target_thing_name}/principals",
        "Attaches a certificate (principal) to a Thing for authentication",
        f"thingName: {target_thing_name}, principal: {cert_arn}",
        "Empty response on success"
    )
    
    response = safe_operation(
        iot.attach_thing_principal,
        f"Attaching certificate to {target_thing_name}",
        api_details,
        thingName=target_thing_name,
        principal=cert_arn
    )
    
    if response is not None:
        print(f"✅ Certificate successfully attached to {target_thing_name}")
        print_info("The Thing can now use this certificate for authentication", 1)
        return target_thing_name
    
    return None

def create_policy_interactive(iot):
    """Create IoT policy interactively or select existing"""
    print_step(3, "IoT Policy Management")
    
    print_info("IoT Policies define what actions a certificate can perform")
    print_info("You can create a new policy or use an existing one")
    time.sleep(1)  # nosemgrep: arbitrary-sleep
    
    # First, check if there are existing policies
    try:
        existing_policies = iot.list_policies().get('policies', [])
        if existing_policies:
            print(f"\n📋 Found {len(existing_policies)} existing policies:")
            for i, policy in enumerate(existing_policies, 1):
                print(f"   {i}. {policy['policyName']}")
            
            print(f"\n📝 Policy Options:")
            print(f"1. Use existing policy")
            print(f"2. Create new policy")
            
            while True:
                choice = input("\nSelect option (1-2): ").strip()
                if choice == '1':
                    # Select existing policy
                    while True:
                        try:
                            policy_choice = int(input(f"Select policy (1-{len(existing_policies)}): ")) - 1
                            if 0 <= policy_choice < len(existing_policies):
                                selected_policy = existing_policies[policy_choice]['policyName']
                                print(f"✅ Selected existing policy: {selected_policy}")
                                return selected_policy
                            else:
                                print("❌ Invalid selection")
                        except ValueError:
                            print("❌ Please enter a valid number")
                elif choice == '2':
                    break  # Continue to create new policy
                else:
                    print("❌ Please select 1 or 2")
        else:
            print(f"\n📝 No existing policies found. Creating new policy...")
    except Exception as e:
        print(f"⚠️  Error listing policies: {str(e)}")
        print(f"Proceeding to create new policy...")
    
    # Create new policy
    policy_name = None
    while True:
        policy_name = input("\nEnter new policy name: ").strip()
        if not policy_name:
            print("❌ Policy name is required")
            continue
        
        # Check if policy exists
        try:
            iot.get_policy(policyName=policy_name)
            print(f"⚠️  Policy '{policy_name}' already exists")
            choice = input("Would you like to use a different name? (y/N): ").strip().lower()
            if choice == 'y':
                continue
            else:
                print(f"✅ Using existing policy: {policy_name}")
                return policy_name
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                print(f"✅ Policy name '{policy_name}' is available")
                break
            else:
                print(f"❌ Error checking policy: {e.response['Error']['Message']}")
                continue
    
    print(f"\n📝 Policy Templates:")
    print(f"1. Basic Device Policy (connect, publish, subscribe)")
    print(f"2. Read-Only Policy (connect, subscribe only)")
    print(f"3. Custom Policy (enter your own JSON)")
    
    while True:
        choice = input("\nSelect policy template (1-3): ").strip()
        
        if choice == '1':
            policy_document = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": [
                            "iot:Connect",
                            "iot:Publish",
                            "iot:Subscribe",
                            "iot:Receive"
                        ],
                        "Resource": "*"
                    }
                ]
            }
            print(f"\n⚠️  Production Security Note:")
            print(f"   This policy uses 'Resource': '*' for demonstration purposes.")
            print(f"   In production, use specific resource ARNs and policy variables")
            print(f"   like ${{iot:Connection.Thing.ThingName}} to restrict device access")
            print(f"   to only their specific resources. Policy variables are beyond")
            print(f"   the scope of this basic learning path.")
            break
            
        elif choice == '2':
            policy_document = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": [
                            "iot:Connect",
                            "iot:Subscribe",
                            "iot:Receive"
                        ],
                        "Resource": "*"
                    }
                ]
            }
            print(f"\n⚠️  Production Security Note:")
            print(f"   This policy uses 'Resource': '*' for demonstration purposes.")
            print(f"   In production, use specific resource ARNs and policy variables")
            print(f"   like ${{iot:Connection.Thing.ThingName}} to restrict device access")
            print(f"   to only their specific resources. Policy variables are beyond")
            print(f"   the scope of this basic learning path.")
            break
            
        elif choice == '3':
                
            print("\nEnter your policy JSON (press Enter twice when done):")
            policy_lines = []
            while True:
                line = input()
                if line == "" and policy_lines and policy_lines[-1] == "":
                    break
                policy_lines.append(line)
            
            try:
                policy_text = "\n".join(policy_lines[:-1])  # Remove last empty line
                policy_document = json.loads(policy_text)
                break
            except json.JSONDecodeError as e:
                print(f"❌ Invalid JSON: {str(e)}")
                continue
        else:
            print("❌ Invalid choice. Please select 1-3.")
    
    print(f"\n📄 Policy to be created:")
    print(f"   Name: {policy_name}")
    print(f"   Document: {json.dumps(policy_document, indent=2)}")
    
    api_details = (
        "create_policy",
        "PUT",
        f"/policies/{policy_name}",
        "Creates a new IoT policy with specified permissions",
        f"policyName: {policy_name}, policyDocument: JSON policy document",
        "policyName, policyArn, policyDocument, policyVersionId"
    )
    
    response = safe_operation(
        iot.create_policy,
        f"Creating policy '{policy_name}'",
        api_details,
        policyName=policy_name,
        policyDocument=json.dumps(policy_document)
    )
    
    if response:
        print(f"✅ Policy '{policy_name}' created successfully")
        return policy_name
    
    return None

def attach_policy_to_certificate(iot, cert_arn, policy_name=None):
    """Attach policy to certificate"""
    print_step(4, "Attaching Policy to Certificate")
    
    print_info("Policies must be attached to certificates to grant permissions")
    print_info("Without a policy, the certificate cannot perform any IoT operations")
    time.sleep(1)  # nosemgrep: arbitrary-sleep
    
    if not policy_name:
        # List existing policies
        try:
            policies = iot.list_policies().get('policies', [])
            if policies:
                print(f"\n📋 Available Policies:")
                for i, policy in enumerate(policies, 1):
                    print(f"   {i}. {policy['policyName']}")
                
                while True:
                    try:
                        choice = int(input(f"\nSelect policy (1-{len(policies)}): ")) - 1
                        if 0 <= choice < len(policies):
                            policy_name = policies[choice]['policyName']
                            break
                        else:
                            print("❌ Invalid selection")
                    except ValueError:
                        print("❌ Please enter a valid number")
            else:
                print("❌ No policies found. Creating one first...")
                policy_name = create_policy_interactive(iot)
                if not policy_name:
                    return False
        except Exception as e:
            print(f"❌ Error listing policies: {str(e)}")
            return False
    
    print(f"\n🔗 Attaching policy '{policy_name}' to certificate")
    
    api_details = (
        "attach_policy",
        "PUT",
        f"/target-policies/{policy_name}",
        "Attaches an IoT policy to a certificate to grant permissions",
        f"policyName: {policy_name}, target: {cert_arn}",
        "Empty response on success"
    )
    
    response = safe_operation(
        iot.attach_policy,
        f"Attaching policy to certificate",
        api_details,
        policyName=policy_name,
        target=cert_arn
    )
    
    if response is not None:
        print(f"✅ Policy '{policy_name}' attached to certificate")
        print_info("Certificate now has the permissions defined in the policy", 1)
        return True
    
    return False

def print_summary(cert_id, cert_arn, thing_name, policy_name):
    """Print setup summary"""
    print_step(5, "Setup Complete! 🎉")
    
    print(f"📊 Summary of what was created:")
    print(f"   🔐 Certificate ID: {cert_id}")
    print(f"   📱 Attached to Thing: {thing_name}")
    print(f"   📄 Policy Attached: {policy_name}")
    
    print(f"\n🔍 What you can explore now:")
    print(f"   • Use iot_registry_explorer.py to view the certificate")
    print(f"   • Check the Thing to see its attached certificate")
    print(f"   • Review the policy permissions")
    
    print(f"\n💡 Key Learning Points:")
    print(f"   • Certificates provide device identity and authentication")
    print(f"   • Things represent your IoT devices in AWS")
    print(f"   • Policies define what actions certificates can perform")
    print(f"   • All three work together for secure IoT communication")

def print_api_details(operation, method, path, description, inputs=None, outputs=None):
    """Print detailed API information for learning"""
    print(f"\n🔍 API Details:")
    print(f"   Operation: {operation}")
    print(f"   HTTP Method: {method}")
    print(f"   API Path: {path}")
    print(f"   Description: {description}")
    if inputs:
        print(f"   Input Parameters: {inputs}")
    if outputs:
        print(f"   Expected Output: {outputs}")
    time.sleep(1)  # nosemgrep: arbitrary-sleep

def get_thing_certificates(iot, thing_name):
    """Get certificates attached to a Thing"""
    print_api_details(
        "list_thing_principals",
        "GET",
        f"/things/{thing_name}/principals",
        "Lists all principals (certificates) attached to a specific Thing",
        f"thingName: {thing_name}",
        "Array of principal ARNs (certificate ARNs)"
    )
    
    try:
        response = iot.list_thing_principals(thingName=thing_name)
        principals = response.get('principals', [])
        cert_arns = [p for p in principals if 'cert/' in p]
        
        print(f"📤 API Response: Found {len(cert_arns)} certificate(s)")
        for cert_arn in cert_arns:
            cert_id = cert_arn.split('/')[-1]
            print(f"   Certificate ID: {cert_id}")
        
        return cert_arns
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return []

def certificate_status_workflow(iot):
    """Workflow to enable/disable certificates"""
    print("\n🔄 Certificate Status Management")
    print("=" * 40)
    print("🎓 Learning Objectives:")
    print("• Understand certificate lifecycle management")
    print("• Learn enable/disable operations")
    print("• Practice certificate status control")
    print("• Explore update_certificate API")
    print("=" * 40)
    
    # List all certificates
    print(f"\n🔍 Fetching all certificates...")
    
    api_details = (
        "list_certificates",
        "GET",
        "/certificates",
        "Lists all X.509 certificates in your AWS account",
        "None (optional: pageSize, marker, ascendingOrder)",
        "Array of certificate objects with IDs, ARNs, status, creation dates"
    )
    
    response = safe_operation(
        iot.list_certificates,
        "Listing all certificates",
        api_details
    )
    
    if not response:
        print("❌ Failed to list certificates")
        return
    
    certificates = response.get('certificates', [])
    
    if not certificates:
        print("📋 No certificates found in your account")
        print("💡 Create certificates first using options 1 or 2")
        return
    
    print(f"\n📋 Found {len(certificates)} certificate(s):")
    
    # Get Thing associations for each certificate
    cert_thing_map = {}
    for cert in certificates:
        cert_arn = cert['certificateArn']
        try:
            # Find Things associated with this certificate
            things_response = iot.list_principal_things(principal=cert_arn)
            things = things_response.get('things', [])
            cert_thing_map[cert['certificateId']] = things[0] if things else None
        except Exception:
            cert_thing_map[cert['certificateId']] = None
    
    for i, cert in enumerate(certificates, 1):
        status_icon = "🟢" if cert['status'] == 'ACTIVE' else "🔴"
        thing_name = cert_thing_map.get(cert['certificateId'])
        thing_info = f" → {thing_name}" if thing_name else " (No Thing attached)"
        print(f"   {i}. {cert['certificateId'][:16]}...{thing_info} - {status_icon} {cert['status']}")
        print(f"      Created: {cert.get('creationDate', 'Unknown')}")
    
    # Select certificate
    while True:
        try:
            choice = int(input(f"\nSelect certificate (1-{len(certificates)}): ")) - 1
            if 0 <= choice < len(certificates):
                selected_cert = certificates[choice]
                break
            else:
                print("❌ Invalid selection")
        except ValueError:
            print("❌ Please enter a valid number")
    
    cert_id = selected_cert['certificateId']
    current_status = selected_cert['status']
    
    thing_name = cert_thing_map.get(cert_id)
    print(f"\n📝 Selected Certificate:")
    print(f"   ID: {cert_id}")
    print(f"   Attached to Thing: {thing_name or 'None'}")
    print(f"   Current Status: {current_status}")
    print(f"   ARN: {selected_cert.get('certificateArn', 'N/A')}")
    
    # Determine action based on current status
    if current_status == 'ACTIVE':
        new_status = 'INACTIVE'
        action = "disable"
        icon = "🔴"
    else:
        new_status = 'ACTIVE'
        action = "enable"
        icon = "🟢"
    
    print(f"\n🔄 Available Action:")
    print(f"   {icon} {action.title()} certificate (set status to {new_status})")
    
    confirm = input(f"\nDo you want to {action} this certificate? (y/N): ").strip().lower()
    
    if confirm != 'y':
        print("❌ Operation cancelled")
        return
    
    # Update certificate status
    api_details = (
        "update_certificate",
        "PUT",
        f"/certificates/{cert_id}",
        "Updates the status of an X.509 certificate",
        f"certificateId: {cert_id}, newStatus: {new_status}",
        "Empty response on success"
    )
    
    response = safe_operation(
        iot.update_certificate,
        f"{action.title()}ing certificate",
        api_details,
        certificateId=cert_id,
        newStatus=new_status
    )
    
    if response is not None:
        print(f"\n✅ Certificate {action}d successfully!")
        print(f"\n📊 Status Change Summary:")
        print(f"   Certificate ID: {cert_id}")
        print(f"   Attached to Thing: {thing_name or 'None'}")
        print(f"   Previous Status: {current_status}")
        print(f"   New Status: {new_status}")
        
        print(f"\n💡 What this means:")
        if new_status == 'ACTIVE':
            print(f"   • Certificate can now be used for device authentication")
            print(f"   • Devices with this certificate can connect to AWS IoT")
            print(f"   • MQTT connections using this certificate will succeed")
        else:
            print(f"   • Certificate is now disabled for authentication")
            print(f"   • Devices with this certificate cannot connect to AWS IoT")
            print(f"   • MQTT connections using this certificate will fail")
        
        print(f"\n🔍 Next Steps:")
        print(f"   • Use iot_registry_explorer.py to verify the status change")
        print(f"   • Test MQTT connection to see the effect")
        if new_status == 'INACTIVE':
            print(f"   • Re-enable when ready to restore device connectivity")
    else:
        print(f"❌ Failed to {action} certificate")

def attach_policy_workflow(iot):
    """Workflow to attach policy to existing certificate"""
    print("\n🔗 Policy Attachment Workflow")
    print("=" * 40)
    
    # Select Thing
    selected_thing = select_thing(iot)
    if not selected_thing:
        return
    
    # Get certificates for the Thing
    print(f"\n🔍 Checking certificates for Thing: {selected_thing}")
    cert_arns = get_thing_certificates(iot, selected_thing)
    
    if not cert_arns:
        print(f"❌ No certificates found for Thing '{selected_thing}'")
        print("💡 Tip: Run option 1 first to create and attach a certificate")
        return
    
    # Select certificate if multiple
    if len(cert_arns) == 1:
        selected_cert_arn = cert_arns[0]
        cert_id = selected_cert_arn.split('/')[-1]
        print(f"✅ Using certificate: {cert_id}")
    else:
        print(f"\n📋 Multiple certificates found:")
        for i, cert_arn in enumerate(cert_arns, 1):
            cert_id = cert_arn.split('/')[-1]
            print(f"   {i}. {cert_id}")
        
        while True:
            try:
                choice = int(input(f"Select certificate (1-{len(cert_arns)}): ")) - 1
                if 0 <= choice < len(cert_arns):
                    selected_cert_arn = cert_arns[choice]
                    break
                else:
                    print("❌ Invalid selection")
            except ValueError:
                print("❌ Please enter a valid number")
    
    # Create or select policy
    policy_name = create_policy_interactive(iot)
    if policy_name:
        attach_policy_to_certificate(iot, selected_cert_arn, policy_name)
        print(f"\n🎉 Policy '{policy_name}' attached to certificate for Thing '{selected_thing}'")

def detach_policy_workflow(iot):
    """Workflow to detach policy from certificate"""
    print("\n🔓 Policy Detachment Workflow")
    print("=" * 40)
    print("🎓 Learning Objectives:")
    print("• Understand policy detachment process")
    print("• Learn to find devices by policy")
    print("• Practice certificate-policy relationship management")
    print("• Explore detach_policy API")
    print("=" * 40)
    
    # Step 1: List all policies
    print(f"\n🔍 Fetching all policies...")
    
    api_details = (
        "list_policies",
        "GET",
        "/policies",
        "Lists all IoT policies in your AWS account",
        "None (optional: marker, pageSize, ascendingOrder)",
        "Array of policy objects with names and ARNs"
    )
    
    response = safe_operation(
        iot.list_policies,
        "Listing all policies",
        api_details
    )
    
    if not response:
        print("❌ Failed to list policies")
        return
    
    policies = response.get('policies', [])
    
    if not policies:
        print("📋 No policies found in your account")
        print("💡 Create policies first using options 1, 2, or 3")
        return
    
    # Step 2: Select policy
    print(f"\n📋 Found {len(policies)} policy(ies):")
    for i, policy in enumerate(policies, 1):
        print(f"   {i}. {policy['policyName']}")
    
    while True:
        try:
            choice = int(input(f"\nSelect policy to detach (1-{len(policies)}): ")) - 1
            if 0 <= choice < len(policies):
                selected_policy = policies[choice]['policyName']
                break
            else:
                print("❌ Invalid selection")
        except ValueError:
            print("❌ Please enter a valid number")
    
    print(f"\n✅ Selected policy: {selected_policy}")
    
    # Step 3: Find certificates with this policy attached
    print(f"\n🔍 Finding certificates with policy '{selected_policy}' attached...")
    
    api_details = (
        "list_targets_for_policy",
        "POST",
        f"/targets-for-policy/{selected_policy}",
        "Lists all targets (certificates) that have the specified policy attached",
        f"policyName: {selected_policy}",
        "Array of target ARNs (certificate ARNs)"
    )
    
    response = safe_operation(
        iot.list_targets_for_policy,
        f"Finding targets for policy '{selected_policy}'",
        api_details,
        policyName=selected_policy
    )
    
    if not response:
        print("❌ Failed to list policy targets")
        return
    
    targets = response.get('targets', [])
    cert_targets = [t for t in targets if 'cert/' in t]
    
    if not cert_targets:
        print(f"📋 No certificates found with policy '{selected_policy}' attached")
        print("💡 This policy is not currently attached to any certificates")
        return
    
    # Step 4: Get Thing associations for each certificate
    print(f"\n📋 Found {len(cert_targets)} certificate(s) with this policy:")
    cert_thing_map = {}
    
    for i, cert_arn in enumerate(cert_targets, 1):
        cert_id = cert_arn.split('/')[-1]
        
        # Find Things associated with this certificate
        try:
            things_response = iot.list_principal_things(principal=cert_arn)
            things = things_response.get('things', [])
            thing_name = things[0] if things else None
            cert_thing_map[cert_arn] = thing_name
            
            thing_info = f" → {thing_name}" if thing_name else " (No Thing attached)"
            print(f"   {i}. {cert_id[:16]}...{thing_info}")
        except Exception as e:
            print(f"   {i}. {cert_id[:16]}... (Error getting Thing: {str(e)})")
            cert_thing_map[cert_arn] = None
    
    # Step 5: Select certificate
    while True:
        try:
            choice = int(input(f"\nSelect certificate to detach policy from (1-{len(cert_targets)}): ")) - 1
            if 0 <= choice < len(cert_targets):
                selected_cert_arn = cert_targets[choice]
                break
            else:
                print("❌ Invalid selection")
        except ValueError:
            print("❌ Please enter a valid number")
    
    selected_cert_id = selected_cert_arn.split('/')[-1]
    thing_name = cert_thing_map.get(selected_cert_arn)
    
    print(f"\n📝 Detachment Summary:")
    print(f"   Policy: {selected_policy}")
    print(f"   Certificate ID: {selected_cert_id}")
    print(f"   Attached to Thing: {thing_name or 'None'}")
    
    # Step 6: Confirm detachment
    confirm = input(f"\nDetach policy '{selected_policy}' from this certificate? (y/N): ").strip().lower()
    
    if confirm != 'y':
        print("❌ Operation cancelled")
        return
    
    # Step 7: Detach policy
    api_details = (
        "detach_policy",
        "POST",
        f"/target-policies/{selected_policy}",
        "Detaches an IoT policy from a certificate target",
        f"policyName: {selected_policy}, target: {selected_cert_arn}",
        "Empty response on success"
    )
    
    response = safe_operation(
        iot.detach_policy,
        f"Detaching policy from certificate",
        api_details,
        policyName=selected_policy,
        target=selected_cert_arn
    )
    
    if response is not None:
        print(f"\n✅ Policy detached successfully!")
        print(f"\n📊 Detachment Results:")
        print(f"   Policy '{selected_policy}' removed from certificate {selected_cert_id}")
        if thing_name:
            print(f"   Thing '{thing_name}' certificate no longer has this policy")
        
        print(f"\n💡 What this means:")
        print(f"   • Certificate can no longer perform actions defined in '{selected_policy}'")
        print(f"   • Device may lose specific permissions (connect, publish, subscribe)")
        print(f"   • Other policies attached to this certificate still apply")
        print(f"   • Policy still exists and can be attached to other certificates")
        
        print(f"\n🔍 Next Steps:")
        print(f"   • Use iot_registry_explorer.py to verify policy detachment")
        print(f"   • Test device connectivity to see permission changes")
        print(f"   • Attach different policy if needed using option 3")
    else:
        print(f"❌ Failed to detach policy")

def certificate_creation_workflow(iot):
    """Full workflow for certificate creation and attachment"""
    print("\n🔐 Certificate Creation Workflow")
    print("=" * 40)
    
    # Select Thing first
    selected_thing = select_thing(iot)
    if not selected_thing:
        return
    
    print("\n📚 LEARNING MOMENT: Certificate Creation Process")
    print("We will now create an X.509 certificate using AWS IoT's certificate authority. This generates a unique public/private key pair where AWS keeps the public key and provides you with both the certificate and private key for your device.")
    print("\n🔄 NEXT: Creating certificate with AWS IoT")
    input("Press Enter to continue...")
    
    cert_arn, cert_id = create_certificate(iot, selected_thing)
    if not cert_arn:
        print("❌ Failed to create certificate. Exiting.")
        return
    
    print("\n📚 LEARNING MOMENT: Certificate-Thing Attachment")
    print("Now we'll attach the certificate to your selected Thing. This creates the secure binding between the certificate identity and the logical device representation in AWS IoT. Once attached, the device can use this certificate to authenticate with AWS IoT Core.")
    print("\n🔄 NEXT: Attaching certificate to Thing")
    input("Press Enter to continue...")
    
    thing_name = attach_certificate_to_thing(iot, cert_arn, selected_thing)
    if not thing_name:
        print("❌ Failed to attach certificate to Thing. Exiting.")
        return
    
    # Ask about policy
    create_policy = input("\nWould you like to create and attach a policy? (y/N): ").strip().lower()
    policy_name = None
    
    if create_policy == 'y':
        policy_name = create_policy_interactive(iot)
        if policy_name:
            attach_policy_to_certificate(iot, cert_arn, policy_name)
    else:
        attach_existing = input("Would you like to attach an existing policy? (y/N): ").strip().lower()
        if attach_existing == 'y':
            if attach_policy_to_certificate(iot, cert_arn):
                policy_name = "Existing Policy"
    
    print_summary(cert_id, cert_arn, thing_name, policy_name or "None", "AWS-Generated")

def generate_sample_certificate():
    """Generate a sample certificate using OpenSSL for learning"""
    print_step("OpenSSL", "Generate Sample Certificate with OpenSSL")
    
    print_info("This creates a self-signed certificate for learning purposes")
    print_info("In production, use certificates from a trusted Certificate Authority")
    time.sleep(1)  # nosemgrep: arbitrary-sleep
    
    # Create sample-certs directory
    sample_dir = os.path.join(os.getcwd(), 'sample-certs')
    os.makedirs(sample_dir, exist_ok=True)
    
    cert_name = input("\nEnter certificate name [default: sample-device]: ").strip() or "sample-device"
    
    # Validate certificate name to prevent command injection
    import re
    import shlex
    if not re.match(r'^[a-zA-Z0-9_-]+$', cert_name):
        print("❌ Certificate name can only contain letters, numbers, hyphens, and underscores")
        return None, None
    
    key_file = os.path.join(sample_dir, f'{cert_name}.key')
    cert_file = os.path.join(sample_dir, f'{cert_name}.crt')
    
    print(f"\n🔑 Generating certificate files:")
    print(f"   Private Key: {key_file}")
    print(f"   Certificate: {cert_file}")
    
    # OpenSSL command to generate private key and certificate
    openssl_cmd = [
        'openssl', 'req', '-x509', '-newkey', 'rsa:2048',
        '-keyout', key_file,
        '-out', cert_file,
        '-days', '365',
        '-nodes',
        '-subj', f'/CN={cert_name}/O=AWS IoT Learning/C=US'
    ]
    
    try:
        print(f"\n🔄 Running OpenSSL command...")
        print(f"📥 Command: {' '.join(openssl_cmd)}")
        
        import subprocess
        result = subprocess.run(openssl_cmd, capture_output=True, text=True, shell=False)  # nosemgrep: dangerous-subprocess-use-audit
        
        if result.returncode == 0:
            print(f"✅ Certificate generated successfully")
            print(f"\n📊 Certificate Details:")
            print(f"   • Type: Self-signed X.509")
            print(f"   • Key Size: 2048-bit RSA")
            print(f"   • Validity: 365 days")
            print(f"   • Subject: CN={cert_name}, O=AWS IoT Learning, C=US")
            
            # Show certificate info
            info_cmd = ['openssl', 'x509', '-in', cert_file, '-text', '-noout']
            info_result = subprocess.run(info_cmd, capture_output=True, text=True, shell=False)  # nosemgrep: dangerous-subprocess-use-audit
            if info_result.returncode == 0:
                print(f"\n🔍 Certificate Information:")
                lines = info_result.stdout.split('\n')
                for line in lines[:10]:  # Show first 10 lines
                    if line.strip():
                        print(f"   {line.strip()}")
                print("   ...")
            
            return cert_file
        else:
            print(f"❌ OpenSSL error: {result.stderr}")
            return None
            
    except FileNotFoundError:
        print("❌ OpenSSL not found. Please install OpenSSL:")
        print("   macOS: brew install openssl")
        print("   Ubuntu: sudo apt-get install openssl")
        print("   Windows: Download from https://slproweb.com/products/Win32OpenSSL.html")
        return None
    except Exception as e:
        print(f"❌ Error generating certificate: {str(e)}")
        return None

def get_certificate_file_path():
    """Get certificate file path from user with options"""
    print_info("Choose how to provide your X.509 certificate:")
    print("\n📋 Certificate Options:")
    print("1. Use existing certificate file")
    print("2. Generate sample certificate with OpenSSL")
    
    while True:
        choice = input("\nSelect option (1-2): ").strip()
        
        if choice == '1':
            return get_existing_certificate_path()
        elif choice == '2':
            return generate_sample_certificate()
        else:
            print("❌ Invalid choice. Please select 1-2.")

def get_existing_certificate_path():
    """Get path to existing certificate file"""
    print_info("Certificate must be in PEM format (.crt or .pem file)")
    print_info("PEM format starts with '-----BEGIN CERTIFICATE-----'")
    
    while True:
        cert_path = input("\nEnter path to certificate file: ").strip()
        if not cert_path:
            print("❌ Certificate path is required")
            continue
        
        if not os.path.exists(cert_path):
            print(f"❌ File not found: {cert_path}")
            continue
        
        if not cert_path.lower().endswith(('.crt', '.pem')):
            print("⚠️  Warning: File doesn't have .crt or .pem extension")
            confirm = input("Continue anyway? (y/N): ").strip().lower()
            if confirm != 'y':
                continue
        
        return cert_path

def validate_certificate_file(cert_path):
    """Validate certificate file format with detailed feedback"""
    print_info("Validating certificate file format...")
    
    try:
        with open(cert_path, 'r', encoding='utf-8') as f:
            cert_content = f.read()
        
        print(f"📥 Certificate file content preview:")
        lines = cert_content.split('\n')
        for i, line in enumerate(lines[:5]):
            print(f"   Line {i+1}: {line[:60]}{'...' if len(line) > 60 else ''}")
        if len(lines) > 5:
            print(f"   ... and {len(lines) - 5} more lines")
        
        # Basic PEM format validation
        if not cert_content.startswith('-----BEGIN CERTIFICATE-----'):
            print("❌ Invalid certificate format. Must be PEM format starting with '-----BEGIN CERTIFICATE-----'")
            print("💡 Tip: Convert DER to PEM using: openssl x509 -inform DER -outform PEM -in cert.der -out cert.pem")
            return False
        
        if not cert_content.strip().endswith('-----END CERTIFICATE-----'):
            print("❌ Invalid certificate format. Must end with '-----END CERTIFICATE-----'")
            return False
        
        # Count certificate sections
        cert_count = cert_content.count('-----BEGIN CERTIFICATE-----')
        print(f"📊 Certificate validation results:")
        print(f"   • Format: PEM ✅")
        print(f"   • Certificate count: {cert_count}")
        print(f"   • File size: {len(cert_content)} bytes")
        
        if cert_count > 1:
            print("⚠️  Multiple certificates found. Only the first will be used.")
        
        print("✅ Certificate file format validated")
        return True
        
    except Exception as e:
        print(f"❌ Error reading certificate file: {str(e)}")
        return False

def register_certificate_with_aws(iot, cert_path):
    """Register external certificate with AWS IoT with detailed API learning"""
    try:
        with open(cert_path, 'r', encoding='utf-8') as f:
            cert_pem = f.read()
        
        print_info("Registering external certificate with AWS IoT...")
        print_info("This registers your certificate without AWS generating new keys")
        print_info("Your private key stays with you - AWS only gets the public certificate")
        time.sleep(1)  # nosemgrep: arbitrary-sleep
        
        api_details = (
            "register_certificate_without_ca",
            "POST", 
            "/certificate/register-no-ca",
            "Registers a self-signed X.509 certificate without requiring CA registration",
            "certificatePem: <PEM-encoded-certificate>, status: ACTIVE",
            "certificateArn, certificateId"
        )
        
        response = safe_operation(
            iot.register_certificate_without_ca,
            "Registering self-signed certificate with AWS IoT",
            api_details,
            certificatePem=cert_pem,
            status='ACTIVE'
        )
        
        if response:
            cert_arn = response['certificateArn']
            cert_id = response['certificateId']
            
            print(f"\n📋 Certificate Registration Results:")
            print(f"   Certificate ID: {cert_id}")
            print(f"   Certificate ARN: {cert_arn}")
            print(f"   Status: ACTIVE")
            print(f"   Source: External (user-provided)")
            print(f"   Registration Method: register_certificate API")
            
            print(f"\n🔄 What happened:")
            print(f"   1. AWS IoT validated your certificate format")
            print(f"   2. Self-signed certificate registered without CA requirement")
            print(f"   3. Certificate status set to ACTIVE")
            print(f"   4. AWS assigned unique Certificate ID and ARN")
            print(f"   5. Certificate is now ready for Thing attachment")
            
            print(f"\n💡 Key Difference:")
            print(f"   • Used register_certificate_without_ca API")
            print(f"   • No Certificate Authority (CA) registration required")
            print(f"   • Perfect for self-signed certificates and learning")
            print(f"   • Production systems typically use CA-signed certificates")
            
            return cert_arn, cert_id, cert_pem
        
        return None, None, None
        
    except Exception as e:
        print(f"❌ Error registering certificate: {str(e)}")
        return None, None, None

def register_external_certificate_workflow(iot):
    """Complete workflow for registering external certificate"""
    print("\n📜 External Certificate Registration Workflow")
    print("=" * 50)
    print("🎓 Learning Objectives:")
    print("• Understand difference between AWS-generated vs external certificates")
    print("• Learn certificate registration process")
    print("• Practice certificate validation and attachment")
    print("• Explore register_certificate API")
    print("=" * 50)
    
    # Step 1: Get certificate file
    cert_path = get_certificate_file_path()
    if not cert_path:
        print("❌ Certificate file required. Exiting workflow.")
        return
    
    # Step 2: Validate certificate
    if not validate_certificate_file(cert_path):
        print("❌ Certificate validation failed. Exiting workflow.")
        return
    
    # Step 3: Select Thing first
    selected_thing = select_thing(iot)
    if not selected_thing:
        print("❌ Thing selection required. Exiting workflow.")
        return
    
    print("\n📚 LEARNING MOMENT: External Certificate Registration")
    print("We will now register your external certificate with AWS IoT. Unlike AWS-generated certificates, this process registers your existing certificate without AWS creating new keys. Your private key remains under your control while AWS validates and registers the public certificate.")
    print("\n🔄 NEXT: Registering certificate with AWS IoT")
    input("Press Enter to continue...")
    
    # Step 4: Register certificate with AWS IoT
    cert_arn, cert_id, cert_pem = register_certificate_with_aws(iot, cert_path)
    if not cert_arn:
        print("❌ Certificate registration failed. Exiting workflow.")
        return
    
    # Step 4.5: Save certificate files locally for MQTT client use
    print(f"\n💾 Saving certificate files locally for MQTT client...")
    cert_dir = f"certificates/{selected_thing}"
    os.makedirs(cert_dir, exist_ok=True)
    
    # Save certificate file
    cert_file = f"{cert_dir}/{cert_id}.crt"
    with open(cert_file, 'w', encoding='utf-8') as f:
        f.write(cert_pem)
    print(f"📄 Certificate saved: {cert_file}")
    
    # Handle private key file
    key_file = f"{cert_dir}/{cert_id}.key"
    if cert_path.endswith('.crt') or cert_path.endswith('.pem'):
        # Look for corresponding key file
        key_path = cert_path.replace('.crt', '.key').replace('.pem', '.key')
        if os.path.exists(key_path):
            print(f"🔍 Found corresponding private key: {key_path}")
            with open(key_path, 'r', encoding='utf-8') as f:
                key_content = f.read()
            with open(key_file, 'w', encoding='utf-8') as f:
                f.write(key_content)
            print(f"🔑 Private key saved: {key_file}")
        else:
            print(f"⚠️  Private key not found at: {key_path}")
            manual_key = input("Enter path to private key file (or press Enter to skip): ").strip()
            if manual_key and os.path.exists(manual_key):
                with open(manual_key, 'r', encoding='utf-8') as f:
                    key_content = f.read()
                with open(key_file, 'w', encoding='utf-8') as f:
                    f.write(key_content)
                print(f"🔑 Private key saved: {key_file}")
            else:
                print("⚠️  Private key not saved - MQTT client may not work")
    
    print(f"💾 Certificate files saved to: {cert_dir}")
    
    print("\n📚 LEARNING MOMENT: Certificate-Thing Attachment")
    print("Now we'll attach your registered certificate to the selected Thing. This creates the secure binding between your external certificate and the logical device representation in AWS IoT, enabling the device to authenticate using your existing certificate.")
    print("\n🔄 NEXT: Attaching certificate to Thing")
    input("Press Enter to continue...")
    
    # Step 5: Attach certificate to Thing
    thing_name = attach_certificate_to_thing(iot, cert_arn, selected_thing)
    if not thing_name:
        print("❌ Certificate attachment failed. Exiting workflow.")
        return
    
    # Step 6: Optional policy attachment
    create_policy = input("\nWould you like to create and attach a policy? (y/N): ").strip().lower()
    policy_name = None
    
    if create_policy == 'y':
        policy_name = create_policy_interactive(iot)
        if policy_name:
            attach_policy_to_certificate(iot, cert_arn, policy_name)
    else:
        attach_existing = input("Would you like to attach an existing policy? (y/N): ").strip().lower()
        if attach_existing == 'y':
            if attach_policy_to_certificate(iot, cert_arn):
                policy_name = "Existing Policy"
    
    # Step 7: Summary
    print_summary(cert_id, cert_arn, thing_name, policy_name or "None", "External")

def print_summary(cert_id, cert_arn, thing_name, policy_name, cert_source="AWS-Generated"):
    """Print enhanced setup summary with certificate source"""
    print_step("Final", "Setup Complete! 🎉")
    
    print(f"📊 Summary of what was created/configured:")
    print(f"   🔐 Certificate ID: {cert_id}")
    print(f"   🏷️  Certificate Source: {cert_source}")
    print(f"   📱 Attached to Thing: {thing_name}")
    print(f"   📄 Policy Attached: {policy_name}")
    
    print(f"\n🔍 What you can explore now:")
    print(f"   • Use iot_registry_explorer.py to view the certificate")
    print(f"   • Check the Thing to see its attached certificate")
    print(f"   • Review the policy permissions")
    if cert_source == "External":
        print(f"   • Compare external vs AWS-generated certificate workflows")
    
    print(f"\n💡 Key Learning Points:")
    print(f"   • Certificates provide device identity and authentication")
    print(f"   • Things represent your IoT devices in AWS")
    print(f"   • Policies define what actions certificates can perform")
    if cert_source == "External":
        print(f"   • External certificates integrate with existing PKI infrastructure")
        print(f"   • register_certificate API vs create_keys_and_certificate API")
    print(f"   • All components work together for secure IoT communication")

def main():
    import sys
    
    try:
        # Check for debug flag
        debug_mode = '--debug' in sys.argv or '-d' in sys.argv
        
        print("🔐 AWS IoT Certificate & Policy Manager")
        print("=" * 50)
        
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
        
        print("This script teaches you AWS IoT security concepts:")
        print("• X.509 certificates for device authentication")
        print("• Certificate-to-Thing attachment")
        print("• IoT policies for authorization")
        print("• Policy attachment and detachment")
        print("• External certificate registration")
        print("• Complete API details for each operation")
        
        if debug_mode:
            print(f"\n🔍 DEBUG MODE ENABLED")
            print(f"• Enhanced API request/response logging")
            print(f"• Full error details and tracebacks")
            print(f"• Extended educational information")
        else:
            print(f"\n💡 Tip: Use --debug or -d flag for enhanced API logging")
        
        print("=" * 50)
        
        try:
            iot = boto3.client('iot')
            print("✅ AWS IoT client initialized")
            
            if debug_mode:
                print(f"🔍 DEBUG: Client configuration:")
                print(f"   Region: {iot.meta.region_name}")
                print(f"   Service: {iot.meta.service_model.service_name}")
                print(f"   API Version: {iot.meta.service_model.api_version}")
        except Exception as e:
            print(f"❌ Error initializing AWS IoT client: {str(e)}")
            return
    
        # Set global debug mode for safe_operation calls
        global DEBUG_MODE
        DEBUG_MODE = debug_mode
        
        print("\n📚 LEARNING MOMENT: IoT Security Foundation")
        print("AWS IoT security is built on X.509 certificates for device authentication and IoT policies for authorization. Certificates uniquely identify devices, while policies define what actions devices can perform. Understanding this security model is crucial for building secure IoT solutions.")
        print("\n🔄 NEXT: We will explore certificate and policy management operations")
        input("Press Enter to continue...")
    
        while True:
            try:
                print("\n📋 Main Menu:")
                print("1. Create AWS IoT Certificate & Attach to Thing (+ Optional Policy)")
                print("2. Register External Certificate & Attach to Thing (+ Optional Policy)")
                print("3. Attach Policy to Existing Certificate")
                print("4. Detach Policy from Certificate")
                print("5. Enable/Disable Certificate")
                print("6. Exit")
                
                choice = input("\nSelect option (1-6): ").strip()
                
                if choice == '1':
                    print("\n📚 LEARNING MOMENT: Certificate Creation & Thing Attachment")
                    print("Creating an AWS IoT certificate establishes a unique digital identity for your device. The certificate contains a public key that AWS IoT uses to authenticate the device, while the private key stays securely on the device. Attaching the certificate to a Thing creates the binding between the device identity and its logical representation in AWS IoT.")
                    print("\n🔄 NEXT: We will create a certificate and attach it to a Thing")
                    input("Press Enter to continue...")
                    
                    certificate_creation_workflow(iot)
                elif choice == '2':
                    print("\n📚 LEARNING MOMENT: External Certificate Registration")
                    print("Sometimes you need to use certificates from your own Certificate Authority (CA) or existing PKI infrastructure. AWS IoT allows you to register external certificates, giving you flexibility in certificate management while maintaining security. This is useful for organizations with established certificate policies.")
                    print("\n🔄 NEXT: We will register an external certificate with AWS IoT")
                    input("Press Enter to continue...")
                    
                    register_external_certificate_workflow(iot)
                elif choice == '3':
                    print("\n📚 LEARNING MOMENT: Policy Attachment for Authorization")
                    print("While certificates handle authentication (who you are), IoT policies handle authorization (what you can do). Policies define which MQTT topics a device can publish to, subscribe to, and what AWS IoT operations it can perform. Attaching policies to certificates grants specific permissions to devices.")
                    print("\n🔄 NEXT: We will attach a policy to an existing certificate")
                    input("Press Enter to continue...")
                    
                    attach_policy_workflow(iot)
                elif choice == '4':
                    print("\n📚 LEARNING MOMENT: Policy Detachment for Permission Management")
                    print("Sometimes you need to remove specific permissions from a device without deleting the entire certificate. Policy detachment allows you to revoke specific permissions while keeping the device's identity intact. This is useful for changing device roles, troubleshooting permission issues, or implementing security policies.")
                    print("\n🔄 NEXT: We will detach a policy from a certificate")
                    input("Press Enter to continue...")
                    
                    detach_policy_workflow(iot)
                elif choice == '5':
                    print("\n📚 LEARNING MOMENT: Certificate Lifecycle Management")
                    print("Certificate status controls whether a device can connect to AWS IoT. ACTIVE certificates allow connections, while INACTIVE certificates block them. This provides immediate security control - you can instantly disable compromised devices or temporarily suspend access without deleting the certificate entirely.")
                    print("\n🔄 NEXT: We will manage certificate status (enable/disable)")
                    input("Press Enter to continue...")
                    
                    certificate_status_workflow(iot)
                elif choice == '6':
                    print("👋 Goodbye!")
                    break
                else:
                    print("❌ Invalid choice. Please select 1-6.")
                
                try:
                    input("\nPress Enter to continue...")
                except KeyboardInterrupt:
                    print("\n\n👋 Goodbye!")
                    break
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
    
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")

if __name__ == "__main__":
    main()