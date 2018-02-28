import airflow
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta, date
import os
from airflow.models import Variable
import sys

sys.path.append("/usr/local/airflow/dags")
import twitter_main as tm
import driver as d
import twitterutils as tu


startdate = date.today()
default_args = {
     'owner': 'jason',
     'depends_on_past': False,
     'start_date': startdate,
     'email': ['jkuruzovich@gmail.com'],
     'email_on_failure': True,
     'email_on_retry': False,
     'retries': 1,
     'retry_delay': timedelta(minutes=5),
     'max_active_runs': 1
#     # 'queue': 'bash_queue',
#     # 'pool': 'backfill',
#     # 'priority_weight': 10,
#     # 'end_date': datetime(2016, 1, 1),
 }

dag_profiles = DAG('twitter_get_profiles', default_args=default_args, schedule_interval="0 0 * * *")
dag_timelines = DAG('twitter_get_timelines', default_args=default_args, schedule_interval="0 0 * * *")

# John. #Currently this (below) doesn't work because we are using output from task 1 in task 2. Tasks have to be independent.

# # Create config dictionary
cf_dict = d.config_init("./config.yaml");

# Authorize twitter
twitter = tu.create_twitter_auth(cf_dict)

# Create dictionary of names
all_users = d.get_all_users_from_file(cf_dict)

task1 = PythonOperator(
              task_id='get_profiles',
              python_callable=d.create_profile_stats,
              op_args=(twitter, cf_dict, all_users),
              dag=dag_profiles)

task2 = PythonOperator(
              task_id='create_timelines',
              python_callable=d.create_timelines,
              op_args=(twitter, cf_dict, all_users),
              dag=dag_timelines)
