from botocore.config import Config

my_config = Config(
    aws_access_key_id='AKIA4WFODKLORNT2B7E6',
    aws_secret_access_key='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',
    region_name='ap-southeast-2',
    signature_version='v4',
    retries={
        'max_attempts': 10,
        'mode': 'standard'
    }
)

# client = boto3.client('kinesis', config=my_config)
