import os
import uuid

import boto3
import pprint

import requests
from boto3.dynamodb.conditions import Key, Attr

# def put_movie(title, year, plot, rating, dynamodb=None):
#     if not dynamodb:
dynamodb = boto3.resource('dynamodb')
#
table = dynamodb.Table('login')

#     response = table.put_item(
#         Item={
#             'year': year,
#             'title': title,
#             'info': {
#                 'plot': plot,
#                 'rating': rating
#             }
#         }
#     )
#     return response
#
#
# def create_movie_table(dynamodb=None):
#     if not dynamodb:
#         dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")
#
#     table = dynamodb.create_table(
#         TableName='Movies',
#         KeySchema=[
#             {
#                 'AttributeName': 'year',
#                 'KeyType': 'HASH'  # Partition key
#             },
#             {
#                 'AttributeName': 'title',
#                 'KeyType': 'RANGE'  # Sort key
#             }
#         ],
#         AttributeDefinitions=[
#             {
#                 'AttributeName': 'year',
#                 'AttributeType': 'N'
#             },
#             {
#                 'AttributeName': 'title',
#                 'AttributeType': 'S'
#             },
#
#         ],
#         ProvisionedThroughput={
#             'ReadCapacityUnits': 10,
#             'WriteCapacityUnits': 10
#         }
#     )
#     return table
#
#
# if __name__ == '__main__':
#     # movie_table = create_movie_table()
#     dynamodb = boto3.resource('dynamodb')
#     login_table = dynamodb.Table('login')
#     print("Table status:", login_table.table_status)
#     # movie_resp = put_movie("The Big New Movie", 2015,
#     #                        "Nothing happens at all.", 0)
#     # print("Put movie succeeded:")
#     # pprint(movie_resp, sort_dicts=False)
#     response = login_table.get_item(
#         Key={
#             'user_name': 'abhis0'
#         }
#     )
#     print(response)
#     item = response['Item']
#     print(item)


# import json
#
# f = open('a2.json')
#
# data = json.load(f)
#
# print(data)
# for i in data['songs']:
#     print(type(i))
#     print(i.get("title"))

# print("here")
# response = table.get_item(
#     Key={
#         'id': 'abhis0',
#         'email': 'a'
#     }
# )
# print(response)

# response = table.query(
#     KeyConditionExpression=Key('email').eq('s38132650@student.rmit.edu.au')
# )
# items = response['Items'][0]
# print(items)
# print(items.pop('pass'))
# # items['pass'] = None
# print(items.pop('pass', None))
# print(items)
#
# title = None
# year = None
# artist = None
music_table = dynamodb.Table('music')
# response = music_table.scan(
#     FilterExpression=(Attr('title').ne(title) if title is None else Attr('title').eq(title)) & (
#         Attr('year').ne(year) if year is None else Attr('year').eq(year)) & (
#                          Attr('artist').ne(artist) if artist is None else Attr('artist').eq(artist))
# )
#
# print(response)
# print(response['Items'])
# print(type(response['Items']))
# print(type(response['Items'][0]))
# for i in response['Items']:
#     print(i)

# print(uuid.uuid1().hex)
# x = []
# for i in range(100000):
#     a = str(uuid.uuid4().hex)
#     if a in x:
#         print("True")
#     else:
#         print("No")
#         x.append(a)
# title = 'Hello'
# year = None
# artist = None
# year = year if year is None else int(year)
# response = music_table.scan(
#     FilterExpression=(Attr('title').ne(title) if title is None else Attr('title').eq(title)) &
#                      (Attr('year').ne(year) if year is None else Attr('year').eq(year)) &
#                      (Attr('artist').ne(artist) if artist is None else Attr('artist').eq(artist))
# )
# print(response['Items'])
#
# if not response['Items']:
#     print("NONE")

# response = table.put_item(
#     Item={
#         'email': '1@1',
#         'pass': '1',
#         'id': 'what'
#     }
# )

# response = table.update_item(
#     Key={
#         'email': '1@1',
#     },
#     UpdateExpression="set user_name=:p, id=:i",
#     ExpressionAttributeValues={
#         ':p': 'abhis0',
#         ':i': '3',
#     },
# )
# print(response)


s3 = boto3.resource('s3')
client = boto3.client('s3')


# listt = []
# listtt = client.list_buckets().get('Buckets')
# for x in listtt:
#     listt.append(x.get('Name'))
#
# print(listt)
# if 'abhi-dev-music-images' in listt:
#     print('True')
# print(listt[0].get('Name'))

# response = client.create_bucket(
#     ACL='public-read',
#     Bucket='abhi-dev-music-images',
#     CreateBucketConfiguration={
#         'LocationConstraint': 'ap-southeast-2'
#     },
#     ObjectLockEnabledForBucket=False
# )

# s3.meta.client.upload_file('hello.txt', 'abhi-dev-music-images', 'hello.txt')
# print(response)

# def download_all_images_from_json_to_bucket(url, uid):
#     response = requests.get(url)
#     file = open("temp.jpg", "wb")
#     file.write(response.content)
#     file.close()
#     os.remove('temp.jpg')
#     client.upload_file('temp.jpg', 'abhi-dev-music-images', uid + '.jpg', ExtraArgs={'ACL': 'public-read'})
#     return 'True'


# print(
#     download_all_images_from_json_to_bucket('http://www.songnotes.cc/images/artists/TheTallestManOnEarth.jpg',
#                                             '123456'))


uid = '02aaf440830147a8a0c5b3186c2273bc'
response = music_table.get_item(
    Key={
        'id': uid,
    }
)
print(response)
dict_music = {}
dict_music['title'] = response.get('Item').get('title')
dict_music['artist'] = response.get('Item').get('artist')
dict_music['year'] = response.get('Item').get('year')
dict_music['img_url'] = response.get('Item').get('img_url')
dict_music['web_url'] = response.get('Item').get('web_url')
print(dict_music)
print(response.get('Item'))