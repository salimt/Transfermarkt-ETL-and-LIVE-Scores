import subprocess

try:
    from google.cloud import storage
except ImportError:
    subprocess.check_call(["pip", "install", "google-cloud-storage"])

import os
import sys
from google.cloud import storage
from typing import List
import validation as va


def move_file_to_bucket(bucket_name: str, file_path: str) -> None:
    """
    Upload a file to a Google Cloud Storage bucket.

    Args:
        bucket_name (str): Name of the Google Cloud Storage bucket.
        file_path (str): Path to the file to be uploaded.

    Returns:
        None
    """
    # Set the path to your service account key file
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "ssh key path"

    # Extract filename from file path
    file_name = os.path.basename(file_path)

    # Create a GCS client
    client = storage.Client()

    # Get the bucket
    bucket = client.bucket(bucket_name)

    # Create a blob with the file name
    blob = bucket.blob(file_name)

    # Upload the file to the blob
    blob.upload_from_filename(file_path)

    print(f'File saved to {bucket_name}/{file_name}')

def main() -> None:
    """
    The main function of the script. It validates the input, defines the bucket name and file paths,
    and moves the files to the bucket. If any error occurs, it prints the error and exits the program.

    :param output_name: The name of the output, passed as a command line argument.
    """
    output_name = sys.argv[1]
    try:
        import os
        va.validate_input(output_name)
        bucket_name = "parma-project-terra-bucket"
        file_paths = [f'/tmp/{output_name}-profiles-cleaned.csv',
                   f'/tmp/{output_name}-market-cleaned.csv',
                   f'/tmp/{output_name}-player_stats.csv']
        
        for file in file_paths:
            move_file_to_bucket(bucket_name, file)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()



