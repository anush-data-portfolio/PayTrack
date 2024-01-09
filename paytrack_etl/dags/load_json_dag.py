
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.operators.bash import BashOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.decorators import dag, task
from airflow.utils.dates import days_ago
from paytrack.models.schema import User
import json
from dataclasses import asdict
from paytrack.loader import Loader
from config import Config


default_args = {
    'owner': 'anush',
    'depends_on_past': False,
    'start_date' : days_ago(0),
    'email': ['anush.venkatakrishna@gmail.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'catchup': False,
}




def get_query():
    file = 'dags/data/2023.json'
    with open(file) as f:
        data= eval(json.load(f)) 
    user = User(**data)
    loader = Loader(user)
    query = loader.update_punches()
    with open('dags/temp/scripts/insert_punches.sql', 'w') as f:
        f.write(query)
    return query

    
dag = DAG(
    dag_id='json_to_postgres',
    default_args=default_args,
    description='Update Json to postgres',
    tags=['etl'],
    schedule_interval=None
)

with dag:
    start_pipeline = EmptyOperator(task_id='start_pipeline')

    load_query = PythonOperator(
        task_id='load_query',
        python_callable=get_query,
        provide_context=True,
        dag=dag
    )

    insert_data = PostgresOperator(
        task_id='insert_data',
        postgres_conn_id='paytrack_db',
        sql="/temp/scripts/insert_punches.sql"
    )

    clear_temp = BashOperator(
        task_id='clear_temp',
        bash_command='rm -rf /opt/airflow/dags/temp/scripts/insert_punches.sql'
    )



    end_pipeline = EmptyOperator(task_id='end_pipeline')
    start_pipeline >>  load_query >> insert_data >> clear_temp >> end_pipeline

    # start_pipeline >> extract >> create_tables >> load_query >> insert_data >> end_pipeline
