## Tools

* go install -v github.com/shabarkin/aws-enumerator@latest
```
	aws-enumerator cred
	aws-enumerator enum -services all
	aws-enumerator dump -services <service>
```

## AWS CLI Commands

```
aws configure	            # Run as well aws-enumerator cred (to make sure you update the tool)
aws sts get-caller-identity # whoami for aws
```

```
aws iam list-attached-user-policies --user-name <USERNAME>	# List all policies
```

```
aws iam get-policy --policy-arn <POLICY_ARN>											# Get Policy VersionId
aws iam get-policy-version --policy-arn <PolicyArn> --version-id <DefaultVersionId> 	# Get Policy Document
```

```
aws iam get-role --role-name <ROLE_NAME>					# List roles of a role name
aws iam list-attached-role-policies --role-name <ROLE_NAME>	# List policies of role name
```

```
aws sts assume-role --role-arn <ROLE_ARN> --role-session-name <ROLE_NAME>
(aws sts assume-role --role-arn arn:aws:iam::427648302155:role/ExternalCostOpimizeAccess --role-session-name ExternalCostOpimizeAccess)
aws sts assume-role --role-arn <ROLE_ARN> --role-session-name <ROLE_NAME> --external-id 37911
        "AssumeRolePolicyDocument": {                                                            
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "AWS": "arn:aws:iam::427648302155:user/ext-cost-user"
                    },
                    "Action": "sts:AssumeRole",
                    "Condition": {
                        "StringEquals": {
                            "sts:ExternalId": "37911" <-----------------------------------------
                        }
                    }
                }
            ]
        }
```

```
aws s3 ls <BUCKET_NAME>     				# ls s3 bucket
aws s3 cp s3://<BUCKET_NAME>/<FILE_NAME> -	# cp s3 bucket file
```

```
aws secretsmanager list-secrets --query 'SecretList[*].[Name, Description, ARN]' --output json 	# aws-enumerator enum -services all
```

## Cloud Shell

```
TOKEN=$(curl -X PUT localhost:1338/latest/api/token -H "X-aws-ec2-metadata-token-ttl-seconds: 60")
curl localhost:1338/latest/meta-data/container/security-credentials -H "X-aws-ec2-metadata-token: $TOKEN"

{
        "Type": "",
        "AccessKeyId": "REDACTED",
        "SecretAccessKey": "REDACTED",
        "Token": "REDACTED",
        "Expiration": "2026-01-14T18:35:26Z",
        "Code": "Success"
}
```
