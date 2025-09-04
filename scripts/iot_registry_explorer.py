#!/usr/bin/env python3
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import boto3
import json
import os
import sys
from botocore.exceptions import ClientError, NoCredentialsError

def check_credentials():
    """Validate AWS credentials are available"""
    required_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY']
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if missing:
        print("❌ Missing required environment variables:")
        for var in missing:
            print(f"   - {var}")
        print("\nPlease export your AWS credentials:")
        print("export AWS_ACCESS_KEY_ID=<your-access-key>")
        print("export AWS_SECRET_ACCESS_KEY=<your-secret-key>")
        print("export AWS_SESSION_TOKEN=<your-session-token>  # Optional for temporary credentials")
        sys.exit(1)

def get_http_info(operation, params=None):
    """Get HTTP method and path for the operation"""
    http_info = {
        'list_things': ('GET', '/things'),
        'list_certificates': ('GET', '/certificates'),
        'list_thing_groups': ('GET', '/thing-groups'),
        'list_thing_types': ('GET', '/thing-types'),
        'describe_thing': ('GET', f"/things/{params.get('thingName', '<thingName>') if params else '<thingName>'}"),
        'describe_thing_group': ('GET', f"/thing-groups/{params.get('thingGroupName', '<thingGroupName>') if params else '<thingGroupName>'}"),
        'describe_thing_type': ('GET', f"/thing-types/{params.get('thingTypeName', '<thingTypeName>') if params else '<thingTypeName>'}"),
        'describe_endpoint': ('GET', '/endpoint')
    }
    return http_info.get(operation, ('GET', '/unknown'))

def print_api_call(operation, params=None, description=""):
    """Display the API call being made with explanation"""
    method, path = get_http_info(operation, params)
    print(f"\n🔄 API Call: {operation}")
    print(f"🌐 HTTP Request: {method} https://iot.<region>.amazonaws.com{path}")
    if description:
        print(f"ℹ️  Description: {description}")
    if params:
        print(f"📥 Input Parameters: {json.dumps(params, indent=2)}")
    else:
        print("📥 Input Parameters: None (this API requires no input parameters)")

def print_response(response, explanation=""):
    """Display the API response with explanation"""
    if explanation:
        print(f"💡 Response Explanation: {explanation}")
    print(f"📤 Response Payload: {json.dumps(response, indent=2, default=str)}")

def list_things_paginated(iot, max_results, debug=False):
    """List Things with pagination"""
    print(f"\n📚 LEARNING MOMENT: Pagination")
    print(f"Pagination allows you to retrieve large datasets in smaller chunks. This is essential when managing hundreds or thousands of devices to avoid timeouts and memory issues.")
    print(f"\n🔄 Listing Things with pagination (max {max_results} per page)...")
    
    next_token = None
    page = 1
    total_things = 0
    
    while True:
        params = {'maxResults': max_results}
        if next_token:
            params['nextToken'] = next_token
            
        safe_api_call(
            iot.list_things, "list_things",
            description=f"Page {page} - Retrieves up to {max_results} Things",
            explanation=f"Returns paginated results with nextToken for continuation",
            debug=debug,
            **params
        )
        
        response = iot.list_things(**params)
        things = response.get('things', [])
        total_things += len(things)
        
        print(f"\n📊 Page {page} Summary: {len(things)} Things retrieved")
        
        next_token = response.get('nextToken')
        if not next_token or not things:
            break
            
        page += 1
        continue_paging = input(f"\nContinue to next page? (y/N): ").strip().lower()
        if continue_paging != 'y':
            break
    
    print(f"\n🏁 Pagination Complete: {total_things} total Things found across {page} page(s)")

def list_things_by_type(iot, thing_type, debug=False):
    """List Things filtered by Thing Type"""
    print(f"\n📚 LEARNING MOMENT: Filtering by Thing Type")
    print(f"Filtering allows you to find specific categories of devices. Thing Types act as templates that group similar devices together.")
    print(f"\n🔄 Filtering Things by Thing Type: {thing_type}...")
    
    safe_api_call(
        iot.list_things, "list_things",
        description=f"Retrieves Things filtered by Thing Type '{thing_type}'",
        explanation="Returns only Things that match the specified Thing Type",
        debug=debug,
        thingTypeName=thing_type
    )
    
    response = iot.list_things(thingTypeName=thing_type)
    things = response.get('things', [])
    print(f"\n📊 Filter Results: {len(things)} Things found with Thing Type '{thing_type}'")

def list_things_by_attribute(iot, attr_name, attr_value, debug=False):
    """List Things filtered by attribute"""
    print(f"\n📚 LEARNING MOMENT: Filtering by Attributes")
    print(f"Attribute filtering helps you find devices with specific characteristics. This is useful for targeting devices by location, customer, or other metadata.")
    print(f"\n🔄 Filtering Things by attribute {attr_name}={attr_value}...")
    
    safe_api_call(
        iot.list_things, "list_things",
        description=f"Retrieves Things filtered by attribute '{attr_name}={attr_value}'",
        explanation="Returns only Things that have the specified attribute value",
        debug=debug,
        attributeName=attr_name,
        attributeValue=attr_value
    )
    
    response = iot.list_things(attributeName=attr_name, attributeValue=attr_value)
    things = response.get('things', [])
    print(f"\n📊 Filter Results: {len(things)} Things found with {attr_name}='{attr_value}'")

def safe_api_call(func, operation, description="", explanation="", debug=True, **kwargs):
    """Execute API call with error handling and explanations"""
    try:
        if debug:
            print_api_call(operation, kwargs if kwargs else None, description)
        else:
            print(f"🔄 Executing: {operation}")
        
        response = func(**kwargs)
        
        if debug:
            print_response(response, explanation)
        else:
            print(f"✅ {operation} completed")
            # Show condensed response for non-debug mode
            if response:
                if isinstance(response, dict):
                    # Show key metrics instead of full response
                    if 'things' in response:
                        print(f"📊 Found {len(response['things'])} Things")
                        if response['things']:
                            print("   Thing Names:")
                            for thing in response['things']:
                                thing_type = f" ({thing.get('thingTypeName', 'No Type')})" if thing.get('thingTypeName') else ""
                                print(f"   • {thing['thingName']}{thing_type}")
                    elif 'certificates' in response:
                        print(f"📊 Found {len(response['certificates'])} Certificates")
                        if response['certificates']:
                            print("   Certificate IDs:")
                            for cert in response['certificates']:
                                status = cert.get('status', 'Unknown')
                                print(f"   • {cert['certificateId'][:16]}... ({status})")
                    elif 'thingGroups' in response:
                        print(f"📊 Found {len(response['thingGroups'])} Thing Groups")
                        if response['thingGroups']:
                            print("   Group Names:")
                            for group in response['thingGroups']:
                                print(f"   • {group['groupName']}")
                    elif 'thingTypes' in response:
                        print(f"📊 Found {len(response['thingTypes'])} Thing Types")
                        if response['thingTypes']:
                            print("   Type Names:")
                            for thing_type in response['thingTypes']:
                                print(f"   • {thing_type['thingTypeName']}")
                    elif 'thingName' in response:
                        # Handle describe_thing response
                        print(f"📊 Thing Details:")
                        print(f"   Name: {response['thingName']}")
                        if response.get('thingTypeName'):
                            print(f"   Type: {response['thingTypeName']}")
                        if response.get('attributes'):
                            print(f"   Attributes: {len(response['attributes'])} defined")
                            for key, value in list(response['attributes'].items())[:3]:  # Show first 3 attributes
                                print(f"     • {key}: {value}")
                            if len(response['attributes']) > 3:
                                print(f"     ... and {len(response['attributes']) - 3} more")
                        print(f"   Version: {response.get('version', 'Unknown')}")
                    elif 'thingGroupName' in response:
                        # Handle describe_thing_group response
                        print(f"📊 Thing Group Details:")
                        print(f"   Name: {response['thingGroupName']}")
                        if response.get('thingGroupProperties', {}).get('thingGroupDescription'):
                            print(f"   Description: {response['thingGroupProperties']['thingGroupDescription']}")
                        if response.get('thingGroupProperties', {}).get('attributePayload', {}).get('attributes'):
                            attrs = response['thingGroupProperties']['attributePayload']['attributes']
                            print(f"   Attributes: {len(attrs)} defined")
                    elif 'thingTypeName' in response:
                        # Handle describe_thing_type response
                        print(f"📊 Thing Type Details:")
                        print(f"   Name: {response['thingTypeName']}")
                        if response.get('thingTypeProperties', {}).get('description'):
                            print(f"   Description: {response['thingTypeProperties']['description']}")
                        if response.get('thingTypeProperties', {}).get('searchableAttributes'):
                            attrs = response['thingTypeProperties']['searchableAttributes']
                            print(f"   Searchable Attributes: {', '.join(attrs)}")
                    elif 'endpointAddress' in response:
                        # Handle describe_endpoint response
                        print(f"📊 IoT Endpoint:")
                        print(f"   URL: {response['endpointAddress']}")
                    else:
                        print(f"📊 Response received")
        
        return response
    except ClientError as e:
        print(f"❌ API Error: {e.response['Error']['Code']} - {e.response['Error']['Message']}")
        if debug:
            print(f"🔍 DEBUG: Full error response:")
            print(json.dumps(e.response, indent=2, default=str))
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        if debug:
            import traceback
            print(f"🔍 DEBUG: Full traceback:")
            traceback.print_exc()

def main():
    try:
        # Check for debug flag
        debug_mode = '--debug' in sys.argv or '-d' in sys.argv
        
        print("🚀 AWS IoT Registry API Explorer")
        print("=" * 40)
        
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
        
        print("Interactive exploration of AWS IoT Registry APIs with detailed explanations.")
        
        if debug_mode:
            print(f"\n🔍 DEBUG MODE ENABLED")
            print(f"• Full API request/response details")
            print(f"• Complete HTTP information")
            print(f"• Enhanced error diagnostics")
        else:
            print(f"\n💡 Tip: Use --debug or -d flag for detailed API information")
            print(f"• Condensed mode shows key metrics only")
            print(f"• Debug mode shows complete API details")
        
        print("=" * 40)
        
        check_credentials()
        
        try:
            iot = boto3.client('iot')
            print("✅ AWS IoT client initialized successfully")
            
            if debug_mode:
                print(f"🔍 DEBUG: Client configuration:")
                print(f"   Region: {iot.meta.region_name}")
                print(f"   Service: {iot.meta.service_model.service_name}")
                print(f"   API Version: {iot.meta.service_model.api_version}")
        except NoCredentialsError:
            print("❌ Invalid AWS credentials")
            sys.exit(1)
        
        print("\n📚 LEARNING MOMENT: AWS IoT Registry APIs - Device Management")
        print("The AWS IoT Registry is the central database that stores information about your IoT devices (Things), their organization (Thing Groups), device templates (Thing Types), and security certificates. These APIs allow you to programmatically manage your entire IoT device fleet. Understanding these operations is fundamental to building scalable IoT solutions.")
        print("\n🔄 NEXT: We will explore 8 core Registry APIs with detailed explanations")
        try:
            input("Press Enter to continue...")
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            return
    
        while True:
            try:
                print("\n📋 Available Operations:")
                print("1. List Things")
                print("2. List Certificates") 
                print("3. List Thing Groups")
                print("4. List Thing Types")
                print("5. Describe Thing")
                print("6. Describe Thing Group")
                print("7. Describe Thing Type")
                print("8. Describe Endpoint")
                print("9. Exit")
                
                choice = input("\nSelect operation (1-9): ").strip()
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
        
            if choice == '1':
                print("\n📚 LEARNING MOMENT: List Things - Device Discovery")
                print("The list_things API retrieves all IoT devices (Things) in your account. This is essential for device inventory management, monitoring fleet size, and discovering devices by attributes. You can use pagination and filtering to handle device fleets efficiently.")
                print("\n🔄 NEXT: We will call the list_things API with different options")
                input("Press Enter to continue...")
                
                # Ask for listing options
                print("\n🔍 List Things Options:")
                print("   1. List all Things (basic)")
                print("   2. List Things with pagination")
                print("   3. Filter Things by Thing Type")
                print("   4. Filter Things by attribute")
                
                option = input("Select option (1-4): ").strip()
                
                if option == '2':
                    max_results = input("Enter max results per page (default 5): ").strip()
                    max_results = int(max_results) if max_results.isdigit() else 5
                    list_things_paginated(iot, max_results, debug_mode)
                elif option == '3':
                    thing_type = input("Enter Thing Type name (e.g., SedanVehicle): ").strip()
                    if thing_type:
                        list_things_by_type(iot, thing_type, debug_mode)
                    else:
                        print("❌ No Thing Type specified")
                elif option == '4':
                    attr_name = input("Enter attribute name (e.g., country): ").strip()
                    attr_value = input("Enter attribute value (e.g., USA): ").strip()
                    if attr_name and attr_value:
                        list_things_by_attribute(iot, attr_name, attr_value, debug_mode)
                    else:
                        print("❌ Attribute name and value required")
                else:
                    safe_api_call(
                        iot.list_things, "list_things",
                        description="Retrieves a paginated list of all IoT Things in your AWS account",
                        explanation="Returns an array of Thing objects with basic metadata like name, type, and attributes",
                        debug=debug_mode
                    )
                
                input("\nPress Enter to return to menu...")
                
            elif choice == '2':
                print("\n📚 LEARNING MOMENT: List Certificates - Security Inventory")
                print("X.509 certificates are the foundation of IoT device security. Each certificate uniquely identifies a device and enables secure communication with AWS IoT Core. This API helps you audit your security posture, track certificate lifecycle, and identify devices that need certificate rotation.")
                print("\n🔄 NEXT: We will retrieve all certificates and examine their security properties")
                input("Press Enter to continue...")
                
                safe_api_call(
                    iot.list_certificates, "list_certificates",
                    description="Retrieves a list of X.509 certificates registered in your AWS IoT account",
                    explanation="Returns certificate metadata including ID, ARN, status, and creation date",
                    debug=debug_mode
                )
                input("\nPress Enter to return to menu...")
                
            elif choice == '3':
                print("\n📚 LEARNING MOMENT: List Thing Groups - Device Organization")
                print("Thing Groups provide hierarchical organization for your IoT devices, similar to folders for files. They enable bulk operations, policy inheritance, and logical grouping by location, function, or any business criteria. This is crucial for managing large-scale IoT deployments.")
                print("\n🔄 NEXT: We will explore your Thing Groups and their organizational structure")
                input("Press Enter to continue...")
                
                safe_api_call(
                    iot.list_thing_groups, "list_thing_groups",
                    description="Retrieves a list of Thing Groups used to organize and manage IoT devices",
                    explanation="Returns group names, ARNs, and basic properties for hierarchical device organization",
                    debug=debug_mode
                )
                input("\nPress Enter to return to menu...")
                
            elif choice == '4':
                print("\n📚 LEARNING MOMENT: List Thing Types - Device Templates")
                print("Thing Types are templates that define categories of IoT devices. They act as blueprints specifying common attributes and behaviors for similar devices. For example, a 'SedanVehicle' type might define attributes like engine type and seating capacity. Thing Types help organize your device fleet and enable standardized device management.")
                print("\n🔄 NEXT: We will examine your Thing Types and their attribute schemas")
                input("Press Enter to continue...")
                
                safe_api_call(
                    iot.list_thing_types, "list_thing_types",
                    description="Retrieves a list of Thing Types that define device templates and attributes",
                    explanation="Returns type names, ARNs, and metadata for device categorization templates",
                    debug=debug_mode
                )
                input("\nPress Enter to return to menu...")
                
            elif choice == '5':
                print("\n📚 LEARNING MOMENT: Describe Thing - Device Details")
                print("The describe_thing API provides complete information about a specific IoT device, including its attributes, Thing Type, version, and unique identifiers. This is essential for device troubleshooting, configuration management, and understanding device relationships within your IoT architecture.")
                print("\n🔄 NEXT: We will examine detailed information for a specific Thing")
                input("Press Enter to continue...")
                
                # Show available Things
                try:
                    things_response = iot.list_things()
                    if things_response.get('things'):
                        print(f"\n📋 Available Things ({len(things_response['things'])}):")  
                        for i, thing in enumerate(things_response['things'][:10], 1):
                            thing_type = f" ({thing.get('thingTypeName', 'No Type')})" if thing.get('thingTypeName') else ""
                            print(f"   {i}. {thing['thingName']}{thing_type}")
                        if len(things_response['things']) > 10:
                            print(f"   ... and {len(things_response['things']) - 10} more")
                    else:
                        print("\n⚠️ No Things found in your account")
                except Exception as e:
                    print(f"\n⚠️ Could not list Things: {str(e)}")
                
                thing_name = input("\nEnter Thing name: ").strip()
                if thing_name:
                    safe_api_call(
                        iot.describe_thing, "describe_thing",
                        description="Retrieves detailed information about a specific IoT Thing",
                        explanation="Returns complete Thing details including attributes, type, version, and ARN",
                        debug=debug_mode,
                        thingName=thing_name
                    )
                    input("\nPress Enter to return to menu...")
                    
            elif choice == '6':
                print("\n📚 LEARNING MOMENT: Describe Thing Group - Group Management")
                print("Thing Group details reveal the organizational structure of your IoT fleet. You can see group properties, parent-child hierarchies, attached policies, and member devices. This information is vital for understanding access control, policy inheritance, and device organization strategies.")
                print("\n🔄 NEXT: We will examine detailed properties of a specific Thing Group")
                input("Press Enter to continue...")
                
                # Show available Thing Groups
                try:
                    groups_response = iot.list_thing_groups()
                    if groups_response.get('thingGroups'):
                        print(f"\n📋 Available Thing Groups ({len(groups_response['thingGroups'])}):")  
                        for i, group in enumerate(groups_response['thingGroups'], 1):
                            print(f"   {i}. {group['groupName']}")
                    else:
                        print("\n⚠️ No Thing Groups found in your account")
                except Exception as e:
                    print(f"\n⚠️ Could not list Thing Groups: {str(e)}")
                
                group_name = input("\nEnter Thing Group name: ").strip()
                if group_name:
                    safe_api_call(
                        iot.describe_thing_group, "describe_thing_group",
                        description="Retrieves detailed information about a specific Thing Group",
                        explanation="Returns group properties, hierarchy info, and associated policies",
                        debug=debug_mode,
                        thingGroupName=group_name
                    )
                    input("\nPress Enter to return to menu...")
                    
            elif choice == '7':
                print("\n📚 LEARNING MOMENT: Describe Thing Type - Template Analysis")
                print("Thing Type details show the blueprint definition for device categories. You can examine searchable attributes, property constraints, and metadata that define how devices of this type should be structured. This helps ensure consistent device registration and enables efficient fleet queries.")
                print("\n🔄 NEXT: We will analyze the schema and properties of a specific Thing Type")
                input("Press Enter to continue...")
                
                # Show available Thing Types
                try:
                    types_response = iot.list_thing_types()
                    if types_response.get('thingTypes'):
                        print(f"\n📋 Available Thing Types ({len(types_response['thingTypes'])}):")  
                        for i, thing_type in enumerate(types_response['thingTypes'], 1):
                            print(f"   {i}. {thing_type['thingTypeName']}")
                    else:
                        print("\n⚠️ No Thing Types found in your account")
                except Exception as e:
                    print(f"\n⚠️ Could not list Thing Types: {str(e)}")
                
                type_name = input("\nEnter Thing Type name: ").strip()
                if type_name:
                    safe_api_call(
                        iot.describe_thing_type, "describe_thing_type",
                        description="Retrieves detailed information about a specific Thing Type",
                        explanation="Returns type properties, searchable attributes, and creation metadata",
                        debug=debug_mode,
                        thingTypeName=type_name
                    )
                    input("\nPress Enter to return to menu...")
                    
            elif choice == '8':
                print("\n📚 LEARNING MOMENT: Describe Endpoint - Connection Discovery")
                print("IoT endpoints are the gateway URLs that devices use to connect to AWS IoT Core. Different endpoint types serve different purposes: Data-ATS for device communication, CredentialProvider for authentication, and Jobs for device management. Understanding endpoints is crucial for device connectivity configuration.")
                print("\n🔄 NEXT: We will discover the endpoint URL for device connections")
                input("Press Enter to continue...")
                
                endpoint_type = input("Enter endpoint type (iot:Data-ATS, iot:Data, iot:CredentialProvider, iot:Jobs) [default: iot:Data-ATS]: ").strip()
                if not endpoint_type:
                    endpoint_type = "iot:Data-ATS"
                safe_api_call(
                    iot.describe_endpoint, "describe_endpoint",
                    description="Retrieves the IoT endpoint URL for your AWS account and region",
                    explanation="Returns the HTTPS endpoint URL used for device communication and data operations",
                    debug=debug_mode,
                    endpointType=endpoint_type
                )
                input("\nPress Enter to return to menu...")
                
            elif choice == '9':
                print("👋 Goodbye!")
                break
                
            else:
                print("❌ Invalid choice. Please select 1-9.")
                
            # Handle Ctrl+C in continue prompts
            if choice != '9':
                try:
                    pass  # Continue prompts are already handled in individual sections
                except KeyboardInterrupt:
                    print("\n\n👋 Goodbye!")
                    break
    
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")

if __name__ == "__main__":
    main()