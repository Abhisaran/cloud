from flask import Flask, render_template, redirect, url_for, request
import database
import logging

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')
app.logger.debug('app.py logging BEGIN')


@app.route('/', defaults={'e': None})
@app.route('/', methods=['GET', 'POST'], defaults={'e': None})
@app.route('/<string:e>', methods=['GET', 'POST'])
def index(e):
    app.logger.debug('app.py index')
    app.logger.debug('app.py login BEGIN')
    app.logger.info('app.py login error: %s', e)
    data = {'e': e}
    if request.method == 'POST':
        app.logger.info("login POST request: %s", request)
        app.logger.info("login POST request: %s %s", request.form['email'], request.form['password'])
        record = database.check_login(request.form['email'], request.form['password'])
        if record is not None:
            return redirect(url_for('main', record=record))
        else:
            e = "Email or password is invalid"
            data = {'e': e}
    app.logger.debug('app.py login END')
    return render_template('index.html', data=data)


@app.route('/main/', methods=['GET', 'POST'], defaults={'record': None})
@app.route('/main/<string:record>', methods=['GET', 'POST'])
def main(record):
    e = None
    q_data = None
    if record is None:
        return redirect(url_for('index'))
    if request.method == 'POST':
        app.logger.info("main POST request: %s", request)
        if request.form['title']:
            t = request.form['title']
        else:
            t = None
        if request.form['year']:
            y = request.form['year']
        else:
            y = None
        if request.form['artist']:
            a = request.form['artist']
        else:
            a = None
        q_data = database.query_music(t, y, a)

    user_data = database.get_user_data(record, None)
    sub = []
    if user_data is not None:
        sub = database.get_sub_music(user_data.get('slist'))
    data = {'e': e, 'user_data': user_data, 'uid': record, 'q_data': q_data, 'sub': sub}
    return render_template('main.html', data=data)


@app.route('/reg/', methods=['GET', 'POST'])
def reg():
    e = None
    if request.method == 'POST':
        app.logger.info("login POST request: %s", request)
        app.logger.info("login POST request: %s %s", request.form['email'], request.form['password'])
        user_data = database.get_user_data(None, request.form['email'])
        if user_data:
            e = 'Email already exists'
        else:
            if database.put_user_data(request.form['email'], request.form['username'], request.form['password']):
                return redirect(url_for('index'))
    data = {'e': e}
    return render_template('reg.html', data=data)


@app.route('/logout/', methods=['GET', 'POST'], defaults={'record': None})
@app.route('/logout/<string:record>', methods=['GET', 'POST'])
def logout(record):
    e = None
    if record is None:
        return redirect(url_for('index'))
    database.remove_record(record)
    return redirect(url_for('index'))


@app.route('/sub/<string:record>/<string:s>')
def subscribe(record, s):
    e = None
    print("Record, string", record, s)
    if record is None:
        print("RECORD IS NONE***")
        return redirect(url_for('index'))
    database.subscribe(record, s)
    return redirect(url_for('main', record=record))


@app.route('/unsub/<string:record>/<string:s>')
def unsubscribe(record, s):
    e = None
    print("Record, string", record, s)
    if record is None:
        print("RECORD IS NONE***")
        return redirect(url_for('index'))
    database.unsubscribe(record, s)
    return redirect(url_for('main', record=record))


if __name__ == '__main__':
    database.check_defaults()
    app.run()

if __name__ != '__main__':
    database.check_defaults()
