import boto3
import os
import urllib
import sys
from datetime import datetime
import boto3.session

AWS_PROFILE = os.getenv("AWS_PROFILE", "default") # Seu profile da AWS
session = boto3.session.Session(profile_name=AWS_PROFILE)
s3_client = session.client("s3")

BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data/"
BASE_FILE_NAME = "{source_name}_{date}.parquet"
SOURCES = [
    "yellow_tripdata",
    "green_tripdata",
    "fhv_tripdata",
    "fhvhv_tripdata",
]

project_name = "datalake-template-project"  
S3_BUCKET = os.getenv("S3_BUCKET", f"{project_name}-bronze-zone")
S3_PATH = os.getenv("S3_PATH", "nyc_tlc")

def download_and_upload(s3_client, date_str):
    # Converte para datetime para validação e formatação
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m")
    except ValueError:
        raise ValueError("Data inválida. Use o formato YYYY-MM. Ex: 2023-01")

    for source in SOURCES:
        file_name = BASE_FILE_NAME.format(source_name=source, date=date_obj.strftime("%Y-%m"))
        url = BASE_URL + file_name
        print(f"Downloading {url}")
        local_path = f"/tmp/{file_name}"

        try:
            urllib.request.urlretrieve(url, local_path)
        except Exception as e:
            print(f"Erro ao baixar {url}: {e}")
            continue

        s3_key = f"{S3_PATH}/{source}/partition_year_month={date_str}/{file_name}"
        print(f"Uploading to s3://{S3_BUCKET}/{s3_key}")
        try:
            s3_client.upload_file(local_path, S3_BUCKET, s3_key)
        except Exception as e:
            print(f"Erro ao enviar para o S3: {e}")
            continue

def main():
    if len(sys.argv) != 2:
        print("Run correto: python ingestion.py YYYY-MM")
        sys.exit(1)

    date_input = sys.argv[1]
    print(f"Started processing for date: {date_input}")
    download_and_upload(s3_client, date_input)
    print("Finished processing!")

if __name__ == "__main__":
    main()