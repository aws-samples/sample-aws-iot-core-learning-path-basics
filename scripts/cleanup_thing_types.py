#!/usr/bin/env python3
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

"""
AWS IoT Thing Type Cleanup Utility
Handles the 5-minute deprecation waiting period required by AWS IoT.
"""
import boto3
import json
import time
import sys
from datetime import datetime, timedelta
from botocore.exceptions import ClientError

# Sample Thing Types created by setup script
SAMPLE_THING_TYPES = ['SedanVehicle', 'SUVVehicle', 'TruckVehicle']

def print_api_call(operation, description, params=None):
    """Print detailed API call information"""
    print(f"\n🔍 API Call: {operation}")
    print(f"📖 Description: {description}")
    if params:
        print(f"📥 Input Parameters:")
        print(json.dumps(params, indent=2, default=str))

def safe_operation(iot, operation, description, debug=False, **kwargs):
    """Execute IoT operation with detailed logging"""
    try:
        if debug:
            print_api_call(operation.__name__, description, kwargs)
        
        response = operation(**kwargs)
        
        if debug and response:
            print(f"📤 API Response:")
            print(json.dumps(response, indent=2, default=str))
        
        return response, True
    except ClientError as e:
        print(f"❌ {description} failed: {e.response['Error']['Message']}")
        if debug:
            print(f"🔍 DEBUG: Full error response:")
            print(json.dumps(e.response, indent=2, default=str))
        return None, False

def check_thing_type_status(iot, thing_type_name, debug=False):
    """Check if a Thing Type is deprecated and when"""
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
            creation_date = thing_type_metadata.get('creationDate')
            
            return {
                'exists': True,
                'deprecated': deprecated,
                'deprecation_date': deprecation_date,
                'creation_date': creation_date
            }
        
        return {'exists': False}
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            return {'exists': False}
        else:
            print(f"❌ Error checking Thing Type {thing_type_name}: {e.response['Error']['Message']}")
            return {'exists': False, 'error': str(e)}

def calculate_wait_time(deprecation_date):
    """Calculate remaining wait time for Thing Type deletion"""
    if not deprecation_date:
        return 300  # Default 5 minutes if we can't determine
    
    try:
        # Parse the deprecation date
        if isinstance(deprecation_date, str):
            # Handle different date formats
            try:
                dep_time = datetime.fromisoformat(deprecation_date.replace('Z', '+00:00'))
            except:
                # Fallback parsing
                dep_time = datetime.strptime(deprecation_date[:19], '%Y-%m-%dT%H:%M:%S')
        else:
            dep_time = deprecation_date
        
        # Calculate time elapsed since deprecation
        now = datetime.now(dep_time.tzinfo) if dep_time.tzinfo else datetime.now()
        elapsed = (now - dep_time).total_seconds()
        
        # AWS requires 5 minutes (300 seconds)
        remaining = max(0, 300 - elapsed)
        return int(remaining)
        
    except Exception as e:
        print(f"⚠️  Could not calculate wait time: {str(e)}")
        return 300  # Default to 5 minutes

def main():
    debug_mode = '--debug' in sys.argv or '-d' in sys.argv
    
    print("🏷️  AWS IoT Thing Type Cleanup Utility")
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
    
    print("This utility handles the 5-minute waiting period required")
    print("between Thing Type deprecation and deletion.")
    
    if debug_mode:
        print(f"\n🔍 DEBUG MODE ENABLED")
    
    print("=" * 50)
    
    try:
        iot = boto3.client('iot')
        print("✅ AWS IoT client initialized")
        
        if debug_mode:
            print(f"🔍 DEBUG: Client initialized")
        
        # Check status of all sample Thing Types
        print(f"\n📋 Checking status of sample Thing Types...")
        
        thing_type_status = {}
        for thing_type_name in SAMPLE_THING_TYPES:
            status = check_thing_type_status(iot, thing_type_name, debug=debug_mode)
            thing_type_status[thing_type_name] = status
            
            if status['exists']:
                if status['deprecated']:
                    wait_time = calculate_wait_time(status['deprecation_date'])
                    print(f"⚠️  {thing_type_name}: Deprecated ({wait_time}s remaining)")
                else:
                    print(f"🟢 {thing_type_name}: Active (needs deprecation)")
            else:
                print(f"❌ {thing_type_name}: Not found (already deleted or never created)")
        
        # Separate into categories
        active_types = [name for name, status in thing_type_status.items() 
                       if status['exists'] and not status['deprecated']]
        deprecated_types = [name for name, status in thing_type_status.items() 
                           if status['exists'] and status['deprecated']]
        
        if not active_types and not deprecated_types:
            print(f"\n✅ No sample Thing Types found to clean up")
            return
        
        # Handle active Thing Types (need deprecation)
        if active_types:
            print(f"\n⚠️  Found {len(active_types)} active Thing Types that need deprecation:")
            for name in active_types:
                print(f"   • {name}")
            
            deprecate = input(f"\nDeprecate these Thing Types now? (y/N): ").strip().lower()
            if deprecate == 'y':
                for thing_type_name in active_types:
                    print(f"\n🏷️  Deprecating {thing_type_name}...")
                    deprecate_response, success = safe_operation(
                        iot, iot.deprecate_thing_type,
                        f"Deprecate Thing Type {thing_type_name}",
                        debug=debug_mode,
                        thingTypeName=thing_type_name,
                        undoDeprecate=False
                    )
                    
                    if success:
                        print(f"✅ {thing_type_name} deprecated")
                        deprecated_types.append(thing_type_name)
                    else:
                        print(f"❌ Failed to deprecate {thing_type_name}")
        
        # Handle deprecated Thing Types (ready for deletion after wait)
        if deprecated_types:
            print(f"\n⏰ Found {len(deprecated_types)} deprecated Thing Types:")
            
            max_wait_time = 0
            for name in deprecated_types:
                status = thing_type_status.get(name, {})
                wait_time = calculate_wait_time(status.get('deprecation_date'))
                max_wait_time = max(max_wait_time, wait_time)
                
                if wait_time > 0:
                    print(f"   • {name} (wait {wait_time}s)")
                else:
                    print(f"   • {name} (ready for deletion)")
            
            if max_wait_time > 0:
                print(f"\n⏰ Maximum wait time: {max_wait_time} seconds ({max_wait_time//60}:{max_wait_time%60:02d})")
                print(f"\n🎯 Options:")
                print(f"1. Wait and delete automatically")
                print(f"2. Try deletion now (may fail)")
                print(f"3. Exit (run again later)")
                
                choice = input(f"\nSelect option (1-3): ").strip()
                
                if choice == '1':
                    print(f"\n⏳ Waiting {max_wait_time} seconds for AWS IoT constraint...")
                    
                    # Countdown with progress
                    for remaining in range(max_wait_time, 0, -10):
                        minutes = remaining // 60
                        seconds = remaining % 60
                        print(f"⏰ {minutes:02d}:{seconds:02d} remaining - Press Ctrl+C to cancel")
                        time.sleep(min(10, remaining))  # nosemgrep: arbitrary-sleep
                    
                    print(f"✅ Wait period completed!")
                    
                elif choice == '3':
                    print(f"👋 Exiting. Run this script again when ready to delete.")
                    return
            
            # Attempt deletion
            print(f"\n🗑️  Attempting to delete Thing Types...")
            
            for thing_type_name in deprecated_types:
                print(f"\n🗑️  Deleting {thing_type_name}...")
                
                try:
                    if debug_mode:
                        print_api_call("delete_thing_type", f"Delete Thing Type {thing_type_name}", 
                                     {"thingTypeName": thing_type_name})
                    
                    iot.delete_thing_type(thingTypeName=thing_type_name)
                    print(f"✅ Successfully deleted {thing_type_name}")
                    
                except ClientError as e:
                    error_code = e.response['Error']['Code']
                    error_message = e.response['Error']['Message']
                    
                    if 'cannot delete non deprecated thing type' in error_message.lower():
                        print(f"❌ {thing_type_name}: Not deprecated (unexpected)")
                    elif 'must wait' in error_message.lower() or 'recently deprecated' in error_message.lower():
                        print(f"⏰ {thing_type_name}: Still in waiting period")
                        print(f"   💡 Try again in a few minutes")
                    else:
                        print(f"❌ {thing_type_name}: {error_message}")
                    
                    if debug_mode:
                        print(f"🔍 DEBUG: Full error response:")
                        print(json.dumps(e.response, indent=2, default=str))
        
        print(f"\n🎉 Thing Type cleanup utility completed!")
        
    except KeyboardInterrupt:
        print(f"\n\n🛑 Interrupted by user")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        if debug_mode:
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()