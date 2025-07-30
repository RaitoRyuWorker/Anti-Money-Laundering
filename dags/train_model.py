from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from datetime import datetime

default_args = {
    "owner": "airflow",
    "retries": 0,
}

def train_model():
    train_model_job = SparkSubmitOperator(
        task_id="train_model",
        conn_id="my_spark_conn",
        application="jobs/train_model/random_forest.py",
        verbose=True,
        jars="/mnt/shared/jars/hadoop-aws-3.3.4.jar,/mnt/shared/jars/aws-java-sdk-bundle-1.12.262.jar",
    )
    train_model_job
    return None

with DAG(
    dag_id="train_model",
    default_args=default_args,
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=["train", "spark"]
) as dag:
    train_model()