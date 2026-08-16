import boto3
from botocore.config import Config

""" configuration """
my_config = Config(
    region_name='us-east-1',
    s3={'addressing_style': 'path'}
)

s3_client = boto3.client('s3', config=my_config)

TAG_KEY = 'CreatedBy'
TAG_VALUE = 'platform-cli'


def create_bucket(bucket_name, is_public=False):
    """יוצר S3 Bucket עם הגדרות פרטיות/ציבוריות ותגים"""
    s3_client.create_bucket(Bucket=bucket_name)
    #  Public / Private config
    if not is_public:
        # private (default choice)
        s3_client.put_public_access_block(
            Bucket=bucket_name,
            PublicAccessBlockConfiguration={
                'BlockPublicAcls': True,
                'IgnorePublicAcls': True,
                'BlockPublicPolicy': True,
                'RestrictPublicBuckets': True
            }
        )
    else:
        # user request for public bucket (A cli approval is needed)
        s3_client.put_public_access_block(
            Bucket=bucket_name,
            PublicAccessBlockConfiguration={
                'BlockPublicAcls': False,
                'IgnorePublicAcls': False,
                'BlockPublicPolicy': False,
                'RestrictPublicBuckets': False
            }
        )

    # adding tags
    s3_client.put_bucket_tagging(
        Bucket=bucket_name,
        Tagging={
            'TagSet': [
                {'Key': TAG_KEY, 'Value': TAG_VALUE},
                {'Key': 'Owner', 'Value': 'nitzan'}
            ]
        }
    )
    return bucket_name

def is_cli_bucket(bucket_name):
    # checks if it's a cli created based on its tags
    try:
        response = s3_client.get_bucket_tagging(Bucket=bucket_name)
        tags = response.get('TagSet', [])
        return any(t['Key'] == TAG_KEY and t['Value'] == TAG_VALUE for t in tags)
    except Exception:
        # if no tags or not existed
        return False


def get_cli_buckets():
    response = s3_client.list_buckets()
    cli_buckets = []
    for bucket in response.get('Buckets', []):
        name = bucket['Name']
        if is_cli_bucket(name):
            cli_buckets.append(name)
    return cli_buckets


def upload_file_to_bucket(bucket_name, file_path, object_name=None):
    # upload file - only cli
    if not is_cli_bucket(bucket_name):
        raise PermissionError("Access Denied: You can only upload files to CLI-created buckets.")

    if object_name is None:
        object_name = file_path.split('/')[-1]

    s3_client.upload_file(file_path, bucket_name, object_name)


def delete_file_from_bucket(bucket_name, object_name):
    # delete file - only cli
    if not is_cli_bucket(bucket_name):
        raise PermissionError("Access Denied: You can only delete files from CLI-created buckets.")

    s3_client.delete_object(Bucket=bucket_name, Key=object_name)

def list_bucket_files(bucket_name):
    # returns a bucket's list of file, only cli created
    if not is_cli_bucket(bucket_name):
        raise PermissionError("Access Denied: You can only view files from CLI-created buckets.")

    response = s3_client.list_objects_v2(Bucket=bucket_name)
    return [obj['Key'] for obj in response.get('Contents', [])]


def update_bucket_visibility(bucket_name, is_public):
    # update bucket visibility (public/private)
    if not is_cli_bucket(bucket_name):
        raise PermissionError("Access Denied: You can only modify CLI-created buckets.")

    if not is_public:
        s3_client.put_public_access_block(
            Bucket=bucket_name,
            PublicAccessBlockConfiguration={
                'BlockPublicAcls': True,
                'IgnorePublicAcls': True,
                'BlockPublicPolicy': True,
                'RestrictPublicBuckets': True
            }
        )
    else:
        s3_client.put_public_access_block(
            Bucket=bucket_name,
            PublicAccessBlockConfiguration={
                'BlockPublicAcls': False,
                'IgnorePublicAcls': False,
                'BlockPublicPolicy': False,
                'RestrictPublicBuckets': False
            }
        )

def delete_bucket(bucket_name):
    """ deletes the bucket ( has to be empty)"""
    if not is_cli_bucket(bucket_name):
        raise PermissionError("Access Denied: You can only delete CLI-created buckets.")
    s3_client.delete_bucket(Bucket=bucket_name)
