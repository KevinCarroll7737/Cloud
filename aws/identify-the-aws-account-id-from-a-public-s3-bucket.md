Attack Path
===

<img width="1920" height="1020" alt="image" src="https://github.com/user-attachments/assets/29857ab1-16a3-48c4-967c-30eca926d1df" />

Configuring AWS Account
---

1. Create a User on your AWS Account (IAM > Users)
```
{
    "Version": "2012-10-17",
    "Statement": {
        "Effect": "Allow",
        "Action": "sts:AssumeRole",
        "Resource": "arn:aws:iam::<YOUR_AWS_ACCOUNT_ID>:role/<YOUR_ROLE_NAME>"
    }
}
``` 
2. Create a Role on you AWS Account (IAM > Roles)
```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllBucketsGetObject",
      "Effect": "Allow",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::*/*"
    },
    {
      "Sid": "AllBucketsList",
      "Effect": "Allow",
      "Action": "s3:ListBucket",
      "Resource": "arn:aws:s3:::*"
    }
  ]
}

```
3. Assign the Role to your User (IAM > Role > The new Role > Trust RelationShips)
```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::<YOUR_AWS_ACCOUNT_ID>:user/<New_USER>"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
```

Solution
---
1. Find a S3 bucket name
2. Try to brute-force the AWS AccountID of the S3 bucket
```
aws configure # your user with assume role role
s3-account-search arn:aws:iam::<your_aws_account_id>:role/<assume_role> <bucket_name>
```
4. Get the AWS Region from the HTTP header
```
curl -I https://<bucket_name>.s3.amazonaws.com
```
5. Check for EC2 Public Snapshots
```
AWS Console > EC2 > Snapshot > Public Snapshot: Owner = <Brute_forced_AccountID>
```

Defense
---

AWS account IDs can be used to search for EC2 public snapshots. It is recommended to avoid exposing EC2 snapshots publicly.

Lab URL
---

https://pwnedlabs.io/labs/identify-the-aws-account-id-from-a-public-s3-bucket
