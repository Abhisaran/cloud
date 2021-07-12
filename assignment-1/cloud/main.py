import logging
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, request, jsonify
from google.cloud import storage
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import os

app = Flask(__name__)
app.config["CACHE_TYPE"] = "null"
app.config['JSON_SORT_KEYS'] = False
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

app.logger.debug("Application started, initializing settings")
user_list = {}
post_list = {}
current_user = None

cred_path = 'project1-308701-860664360d63.json'
storage_client = storage.Client.from_service_account_json(cred_path)
bucket_name = "project1-308701.appspot.com"
bucket = storage_client.bucket(bucket_name)

cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred)
db = firestore.client()
users_ref = db.collection(u'users')
posts_ref = db.collection(u'posts')


def pop_user_list():
    app.logger.debug("BEGIN pop_user_list")
    global user_list, users_ref
    docs = users_ref.stream()
    user_list = {}
    for doc in docs:
        user_list[doc.to_dict().get('id')] = doc.to_dict()
    # print("***User list***")
    # print(user_list)
    # print("***User list***")
    app.logger.info("pop_user_list user_list:%s", user_list)
    app.logger.debug("END pop_user_list")
    return user_list


def pop_post_list():
    app.logger.debug("BEGIN pop_post_list")
    global posts_ref, post_list
    posts = posts_ref.stream()
    post_list = {}
    for post in posts:
        post_list[post.id] = post.to_dict()
    app.logger.info("pop_post_list post_list:%s", post_list)
    app.logger.debug("END pop_post_list")
    return


def check_username(username):
    app.logger.debug("BEGIN check_username")
    app.logger.info("check_username username:%s", username)
    global user_list
    for usr in user_list:
        if str(user_list[usr].get('user_name')).lower() == str(username).lower():
            print(str(user_list[usr].get('username')).lower())
            print(str(username).lower())
            app.logger.debug("END check_username TRUE")
            return True
    app.logger.debug("END check_username FALSE")
    return False


def create_user(user_id, username, password, img_url):
    app.logger.debug("BEGIN create_user")
    app.logger.info("create_user user_id, username, password, img_url:%s %s %s %s", user_id, username,
                    password, img_url)
    global users_ref, user_list
    if not (check_username(username) or user_id in user_list):
        data = {u'id': str(user_id), u'user_name': str(username), u'password': str(password),
                u'img_url': str(img_url), 'post_list': []}
        users_ref.add(data)
        app.logger.debug("END create_user TRUE")
        return True
    else:
        app.logger.debug("END create_user FALSE")
        return False


def update_user_password(user_id, oldpass, newpass):
    app.logger.debug("BEGIN update_user_password")
    app.logger.info("update_user_password user_id, oldpass, newpass:%s %s %s", user_id, oldpass, newpass)
    global users_ref, user_list, current_user
    if user_id in user_list and current_user == user_id:
        doc_id = None
        docs = users_ref.stream()
        for doc in docs:
            di = doc.to_dict()
            if user_id == di.get('id'):
                app.logger.debug("END update_user_password user_id found")
                doc_id = doc.id
                if oldpass != di.get('password'):
                    app.logger.debug("END update_user_password old_password FALSE")
                    return False
                break
        if doc_id is None:
            app.logger.debug("END update_user_password doc_id not found FALSE")
            return False
        users_ref.document(doc_id).update({'password': newpass})
        app.logger.debug("END update_user_password TRUE")
        return True
    else:
        app.logger.debug("END update_user_password doc_id not found FALSE")
        return False


def update_user_post(user_id, post_id):
    app.logger.debug("BEGIN update_user_post")
    app.logger.info("update_user_post user_id, post_id:%s %s", user_id, post_id)
    global users_ref, user_list, current_user
    if user_id in user_list and current_user == user_id:
        doc_id = None
        docs = users_ref.stream()
        for doc in docs:
            di = doc.to_dict()
            if user_id == di.get('id'):
                doc_id = doc.id
        if doc_id is None:
            app.logger.debug("END update_user_post doc_id is None FALSE")
            return False
        users_ref.document(doc_id).update({'post_list': firestore.ArrayUnion([post_id])})
        app.logger.debug("END update_user_post TRUE")
        return True
    else:
        app.logger.debug("END update_user_post FALSE")
        return False


def create_post(user_id, subject, message, img_url):
    app.logger.debug("BEGIN create_post")
    global posts_ref, post_list
    post = {u'creator': str(user_id), u'subject': str(subject), u'message': str(message),
            u'img_url': str(img_url), 'time': firestore.SERVER_TIMESTAMP, }
    app.logger.info("create_post post: %s", post)
    doc_ref = posts_ref.add(post)[1].id
    update_user_post(user_id, doc_ref)
    app.logger.debug("END create_post")
    return doc_ref


def update_post(user_id, post_id, subject, message, img_url):
    app.logger.debug("BEGIN update_post")
    pop_post_list()
    global posts_ref, post_list
    post = {u'creator': str(user_id), u'subject': str(subject), u'message': str(message),
            u'img_url': str(img_url), 'time': firestore.SERVER_TIMESTAMP, }
    app.logger.info("update_post post: %s", post)
    if post_id in post_list:
        posts_ref.document(post_id).update(post)
        app.logger.debug("END update_post TRUE")
        return True
    else:
        app.logger.debug("END update_post FALSE")
        return False


def sort_datetime(unordered_dict):
    app.logger.debug("BEGIN sort_datetime")
    ordered_dict = {}
    global user_list
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
        ordered_dict[biggest_key] = unordered_dict[biggest_key]
        ordered_dict[biggest_key][
            'creator_img'] = user_list.get(unordered_dict[biggest_key].get('creator')).get('img_url')
        unordered_dict.pop(biggest_key)
        unordered_dict_keys.remove(biggest_key)
        app.logger.info("sort_datetime ordered_dict %s", ordered_dict)
        app.logger.debug("END sort_datetime")
    return ordered_dict


# def get_user_post_sort_datetime(unordered_dict):
#     ordered_dict = {}
#     counter = 0
#     while len(unordered_dict) > 0:
#         unordered_dict_keys = list(unordered_dict)
#         biggest = 0
#         biggest_key = None
#         for i in range(len(unordered_dict)):
#             if biggest == 0:
#                 biggest_key = unordered_dict_keys[0]
#                 biggest = unordered_dict[biggest_key].get('time')
#                 continue
#             elif unordered_dict[biggest_key].get('time') < unordered_dict[unordered_dict_keys[i]].get(
#                     'time'):
#                 biggest = unordered_dict[unordered_dict_keys[i]].get('time')
#                 biggest_key = unordered_dict_keys[i]
#         unordered_dict[biggest_key]['time'] = datetime.fromtimestamp(
#             unordered_dict[biggest_key].get('time').timestamp())
#         ordered_dict[counter] = unordered_dict[biggest_key]
#         counter += 1
#         unordered_dict.pop(biggest_key)
#         unordered_dict_keys.remove(biggest_key)
#
#     return ordered_dict


@app.route('/login', methods=['GET', 'POST'], defaults={'error': None})
@app.route('/login/<string:error>', methods=['GET', 'POST'])
def login(error):
    app.logger.debug("BEGIN login error:%s", error)
    pop_user_list()
    global current_user
    app.logger.info("login current_user: %s", current_user)
    # print("Current user:" + str(current_user))
    if str(error).__eq__("Please login first"):
        app.logger.info("login error: %s", error)
    # print("ERROR:" + str(error))
    elif type(error) != str:
        error = None
    if current_user is not None:
        app.logger.info("login current_user is logged in: %s", current_user)
        return redirect(url_for('forum'))
    if request.method == 'POST':
        app.logger.info("login POST request: %s", request)
        if request.form['id'] in user_list and user_list.get(request.form['id']).get(
                'password') == request.form['password']:
            current_user = user_list.get(request.form['id']).get('id')
            app.logger.info("login current_user password TRUE setting current_user: %s", current_user)
            return redirect(url_for('forum'))
        else:
            app.logger.debug("login current_user password FALSE:")
            error = 'ID or password is invalid'
    app.logger.debug("END login error: %s", error)
    return render_template('login.html', error=error)


@app.route("/")
def index():
    app.logger.debug("BEGIN index, redirecting to login")
    return redirect((url_for('login')))


@app.route("/forum", methods=['GET', 'POST'])
def forum():
    app.logger.debug("BEGIN forum")
    global current_user
    app.logger.debug("BEGIN forum current_user: %s", current_user)
    error = None
    print("forum user:" + str(current_user))
    if current_user is None:
        app.logger.debug("forum current_user is not logged in, redirecting to login")
        return redirect(url_for('login', error='Please login first'))
    else:
        if request.method == 'POST':
            app.logger.info("forum POST request: %s", request)
            post_subject = request.form['subject']
            post_message = request.form['message']
            post_url = "url"
            app.logger.info(
                "forum create_post current_user, post_subject, post_message, post_url: %s %s %s %s",
                current_user, post_subject, post_message, post_url)
            post_id = create_post(current_user, post_subject, post_message, post_url)
            rel_file_dest = 'img/post_default/'
            file_dest = post_id + '.jpg'
            post_url = 'https://storage.googleapis.com/project1-308701.appspot.com/img/post_default/' + file_dest
            blob = bucket.blob(rel_file_dest + file_dest)
            f = request.files['img']
            f.save('/tmp/post.jpg')
            blob.upload_from_filename('/tmp/post.jpg')
            os.remove('/tmp/post.jpg')
            # f.save('post.jpg')
            # blob.upload_from_filename('post.jpg')
            # os.remove('post.jpg')
            app.logger.info(
                "forum update_post current_user, post_id, post_subject, post_message, post_url: %s %s %s %s",
                current_user, post_id, post_subject, post_message, post_url)
            if update_post(current_user, post_id, post_subject, post_message, post_url):
                app.logger.debug("forum update_post SUCCESS:")
                error = "Success!"
            else:
                app.logger.debug("forum update_post FAILED:")
                error = "Failed, Try again!"

        pop_post_list()
        global user_list, post_list
        user_details = user_list[current_user]
        user_img = user_details.get('img_url')
        context = {'title': 'Forum Page', 'user': current_user, 'user_img': user_img,
                   'error': error}
        app.logger.debug("END forum context: %s", context)
        return render_template("forum.html", context=context)


@app.route("/user", methods=['GET', 'POST'])
def user():
    app.logger.debug("BEGIN user")
    pass_error = None
    global current_user
    if current_user is None:
        app.logger.debug("user current_user is not logged in, redirecting to login")
        return redirect(url_for('login', error='Please login first'))
    else:
        if request.method == 'POST':
            app.logger.info("user POST request: %s", request)
            oldpass = request.form['oldpass']
            newpass = request.form['newpass']
            app.logger.info("user update_user_password current_user, oldpass, newpass: %s %s %s",
                            current_user,
                            oldpass, newpass)
            if update_user_password(current_user, oldpass, newpass):
                current_user = None
                app.logger.debug("user password changed, user logged out")
                app.logger.debug("user current_user is not logged in, redirecting to login")
                return redirect(url_for('login', error='Password Changed, try logging in'))
            else:
                app.logger.debug("user old password incorrect")
                pass_error = "The old password is incorrect! Try again"
    global user_list, post_list
    user_details = user_list[current_user]
    user_img = user_details.get('img_url')
    context = {'title': 'User Page', 'user': current_user, 'pass_error': pass_error, 'user_img': user_img}
    app.logger.debug("END user context: %s", context)
    return render_template("user.html", context=context)


@app.route("/user/update-post", methods=['GET', 'POST'])
def user_post_update():
    app.logger.debug("BEGIN user_post_update")
    global current_user
    error = None
    if current_user is None:
        app.logger.debug("user_post_update current_user is not logged in, redirecting to login")
        return redirect(url_for('login', error='Please login first'))
    else:
        if request.method == 'POST':
            if request.files:
                print("FILES LENGTH PRESENT", request.files)
            else:
                print("FILES LENGTH NOT PRESENT", request.files)
            app.logger.info("user_post_update POST request: %s", request)
            post_subject = request.form['subject']
            post_message = request.form['message']
            post_id = request.form['id']
            rel_file_dest = 'img/post_default/'
            file_dest = post_id + '.jpg'
            post_url = 'https://storage.googleapis.com/project1-308701.appspot.com/img/post_default/' + file_dest
            blob = bucket.blob(rel_file_dest + file_dest)
            f = request.files['img']
            f.save('/tmp/post.jpg')
            blob.upload_from_filename('/tmp/post.jpg')
            os.remove('/tmp/post.jpg')
            # f.save('post.jpg')
            # blob.upload_from_filename('post.jpg')
            # os.remove('post.jpg')
            app.logger.info(
                "user_post_update update_post current_user, post_id, post_subject, post_message, post_url: %s %s %s %s %s",
                current_user, post_id, post_subject, post_message, post_url)
            if update_post(current_user, post_id, post_subject, post_message, post_url):
                app.logger.debug("user_post_update update_post SUCCESS:")
                return redirect(url_for('forum'))
            else:
                app.logger.debug("user_post_update update_post FAILED:")
                error = "Failed, Try again!"
    global user_list, post_list
    user_details = user_list[current_user]
    user_img = user_details.get('img_url')
    context = {'title': 'User Page', 'user': current_user, 'error': error, 'user_img': user_img}
    app.logger.debug("END user_post_update context: %s", context)
    return render_template("user.html", context=context)


@app.route("/register", methods=['GET', 'POST'])
def register():
    app.logger.debug("BEGIN register")
    pop_user_list()
    global current_user
    error = None
    # print("Current user:" + str(current_user))
    if current_user is not None:
        app.logger.debug("register current_user is logged in, redirecting to logout")
        return redirect(url_for('logout'))
    if request.method == 'POST':
        app.logger.info("register POST request: %s", request)
        if request.form['id'] in user_list:
            error = 'The ID already exists'
        elif check_username(request.form['username']):
            error = 'The username already exists'
        else:
            # if request.files['img']
            print(request.files['img'])
            rel_file_dest = 'img/user_default/'
            file_dest = str(request.form['id']) + '.jpg'
            url = 'https://storage.googleapis.com/project1-308701.appspot.com/img/user_default/' + file_dest
            app.logger.info(
                "register create_user request.form['id'], request.form['username'], request.form['password'],url: %s %s %s",
                request.form['id'], request.form['username'], request.form['password'],
                url)
            if create_user(request.form['id'], request.form['username'], request.form['password'],
                           url):
                blob = bucket.blob(rel_file_dest + file_dest)
                f = request.files['img']
                f.save('/tmp/temp.jpg')
                blob.upload_from_filename('/tmp/temp.jpg')
                os.remove('/tmp/temp.jpg')
                # f.save('temp.jpg')
                # blob.upload_from_filename('temp.jpg')
                # os.remove('temp.jpg')
                app.logger.debug("END register User created")
                return redirect(url_for('login', error='User created, try logging in'))
            else:
                error = "please try again"
    app.logger.debug("END register User not created error: %s", error)
    return render_template("register.html", error=error)


@app.route("/logout")
def logout():
    app.logger.debug("BEGIN logout")
    global current_user
    current_user = None
    app.logger.debug("END logout")
    return redirect((url_for('login')))


@app.route("/forum/all-posts")
def all_posts():
    app.logger.debug("BEGIN all_posts")
    pop_post_list()
    global post_list
    app.logger.debug("BEGIN all_posts")
    return jsonify(sort_datetime(post_list))


@app.route("/forum/user-posts")
def user_posts():
    app.logger.debug("BEGIN user_posts")
    pop_post_list()
    pop_user_list()
    global post_list, current_user, user_list
    user_post = user_list[current_user].get('post_list')
    new_dict = {}
    for i in user_post:
        new_dict[i] = post_list[i]
    app.logger.info("END user_posts new_dict: %s", new_dict)
    app.logger.debug("END user_posts")
    return jsonify(sort_datetime(new_dict))


if __name__ == "__main__":
    app.logger.debug("BEGIN FLASK APPLICATION")
    app.run(debug=True)
    app.logger.debug("END FLASK APPLICATION")
    # app.run(host='127.0.0.1', port=8080, debug=True)
