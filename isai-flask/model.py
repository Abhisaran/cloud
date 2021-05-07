import boto3
import uuid
import logging
import json
import os
import requests
from boto3.dynamodb.conditions import Attr

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

if __name__ != '__main__':
    gunicorn_error_logger = logging.getLogger('gunicorn.error')
    logger.handlers.extend(gunicorn_error_logger.handlers)
    logger.setLevel(logging.DEBUG)


def init_boto3():
    logger.debug('model.py init_boto3 BEGIN')
    dynamodb_client = boto3.client('dynamodb')
    dynamodb_resource = boto3.resource('dynamodb')
    s3_client = boto3.client('s3')
    s3_resource = boto3.resource('s3')
    logger.info(
        'model.py init_boto3 dynamodb_client, dynamodb_resource, s3_client, s3_resource: %s %s %s %s',
        dynamodb_client, dynamodb_resource,
        s3_client, s3_resource)
    bucket_list = []
    for s in s3_client.list_buckets().get('Buckets'):
        bucket_list.append(s.get('Name'))
    existing_tables = dynamodb_client.list_tables()['TableNames']
    logger.info('model.py init_boto3 existing, buckets: %s %s', existing_tables, bucket_list)
    if 'login' not in existing_tables:
        if not assert_dynamo_login_table(dynamodb_client, dynamodb_resource):
            logger.debug('model.py assert_dynamo Unexpected error, try again END')
        return False
    if 'music' not in existing_tables:
        if not assert_dynamo_music_table(dynamodb_client, dynamodb_resource, s3_client):
            logger.debug('model.py assert_dynamo Unexpected error, try again END')
            return False
    if 'abhi-dev-music-images' not in bucket_list:
        if not assert_s3_bucket(s3_client):
            logger.debug('model.py assert_dynamo Unexpected error, try again END')
            return False

    logger.debug('model.py init_boto3 END')
    return True


#
# def check_existing_tables():
#     logger.debug('model.py check_existing_tables BEGIN')
#     existing_tables = boto3.client('dynamodb').list_tables()['TableNames']
#     logger.info('model.py check_existing_tables error: %s', existing_tables)
#     logger.debug('model.py check_existing_tables END')
#     return existing_tables

def insert_defaults_login_table(client):
    logger.debug('model.py insert_defaults_login_table BEGIN')
    for i in range(10):
        email = 's3813265' + str(i) + '@student.rmit.edu.au'
        user_name = 'abhis' + str(i)
        pswd = str(i) + str((i + 1) % 10) + str((i + 2) % 10) + str((i + 3) % 10) + str((i + 4) % 10) + str(
            (i + 5) % 10)
        client.put_item(
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
            }
        )
    logger.debug('model.py insert_defaults_login_table END')
    return True


def insert_defaults_music_table(client, s3):
    logger.debug('model.py insert_defaults_music_table BEGIN')
    f = open('a2.json')
    data = json.load(f)
    for item in data['songs']:
        title = item.get('title')
        artist = item.get('artist')
        year = item.get('year')
        web_url = item.get('web_url')
        uid = str(uuid.uuid4().hex)
        img_url = item.get('img_url')
        img_url = download_all_images_from_json_to_bucket(s3, img_url, uid)
        client.put_item(
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
    logger.debug('model.py insert_defaults_music_table END')
    return True


def download_all_images_from_json_to_bucket(client, url, uid):
    logger.debug('model.py download_all_images_from_json_to_bucket BEGIN')
    response = requests.get(url)
    logger.debug('model.py download_all_images_from_json_to_bucket %s', response)
    file = open("temp.jpg", "wb")
    file.write(response.content)
    file.close()
    client.upload_file('temp.jpg', 'abhi-dev-music-images', uid + '.jpg',
                       ExtraArgs={'ACL': 'public-read'})
    os.remove('temp.jpg')
    return 'https://abhi-dev-music-images.s3-ap-southeast-2.amazonaws.com/' + uid + '.jpg'


def assert_s3_bucket(client):
    logger.debug('model.py assert_s3_bucket BEGIN')
    client.create_bucket(
        ACL='public-read',
        Bucket='abhi-dev-music-images1',
        CreateBucketConfiguration={
            'LocationConstraint': 'ap-southeast-2'
        },
        ObjectLockEnabledForBucket=False
    )
    logger.debug('model.py assert_s3_bucket END')
    return True


def assert_dynamo_login_table(client, resource):
    logger.debug('model.py assert_dynamo_login_table BEGIN')
    logger.debug('model.py assert_dynamo_login_table Table does not exist')
    login_table = resource.create_table(
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
    client.get_waiter('table_exists').wait(TableName='login')
    logger.info('model.py assert_dynamo_login_table login table: %s', login_table)
    if login_table is None:
        logger.debug(
            'model.py assert_dynamo_login_table Unexpected failure, login table not created')
    else:
        logger.debug('model.py assert_dynamo_login_table Table login is created')
        insert_defaults_login_table(client)
    logger.debug('model.py assert_dynamo_music_table END')
    return True


def assert_dynamo_music_table(client, resource, s3):
    logger.debug('model.py assert_dynamo_music_table BEGIN')
    logger.debug('model.py assert_dynamo_music_table Table does not exist')
    music_table = resource.create_table(
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
    client.get_waiter('table_exists').wait(TableName='music')
    logger.info('model.py assert_dynamo_music_table music table: %s', music_table)
    if music_table is None:
        logger.debug(
            'model.py assert_dynamo_music_table Unexpected failure, music table not created')
    else:
        logger.debug('model.py assert_dynamo_music_table music table created')
        insert_defaults_music_table(client, s3)
    logger.debug('model.py assert_dynamo_music_table END')
    return True


#
# def assert_dynamo(existing_tables):
#     logger.debug('model.py assert_dynamo START')
#     if 'login' not in existing_tables:
#         if not assert_dynamo_login_table():
#             logger.debug('model.py assert_dynamo Unexpected error, try again END')
#         return False
#     if 'music' not in existing_tables:
#         if not assert_dynamo_music_table():
#             logger.debug('model.py assert_dynamo Unexpected error, try again END')
#             return False
#     if 'login' not in existing_tables:
#         if not assert_s3_bucket():
#             logger.debug('model.py assert_dynamo Unexpected error, try again END')
#             return False
#     logger.debug('model.py assert_dynamo END')
#     return True


def validate_user_return_session(email, pswd):
    login_table = boto3.resource('dynamodb').Table('login')
    logger.debug('model.py validate_user_return_session BEGIN')
    logger.info('model.py validate_user_return_session email, pswd: %s %s', email, pswd)
    response = login_table.get_item(
        Key={
            'email': email,
        }
    )
    logger.info('model.py validate_user_return_session response: %s', response)
    if 'Item' in response and response['Item']['pass'] == pswd:
        logger.debug('model.py validate_user_return_session END')
        return response['Item']['id']
    logger.debug('model.py validate_user_return_session END')
    return None


def validate_user_email(email):
    login_table = boto3.resource('dynamodb').Table('login')
    logger.debug('model.py validate_user_email BEGIN')
    logger.info('model.py validate_user_email email: %s', email)
    response = login_table.get_item(
        Key={
            'email': email,
        }
    )
    logger.info('model.py validate_user_email response: %s', response)
    if 'Item' in response:
        logger.info('model.py validate_user_email response item: %s', response['Item'])
        logger.debug('model.py validate_user_email END')
        return True
    logger.debug('model.py validate_user_email END')
    return False


# def store_session(session_id, session_details):
#     logger.debug('model.py store_session BEGIN')
#     logger.info('model.py store_session session_id, session_details: %s %s', session_id,
#                 session_details)
#     session['session_dict'][session_id] = session_details
#     logger.info('model.py store_session session_dict[session_id]: %s', session['session_dict'][session_id])
#     logger.debug('model.py store_session END')
#     return session_id


# def refresh_session(session_id):
#     logger.debug('model.py refresh_session BEGIN')
#     email = session['session_dict'][session_id].get('email')
#     logger.info('model.py store_session session_id, email: %s %s', session_id, email)
#     response = session['login_table'].get_item(
#         Key={
#             'email': email,
#         }
#     )
#     logger.info('model.py refresh_session response: %s', response)
#     if 'Item' in response:
#         store_session(session_id, response['Item'])
#         logger.debug('model.py refresh_session END')
#         return True
#     logger.debug('model.py refresh_session END')
#     return False


# def remove_session(session_id):
#     logger.debug('model.py remove_session BEGIN')
#     session['session_dict'].pop(session_id, None)
#     logger.debug('model.py remove_session END')
#     return True


def validate_session(session_id):
    logger.debug('model.py validate_session %s', session_id)
    table = boto3.resource('dynamodb').Table('login')
    response = table.scan(
        FilterExpression=Attr("id").eq(session_id)
    )
    logger.info('model.py validate_session %s', response['Items'])
    if response['Items']:
        return True
    return False


def get_user_from_session(session_id):
    logger.debug('model.py get_user_from_session BEGIN')
    table = boto3.resource('dynamodb').Table('login')
    response = table.scan(
        FilterExpression=Attr("id").eq(session_id)
    )
    logger.info('model.py validate_session %s', response['Items'])
    if response['Items']:
        new_dict = response['Items'][0]
        new_dict.pop('pass')
        logger.info('model.py get_user_from_session %s', new_dict)
        logger.debug('model.py get_user_from_session END')
        return new_dict
    return None


def create_new_user(email, username, pswd):
    logger.debug('model.py create_new_user BEGIN')
    table = boto3.resource('dynamodb').Table('login')
    table.put_item(
        Item={
            'user_name': username,
            'email': email,
            'pass': pswd,
            'id': str(uuid.uuid4().hex),
        }
    )
    logger.debug('model.py create_new_user END')
    return True


def query_music_table(title, year, artist):
    logger.debug('model.py query_music_table BEGIN')
    logger.info('model.py query_music_table title, year, artist: %s %s %s', title, year, artist)
    year = year if year is None else int(year)
    table = boto3.resource('dynamodb').Table('music')
    response = table.scan(
        FilterExpression=(Attr('title').ne(title) if title is None else Attr('title').contains(title)) &
                         (Attr('year').ne(year) if year is None else Attr('year').contains(year)) &
                         (Attr('artist').ne(artist) if artist is None else Attr('artist').contains(artist))
    )
    logger.debug('model.py query_music_table END')
    return response['Items']


def session_music_subscribe(session_id, music):
    logger.debug('model.py session_music_subscribe BEGIN')
    user = get_user_from_session(session_id)
    sub_list = user.get('sub_list')
    email = user.get('email')
    logger.debug('model.py session_music_subscribe session, music, email, sub_list: %s %s %s %s',
                 session_id, music, email, sub_list)
    if sub_list is None:
        sub_list = []
    if music in sub_list:
        return True
    sub_list.append(music)
    table = boto3.resource('dynamodb').Table('login')
    response = table.update_item(
        Key={
            'email': email,
        },
        UpdateExpression="set sub_list=:s",
        ExpressionAttributeValues={
            ':s': sub_list,
        },
    )
    logger.info('model.py session_music_subscribe response: %s', response)
    logger.debug('model.py session_music_subscribe END')
    return True


def session_music_unsubscribe(session_id, music):
    logger.debug('model.py session_music_unsubscribe BEGIN')
    user = get_user_from_session(session_id)
    sub_list = user.get('sub_list')
    email = user.get('email')
    logger.debug(
        'model.py session_music_unsubscribe session_id, music, email, sub_list: %s %s %s %s',
        session_id, music, email, sub_list)
    if sub_list is None:
        return False
    if music in sub_list:
        sub_list.remove(music)
    else:
        return True
    table = boto3.resource('dynamodb').Table('login')
    response = table.update_item(
        Key={
            'email': email,
        },
        UpdateExpression="set sub_list=:s",
        ExpressionAttributeValues={
            ':s': sub_list,
        },
    )
    logger.info('model.py session_music_unsubscribe response: %s', response)
    logger.debug('model.py session_music_unsubscribe END')
    return True


# def get_sub_list(session_id):
#     logger.debug('model.py get_sub_list BEGIN')
#     refresh_session(session_id)
#     sub_list = session['session_dict'].get(session_id).get('sub_list')
#     logger.debug('model.py get_sub_list END')
#     return sub_list


def get_music_dict_from_sub_id(uid):
    logger.debug('model.py get_music_dict_from_sub_id BEGIN')
    table = boto3.resource('dynamodb').Table('music')
    response = table.get_item(
        Key={
            'id': uid,
        }
    )
    logger.info('model.py get_music_dict_from_sub_id response.get(Item):%s', response.get('Item'))
    logger.debug('model.py get_music_dict_from_sub_id END')
    return response.get('Item')
