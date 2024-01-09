FROM apache/airflow:latest
COPY requirements.txt /
RUN pip install --no-cache-dir "apache-airflow==2.8.0" -r /requirements.txt
ENV AIRFLOW__CORE__LOAD_EXAMPLES=False
ENV AIRFLOW_PROJ_DIR=/Users/anushkrishnav/Documents/Projects/PayTrack
