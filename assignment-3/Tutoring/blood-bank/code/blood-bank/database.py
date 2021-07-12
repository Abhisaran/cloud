import boto3
import logging

import requests
from cryptography.fernet import Fernet
from geopy.geocoders import Nominatim
from datetime import datetime

logger = logging.getLogger(__name__)
logging.basicConfig(filename='tmp2.log', filemode='a', level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')


def get_boto3_s3():
    return boto3.resource('s3', region_name='ap-southeast-2'), boto3.client('s3', region_name='ap-southeast-2')


def get_boto3_dynamodb():
    return boto3.resource('dynamodb', region_name='ap-southeast-2'), boto3.client('dynamodb',
                                                                                  region_name='ap-southeast-2')


def get_boto3_rds():
    return boto3.resource('rds', region_name='ap-southeast-2'), boto3.client('rds', region_name='ap-southeast-2')


def check_s3(resource=None, client=None):
    logger.info('database.py check_s3 BEGIN')
    if client is None or resource is None:
        resource, client = get_boto3_s3()
    print(client.list_buckets().get('Buckets'))
    s3_list = []
    for s in client.list_buckets().get('Buckets'):
        s3_list.append(s.get('Name'))
    if 'blood-bank-dev-s3' in s3_list:
        logger.info('database.py check_s3 blood-bank-dev-s3 already exists')
        return True
    client.create_bucket(
        Bucket='blood-bank-dev-s3',
        CreateBucketConfiguration={
            'LocationConstraint': 'ap-southeast-2'
        },
        ACL='public-read',
        ObjectLockEnabledForBucket=False
    )
    client.get_waiter('bucket_exists').wait(Bucket='blood-bank-dev-s3')
    logger.info('database.py check_s3 blood-bank-dev-s3 created END')
    return True


def check_dynamodb(resource=None, client=None):
    logger.info('database.py check_dynamodb BEGIN')
    if client is None or resource is None:
        resource, client = get_boto3_dynamodb()
    table_list = client.list_tables()['TableNames']
    if 'users' in table_list:
        logger.info('database.py check_dynamodb users table already exists')
    else:
        table = resource.create_table(
            TableName='users',
            KeySchema=[
                {
                    'AttributeName': 'username',
                    'KeyType': 'HASH'
                },
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'username',
                    'AttributeType': 'S'
                },
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        table.meta.client.get_waiter('table_exists').wait(TableName='users')

    if 'user-donor' in table_list:
        logger.info('database.py check_dynamodb donor table already exists')
    else:
        table = resource.create_table(
            TableName='user-donor',
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
        table.meta.client.get_waiter('table_exists').wait(TableName='user-donor')

    if 'user-receiver' in table_list:
        logger.info('database.py check_dynamodb receiver table already exists')
    else:
        table = resource.create_table(
            TableName='user-receiver',
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
        table.meta.client.get_waiter('table_exists').wait(TableName='user-receiver')

    if 'user-center' in table_list:
        logger.info('database.py check_dynamodb center table already exists')
    else:
        table = resource.create_table(
            TableName='user-center',
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
        table.meta.client.get_waiter('table_exists').wait(TableName='user-center')
    # Wait until the table exists.

    if 'blood-requests' in table_list:
        logger.info('database.py check_dynamodb blood requests table already exists')
    else:
        table = resource.create_table(
            TableName='blood-requests',
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
        table.meta.client.get_waiter('table_exists').wait(TableName='blood-requests')
    return True


def check_rds(resource=None, client=None):
    logger.info('database.py check_rds BEGIN')
    if client is None or resource is None:
        resource, client = get_boto3_rds()

    response = client.create_db_instance(
        AllocatedStorage=5,
        DBInstanceClass='db.t2.micro',
        DBInstanceIdentifier='mymysqlinstance',
        Engine='MySQL',
        MasterUserPassword='MyPassword',
        MasterUsername='MyUser',
    )
    client.get_waiter('db_instance_available').wait(DBInstanceIdentifier='mymysqlinstance')
    return True


def check_login_entity(email, password, entity):
    resource, client = get_boto3_dynamodb()
    print(entity)
    table = resource.Table('user-' + entity)
    response = table.get_item(
        Key={
            'email': email
        }
    )
    print(response)
    logger.info('database.py check_login_entity %s', response)
    if 'Item' in response and response['Item']['password'] == password:
        return True
    return False


def sign_up_entity(email, password, entity):
    logger.info('database.py sign_up_entity BEGIN')
    resource, client = get_boto3_dynamodb()
    table = resource.Table('user-' + entity)
    response = client.get_item(
        TableName='user-' + entity,
        Key={
            'email': {
                'S': email}
        }
    )

    if 'Item' in response:
        return False

    response = table.put_item(
        Item={
            'email': email,
            'password': password
        }
    )
    logger.info('database.py sign_up_entity %s', response)
    logger.info('database.py sign_up_entity END')
    return True


def get_donor_details(email):
    logger.info('database.py get_donor_details BEGIN')
    resource, client = get_boto3_dynamodb()
    table = resource.Table('user-donor')
    response = table.get_item(
        Key={
            'email': email
        }
    )
    item1 = response.get('Item')
    item1.pop('password')

    print(item1)
    logger.info('database.py get_donor_details END')
    return item1


def update_donor_details(form_data_dict, email):
    logger.info('database.py update_donor_details BEGIN')
    resource, client = get_boto3_dynamodb()
    table = resource.Table('user-donor')

    response = table.get_item(
        Key={
            'email': email
        }
    )
    item1 = response.get('Item')
    item2 = form_data_dict
    item1.update(item2)
    response = table.put_item(Item=item1)
    logger.info('database.py update_donor_details %s', response)
    logger.info('database.py update_donor_details END')
    return True


def get_donor_list():
    logger.info('database.py get_donor_list BEGIN')
    resource, client = get_boto3_dynamodb()
    table = resource.Table('user-donor')
    res = table.scan()
    print(res.get('Items'))

    logger.info('database.py get_donor_list END')
    return res.get('Items')


def get_blood_request_list():
    logger.info('database.py get_donor_blood_request_list BEGIN')
    resource, client = get_boto3_dynamodb()
    table = resource.Table('blood-requests')
    res = table.scan()
    print(res.get('Items'))

    logger.info('database.py get_donor_blood_request_list END')
    return res.get('Items')


def get_receiver_details(email):
    logger.info('database.py get_receiver_details BEGIN')
    resource, client = get_boto3_dynamodb()
    table = resource.Table('user-receiver')
    response = table.get_item(
        Key={
            'email': email
        }
    )
    item1 = response.get('Item')
    item1.pop('password')

    print(item1)
    logger.info('database.py get_receiver_details END')
    return item1


def update_receiver_details(form_data_dict, email):
    logger.info('database.py update_receiver_details BEGIN')
    resource, client = get_boto3_dynamodb()
    table = resource.Table('user-receiver')

    response = table.get_item(
        Key={
            'email': email
        }
    )
    item1 = response.get('Item')
    item2 = form_data_dict
    item1.update(item2)
    response = table.put_item(Item=item1)
    logger.info('database.py update_receiver_details %s', response)
    logger.info('database.py update_receiver_details END')
    return True


def update_receiver_blood_request(email, uid):
    logger.info('database.py update_receiver_blood_request BEGIN')
    resource, client = get_boto3_dynamodb()
    table = resource.Table('user-receiver')

    response = table.get_item(
        Key={
            'email': email
        }
    )
    item = response.get('Item')
    if 'blood_request_list' in item:
        blood_req_list = list(item.get('blood_request_list'))
    else:
        blood_req_list = []
    blood_req_list.append(uid)
    item['blood_request_list'] = blood_req_list
    response = table.put_item(Item=item)
    logger.info('database.py update_receiver_blood_request %s', response)
    logger.info('database.py update_receiver_blood_request END')
    return True


def get_blood_request_list_for_receiver(email):
    logger.info('database.py get_blood_request_list_for_receiver BEGIN')
    resource, client = get_boto3_dynamodb()
    table = resource.Table('user-receiver')
    response = table.get_item(
        Key={
            'email': email
        }
    )
    item = response.get('Item')
    if 'blood_request_list' in item:
        blood_req_list = list(item.get('blood_request_list'))
    else:
        return []
    blood_req_list_list = []
    for i in blood_req_list:
        blood_req_list_list.append(get_blood_request_from_uid(i))
    logger.info('database.py get_blood_request_list_for_receiver %s', blood_req_list_list)
    logger.info('database.py get_blood_request_list_for_receiver END')
    return blood_req_list_list


def get_blood_request_from_uid(uid):
    logger.info('database.py get_blood_request_from_uid BEGIN')
    resource, client = get_boto3_dynamodb()
    table = resource.Table('blood-requests')

    response = table.get_item(
        Key={
            'uid': uid
        }
    )
    item = response.get('Item')
    logger.info('database.py get_blood_request_from_uid %s', response)
    logger.info('database.py get_blood_request_from_uid END')
    return item


def get_center_details(email):
    logger.info('database.py get_center_details BEGIN')
    resource, client = get_boto3_dynamodb()
    table = resource.Table('user-center')
    response = table.get_item(
        Key={
            'email': email
        }
    )
    item1 = response.get('Item')
    item1.pop('password')

    print(item1)
    logger.info('database.py get_center_details END')
    return item1


def update_center_details(form_data_dict, email):
    logger.info('database.py update_receiver_details BEGIN')
    resource, client = get_boto3_dynamodb()
    table = resource.Table('user-center')

    response = table.get_item(
        Key={
            'email': email
        }
    )
    item1 = response.get('Item')
    item2 = form_data_dict
    item1.update(item2)
    response = table.put_item(Item=item1)
    logger.info('database.py update_center_details %s', response)
    logger.info('database.py update_center_details END')
    return True


def blood_request_allocate_to_donor(email, req_id, center_id):
    logger.info('database.py blood_request_allocate_to_donor BEGIN')
    resource, client = get_boto3_dynamodb()
    table = resource.Table('user-donor')

    response = table.get_item(
        Key={
            'email': email
        }
    )
    print(email, req_id, center_id)
    user = response.get('Item')
    print(response)
    if 'blood_request_list' in user:
        blood_req_list = list(user.get('blood_request_list'))
    else:
        blood_req_list = []
    blood_req_list.append(req_id)
    user['blood_request_list'] = blood_req_list
    response = table.put_item(Item=user)

    table = resource.Table('blood-requests')

    response = table.get_item(
        Key={
            'uid': req_id
        }
    )
    blood_req = response.get('Item')
    blood_req['allocated'] = True
    blood_req['allocated_user_id'] = email
    blood_req['allocated_center_id'] = center_id
    response = table.put_item(Item=blood_req)
    logger.info('database.py blood_request_allocate_to_donor %s', response)
    logger.info('database.py blood_request_allocate_to_donor END')
    return True


def initiate():
    logger.info('database.py initiate BEGIN')
    check_s3()
    check_dynamodb()
    # check_rds()
    logger.info('database.py initiate END')
    return True


def encrypt(message):
    try:
        if type(message) is str:
            message = message.encode()
        key = b'lggCcPdSdMHqH6c7P8C88B9KpysMoo5_zCjUTxhqPyA='
        return Fernet(key).encrypt(message).decode()
    except:
        return None


def decrypt(token):
    try:
        if type(token) is str:
            token = token.encode()
        key = b'lggCcPdSdMHqH6c7P8C88B9KpysMoo5_zCjUTxhqPyA='
        return Fernet(key).decrypt(token).decode()
    except:
        return None


def get_weather():
    date_time = datetime.now()
    time = date_time.strftime("%H:%M:%S")
    date = date_time.strftime("%Y-%m-%d")
    place = "Melbourne"
    geolocator = Nominatim(user_agent="forecast")
    location = geolocator.geocode(place)
    latitude = round(location.latitude, 2)
    longitude = round(location.longitude, 2)
    api_endpoint = f"https://api.weather.com/v2/turbo/vt1dailyForecast?apiKey=d522aa97197fd864d36b418f39ebb323&format=json&geocode={latitude}%2C{longitude}&language=en-IN&units=m"
    response = requests.get(api_endpoint)
    response_data = response.json()
    # print(response_data)
    # print(weather.get('day').get('temperature'))

    try:
        # data wise data
        dates_time_list = response_data["vt1dailyForecast"]["validDate"]
        dates_list = [_.split("T0")[0] for _ in dates_time_list]
        # today's date index
        date_index = dates_list.index(date)
    except Exception as e:
        print("Please check the date format. [Y-m-d]")

    try:
        # day
        temperature_day = response_data["vt1dailyForecast"][
            "day"]["temperature"][date_index]
        precipitate_day = response_data["vt1dailyForecast"][
            "day"]["precipPct"][date_index]
        uv_description_day = response_data["vt1dailyForecast"][
            "day"]["uvDescription"][date_index]
        wind_speed_day = response_data["vt1dailyForecast"][
            "day"]["windSpeed"][date_index]
        humidity_day = response_data["vt1dailyForecast"][
            "day"]["humidityPct"][date_index]
        phrases_day = response_data["vt1dailyForecast"][
            "day"]["phrase"][date_index]
        narrative_day = response_data["vt1dailyForecast"][
            "day"]["narrative"][date_index]

        forecast_output = {"place": place, "time": time, "date": date, "day": {"temperature": temperature_day,
                                                                               "precipitate": precipitate_day,
                                                                               "uv_description": uv_description_day,
                                                                               "wind_speed": wind_speed_day,
                                                                               "humidity": humidity_day,
                                                                               "phrases": phrases_day,
                                                                               "narrative": narrative_day
                                                                               }, }

    except Exception as e:
        return "Exception while fetching data"

    return forecast_output


def image_to_s3(uid, resource=None, client=None):
    resource, client = get_boto3_s3()
    client.upload_file('./tmp/temp.jpg', 'blood-bank-dev-s3', uid + '.jpg',
                       ExtraArgs={'ACL': 'public-read'})
    return True