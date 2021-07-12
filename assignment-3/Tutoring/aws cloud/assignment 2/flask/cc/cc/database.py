import json
import os
import uuid
from boto3.dynamodb.conditions import Attr
import boto3
import requests


def check_defaults():
    create_tables()
    return True


def create_s3(s3):
    buckets = []
    for b in s3.list_buckets().get('Buckets'):
        buckets.append(b.get('Name'))
    if 'abdul-a2-image-s3' in buckets:
        return True
    else:
        s3.create_bucket(
            ACL='public-read',
            Bucket='abdul-a2-image-s3',
            CreateBucketConfiguration={
                'LocationConstraint': 'ap-southeast-2'
            },
            ObjectLockEnabledForBucket=False
        )
        return True


def create_tables():
    db = boto3.client('dynamodb')
    dr = boto3.resource('dynamodb')
    s3 = boto3.client('s3')
    create_s3(s3)
    name1 = 'login'
    name2 = 'music'
    name3 = 'records'
    tables = db.list_tables()['TableNames']
    if name1 not in tables:
        dr.create_table(
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
        db.get_waiter('table_exists').wait(TableName='login')

        p = ['012345', '123456', '234567', '345678', '456789', '567890', '678901', '789012', '890123', '901234']
        for i in range(10):
            email = 's3691389' + str(i) + '@student.rmit.edu.au'
            user_name = 'abdul' + str(i)
            pswd = p[i]
            db.put_item(
                TableName='login',
                Item={
                    'username': {
                        'S': user_name,
                    },
                    'email': {
                        'S': email,
                    },
                    'passwd': {
                        'S': pswd,
                    },
                    'slist': {
                        'SS': [''],
                    },
                }
            )
    if name2 not in tables:
        dr.create_table(
            TableName='music',
            KeySchema=[
                {
                    'AttributeName': 'uid',
                    'KeyType': 'HASH'
                },
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'uid',
                    'AttributeType': 'S'
                },
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        db.get_waiter('table_exists').wait(TableName='music')
        file = open('a2.json')
        json_data = json.load(file)
        for j in json_data['songs']:
            t = j.get('title')
            a = j.get('artist')
            y = j.get('year')
            w = j.get('web_url')
            uid = str(uuid.uuid4().hex)
            i = download_images(j.get('img_url'), uid, s3)
            db.put_item(
                TableName='music',
                Item={
                    'uid': {
                        'S': uid,
                    },
                    'title': {
                        'S': t,
                    },
                    'artist': {
                        'S': a,
                    },
                    'year': {
                        'N': y,
                    },
                    'web_url': {
                        'S': w,
                    },
                    'img_url': {
                        'S': i,
                    },
                }
            )

    if name3 not in tables:
        dr.create_table(
            TableName='records',
            KeySchema=[
                {
                    'AttributeName': 'uid',
                    'KeyType': 'HASH'
                },
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'uid',
                    'AttributeType': 'S'
                },
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        db.get_waiter('table_exists').wait(TableName='records')
    return True


def check_login(email, passwd):
    db = boto3.resource('dynamodb')
    r = db.Table('login').get_item(
        Key={
            'email': email,
        }
    )
    if 'Item' in r and r['Item']['passwd'] == passwd:
        return put_record(str(uuid.uuid4().hex), r['Item']['email'], db)
    return None


def download_images(url, uid, s3):
    response = requests.get(url)
    file = open("t.jpg", "wb")
    file.write(response.content)
    file.close()
    s3.upload_file('t.jpg', 'abdul-a2-image-s3', uid + '.jpg', ExtraArgs={'ACL': 'public-read'})
    os.remove('t.jpg')
    return 'https://abdul-a2-image-s3.s3-ap-southeast-2.amazonaws.com/' + uid + '.jpg'


def put_record(uid, email, db):
    r = db.Table('records').put_item(
        Item={
            'uid': uid,
            'email': email,
        }
    )
    return uid


def get_record(uid):
    db = boto3.resource('dynamodb').Table('records')
    r = db.get_item(
        Key={
            'uid': uid,
        }
    )
    if 'Item' in r:
        return r['Item']['email']
    return False


def remove_record(uid):
    db = boto3.resource('dynamodb').Table('records')
    r = db.delete_item(
        Key={
            'uid': uid,
        }
    )
    return True


def get_user_data(uid, email):
    db = boto3.resource('dynamodb')
    if uid is None:
        r = db.Table('login').get_item(
            Key={
                'email': email,
            }
        )
        if 'Item' in r:
            return r['Item']
    else:
        r = db.Table('records').get_item(
            Key={
                'uid': uid,
            }
        )
        if 'Item' in r:
            email = r['Item']['email']
            r = db.Table('login').get_item(
                Key={
                    'email': email,
                }
            )
            if 'Item' in r:
                return r['Item']
    return None


def put_user_data(email, username, password):
    db = boto3.resource('dynamodb')
    r = db.Table('login').put_item(
        Item={
            'username': username,
            'email': email,
            'passwd': password,
            'slist': [''],
        }
    )
    return True


def get_music(uid):
    db = boto3.resource('dynamodb').Table('music')
    r = db.get_item(
        Key={
            'uid': uid,
        }
    )
    if 'Item' in r:
        return r['Item']
    return None


def get_sub_music(subs):
    if subs is None:
        return None
    if not subs:
        print("NONEEE")
        return None
    new = []
    print("SuBS", subs)
    for s in subs:
        if not s or s is None:
            continue
        new.append(get_music(s))
    return new


def query_music(t, y, a):
    db = boto3.resource('dynamodb').Table('music')
    if y is None:
        y = y
    else:
        y = int(y)
    r = db.scan(
        FilterExpression=(Attr('title').eq(t) if t is not None else Attr('title').ne(t)) &
                         (Attr('year').eq(y) if y is not None else Attr('year').ne(y)) &
                         (Attr('artist').eq(a) if a is not None else Attr('artist').ne(a))
    )
    print("r['Items']", r['Items'])
    return r['Items']


def subscribe(r, m):
    a = get_user_data(r, None)
    s = list(a.get('slist'))
    if s is None:
        s = []
    if m in s:
        return
    s.append(m)
    db = boto3.resource('dynamodb').Table('login')
    db.update_item(
        Key={
            'email': a.get('email'),
        },
        UpdateExpression="set slist=:s",
        ExpressionAttributeValues={
            ':s': s,
        },
    )
    return True


def unsubscribe(r, m):
    a = get_user_data(r, None)
    s = list(a.get('slist'))
    if s is None:
        return
    if m in s:
        s.remove(m)
    else:
        return
    db = boto3.resource('dynamodb').Table('login')
    db.update_item(
        Key={
            'email': a.get('email'),
        },
        UpdateExpression="set slist=:s",
        ExpressionAttributeValues={
            ':s': s,
        },
    )
    return True
