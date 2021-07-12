import os

from google.cloud import storage
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime

#
# class User:
#

storage_client = storage.Client.from_service_account_json(
    'project1-308701-860664360d63.json')

# Make an authenticated API request
buckets = list(storage_client.list_buckets())
# print(buckets)
bucket_name = "project1-308701.appspot.com"
# bucket_name = "project1-308701.appspot.com/img/user_default"
bucket = storage_client.bucket(bucket_name)
print(bucket)
blob = bucket.blob("img/user_default/abhisaran.jpg")
# blob.upload_from_filename("C:/Users/abhis/Downloads/8.jpg")
# Use the application default credentials
# cred = credentials.ApplicationDefault()
# firebase_admin.initialize_app(cred, {
#     'projectId': project_id,
# })

# db = firestore.client()
cred = credentials.Certificate('project1-308701-860664360d63.json')
firebase_admin.initialize_app(cred)

db = firestore.client()

print(db)

users_ref = db.collection(u'users')
print(users_ref)
docs = users_ref.stream()

posts_ref = db.collection(u'posts')
print(posts_ref)
posts = posts_ref.stream()

post = {u'creator': str("ADMIN"), u'subject': str("subject"),
        u'message': str("message"),
        u'img_url': str("img_url"), 'time': firestore.SERVER_TIMESTAMP}
new_doc_ref = posts_ref.document()
print("HELLO")
# doc_ref = posts_ref.add(post)[1]

user_l = {}
for doc in docs:
    print(doc.id)
    di = doc.to_dict()
    # if di.get('id') == 'a':
    #     print('Yes')
    #     users_ref.document(doc.id).update({'password':'gommala'})
    #     users_ref.document(doc.id).update({'post_list': firestore.ArrayUnion(['post_id'])})
    # print(f'{doc.id} => {doc.to_dict()}')
    # user_l[doc.id] = doc.to_dict()
    user_l[di.get('id')] = doc.to_dict()
    # print(di.get('id'))

print(user_l)
# print(sorted(user_l, key=lambda ))
post_list = {}

for post in posts:
    print(post.to_dict())
    post_list[post.id] = post.to_dict()
    # print("Hello", datetime.fromtimestamp(post.get('time').timestamp()))

print(post_list)
print('DONE')
print(post_list.items())
# print("Sorted", sorted(post_list.items(), key=post_list.get().get('time')))
print("**************")
unordered_dict = {}
unordered_dict.update(post_list)
print(list(unordered_dict))
print("WE ARE HERE")
# while len(temp_post_list) > 0:
#     temp_post_list_keys = list(temp_post_list)
#     smallest = 0
#     smallest_key = None
#     for i in range(len(temp_post_list)):
#         if smallest == 0:
#             smallest_key = temp_post_list_keys[0]
#             smallest = temp_post_list[smallest_key].get('time')
#             continue
#         elif temp_post_list[smallest_key].get('time') > temp_post_list[temp_post_list_keys[i]].get('time'):
#             smallest = temp_post_list[temp_post_list_keys[i]].get('time')
#             smallest_key = temp_post_list_keys[i]
#     print(smallest)
#     temp_post_list.pop(smallest_key)
#     temp_post_list_keys.remove(smallest_key)

ordered_dict = {}
counter = 0
while len(unordered_dict) > 0:
    unordered_dict_keys = list(unordered_dict)
    biggest = 0
    biggest_key = None
    for i in range(len(unordered_dict)):
        if biggest == 0:
            biggest_key = unordered_dict_keys[0]
            biggest = unordered_dict[biggest_key].get('time')
            continue
        elif unordered_dict[biggest_key].get('time') < unordered_dict[unordered_dict_keys[i]].get(
                'time'):
            biggest = unordered_dict[unordered_dict_keys[i]].get('time')
            biggest_key = unordered_dict_keys[i]
    unordered_dict[biggest_key]['time'] = datetime.fromtimestamp(
        unordered_dict[biggest_key].get('time').timestamp())

    ordered_dict[counter] = unordered_dict[biggest_key]
    counter += 1
    # datetime.fromtimestamp(post.get('time').timestamp())
    unordered_dict.pop(biggest_key)
    unordered_dict_keys.remove(biggest_key)

print(ordered_dict)
print("*****")

# for i in range(len(post_list)):
#     smallest = 0
#     smallest_key = None
#     for

# print(sorted(post_list, key=lambda x: for a in post_list))
# for i in range(10):
#
# post = {'time': firestore.SERVER_TIMESTAMP, u'creator': str("anaconda12"), u'subject': str("subject"),
#         u'message': str("message"),
#         u'img_url': str("img_url")}
# new_doc_ref = posts_ref.document()
# # doc_ref.set(post)
# # print(doc_ref.id)
# posts_ref.add(post)

# print(user_l)
#
# print(user_l.get('s381326505').get('password'))


# for i in range(10):
#     data = {u'id': u's3813265'+str(i), u'user_name': {u'last_name': u's'+str(i), u'first_name': u'abhi'},
#             u'password': u'123456'+str(i)}
#     users_ref.document(u'user'+str(i)).set(data)


# for i in range(10):
#     data = {u'id': u's3813265' + str(i), u'user_name': u'abhis' + str(i),
#             u'password': u'123456' + str(i),
#             u'img_url': u'https://storage.googleapis.com/project1-308701.appspot.com/img/user_default/' + str(
#                 i) + '.jpg',
#             'post_list': []}
#     users_ref.document(u'user' + str(i)).set(data)

# data = {u'id': u's381326512', u'user_name': u'abhis',
#         u'password': u'123456', u'img_url':u'https://storage.googleapis.com/project1-308701.appspot.com/img/user_default/0.jpg'}
# users_ref.add(data)
