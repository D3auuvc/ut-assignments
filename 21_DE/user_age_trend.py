from email.policy import default
from datetime import datetime, timedelta

from airflow.models.baseoperator import BaseOperator
from airflow.models.dag import DAG
from airflow.operators.dagrun_operator import TriggerDagRunOperator
from airflow.utils.trigger_rule import TriggerRule

DEFAULT_ARGS = {
    'owner': 'Tartu',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

DATA_FOLDER = r'/tmp/data'

user_age_trend_trigger_dag = DAG(
    dag_id='user_age_trend_trigger_dag',  # name of dag
    schedule_interval='None',  # execute every minute
    start_date=datetime(2022, 9, 14, 9, 15, 0),
    catchup=False,  # in case execution has been paused, should it execute everything in between
    # the PostgresOperator will look for files in this folder
    template_searchpath=DATA_FOLDER,
    default_args=DEFAULT_ARGS,  # args assigned to all operators
)
