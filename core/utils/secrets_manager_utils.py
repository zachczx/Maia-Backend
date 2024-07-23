import boto3
import json
from botocore.exceptions import ClientError

def get_secret(secret_key):
    secret_name = "prod/maia/backend"
    region_name = "ap-southeast-1"

    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        raise e

    if 'SecretString' in get_secret_value_response:
        secret_string = get_secret_value_response['SecretString']
        secret_dict = json.loads(secret_string)
        if secret_key in secret_dict:
            secret = secret_dict[secret_key]
            return secret
        else:
            raise KeyError(f"{secret_key} not found in secret")
    else:
        raise KeyError("SecretString not found in get_secret_value_response")
