from flask import Flask, render_template, redirect, url_for, request, jsonify
import model
import logging

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')


def settings():
    mod = model.init_boto3()


@app.route('/')
def hello_world():
    context = {'content': model.assert_dynamo()}
    return render_template('index.html', context=context)


if __name__ == '__main__':
    settings()
    app.run()
