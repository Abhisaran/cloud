import boto3
import uuid


def init_boto3():
    return 0


def check_dynamo():
    dynamodb = boto3.resource('dynamodb')
    login_table = dynamodb.Table('login')
    print("Table status:", login_table.table_status)
    # movie_resp = put_movie("The Big New Movie", 2015,
    #                        "Nothing happens at all.", 0)
    # print("Put movie succeeded:")
    # pprint(movie_resp, sort_dicts=False)
    response = login_table.get_item(
        Key={
            'user_name': 'abhis0'
        }
    )
    print(response)
    item = response['Item']
    print(item)
    return login_table.table_status