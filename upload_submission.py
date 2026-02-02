#!/usr/bin/env python3
"""
Upload submission script for competition.

This script:
1. Reads the submission zip file
2. Encodes it as base64
3. Sends it to the Lambda endpoint with the API key
4. Displays the results
"""

import sys
import os
import json
import base64
import argparse
import requests
from pathlib import Path


class SubmissionError(Exception):
    """Custom exception for submission errors with title and details."""
    def __init__(self, title: str, details: str = None):
        self.title = title
        self.details = details
        super().__init__(title)


def upload_submission(api_key: str, endpoint: str, role: str, file_path: Path) -> dict:
    """
    Upload submission to the Lambda endpoint.

    Args:
        api_key: API key for authentication
        endpoint: Lambda endpoint URL
        role: Submission role (attacker or defender)
        file_path: Path to the zip file

    Returns:
        Response dictionary from the server
    """
    # Read and encode the file
    with open(file_path, 'rb') as f:
        file_content = f.read()

    encoded_content = base64.b64encode(file_content).decode('utf-8')

    # Prepare the request
    payload = {
        'api_key': api_key,
        'role': role,
        'file': encoded_content,
        'filename': file_path.name
    }
    
    # Send the request
    print(f"📤 Uploading {file_path.name} ({len(file_content)} bytes)...")
    
    try:
        response = requests.post(
            endpoint,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )

        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Upload failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = e.response.json()
                print(f"   Server response: {json.dumps(error_detail, indent=2)}")
                # Valid JSON response with error message from server
                server_error = error_detail.get('error', str(e))
                raise SubmissionError(server_error, str(e))
            except SubmissionError:
                raise
            except:
                # Response exists but isn't valid JSON - likely wrong endpoint
                print(f"   Server response: {e.response.text}")
                raise SubmissionError(
                    "API endpoint not found.",
                    f"{e}\n\nPlease check the submission_endpoint is correct."
                )
        else:
            # No response at all - connection failed, likely wrong endpoint
            raise SubmissionError(
                "API endpoint not found.",
                f"{e}\n\nPlease check the submission_endpoint is correct."
            )


def main():
    """Main upload function."""
    parser = argparse.ArgumentParser(description='Upload submission to competition Lambda')
    parser.add_argument('--api-key', required=True, help='API key for authentication')
    parser.add_argument('--endpoint', required=True, help='Lambda endpoint URL')
    parser.add_argument('--role', required=True, choices=['attacker', 'defender'],
                        help='Submission role: attacker or defender')
    parser.add_argument('--file', required=True, help='Path to submission zip file')
    parser.add_argument('--file-list', help='Path to file containing list of uploaded files')
    parser.add_argument('--submission-path', help='Original submission path (for display)')
    parser.add_argument('--print-info', action='store_true', default=False,
                        help='Print detailed submission info after upload')

    args = parser.parse_args()

    file_path = Path(args.file)

    if not file_path.exists():
        print(f"❌ Error: File not found: {file_path}")
        sys.exit(1)

    if not file_path.suffix == '.zip':
        print(f"⚠️  Warning: File does not have .zip extension: {file_path}")

    print("=" * 60)
    print(f"🚀 Competition Submission Upload ({args.role.upper()})")
    print("=" * 60)
    print()

    try:
        result = upload_submission(args.api_key, args.endpoint, args.role, file_path)
        
        # Save result to file for GitHub Actions output
        with open('submission_result.json', 'w') as f:
            json.dump(result, f, indent=2)
        
        # Parse response
        if isinstance(result, str):
            result = json.loads(result)
        
        # Handle both direct dict and body-wrapped responses
        if 'body' in result:
            body = result['body']
            if isinstance(body, str):
                body = json.loads(body)
        else:
            body = result

        # Print detailed info if requested
        if args.print_info:
            print()
            print("=" * 60)
            print("✅ Submission Successful!")
            print("=" * 60)
            print()
            print(f"  Team: {body.get('team_name', 'Unknown')}")
            print(f"  Role: {body.get('role', 'Unknown').upper()}")
            print()
            print(f"  Total Submissions: {body.get('submission_number', 'Unknown')}")
            print(f"  Attacker Submissions: {body.get('attacker_submissions', 'Unknown')}")
            print(f"  Defender Submissions: {body.get('defender_submissions', 'Unknown')}")
            print(f"  This {body.get('role', 'Unknown').capitalize()} Submission: #{body.get('role_submission_number', 'Unknown')}")
            print()
            print(f"  Files: {body.get('file_count', 'Unknown')} files ({body.get('total_size', 'Unknown')} bytes)")
            print(f"  Time: {body.get('submission_time', 'Unknown')}")
            print(f"  S3 Prefix: {body.get('s3_prefix', 'Unknown')}")
            print()
            print(f"  Message: {body.get('message', 'No message')}")
            print()

        # Set GitHub Actions outputs
        if os.getenv('GITHUB_OUTPUT'):
            with open(os.getenv('GITHUB_OUTPUT'), 'a') as f:
                f.write(f"status=success\n")
                f.write(f"submission_number={body.get('submission_number', 'Unknown')}\n")
                f.write(f"message={body.get('message', 'Submission successful')}\n")

        # Write GitHub Actions Job Summary
        if os.getenv('GITHUB_STEP_SUMMARY'):
            role = body.get('role', 'unknown')
            role_emoji = '🔴' if role == 'attacker' else '🔵'
            with open(os.getenv('GITHUB_STEP_SUMMARY'), 'a') as f:
                f.write(f"## {role_emoji} Submission Successful!\n\n")
                f.write(f"### Team: **{body.get('team_name', 'Unknown')}**\n\n")
                f.write("| Metric | Value |\n")
                f.write("|--------|-------|\n")
                f.write(f"| **Role** | {role.upper()} |\n")
                f.write(f"| **This Submission** | #{body.get('role_submission_number', '?')} |\n")
                f.write(f"| **Total Submissions** | {body.get('submission_number', '?')} |\n")
                f.write(f"| **Attacker Submissions** | {body.get('attacker_submissions', '?')} |\n")
                f.write(f"| **Defender Submissions** | {body.get('defender_submissions', '?')} |\n")
                f.write(f"| **Files Uploaded** | {body.get('file_count', '?')} |\n")
                f.write(f"| **Total Size** | {body.get('total_size', '?')} bytes |\n")
                f.write(f"| **Submission Time** | {body.get('submission_time', '?')} |\n")
                f.write(f"\n> 💡 {body.get('message', 'Submission successful')}\n")

                # Add file list if provided
                if args.file_list and Path(args.file_list).exists():
                    files = Path(args.file_list).read_text().strip().split('\n')
                    files = [f for f in files if f]  # filter empty lines
                    if files:
                        # Show submission path prefix if provided
                        path_prefix = args.submission_path or ''
                        path_prefix = path_prefix.rstrip('/')
                        f.write(f"\n<details>\n<summary>📁 Uploaded Files ({path_prefix}/)</summary>\n\n")
                        f.write("```\n")
                        for file in files:
                            f.write(f"{path_prefix}/{file}\n")
                        f.write("```\n</details>\n")

        sys.exit(0)
        
    except Exception as e:
        print()
        print("=" * 60)
        print("❌ Submission Failed!")
        print("=" * 60)
        print()
        print(f"  Error: {str(e)}")
        print()

        # Set GitHub Actions outputs
        if os.getenv('GITHUB_OUTPUT'):
            with open(os.getenv('GITHUB_OUTPUT'), 'a') as f:
                f.write("status=failure\n")
                f.write(f"message=Submission failed: {str(e)}\n")

        # Write GitHub Actions Job Summary for failure
        if os.getenv('GITHUB_STEP_SUMMARY'):
            with open(os.getenv('GITHUB_STEP_SUMMARY'), 'a') as f:
                f.write("## ❌ Submission Failed\n\n")
                if isinstance(e, SubmissionError) and e.details:
                    f.write(f"**Error:** {e.title}\n\n")
                    f.write(f"```\n{e.details}\n```\n")
                else:
                    f.write(f"**Error:** {str(e)}\n")

        sys.exit(1)


if __name__ == '__main__':
    main()

