import urllib.request
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python_operator import PythonOperator

DEFAULT_ARGS = {
    'owner': 'Tartu',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

API_URL = r'https://randomuser.me/api/?results=5&format=csv'
FILE_NAME = r'crm.csv'

DATA_FOLDER = r'/tmp/data'

crm_generator_dag = DAG(
    dag_id='crm_generator',  # name of dag
    schedule_interval='* * * * *',  # execute every minute
    start_date=datetime(2022, 9, 14, 9, 15, 0),
    catchup=False,  # in case execution has been paused, should it execute everything in between
    # the PostgresOperator will look for files in this folder
    template_searchpath=DATA_FOLDER,
    default_args=DEFAULT_ARGS,  # args assigned to all operators
)

# Task 1 - fetch the 5 users from the API at https://randomuser.me/ Save the users into a csv file.


def get_five_users(url, output_folder, file_name):
    # Download the file from `url` and save it locally under `file_name`:
    with urllib.request.urlopen(url) as response, open(f'{output_folder}/{file_name}', 'wb') as out_file:
        data = response.read()  # a `bytes` object
        out_file.write(data)


first_task = PythonOperator(
    task_id='get_five_users',
    dag=crm_generator_dag,
    trigger_rule='none_failed',
    python_callable=get_five_users,
    op_kwargs={
        'output_folder': DATA_FOLDER,
        'url': API_URL,
        'file_name': FILE_NAME
    },
)
