import boto3
import uuid
import logging
import json

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

dynamodb_client = None
dynamodb_resource = None
existing_tables = None
boto_init_status = None


def init_boto3():
    global dynamodb_client, dynamodb_resource, boto_init_status, existing_tables
    dynamodb_client = boto3.client('dynamodb')
    dynamodb_resource = boto3.resource('dynamodb')
    check_existing_tables()
    logger.info("init_boto3 Existing tables: ", str(existing_tables))
    boto_init_status = True
    return 0


def check_existing_tables():
    global existing_tables
    existing_tables = dynamodb_client.list_tables()['TableNames']


def insert_defaults_login_table():
    for i in range(10):
        email = 's3813265' + str(i) + '@student.rmit.edu.au'
        user_name = 'abhis' + str(i)
        pswd = str(i) + str((i + 1) % 10) + str((i + 2) % 10) + str((i + 3) % 10) + str((i + 4) % 10) + str(
            (i + 5) % 10)
        item = dynamodb_client.put_item(
            TableName='login',
            Item={
                'user_name': {
                    'S': user_name,
                },
                'email': {
                    'S': email,
                },
                'pass': {
                    'S': pswd,
                },
            }
        )
    return True


def insert_defaults_music_table():
    f = open('a2.json')
    data = json.load(f)
    for item in data['songs']:
        title = item.get('title')
        artist = item.get('artist')
        year = item.get('year')
        web_url = item.get('web_url')
        img_url = item.get('img_url')
        item = dynamodb_client.put_item(
            TableName='music',
            Item={
                'title': {
                    'S': title,
                },
                'artist': {
                    'S': artist,
                },
                'year': {
                    'N': year,
                },
                'web_url': {
                    'S': web_url,
                },
                'img_url': {
                    'S': img_url,
                },
            }
        )
    return True


def assert_dynamo_login_table():
    if not boto_init_status:
        print("Unexpected boto_init_status")
        return False
    table_name = 'login'
    logger.info("assert_dynamo_login_table Start")
    check_existing_tables()
    if table_name not in existing_tables:
        logger.info("assert_dynamo_login_table Table does not exist")
        login_table = dynamodb_resource.create_table(
            TableName='login',
            KeySchema=[
                {
                    'AttributeName': 'user_name',
                    'KeyType': 'HASH'
                },
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'user_name',
                    'AttributeType': 'S'
                },
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        dynamodb_client.get_waiter('table_exists').wait(TableName='login')
        print(login_table)
        if login_table is None:
            print("Unexpected failure, login table creation")
        else:
            print("Table login is created")
            insert_defaults_login_table()
    else:
        login_table = dynamodb_resource.Table(table_name)
        logger.info("assert_dynamo_login_table login_table.table_status: ", login_table.table_status)
    return True


def assert_dynamo_music_table():
    if boto_init_status != True:
        print("Unexpected boto_init_status")
        return False
    logger.info("assert_dynamo_music_table Start")
    table_name = 'music'
    check_existing_tables()
    if table_name not in existing_tables:
        logger.info("assert_dynamo_music_table Table does not exist")
        music_table = dynamodb_resource.create_table(
            TableName='music',
            KeySchema=[
                {
                    'AttributeName': 'title',
                    'KeyType': 'HASH'
                },
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'title',
                    'AttributeType': 'S'
                },
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        dynamodb_client.get_waiter('table_exists').wait(TableName='music')
        print(music_table)
        if music_table is None:
            print("Unexpected failure, music table creation")
        else:
            print("Table music is created")
            insert_defaults_music_table()
    else:
        music_table = dynamodb_resource.Table(table_name)
        print("Table status:", music_table.table_status)
    return True


def assert_dynamo():
    if not assert_dynamo_login_table():
        print("Unexpected error, try again")
        return False
    if not assert_dynamo_music_table():
        print("Unexpected error, try again")
        return False
    return True



