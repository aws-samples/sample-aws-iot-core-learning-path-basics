#!/usr/bin/env python3
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import boto3
import json
import uuid
import random
import time
from datetime import datetime, timedelta
from botocore.exceptions import ClientError

# Configuration
THING_COUNT = 20
THING_TYPES = ['SedanVehicle', 'SUVVehicle', 'TruckVehicle']
THING_GROUPS = ['CustomerFleet', 'TestFleet', 'MaintenanceFleet', 'DealerFleet']
COUNTRIES = ['USA', 'Germany', 'Japan', 'Canada', 'Brazil', 'UK', 'France', 'Australia', 'India', 'Mexico']

def print_step(step, description):
    """Print setup step with formatting"""
    print(f"\n🔧 Step {step}: {description}")
    print("-" * 50)

def safe_create(func, resource_type, name, debug=False, **kwargs):
    """Safely create resource with error handling and optional debug info"""
    try:
        if debug:
            print(f"\n🔍 DEBUG: Creating {resource_type}: {name}")
            print(f"📤 API Call: {func.__name__}")
            print(f"📥 Input Parameters:")
            print(json.dumps(kwargs, indent=2, default=str))
        else:
            print(f"Creating {resource_type}: {name}")
        
        response = func(**kwargs)
        
        if debug:
            print(f"📤 API Response:")
            print(json.dumps(response, indent=2, default=str))
        
        print(f"✅ Created {resource_type}: {name}")
        time.sleep(0.5 if not debug else 1.0)  # nosemgrep: arbitrary-sleep
        return response
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceAlreadyExistsException':
            print(f"⚠️  {resource_type} {name} already exists, skipping")
        else:
            print(f"❌ Error creating {resource_type} {name}: {e.response['Error']['Message']}")
            if debug:
                print(f"🔍 DEBUG: Full error response:")
                print(json.dumps(e.response, indent=2, default=str))
        time.sleep(0.5)  # nosemgrep: arbitrary-sleep
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        if debug:
            import traceback
            print(f"🔍 DEBUG: Full traceback:")
            traceback.print_exc()
        time.sleep(0.5)  # nosemgrep: arbitrary-sleep

def create_thing_types(iot, debug=False):
    """Create predefined Thing Types"""
    print_step(1, "Creating Thing Types")
    
    for thing_type in THING_TYPES:
        # Check if Thing Type already exists
        try:
            response = iot.describe_thing_type(thingTypeName=thing_type)
            if response.get('thingTypeMetadata', {}).get('deprecated'):
                print(f"   ⚠️ Thing Type {thing_type} is deprecated, undeprecating...")
                iot.deprecate_thing_type(thingTypeName=thing_type, undoDeprecate=True)
                print(f"   ✅ Thing Type {thing_type} undeprecated successfully")
            else:
                print(f"   ℹ️ Thing Type {thing_type} already exists and is active")
            continue
        except iot.exceptions.ResourceNotFoundException:
            # Thing Type doesn't exist, create it
            pass
        except Exception as e:
            print(f"   ❌ Error checking Thing Type {thing_type}: {str(e)}")
            continue
        
        description = f"Template for {thing_type.replace('Vehicle', ' Vehicle')} category"
        safe_create(
            iot.create_thing_type,
            "Thing Type", thing_type,
            debug=debug,
            thingTypeName=thing_type,
            thingTypeProperties={
                'thingTypeDescription': description,
                'searchableAttributes': ['customerId', 'country', 'manufacturingDate']
            }
        )

def create_thing_groups(iot, debug=False):
    """Create predefined Thing Groups"""
    print_step(2, "Creating Thing Groups")
    
    for group in THING_GROUPS:
        description = f"Group for devices in {group.replace('Floor', ' Floor')}"
        safe_create(
            iot.create_thing_group,
            "Thing Group", group,
            debug=debug,
            thingGroupName=group,
            thingGroupProperties={
                'thingGroupDescription': description,
                'attributePayload': {
                    'attributes': {
                        'location': group,
                        'managed': 'true'
                    }
                }
            }
        )

def generate_random_date():
    """Generate random date within last year"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    random_date = start_date + timedelta(
        seconds=random.randint(0, int((end_date - start_date).total_seconds()))
    )
    return random_date.strftime('%Y-%m-%d')

def create_things(iot, debug=False):
    """Create sample Things with attributes"""
    print_step(3, f"Creating {THING_COUNT} Things with attributes")
    
    for i in range(1, THING_COUNT + 1):
        thing_name = f"Vehicle-VIN-{i:03d}"
        customer_id = str(uuid.uuid4())
        country = random.choice(COUNTRIES)
        manufacturing_date = generate_random_date()
        thing_type = random.choice(THING_TYPES)
        
        if not debug:
            print(f"\n📱 Creating Thing: {thing_name}")
            print(f"   Customer ID: {customer_id}")
            print(f"   Country: {country}")
            print(f"   Manufacturing Date: {manufacturing_date}")
            print(f"   Thing Type: {thing_type}")
            time.sleep(0.8)  # nosemgrep: arbitrary-sleep
        
        safe_create(
            iot.create_thing,
            "Thing", thing_name,
            debug=debug,
            thingName=thing_name,
            thingTypeName=thing_type,
            attributePayload={
                'attributes': {
                    'customerId': customer_id,
                    'country': country,
                    'manufacturingDate': manufacturing_date
                }
            }
        )

def add_things_to_groups(iot, debug=False):
    """Add Things to random Thing Groups"""
    print_step(4, "Adding Things to Thing Groups")
    
    for i in range(1, THING_COUNT + 1):
        thing_name = f"Vehicle-VIN-{i:03d}"
        group_name = random.choice(THING_GROUPS)
        
        try:
            if debug:
                print(f"\n🔍 DEBUG: Adding {thing_name} to group {group_name}")
                print(f"📤 API Call: add_thing_to_thing_group")
                print(f"📥 Input Parameters:")
                print(json.dumps({
                    'thingGroupName': group_name,
                    'thingName': thing_name
                }, indent=2))
            else:
                print(f"Adding {thing_name} to group {group_name}")
            
            response = iot.add_thing_to_thing_group(
                thingGroupName=group_name,
                thingName=thing_name
            )
            
            if debug:
                print(f"📤 API Response:")
                print(json.dumps(response, indent=2, default=str))
            
            print(f"✅ Added {thing_name} to {group_name}")
            time.sleep(0.3 if not debug else 1.0)  # nosemgrep: arbitrary-sleep
        except ClientError as e:
            print(f"❌ Error adding {thing_name} to {group_name}: {e.response['Error']['Message']}")
            if debug:
                print(f"🔍 DEBUG: Full error response:")
                print(json.dumps(e.response, indent=2, default=str))
            time.sleep(0.3)  # nosemgrep: arbitrary-sleep

def print_summary(iot):
    """Print summary of created resources"""
    print_step(5, "Setup Summary")
    
    try:
        things = iot.list_things()
        thing_types = iot.list_thing_types()
        thing_groups = iot.list_thing_groups()
        
        print(f"📊 Resources Created:")
        print(f"   Things: {len(things.get('things', []))}")
        print(f"   Thing Types: {len(thing_types.get('thingTypes', []))}")
        print(f"   Thing Groups: {len(thing_groups.get('thingGroups', []))}")
        
        print(f"\n🎯 Sample Thing Names:")
        for thing in things.get('things', [])[:5]:
            print(f"   - {thing['thingName']}")
        if len(things.get('things', [])) > 5:
            print(f"   ... and {len(things.get('things', [])) - 5} more")
            
    except Exception as e:
        print(f"❌ Error getting summary: {str(e)}")

def main():
    import sys
    
    try:
        # Check for debug flag
        debug_mode = '--debug' in sys.argv or '-d' in sys.argv
        
        print("🚀 AWS IoT Sample Data Setup")
        print("=" * 32)
        
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
        
        print(f"This script will create sample IoT resources for learning:")
        print(f"• {len(THING_TYPES)} Thing Types: {', '.join(THING_TYPES)}")
        print(f"• {len(THING_GROUPS)} Thing Groups: {', '.join(THING_GROUPS)}")
        print(f"• {THING_COUNT} Things with random attributes")
        
        if debug_mode:
            print(f"\n🔍 DEBUG MODE ENABLED")
            print(f"• Will show detailed API requests and responses")
            print(f"• Slower execution with extended pauses")
            print(f"• Full error details and tracebacks")
        else:
            print(f"\n💡 Tip: Use --debug or -d flag to see detailed API calls")
        
        print("=" * 32)
        
        confirm = input("Continue? (y/N): ").strip().lower()
        if confirm != 'y':
            print("Setup cancelled")
            return
        
        try:
            iot = boto3.client('iot')
            print("✅ AWS IoT client initialized")
            
            if debug_mode:
                print(f"🔍 DEBUG: Client configuration:")
                print(f"   Service: {iot.meta.service_model.service_name}")
                print(f"   API Version: {iot.meta.service_model.api_version}")
        except Exception as e:
            print(f"❌ Error initializing AWS IoT client: {str(e)}")
            print("Make sure you have AWS credentials and region configured")
            return
        
        print("\n📚 LEARNING MOMENT: AWS IoT Resource Hierarchy")
        print("AWS IoT uses a hierarchical structure to organize devices: Thing Types (templates) define device categories, Thing Groups provide organizational structure, and Things represent actual devices. This hierarchy enables scalable device management, bulk operations, and policy inheritance across your IoT fleet.")
        print("\n🔄 NEXT: We will create sample resources to demonstrate this hierarchy")
        input("Press Enter to continue...")
        
        # Execute setup steps with debug flag
        create_thing_types(iot, debug=debug_mode)
        
        print("\n📚 LEARNING MOMENT: Thing Groups - Device Organization")
        print("Thing Groups provide hierarchical organization for your IoT devices, similar to folders for files. They enable bulk operations, policy inheritance, and logical grouping by location, function, or business criteria. Groups can contain other groups, creating flexible organizational structures for large IoT deployments.")
        print("\n🔄 NEXT: We will create Thing Groups for device organization")
        input("Press Enter to continue...")
        
        create_thing_groups(iot, debug=debug_mode)
        
        print("\n📚 LEARNING MOMENT: Things - Device Registration")
        print("Things represent your actual IoT devices in AWS IoT Core. Each Thing has a unique name, optional attributes (like serial number, location), and can be assigned to a Thing Type for standardization. Things are the foundation for device management, security policies, and shadow state synchronization.")
        print("\n🔄 NEXT: We will create individual Things with realistic attributes")
        input("Press Enter to continue...")
        
        create_things(iot, debug=debug_mode)
        
        print("\n📚 LEARNING MOMENT: Thing-Group Relationships")
        print("Adding Things to Groups creates organizational relationships that enable bulk operations and policy inheritance. A Thing can belong to multiple groups, and groups can be nested. This hierarchy is essential for managing device fleets at scale, applying policies, and organizing devices by business logic.")
        print("\n🔄 NEXT: We will assign Things to appropriate Groups")
        input("Press Enter to continue...")
        
        add_things_to_groups(iot, debug=debug_mode)
        print_summary(iot)
        
        print(f"\n🎉 Setup complete! You can now use iot_registry_explorer.py to explore the data.")
        
        if debug_mode:
            print(f"\n🔍 DEBUG: Session completed with detailed API logging")
        
    except KeyboardInterrupt:
        print("\n\n👋 Setup cancelled by user. Goodbye!")

if __name__ == "__main__":
    main()