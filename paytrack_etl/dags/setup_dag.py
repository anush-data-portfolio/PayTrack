
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.operators.bash import BashOperator
from airflow.decorators import dag, task
from airflow.utils.dates import days_ago
from paytrack.paytrackobj import Paytrack
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

def pydantic_to_dict(pydantic_obj):
    return asdict(pydantic_obj)


def pay_data():
    paytrack = Paytrack()
    data: User = paytrack.get_pay_data()
    return data.model_dump()


def get_query(**kwargs):
    ti = kwargs['ti']
    data_dict = ti.xcom_pull(task_ids='extract')
    user = User(**data_dict)
    config = Config()
    key = config.SECRET_KEY
    loader = Loader(user)
    query = loader.get_query()
    with open('dags/temp/scripts/setup.sql', 'w') as f:
        f.write(query)
    return query

def get_json_query():
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
    dag_id='catchup',
    default_args=default_args,
    description='Extract, transform and load data into postgres',
    tags=['etl'],
    schedule_interval=None
)

with dag:
    start_pipeline = EmptyOperator(task_id='start_pipeline')


    extract = PythonOperator(
        task_id='extract',
        python_callable=pay_data,
        dag=dag
    )

    create_tables = PostgresOperator(
        task_id='create_tables',
        postgres_conn_id='paytrack_db',
        sql='scripts/tables.sql',
    )

    query = """
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = 'public'
    ORDER BY table_name;
    """
    load_query = PythonOperator(
        task_id='load_query',
        python_callable=get_query,
        provide_context=True,
        dag=dag
    )

    load_json_query = PythonOperator(
        task_id='load_json_query',
        python_callable=get_json_query,
        provide_context=True,
        dag=dag
    )

    insert_data = PostgresOperator(
        task_id='insert_data',
        postgres_conn_id='paytrack_db',
        sql="/temp/scripts/setup.sql"
    )

    insert_json_data = PostgresOperator(
        task_id='insert_json_data',
        postgres_conn_id='paytrack_db',
        sql="/temp/scripts/insert_punches.sql"
    )

    # remove sql files from temp/scripts
    clear_temp = BashOperator(
        task_id='clear_temp',
        bash_command='rm -rf /opt/airflow/dags/temp/scripts/setup.sql'
    )

    clear_json_temp = BashOperator(
        task_id='clear_json_temp',
        bash_command='rm -rf /opt/airflow/dags/temp/scripts/insert_punches.sql'
    )

    end_pipeline = EmptyOperator(task_id='end_pipeline')
    create_tables
    start_pipeline >> [extract, load_json_query]  # Start both pipelines simultaneously

    extract >>  load_query >> insert_data >> clear_temp >> end_pipeline

    load_json_query >> insert_json_data >> clear_json_temp >> end_pipeline


