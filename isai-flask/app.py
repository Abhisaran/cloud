from flask import Flask, render_template, redirect, url_for, request, jsonify
import model
import logging

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')
app.logger.debug('app.py logging BEGIN')

if __name__ != '__main__':
    app.logger.debug('app.py !__main__ BEGIN')
    gunicorn_error_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers.extend(gunicorn_error_logger.handlers)
    app.logger.setLevel(logging.DEBUG)


def settings():
    app.logger.debug('app.py settings')
    return model.init_boto3()


@app.errorhandler(404)
def page_not_found(e):
    app.logger.debug('app.py page_not_found')
    return redirect(url_for('login'))


@app.route('/')
def index():
    app.logger.debug('app.py index')
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'], defaults={'error': None})
@app.route('/login/<string:error>', methods=['GET', 'POST'])
def login(error):
    app.logger.debug('app.py login BEGIN')
    app.logger.info('app.py login error: %s', error)
    context = {'error': error}
    if request.method == 'POST':
        app.logger.info("login POST request: %s", request)
        app.logger.info("login POST request: %s %s", request.form['email'], request.form['password'])
        login_validation = model.validate_user_return_session(request.form['email'], request.form['password'])
        app.logger.info('app.py login validation: %s', login_validation)
        if login_validation:
            return redirect(url_for('main', session=login_validation))
        else:
            error = "Email or password is invalid"
            context = {'error': error}
    app.logger.info('app.py login context: %s', context)
    app.logger.debug('app.py login END')
    return render_template('login.html', context=context)


@app.route('/main', methods=['GET', 'POST'], defaults={'session': None, })
@app.route('/main/<string:session>', methods=['GET', 'POST'])
# @app.route('/main/<string:session>/<string:>', methods=['GET', 'POST'])
def main(session):
    app.logger.debug('app.py main BEGIN %s', session)
    if session is None:
        app.logger.debug('app.py main END')
        return redirect(url_for('login', error='Please login first'))
    if not model.validate_session(session):
        app.logger.debug('app.py main END')
        return redirect(
            url_for('login', error='Unauthenticated access detected, this user has been reported'))
    new_music = None
    if 'new_music' in request.args:
        new_music = request.args['new_music']
    query_list = []
    uid_sub_list = model.get_sub_list(session)
    sub_list = []
    if uid_sub_list:
        for uid in uid_sub_list:
            sub_list.append(model.get_music_dict_from_sub_id(uid))
    if request.method == 'POST':
        app.logger.info("main POST request: %s", request)
        title = request.form['title'] if request.form['title'] else None
        year = request.form['year'] if request.form['year'] else None
        artist = request.form['artist'] if request.form['artist'] else None
        query_list = model.query_music_table(title, year, artist)
    user_dict = model.get_user_from_session(session)
    context = {'content': "Hello there", 'user': user_dict, 'session': session, 'query_list': query_list,
               'sub_list': sub_list, 'new_music': new_music}
    app.logger.info('app.py main context: %s', context)
    app.logger.debug('app.py main END')
    return render_template('main.html', context=context)


@app.route('/register', methods=['GET', 'POST'])
def register():
    app.logger.debug('app.py register BEGIN')
    error = None
    if request.method == 'POST':
        if not model.validate_user_email(request.form['email']):
            if model.create_new_user(request.form['email'], request.form['username'],
                                     request.form['password']):
                app.logger.debug('app.py register new user created')
                app.logger.debug('app.py register END')
                return redirect(url_for('login', error='New user created, try logging in'))
            else:
                app.logger.debug('app.py register Unexpected error user not created')
                error = "Unexpected error user creation"
        else:
            error = "Email already exists"
    context = {'content': "Hello there", 'error': error}
    app.logger.info('app.py register context:%s', context)
    app.logger.debug('app.py register END')
    return render_template('register.html', context=context)


@app.route('/main/subscribe/<string:session>/<string:music>')
def subscribe(session, music):
    app.logger.debug('app.py subscribe BEGIN')
    error = "Logged out"
    app.logger.info('app.py subscribe session, music: %s %s', session, music)
    if session is None:
        error = 'Please login first'
    if not model.validate_session(session) or music is None:
        error = 'Unauthenticated access detected, this user has been reported'
        app.logger.debug('app.py subscribe Unauthenticated access detected, this user has been reported END')
        return redirect(url_for('login', error=error))
    if model.session_music_subscribe(session, music):
        app.logger.debug('app.py subscribe END')
        return redirect(url_for('main', session=session, new_music='New music subscription available!'))
    app.logger.debug('app.py subscribe redirect to login END')
    return redirect(url_for('login', error=error))


@app.route('/main/unsubscribe/<string:session>/<string:music>')
def unsubscribe(session, music):
    app.logger.debug('app.py unsubscribe BEGIN')
    error = "Logged out"
    if session is None:
        error = 'Please login first'
    if not model.validate_session(session) or music is None:
        error = 'Unauthenticated access detected, this user has been reported'
        app.logger.debug(
            'app.py unsubscribe Unauthenticated access detected, this user has been reported END')
        return redirect(url_for('login', error=error))
    if model.session_music_unsubscribe(session, music):
        app.logger.debug('app.py unsubscribe END')
        return redirect(url_for('main', session=session, new_music='Unsubscribed!'))
    app.logger.debug('app.py unsubscribe redirect to login END')
    return redirect(url_for('login', error=error))


@app.route('/logout', defaults={'session': None})
@app.route('/logout/<string:session>')
def logout(session):
    app.logger.debug('app.py logout BEGIN %s', session)
    error = "Logged out"
    if session is None:
        error = 'Please login first'
    if not model.validate_session(session):
        error = 'Unauthenticated access detected, this user has been reported'
    model.remove_session(session)
    app.logger.debug('app.py logout END %s', error)
    return redirect(url_for('login', error=error))


if __name__ == '__main__':
    app.logger.debug('app.py __main__ BEGIN')
    settings()
    app.run()
