import airflow
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import os
from airflow.models import Variable
import sys
import twitter_main as tm
import twitterutils as tu

# Create config dictionary
cf_dict = tm.config_init("./config/config.yaml");
print("dict", cf_dict)
# Convert screen_names.txt to screen_names.csv
tm.text_to_csv(cf_dict['names_path'])

# # Convert list of names into one string to pull multiple users in one request
names = tm.names_to_string(cf_dict);

# # Authorize twitter
twitter = tu.create_twitter_auth(cf_dict)

# # Find the profiles of all the names in screen_names.txt and create a YYYY-MM-DD-user_profiles.json file
# # containing the profiles
#profiles_fn = tu.get_profiles(twitter, cf_dict['names_path'], cf_dict, names)

# # Create .json file for each profile
#tu.profiles_to_timelines(twitter, profiles_fn, cf_dict)


#create_user_stats(cf_dict)


print("hello world")
#cf = {}
# cf=sf.getConfig('/dojo/config_prd.ini')
#cf = sf.getConfig('/dojo/config_dev_redshift.ini')
#mongo = sf.connectMongo(cf)
#session = sf.createBotoSession(cf)
#s3 = session.resource('s3')
#startdate = datetime(2017, 4, 14, 0, 0)
#
# # #### This is a manual test. This is markdown and wont be run.
# # email='jkuruzovich@gmail.com'
# # user=sf.retreiveUser(mongo,email)
# # job=sf.createJobID(user['email']+cf['now'])
# # sf.extractSalesforce(cf,user,job)
# # sf.verifyS3Bucket(s3,job)
# # sf.csvToS3(cf,s3,job)
# # sf.createTables(cf,user)
# # sf.s3ToRedshift(cf,s3,user,job)
# # sf.deleteS3Bucket(s3,job)
#
# # In[3]:
#
# default_args = {
#     'owner': 'jason',
#     'depends_on_past': False,
#     'start_date': startdate,
#     'email': ['jkuruzovich@gmail.com'],
#     'email_on_failure': True,
#     'email_on_retry': False,
#     'retries': 1,
#     'retry_delay': timedelta(minutes=5),
#     'max_active_runs': 1
#     # 'queue': 'bash_queue',
#     # 'pool': 'backfill',
#     # 'priority_weight': 10,
#     # 'end_date': datetime(2016, 1, 1),
# }
# dag = DAG('salesforce_daily_full_dag', default_args=default_args, schedule_interval="0 0 * * *")
#
# # In[4]:
#
# #### This is a manual test. This is markdown and wont be run.
#
# users = sf.retreiveUsers(mongo, cf, {'interface': 'live'})
# if len(users) > 0:
#     for user in users:
#         job = sf.createJobID(user['email'])
#
#         salesforce_to_csv = PythonOperator(
#             task_id='salesforce_to_csv',
#             provide_context=True,
#             python_callable=sf.extractSalesforce,
#             op_kwargs={'cf': cf, 'user': user, 'job': job},
#             dag=dag)
#
#         verify_bucket = PythonOperator(
#             task_id='verify_bucket',
#             provide_context=True,
#             python_callable=sf.verifyS3Bucket,
#             op_kwargs={'s3': s3, 'job': job},
#             dag=dag)
#
#         verify_bucket.set_upstream(salesforce_to_csv)
#
#         csv_to_s3 = PythonOperator(
#             task_id='csv_to_s3',
#             provide_context=True,
#             python_callable=sf.csvToS3,
#             op_kwargs={'cf': cf, 's3': s3, 'job': job},
#             dag=dag)
#         csv_to_s3.set_upstream(verify_bucket)
#
#         create_tables = PythonOperator(
#             task_id='create_tables',
#             python_callable=sf.createTables,
#             op_kwargs={'cf': cf, 'user': user},
#             dag=dag)
#
#         create_tables.set_upstream(csv_to_s3)
#
#         s3_to_Redshift = PythonOperator(
#             task_id='s3_to_redshift',
#             provide_context=True,
#             python_callable=sf.s3ToRedshift,
#             op_kwargs={'cf': cf, 's3': s3, 'user': user, 'job': job},
#             dag=dag)
#
#         s3_to_Redshift.set_upstream(create_tables)
#
#         s3_cleanup = PythonOperator(
#             task_id='s3_cleanup',
#             provide_context=True,
#             python_callable=sf.deleteS3Bucket,
#             op_kwargs={'s3': s3, 'job': job},
#             dag=dag)
#
#         s3_cleanup.set_upstream(s3_to_Redshift)
#
#         last_all = PythonOperator(
#             task_id='last_all',
#             python_callable=sf.updateUser,
#             op_kwargs={'mongo': mongo, 'email': user['email'], 'name': 'last_all', 'value': str(cf['now'])},
#             dag=dag)
#
#         last_all.set_upstream(s3_cleanup)
#
