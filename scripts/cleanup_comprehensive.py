#!/usr/bin/env python3
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

"""
Comprehensive cleanup script for AWS IoT sample data.
This script provides more granular control over what gets cleaned up.
"""
import boto3
import os
import shutil
import json
from botocore.exceptions import ClientError

# Sample data patterns
SAMPLE_THING_TYPES = ['SedanVehicle', 'SUVVehicle', 'TruckVehicle']
SAMPLE_THING_GROUPS = ['CustomerFleet', 'TestFleet', 'MaintenanceFleet', 'DealerFleet']
SAMPLE_THING_PREFIX = 'Device-'

def safe_operation(func, operation_name, **kwargs):
    """Execute operation with error handling"""
    try:
        print(f"🔄 {operation_name}...")
        response = func(**kwargs)
        print(f"✅ {operation_name} completed")
        return response, True
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print(f"⚠️  {operation_name} - Resource not found, skipping")
        else:
            print(f"❌ {operation_name} failed: {e.response['Error']['Message']}")
        return None, False
    except Exception as e:
        print(f"❌ {operation_name} failed: {str(e)}")
        return None, False

def get_certificate_details(iot, cert_arn):
    """Get detailed information about a certificate"""
    cert_id = cert_arn.split('/')[-1]
    
    try:
        # Get certificate details
        cert_response = iot.describe_certificate(certificateId=cert_id)
        
        # Get attached policies
        policies_response = iot.list_attached_policies(target=cert_arn)
        policies = policies_response.get('policies', [])
        
        # Get attached Things (principals)
        principals_response = iot.list_principal_things(principal=cert_arn)
        things = principals_response.get('things', [])
        
        return {
            'certificateId': cert_id,
            'certificateArn': cert_arn,
            'status': cert_response.get('certificateDescription', {}).get('status'),
            'creationDate': cert_response.get('certificateDescription', {}).get('creationDate'),
            'attachedPolicies': [p['policyName'] for p in policies],
            'attachedThings': things
        }
    except Exception as e:
        print(f"❌ Error getting certificate details for {cert_id}: {str(e)}")
        return None

def interactive_certificate_cleanup(iot):
    """Interactive certificate cleanup with detailed information"""
    print("\n🔐 Interactive Certificate Cleanup")
    print("=" * 50)
    
    try:
        certificates = iot.list_certificates().get('certificates', [])
        
        if not certificates:
            print("ℹ️  No certificates found in account")
            return
        
        print(f"Found {len(certificates)} certificate(s) in your account\n")
        
        for i, cert in enumerate(certificates, 1):
            cert_arn = cert['certificateArn']
            cert_id = cert['certificateId']
            
            print(f"📋 Certificate {i}/{len(certificates)}")
            print(f"   ID: {cert_id}")
            print(f"   Status: {cert.get('status', 'Unknown')}")
            print(f"   Created: {cert.get('creationDate', 'Unknown')}")
            
            # Get detailed information
            details = get_certificate_details(iot, cert_arn)
            if details:
                if details['attachedThings']:
                    print(f"   Attached to Things: {', '.join(details['attachedThings'])}")
                else:
                    print(f"   Attached to Things: None")
                
                if details['attachedPolicies']:
                    print(f"   Attached Policies: {', '.join(details['attachedPolicies'])}")
                else:
                    print(f"   Attached Policies: None")
            
            # Ask user what to do
            while True:
                choice = input(f"\n   Action for certificate {cert_id}? (d)elete, (s)kip, (q)uit: ").strip().lower()
                
                if choice == 'd':
                    cleanup_single_certificate(iot, cert_arn, details)
                    break
                elif choice == 's':
                    print(f"   ⏭️  Skipped certificate {cert_id}")
                    break
                elif choice == 'q':
                    print("   🛑 Cleanup cancelled by user")
                    return
                else:
                    print("   ❌ Invalid choice. Please enter 'd', 's', or 'q'")
            
            print()  # Empty line for readability
            
    except Exception as e:
        print(f"❌ Error during interactive cleanup: {str(e)}")

def cleanup_single_certificate(iot, cert_arn, details=None):
    """Clean up a single certificate with all its attachments"""
    cert_id = cert_arn.split('/')[-1]
    
    if not details:
        details = get_certificate_details(iot, cert_arn)
    
    if not details:
        print(f"❌ Could not get details for certificate {cert_id}")
        return False
    
    print(f"   🧹 Cleaning up certificate {cert_id}...")
    
    # Detach from policies
    for policy_name in details['attachedPolicies']:
        safe_operation(
            iot.detach_policy,
            f"Detaching policy '{policy_name}'",
            policyName=policy_name,
            target=cert_arn
        )
    
    # Detach from Things
    for thing_name in details['attachedThings']:
        safe_operation(
            iot.detach_thing_principal,
            f"Detaching from Thing '{thing_name}'",
            thingName=thing_name,
            principal=cert_arn
        )
    
    # Deactivate certificate
    if details['status'] == 'ACTIVE':
        safe_operation(
            iot.update_certificate,
            "Deactivating certificate",
            certificateId=cert_id,
            newStatus='INACTIVE'
        )
    
    # Delete certificate
    success = safe_operation(
        iot.delete_certificate,
        f"Deleting certificate {cert_id}",
        certificateId=cert_id
    )[1]
    
    if success:
        # Clean up local files
        cleanup_local_certificate_files(cert_id, details['attachedThings'])
    
    return success

def cleanup_local_certificate_files(cert_id, thing_names):
    """Clean up local certificate files for a specific certificate"""
    cert_dir = os.path.join(os.getcwd(), 'certificates')
    
    if not os.path.exists(cert_dir):
        return
    
    files_removed = 0
    
    # Check each Thing directory
    for thing_name in thing_names:
        thing_dir = os.path.join(cert_dir, thing_name)
        if os.path.exists(thing_dir):
            for file_name in os.listdir(thing_dir):
                if cert_id in file_name:
                    file_path = os.path.join(thing_dir, file_name)
                    try:
                        os.remove(file_path)
                        print(f"   🗑️  Removed: {file_path}")
                        files_removed += 1
                    except Exception as e:
                        print(f"   ❌ Could not remove {file_path}: {str(e)}")
            
            # Remove empty directories
            try:
                if not os.listdir(thing_dir):
                    os.rmdir(thing_dir)
                    print(f"   🗑️  Removed empty directory: {thing_dir}")
            except:
                pass
    
    if files_removed > 0:
        print(f"   ✅ Removed {files_removed} local certificate file(s)")

def list_all_resources(iot):
    """List all IoT resources for review"""
    print("\n📊 Current AWS IoT Resources")
    print("=" * 50)
    
    try:
        # Things
        things = iot.list_things().get('things', [])
        print(f"\n📱 Things ({len(things)}):")
        for thing in things:
            sample_marker = "🎯 SAMPLE" if thing['thingName'].startswith(SAMPLE_THING_PREFIX) else ""
            print(f"   - {thing['thingName']} (Type: {thing.get('thingTypeName', 'None')}) {sample_marker}")
        
        # Thing Types
        thing_types = iot.list_thing_types().get('thingTypes', [])
        print(f"\n🏷️  Thing Types ({len(thing_types)}):")
        for tt in thing_types:
            sample_marker = "🎯 SAMPLE" if tt['thingTypeName'] in SAMPLE_THING_TYPES else ""
            print(f"   - {tt['thingTypeName']} {sample_marker}")
        
        # Thing Groups
        thing_groups = iot.list_thing_groups().get('thingGroups', [])
        print(f"\n📁 Thing Groups ({len(thing_groups)}):")
        for tg in thing_groups:
            sample_marker = "🎯 SAMPLE" if tg['groupName'] in SAMPLE_THING_GROUPS else ""
            print(f"   - {tg['groupName']} {sample_marker}")
        
        # Certificates
        certificates = iot.list_certificates().get('certificates', [])
        print(f"\n🔐 Certificates ({len(certificates)}):")
        for cert in certificates:
            print(f"   - {cert['certificateId']} (Status: {cert.get('status', 'Unknown')})")
        
        # Policies
        policies = iot.list_policies().get('policies', [])
        print(f"\n📄 Policies ({len(policies)}):")
        for policy in policies:
            print(f"   - {policy['policyName']}")
        
    except Exception as e:
        print(f"❌ Error listing resources: {str(e)}")

def main():
    print("🔧 Comprehensive AWS IoT Cleanup Tool")
    print("=" * 50)
    print("This tool provides granular control over IoT resource cleanup.")
    print("You can choose exactly what to clean up.")
    print("=" * 50)
    
    try:
        iot = boto3.client('iot')
        print("✅ AWS IoT client initialized")
    except Exception as e:
        print(f"❌ Error initializing AWS IoT client: {str(e)}")
        return
    
    while True:
        print("\n📋 Cleanup Options:")
        print("1. List all resources (review what exists)")
        print("2. Clean up sample data only (safe, automated)")
        print("3. Interactive certificate cleanup (choose what to delete)")
        print("4. Clean up local certificate files only")
        print("5. Exit")
        
        choice = input("\nSelect option (1-5): ").strip()
        
        if choice == '1':
            list_all_resources(iot)
            
        elif choice == '2':
            print("\n🎯 Automated Sample Data Cleanup")
            print("This will clean up only the resources created by setup_sample_data.py")
            confirm = input("Continue? (y/N): ").strip().lower()
            if confirm == 'y':
                # Import and run the safe cleanup from the updated script
                from cleanup_sample_data import (
                    cleanup_sample_things, cleanup_sample_thing_groups, 
                    cleanup_sample_thing_types, cleanup_local_files
                )
                cleanup_sample_things(iot)
                cleanup_sample_thing_groups(iot)
                cleanup_sample_thing_types(iot)
                cleanup_local_files()
                print("✅ Sample data cleanup complete")
            
        elif choice == '3':
            interactive_certificate_cleanup(iot)
            
        elif choice == '4':
            cert_dir = os.path.join(os.getcwd(), 'certificates')
            if os.path.exists(cert_dir):
                confirm = input(f"Delete all files in {cert_dir}? (y/N): ").strip().lower()
                if confirm == 'y':
                    try:
                        shutil.rmtree(cert_dir)
                        print(f"✅ Removed {cert_dir}")
                    except Exception as e:
                        print(f"❌ Error: {str(e)}")
            else:
                print("ℹ️  No certificates directory found")
                
        elif choice == '5':
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please select 1-5.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()