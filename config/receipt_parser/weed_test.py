from time import sleep

import boto3

print("Setting up boto3 client...")
s3 = boto3.client(
    "s3",
    endpoint_url="http://seaweedfs:8333",
    aws_access_key_id="admin",
    aws_secret_access_key="secret",
    region_name="us-east-1",
)

test_file_name: str = "requirements.txt"

print(f"Uploading {test_file_name}...")
with open(test_file_name, "rb") as f:
    s3.upload_fileobj(
        f,
        "rp-bucket",
        "requirements.txt",
    )

sleep(5)

print(f"Downloading {test_file_name}...")
response = s3.get_object(
    Bucket="rp-bucket",
    Key=test_file_name,
)

print(f"Reading response...")
image_data = response["Body"].read()
print(image_data)
