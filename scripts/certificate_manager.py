#!/usr/bin/env python3
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import json
import os
import re
import sys
import time

# Add i18n to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "i18n"))

import boto3
from botocore.exceptions import ClientError, NoCredentialsError, NoRegionError
from language_selector import get_language
from loader import load_messages

# Global variables
USER_LANG = "en"
messages = {}
DEBUG_MODE = True  # Default to True for educational purposes


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

    print(f"\n{moment.get('title', '')}")
    print(moment.get("content", ""))
    print(f"\n🔄 NEXT: {moment.get('next', '')}")


def check_credentials():
    """Validate AWS credentials are available"""
    required_vars = ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print(get_message("credentials_check_failed"))
        for var in missing_vars:
            print(f"   - {var}")
        print()
        for instruction in get_message("credentials_instructions"):
            print(instruction)
        print()
        sys.exit(1)


def display_aws_context():
    """Display current AWS account and region information"""
    try:
        sts = boto3.client("sts")
        iot = boto3.client("iot")
        identity = sts.get_caller_identity()

        print(f"\n{get_message('aws_config')}")
        print(f"   {get_message('account_id')}: {identity['Account']}")
        print(f"   {get_message('region')}: {iot.meta.region_name}")
    except Exception as e:
        print(f"\n{get_message('aws_context_error')} {str(e)}")
        print(get_message("aws_credentials_reminder"))
    print()


def print_step(step, description):
    """Print step with formatting"""
    print(f"\n🔐 Step {step}: {description}")
    print("-" * 50)


def print_info(message, indent=0):
    """Print informational message with optional indent"""
    prefix = "   " * indent
    print(f"{prefix}ℹ️  {message}")


def validate_policy_security(policy_document, policy_name):
    """Validate policy for security best practices"""
    warnings = []

    for statement in policy_document.get("Statement", []):
        # Check for wildcard resources
        resources = statement.get("Resource", [])
        if isinstance(resources, str):
            resources = [resources]

        if "*" in resources:
            warnings.append(
                f"Policy '{policy_name}' uses wildcard resource '*' - consider using specific ARNs"
            )

        # Check for missing conditions
        if not statement.get("Condition"):
            warnings.append(
                f"Policy '{policy_name}' lacks condition statements for additional security"
            )

    return warnings


def print_enhanced_security_warning(policy_name, policy_document, validation_warnings):
    """Print enhanced security warning with validation results"""
    print(f"\n{get_message('policy_to_be_created')}")
    print(f"   {get_message('policy_name_label')}: {policy_name}")
    print(
        f"   {get_message('policy_document_label')}: {json.dumps(policy_document, indent=2)}"
    )

    print(f"\n{get_message('security_warning')}")
    for detail in get_message("security_warning_details"):
        print(detail)

    if validation_warnings:
        print(f"\n{get_message('policy_validation_issues')}")
        for warning in validation_warnings:
            print(f"   • {warning}")


def safe_operation(func, operation_name, api_details=None, debug=None, **kwargs):
    """Execute operation with error handling and API details"""
    if debug is None:
        debug = DEBUG_MODE

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
            print(
                f"✅ {get_message('operation_completed_successfully').format(operation_name)}"
            )
            print(
                f"📤 {get_message('output_label')}: {json.dumps(response, indent=2, default=str)[:500]}{'...' if len(str(response)) > 500 else ''}"
            )
        else:
            print(f"✅ {get_message('operation_completed').format(operation_name)}")

        time.sleep(1 if debug else 0.5)
        return response
    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "Unknown")
        error_message = e.response.get("Error", {}).get("Message", "Unknown error")
        print(f"❌ API Error {operation_name}: {error_code} - {error_message}")
        if debug:
            print("🔍 DEBUG: Full error response:")
            print(json.dumps(e.response, indent=2, default=str))
        time.sleep(0.5)
        return None
    except Exception as e:
        print(f"❌ Error {operation_name}: {str(e)}")
        if debug:
            import traceback

            print("🔍 DEBUG: Full traceback:")
            traceback.print_exc()
        time.sleep(0.5)
        return None


def print_api_details(operation, method, path, description, inputs=None, outputs=None):
    """Print detailed API information for learning"""
    print(f"\n{get_message('api_details_header')}")
    print(f"   {get_message('operation_label')}: {operation}")
    print(f"   {get_message('http_method_label')}: {method}")
    print(f"   {get_message('api_path_label')}: {path}")
    print(f"   {get_message('description_label')}: {description}")
    if inputs:
        print(f"   {get_message('input_parameters_label')}: {inputs}")
    if outputs:
        print(f"   {get_message('expected_output_label')}: {outputs}")
    time.sleep(1)


def save_certificate_files(thing_name, cert_id, cert_pem, private_key, public_key):
    """Save certificate files to local folder structure"""
    # Validate thing_name to prevent path traversal
    if not re.match(r"^[a-zA-Z0-9_-]+$", thing_name):
        raise ValueError(
            f"Invalid thing_name: {thing_name}. Only alphanumeric characters, hyphens, and underscores allowed."
        )

    # Create certificates directory structure
    base_dir = os.path.join(os.getcwd(), "certificates", thing_name)
    os.makedirs(base_dir, exist_ok=True)

    # Save certificate files
    cert_file = os.path.join(base_dir, f"{cert_id}.crt")
    key_file = os.path.join(base_dir, f"{cert_id}.key")
    pub_file = os.path.join(base_dir, f"{cert_id}.pub")

    with open(cert_file, "w", encoding="utf-8") as f:
        f.write(cert_pem)

    with open(key_file, "w", encoding="utf-8") as f:
        f.write(private_key)

    with open(pub_file, "w", encoding="utf-8") as f:
        f.write(public_key)

    print(f"   📄 {get_message('certificate_file_label')}: {cert_file}")
    print(f"   🔐 {get_message('private_key_file_label')}: {key_file}")
    print(f"   🔑 {get_message('public_key_file_label')}: {pub_file}")

    return base_dir


def check_existing_certificates(iot, thing_name):
    """Check if Thing already has certificates attached"""
    try:
        response = iot.list_thing_principals(thingName=thing_name)
        principals = response.get("principals", [])

        # Filter for certificate ARNs
        cert_arns = [p for p in principals if "cert/" in p]

        if cert_arns:
            print(
                get_message("thing_already_has_certificates").format(
                    thing_name, len(cert_arns)
                )
            )
            for i, cert_arn in enumerate(cert_arns, 1):
                cert_id = cert_arn.split("/")[-1]
                print(get_message("certificate_id_item").format(i, cert_id))

            return cert_arns

        return []

    except Exception as e:
        print(f"{get_message('error_checking_certificates')} {str(e)}")
        return []


def cleanup_certificate(iot, cert_arn, thing_name):
    """Remove certificate association and clean up"""
    cert_id = cert_arn.split("/")[-1]
    print(f"\n{get_message('cleanup_certificate').format(cert_id)}")

    # Detach policies
    try:
        policies = iot.list_attached_policies(target=cert_arn).get("policies", [])
        for policy in policies:
            safe_operation(
                iot.detach_policy,
                f"Detaching policy '{policy['policyName']}'",
                policyName=policy["policyName"],
                target=cert_arn,
            )
    except Exception as e:
        print(f"{get_message('error_detaching_policies')} {str(e)}")

    # Detach from Thing
    safe_operation(
        iot.detach_thing_principal,
        f"Detaching certificate from {thing_name}",
        thingName=thing_name,
        principal=cert_arn,
    )

    # Deactivate and delete certificate
    safe_operation(
        iot.update_certificate,
        "Deactivating certificate",
        certificateId=cert_id,
        newStatus="INACTIVE",
    )

    safe_operation(
        iot.delete_certificate, "Deleting certificate", certificateId=cert_id
    )

    # Remove local files if they exist
    if not re.match(r"^[a-zA-Z0-9_-]+$", thing_name):
        print(f"{get_message('skipping_file_cleanup')} {thing_name}")
        return

    cert_folder = os.path.join(os.getcwd(), "certificates", thing_name)
    if os.path.exists(cert_folder):
        for file in os.listdir(cert_folder):
            if cert_id in file:
                file_path = os.path.join(cert_folder, file)
                os.remove(file_path)
                print(f"{get_message('removed_local_file')} {file_path}")

    print(get_message("certificate_cleaned_up").format(cert_id))


def create_certificate(iot, thing_name=None):
    """Create a new X.509 certificate and save locally"""
    print_step(1, get_message("step_creating_certificate"))

    print_info(get_message("certificates_for_auth"))
    print_info(get_message("cert_contains_keypair"))
    time.sleep(1)

    api_details = (
        "create_keys_and_certificate",
        "POST",
        "/keys-and-certificate",
        get_message("api_desc_create_keys_cert"),
        get_message("api_input_set_active"),
        get_message("api_output_cert_keypair"),
    )

    response = safe_operation(
        iot.create_keys_and_certificate,
        get_message("creating_cert_keypair"),
        api_details,
        setAsActive=True,
    )

    if response:
        cert_arn = response["certificateArn"]
        cert_id = response["certificateId"]
        cert_pem = response["certificatePem"]
        private_key = response["keyPair"]["PrivateKey"]
        public_key = response["keyPair"]["PublicKey"]

        print(f"\n{get_message('certificate_details')}")
        print(f"   {get_message('certificate_id_label')}: {cert_id}")
        print(f"   {get_message('certificate_arn_label')}: {cert_arn}")
        print(f"   {get_message('status_active')}")

        # Save certificate files locally
        if thing_name:
            cert_folder = save_certificate_files(
                thing_name, cert_id, cert_pem, private_key, public_key
            )
            print(f"\n{get_message('certificate_files_saved')} {cert_folder}")

        print(f"\n{get_message('certificate_components_created')}")
        for component in get_message("certificate_components_list"):
            print(component)

        return cert_arn, cert_id

    return None, None


def select_thing(iot):
    """Select a Thing for certificate creation"""
    print_info(get_message("fetching_things").replace("ℹ️ ", ""))

    try:
        # Handle pagination to get ALL things
        things = []
        next_token = None

        while True:
            if next_token:
                response = iot.list_things(nextToken=next_token)
            else:
                response = iot.list_things()

            things.extend(response.get("things", []))
            next_token = response.get("nextToken")

            if not next_token:
                break

        if not things:
            print(get_message("no_things_found_run_setup"))
            return None

        while True:
            print(f"\n{get_message('available_things_count').format(len(things))}")

            # Show first 10 things
            display_count = min(len(things), 10)
            for i in range(display_count):
                thing = things[i]
                print(
                    f"   {i+1}. {thing['thingName']} (Type: {thing.get('thingTypeName', 'None')})"
                )

            if len(things) > 10:
                print(f"   ... and {len(things) - 10} more")

            print(f"\n{get_message('options_header_simple')}")
            print(f"   {get_message('enter_number_select_thing').format(len(things))}")
            print(f"   {get_message('type_all_see_things')}")
            print(f"   {get_message('type_manual_enter_name')}")

            choice = input(f"\n{get_message('your_choice')}").strip()

            if choice.lower() == "all":
                print(f"\n{get_message('all_things_header')}")
                for i, thing in enumerate(things, 1):
                    print(
                        f"   {i}. {thing['thingName']} (Type: {thing.get('thingTypeName', 'None')})"
                    )
                input(get_message("press_enter_continue_simple"))
                continue

            elif choice.lower() == "manual":
                thing_name = input(get_message("enter_thing_name")).strip()
                if thing_name:
                    # Validate thing_name to prevent injection attacks
                    if not re.match(r"^[a-zA-Z0-9_-]+$", thing_name):
                        print(get_message("invalid_thing_name_chars"))
                        continue
                    # Verify Thing exists
                    try:
                        iot.describe_thing(thingName=thing_name)
                        print(get_message("thing_found_check").format(thing_name))
                        return thing_name
                    except ClientError:
                        print(get_message("thing_not_found_check").format(thing_name))
                        continue
                else:
                    print(get_message("thing_name_cannot_be_empty"))
                    continue

            else:
                try:
                    thing_index = int(choice) - 1
                    if 0 <= thing_index < len(things):
                        selected_thing = things[thing_index]["thingName"]
                        print(get_message("selected_thing").format(selected_thing))
                        return selected_thing
                    else:
                        print(
                            get_message("invalid_selection_enter_range").format(
                                len(things)
                            )
                        )
                except ValueError:
                    print(get_message("enter_valid_number_all_manual"))

    except Exception as e:
        print(f"{get_message('error_listing_things')} {str(e)}")
        return None


def attach_certificate_to_thing(iot, cert_arn, target_thing_name):
    """Attach certificate to the designated Thing"""
    print_step(2, get_message("step_attaching_certificate"))

    print_info(get_message("certs_must_be_attached"))
    print_info(get_message("creates_secure_relationship"))
    print_info(get_message("cert_will_be_attached").format(target_thing_name))
    time.sleep(1)

    # Check for existing certificates
    existing_certs = check_existing_certificates(iot, target_thing_name)
    if existing_certs:
        cleanup_choice = (
            input(f"\n{get_message('remove_existing_certificates')}").strip().lower()
        )
        if cleanup_choice == "y":
            for cert_arn_existing in existing_certs:
                cleanup_certificate(iot, cert_arn_existing, target_thing_name)
        else:
            print(get_message("proceeding_with_multiple"))

    print(
        f"\n{get_message('attaching_certificate_to_thing').format(target_thing_name)}"
    )

    api_details = (
        "attach_thing_principal",
        "PUT",
        f"/things/{target_thing_name}/principals",
        get_message("api_desc_attach_thing_principal"),
        f"thingName: {target_thing_name}, principal: {cert_arn}",
        get_message("api_output_empty_success"),
    )

    response = safe_operation(
        iot.attach_thing_principal,
        get_message("attaching_cert_to_thing_name").format(target_thing_name),
        api_details,
        thingName=target_thing_name,
        principal=cert_arn,
    )

    if response is not None:
        print(
            get_message("certificate_successfully_attached").format(target_thing_name)
        )
        print_info(get_message("thing_can_use_cert"), 1)
        return target_thing_name

    return None


def create_policy_interactive(iot):
    """Create IoT policy interactively or select existing"""
    print_step(3, get_message("step_policy_management"))

    print_info(get_message("iot_policies_define_actions"))
    print_info(get_message("create_new_or_existing"))
    time.sleep(1)

    # First, check if there are existing policies
    try:
        existing_policies = iot.list_policies().get("policies", [])
        if existing_policies:
            print(
                f"\n{get_message('found_existing_policies').format(len(existing_policies))}"
            )
            for i, policy in enumerate(existing_policies, 1):
                print(f"   {i}. {policy['policyName']}")

            print(f"\n{get_message('policy_options')}")
            print(get_message("use_existing_policy"))
            print(get_message("create_new_policy"))

            while True:
                choice = input(f"\n{get_message('select_option_1_2')}").strip()
                if choice == "1":
                    # Select existing policy
                    while True:
                        try:
                            policy_choice = (
                                int(
                                    input(
                                        f"Select policy (1-{len(existing_policies)}): "
                                    )
                                )
                                - 1
                            )
                            if 0 <= policy_choice < len(existing_policies):
                                selected_policy = existing_policies[policy_choice][
                                    "policyName"
                                ]
                                print(
                                    get_message("selected_existing_policy").format(
                                        selected_policy
                                    )
                                )
                                return selected_policy
                            else:
                                print(get_message("invalid_selection_generic"))
                        except ValueError:
                            print(get_message("enter_valid_number_generic"))
                elif choice == "2":
                    break  # Continue to create new policy
                else:
                    print(get_message("select_1_or_2"))
        else:
            print(f"\n{get_message('no_existing_policies')}")
    except Exception as e:
        print(f"{get_message('error_listing_policies')} {str(e)}")
        print(get_message("proceeding_create_new"))

    # Create new policy
    policy_name = None
    while True:
        policy_name = input(f"\n{get_message('enter_new_policy_name')}").strip()
        if not policy_name:
            print(get_message("policy_name_required"))
            continue

        # Check if policy exists
        try:
            iot.get_policy(policyName=policy_name)
            print(get_message("policy_already_exists").format(policy_name))
            choice = input(get_message("use_different_name")).strip().lower()
            if choice == "y":
                continue
            else:
                print(get_message("using_existing_policy").format(policy_name))
                return policy_name
        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                print(get_message("policy_name_available").format(policy_name))
                break
            else:
                print(
                    get_message("error_checking_policy").format(
                        e.response["Error"]["Message"]
                    )
                )
                continue

    print(f"\n{get_message('policy_templates')}")
    print(get_message("basic_device_policy"))
    print(get_message("readonly_policy"))
    print(get_message("custom_policy"))

    while True:
        choice = input(get_message("select_policy_template")).strip()

        if choice == "1":
            policy_document = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": [
                            "iot:Connect",
                            "iot:Publish",
                            "iot:Subscribe",
                            "iot:Receive",
                        ],
                        "Resource": "*",
                    }
                ],
            }
            # Validate policy and show enhanced warnings
            validation_warnings = validate_policy_security(policy_document, policy_name)
            print_enhanced_security_warning(
                policy_name, policy_document, validation_warnings
            )

            # Ask for confirmation if there are security warnings
            if validation_warnings:
                confirm = input(get_message("proceed_despite_warnings")).strip().lower()
                if confirm != "y":
                    print(get_message("policy_creation_cancelled"))
                    return None
            break

        elif choice == "2":
            policy_document = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": ["iot:Connect", "iot:Subscribe", "iot:Receive"],
                        "Resource": "*",
                    }
                ],
            }
            # Validate policy and show enhanced warnings
            validation_warnings = validate_policy_security(policy_document, policy_name)
            print_enhanced_security_warning(
                policy_name, policy_document, validation_warnings
            )

            # Ask for confirmation if there are security warnings
            if validation_warnings:
                confirm = input(get_message("proceed_despite_warnings")).strip().lower()
                if confirm != "y":
                    print(get_message("policy_creation_cancelled"))
                    return None
            break

        elif choice == "3":
            print(f"\n{get_message('enter_policy_json')}")
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
                print(get_message("invalid_json_error").format(str(e)))
                continue
        else:
            print(get_message("select_1_2_or_3"))

    print(f"\n{get_message('policy_to_be_created_header')}")
    print(f"   {get_message('name_label_simple')}: {policy_name}")
    print(
        f"   {get_message('document_label_simple')}: {json.dumps(policy_document, indent=2)}"
    )

    api_details = (
        "create_policy",
        "PUT",
        f"/policies/{policy_name}",
        "Creates a new IoT policy with specified permissions",
        f"policyName: {policy_name}, policyDocument: JSON policy document",
        get_message("api_output_policy_details"),
    )

    response = safe_operation(
        iot.create_policy,
        f"Creating policy '{policy_name}'",
        api_details,
        policyName=policy_name,
        policyDocument=json.dumps(policy_document),
    )

    if response:
        print(f"✅ Policy '{policy_name}' created successfully")
        return policy_name

    return None


def attach_policy_to_certificate(iot, cert_arn, policy_name=None):
    """Attach policy to certificate"""
    print_step(4, get_message("step_attaching_policy"))

    print_info(get_message("policies_must_be_attached"))
    print_info(get_message("without_policy_no_operations"))
    time.sleep(1)

    if not policy_name:
        # List existing policies
        try:
            policies = iot.list_policies().get("policies", [])
            if policies:
                print(f"\n{get_message('available_policies')}")
                for i, policy in enumerate(policies, 1):
                    print(f"   {i}. {policy['policyName']}")

                while True:
                    try:
                        choice = (
                            int(input(f"\nSelect policy (1-{len(policies)}): ")) - 1
                        )
                        if 0 <= choice < len(policies):
                            policy_name = policies[choice]["policyName"]
                            break
                        else:
                            print(get_message("invalid_selection_simple"))
                    except ValueError:
                        print(get_message("enter_valid_number_simple"))
            else:
                print(get_message("no_policies_found_create"))
                policy_name = create_policy_interactive(iot)
                if not policy_name:
                    return False
        except Exception as e:
            print(get_message("error_listing_policies_simple").format(str(e)))
            return False

    print(f"\n🔗 Attaching policy '{policy_name}' to certificate")

    api_details = (
        "attach_policy",
        "PUT",
        f"/target-policies/{policy_name}",
        "Attaches an IoT policy to a certificate to grant permissions",
        f"policyName: {policy_name}, target: {cert_arn}",
        get_message("api_output_empty_success"),
    )

    response = safe_operation(
        iot.attach_policy,
        "Attaching policy to certificate",
        api_details,
        policyName=policy_name,
        target=cert_arn,
    )

    if response is not None:
        print(f"✅ Policy '{policy_name}' attached to certificate")
        print_info(get_message("cert_now_has_permissions"), 1)
        return True

    return False


def get_thing_certificates(iot, thing_name):
    """Get certificates attached to a Thing"""
    print_api_details(
        "list_thing_principals",
        "GET",
        f"/things/{thing_name}/principals",
        "Lists all principals (certificates) attached to a specific Thing",
        f"thingName: {thing_name}",
        "Array of principal ARNs (certificate ARNs)",
    )

    try:
        response = iot.list_thing_principals(thingName=thing_name)
        principals = response.get("principals", [])
        cert_arns = [p for p in principals if "cert/" in p]

        print(get_message("api_response_found_certs").format(len(cert_arns)))
        for cert_arn in cert_arns:
            cert_id = cert_arn.split("/")[-1]
            print(f"   {get_message('certificate_id_simple')}: {cert_id}")

        return cert_arns
    except Exception as e:
        print(get_message("error_simple").format(str(e)))
        return []


def certificate_status_workflow(iot):
    """Workflow to enable/disable certificates"""
    print(f"\n{get_message('certificate_status_management')}")
    print("=" * 40)
    print(get_message("learning_objectives_header"))
    for objective in get_message("cert_lifecycle_objectives"):
        print(objective)
    print("=" * 40)

    # List all certificates
    print(f"\n{get_message('fetching_all_certificates')}")

    api_details = (
        "list_certificates",
        "GET",
        "/certificates",
        get_message("api_desc_list_certificates"),
        get_message("api_input_optional_pagination"),
        get_message("api_output_certificates_list"),
    )

    response = safe_operation(
        iot.list_certificates, get_message("listing_all_certificates"), api_details
    )

    if not response:
        print(get_message("failed_to_list_certificates"))
        return

    certificates = response.get("certificates", [])

    if not certificates:
        print(get_message("no_certificates_found"))
        print(get_message("create_certificates_first"))
        return

    print(f"\n{get_message('found_certificates_count').format(len(certificates))}")

    # Get Thing associations for each certificate
    cert_thing_map = {}
    for cert in certificates:
        cert_arn = cert["certificateArn"]
        try:
            # Find Things associated with this certificate
            things_response = iot.list_principal_things(principal=cert_arn)
            things = things_response.get("things", [])
            cert_thing_map[cert["certificateId"]] = things[0] if things else None
        except Exception:
            cert_thing_map[cert["certificateId"]] = None

    for i, cert in enumerate(certificates, 1):
        status_icon = "🟢" if cert["status"] == "ACTIVE" else "🔴"
        thing_name = cert_thing_map.get(cert["certificateId"])
        thing_info = (
            f" → {thing_name}" if thing_name else f" {get_message('no_thing_attached')}"
        )
        status_text = (
            get_message("active_status")
            if cert["status"] == "ACTIVE"
            else get_message("inactive_status")
        )
        print(
            f"   {i}. {cert['certificateId'][:16]}...{thing_info} - {status_icon} {status_text}"
        )
        print(
            f"      {get_message('created_label')}: {cert.get('creationDate', get_message('unknown_label'))}"
        )

    # Select certificate
    while True:
        try:
            choice = int(input(f"\nSelect certificate (1-{len(certificates)}): ")) - 1
            if 0 <= choice < len(certificates):
                selected_cert = certificates[choice]
                break
            else:
                print(get_message("invalid_selection_simple_msg"))
        except ValueError:
            print(get_message("enter_valid_number_simple_msg"))

    cert_id = selected_cert["certificateId"]
    current_status = selected_cert["status"]

    thing_name = cert_thing_map.get(cert_id)
    print(f"\n{get_message('selected_certificate')}")
    print(f"   {get_message('certificate_id_short')}: {cert_id}")
    print(
        f"   {get_message('attached_to_thing')}: {thing_name or get_message('none_label')}"
    )
    print(f"   {get_message('current_status_label')}: {current_status}")
    print(
        f"   {get_message('arn_label')}: {selected_cert.get('certificateArn', 'N/A')}"
    )

    # Determine action based on current status
    if current_status == "ACTIVE":
        new_status = "INACTIVE"
        action = "disable"
        icon = "🔴"
    else:
        new_status = "ACTIVE"
        action = "enable"
        icon = "🟢"

    print(f"\n{get_message('available_action')}")
    if action == "enable":
        print(f"   {icon} {get_message('enable_certificate')}")
    else:
        print(f"   {icon} {get_message('disable_certificate')}")

    confirm = (
        input(f"\n{get_message('do_you_want_to_action_cert').format(action)}")
        .strip()
        .lower()
    )

    if confirm != "y":
        print(get_message("operation_cancelled_simple"))
        return

    # Update certificate status
    api_details = (
        "update_certificate",
        "PUT",
        f"/certificates/{cert_id}",
        "Updates the status of an X.509 certificate",
        f"certificateId: {cert_id}, newStatus: {new_status}",
        get_message("api_output_empty_success"),
    )

    response = safe_operation(
        iot.update_certificate,
        f"{action.title()}ing certificate",
        api_details,
        certificateId=cert_id,
        newStatus=new_status,
    )

    if response is not None:
        print(f"\n{get_message('certificate_action_success').format(action)}")
        print(f"\n{get_message('status_change_summary')}")
        print(f"   {get_message('certificate_id_simple')}: {cert_id}")
        print(
            f"   {get_message('attached_to_thing')}: {thing_name or get_message('none_label')}"
        )
        print(f"   {get_message('previous_status_label')}: {current_status}")
        print(f"   {get_message('new_status_label_simple')}: {new_status}")

        print(f"\n{get_message('what_this_means_simple')}")
        if new_status == "ACTIVE":
            print(get_message("cert_can_be_used_auth"))
            print(get_message("devices_can_connect"))
            print(get_message("mqtt_connections_succeed"))
        else:
            print(get_message("cert_disabled_auth"))
            print(get_message("devices_cannot_connect"))
            print(get_message("mqtt_connections_fail"))

        print(f"\n{get_message('next_steps_simple')}")
        print(get_message("use_registry_explorer"))
        print(get_message("test_mqtt_connection"))
        if new_status == "INACTIVE":
            print(get_message("reenable_when_ready_simple"))
    else:
        print(get_message("failed_to_action_certificate").format(action))


def attach_policy_workflow(iot):
    """Workflow to attach policy to existing certificate"""
    print(f"\n{get_message('policy_attachment_workflow_title')}")
    print("=" * 40)

    # Select Thing
    selected_thing = select_thing(iot)
    if not selected_thing:
        return

    # Get certificates for the Thing
    print(f"\n{get_message('checking_certificates_for_thing').format(selected_thing)}")
    cert_arns = get_thing_certificates(iot, selected_thing)

    if not cert_arns:
        print(get_message("no_certificates_for_thing_msg").format(selected_thing))
        print(get_message("tip_run_option_1_msg"))
        return

    # Select certificate if multiple
    if len(cert_arns) == 1:
        selected_cert_arn = cert_arns[0]
        cert_id = selected_cert_arn.split("/")[-1]
        print(get_message("using_certificate_msg").format(cert_id))
    else:
        print(f"\n{get_message('multiple_certificates_found_msg')}")
        for i, cert_arn in enumerate(cert_arns, 1):
            cert_id = cert_arn.split("/")[-1]
            print(f"   {i}. {cert_id}")

        while True:
            try:
                choice = (
                    int(
                        input(
                            get_message("select_certificate_prompt").format(
                                len(cert_arns)
                            )
                        )
                    )
                    - 1
                )
                if 0 <= choice < len(cert_arns):
                    selected_cert_arn = cert_arns[choice]
                    break
                else:
                    print(get_message("invalid_selection_simple_msg"))
            except ValueError:
                print(get_message("enter_valid_number_simple_msg"))

    # Create or select policy
    policy_name = create_policy_interactive(iot)
    if policy_name:
        attach_policy_to_certificate(iot, selected_cert_arn, policy_name)
        print(
            f"\n🎉 Policy '{policy_name}' attached to certificate for Thing '{selected_thing}'"
        )


def detach_policy_workflow(iot):
    """Workflow to detach policy from certificate"""
    print(f"\n{get_message('policy_detachment_workflow')}")
    print("=" * 40)
    print(get_message("learning_objectives_header_simple"))
    print(get_message("understand_policy_detachment"))
    print(get_message("learn_find_devices_by_policy"))
    print(get_message("practice_cert_policy_mgmt"))
    print(get_message("explore_detach_policy_api"))
    print("=" * 40)

    # Step 1: List all policies
    print(f"\n{get_message('fetching_all_policies')}")

    api_details = (
        "list_policies",
        "GET",
        "/policies",
        "Lists all IoT policies in your AWS account",
        get_message("api_input_optional_pagination"),
        get_message("api_output_policies_list"),
    )

    response = safe_operation(iot.list_policies, "Listing all policies", api_details)

    if not response:
        print(get_message("failed_to_list_policies"))
        return

    policies = response.get("policies", [])

    if not policies:
        print(get_message("no_policies_found_account"))
        print(get_message("create_policies_first"))
        return

    # Step 2: Select policy
    print(f"\n{get_message('found_policies_count').format(len(policies))}")
    for i, policy in enumerate(policies, 1):
        print(f"   {i}. {policy['policyName']}")

    while True:
        try:
            choice = int(input(f"\nSelect policy to detach (1-{len(policies)}): ")) - 1
            if 0 <= choice < len(policies):
                selected_policy = policies[choice]["policyName"]
                break
            else:
                print(get_message("invalid_selection_simple_msg"))
        except ValueError:
            print(get_message("enter_valid_number_simple_msg"))

    print(f"\n✅ Selected policy: {selected_policy}")

    # Step 3: Find certificates with this policy attached
    print(f"\n🔍 Finding certificates with policy '{selected_policy}' attached...")

    api_details = (
        "list_targets_for_policy",
        "POST",
        f"/targets-for-policy/{selected_policy}",
        "Lists all targets (certificates) that have the specified policy attached",
        f"policyName: {selected_policy}",
        "Array of target ARNs (certificate ARNs)",
    )

    response = safe_operation(
        iot.list_targets_for_policy,
        f"Finding targets for policy '{selected_policy}'",
        api_details,
        policyName=selected_policy,
    )

    if not response:
        print(get_message("failed_to_list_policy_targets"))
        return

    targets = response.get("targets", [])
    cert_targets = [t for t in targets if "cert/" in t]

    if not cert_targets:
        print(get_message("no_certs_with_policy").format(selected_policy))
        print(get_message("policy_not_attached"))
        return

    # Step 4: Get Thing associations for each certificate
    print(f"\n{get_message('found_certs_with_policy').format(len(cert_targets))}")
    cert_thing_map = {}

    for i, cert_arn in enumerate(cert_targets, 1):
        cert_id = cert_arn.split("/")[-1]

        # Find Things associated with this certificate
        try:
            things_response = iot.list_principal_things(principal=cert_arn)
            things = things_response.get("things", [])
            thing_name = things[0] if things else None
            cert_thing_map[cert_arn] = thing_name

            thing_info = (
                f" → {thing_name}"
                if thing_name
                else f" {get_message('no_thing_attached')}"
            )
            print(f"   {i}. {cert_id[:16]}...{thing_info}")
        except Exception as e:
            print(f"   {i}. {cert_id[:16]}... (Error getting Thing: {str(e)})")
            cert_thing_map[cert_arn] = None

    # Step 5: Select certificate
    while True:
        try:
            choice = (
                int(
                    input(
                        f"\nSelect certificate to detach policy from (1-{len(cert_targets)}): "
                    )
                )
                - 1
            )
            if 0 <= choice < len(cert_targets):
                selected_cert_arn = cert_targets[choice]
                break
            else:
                print(get_message("invalid_selection_simple_msg"))
        except ValueError:
            print(get_message("enter_valid_number_simple_msg"))

    selected_cert_id = selected_cert_arn.split("/")[-1]
    thing_name = cert_thing_map.get(selected_cert_arn)

    print(f"\n{get_message('detachment_summary')}")
    print(f"   {get_message('policy_label_simple')}: {selected_policy}")
    print(f"   {get_message('certificate_id_simple')}: {selected_cert_id}")
    print(
        f"   {get_message('attached_to_thing')}: {thing_name or get_message('none_label')}"
    )

    # Step 6: Confirm detachment
    confirm = (
        input(f"\n{get_message('detach_policy_from_cert').format(selected_policy)}")
        .strip()
        .lower()
    )

    if confirm != "y":
        print(get_message("operation_cancelled_simple"))
        return

    # Step 7: Detach policy
    api_details = (
        "detach_policy",
        "POST",
        f"/target-policies/{selected_policy}",
        "Detaches an IoT policy from a certificate target",
        f"policyName: {selected_policy}, target: {selected_cert_arn}",
        get_message("api_output_empty_success"),
    )

    response = safe_operation(
        iot.detach_policy,
        "Detaching policy from certificate",
        api_details,
        policyName=selected_policy,
        target=selected_cert_arn,
    )

    if response is not None:
        print(f"\n{get_message('policy_detached_successfully')}")
        print(f"\n{get_message('detachment_results')}")
        print(
            get_message("policy_removed_from_cert").format(
                selected_policy, selected_cert_id
            )
        )
        if thing_name:
            print(get_message("thing_cert_no_longer_has_policy").format(thing_name))

        print(f"\n{get_message('what_this_means_detach')}")
        print(get_message("cert_no_longer_perform_actions").format(selected_policy))
        print(get_message("device_may_lose_permissions"))
        print(get_message("other_policies_still_apply"))
        print(get_message("policy_still_exists"))

        print(f"\n{get_message('next_steps_detach')}")
        print(get_message("use_registry_explorer_verify"))
        print(get_message("test_device_connectivity"))
        print(get_message("attach_different_policy"))
    else:
        print(get_message("failed_to_detach_policy"))


def certificate_creation_workflow(iot):
    """Full workflow for certificate creation and attachment"""
    print(f"\n{get_message('certificate_creation', 'workflow_titles')}")
    print("=" * 40)

    # Select Thing first
    selected_thing = select_thing(iot)
    if not selected_thing:
        return

    print(f"\n{get_message('learning_moment_cert_process')}")
    print(get_message("cert_creation_explanation"))
    print(f"\n{get_message('next_creating_cert')}")
    input(get_message("press_enter"))

    cert_arn, cert_id = create_certificate(iot, selected_thing)
    if not cert_arn:
        print(get_message("failed_to_create_certificate"))
        return

    print(f"\n{get_message('learning_moment_cert_attachment')}")
    print(get_message("cert_attachment_explanation"))
    print(f"\n{get_message('next_attaching_cert')}")
    input(get_message("press_enter_continue_generic"))

    thing_name = attach_certificate_to_thing(iot, cert_arn, selected_thing)
    if not thing_name:
        print(get_message("failed_to_attach_certificate"))
        return

    # Ask about policy
    create_policy = (
        input(f"\n{get_message('would_like_create_policy')}").strip().lower()
    )
    policy_name = None

    if create_policy == "y":
        policy_name = create_policy_interactive(iot)
        if policy_name:
            attach_policy_to_certificate(iot, cert_arn, policy_name)
    else:
        attach_existing = input(get_message("attach_existing_policy")).strip().lower()
        if attach_existing == "y":
            if attach_policy_to_certificate(iot, cert_arn):
                policy_name = "Existing Policy"

    print_summary(cert_id, cert_arn, thing_name, policy_name or "None", "AWS-Generated")


def generate_sample_certificate():
    """Generate a sample certificate using OpenSSL for learning"""
    print_step("OpenSSL", "Generate Sample Certificate with OpenSSL")

    print_info(get_message("creates_self_signed_cert"))
    print_info(get_message("production_use_trusted_ca"))
    time.sleep(1)

    # Create sample-certs directory
    sample_dir = os.path.join(os.getcwd(), "sample-certs")
    os.makedirs(sample_dir, exist_ok=True)

    cert_name = input(get_message("enter_cert_name_default")).strip() or "sample-device"

    # Validate certificate name to prevent command injection
    if not re.match(r"^[a-zA-Z0-9_-]+$", cert_name):
        print(get_message("cert_name_invalid_chars"))
        return None

    key_file = os.path.join(sample_dir, f"{cert_name}.key")
    cert_file = os.path.join(sample_dir, f"{cert_name}.crt")

    print(f"\n{get_message('generating_cert_files')}")
    print(f"   {get_message('private_key_label')}: {key_file}")
    print(f"   {get_message('certificate_label')}: {cert_file}")

    # OpenSSL command to generate private key and certificate
    openssl_cmd = [
        "openssl",
        "req",
        "-x509",
        "-newkey",
        "rsa:2048",
        "-keyout",
        key_file,
        "-out",
        cert_file,
        "-days",
        "365",
        "-nodes",
        "-subj",
        f"/CN={cert_name}/O=AWS IoT Learning/C=US",
    ]

    try:
        print(f"\n{get_message('running_openssl_command')}")
        print(f"{get_message('command_label')}: {' '.join(openssl_cmd)}")

        import subprocess

        result = subprocess.run(
            openssl_cmd, capture_output=True, text=True, shell=False
        )

        if result.returncode == 0:
            print(get_message("certificate_generated_successfully"))
            print(f"\n{get_message('certificate_details_header')}")
            print(f"   {get_message('cert_type_self_signed')}")
            print(f"   {get_message('cert_algorithm')}")
            print(f"   {get_message('cert_validity')}")
            print(f"   • Subject: CN={cert_name}, O=AWS IoT Learning, C=US")

            # Show certificate info
            info_cmd = ["openssl", "x509", "-in", cert_file, "-text", "-noout"]
            info_result = subprocess.run(
                info_cmd, capture_output=True, text=True, shell=False
            )
            if info_result.returncode == 0:
                print(f"\n{get_message('certificate_information')}")
                lines = info_result.stdout.split("\n")
                for line in lines[:10]:  # Show first 10 lines
                    if line.strip():
                        print(f"   {line.strip()}")
                print("   ...")

            return cert_file
        else:
            print(f"❌ OpenSSL error: {result.stderr}")
            return None

    except FileNotFoundError:
        print(get_message("openssl_not_found"))
        print(get_message("install_openssl_macos"))
        print(get_message("install_openssl_ubuntu"))
        print(get_message("windows_openssl_download"))
        return None
    except Exception as e:
        print(f"❌ Error generating certificate: {str(e)}")
        return None


def get_certificate_file_path():
    """Get certificate file path from user with options"""
    print_info(get_message("choose_cert_provision"))
    print(f"\n{get_message('certificate_options')}")
    print(get_message("use_existing_cert_file"))
    print(get_message("generate_sample_cert"))

    while True:
        choice = input(f"\n{get_message('select_option_1_2_prompt')}").strip()

        if choice == "1":
            return get_existing_certificate_path()
        elif choice == "2":
            return generate_sample_certificate()
        else:
            print(get_message("invalid_choice_1_2"))


def get_existing_certificate_path():
    """Get path to existing certificate file"""
    print_info(get_message("cert_must_be_pem_info"))
    print_info(get_message("pem_format_starts_with"))

    while True:
        cert_path = input(get_message("enter_cert_path")).strip()
        if not cert_path:
            print(get_message("cert_path_required"))
            continue

        # Validate cert_path to prevent path traversal
        if not os.path.abspath(cert_path).startswith(os.path.abspath(os.getcwd())):
            print(get_message("cert_file_within_working_dir"))
            continue

        if not os.path.exists(cert_path):
            print(get_message("file_not_found").format(cert_path))
            continue

        if not cert_path.lower().endswith((".crt", ".pem")):
            print(get_message("warning_no_crt_pem"))
            confirm = input(get_message("continue_anyway")).strip().lower()
            if confirm != "y":
                continue

        return cert_path


def validate_certificate_file(cert_path):
    """Validate certificate file format with detailed feedback"""
    print_info(get_message("validating_cert_format"))

    try:
        with open(cert_path, "r", encoding="utf-8") as f:
            cert_content = f.read()

        print(get_message("cert_file_content_preview"))
        lines = cert_content.split("\n")
        for i, line in enumerate(lines[:5]):
            print(f"   Line {i+1}: {line[:60]}{'...' if len(line) > 60 else ''}")
        if len(lines) > 5:
            print(f"   ... and {len(lines) - 5} more lines")

        # Basic PEM format validation
        if not cert_content.startswith("-----BEGIN CERTIFICATE-----"):
            print(get_message("invalid_cert_format_start"))
            print(get_message("tip_convert_der_to_pem"))
            return False

        if not cert_content.strip().endswith("-----END CERTIFICATE-----"):
            print(get_message("invalid_cert_format_end"))
            return False

        # Count certificate sections
        cert_count = cert_content.count("-----BEGIN CERTIFICATE-----")
        print(get_message("cert_validation_results"))
        print(get_message("format_pem_check"))
        print(f"{get_message('certificate_count_label')}: {cert_count}")
        print(f"{get_message('file_size_label')}: {len(cert_content)} bytes")

        if cert_count > 1:
            print(get_message("multiple_certs_warning"))

        print(get_message("cert_format_validated"))
        return True

    except FileNotFoundError:
        print(get_message("cert_file_not_found"))
        return False
    except PermissionError:
        print(get_message("permission_denied_cert"))
        return False
    except UnicodeDecodeError:
        print(get_message("cert_encoding_error"))
        return False
    except Exception as e:
        print(f"❌ Unexpected error reading certificate file: {str(e)}")
        return False


def register_certificate_with_aws(iot, cert_path):
    """Register external certificate with AWS IoT with detailed API learning"""
    try:
        with open(cert_path, "r", encoding="utf-8") as f:
            cert_pem = f.read()

        print_info(get_message("registering_external_cert"))
        print_info(get_message("registers_without_new_keys"))
        print_info(get_message("private_key_stays_with_you"))
        time.sleep(1)

        api_details = (
            "register_certificate_without_ca",
            "POST",
            "/certificate/register-no-ca",
            "Registers a self-signed X.509 certificate without requiring CA registration",
            "certificatePem: <PEM-encoded-certificate>, status: ACTIVE",
            get_message("api_output_cert_arn_id"),
        )

        response = safe_operation(
            iot.register_certificate_without_ca,
            "Registering self-signed certificate with AWS IoT",
            api_details,
            certificatePem=cert_pem,
            status="ACTIVE",
        )

        if response:
            cert_arn = response["certificateArn"]
            cert_id = response["certificateId"]

            print(f"\n{get_message('cert_registration_results')}")
            print(f"   {get_message('certificate_id_simple')}: {cert_id}")
            print(f"   {get_message('arn_label')}: {cert_arn}")
            print(get_message("status_active"))
            print(get_message("source_external"))
            print(get_message("registration_method"))

            print(f"\n{get_message('what_happened')}")
            for step in get_message("what_happened_steps"):
                print(step)

            print(f"\n{get_message('key_difference')}")
            for detail in get_message("key_difference_details"):
                print(detail)
            print(get_message("perfect_for_self_signed"))
            print(get_message("production_use_ca_signed"))

            return cert_arn, cert_id, cert_pem

        return None, None, None

    except FileNotFoundError:
        print(get_message("cert_file_not_found"))
        return None, None, None
    except PermissionError:
        print(get_message("permission_denied_cert"))
        return None, None, None
    except UnicodeDecodeError:
        print(get_message("cert_encoding_error"))
        return None, None, None
    except Exception as e:
        print(f"❌ Unexpected error registering certificate: {str(e)}")
        return None, None, None


def register_external_certificate_workflow(iot):
    """Complete workflow for registering external certificate"""
    print(f"\n{get_message('external_registration', 'workflow_titles')}")
    print("=" * 50)
    print(get_message("learning_objectives"))
    for objective in get_message("external_cert_objectives"):
        print(objective)
    print("=" * 50)

    # Step 1: Get certificate file
    cert_path = get_certificate_file_path()
    if not cert_path:
        print(get_message("cert_file_required"))
        return

    # Step 2: Validate certificate
    if not validate_certificate_file(cert_path):
        print(get_message("cert_validation_failed"))
        return

    # Step 3: Select Thing first
    selected_thing = select_thing(iot)
    if not selected_thing:
        print(get_message("thing_selection_required"))
        return

    print(f"\n{get_message('external_cert_registration_moment')}")
    print(get_message("external_cert_explanation"))
    print(f"\n{get_message('next_registering_cert')}")
    input(get_message("press_enter"))

    # Step 4: Register certificate with AWS IoT
    cert_arn, cert_id, cert_pem = register_certificate_with_aws(iot, cert_path)
    if not cert_arn:
        print(get_message("cert_registration_failed"))
        return

    # Step 4.5: Save certificate files locally for MQTT client use
    print(f"\n{get_message('saving_cert_files_locally')}")
    # Validate selected_thing to prevent path traversal
    if not re.match(r"^[a-zA-Z0-9_-]+$", selected_thing):
        print(get_message("skipping_file_save_invalid_name").format(selected_thing))
        print(get_message("cert_registered_files_not_saved"))
        return

    cert_dir = f"certificates/{selected_thing}"
    os.makedirs(cert_dir, exist_ok=True)

    # Save certificate file
    cert_file = f"{cert_dir}/{cert_id}.crt"
    with open(cert_file, "w", encoding="utf-8") as f:
        f.write(cert_pem)
    print(f"📄 Certificate saved: {cert_file}")

    # Handle private key file
    key_file = f"{cert_dir}/{cert_id}.key"
    if cert_path.endswith(".crt") or cert_path.endswith(".pem"):
        # Look for corresponding key file
        key_path = cert_path.replace(".crt", ".key").replace(".pem", ".key")
        # Validate key_path to prevent path traversal
        if not os.path.realpath(key_path).startswith(os.path.realpath(os.getcwd())):
            print(get_message("key_file_within_working_dir"))
        elif os.path.exists(key_path):
            print(get_message("found_private_key").format(key_path))
            with open(key_path, "r", encoding="utf-8") as f:
                key_content = f.read()
            with open(key_file, "w", encoding="utf-8") as f:
                f.write(key_content)
            print(get_message("private_key_saved").format(key_file))
        else:
            print(get_message("private_key_not_found").format(key_path))
            manual_key = input(get_message("enter_key_path")).strip()
            if manual_key:
                # Validate manual_key path to prevent path traversal
                if not os.path.realpath(manual_key).startswith(
                    os.path.realpath(os.getcwd())
                ):
                    print(get_message("key_file_within_working_dir"))
                elif os.path.exists(manual_key):
                    with open(manual_key, "r", encoding="utf-8") as f:
                        key_content = f.read()
                    with open(key_file, "w", encoding="utf-8") as f:
                        f.write(key_content)
                    print(get_message("private_key_saved").format(key_file))
                else:
                    print(get_message("key_file_not_found").format(manual_key))
            else:
                print(get_message("private_key_not_saved"))

    print(f"💾 Certificate files saved to: {cert_dir}")

    print(f"\n{get_message('learning_moment_cert_attachment')}")
    print(get_message("cert_attachment_explanation"))
    print(f"\n{get_message('next_attaching_cert')}")
    input(get_message("press_enter_continue_simple"))

    # Step 5: Attach certificate to Thing
    thing_name = attach_certificate_to_thing(iot, cert_arn, selected_thing)
    if not thing_name:
        print(get_message("cert_attachment_failed"))
        return

    # Step 6: Optional policy attachment
    create_policy = (
        input(f"\n{get_message('would_like_create_policy')}").strip().lower()
    )
    policy_name = None

    if create_policy == "y":
        policy_name = create_policy_interactive(iot)
        if policy_name:
            attach_policy_to_certificate(iot, cert_arn, policy_name)
    else:
        attach_existing = input(get_message("attach_existing_policy")).strip().lower()
        if attach_existing == "y":
            if attach_policy_to_certificate(iot, cert_arn):
                policy_name = "Existing Policy"

    # Step 7: Summary
    print_summary(cert_id, cert_arn, thing_name, policy_name or "None", "External")


def print_summary(
    cert_id, cert_arn, thing_name, policy_name, cert_source="AWS-Generated"
):
    """Print enhanced setup summary with certificate source"""
    print_step("Final", get_message("setup_complete"))

    print(f"\n{get_message('summary_created_configured')}")
    print(f"   {get_message('certificate_id_label')}: {cert_id}")
    print(f"   {get_message('certificate_source_label')}: {cert_source}")
    print(f"   {get_message('attached_to_thing_label')}: {thing_name}")
    print(f"   {get_message('policy_attached_label')}: {policy_name}")

    print(f"\n{get_message('what_you_can_explore')}")
    print(get_message("use_registry_explorer_view"))
    print(get_message("check_thing_attached_cert"))
    print(get_message("review_policy_permissions"))
    if cert_source == "External":
        print(get_message("compare_external_vs_aws"))

    print(f"\n{get_message('key_learning_points')}")
    print(get_message("certs_provide_device_identity"))
    print(get_message("things_represent_iot_devices"))
    print(get_message("policies_define_actions"))
    if cert_source == "External":
        print(get_message("external_certs_integrate_pki"))
        print(get_message("register_vs_create_api"))
    print(get_message("all_components_work_together"))


def main():
    try:
        # Get user's preferred language
        global USER_LANG, messages
        USER_LANG = get_language()
        messages = load_messages("certificate_manager", USER_LANG)

        # Check for debug flag
        debug_mode = "--debug" in sys.argv or "-d" in sys.argv

        print(get_message("title"))
        print(get_message("separator"))

        # Check credentials first - exit immediately if missing
        check_credentials()

        # Display AWS context first
        display_aws_context()

        print(get_message("description_intro"))
        for concept in get_message("security_concepts"):
            print(concept)

        if debug_mode:
            print(f"\n{get_message('debug_enabled')}")
            for feature in get_message("debug_features"):
                print(feature)
        else:
            print(f"\n{get_message('tip')}")

        print(get_message("separator"))

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
        except Exception as e:
            print(f"{get_message('client_error')} {str(e)}")
            return

        # Set global debug mode for safe_operation calls
        global DEBUG_MODE
        DEBUG_MODE = debug_mode

        print_learning_moment("security_foundation")
        input(get_message("press_enter"))

        while True:
            try:
                print(f"\n{get_message('main_menu')}")
                for option in get_message("menu_options"):
                    print(option)

                choice = input(f"\n{get_message('select_option')}").strip()

                if choice == "1":
                    print_learning_moment("certificate_creation")
                    input(get_message("press_enter"))
                    certificate_creation_workflow(iot)

                elif choice == "2":
                    print_learning_moment("external_registration")
                    input(get_message("press_enter"))
                    register_external_certificate_workflow(iot)

                elif choice == "3":
                    print_learning_moment("policy_attachment")
                    input(get_message("press_enter"))
                    attach_policy_workflow(iot)

                elif choice == "4":
                    print_learning_moment("policy_detachment")
                    input(get_message("press_enter"))
                    detach_policy_workflow(iot)

                elif choice == "5":
                    print_learning_moment("certificate_lifecycle")
                    input(get_message("press_enter"))
                    certificate_status_workflow(iot)

                elif choice == "6":
                    print(get_message("goodbye"))
                    break
                else:
                    print(get_message("invalid_choice"))

                try:
                    input(f"\n{get_message('press_enter')}")
                except KeyboardInterrupt:
                    print(f"\n\n{get_message('goodbye')}")
                    break
            except KeyboardInterrupt:
                print(f"\n\n{get_message('goodbye')}")
                break

    except KeyboardInterrupt:
        print(f"\n\n{get_message('goodbye')}")


if __name__ == "__main__":
    main()
