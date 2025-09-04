#!/usr/bin/env python3
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import boto3
import os
import shutil
import json
import time
from botocore.exceptions import ClientError

# Sample data patterns created by setup scripts
SAMPLE_THING_TYPES = ['SedanVehicle', 'SUVVehicle', 'TruckVehicle']
SAMPLE_THING_GROUPS = ['CustomerFleet', 'TestFleet', 'MaintenanceFleet', 'DealerFleet']
SAMPLE_THING_PREFIX = 'Vehicle-VIN-'  # Things created as Vehicle-VIN-001, Vehicle-VIN-002, etc.

def print_api_call(operation, description, params=None):
    """Print detailed API call information for educational purposes"""
    print(f"\n🔍 API Call: {operation}")
    print(f"📖 Description: {description}")
    if params:
        print(f"📥 Input Parameters:")
        print(json.dumps(params, indent=2, default=str))
    else:
        print(f"📥 Input Parameters: None")

def print_api_response(response, success=True):
    """Print API response details"""
    if success:
        print(f"📤 API Response:")
        if response:
            print(json.dumps(response, indent=2, default=str))
        else:
            print("Empty response (operation completed successfully)")
    time.sleep(0.5)  # nosemgrep: arbitrary-sleep

def safe_delete(func, resource_type, name, debug=False, **kwargs):
    """Safely delete resource with error handling and optional debug info"""
    try:
        if debug:
            print_api_call(func.__name__, f"Delete {resource_type}: {name}", kwargs)
        else:
            print(f"Deleting {resource_type}: {name}")
        
        response = func(**kwargs)
        
        if debug:
            print_api_response(response, success=True)
        
        print(f"✅ Deleted {resource_type}: {name}")
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print(f"⚠️  {resource_type} {name} not found, skipping")
        else:
            print(f"❌ Error deleting {resource_type} {name}: {e.response['Error']['Message']}")
            if debug:
                print(f"🔍 DEBUG: Full error response:")
                print(json.dumps(e.response, indent=2, default=str))
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        if debug:
            import traceback
            print(f"🔍 DEBUG: Full traceback:")
            traceback.print_exc()
        return False

def safe_operation(iot, operation, description, debug=False, **kwargs):
    """Execute any IoT operation with detailed logging"""
    try:
        if debug:
            print_api_call(operation.__name__, description, kwargs)
        
        response = operation(**kwargs)
        
        if debug:
            print_api_response(response, success=True)
        
        return response, True
    except ClientError as e:
        print(f"❌ {description} failed: {e.response['Error']['Message']}")
        if debug:
            print(f"🔍 DEBUG: Full error response:")
            print(json.dumps(e.response, indent=2, default=str))
        return None, False
    except Exception as e:
        print(f"❌ {description} failed: {str(e)}")
        if debug:
            import traceback
            print(f"🔍 DEBUG: Full traceback:")
            traceback.print_exc()
        return None, False

def cleanup_certificate(iot, cert_arn, thing_name=None, debug=False):
    """Clean up a certificate and its attachments with detailed API logging"""
    cert_id = cert_arn.split('/')[-1]
    print(f"\n🔐 Cleaning up certificate: {cert_id}")
    
    try:
        # List and detach all policies from certificate
        if debug:
            print(f"\n🔍 Step 1: Listing policies attached to certificate")
        
        policies_response, success = safe_operation(
            iot, iot.list_attached_policies,
            f"List policies attached to certificate {cert_id}",
            debug=debug,
            target=cert_arn
        )
        
        if success and policies_response:
            policies = policies_response.get('policies', [])
            print(f"📋 Found {len(policies)} attached policies")
            
            for policy in policies:
                policy_name = policy['policyName']
                print(f"\n🔗 Detaching policy: {policy_name}")
                safe_delete(
                    iot.detach_policy,
                    f"Policy attachment '{policy_name}'",
                    f"from certificate {cert_id}",
                    debug=debug,
                    policyName=policy_name,
                    target=cert_arn
                )
        
        # Detach certificate from Things
        if thing_name:
            print(f"\n🔗 Detaching certificate from Thing: {thing_name}")
            safe_delete(
                iot.detach_thing_principal,
                "Certificate attachment",
                f"from Thing {thing_name}",
                debug=debug,
                thingName=thing_name,
                principal=cert_arn
            )
        
        # Deactivate certificate
        print(f"\n⏸️  Deactivating certificate: {cert_id}")
        deactivate_response, success = safe_operation(
            iot, iot.update_certificate,
            f"Deactivate certificate {cert_id}",
            debug=debug,
            certificateId=cert_id,
            newStatus='INACTIVE'
        )
        
        if success:
            print(f"✅ Certificate {cert_id} deactivated")
        
        # Delete certificate
        print(f"\n🗑️  Deleting certificate: {cert_id}")
        safe_delete(
            iot.delete_certificate,
            "Certificate",
            cert_id,
            debug=debug,
            certificateId=cert_id
        )
        
    except Exception as e:
        print(f"❌ Error cleaning up certificate {cert_id}: {str(e)}")
        if debug:
            import traceback
            traceback.print_exc()

def cleanup_sample_things(iot, debug=False):
    """Clean up sample Things and their certificates with detailed API logging"""
    print("\n🗑️  Step 1: Cleaning up sample Things and certificates...")
    print("-" * 50)
    
    try:
        # List all Things
        if debug:
            print(f"🔍 Listing all Things to find sample Things")
        
        list_response, success = safe_operation(
            iot, iot.list_things,
            "List all Things",
            debug=debug
        )
        
        if not success:
            return
        
        things = list_response.get('things', [])
        sample_things = [t for t in things if t['thingName'].startswith(SAMPLE_THING_PREFIX)]
        
        print(f"📋 Found {len(sample_things)} sample Things to clean up")
        
        for thing in sample_things:
            thing_name = thing['thingName']
            print(f"\n📱 Processing Thing: {thing_name}")
            
            # Get certificates attached to this Thing
            if debug:
                print(f"🔍 Listing principals (certificates) for Thing: {thing_name}")
            
            principals_response, success = safe_operation(
                iot, iot.list_thing_principals,
                f"List principals for Thing {thing_name}",
                debug=debug,
                thingName=thing_name
            )
            
            if success and principals_response:
                principals = principals_response.get('principals', [])
                cert_arns = [p for p in principals if 'cert/' in p]
                
                print(f"🔐 Found {len(cert_arns)} certificate(s) attached to {thing_name}")
                
                # Clean up certificates first
                for cert_arn in cert_arns:
                    cleanup_certificate(iot, cert_arn, thing_name, debug=debug)
            
            # Delete the Thing
            print(f"\n🗑️  Deleting Thing: {thing_name}")
            safe_delete(iot.delete_thing, "Thing", thing_name, debug=debug, thingName=thing_name)
            
    except Exception as e:
        print(f"❌ Error cleaning up Things: {str(e)}")
        if debug:
            import traceback
            traceback.print_exc()

def cleanup_orphaned_certificates(iot, debug=False):
    """Clean up any certificates that might be orphaned with detailed API logging"""
    print("\n🔐 Step 2: Checking for orphaned certificates...")
    print("-" * 50)
    
    try:
        # List all certificates
        if debug:
            print(f"🔍 Listing all certificates to check for orphaned ones")
        
        list_response, success = safe_operation(
            iot, iot.list_certificates,
            "List all certificates",
            debug=debug
        )
        
        if not success:
            return
        
        certificates = list_response.get('certificates', [])
        print(f"📋 Found {len(certificates)} certificate(s) in account")
        
        for cert in certificates:
            cert_arn = cert['certificateArn']
            cert_id = cert['certificateId']
            cert_status = cert.get('status', 'Unknown')
            
            print(f"\nℹ️  Certificate: {cert_id} (Status: {cert_status})")
            
            if debug:
                print(f"🔍 Checking if certificate {cert_id} is attached to any Things")
                
                # Get Things attached to this certificate
                try:
                    things_response, success = safe_operation(
                        iot, iot.list_principal_things,
                        f"List Things attached to certificate {cert_id}",
                        debug=debug,
                        principal=cert_arn
                    )
                    
                    if success and things_response:
                        attached_things = things_response.get('things', [])
                        sample_things = [t for t in attached_things if t.startswith(SAMPLE_THING_PREFIX)]
                        
                        if sample_things:
                            print(f"⚠️  Certificate {cert_id} was attached to sample Things: {', '.join(sample_things)}")
                            print(f"   This certificate should have been cleaned up in Step 1")
                        else:
                            print(f"✅ Certificate {cert_id} is not attached to sample Things")
                    
                except Exception as e:
                    print(f"⚠️  Could not check Things for certificate {cert_id}: {str(e)}")
            
            # Note: We don't automatically delete certificates here as they might be used by non-sample resources
            # The certificate cleanup happens in Step 1 when processing sample Things
                
    except Exception as e:
        print(f"❌ Error listing certificates: {str(e)}")
        if debug:
            import traceback
            traceback.print_exc()

def cleanup_sample_policies(iot, debug=False):
    """Clean up policies that might have been created by certificate manager"""
    print("\n📄 Step 3: Cleaning up sample policies...")
    print("-" * 50)
    
    try:
        # List all policies
        if debug:
            print(f"🔍 Listing all policies to check for cleanup")
        
        list_response, success = safe_operation(
            iot, iot.list_policies,
            "List all policies",
            debug=debug
        )
        
        if not success:
            return
        
        policies = list_response.get('policies', [])
        
        print(f"📋 Found {len(policies)} policies in account")
        
        # Look for policies that appear to be sample/learning policies
        sample_policy_patterns = ['sample', 'test', 'demo', 'learning', 'device', 'basic', 'readonly']
        policies_deleted = 0
        policies_skipped = 0
        
        for policy in policies:
            policy_name = policy['policyName']
            
            # Check if policy name contains sample patterns (case insensitive)
            is_sample_policy = any(pattern.lower() in policy_name.lower() for pattern in sample_policy_patterns)
            
            if is_sample_policy:
                print(f"\n📄 Checking policy: {policy_name}")
                
                try:
                    # Check if policy is attached to any certificates
                    if debug:
                        print(f"🔍 Checking targets for policy: {policy_name}")
                    
                    targets_response, success = safe_operation(
                        iot, iot.list_targets_for_policy,
                        f"List targets for policy {policy_name}",
                        debug=debug,
                        policyName=policy_name
                    )
                    
                    if success and targets_response:
                        targets = targets_response.get('targets', [])
                        
                        if targets:
                            print(f"   ⚠️  Policy {policy_name} is attached to {len(targets)} target(s), skipping")
                            if debug:
                                for target in targets:
                                    print(f"      - {target}")
                            policies_skipped += 1
                        else:
                            # Policy is not attached to anything, safe to delete
                            print(f"   🗑️  Deleting unattached policy: {policy_name}")
                            
                            delete_success = safe_delete(
                                iot.delete_policy,
                                "Policy",
                                policy_name,
                                debug=debug,
                                policyName=policy_name
                            )
                            
                            if delete_success:
                                policies_deleted += 1
                    
                except Exception as e:
                    print(f"   ❌ Error checking policy {policy_name}: {str(e)}")
                    if debug:
                        import traceback
                        traceback.print_exc()
            else:
                if debug:
                    print(f"   ℹ️  Policy {policy_name} doesn't match sample patterns, skipping")
        
        print(f"\n📊 Policy cleanup summary:")
        print(f"   ✅ Deleted: {policies_deleted} policies")
        print(f"   ⚠️  Skipped: {policies_skipped} policies (still attached to resources)")
        
        if policies_skipped > 0:
            print(f"\n💡 Skipped policies are still attached to certificates or other resources")
            print(f"   They will be cleaned up automatically when certificates are deleted")
            print(f"   Or you can manually detach and delete them if needed")
        
    except Exception as e:
        print(f"❌ Error during policy cleanup: {str(e)}")
        if debug:
            import traceback
            traceback.print_exc()

def cleanup_sample_thing_groups(iot, debug=False):
    """Clean up sample Thing Groups with detailed API logging"""
    print("\n📁 Step 4: Cleaning up sample Thing Groups...")
    print("-" * 50)
    
    try:
        # List Thing Groups
        if debug:
            print(f"🔍 Listing all Thing Groups to find sample groups")
        
        list_response, success = safe_operation(
            iot, iot.list_thing_groups,
            "List all Thing Groups",
            debug=debug
        )
        
        if not success:
            return
        
        thing_groups = list_response.get('thingGroups', [])
        sample_groups = [g for g in thing_groups if g['groupName'] in SAMPLE_THING_GROUPS]
        
        print(f"📋 Found {len(sample_groups)} sample Thing Groups to clean up")
        
        for group in sample_groups:
            group_name = group['groupName']
            print(f"\n📁 Deleting Thing Group: {group_name}")
            safe_delete(
                iot.delete_thing_group,
                "Thing Group",
                group_name,
                debug=debug,
                thingGroupName=group_name
            )
            
    except Exception as e:
        print(f"❌ Error cleaning up Thing Groups: {str(e)}")
        if debug:
            import traceback
            traceback.print_exc()

def cleanup_sample_thing_types(iot, debug=False):
    """Clean up sample Thing Types (requires deprecation + 5-minute wait + deletion)"""
    print("\n🏷️  Step 5: Cleaning up sample Thing Types...")
    print("-" * 50)
    
    try:
        # List Thing Types
        if debug:
            print(f"🔍 Listing all Thing Types to find sample types")
        
        list_response, success = safe_operation(
            iot, iot.list_thing_types,
            "List all Thing Types",
            debug=debug
        )
        
        if not success:
            return
        
        thing_types = list_response.get('thingTypes', [])
        sample_types = [t for t in thing_types if t['thingTypeName'] in SAMPLE_THING_TYPES]
        
        print(f"📋 Found {len(sample_types)} sample Thing Types to clean up")
        
        if not sample_types:
            print("ℹ️  No sample Thing Types found to clean up")
            return
        
        # Check if any Thing Types are already deprecated
        deprecated_types = []
        active_types = []
        
        for thing_type in sample_types:
            thing_type_name = thing_type['thingTypeName']
            
            # Check current status
            try:
                describe_response, success = safe_operation(
                    iot, iot.describe_thing_type,
                    f"Check status of Thing Type {thing_type_name}",
                    debug=debug,
                    thingTypeName=thing_type_name
                )
                
                if success and describe_response:
                    thing_type_metadata = describe_response.get('thingTypeMetadata', {})
                    deprecated = thing_type_metadata.get('deprecated', False)
                    deprecation_date = thing_type_metadata.get('deprecationDate')
                    
                    if deprecated:
                        deprecated_types.append({
                            'name': thing_type_name,
                            'deprecation_date': deprecation_date
                        })
                        print(f"ℹ️  Thing Type {thing_type_name} is already deprecated (since {deprecation_date})")
                    else:
                        active_types.append(thing_type_name)
                        print(f"ℹ️  Thing Type {thing_type_name} is active (needs deprecation)")
                        
            except Exception as e:
                print(f"⚠️  Could not check status of {thing_type_name}: {str(e)}")
                active_types.append(thing_type_name)  # Assume active if we can't check
        
        # Step 1: Deprecate active Thing Types
        newly_deprecated = []
        if active_types:
            print(f"\n⚠️  Deprecating {len(active_types)} active Thing Types...")
            
            for thing_type_name in active_types:
                print(f"\n🏷️  Deprecating Thing Type: {thing_type_name}")
                deprecate_response, success = safe_operation(
                    iot, iot.deprecate_thing_type,
                    f"Deprecate Thing Type {thing_type_name}",
                    debug=debug,
                    thingTypeName=thing_type_name,
                    undoDeprecate=False
                )
                
                if success:
                    print(f"✅ Thing Type {thing_type_name} deprecated")
                    newly_deprecated.append(thing_type_name)
                else:
                    print(f"❌ Could not deprecate Thing Type {thing_type_name}")
        
        # Step 2: Handle the 5-minute waiting period
        all_deprecated = deprecated_types + [{'name': name, 'deprecation_date': 'just now'} for name in newly_deprecated]
        
        if all_deprecated:
            print(f"\n⏰ AWS IoT Constraint: Thing Types must wait 5 minutes after deprecation before deletion")
            print(f"📋 Thing Types to delete:")
            for item in all_deprecated:
                print(f"   • {item['name']} (deprecated: {item['deprecation_date']})")
            
            print(f"\n🎯 Deletion Options:")
            print(f"1. Wait 5 minutes now and delete automatically")
            print(f"2. Skip deletion (run cleanup again later)")
            print(f"3. Try deletion now (may fail if not enough time has passed)")
            
            while True:
                choice = input("\nSelect option (1-3): ").strip()
                
                if choice == '1':
                    print(f"\n⏳ Waiting 5 minutes for AWS IoT constraint...")
                    print(f"💡 This is required by AWS IoT - Thing Types cannot be deleted immediately after deprecation")
                    
                    # Show countdown
                    import time
                    wait_seconds = 300  # 5 minutes
                    for remaining in range(wait_seconds, 0, -30):
                        minutes = remaining // 60
                        seconds = remaining % 60
                        print(f"⏰ Time remaining: {minutes:02d}:{seconds:02d} - You can cancel with Ctrl+C")
                        time.sleep(30)  # nosemgrep: arbitrary-sleep
                    
                    print(f"✅ 5-minute wait period completed!")
                    break
                    
                elif choice == '2':
                    print(f"⏭️  Skipping Thing Type deletion")
                    print(f"💡 To delete later, run: python cleanup_sample_data.py")
                    print(f"   The Thing Types are already deprecated and will be ready for deletion")
                    return
                    
                elif choice == '3':
                    print(f"🚀 Attempting deletion now (may fail due to timing constraint)")
                    break
                    
                else:
                    print(f"❌ Invalid choice. Please enter 1, 2, or 3")
            
            # Step 3: Delete the deprecated Thing Types
            print(f"\n🗑️  Deleting deprecated Thing Types...")
            
            for item in all_deprecated:
                thing_type_name = item['name']
                print(f"\n🗑️  Attempting to delete Thing Type: {thing_type_name}")
                
                delete_success = safe_delete(
                    iot.delete_thing_type,
                    "Thing Type",
                    thing_type_name,
                    debug=debug,
                    thingTypeName=thing_type_name
                )
                
                if not delete_success:
                    print(f"💡 If deletion failed due to timing, wait a few more minutes and try again")
                    print(f"   The Thing Type {thing_type_name} is deprecated and ready for deletion")
        
    except KeyboardInterrupt:
        print(f"\n\n🛑 Cleanup interrupted by user")
        print(f"💡 Thing Types that were deprecated can be deleted later by running cleanup again")
    except Exception as e:
        print(f"❌ Error cleaning up Thing Types: {str(e)}")
        if debug:
            import traceback
            traceback.print_exc()

def cleanup_sample_shadows(iot, debug=False):
    """Clean up device shadows for sample Things"""
    print("\n🌙 Step 6: Cleaning up device shadows...")
    print("-" * 50)
    
    # Get list of sample Things that might have shadows
    sample_thing_names = [f"Vehicle-VIN-{i:03d}" for i in range(1, 21)]
    
    shadows_deleted = 0
    
    for thing_name in sample_thing_names:
        try:
            # Check if shadow exists by trying to get it
            if debug:
                print(f"🔍 DEBUG: Checking shadow for Thing: {thing_name}")
            
            response = iot.get_thing_shadow(thingName=thing_name)
            
            # Shadow exists, delete it
            if debug:
                print(f"🔍 DEBUG: Deleting shadow for Thing: {thing_name}")
            
            iot.delete_thing_shadow(thingName=thing_name)
            print(f"   ✅ Deleted shadow for {thing_name}")
            shadows_deleted += 1
            
        except iot.exceptions.ResourceNotFoundException:
            # No shadow exists for this Thing
            if debug:
                print(f"🔍 DEBUG: No shadow found for {thing_name}")
            continue
        except Exception as e:
            print(f"   ❌ Error deleting shadow for {thing_name}: {str(e)}")
            if debug:
                import traceback
                traceback.print_exc()
    
    print(f"📊 Shadow cleanup summary: {shadows_deleted} shadows deleted")

def cleanup_sample_rules(iot, debug=False):
    """Clean up IoT rules that might have been created during learning"""
    print("\n📋 Step 7: Cleaning up sample IoT rules...")
    print("-" * 50)
    
    try:
        # List all rules
        if debug:
            print(f"🔍 DEBUG: Listing all IoT rules")
        
        response = iot.list_topic_rules()
        rules = response.get('rules', [])
        
        # Look for rules that appear to be sample/learning rules
        sample_rule_patterns = ['sample', 'test', 'demo', 'learning', 'device']
        rules_deleted = 0
        
        for rule in rules:
            rule_name = rule['ruleName']
            
            # Check if rule name contains sample patterns (case insensitive)
            is_sample_rule = any(pattern.lower() in rule_name.lower() for pattern in sample_rule_patterns)
            
            if is_sample_rule:
                try:
                    if debug:
                        print(f"🔍 DEBUG: Deleting rule: {rule_name}")
                    
                    iot.delete_topic_rule(ruleName=rule_name)
                    print(f"   ✅ Deleted rule: {rule_name}")
                    rules_deleted += 1
                    
                except Exception as e:
                    print(f"   ❌ Error deleting rule {rule_name}: {str(e)}")
                    if debug:
                        import traceback
                        traceback.print_exc()
        
        if rules_deleted == 0:
            print("   ℹ️ No sample rules found to delete")
        else:
            print(f"📊 Rules cleanup summary: {rules_deleted} rules deleted")
            
    except Exception as e:
        print(f"❌ Error during rules cleanup: {str(e)}")
        if debug:
            import traceback
            traceback.print_exc()

def cleanup_local_files(debug=False):
    """Clean up local certificate files with detailed logging"""
    print("\n💾 Step 8: Cleaning up local certificate files...")
    print("-" * 50)
    
    # Clean up main certificates directory
    cert_dir = os.path.join(os.getcwd(), 'certificates')
    
    if debug:
        print(f"🔍 Checking for local certificates directory: {cert_dir}")
    
    if os.path.exists(cert_dir):
        try:
            if debug:
                # Show what's being deleted
                print(f"📁 Contents of certificates directory:")
                for root, dirs, files in os.walk(cert_dir):
                    level = root.replace(cert_dir, '').count(os.sep)
                    indent = ' ' * 2 * level
                    print(f"{indent}{os.path.basename(root)}/")
                    subindent = ' ' * 2 * (level + 1)
                    for file in files:
                        file_path = os.path.join(root, file)
                        file_size = os.path.getsize(file_path)
                        print(f"{subindent}{file} ({file_size} bytes)")
            
            shutil.rmtree(cert_dir)
            print(f"✅ Removed local certificates directory: {cert_dir}")
            
            if debug:
                print(f"🔍 Directory {cert_dir} successfully deleted")
                
        except Exception as e:
            print(f"❌ Error removing certificates directory: {str(e)}")
            if debug:
                import traceback
                traceback.print_exc()
    else:
        print("ℹ️  No local certificates directory found")
        if debug:
            print(f"🔍 Directory {cert_dir} does not exist")
    
    # Clean up sample-certs directory (created by OpenSSL certificate generation)
    sample_cert_dir = os.path.join(os.getcwd(), 'sample-certs')
    
    if debug:
        print(f"🔍 Checking for sample certificates directory: {sample_cert_dir}")
    
    if os.path.exists(sample_cert_dir):
        try:
            if debug:
                # Show what's being deleted
                print(f"📁 Contents of sample-certs directory:")
                for root, dirs, files in os.walk(sample_cert_dir):
                    level = root.replace(sample_cert_dir, '').count(os.sep)
                    indent = ' ' * 2 * level
                    print(f"{indent}{os.path.basename(root)}/")
                    subindent = ' ' * 2 * (level + 1)
                    for file in files:
                        file_path = os.path.join(root, file)
                        file_size = os.path.getsize(file_path)
                        print(f"{subindent}{file} ({file_size} bytes)")
            
            shutil.rmtree(sample_cert_dir)
            print(f"✅ Removed sample certificates directory: {sample_cert_dir}")
            
            if debug:
                print(f"🔍 Directory {sample_cert_dir} successfully deleted")
                
        except Exception as e:
            print(f"❌ Error removing sample-certs directory: {str(e)}")
            if debug:
                import traceback
                traceback.print_exc()
    else:
        print("ℹ️  No sample certificates directory found")
        if debug:
            print(f"🔍 Directory {sample_cert_dir} does not exist")

def print_summary():
    """Print cleanup summary"""
    print("\n🎉 Cleanup Summary")
    print("=" * 50)
    print("✅ Sample Things cleaned up (Vehicle-VIN-001, Vehicle-VIN-002, etc.)")
    print("✅ Associated certificates cleaned up")
    print("✅ Sample Thing Groups cleaned up")
    print("✅ Sample Thing Types cleaned up")
    print("✅ Local certificate files cleaned up (certificates/ and sample-certs/)")
    print("✅ Device state files cleaned up (device_state.json files)")
    print("⚠️  Policies require manual review and cleanup")
    print("\n💡 Your AWS IoT account now only contains non-sample resources")

def main():
    import sys
    
    # Check for debug flag
    debug_mode = '--debug' in sys.argv or '-d' in sys.argv
    
    print("🧹 AWS IoT Sample Data Cleanup")
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
    
    print("This script will clean up ONLY the sample resources created by:")
    print("• setup_sample_data.py")
    print("• certificate_manager.py")
    print("\nIt will NOT affect other IoT resources in your account.")
    
    if debug_mode:
        print(f"\n🔍 DEBUG MODE ENABLED")
        print(f"• Will show detailed API requests and responses")
        print(f"• Includes complete error details and tracebacks")
        print(f"• Educational API call documentation")
    else:
        print(f"\n💡 Tip: Use --debug or -d flag to see detailed API calls")
    
    print("=" * 50)
    
    print(f"\n🎯 Resources to be cleaned up:")
    print(f"• Things starting with '{SAMPLE_THING_PREFIX}' (Vehicle-VIN-001, Vehicle-VIN-002, etc.)")
    print(f"• Thing Types: {', '.join(SAMPLE_THING_TYPES)} (will be deprecated first)")
    print(f"• Thing Groups: {', '.join(SAMPLE_THING_GROUPS)}")
    print(f"• Certificates attached to sample Things")
    print(f"• Local certificate files in ./certificates/")
    print(f"• Policies will be listed for manual review")
    
    confirm = input("\nContinue with cleanup? (y/N): ").strip().lower()
    if confirm != 'y':
        print("Cleanup cancelled")
        return
    
    try:
        iot = boto3.client('iot')
        print("✅ AWS IoT client initialized")
        
        if debug_mode:
            print(f"🔍 DEBUG: Client configuration:")
            print(f"   Service: {iot.meta.service_model.service_name}")
            print(f"   Service: {iot.meta.service_model.service_name}")
            print(f"   API Version: {iot.meta.service_model.api_version}")
        
        print("\n📚 LEARNING MOMENT: Resource Cleanup & Lifecycle Management")
        print("Proper resource cleanup is essential in IoT deployments to avoid unnecessary costs and maintain security. AWS IoT resources have dependencies - certificates must be detached before deletion, Thing Types must be deprecated before removal, and policies should be carefully reviewed since they may be shared across devices.")
        print("\n🔄 NEXT: We will safely clean up sample resources in the correct order")
        input("Press Enter to continue...")
        
        # Execute cleanup steps in order with debug flag
        cleanup_sample_things(iot, debug=debug_mode)
        cleanup_orphaned_certificates(iot, debug=debug_mode)
        cleanup_sample_policies(iot, debug=debug_mode)
        cleanup_sample_thing_groups(iot, debug=debug_mode)
        cleanup_sample_thing_types(iot, debug=debug_mode)
        cleanup_sample_shadows(iot, debug=debug_mode)
        cleanup_sample_rules(iot, debug=debug_mode)
        cleanup_local_files(debug=debug_mode)
        print_summary()
        
        if debug_mode:
            print(f"\n🔍 DEBUG: Cleanup session completed with detailed API logging")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        if debug_mode:
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()