from google.oauth2 import service_account
from flask import Flask, render_template
from google.cloud import bigquery

path = "bigqapp-310208-35423e2f6eca.json"
c = service_account.Credentials.from_service_account_file(path)
client = bigquery.Client(credentials=c)

app = Flask(__name__)


@app.route('/')
def big():
    q = """
    SELECT time_ref, SUM (value) as total FROM `bigqapp-310208.bigapp.gs` GROUP BY time_ref ORDER BY SUM(value) DESC
        limit 10;
    """
    qj = client.query(q)
    data = {'qj': qj}

    return render_template("index.html", data=data)


if __name__ == '__main__':
    app.run()
