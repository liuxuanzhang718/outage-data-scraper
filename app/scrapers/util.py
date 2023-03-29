import os
import boto3
import io
import pandas as pd

from datetime import datetime
from urllib.error import HTTPError, URLError
from urllib.request import urlopen, Request


def is_aws_env():
    return os.environ.get('AWS_LAMBDA_FUNCTION_NAME') or os.environ.get('AWS_EXECUTION_ENV')


def save(df, bucket_name=None, file_path=None):
    """save df without duplication entries"""
    if is_aws_env():
        # Check if the file exists in the bucket
        s3_client = boto3.client('s3')
        try:
            s3_client.head_object(Bucket=bucket_name, Key=file_path)
        except:
            # initial save
            s3_resource = boto3.resource('s3')
            s3_object = s3_resource.Object(bucket_name, file_path)
            response = s3_object.put(Body=df.to_csv(index=False), ContentType='text/csv')
            status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")
            return f"new outages table initialized at {file_path}. Status - {status}"

        else:
            # combine and drop duplicate
            s3_object = s3_client.get_object(Bucket=bucket_name, Key=file_path)
            df_og = pd.read_csv(io.BytesIO(s3_object['Body'].read()))
            df = df_og.append(df, ignore_index=True)
            # TODO: maybe delete?
            df.drop_duplicates(inplace=True)

            # update to s3
            with io.StringIO() as csv_buffer:
                df.to_csv(csv_buffer, index=False)

                response = s3_client.put_object(
                    Bucket=bucket_name, Key=file_path, Body=csv_buffer.getvalue()
                )
                status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")

            return f"{bucket_name} outages updated to {file_path}. Status - {status}"

    else:
        # TODO: drop duplicate save
        local_path = f"{os.getcwd()}/../{bucket_name}/{file_path}"
        df.to_csv(local_path, index=False)
        print(f"outages data saved to {file_path}")


def check_duplicate():
    pass

def make_request(url, headers=None):
    # TODO: refactor all 'urlopen'
    if headers is None:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_2) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/109.0.0.0 Safari/537.36'}
    request = Request(url, headers=headers or {})
    try:
        with urlopen(request, timeout=10) as response:
            print(response.status)
            return response.read(), response
    except HTTPError as error:
        print(error.status, error.reason)
    except URLError as error:
        print(error.reason)
    except TimeoutError:
        print("Request timed out")

def timenow():
    return datetime.strftime(datetime.now(), "%m-%d-%Y %H:%M:%S")