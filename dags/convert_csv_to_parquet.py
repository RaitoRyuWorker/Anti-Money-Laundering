from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.decorators import task
from airflow.models import Variable
from datetime import datetime, timedelta
import os
import subprocess

default_args = {
    "owner": "airflow",
    "retries": 0,
}

def convert_files_to_parquet():
    submit_job = SparkSubmitOperator(
        task_id="submit_job",
        conn_id="my_spark_conn",
        application="jobs/spark_csv_to_parquet.py",
        verbose=True,
        jars="/mnt/shared/jars/hadoop-aws-3.3.4.jar,/mnt/shared/jars/aws-java-sdk-bundle-1.12.262.jar",
    )
    submit_job

with DAG(
    dag_id="csv_to_parquet_bronze_dag",
    default_args=default_args,
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=["bronze", "etl", "spark"]
) as dag:
    
    convert_files_to_parquet()

    # convert_task = PythonOperator(
    #     task_id="convert_csv_to_parquet",
    #     python_callable=convert_files_to_parquet,
    #     provide_context=True
    # )

    # convert_task
