import logging
from google.cloud import bigquery
import validation as va
import sys
from typing import Dict

def load_csv_to_bigquery(file_table_mapping: Dict[str, str], dataset_id: str) -> None:
    """
    Load CSV files from Google Cloud Storage (GCS) into BigQuery.

    Args:
        file_table_mapping (Dict[str, str]): A dictionary mapping file URIs to table names.
        dataset_id (str): The ID of the BigQuery dataset.

    Returns:
        None
    """
    try:
        client = bigquery.Client()

        # Iterate over each file URI and corresponding table name
        for file_uri, table_name in file_table_mapping.items():

            # Construct the table reference
            table_ref = client.dataset(dataset_id).table(table_name)

            # Configure the job to load the data from GCS into BigQuery
            job_config = bigquery.LoadJobConfig(
                source_format=bigquery.SourceFormat.CSV,
                skip_leading_rows=1,
                autodetect=True,
                write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE
            )
            
            # Start the job to load data from GCS into BigQuery
            load_job = client.load_table_from_uri(
                file_uri, table_ref, job_config=job_config
            )
            
            # Wait for the job to complete
            load_job.result()
            
            print(f"Loaded data from {file_uri} into BigQuery table")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        sys.exit(1)
        
def main() -> None:
    """
    Main entry point of the script.
    """
    output_name = sys.argv[1]

    try:
        import os
        va.validate_input(output_name)
        # Set the path to your service account key file
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "ssh key path"

        bucket_name = "parma-project-terra-bucket"
        file_table_mapping = {
            f"gs://{bucket_name}/{output_name}-profiles-cleaned.csv": "profiles",
            f"gs://{bucket_name}/{output_name}-market-cleaned.csv": "market_value_history",
            f"gs://{bucket_name}/{output_name}-player_stats.csv": "players_stats"
        }
        dataset_id = "transfermarkt_analytics"


        # Call the function to load data from GCS into BigQuery
        load_csv_to_bigquery(file_table_mapping, dataset_id)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
