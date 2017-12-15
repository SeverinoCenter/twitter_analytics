
FROM puckel/docker-airflow:1.8.2
ENV AIRFLOW_HOME /usr/local/airflow
user root
COPY requirements.txt /tmp/
RUN pip install --requirement /tmp/requirements.txt

COPY script/entrypoint.sh ${AIRFLOW_HOME}/entrypoint.sh
COPY config/airflow.cfg ${AIRFLOW_HOME}/airflow.cfg

RUN chown -R airflow: ${AIRFLOW_HOME} \
    && chmod +x ${AIRFLOW_HOME}/entrypoint.sh
EXPOSE 8888
USER airflow
WORKDIR ${AIRFLOW_HOME}
ENTRYPOINT ["./entrypoint.sh"]
