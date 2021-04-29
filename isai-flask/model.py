import boto3
import uuid
import logging
import json
import os
import requests
from boto3.dynamodb.conditions import Key, Attr
from flask import Flask

current_app = Flask(__name__)

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
    current_app.logger.debug('model.py init_boto3 BEGIN')
    # current_app.logger.info('model.py init_boto3 error: %s', error)
    global dynamodb_client, dynamodb_resource, boto_init_status, existing_tables, s3_client, s3_resource
    dynamodb_client = boto3.client('dynamodb')
    dynamodb_resource = boto3.resource('dynamodb')
    s3_client = boto3.client('s3')
    s3_resource = boto3.resource('s3')
    current_app.logger.info(
        'model.py init_boto3 dynamodb_client, dynamodb_resource, s3_client, s3_resource: %s %s %s %s',
        dynamodb_client, dynamodb_resource,
        s3_client, s3_resource)
    check_existing_tables()
    boto_init_status = True
    assert_dynamo()
    current_app.logger.debug('model.py init_boto3 END')
    return True


def check_existing_tables():
    current_app.logger.debug('model.py check_existing_tables BEGIN')
    global existing_tables
    existing_tables = dynamodb_client.list_tables()['TableNames']
    current_app.logger.info('model.py check_existing_tables error: %s', existing_tables)
    current_app.logger.debug('model.py check_existing_tables END')


def insert_defaults_login_table():
    current_app.logger.debug('model.py insert_defaults_login_table BEGIN')
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
    current_app.logger.debug('model.py insert_defaults_login_table END')
    return True


def insert_defaults_music_table():
    current_app.logger.debug('model.py insert_defaults_music_table BEGIN')
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
    current_app.logger.debug('model.py insert_defaults_music_table END')
    return True


def download_all_images_from_json_to_bucket(url, uid):
    current_app.logger.debug('model.py download_all_images_from_json_to_bucket BEGIN')
    response = requests.get(url)
    current_app.logger.debug('model.py download_all_images_from_json_to_bucket %s', response)
    file = open("temp.jpg", "wb")
    file.write(response.content)
    file.close()
    s3_client.upload_file('temp.jpg', 'abhi-dev-music-images', uid + '.jpg', ExtraArgs={'ACL': 'public-read'})
    os.remove('temp.jpg')
    return 'https://abhi-dev-music-images.s3-ap-southeast-2.amazonaws.com/' + uid + '.jpg'


def assert_s3_bucket():
    current_app.logger.debug('model.py assert_s3_bucket BEGIN')
    bucket_list = []
    for s in s3_client.list_buckets().get('Buckets'):
        bucket_list.append(s.get('Name'))
    if 'abhi-dev-music-images' in bucket_list:
        current_app.logger.debug('model.py assert_s3_bucket S3 found')
        current_app.logger.debug('model.py assert_s3_bucket END')
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
        current_app.logger.debug('model.py assert_s3_bucket END')
        return True


def assert_dynamo_login_table():
    current_app.logger.debug('model.py assert_dynamo_login_table BEGIN')
    if not boto_init_status:
        current_app.logger.debug('model.py assert_dynamo_login_table Unexpected boto_init_status')
        return False
    table_name = 'login'
    global login_table
    check_existing_tables()
    if table_name not in existing_tables:
        current_app.logger.debug('model.py assert_dynamo_login_table Table does not exist')
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
        current_app.logger.info('model.py assert_dynamo_login_table login table: %s', login_table)
        if login_table is None:
            current_app.logger.debug(
                'model.py assert_dynamo_login_table Unexpected failure, login table not created')
        else:
            current_app.logger.debug('model.py assert_dynamo_login_table Table login is created')
            insert_defaults_login_table()
    else:
        login_table = dynamodb_resource.Table(table_name)
        logger.info("model.py assert_dynamo_login_table login_table.table_status: %s",
                    login_table.table_status)
    current_app.logger.debug('model.py assert_dynamo_music_table END')
    return True


def assert_dynamo_music_table():
    current_app.logger.debug('model.py assert_dynamo_music_table BEGIN')
    if boto_init_status != True:
        current_app.logger.debug('model.py assert_dynamo_music_table Unexpected boto_init_status')
        return False
    table_name = 'music'
    global music_table
    check_existing_tables()
    if table_name not in existing_tables:
        current_app.logger.debug('model.py assert_dynamo_music_table Table does not exist')
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
        current_app.logger.info('model.py assert_dynamo_music_table music table: %s', music_table)
        if music_table is None:
            current_app.logger.debug(
                'model.py assert_dynamo_music_table Unexpected failure, music table not created')
        else:
            current_app.logger.debug('model.py assert_dynamo_music_table music table created')
            insert_defaults_music_table()
    else:
        music_table = dynamodb_resource.Table(table_name)
        current_app.logger.debug('model.py assert_dynamo_music_table music table status: %s',
                                 music_table.table_status)
        current_app.logger.debug('model.py assert_dynamo_music_table END')
    return True


def assert_dynamo():
    current_app.logger.debug('model.py assert_dynamo START')
    if not assert_dynamo_login_table():
        current_app.logger.debug('model.py assert_dynamo Unexpected error, try again END')
        return False
    if not assert_dynamo_music_table():
        current_app.logger.debug('model.py assert_dynamo Unexpected error, try again END')
        return False
    if not assert_s3_bucket():
        current_app.logger.debug('model.py assert_dynamo Unexpected error, try again END')
        return False
    current_app.logger.debug('model.py assert_dynamo END')
    return True


def validate_user_return_session(email, pswd):
    current_app.logger.debug('model.py validate_user_return_session BEGIN')
    current_app.logger.info('model.py validate_user_return_session email, pswd: %s %s', email, pswd)
    response = login_table.get_item(
        Key={
            'email': email,
        }
    )
    current_app.logger.info('model.py validate_user_return_session response: %s', response)
    if 'Item' in response and response['Item']['pass'] == pswd:
        session_token = str(uuid.uuid1().hex)
        current_app.logger.debug('model.py validate_user_return_session END')
        return store_session(session_token, response['Item'])
    current_app.logger.debug('model.py validate_user_return_session END')
    return None


def validate_user_email(email):
    current_app.logger.debug('model.py validate_user_email BEGIN')
    current_app.logger.info('model.py validate_user_email email: %s', email)
    response = login_table.get_item(
        Key={
            'email': email,
        }
    )
    current_app.logger.info('model.py validate_user_email response: %s', response)
    if 'Item' in response:
        current_app.logger.info('model.py validate_user_email response item: %s', response['Item'])
        current_app.logger.debug('model.py validate_user_email END')
        return True
    current_app.logger.debug('model.py validate_user_email END')
    return False


def store_session(session_id, session_details):
    current_app.logger.debug('model.py store_session BEGIN')
    current_app.logger.info('model.py store_session session_id, session_details: %s %s', session_id,
                            session_details)
    global session_dict
    session_dict[session_id] = session_details
    current_app.logger.info('model.py store_session session_dict[session_id]: %s', session_dict[session_id])
    current_app.logger.debug('model.py store_session END')
    return session_id


def refresh_session(session_id):
    current_app.logger.debug('model.py refresh_session BEGIN')
    email = session_dict[session_id].get('email')
    current_app.logger.info('model.py store_session session_id, email: %s %s', session_id, email)
    response = login_table.get_item(
        Key={
            'email': email,
        }
    )
    current_app.logger.info('model.py refresh_session response: %s', response)
    if 'Item' in response:
        store_session(session_id, response['Item'])
        current_app.logger.debug('model.py refresh_session END')
        return True
    current_app.logger.debug('model.py refresh_session END')
    return False


def remove_session(session_id):
    current_app.logger.debug('model.py remove_session BEGIN')
    global session_dict
    session_dict.pop(session_id, None)
    current_app.logger.debug('model.py remove_session END')
    return True


def validate_session(session_id):
    current_app.logger.debug('model.py validate_session')
    return session_id in session_dict


def get_user_from_session(session_id):
    current_app.logger.debug('model.py get_user_from_session BEGIN')
    if session_id not in session_dict:
        current_app.logger.debug('model.py get_user_from_session END')
        return False
    else:
        new_dict = session_dict[session_id]
        new_dict.pop('pass', None)
        current_app.logger.info('model.py get_user_from_session %s', new_dict)
        current_app.logger.debug('model.py get_user_from_session END')
        return new_dict


def create_new_user(email, username, pswd):
    current_app.logger.debug('model.py create_new_user BEGIN')
    login_table.put_item(
        Item={
            'user_name': username,
            'email': email,
            'pass': pswd,
        }
    )
    current_app.logger.debug('model.py create_new_user END')
    return True


def query_music_table(title, year, artist):
    current_app.logger.debug('model.py query_music_table BEGIN')
    current_app.logger.info('model.py query_music_table title, year, artist: %s %s %s', title, year, artist)
    year = year if year is None else int(year)
    response = music_table.scan(
        FilterExpression=(Attr('title').ne(title) if title is None else Attr('title').eq(title)) &
                         (Attr('year').ne(year) if year is None else Attr('year').eq(year)) &
                         (Attr('artist').ne(artist) if artist is None else Attr('artist').eq(artist))
    )
    current_app.logger.debug('model.py query_music_table END')
    return response['Items']


def session_music_subscribe(session, music):
    current_app.logger.debug('model.py session_music_subscribe BEGIN')
    sub_list = get_sub_list(session)
    email = session_dict[session].get('email')
    current_app.logger.debug('model.py session_music_subscribe session, music, email, sub_list: %s %s %s %s',
                             session, music, email, sub_list)
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
    current_app.logger.info('model.py session_music_subscribe response: %s', response)
    current_app.logger.debug('model.py session_music_subscribe END')
    return True


def session_music_unsubscribe(session, music):
    current_app.logger.debug('model.py session_music_unsubscribe BEGIN')
    sub_list = get_sub_list(session)
    email = session_dict[session].get('email')
    current_app.logger.debug(
        'model.py session_music_unsubscribe session, music, email, sub_list: %s %s %s %s',
        session, music, email, sub_list)
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
    current_app.logger.info('model.py session_music_unsubscribe response: %s', response)
    current_app.logger.debug('model.py session_music_unsubscribe END')
    return True


def get_sub_list(session):
    current_app.logger.debug('model.py get_sub_list BEGIN')
    refresh_session(session)
    sub_list = session_dict.get(session).get('sub_list')
    current_app.logger.debug('model.py get_sub_list END')
    return sub_list


def get_music_dict_from_sub_id(uid):
    current_app.logger.debug('model.py get_music_dict_from_sub_id BEGIN')
    response = music_table.get_item(
        Key={
            'id': uid,
        }
    )
    current_app.logger.info('model.py get_music_dict_from_sub_id response.get(Item):%s', response.get('Item'))
    current_app.logger.debug('model.py get_music_dict_from_sub_id END')
    return response.get('Item')
