import uuid

from flask import Flask, render_template, redirect, url_for, request
import logging
import database
import requests
import json

application = app = Flask(__name__)
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')
app.logger.debug('application.py logging BEGIN')


@app.route('/')
def landing():
    app.logger.debug('application.py landing BEGIN')
    return render_template('index.html')


@app.route('/login/', methods=['get', 'post'], defaults={'msg': None})
@app.route('/login/<string:msg>', methods=['get', 'post'])
def login_page(msg=None):
    app.logger.debug('application.py login_page BEGIN')
    data = {'msg': msg}
    if request.method == 'POST':
        print(request.form['email'], request.form['password'], request.form['entity'])
        if request.form['entity'] == 'b28031811a11':
            if database.check_login_entity(request.form['email'], request.form['password'], 'donor'):
                return redirect(url_for('donor', user_id=database.encrypt(request.form['email'])))
            else:
                data['msg'] = "Login Error"
                return render_template('login.html', data=data)
        if request.form['entity'] == 'a41318003fed':
            if database.check_login_entity(request.form['email'], request.form['password'], 'receiver'):
                return redirect(url_for('receiver', user_id=database.encrypt(request.form['email'])))
            else:
                data['msg'] = "Login Error"
                return render_template('login.html', data=data)
        if request.form['entity'] == 'defe3844e80e':
            if database.check_login_entity(request.form['email'], request.form['password'], 'center'):
                return redirect(url_for('center', user_id=database.encrypt(request.form['email'])))
            else:
                data['msg'] = "Login Error"
                return render_template('login.html', data=data)
        return redirect(url_for('login_page', msg='Error'))
    return render_template('login.html', data=data)


@app.route('/donor/', methods=['get', 'post'], defaults={'user_id': None})
@app.route('/donor/<string:user_id>', methods=['get', 'post'])
def donor(user_id=None):
    app.logger.debug('application.py login_receiver BEGIN')
    if user_id is None:
        return redirect(url_for('login_page', msg='Error try again'))
    email = database.decrypt(user_id)
    if email is None:
        return redirect(url_for('login_page', msg='Error try again'))
    if request.method == 'POST':
        form_data = request.form
        form_data_dict = dict(form_data)
        form_data_dict.pop('submit')
        print(request)
        print("HELLOOOOO")
        print(form_data_dict)
        if request.files.get('img'):
            print('TRUEE')
            # f = open('./tmp')
            f = request.files['img']
            f.save('/tmp/temp.jpg')
            f.close()
            uid = str(uuid.uuid4())
            image = "https://blood-bank-dev-s3.s3.ap-southeast-2.amazonaws.com/" + uid + ".jpg"
            database.image_to_s3(uid)
            form_data_dict['img'] = image
        form_data_dict['blood_request_list'] = []
        database.update_donor_details(form_data_dict, email)

    blood_req_list = database.get_blood_request_list()
    print(blood_req_list)
    print("BLOOD")
    donor_details = database.get_donor_details(email)
    data = {'donor_details': donor_details, 'blood_req_list': blood_req_list, 'weather': database.get_weather()}
    return render_template('donor.html', data=data)


@app.route('/receiver/', methods=['get', 'post'], defaults={'user_id': None})
@app.route('/receiver/<string:user_id>', methods=['get', 'post'])
def receiver(user_id=None):
    data = {}
    app.logger.debug('application.py login_receiver BEGIN')
    if user_id is None:
        return redirect(url_for('login_page', msg='Error try again'))
    email = database.decrypt(user_id)
    if email is None:
        return redirect(url_for('login_page', msg='Error try again'))
    if request.method == 'POST':
        form_data = request.form
        form_data_dict = dict(form_data)
        print(request.form)
        print(form_data_dict)
        if form_data_dict['form_type'] == "user_details":
            if request.files.get('img'):
                # f = open('./tmp')
                f = request.files['img']
                f.save('/tmp/temp.jpg')
                f.close()
                uid = str(uuid.uuid4())
                image = "https://blood-bank-dev-s3.s3.ap-southeast-2.amazonaws.com/" + uid + ".jpg"
                database.image_to_s3(uid)
                form_data_dict['img'] = image
            form_data_dict.pop('submit')
            database.update_receiver_details(form_data_dict, email)
        if form_data_dict['form_type'] == "blood_request":
            try:
                form_data_dict['password'] = "idkbro"
                form_data_dict['receiver_id'] = email
                form_data_dict.pop('form_type')

                print(form_data_dict)
                res = requests.post(
                    "https://3l2j9r52t8.execute-api.ap-southeast-2.amazonaws.com/beta/set-blood-request",
                    data=json.dumps(form_data_dict))
                data['post_request'] = json.loads(res.content)
                print(res.content.decode())
                uid = data['post_request'].get('uid')
                database.update_receiver_blood_request(email, uid)
            except ValueError as e:
                data["post_request"] = "Wrong json format"

    receiver_details = database.get_receiver_details(email)
    data['receiver_details'] = receiver_details
    data['blood_request_list'] = database.get_blood_request_list_for_receiver(email)
    data['blood_request_details'] = ""
    data['weather'] = database.get_weather()
    return render_template('receiver.html', data=data)


@app.route('/center/', methods=['get', 'post'], defaults={'user_id': None})
@app.route('/center/<string:user_id>', methods=['get', 'post'])
def center(user_id=None):
    app.logger.debug('application.py login_center BEGIN')
    data = {'main_user_id': user_id}
    if user_id is None:
        return redirect(url_for('login_page', msg='Error try again center user'))
    email = database.decrypt(user_id)
    if email is None:
        return redirect(url_for('login_page', msg='Error try again center email'))
    if request.method == 'POST':
        form_data = request.form
        form_data_dict = dict(form_data)
        if request.files.get('img'):
            # f = open('./tmp')
            f = request.files['img']
            f.save('/tmp/temp.jpg')
            f.close()
            uid = str(uuid.uuid4())
            image = "https://blood-bank-dev-s3.s3.ap-southeast-2.amazonaws.com/" + uid + ".jpg"
            database.image_to_s3(uid)
            form_data_dict['img'] = image
        form_data_dict.pop('submit')
        form_data_dict['blood_request_list'] = []
        database.update_center_details(form_data_dict, email)
    center_details = database.get_center_details(email)
    data['center_details'] = center_details
    data['blood_request_list'] = database.get_blood_request_list()
    data['donor_list'] = database.get_donor_list()
    data['weather'] = database.get_weather()
    return render_template('center.html', data=data)


@app.route('/blood_request/', defaults={'user_id': None, 'req_id': None, 'center_id': None})
@app.route('/blood_request/<string:center_id>/<string:user_id>/<string:req_id>', methods=['get', 'post'])
def blood_request(req_id=None, user_id=None, center_id=None):
    app.logger.debug('application.py blood_request BEGIN')
    if user_id is None:
        return redirect(url_for('login_page', msg='Error try again User'))
    email = database.decrypt(center_id)
    if email is None:
        return redirect(url_for('login_page', msg='Error try again email'))
    center_uid = database.decrypt(center_id)
    database.blood_request_allocate_to_donor(user_id, req_id, center_uid)
    return redirect(url_for('center', user_id=center_id))


@app.route('/signup/', methods=['get', 'post'], defaults={'msg': None})
@app.route('/signup/<string:msg>', methods=['get', 'post'])
def sign_up(msg=None):
    app.logger.debug('application.py login_page BEGIN')
    data = {'msg': msg}
    if request.method == 'POST':
        if request.form['entity'] == 'b28031811a11':
            if database.sign_up_entity(request.form['email'], request.form['password'], 'donor'):
                return redirect(url_for('login_page', msg='Success Sign up'))
            else:
                data['msg'] = "Email already exists"
                return render_template('signup.html', data=data)
        if request.form['entity'] == 'a41318003fed':
            if database.sign_up_entity(request.form['email'], request.form['password'], 'receiver'):
                return redirect(url_for('login_page', msg='Success Sign up'))
            else:
                data['msg'] = "Email already exists"
                return render_template('signup.html', data=data)
        if request.form['entity'] == 'defe3844e80e':
            if database.sign_up_entity(request.form['email'], request.form['password'], 'center'):
                return redirect(url_for('login_page', msg='Success Sign up'))
            else:
                data['msg'] = "Email already exists"
                return render_template('signup.html', data=data)
        return redirect(url_for('login_page', msg='Sign up Failure'))
    return render_template('signup.html', data=data)


@app.route('/restapi/', methods=['get', 'post'], defaults={'req': None})
@app.route('/restapi/<string:req>', methods=['get', 'post'])
def restapi(req=None):
    app.logger.debug('application.py login_center BEGIN')
    data = {'get_request': ""}
    print("REQQ", req)
    if req is not None:
        res = requests.get("https://3l2j9r52t8.execute-api.ap-southeast-2.amazonaws.com/beta")
        print(res.json())
        data['get_request'] = res.json().get('r')

    if request.method == 'POST':
        data["json_post"] = request.form.get('json_post')
        try:
            json_object = json.loads(request.form.get('json_post').strip().replace('\r', '').replace('\n', ''))
            json_object['password'] = "idkbro"
            res = requests.post("https://3l2j9r52t8.execute-api.ap-southeast-2.amazonaws.com/beta/set-blood-request",
                                data=json.dumps(json_object))
            data["post_request"] = res.content.decode()
        except ValueError as e:
            data["post_request"] = "Wrong json format"

    return render_template('restapi.html', data=data)


@app.route('/stats/')
def stats():
    app.logger.debug('application.py stats BEGIN')
    return render_template('stats.html')


@app.route('/logout/')
def logout():
    app.logger.debug('application.py logout BEGIN')
    return redirect(url_for('login_page'))


# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    app.debug = True
    database.initiate()
    app.run()
