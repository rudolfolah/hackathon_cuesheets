import boto3
import pydub
import requests
from botocore.config import Config

import json
import os.path

DOLBY_API_KEY = ""
DOLBY_SECRET = ""

AWS_ACCESS_KEY = ""
AWS_SECRET_KEY = ""

s3_bucket = "hackathoncuesheet"
s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    config=Config(region_name="us-east-2", signature_version="s3v4"),
)
s3_expires_in = 60 * 60  # in seconds


def generate_presigned_url_get(key):
    url = s3_client.generate_presigned_url(
        ClientMethod="get_object",
        Params={"Bucket": s3_bucket, "Key": key},
        ExpiresIn=s3_expires_in,
    )
    print(url)
    return url


def generate_presigned_url_put(key):
    url = s3_client.generate_presigned_url(
        ClientMethod="put_object",
        Params={"Bucket": s3_bucket, "Key": key},
        ExpiresIn=s3_expires_in,
    )
    print(url)
    return url

def start_analyze(input_s3_url, output_s3_url):
    url = "https://api.dolby.com/media/analyze"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "x-api-key": DOLBY_API_KEY,
    }
    data = {
        "input": input_s3_url,
        "output": output_s3_url,
    }
    response = requests.request("POST", url, headers=headers, json=data)
    print(data)
    print(response.status_code)
    print(response.text)
    if response.status_code == 200:
        return response.json()["job_id"]
    return None


def is_analysis_finished(job_id):
    url = "https://api.dolby.com/media/analyze"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "x-api-key": DOLBY_API_KEY,
    }
    data = {"job_id": job_id}
    response = requests.request("GET", url, headers=headers, params=data)
    print(response.status_code)
    print(response.text)
    if response.status_code == 200:
        return response.json()["status"] == "Success"
    return None


def upload_for_processing(key, file_path):
    input_audio = s3_client.generate_presigned_post(Bucket=s3_bucket, Key=key, ExpiresIn=s3_expires_in)
    with open(file_path, "rb") as object_file:
        object_data = object_file.read()
        files = {'file': (file_path, object_data)}
        response = requests.post(input_audio['url'], headers=input_audio['fields'], data=input_audio['fields'],
                                 files=files)
        if response.status_code == 204:
            return True
    return False


def download_processed_info(s3_key):
    obj = s3_client.get_object(Bucket=s3_bucket, Key=s3_key)
    data = obj["Body"].read().decode("utf-8")
    with open("output/processed-example.json", "w") as f:
        f.write(data)
    json_data = json.loads(data)
    return json_data


def main():
    key = "example.ogg"
    if upload_for_processing("example.ogg", "dataset/example.ogg"):
        dolby_input = generate_presigned_url_get("example.ogg")
        dolby_output = generate_presigned_url_put("processed-example.json")
        print(dolby_output)
        job_id = start_analyze(dolby_input, dolby_output)
        with open("dolby_job_ids.txt", "a") as f:
            f.write(f"{job_id},{key}\n")
        is_analysis_finished(job_id)


if __name__ == "__main__":
    if os.path.exists("./dolby_job_ids.txt"):
        with open("./dolby_job_ids.txt", "r") as f:
            for line in f:
                job_id, key = line.strip().split(',')
                if is_analysis_finished(job_id):
                    download_processed_info(key)
    # main()
