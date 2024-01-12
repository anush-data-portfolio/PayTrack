from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.operators.bash import BashOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.utils.dates import days_ago
from paytrack.models.schema import User
from paytrack.loader import Loader
from config import Config
from paytrack.paytrackobj import Paytrack

default_args = {
    'owner': 'anush',
    'depends_on_past': False,
    'start_date': days_ago(0),
    'email': ['anush.venkatakrishna@gmail.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'catchup': False,
}

def get_punches():
    """
    Retrieve punch data using the Paytrack object.

    Returns:
    dict: Punch data in dictionary format.
    """
    paytrack = Paytrack(is_today=True)
    data: User = paytrack.get_pay_data()
    return data.model_dump()

def get_query(**kwargs):
    """
    Generate SQL query based on extracted data.

    Parameters:
    - kwargs (dict): Keyword arguments passed by Airflow.

    Returns:
    str: SQL query string.
    """
    ti = kwargs['ti']
    data_dict = ti.xcom_pull(task_ids='extract')
    user = User(**data_dict)
    loader = Loader(user)
    query = loader.update_punches()

    # If query is an empty string, return "skip"
    if len(query) == 0:
        return "skip"

    with open('dags/temp/scripts/update_punches.sql', 'w') as f:
        f.write(query)
    return query

def skip_task(**kwargs):
    """
    Determine whether to skip or proceed to the next task.

    Parameters:
    - kwargs (dict): Keyword arguments passed by Airflow.

    Returns:
    str: Task ID for the next task to execute.
    """
    ti = kwargs['ti']
    data_dict = ti.xcom_pull(task_ids='load_query')
    if data_dict == "skip":
        return "dummy_task"
    return "insert_data"

# Schedule everyday at 10 pm
dag = DAG(
    dag_id='update_punches',
    default_args=default_args,
    description='Look for new punches and update them every day',
    tags=['etl'],
    schedule_interval='0 22 * * *'
)

with dag:
    start_pipeline = EmptyOperator(task_id='start_pipeline')

    extract = PythonOperator(
        task_id='extract',
        python_callable=get_punches,
        provide_context=True,
        dag=dag
    )

    load_query = PythonOperator(
        task_id='load_query',
        python_callable=get_query,
        provide_context=True,
        dag=dag
    )

    branch_it = BranchPythonOperator(
        task_id='branch_it',
        python_callable=skip_task,
        provide_context=True
    )

    insert_data = PostgresOperator(
        task_id='insert_data',
        postgres_conn_id='paytrack_db',
        sql="/temp/scripts/update_punches.sql",
    )

    dummy_task = EmptyOperator(task_id='dummy_task')

    clear_temp = BashOperator(
        task_id='clear_temp',
        bash_command='rm -rf /opt/airflow/dags/temp/scripts/update_punches.sql',
        trigger_rule='none_failed'
    )

    end_pipeline = EmptyOperator(task_id='end_pipeline', trigger_rule='none_failed_min_one_success')

    start_pipeline >> extract >> load_query >> branch_it
    branch_it >> [insert_data, dummy_task] 
    [insert_data, dummy_task] >> clear_temp >> end_pipeline
