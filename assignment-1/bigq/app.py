from flask import Flask, render_template
from google.cloud import bigquery
from google.oauth2 import service_account
from google.cloud.exceptions import NotFound

cred_path = "tokyo-list-308701-4bb8fbb50c06.json"
credentials = service_account.Credentials.from_service_account_file(cred_path)
client = bigquery.Client(credentials=credentials)

# init dataset
dataset = None
dataset_id = "{}.{}".format(client.project, 'country_stats')
try:
    dataset = client.get_dataset(dataset_id)
    print("Dataset {} already exists".format(dataset_id))
except NotFound:
    dataset = bigquery.Dataset(dataset_id)
    dataset.location = "US"
    dataset = client.create_dataset(dataset, timeout=30)  # Make an API request.
    print("Created dataset {}.{}".format(client.project, dataset.dataset_id))
    print("Dataset {} is not found".format(dataset_id))

# upload country_classification.csv
table_id = "{}.{}.{}".format(client.project, dataset.dataset_id, "country_class")
try:
    client.get_table(table_id)  # Make an API request.
    print("Table {} already exists.".format(table_id))
except NotFound:
    job_config = bigquery.LoadJobConfig(schema=[
        bigquery.SchemaField("country_code", "STRING"),
        bigquery.SchemaField("country_label", "STRING"),
    ],
        source_format=bigquery.SourceFormat.CSV, skip_leading_rows=1, autodetect=True,
    )
    file_path = 'a1_2/a1_2/country_classification.csv'
    with open(file_path, "rb") as source_file:
        job = client.load_table_from_file(source_file, table_id, job_config=job_config)
    job.result()  # Waits for the job to complete.
    table = client.get_table(table_id)  # Make an API request.
    print(
        "Loaded {} rows and {} columns to {}".format(
            table.num_rows, len(table.schema), table_id
        )
    )

# upload services_classification.csv
table_id = "{}.{}.{}".format(client.project, dataset.dataset_id, "service_class")
try:
    client.get_table(table_id)
    print("Table {} already exists.".format(table_id))
except NotFound:
    job_config = bigquery.LoadJobConfig(schema=[
        bigquery.SchemaField("code", "STRING"),
        bigquery.SchemaField("service_label", "STRING"),
    ],
        source_format=bigquery.SourceFormat.CSV, skip_leading_rows=1, autodetect=True,
    )
    file_path = 'a1_2/a1_2/services_classification.csv'
    with open(file_path, "rb") as source_file:
        job = client.load_table_from_file(source_file, table_id, job_config=job_config)
    job.result()  # Waits for the job to complete.
    table = client.get_table(table_id)  # Make an API request.
    print(
        "Loaded {} rows and {} columns to {}".format(
            table.num_rows, len(table.schema), table_id
        )
    )

# upload gsquarterlySeptember20.csv
table_id = "{}.{}.{}".format(client.project, dataset.dataset_id, "gsquarterly")
try:
    client.get_table(table_id)
    print("Table {} already exists.".format(table_id))
except NotFound:
    job_config = bigquery.LoadJobConfig(schema=[
        bigquery.SchemaField("time_ref", "INT64"),
        bigquery.SchemaField("account", "STRING"),
        bigquery.SchemaField("code", "INT64"),
        bigquery.SchemaField("country_code", "STRING"),
        bigquery.SchemaField("product_type", "STRING"),
        bigquery.SchemaField("value", "INT64"),
        bigquery.SchemaField("status", "STRING"),
    ],
        source_format=bigquery.SourceFormat.CSV, skip_leading_rows=1, autodetect=True,
    )
    file_path = 'a1_2/a1_2/gsquarterlySeptember20.csv'
    with open(file_path, "rb") as source_file:
        job = client.load_table_from_file(source_file, table_id, job_config=job_config)
    job.result()  # Waits for the job to complete.
    table = client.get_table(table_id)  # Make an API request.
    print(
        "Loaded {} rows and {} columns to {}".format(
            table.num_rows, len(table.schema), table_id
        )
    )

app = Flask(__name__)


@app.route('/')
def hello_world():
    query = """
    SELECT time_ref, SUM (value) as total_trade
        FROM `tokyo-list-308701.country_stats.gsquarterly`
        GROUP BY time_ref
        ORDER BY total_trade DESC
        limit 10;
    """
    query_job1 = client.query(query)
    #
    # print("The query data:")
    # for row in query_job:
    #     print(row)
    #     print("time_ref={}, trade value={}".format(row[0], row["total_people"]))

    query = """
    select (select cc.country_label from `tokyo-list-308701.country_stats.country_class` as cc where cc.country_code=import_table.country_code) as country_label, 
import_table.import_value-export_table.export_value as trade_deficit_value, import_table.product_type, import_table.status from (select gs.country_code, gs.product_type, gs.status, sum(gs.value) as import_value from `tokyo-list-308701.country_stats.gsquarterly` as gs where gs.account = 'Imports' and gs.status = 'F' and (CAST(gs.time_ref AS STRING) like '2014%'or CAST(gs.time_ref AS STRING) like '2015%' or CAST(gs.time_ref AS STRING) like '2016%') group by gs.country_code, gs.product_type, gs.status order by gs.country_code ) as import_table
,(select gs.country_code, gs.product_type, gs.status, sum(gs.value) as export_value from `tokyo-list-308701.country_stats.gsquarterly` as gs where gs.account = 'Exports' and gs.status = 'F' and (CAST(gs.time_ref AS STRING) like '2014%'or CAST(gs.time_ref AS STRING) like '2015%' or CAST(gs.time_ref AS STRING) like '2016%')  group by gs.country_code, gs.product_type, gs.status order by gs.country_code ) as export_table
where import_table.country_code=export_table.country_code and import_table.product_type=export_table.product_type order by trade_deficit_value desc limit 50    
"""

    query_job2 = client.query(query)

    query = """
        select (select service_label from `tokyo-list-308701.country_stats.service_class` where code=task3.code) as service_label, task3.trade_surplus_value from 
(select import_table.code,
export_table.export_value-import_table.import_value as trade_surplus_value, import_table.time_ref from (select gs.code, gs.country_code, gs.time_ref, sum(gs.value) as import_value from `tokyo-list-308701.country_stats.gsquarterly` as gs where gs.account = 'Imports' group by gs.code, gs.country_code, gs.time_ref order by gs.country_code) as import_table
,(select gs.code, gs.country_code, gs.time_ref, sum(gs.value) as export_value from `tokyo-list-308701.country_stats.gsquarterly` as gs where gs.account = 'Exports' group by gs.code, gs.country_code, gs.time_ref order by gs.country_code) as export_table
where import_table.country_code=export_table.country_code and import_table.time_ref=export_table.time_ref order by trade_surplus_value desc    
) as task3,
(SELECT time_ref, SUM (value) as total_people, code
    FROM `tokyo-list-308701.country_stats.gsquarterly`
    GROUP BY time_ref, code
    ORDER BY total_people DESC
    limit 10) as task1,
(select import_table.country_code, import_table.code,
import_table.import_value-export_table.export_value as trade_deficit_value, import_table.product_type, import_table.status from (select gs.country_code, gs.product_type, gs.status,gs.code, sum(gs.value) as import_value from `tokyo-list-308701.country_stats.gsquarterly` as gs where gs.account = 'Imports' and gs.status = 'F' and (CAST(gs.time_ref AS STRING) like '2014%'or CAST(gs.time_ref AS STRING) like '2015%' or CAST(gs.time_ref AS STRING) like '2016%') group by gs.country_code, gs.product_type, gs.status, gs.code order by gs.country_code ) as import_table
,(select gs.country_code, gs.product_type, gs.status, gs.code, sum(gs.value) as export_value from `tokyo-list-308701.country_stats.gsquarterly` as gs where gs.account = 'Exports' and gs.status = 'F' and (CAST(gs.time_ref AS STRING) like '2014%'or CAST(gs.time_ref AS STRING) like '2015%' or CAST(gs.time_ref AS STRING) like '2016%')  group by gs.country_code, gs.product_type, gs.status, gs.code order by gs.country_code ) as export_table
where import_table.country_code=export_table.country_code and import_table.product_type=export_table.product_type order by trade_deficit_value desc limit 50    
) as task2

where task1.time_ref = task3.time_ref and task2.code = task3.code order by task3.trade_surplus_value desc limit 30  """

    query_job3 = client.query(query)

    context = {'query1': query_job1, 'query2': query_job2, 'query3': query_job3}

    return render_template("index.html", context=context)


if __name__ == '__main__':
    app.run()
