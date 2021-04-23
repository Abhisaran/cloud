from flask import Flask, render_template, redirect, url_for, request, jsonify
import model

app = Flask(__name__)


def settings():
    mod = model.init_boto3()


@app.route('/')
def hello_world():
    context = {'content':model.check_dynamo()}
    return render_template('index.html', context=context)


if __name__ == '__main__':
    settings()
    app.run()
