import airflow
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import os
from airflow.models import Variable
import sys

sys.path.append("/usr/local/airflow/dags")
import twitter_main as tm
import twitterutils as tu


startdate = datetime(2017, 12, 21, 0, 0)
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

dag = DAG('twitter_get_profiles', default_args=default_args, schedule_interval="0 0 * * *")


task1 = PythonOperator(
              task_id='get_profiles',
              python_callable=tm.main,
              dag=dag)

# John. #Currently this (below) doesn't work because we are using output from task 1 in task 2. Tasks have to be independent.

# # Create config dictionary
# cf_dict = tm.config_init("./config/config.yaml");
# print("dict", cf_dict)
#
# # Convert screen_names.txt to screen_names.csv
# tm.text_to_csv(cf_dict['names_path'])
#
# # # Convert list of names into one string to pull multiple users in one request
# names = tm.names_to_string(cf_dict);
#
# # # Authorize twitter
# twitter = tu.create_twitter_auth(cf_dict)


# task1 = PythonOperator(
#              task_id='get_profiles',
#              python_callable=tu.get_profiles,
#              op_args=(twitter, cf_dict['names_path'], cf_dict, names),
#              dag=dag)
#
# #Currently this doesn't work because we are using output from task 1 in task 2. Tasks have to be independent.
# task2 = PythonOperator(
#              task_id='profiles_to_timelines',
#              python_callable=tu.profiles_to_timelines,
#              op_args=(twitter, profiles_fn, cf_dict),
#              dag=dag)
#
# task2.set_upstream(task1)

