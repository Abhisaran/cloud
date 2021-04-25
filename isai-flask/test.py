import boto3
import pprint

# def put_movie(title, year, plot, rating, dynamodb=None):
#     if not dynamodb:
#         dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")
#
#     table = dynamodb.Table('Movies')
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


import json

f = open('a2.json')

data = json.load(f)

print(data)
for i in data['songs']:
    print(type(i))
    print(i.get("title"))