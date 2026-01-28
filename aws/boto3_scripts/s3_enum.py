#!/usr/bin/env python3
"""
AWS S3 Bucket Public Access Check
Fetches bucket names, URLs, and public access status
"""

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

def is_bucket_public(s3_client, bucket_name):
    """
    Determine if a bucket is public or has public access
    """
    try:
        # Check public access block configuration
        try:
            response = s3_client.get_public_access_block(Bucket=bucket_name)
            config = response['PublicAccessBlockConfiguration']

            # If all public access is blocked, it's private
            if all([
                config.get('BlockPublicAcls', False),
                config.get('IgnorePublicAcls', False),
                config.get('BlockPublicPolicy', False),
                config.get('RestrictPublicBuckets', False)
            ]):
                return 'Private'
        except ClientError as e:
            if e.response['Error']['Code'] != 'NoSuchPublicAccessBlockConfiguration':
                pass  # Continue to check ACL and policy

        # Check bucket ACL for public access
        try:
            acl = s3_client.get_bucket_acl(Bucket=bucket_name)
            for grant in acl['Grants']:
                grantee = grant.get('Grantee', {})
                if grantee.get('Type') == 'Group':
                    uri = grantee.get('URI', '')
                    if 'AllUsers' in uri or 'AuthenticatedUsers' in uri:
                        return 'PUBLIC (ACL)'
        except ClientError:
            pass

        # Check bucket policy for public access
        try:
            policy = s3_client.get_bucket_policy(Bucket=bucket_name)
            policy_text = policy['Policy'].lower()
            if '"principal":"*"' in policy_text or '"principal":{"aws":"*"}' in policy_text:
                return 'PUBLIC (Policy)'
        except ClientError as e:
            if e.response['Error']['Code'] != 'NoSuchBucketPolicy':
                pass

        return 'Private'

    except Exception as e:
        return f'Error: {str(e)[:30]}'

def get_bucket_region(s3_client, bucket_name):
    """
    Get the region of a bucket
    """
    try:
        response = s3_client.get_bucket_location(Bucket=bucket_name)
        region = response['LocationConstraint']
        return region if region else 'us-east-1'
    except Exception:
        return 'us-east-1'

def enumerate_s3_buckets():
    """
    Enumerate all S3 buckets with name, URL, and public status
    """
    try:
        s3_client = boto3.client('s3')

        # List all buckets
        response = s3_client.list_buckets()

        buckets = []

        print(f"Found {len(response['Buckets'])} bucket(s). Checking public access...\n")

        for idx, bucket in enumerate(response['Buckets'], 1):
            bucket_name = bucket['Name']

            print(f"Processing {idx}/{len(response['Buckets'])}: {bucket_name}")

            # Get region for URL
            region = get_bucket_region(s3_client, bucket_name)

            # Construct S3 URL
            if region == 'us-east-1':
                url = f"https://{bucket_name}.s3.amazonaws.com"
            else:
                url = f"https://{bucket_name}.s3.{region}.amazonaws.com"

            # Check if public
            public_status = is_bucket_public(s3_client, bucket_name)

            buckets.append({
                'Name': bucket_name,
                'URL': url,
                'Region': region,
                'Public': public_status
            })

        return buckets

    except NoCredentialsError:
        print("Error: AWS credentials not found. Please configure your AWS credentials.")
        print("Run 'aws configure' or set up your credentials file.")
        return None

    except ClientError as e:
        print(f"Error accessing AWS: {e}")
        return None

    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

def print_buckets(buckets):
    """
    Print buckets in a formatted table
    """
    if not buckets:
        print("No S3 buckets found.")
        return

    print(f"\n{'='*140}")
    print(f"Total S3 Buckets: {len(buckets)}")

    # Count public buckets
    public_count = sum(1 for b in buckets if 'PUBLIC' in b['Public'])
    if public_count > 0:
        print(f"⚠️  PUBLIC BUCKETS FOUND: {public_count}")

    print(f"{'='*140}\n")

    print(f"{'Bucket Name':<40} {'URL':<60} {'Region':<15} {'Status':<20}")
    print("-" * 140)

    for bucket in buckets:
        status_display = bucket['Public']
        if 'PUBLIC' in status_display:
            status_display = f"⚠️  {status_display}"

        print(f"{bucket['Name']:<40} {bucket['URL']:<60} {bucket['Region']:<15} {status_display:<20}")

    print("-" * 140)

def main():
    """
    Main function
    """
    print("AWS S3 Bucket Enumeration - Name, URL, and Public Access Status")
    print("=" * 140)
    print()

    buckets = enumerate_s3_buckets()

    if buckets is not None:
        print_buckets(buckets)

        # Optionally save to file
        save_option = input("\nWould you like to save this to a CSV file? (y/n): ")
        if save_option.lower() == 'y':
            try:
                import csv
                filename = 's3_buckets_public_check.csv'

                with open(filename, 'w', newline='') as csvfile:
                    if buckets:
                        fieldnames = ['Name', 'URL', 'Region', 'Public']
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        writer.writeheader()
                        writer.writerows(buckets)

                print(f"✓ Data saved to {filename}")
            except Exception as e:
                print(f"Error saving to CSV: {e}")

if __name__ == "__main__":
    main()
