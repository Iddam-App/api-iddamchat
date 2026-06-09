import boto3
from botocore.config import Config
from django.conf import settings


def get_r2_client():
    """Get a boto3 client configured for Cloudflare R2."""
    return boto3.client(
        's3',
        endpoint_url=f'https://{settings.R2_ACCOUNT_ID}.r2.cloudflarestorage.com',
        aws_access_key_id=settings.R2_ACCESS_KEY_ID,
        aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
        config=Config(signature_version='s3v4'),
        region_name='auto',
    )


def upload_file_to_r2(file_obj, key):
    """Upload a file object to R2. Returns the key."""
    client = get_r2_client()
    client.upload_fileobj(
        file_obj,
        settings.R2_BUCKET_NAME,
        key,
        ExtraArgs={'ContentType': file_obj.content_type},
    )
    return key


def get_presigned_url(key, expiration=3600):
    """Generate a presigned URL for downloading from R2."""
    client = get_r2_client()
    return client.generate_presigned_url(
        'get_object',
        Params={
            'Bucket': settings.R2_BUCKET_NAME,
            'Key': key,
        },
        ExpiresIn=expiration,
    )


def delete_file_from_r2(key):
    """Delete a file from R2."""
    client = get_r2_client()
    client.delete_object(
        Bucket=settings.R2_BUCKET_NAME,
        Key=key,
    )
