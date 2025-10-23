#!/usr/bin/env python3
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import json
import os
import sys

# Add i18n to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "i18n"))

import boto3
from botocore.exceptions import ClientError, NoCredentialsError, NoRegionError

from language_selector import get_language
from loader import load_messages

# Global variables
USER_LANG = "en"
messages = {}


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

    print(f"\n📚 LEARNING MOMENT: {moment.get('title', '')}")
    print(moment.get("content", ""))
    print(f"\n🔄 NEXT: {moment.get('next', '')}")


def check_credentials():
    """Validate AWS credentials are available"""
    required_vars = ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]
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
        "list_things": ("GET", "/things"),
        "list_certificates": ("GET", "/certificates"),
        "list_thing_groups": ("GET", "/thing-groups"),
        "list_thing_types": ("GET", "/thing-types"),
        "describe_thing": (
            "GET",
            f"/things/{params.get('thingName', '<thingName>') if params else '<thingName>'}",
        ),
        "describe_thing_group": (
            "GET",
            f"/thing-groups/{params.get('thingGroupName', '<thingGroupName>') if params else '<thingGroupName>'}",
        ),
        "describe_thing_type": (
            "GET",
            f"/thing-types/{params.get('thingTypeName', '<thingTypeName>') if params else '<thingTypeName>'}",
        ),
        "describe_endpoint": ("GET", "/endpoint"),
    }
    return http_info.get(operation, ("GET", "/unknown"))


def print_api_call(operation, params=None, description=""):
    """Display the API call being made with explanation"""
    method, path = get_http_info(operation, params)
    print(f"\n🔄 {get_message('api_call_label')}: {operation}")
    print(f"🌐 {get_message('http_request_label')}: {method} https://iot.<region>.amazonaws.com{path}")
    if description:
        print(f"ℹ️  {get_message('description_label')}: {description}")
    if params:
        print(f"📥 {get_message('input_parameters_label')}: {json.dumps(params, indent=2)}")
    else:
        print(f"📥 {get_message('input_parameters_label')}: {get_message('no_input_parameters')}")


def print_response(response, explanation=""):
    """Display the API response with explanation"""
    if explanation:
        print(f"💡 {get_message('response_explanation_label')}: {explanation}")
    print(f"📤 {get_message('response_payload_label')}: {json.dumps(response, indent=2, default=str)}")


def list_things_paginated(iot, max_results, debug=False):
    """List Things with pagination"""
    print(f"\n{get_message('pagination_learning_title')}")
    print(get_message("pagination_learning_content"))
    print(f"\n{get_message('pagination_listing').format(max_results)}")

    next_token = None
    page = 1
    total_things = 0

    while True:
        params = {"maxResults": max_results}
        if next_token:
            params["nextToken"] = next_token

        safe_api_call(
            iot.list_things,
            "list_things",
            description=get_message("api_desc_list_things_paginated").format(page, max_results),
            explanation=get_message("api_explain_list_things"),
            debug=debug,
            **params,
        )

        response = iot.list_things(**params)
        things = response.get("things", [])
        total_things += len(things)

        print(f"\n{get_message('page_summary').format(page, len(things))}")

        next_token = response.get("nextToken")
        if not next_token or not things:
            break

        page += 1
        continue_paging = input(f"\n{get_message('continue_next_page')}").strip().lower()
        if continue_paging not in [
            "y",
            "s",
        ]:  # Accept both 'y' (yes) and 's' (sí) for Spanish
            break

    print(f"\n{get_message('pagination_complete').format(total_things, page)}")


def list_things_by_type(iot, thing_type, debug=False):
    """List Things filtered by Thing Type"""
    print(f"\n{get_message('filter_by_type_learning_title')}")
    print(get_message("filter_by_type_learning_content"))
    print(f"\n{get_message('filtering_by_type').format(thing_type)}")

    safe_api_call(
        iot.list_things,
        "list_things",
        description=get_message("api_desc_list_things_by_type").format(thing_type),
        explanation=get_message("api_explain_list_things"),
        debug=debug,
        thingTypeName=thing_type,
    )

    response = iot.list_things(thingTypeName=thing_type)
    things = response.get("things", [])
    print(f"\n{get_message('filter_type_results').format(len(things), thing_type)}")


def list_things_by_attribute(iot, attr_name, attr_value, debug=False):
    """List Things filtered by attribute"""
    print(f"\n{get_message('filter_by_attribute_learning_title')}")
    print(get_message("filter_by_attribute_learning_content"))
    print(f"\n{get_message('filtering_by_attribute').format(attr_name, attr_value)}")

    safe_api_call(
        iot.list_things,
        "list_things",
        description=get_message("api_desc_list_things_by_attribute").format(attr_name, attr_value),
        explanation=get_message("api_explain_list_things"),
        debug=debug,
        attributeName=attr_name,
        attributeValue=attr_value,
    )

    response = iot.list_things(attributeName=attr_name, attributeValue=attr_value)
    things = response.get("things", [])
    print(f"\n{get_message('filter_attribute_results').format(len(things), attr_name, attr_value)}")


def safe_api_call(func, operation, description="", explanation="", debug=True, **kwargs):
    """Execute API call with error handling and explanations"""
    try:
        if debug:
            print_api_call(operation, kwargs if kwargs else None, description)
        else:
            print(f"{get_message('executing')} {operation}")

        response = func(**kwargs)

        if debug:
            print_response(response, explanation)
        else:
            print(f"✅ {operation} {get_message('completed')}")
            # Show condensed response for non-debug mode
            if response:
                if isinstance(response, dict):
                    # Show key metrics instead of full response
                    if "things" in response:
                        print(get_message("found_things").format(len(response["things"])))
                        if response["things"]:
                            print(get_message("thing_names"))
                            for thing in response["things"]:
                                thing_type = (
                                    f" ({thing.get('thingTypeName', 'No Type')})" if thing.get("thingTypeName") else ""
                                )
                                print(f"   • {thing['thingName']}{thing_type}")
                    elif "certificates" in response:
                        print(get_message("found_certificates").format(len(response["certificates"])))
                        if response["certificates"]:
                            print(get_message("certificate_ids"))
                            for cert in response["certificates"]:
                                status = cert.get("status", "Unknown")
                                print(f"   • {cert['certificateId'][:16]}... ({status})")
                    elif "thingGroups" in response:
                        print(get_message("found_thing_groups").format(len(response["thingGroups"])))
                        if response["thingGroups"]:
                            print(get_message("group_names"))
                            for group in response["thingGroups"]:
                                print(f"   • {group['groupName']}")
                    elif "thingTypes" in response:
                        print(get_message("found_thing_types").format(len(response["thingTypes"])))
                        if response["thingTypes"]:
                            print(get_message("type_names"))
                            for thing_type in response["thingTypes"]:
                                print(f"   • {thing_type['thingTypeName']}")
                    elif "thingName" in response:
                        # Handle describe_thing response
                        print(get_message("thing_details"))
                        print(f"   {get_message('name_label')}: {response['thingName']}")
                        if response.get("thingTypeName"):
                            print(f"   {get_message('type_label')}: {response['thingTypeName']}")
                        if response.get("attributes"):
                            print(f"   Attributes: {len(response['attributes'])} defined")
                            for key, value in list(response["attributes"].items())[:3]:  # Show first 3 attributes
                                print(f"     • {key}: {value}")
                            if len(response["attributes"]) > 3:
                                print(f"     ... and {len(response['attributes']) - 3} more")
                        print(f"   Version: {response.get('version', 'Unknown')}")
                    elif "thingGroupName" in response:
                        # Handle describe_thing_group response
                        print(get_message("thing_group_details"))
                        print(f"   {get_message('name_label')}: {response['thingGroupName']}")
                        if response.get("thingGroupProperties", {}).get("thingGroupDescription"):
                            print(
                                f"   {get_message('description_simple')}: {response['thingGroupProperties']['thingGroupDescription']}"
                            )
                        if response.get("thingGroupProperties", {}).get("attributePayload", {}).get("attributes"):
                            attrs = response["thingGroupProperties"]["attributePayload"]["attributes"]
                            print(f"   Attributes: {len(attrs)} defined")
                    elif "thingTypeName" in response:
                        # Handle describe_thing_type response
                        print(get_message("thing_type_details"))
                        print(f"   {get_message('name_label')}: {response['thingTypeName']}")
                        if response.get("thingTypeProperties", {}).get("description"):
                            print(f"   {get_message('description_simple')}: {response['thingTypeProperties']['description']}")
                        if response.get("thingTypeProperties", {}).get("searchableAttributes"):
                            attrs = response["thingTypeProperties"]["searchableAttributes"]
                            print(f"   Searchable Attributes: {', '.join(attrs)}")
                    elif "endpointAddress" in response:
                        # Handle describe_endpoint response
                        print("📊 IoT Endpoint:")
                        print(f"   URL: {response['endpointAddress']}")
                    else:
                        print("📊 Response received")

        return response
    except ClientError as e:
        print(f"{get_message('api_error')} {e.response['Error']['Code']} - {e.response['Error']['Message']}")
        if debug:
            print(get_message("debug_full_error"))
            print(json.dumps(e.response, indent=2, default=str))
    except Exception as e:
        print(f"{get_message('error')} {str(e)}")
        if debug:
            import traceback

            print(get_message("debug_full_traceback"))
            traceback.print_exc()


def main():
    try:
        # Get user's preferred language
        global USER_LANG, messages
        USER_LANG = get_language()

        # Load messages for this script and language
        messages = load_messages("iot_registry_explorer", USER_LANG)

        # Check for debug flag
        debug_mode = "--debug" in sys.argv or "-d" in sys.argv

        print(get_message("title"))
        print(get_message("separator"))

        # Display AWS context first
        try:
            sts = boto3.client("sts")
            iot = boto3.client("iot")
            identity = sts.get_caller_identity()

            print(get_message("aws_config"))
            print(f"   {get_message('account_id')}: {identity['Account']}")
            print(f"   {get_message('region')}: {iot.meta.region_name}")
            print()

        except Exception as e:
            print(f"{get_message('aws_context_error')} {str(e)}")
            print(get_message("aws_credentials_reminder"))
            print()

        print(get_message("description"))

        if debug_mode:
            print(f"\n{get_message('debug_enabled')}")
            for feature in get_message("debug_features"):
                print(feature)
        else:
            print(f"\n{get_message('tip')}")
            for feature in get_message("tip_features"):
                print(feature)

        print(get_message("separator"))

        check_credentials()

        try:
            iot = boto3.client("iot")
            print(get_message("client_initialized"))

            if debug_mode:
                print("🔍 DEBUG: Client configuration:")
                print(f"   Region: {iot.meta.region_name}")
                print(f"   Service: {iot.meta.service_model.service_name}")
                print(f"   API Version: {iot.meta.service_model.api_version}")
        except NoCredentialsError:
            print(get_message("invalid_credentials"))
            sys.exit(1)
        except NoRegionError:
            print(get_message("no_region_error"))
            for instruction in get_message("region_setup_instructions"):
                print(f"   {instruction}")
            sys.exit(1)

        print(f"\n📚 LEARNING MOMENT: {get_message('learning_intro_title')}")
        print(get_message("learning_intro_content"))
        print(f"\n🔄 NEXT: {get_message('learning_intro_next')}")
        try:
            input(get_message("press_enter"))
        except KeyboardInterrupt:
            print(f"\n\n{get_message('goodbye')}")
            return

        while True:
            try:
                print(f"\n{get_message('operations_menu')}")
                for operation in get_message("operations"):
                    print(operation)

                choice = input(f"\n{get_message('select_operation')} ").strip()
            except KeyboardInterrupt:
                print(f"\n\n{get_message('goodbye')}")
                break

            if choice == "1":
                print_learning_moment("list_things")
                input(get_message("press_enter"))

                # Ask for listing options
                print(f"\n{get_message('list_things_options')}")
                for menu_item in get_message("list_things_menu"):
                    print(menu_item)

                option = input(get_message("select_option")).strip()

                if option == "2":
                    max_results = input(get_message("max_results_prompt")).strip()
                    max_results = int(max_results) if max_results.isdigit() else 5
                    list_things_paginated(iot, max_results, debug_mode)
                elif option == "3":
                    thing_type = input(get_message("thing_type_prompt")).strip()
                    if thing_type:
                        list_things_by_type(iot, thing_type, debug_mode)
                    else:
                        print(get_message("no_thing_type"))
                elif option == "4":
                    attr_name = input(get_message("attribute_name_prompt")).strip()
                    attr_value = input(get_message("attribute_value_prompt")).strip()
                    if attr_name and attr_value:
                        list_things_by_attribute(iot, attr_name, attr_value, debug_mode)
                    else:
                        print(get_message("attribute_required"))
                else:
                    safe_api_call(
                        iot.list_things,
                        "list_things",
                        description=get_message("api_desc_list_things"),
                        explanation=get_message("api_explain_list_things"),
                        debug=debug_mode,
                    )

                input(f"\n{get_message('return_to_menu')}")

            elif choice == "2":
                print_learning_moment("list_certificates")
                input(get_message("press_enter"))

                safe_api_call(
                    iot.list_certificates,
                    "list_certificates",
                    description=get_message("api_desc_list_certificates"),
                    explanation=get_message("api_explain_list_certificates"),
                    debug=debug_mode,
                )
                input(f"\n{get_message('return_to_menu')}")

            elif choice == "3":
                print_learning_moment("list_thing_groups")
                input(get_message("press_enter"))

                safe_api_call(
                    iot.list_thing_groups,
                    "list_thing_groups",
                    description=get_message("api_desc_list_thing_groups"),
                    explanation=get_message("api_explain_list_thing_groups"),
                    debug=debug_mode,
                )
                input(f"\n{get_message('return_to_menu')}")

            elif choice == "4":
                print_learning_moment("list_thing_types")
                input(get_message("press_enter"))

                safe_api_call(
                    iot.list_thing_types,
                    "list_thing_types",
                    description=get_message("api_desc_list_thing_types"),
                    explanation=get_message("api_explain_list_thing_types"),
                    debug=debug_mode,
                )
                input(f"\n{get_message('return_to_menu')}")

            elif choice == "5":
                print_learning_moment("describe_thing")
                input(get_message("press_enter"))

                # Show available Things
                try:
                    things_response = iot.list_things()
                    if things_response.get("things"):
                        print(f"\n{get_message('available_things')} ({len(things_response['things'])}):")
                        for i, thing in enumerate(things_response["things"][:10], 1):
                            thing_type = f" ({thing.get('thingTypeName', 'No Type')})" if thing.get("thingTypeName") else ""
                            print(f"   {i}. {thing['thingName']}{thing_type}")
                        if len(things_response["things"]) > 10:
                            print(f"   ... and {len(things_response['things']) - 10} more")

                        selection = input(f"\n{get_message('enter_thing_selection')}").strip()
                        thing_name = None

                        # Check if input is a number
                        if selection.isdigit():
                            thing_index = int(selection) - 1
                            if 0 <= thing_index < len(things_response["things"]):
                                thing_name = things_response["things"][thing_index]["thingName"]
                            else:
                                print(f"{get_message('invalid_selection')} 1-{len(things_response['things'])}")
                        else:
                            # Treat as thing name
                            thing_name = selection

                        if thing_name:
                            safe_api_call(
                                iot.describe_thing,
                                "describe_thing",
                                description=get_message("api_desc_describe_thing"),
                                explanation=get_message("api_explain_describe_thing"),
                                debug=debug_mode,
                                thingName=thing_name,
                            )
                    else:
                        print(f"\n{get_message('no_things_found')}")
                except Exception as e:
                    print(f"\n{get_message('could_not_list_things')} {str(e)}")

                input(f"\n{get_message('return_to_menu')}")

            elif choice == "6":
                print_learning_moment("describe_thing_group")
                input(get_message("press_enter"))

                # Show available Thing Groups
                try:
                    groups_response = iot.list_thing_groups()
                    if groups_response.get("thingGroups"):
                        print(f"\n{get_message('available_groups')} ({len(groups_response['thingGroups'])}):")
                        for i, group in enumerate(groups_response["thingGroups"], 1):
                            print(f"   {i}. {group['groupName']}")

                        selection = input(f"\n{get_message('enter_group_selection')}").strip()
                        group_name = None

                        # Check if input is a number
                        if selection.isdigit():
                            group_index = int(selection) - 1
                            if 0 <= group_index < len(groups_response["thingGroups"]):
                                group_name = groups_response["thingGroups"][group_index]["groupName"]
                            else:
                                print(f"{get_message('invalid_selection')} 1-{len(groups_response['thingGroups'])}")
                        else:
                            # Treat as group name
                            group_name = selection

                        if group_name:
                            safe_api_call(
                                iot.describe_thing_group,
                                "describe_thing_group",
                                description=get_message("api_desc_describe_thing_group"),
                                explanation=get_message("api_explain_describe_thing_group"),
                                debug=debug_mode,
                                thingGroupName=group_name,
                            )
                    else:
                        print(f"\n{get_message('no_groups_found')}")
                except Exception as e:
                    print(f"\n{get_message('could_not_list_groups')} {str(e)}")

                input(f"\n{get_message('return_to_menu')}")

            elif choice == "7":
                print_learning_moment("describe_thing_type")
                input(get_message("press_enter"))

                # Show available Thing Types
                try:
                    types_response = iot.list_thing_types()
                    if types_response.get("thingTypes"):
                        print(f"\n{get_message('available_types')} ({len(types_response['thingTypes'])}):")
                        for i, thing_type in enumerate(types_response["thingTypes"], 1):
                            print(f"   {i}. {thing_type['thingTypeName']}")

                        selection = input(f"\n{get_message('enter_type_selection')}").strip()
                        type_name = None

                        # Check if input is a number
                        if selection.isdigit():
                            type_index = int(selection) - 1
                            if 0 <= type_index < len(types_response["thingTypes"]):
                                type_name = types_response["thingTypes"][type_index]["thingTypeName"]
                            else:
                                print(f"{get_message('invalid_selection')} 1-{len(types_response['thingTypes'])}")
                        else:
                            # Treat as type name
                            type_name = selection

                        if type_name:
                            safe_api_call(
                                iot.describe_thing_type,
                                "describe_thing_type",
                                description=get_message("api_desc_describe_thing_type"),
                                explanation=get_message("api_explain_describe_thing_type"),
                                debug=debug_mode,
                                thingTypeName=type_name,
                            )
                    else:
                        print(f"\n{get_message('no_types_found')}")
                except Exception as e:
                    print(f"\n{get_message('could_not_list_types')} {str(e)}")

                input(f"\n{get_message('return_to_menu')}")

            elif choice == "8":
                print_learning_moment("describe_endpoint")
                input(get_message("press_enter"))

                endpoint_type = input(get_message("endpoint_type_prompt")).strip()
                if not endpoint_type:
                    endpoint_type = "iot:Data-ATS"
                safe_api_call(
                    iot.describe_endpoint,
                    "describe_endpoint",
                    description=get_message("api_desc_describe_endpoint"),
                    explanation=get_message("api_explain_describe_endpoint"),
                    debug=debug_mode,
                    endpointType=endpoint_type,
                )
                input(f"\n{get_message('return_to_menu')}")

            elif choice == "9":
                print(get_message("goodbye"))
                break

            else:
                print(get_message("invalid_choice"))

    except KeyboardInterrupt:
        print(f"\n\n{get_message('goodbye')}")


if __name__ == "__main__":
    main()
