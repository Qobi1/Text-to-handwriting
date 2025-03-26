import boto3

s3 = boto3.client(
    "s3",
    region_name="eu-north-1",
    aws_access_key_id="your-access-key",
    aws_secret_access_key="your-secret-key",
)

# List all buckets
buckets = s3.list_buckets()
print([bucket["Name"] for bucket in buckets["Buckets"]])
