import boto3
import uuid
import logging
import json
import os
import requests
from boto3.dynamodb.conditions import Key, Attr

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

dynamodb_client = None
dynamodb_resource = None
existing_tables = None
boto_init_status = None
login_table = None
music_table = None
s3_client = None
s3_resource = None
session_dict = {}


def init_boto3():
    global dynamodb_client, dynamodb_resource, boto_init_status, existing_tables, s3_client, s3_resource
    dynamodb_client = boto3.client('dynamodb')
    dynamodb_resource = boto3.resource('dynamodb')
    s3_client = boto3.client('s3')
    s3_resource = boto3.resource('s3')
    check_existing_tables()
    boto_init_status = True
    print("init_boto3 Existing tables: ", str(existing_tables))
    assert_dynamo()
    return True


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
                'id': {
                    'S': str(uuid.uuid4().hex),
                },
                'user_name': {
                    'S': user_name,
                },
                'email': {
                    'S': email,
                },
                'pass': {
                    'S': pswd,
                },
                'sub_list': {
                    'SS': [''],
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
        uid = str(uuid.uuid4().hex)
        img_url = item.get('img_url')
        img_url = download_all_images_from_json_to_bucket(img_url, uid)
        item = dynamodb_client.put_item(
            TableName='music',
            Item={
                'id': {
                    'S': uid,
                },
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


def download_all_images_from_json_to_bucket(url, uid):
    response = requests.get(url)
    file = open("temp.jpg", "wb")
    file.write(response.content)
    file.close()
    s3_client.upload_file('temp.jpg', 'abhi-dev-music-images', uid + '.jpg', ExtraArgs={'ACL': 'public-read'})
    os.remove('temp.jpg')
    return 'https://abhi-dev-music-images.s3-ap-southeast-2.amazonaws.com/' + uid + '.jpg'


def assert_s3_bucket():
    bucket_list = []
    for s in s3_client.list_buckets().get('Buckets'):
        bucket_list.append(s.get('Name'))
    if 'abhi-dev-music-images' in bucket_list:
        print("S3 found!")
        return True
    else:
        response = s3_client.create_bucket(
            ACL='public-read',
            Bucket='abhi-dev-music-images1',
            CreateBucketConfiguration={
                'LocationConstraint': 'ap-southeast-2'
            },
            ObjectLockEnabledForBucket=False
        )
        return True


def assert_dynamo_login_table():
    if not boto_init_status:
        print("Unexpected boto_init_status")
        return False
    table_name = 'login'
    global login_table
    logger.info("assert_dynamo_login_table Start")
    check_existing_tables()
    if table_name not in existing_tables:
        logger.info("assert_dynamo_login_table Table does not exist")
        login_table = dynamodb_resource.create_table(
            TableName='login',
            KeySchema=[
                {
                    'AttributeName': 'email',
                    'KeyType': 'HASH'
                },
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'email',
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
    global music_table
    check_existing_tables()
    if table_name not in existing_tables:
        logger.info("assert_dynamo_music_table Table does not exist")
        music_table = dynamodb_resource.create_table(
            TableName='music',
            KeySchema=[
                {
                    'AttributeName': 'id',
                    'KeyType': 'HASH'
                },
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'id',
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
    print("Assert Dynamo")
    if not assert_dynamo_login_table():
        print("Unexpected error, try again")
        return False
    if not assert_dynamo_music_table():
        print("Unexpected error, try again")
        return False
    if not assert_s3_bucket():
        print("Unexpected error, try again")
        return False
    return True


def validate_user_return_session(email, pswd):
    response = login_table.get_item(
        Key={
            'email': email,
        }
    )
    print("Response", response)
    if 'Item' in response and response['Item']['pass'] == pswd:
        session_token = str(uuid.uuid1().hex)
        return store_session(session_token, response['Item'])
    return None


def validate_user_email(email):
    response = login_table.get_item(
        Key={
            'email': email,
        }
    )
    print("Response", response)
    if 'Item' in response:
        print("Response item", response['Item'])
        return True
    return False


def store_session(session_id, session_details):
    global session_dict
    session_dict[session_id] = session_details
    return session_id


def refresh_session(session_id):
    email = session_dict[session_id].get('email')
    response = login_table.get_item(
        Key={
            'email': email,
        }
    )
    print("Response", response)
    if 'Item' in response:
        store_session(session_id, response['Item'])
        return True
    return False


def remove_session(session_id):
    global session_dict
    session_dict.pop(session_id, None)
    return True


def validate_session(session_id):
    return session_id in session_dict


def get_user_from_session(session_id):
    if session_id not in session_dict:
        return False
    else:
        new_dict = session_dict[session_id]
        new_dict.pop('pass', None)
        return new_dict


def create_new_user(email, username, pswd):
    login_table.put_item(
        Item={
            'user_name': username,
            'email': email,
            'pass': pswd,
        }
    )
    return True


def query_music_table(title, year, artist):
    # if type(year) is not int:
    #     return False
    year = year if year is None else int(year)
    response = music_table.scan(
        FilterExpression=(Attr('title').ne(title) if title is None else Attr('title').eq(title)) &
                         (Attr('year').ne(year) if year is None else Attr('year').eq(year)) &
                         (Attr('artist').ne(artist) if artist is None else Attr('artist').eq(artist))
    )
    return response['Items']


def session_music_subscribe(session, music):
    sub_list = get_sub_list(session)
    email = session_dict[session].get('email')
    if sub_list is None:
        sub_list = []
    if music in sub_list:
        return True
    sub_list.append(music)
    response = login_table.update_item(
        Key={
            'email': email,
        },
        UpdateExpression="set sub_list=:s",
        ExpressionAttributeValues={
            ':s': sub_list,
        },
    )
    print(response)
    return True


def session_music_unsubscribe(session, music):
    sub_list = get_sub_list(session)
    print(sub_list)
    email = session_dict[session].get('email')
    print(email)
    if sub_list is None:
        return False
    if music in sub_list:
        sub_list.remove(music)
    else:
        return True
    response = login_table.update_item(
        Key={
            'email': email,
        },
        UpdateExpression="set sub_list=:s",
        ExpressionAttributeValues={
            ':s': sub_list,
        },
    )
    print(response)
    return True


def get_sub_list(session):
    refresh_session(session)
    sub_list = session_dict.get(session).get('sub_list')
    return sub_list


def get_music_dict_from_sub_id(uid):
    response = music_table.get_item(
        Key={
            'id': uid,
        }
    )
    # music_dict = {}
    # music_dict['title'] = response.get('Item').get('title')
    # music_dict['artist'] = response.get('Item').get('artist')
    # music_dict['year'] = response.get('Item').get('year')
    # music_dict['img_url'] = response.get('Item').get('img_url')
    # music_dict['web_url'] = response.get('Item').get('web_url')
    # print(music_dict)
    print(response.get('Item'))
    return response.get('Item')
