#!/usr/bin/env python3
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import json
import os
import shutil
import sys
import time
import traceback

import boto3
from botocore.exceptions import ClientError

# Add i18n to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "i18n"))

from language_selector import get_language
from loader import load_messages

# Sample data patterns created by setup scripts
SAMPLE_THING_TYPES = ["SedanVehicle", "SUVVehicle", "TruckVehicle"]
SAMPLE_THING_GROUPS = ["CustomerFleet", "TestFleet", "MaintenanceFleet", "DealerFleet"]
SAMPLE_THING_PREFIX = "Vehicle-VIN-"  # Things created as Vehicle-VIN-001, Vehicle-VIN-002, etc.

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


def debug_print(message):
    """Print debug message if debug mode is enabled"""
    if DEBUG_MODE:
        print(message)


def log_api_call(operation, description, params=None, response=None):
    """Log API call details in debug mode"""
    if not DEBUG_MODE:
        return

    print(f"\n{get_message('api_call_header', operation)}")
    print(f"{get_message('api_description', description)}")

    if params:
        print(get_message("api_input_params"))
        print(json.dumps(params, indent=2, default=str))
    else:
        print(get_message("api_no_params"))

    if response is not None:
        print(get_message("api_response"))
        if response:
            print(json.dumps(response, indent=2, default=str))
        else:
            print(get_message("api_empty_response"))


def clean_certificate(iot_client, certificate_arn):
    """Clean up a certificate and its associated policies"""
    try:
        certificate_id = certificate_arn.split("/")[-1]
        print(f"  {get_message('cleaning_certificate', certificate_id)}")

        # Step 1: List and detach policies
        print(f"    {get_message('step1_list_policies')}")
        list_params = {"target": certificate_arn}
        log_api_call("list_attached_policies", "List policies attached to certificate", list_params)

        policies_response = iot_client.list_attached_policies(target=certificate_arn)
        log_api_call("list_attached_policies", "List policies attached to certificate", list_params, policies_response)

        policies = policies_response.get("policies", [])
        print(f"    {get_message('found_attached_policies', len(policies))}")

        # Detach policies
        for policy in policies:
            policy_name = policy["policyName"]
            print(f"    {get_message('detaching_policy', policy_name)}")

            detach_params = {"policyName": policy_name, "target": certificate_arn}
            log_api_call("detach_policy", "Detach policy from certificate", detach_params)

            iot_client.detach_policy(policyName=policy_name, target=certificate_arn)
            log_api_call("detach_policy", "Detach policy from certificate", detach_params, {})

        # Step 2: List and detach from Things
        list_things_params = {"principal": certificate_arn}
        log_api_call("list_principal_things", "List Things attached to certificate", list_things_params)

        things_response = iot_client.list_principal_things(principal=certificate_arn)
        log_api_call("list_principal_things", "List Things attached to certificate", list_things_params, things_response)

        things = things_response.get("things", [])

        # Detach from Things
        for thing_name in things:
            print(f"    {get_message('detaching_cert_from_thing', thing_name)}")

            detach_thing_params = {"thingName": thing_name, "principal": certificate_arn}
            log_api_call("detach_thing_principal", "Detach certificate from Thing", detach_thing_params)

            iot_client.detach_thing_principal(thingName=thing_name, principal=certificate_arn)
            log_api_call("detach_thing_principal", "Detach certificate from Thing", detach_thing_params, {})

        # Step 3: Deactivate certificate
        print(f"    {get_message('deactivating_certificate', certificate_id)}")

        update_params = {"certificateId": certificate_id, "newStatus": "INACTIVE"}
        log_api_call("update_certificate", "Deactivate certificate", update_params)

        iot_client.update_certificate(certificateId=certificate_id, newStatus="INACTIVE")
        log_api_call("update_certificate", "Deactivate certificate", update_params, {})

        print(f"    {get_message('certificate_deactivated', certificate_id)}")

        # Step 4: Delete certificate
        print(f"    {get_message('deleting_certificate', certificate_id)}")

        delete_params = {"certificateId": certificate_id}
        log_api_call("delete_certificate", "Delete certificate", delete_params)

        iot_client.delete_certificate(certificateId=certificate_id)
        log_api_call("delete_certificate", "Delete certificate", delete_params, {})

        return True

    except Exception as e:
        print(f"    {get_message('error_cleaning_certificate', certificate_id, str(e))}")
        if DEBUG_MODE:
            print(f"{get_message('debug_full_error')}")
            print(json.dumps(str(e), indent=2))
            print(f"{get_message('debug_full_traceback')}")
            traceback.print_exc()
        return False


def cleanup_sample_things(iot_client):
    """Clean up sample Things and their certificates"""
    print(f"\n{get_message('step1_title')}")
    print(get_message("step_separator"))

    # List all Things
    print(get_message("listing_things"))

    log_api_call("list_things", "List all Things to find sample Things")

    try:
        response = iot_client.list_things()
        log_api_call("list_things", "List all Things to find sample Things", None, response)

        all_things = response.get("things", [])

        # Filter sample Things
        sample_things = [thing for thing in all_things if thing["thingName"].startswith(SAMPLE_THING_PREFIX)]

        print(get_message("found_sample_things", len(sample_things)))

        certificates_cleaned = 0

        for thing in sample_things:
            thing_name = thing["thingName"]
            print(f"\n{get_message('processing_thing', thing_name)}")

            # List principals (certificates) for this Thing
            print(f"  {get_message('listing_principals', thing_name)}")

            list_principals_params = {"thingName": thing_name}
            log_api_call("list_thing_principals", "List certificates attached to Thing", list_principals_params)

            try:
                principals_response = iot_client.list_thing_principals(thingName=thing_name)
                log_api_call(
                    "list_thing_principals", "List certificates attached to Thing", list_principals_params, principals_response
                )

                principals = principals_response.get("principals", [])
                print(f"  {get_message('found_certificates', len(principals), thing_name)}")

                # Clean up certificates
                for principal in principals:
                    if clean_certificate(iot_client, principal):
                        certificates_cleaned += 1

            except ClientError as e:
                print(f"  {get_message('error_generic', str(e))}")
                if DEBUG_MODE:
                    print(f"{get_message('debug_full_error')}")
                    print(json.dumps(e.response, indent=2, default=str))

            # Delete the Thing
            print(f"  {get_message('deleting_thing', thing_name)}")

            delete_thing_params = {"thingName": thing_name}
            log_api_call("delete_thing", "Delete Thing", delete_thing_params)

            try:
                iot_client.delete_thing(thingName=thing_name)
                log_api_call("delete_thing", "Delete Thing", delete_thing_params, {})
                print(f"  {get_message('deleted_resource', 'Thing', thing_name)}")

            except ClientError as e:
                if e.response["Error"]["Code"] == "ResourceNotFoundException":
                    print(f"  {get_message('resource_not_found', 'Thing', thing_name)}")
                else:
                    print(f"  {get_message('error_deleting_resource', 'Thing', thing_name, str(e))}")
                    if DEBUG_MODE:
                        print(f"{get_message('debug_full_error')}")
                        print(json.dumps(e.response, indent=2, default=str))

        return certificates_cleaned

    except Exception as e:
        print(f"{get_message('error_generic', str(e))}")
        if DEBUG_MODE:
            print(f"{get_message('debug_full_traceback')}")
            traceback.print_exc()
        return 0


def cleanup_orphaned_certificates(iot_client):
    """Check for and report orphaned certificates"""
    print(f"\n{get_message('step2_title')}")
    print(get_message("step_separator"))

    print(get_message("listing_certificates"))

    log_api_call("list_certificates", "List all certificates to check for orphaned ones")

    try:
        response = iot_client.list_certificates()
        log_api_call("list_certificates", "List all certificates to check for orphaned ones", None, response)

        certificates = response.get("certificates", [])
        print(get_message("found_certificates_account", len(certificates)))

        skipped_certificates = 0

        for cert in certificates:
            cert_id = cert["certificateId"]
            cert_status = cert["status"]
            cert_arn = cert["certificateArn"]

            print(get_message("certificate_info", cert_id, cert_status))

            # Check if certificate is attached to any Things
            print(f"  {get_message('checking_certificate_things', cert_id)}")

            list_things_params = {"principal": cert_arn}
            log_api_call("list_principal_things", "Check Things attached to certificate", list_things_params)

            try:
                things_response = iot_client.list_principal_things(principal=cert_arn)
                log_api_call(
                    "list_principal_things", "Check Things attached to certificate", list_things_params, things_response
                )

                attached_things = things_response.get("things", [])

                # Check if any attached Things are sample Things
                sample_things_attached = [thing for thing in attached_things if thing.startswith(SAMPLE_THING_PREFIX)]

                if sample_things_attached:
                    print(f"  {get_message('cert_attached_sample_things', cert_id, ', '.join(sample_things_attached))}")
                    print(f"  {get_message('cert_should_cleanup_step1')}")
                else:
                    print(f"  {get_message('cert_not_attached_sample', cert_id)}")
                    skipped_certificates += 1

            except ClientError as e:
                print(f"  {get_message('could_not_check_things', cert_id, str(e))}")
                skipped_certificates += 1
                if DEBUG_MODE:
                    print(f"{get_message('debug_full_error')}")
                    print(json.dumps(e.response, indent=2, default=str))

        return skipped_certificates

    except Exception as e:
        print(f"{get_message('error_generic', str(e))}")
        if DEBUG_MODE:
            print(f"{get_message('debug_full_traceback')}")
            traceback.print_exc()
        return 0


def cleanup_sample_policies(iot_client):
    """Clean up sample policies"""
    print(f"\n{get_message('step3_title')}")
    print(get_message("step_separator"))

    print(get_message("listing_policies"))

    log_api_call("list_policies", "List all policies to check for cleanup")

    try:
        response = iot_client.list_policies()
        log_api_call("list_policies", "List all policies to check for cleanup", None, response)

        policies = response.get("policies", [])
        print(get_message("found_policies_account", len(policies)))

        deleted_policies = 0
        skipped_policies = 0

        for policy in policies:
            policy_name = policy["policyName"]
            print(get_message("checking_policy", policy_name))

            # Check if policy matches sample patterns
            is_sample_policy = (
                policy_name.startswith("SamplePolicy")
                or policy_name.startswith("VehiclePolicy")
                or "Sample" in policy_name
                or "Vehicle" in policy_name
            )

            if not is_sample_policy:
                print(f"  {get_message('policy_no_sample_patterns', policy_name)}")
                continue

            # Check if policy is attached to any targets
            print(f"  {get_message('checking_policy_targets', policy_name)}")

            list_targets_params = {"policyName": policy_name}
            log_api_call("list_policy_targets", "Check targets for policy", list_targets_params)

            try:
                targets_response = iot_client.list_targets_for_policy(policyName=policy_name)
                log_api_call("list_policy_targets", "Check targets for policy", list_targets_params, targets_response)

                targets = targets_response.get("targets", [])

                if targets:
                    print(f"  {get_message('policy_attached_targets', policy_name, len(targets))}")
                    skipped_policies += 1
                else:
                    print(f"  {get_message('deleting_unattached_policy', policy_name)}")

                    delete_policy_params = {"policyName": policy_name}
                    log_api_call("delete_policy", "Delete unattached policy", delete_policy_params)

                    iot_client.delete_policy(policyName=policy_name)
                    log_api_call("delete_policy", "Delete unattached policy", delete_policy_params, {})

                    deleted_policies += 1

            except ClientError as e:
                print(f"  {get_message('error_checking_policy', policy_name, str(e))}")
                skipped_policies += 1
                if DEBUG_MODE:
                    print(f"{get_message('debug_full_error')}")
                    print(json.dumps(e.response, indent=2, default=str))

        # Summary
        print(f"\n{get_message('policy_cleanup_summary')}")
        print(get_message("deleted_policies", deleted_policies))
        print(get_message("skipped_policies", skipped_policies))

        return deleted_policies, skipped_policies

    except Exception as e:
        print(f"{get_message('error_generic', str(e))}")
        if DEBUG_MODE:
            print(f"{get_message('debug_full_traceback')}")
            traceback.print_exc()
        return 0, 0


def cleanup_sample_thing_groups(iot_client):
    """Clean up sample Thing Groups"""
    print(f"\n{get_message('step4_title')}")
    print(get_message("step_separator"))

    print(get_message("listing_thing_groups"))

    log_api_call("list_thing_groups", "List all Thing Groups to find sample groups")

    try:
        response = iot_client.list_thing_groups()
        log_api_call("list_thing_groups", "List all Thing Groups to find sample groups", None, response)

        all_groups = response.get("thingGroups", [])

        # Filter sample Thing Groups
        sample_groups = [group for group in all_groups if group["groupName"] in SAMPLE_THING_GROUPS]

        print(get_message("found_sample_groups", len(sample_groups)))

        for group in sample_groups:
            group_name = group["groupName"]
            print(f"{get_message('deleting_thing_group', group_name)}")

            delete_group_params = {"thingGroupName": group_name}
            log_api_call("delete_thing_group", "Delete Thing Group", delete_group_params)

            try:
                iot_client.delete_thing_group(thingGroupName=group_name)
                log_api_call("delete_thing_group", "Delete Thing Group", delete_group_params, {})
                print(f"  {get_message('deleted_resource', 'Thing Group', group_name)}")

            except ClientError as e:
                if e.response["Error"]["Code"] == "ResourceNotFoundException":
                    print(f"  {get_message('resource_not_found', 'Thing Group', group_name)}")
                else:
                    print(f"  {get_message('error_deleting_resource', 'Thing Group', group_name, str(e))}")
                    if DEBUG_MODE:
                        print(f"{get_message('debug_full_error')}")
                        print(json.dumps(e.response, indent=2, default=str))

        return len(sample_groups)

    except Exception as e:
        print(f"{get_message('error_generic', str(e))}")
        if DEBUG_MODE:
            print(f"{get_message('debug_full_traceback')}")
            traceback.print_exc()
        return 0


def cleanup_sample_thing_types(iot_client):
    """Clean up sample Thing Types"""
    print(f"\n{get_message('step5_title')}")
    print(get_message("step_separator"))

    print(get_message("listing_thing_types"))

    log_api_call("list_thing_types", "List all Thing Types to find sample types")

    try:
        response = iot_client.list_thing_types()
        log_api_call("list_thing_types", "List all Thing Types to find sample types", None, response)

        all_types = response.get("thingTypes", [])

        # Filter sample Thing Types
        sample_types = [thing_type for thing_type in all_types if thing_type["thingTypeName"] in SAMPLE_THING_TYPES]

        print(get_message("found_sample_types", len(sample_types)))

        if not sample_types:
            print(get_message("no_sample_types"))
            return 0

        # Check status of each Thing Type
        deprecated_types = []
        active_types = []

        for thing_type in sample_types:
            type_name = thing_type["thingTypeName"]

            describe_params = {"thingTypeName": type_name}
            log_api_call("describe_thing_type", "Check Thing Type status", describe_params)

            try:
                describe_response = iot_client.describe_thing_type(thingTypeName=type_name)
                log_api_call("describe_thing_type", "Check Thing Type status", describe_params, describe_response)

                metadata = describe_response.get("thingTypeMetadata", {})
                deprecation_date = metadata.get("deprecationDate")

                if deprecation_date:
                    print(get_message("thing_type_deprecated", type_name, deprecation_date))
                    deprecated_types.append((type_name, deprecation_date))
                else:
                    print(get_message("thing_type_active", type_name))
                    active_types.append(type_name)

            except ClientError as e:
                print(get_message("could_not_check_status", type_name, str(e)))
                if DEBUG_MODE:
                    print(f"{get_message('debug_full_error')}")
                    print(json.dumps(e.response, indent=2, default=str))

        # Deprecate active Thing Types
        if active_types:
            print(f"\n{get_message('deprecating_active_types', len(active_types))}")

            for type_name in active_types:
                print(get_message("deprecating_thing_type", type_name))

                deprecate_params = {"thingTypeName": type_name}
                log_api_call("deprecate_thing_type", "Deprecate Thing Type", deprecate_params)

                try:
                    iot_client.deprecate_thing_type(thingTypeName=type_name)
                    log_api_call("deprecate_thing_type", "Deprecate Thing Type", deprecate_params, {})

                    print(f"  {get_message('thing_type_deprecated_success', type_name)}")
                    deprecated_types.append((type_name, time.time()))

                except ClientError as e:
                    print(f"  {get_message('could_not_deprecate', type_name)}")
                    if DEBUG_MODE:
                        print(f"{get_message('debug_full_error')}")
                        print(json.dumps(e.response, indent=2, default=str))

        # Handle deletion with 5-minute constraint
        if deprecated_types:
            print(f"\n{get_message('aws_constraint_5min')}")
            print(get_message("thing_types_to_delete"))

            for type_name, dep_date in deprecated_types:
                if isinstance(dep_date, float):
                    dep_date_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(dep_date))
                else:
                    dep_date_str = str(dep_date)
                print(get_message("deprecated_item", type_name, dep_date_str))

            print(f"\n{get_message('deletion_options')}")
            print(get_message("wait_5min_delete"))
            print(get_message("skip_deletion"))
            print(get_message("try_deletion_now"))

            while True:
                try:
                    choice = input(get_message("select_option_1_3")).strip()

                    if choice == "1":
                        # Wait 5 minutes
                        print(f"\n{get_message('waiting_5min')}")
                        print(get_message("constraint_explanation"))

                        try:
                            for i in range(300, 0, -1):  # 5 minutes = 300 seconds
                                minutes = i // 60
                                seconds = i % 60
                                print(f"\r{get_message('time_remaining', minutes, seconds)}", end="", flush=True)
                                time.sleep(1)

                            print(f"\n{get_message('wait_completed')}")

                        except KeyboardInterrupt:
                            print(f"\n{get_message('cleanup_interrupted')}")
                            print(get_message("types_deprecated_delete_later"))
                            return len(deprecated_types)

                        break

                    elif choice == "2":
                        print(f"\n{get_message('skipping_deletion')}")
                        print(get_message("deletion_tip"))
                        print(get_message("types_ready_deletion"))
                        return len(deprecated_types)

                    elif choice == "3":
                        print(f"\n{get_message('attempting_deletion_now')}")
                        break

                    else:
                        print(get_message("invalid_choice_1_3"))

                except KeyboardInterrupt:
                    print(f"\n{get_message('cleanup_interrupted')}")
                    print(get_message("types_deprecated_delete_later"))
                    return len(deprecated_types)

            # Delete deprecated Thing Types
            print(f"\n{get_message('deleting_deprecated_types')}")
            deleted_count = 0

            for type_name, _ in deprecated_types:
                print(get_message("attempting_delete_type", type_name))

                delete_params = {"thingTypeName": type_name}
                log_api_call("delete_thing_type", "Delete Thing Type", delete_params)

                try:
                    iot_client.delete_thing_type(thingTypeName=type_name)
                    log_api_call("delete_thing_type", "Delete Thing Type", delete_params, {})

                    print(f"  {get_message('deleted_resource', 'Thing Type', type_name)}")
                    deleted_count += 1

                except ClientError as e:
                    print(f"  {get_message('error_deleting_resource', 'Thing Type', type_name, str(e))}")
                    if DEBUG_MODE:
                        print(f"{get_message('debug_full_error')}")
                        print(json.dumps(e.response, indent=2, default=str))

            if deleted_count < len(deprecated_types):
                print(f"\n{get_message('deletion_failed_timing')}")
                for type_name, _ in deprecated_types:
                    print(get_message("type_ready_deletion", type_name))

            return deleted_count

        return 0

    except Exception as e:
        print(f"{get_message('error_generic', str(e))}")
        if DEBUG_MODE:
            print(f"{get_message('debug_full_traceback')}")
            traceback.print_exc()
        return 0


def cleanup_device_shadows():
    """Device shadows cleanup (automatic)"""
    print(f"\n{get_message('step6_title')}")
    print(get_message("step_separator"))

    print(get_message("shadows_auto_cleanup"))
    print(get_message("no_manual_shadow_cleanup"))

    debug_print(get_message("debug_shadow_skipped"))

    print(get_message("shadow_cleanup_completed"))


def cleanup_sample_rules(iot_client):
    """Clean up sample IoT rules"""
    print(f"\n{get_message('step7_title')}")
    print(get_message("step_separator"))

    debug_print(get_message("debug_listing_rules"))

    log_api_call("list_topic_rules", "List all IoT rules")

    try:
        response = iot_client.list_topic_rules()
        log_api_call("list_topic_rules", "List all IoT rules", None, response)

        rules = response.get("rules", [])
        deleted_rules = 0

        for rule in rules:
            rule_name = rule["ruleName"]

            # Check if rule matches sample patterns
            is_sample_rule = (
                rule_name.startswith("SampleRule")
                or rule_name.startswith("VehicleRule")
                or "Sample" in rule_name
                or "Vehicle" in rule_name
                or "Learning" in rule_name
            )

            if is_sample_rule:
                debug_print(get_message("debug_deleting_rule", rule_name))

                delete_rule_params = {"ruleName": rule_name}
                log_api_call("delete_topic_rule", "Delete IoT rule", delete_rule_params)

                try:
                    iot_client.delete_topic_rule(ruleName=rule_name)
                    log_api_call("delete_topic_rule", "Delete IoT rule", delete_rule_params, {})

                    print(get_message("deleted_rule", rule_name))
                    deleted_rules += 1

                except ClientError as e:
                    print(get_message("error_deleting_rule", rule_name, str(e)))
                    if DEBUG_MODE:
                        print(f"{get_message('debug_full_error')}")
                        print(json.dumps(e.response, indent=2, default=str))

        if deleted_rules == 0:
            print(get_message("no_sample_rules"))

        print(get_message("rules_cleanup_summary", deleted_rules))
        return deleted_rules

    except Exception as e:
        print(f"{get_message('error_generic', str(e))}")
        if DEBUG_MODE:
            print(f"{get_message('debug_full_traceback')}")
            traceback.print_exc()
        return 0


def cleanup_local_files():
    """Clean up local certificate files"""
    print(f"\n{get_message('step8_title')}")
    print(get_message("step_separator"))

    # Clean up certificates directory
    cert_dir = os.path.join(os.path.dirname(__file__), "..", "certificates")
    cert_dir = os.path.abspath(cert_dir)

    print(get_message("checking_cert_directory", cert_dir))

    if os.path.exists(cert_dir):
        print(get_message("cert_directory_contents"))
        try:
            for item in os.listdir(cert_dir):
                print(f"  • {item}")

            shutil.rmtree(cert_dir)
            print(get_message("removed_cert_directory", cert_dir))
            debug_print(get_message("directory_deleted_success", cert_dir))

        except Exception as e:
            print(get_message("error_removing_cert_dir", str(e)))
            if DEBUG_MODE:
                print(f"{get_message('debug_full_traceback')}")
                traceback.print_exc()
    else:
        print(get_message("no_cert_directory"))
        debug_print(get_message("directory_not_exist", cert_dir))

    # Clean up sample-certs directory
    sample_cert_dir = os.path.join(os.path.dirname(__file__), "..", "sample-certs")
    sample_cert_dir = os.path.abspath(sample_cert_dir)

    print(f"\n{get_message('checking_sample_cert_dir', sample_cert_dir)}")

    if os.path.exists(sample_cert_dir):
        print(get_message("sample_cert_contents"))
        try:
            for item in os.listdir(sample_cert_dir):
                print(f"  • {item}")

            shutil.rmtree(sample_cert_dir)
            print(get_message("removed_sample_cert_dir", sample_cert_dir))
            debug_print(get_message("directory_deleted_success", sample_cert_dir))

        except Exception as e:
            print(get_message("error_removing_sample_dir", str(e)))
            if DEBUG_MODE:
                print(f"{get_message('debug_full_traceback')}")
                traceback.print_exc()
    else:
        print(get_message("no_sample_cert_dir"))
        debug_print(get_message("directory_not_exist", sample_cert_dir))

    # Clean up device state files
    script_dir = os.path.dirname(__file__)
    for filename in os.listdir(script_dir):
        if filename.startswith("device_state") and filename.endswith(".json"):
            file_path = os.path.join(script_dir, filename)
            try:
                os.remove(file_path)
                debug_print(f"Removed device state file: {filename}")
            except Exception as e:
                debug_print(f"Error removing {filename}: {e}")


def main():
    global USER_LANG, messages, DEBUG_MODE

    # Check for debug mode
    DEBUG_MODE = "--debug" in sys.argv or "-d" in sys.argv

    # Get language preference
    USER_LANG = get_language()

    # Load messages
    messages = load_messages("cleanup_sample_data", USER_LANG)

    print(get_message("title"))
    print(get_message("separator"))

    # AWS context information
    print(f"\n{get_message('aws_context_info')}")
    try:
        sts_client = boto3.client("sts")
        identity = sts_client.get_caller_identity()
        print(f"  {get_message('account_id')}: {identity.get('Account', 'Unknown')}")
        print(f"  {get_message('region')}: {boto3.Session().region_name or 'us-east-1'}")
    except Exception as e:
        print(get_message("aws_context_error", str(e)))
        print(get_message("aws_credentials_reminder"))

    # Description
    print(f"\n{get_message('description_intro')}")
    for script in get_message("setup_scripts"):
        print(script)
    print(f"\n{get_message('no_affect_other')}")

    if DEBUG_MODE:
        print(f"\n{get_message('debug_enabled')}")
        for feature in get_message("debug_features"):
            print(feature)
    else:
        print(f"\n{get_message('tip')}")

    # Resources to cleanup
    print(f"\n{get_message('resources_to_cleanup')}")
    print(get_message("things_prefix", SAMPLE_THING_PREFIX))
    print(get_message("thing_types", ", ".join(SAMPLE_THING_TYPES)))
    print(get_message("thing_groups", ", ".join(SAMPLE_THING_GROUPS)))
    print(get_message("certificates_attached"))
    print(get_message("local_cert_files"))
    print(get_message("policies_manual_review"))

    # Confirmation
    response = input(f"\n{get_message('continue_cleanup')}").strip().lower()
    if response not in ["y", "yes", "si", "sí", "はい", "hai", "是", "是的", "sim", "네", "yes"]:
        print(get_message("cleanup_cancelled"))
        return

    try:
        # Initialize IoT client
        iot_client = boto3.client("iot")
        print(f"\n{get_message('client_initialized')}")

        if DEBUG_MODE:
            print(get_message("debug_client_config"))
            print(f"  {get_message('service_label')}: {iot_client._service_model.service_name}")
            print(f"  {get_message('api_version_label')}: {iot_client._service_model.api_version}")

        # Learning moment
        print(f"\n{get_message('learning_moment_title')}")
        print(get_message("learning_moment_content"))
        print(f"\n{get_message('next_cleanup')}")
        input(get_message("press_enter_continue"))

        # Execute cleanup steps
        certificates_cleaned = cleanup_sample_things(iot_client)
        skipped_certificates = cleanup_orphaned_certificates(iot_client)
        deleted_policies, skipped_policies = cleanup_sample_policies(iot_client)
        cleanup_sample_thing_groups(iot_client)
        cleanup_sample_thing_types(iot_client)
        cleanup_device_shadows()
        cleanup_sample_rules(iot_client)
        cleanup_local_files()

        # Final summary
        print(f"\n{get_message('cleanup_summary_title')}")
        print(get_message("summary_separator"))
        print(get_message("things_cleaned"))
        print(get_message("certificates_cleaned"))
        print(get_message("groups_cleaned"))
        print(get_message("types_cleaned"))
        print(get_message("local_files_cleaned"))
        print(get_message("device_state_cleaned"))
        print(f"\n{get_message('account_clean')}")

        # Certificate and policy summary
        if skipped_certificates > 0:
            print(f"\n{get_message('certificate_cleanup_summary')}")
            print(get_message("cleaned_certificates", certificates_cleaned))
            print(get_message("skipped_certificates", skipped_certificates))
            print(f"\n{get_message('skipped_certs_production')}")
            print(get_message("manual_cert_deletion"))

        if skipped_policies > 0:
            print(f"\n{get_message('skipped_policies_note')}")
            print(get_message("policies_cleanup_auto"))
            print(get_message("policies_manual_cleanup"))

        if DEBUG_MODE:
            print(f"\n{get_message('debug_cleanup_completed')}")

        print(f"\n{get_message('goodbye')}")

    except KeyboardInterrupt:
        print(f"\n{get_message('cleanup_interrupted')}")

    except Exception as e:
        print(f"\n{get_message('error_generic', str(e))}")
        if DEBUG_MODE:
            print(f"{get_message('debug_full_traceback')}")
            traceback.print_exc()


if __name__ == "__main__":
    main()
