import boto3 # importing the boto3 library
import json # to help our eyes
import os # to allow creation of directories, and change directory
from datetime import datetime
def custom_serializer(obj): # This was needed to bypass a JSON TypeError issue
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")
access_key = 'REDACTED' # access key to use for the script
secret_access_key = 'REDACTED' # secret key to use for the script
region = 'us-east-1'
bucket = 'REDACTED' # region to use for the script
try:
    os.mkdir(bucket)
except Exception:
    pass
os.chdir(bucket)
session = boto3.Session(aws_access_key_id=access_key, aws_secret_access_key=secret_access_key) # Initiates the session information for the script
s3_client = session.client("s3") # Initiate the s3 session
sts_client = session.client("sts") # Initiate the sts session
secrets_client = session.client("secretsmanager", region_name=region) # Initate the secretsmanager session
sts_caller_info = sts_client.get_caller_identity() # STS whoami
if sts_caller_info:
    #sts_caller_info = json.dumps(sts_caller_info, indent=4, sort_keys=True)
    #print(sts_caller_info) # prints the full index
    print(f"UserId: {sts_caller_info['UserId']}") # Prints the user id value in the index
    print(f"Account: {sts_caller_info['Account']}") # Prints the account value in the index
    print(f"ARN: {sts_caller_info['Arn']}") # Prints the ARN value in the index
bucket_objects = s3_client.list_objects_v2(Bucket=bucket)
for bucket_contents in bucket_objects["Contents"]:
    file_name = str(bucket_contents["Key"])
    print(f"File {file_name} found!")
    with open(file_name, "wb") as file:
         s3_client.download_fileobj(bucket, file_name, file)
         print(f"Downloaded {file_name}")
secrets_list = secrets_client.list_secrets() # List secrets available in SecretsManager
if secrets_list:
    print(json.dumps(secrets_list, indent=4, sort_keys=True, default=custom_serializer)) # Pretty-print the secrets list without modifying its original format
    for secret in secrets_list.get("SecretList"):  # Use .get() to safely access 'SecretList'
        name = secret["Name"]  # Extract the 'Name' field
        try:
            secret_dump = secrets_client.get_secret_value(SecretId=name)  # Get secret details
            print(json.dumps(secret_dump, indent=4, sort_keys=True, default=custom_serializer))
        except Exception:
            pass
