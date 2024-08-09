import subprocess

try:
    import pip
except ImportError:
    subprocess.check_call(["sudo", "apt", "update"])
    subprocess.check_call(["sudo", "apt", "install", "python3-pip"])

try:
    import airflow
except ImportError:
    subprocess.check_call(["pip", "install", "--upgrade", "requests"])
    subprocess.check_call(["pip", "install", "apache-airflow"])

from airflow.models import DAG
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
from datetime import datetime, timedelta

"""
This DAG runs the ELT process for the ransfermarkt data pipeline.
"""

# Output name of extracted file. This will be passed to each
# DAG task so they know which file to process
output_name = datetime.now().strftime("%Y%m%d")

#schedule_interval = "@daily"
schedule_interval = None
start_date = days_ago(1)


default_args = {
    "owner": "salimt",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
    "max_active_runs_per_dag": 1,

}
with DAG(
    "PARMA-ELT-Datapipeline",
    default_args=default_args,
    description="Transfermarkt ELT",
    schedule_interval=schedule_interval,
    start_date=start_date,
    tags=["ParmaELT"],
    catchup=False,
) as dag:

    extract_player_data = BashOperator(
        task_id="extract_player_data",
        bash_command=f"python /opt/airflow/scripts/extract_player_data.py {output_name}",
        dag=dag,
    )
    extract_player_data.doc_md = "Extract player data from Transfermarkt and save as CSV"

    extract_market_data = BashOperator(
        task_id="extract_market_data",
        bash_command=f"python /opt/airflow/scripts/extract_market_data.py {output_name}",
        dag=dag,
    )
    extract_market_data.doc_md = "Extract market data from Transfermarkt and save as CSV"
    
    vm_to_gcp_bucket = BashOperator(
        task_id="vm_to_gcp_bucket",
        bash_command=f"python /opt/airflow/scripts/load_to_gcp_bucket.py {output_name}",
        dag=dag,
    )
    vm_to_gcp_bucket.doc_md = "Upload the extracted data to GCP bucket"

    load_to_bq = BashOperator(
        task_id="load_to_bq",
        bash_command=f"python /opt/airflow/scripts/load_to_bq.py {output_name}",
        dag=dag,
    )
    load_to_bq.doc_md = "Load the extracted data to BigQuery from GCP Bucket"

    clean_profiles_data = BashOperator(
        task_id='clean_profiles_data',
        bash_command=f"python /opt/airflow/scripts/clean_profiles_data.py {output_name}",
        dag=dag,
    )
    clean_profiles_data.doc_md = "Clean the profiles.csv file."

    clean_market_value_history_data = BashOperator(
        task_id='clean_market_value_history_data',
        bash_command=f"python /opt/airflow/scripts/clean_value_history_data.py {output_name}",
        dag=dag,
    )
    clean_market_value_history_data.doc_md = "Clean the profiles.csv file."

    extract_player_stats = BashOperator(
        task_id='extract_player_stats',
        bash_command=f"python /opt/airflow/scripts/extract_player_stats.py {output_name}",
        dag=dag,
    )
    extract_player_stats.doc_md = "Scrape Player Statistics."

    remove_local_files = BashOperator(
        task_id='remove_local_files',
        bash_command=f'rm /tmp/{output_name}-market.csv /tmp/{output_name}-market-cleaned.csv /tmp/{output_name}-profiles.csv /tmp/{output_name}-profiles-cleaned.csv /tmp/{output_name}-profiles-processed-urls.txt /tmp/{output_name}-market-processed_ids.txt /tmp/{output_name}-player_stats.csv /tmp/{output_name}-stats-processed-urls.txt',
        dag=dag,
    )
    remove_local_files.doc_md = "Remove the extracted files from the local system."


extract_player_data >> clean_profiles_data >> extract_market_data >> clean_market_value_history_data >> extract_player_stats >> vm_to_gcp_bucket >> load_to_bq >> remove_local_files