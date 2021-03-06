# import logging
import boto3
from botocore.exceptions import ClientError
from aws_credentials import *
import sys
import os

def upload_file(file_name, bucket, file_key=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :return: True if file was uploaded, else False
    """

    # Upload the file

    s3_client = boto3.client('s3',
        aws_access_key_id = AWS_ACCESS_KEY,
        aws_secret_access_key = AWS_SECRET_KEY
        )

    try:
        #If file_key is provided, use it, else use same file_name
        if file_key:
            response = s3_client.upload_file(file_name, bucket, file_key)
        else:
            response = s3_client.upload_file(file_name, bucket, file_name)
    except ClientError as e:
        raise ValueError(e)
    return True


if __name__ == '__main__':


    file_to_upload = sys.argv[1]
    bucket = sys.argv[2]

    print('Running upload_to_s3.py with following parameters')
    print(f'file_to_upload: {file_to_upload}')
    print(f'bucket: {bucket}')

    upload_file(file_to_upload, bucket)
