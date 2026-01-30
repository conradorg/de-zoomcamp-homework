# Homework 02 - Workflow Orchestration (for 2026 cohort)

In this task **kestra** will be used as orchestrator to import and analyze the taxi data. It will be executed locally via *docker compose*.

**terraform** will be used to create a *BigQuery* dataset for the tables and a *storage bucket* to store the original data files (csv/parquet).


## A - Create Infrastructure
First we will create the BigQuery dataset and the storage bucket. For this step e.g. a service account can be used with the following permissions:
- `BigQuery Admin`
- `Storage Admin`

Set your environment variables in order to use terraform:
```bash
export GOOGLE_APPLICATION_CREDENTIALS=<path_to_credentials> \
export SOME_STRING=<number> \
export TF_VAR_project=<project_name> \
export TF_VAR_bq_dataset_name=${TF_VAR_project//-/_}_bqdataset_${SOME_STRING} \
export TF_VAR_gcs_bucket_name=${TF_VAR_project//-/_}_bucket_${SOME_STRING}
```

Terraform usage:
```bash
terraform init
terraform plan
terraform apply
terraform destroy
```


## B - Kestra Usage
Kestra needs a service account with the following permissions to access data in BigQuery and GCS:
- `BigQuery Data Editor`
- `BigQuery Job User`
- `Storage Object Admin` 

The credentials for this second service account will be made available to kestra using *kestra secrets*. Use the following code to create and `.env_encoded` file which is used by the docker compose. Execute in `02-workflow-orchestration/`:
```bash
echo SECRET_GCP_SERVICE_ACCOUNT=$(cat <path_to_credentials> | base64 -w 0) >> .env_encoded
```

To get kestra running and import the workflow execute:
```bash
docker compose up -d
curl -X POST -u 'admin@kestra.io:Admin1234' http://localhost:8080/api/v1/flows/import -F fileUpload=@flows/09_gcp_taxi_scheduled.yaml
```

Put necessary variables into the KV store via REST API call:
```bash
curl -X PUT -H "Content-Type: text/plain" -u 'admin@kestra.io:Admin1234' http://localhost:8080/api/v1/main/namespaces/zoomcamp/kv/GCP_PROJECT_ID -d \"$TF_VAR_project\"

curl -X PUT -H "Content-Type: text/plain" -u 'admin@kestra.io:Admin1234' http://localhost:8080/api/v1/main/namespaces/zoomcamp/kv/GCP_DATASET -d \"$TF_VAR_bq_dataset_name\"

# curl -X PUT -H "Content-Type: text/plain" -u 'admin@kestra.io:Admin1234' http://localhost:8080/api/v1/main/namespaces/zoomcamp/kv/GCP_LOCATION -d \"$TF_VAR_project\"

curl -X PUT -H "Content-Type: text/plain" -u 'admin@kestra.io:Admin1234' http://localhost:8080/api/v1/main/namespaces/zoomcamp/kv/GCP_BUCKET_NAME -d \"$TF_VAR_gcs_bucket_name\"

```

## C - Kestra Usage: Execute the workflow as backfill
In kestra, navigate to the workflow and then to *triggers*. Click *Backfill executions* and enter the respective data. In Google Cloud watch your data grow in the bucket and BigQuery. Tables can be viewed in BigQuery.


-----


## Quiz Questions

1. Within the execution for Yellow Taxi data for the year 2020 and month 12: what is the uncompressed file size (i.e. the output file yellow_tripdata_2020-12.csv of the extract task)?
    - look in GCS for the file
    - 134.5 MB
2. What is the rendered value of the variable file when the inputs taxi is set to green, year is set to 2020, and month is set to 04 during execution?
    - green_tripdata_2020-04.csv
3. How many rows are there for the Yellow Taxi data for all CSV files in the year 2020?
    - Run a query in BigQuery on the summary table (`yellow_tripdata`):
        ```sql
        SELECT COUNT(1) 
        FROM `<PROJECT>.<BQ_DATASET>.yellow_tripdata` 
        WHERE TIMESTAMP_TRUNC(tpep_pickup_datetime, DAY) >= TIMESTAMP("2020-01-01")
        AND TIMESTAMP_TRUNC(tpep_pickup_datetime, DAY) < TIMESTAMP("2021-01-01")
        ```
    - 24648235
4. How many rows are there for the Green Taxi data for all CSV files in the year 2020?
    - Run a query in BigQuery on the summary table (`green_tripdata`):
        ```sql
        SELECT COUNT(1) 
        FROM `<PROJECT>.<BQ_DATASET>.green_tripdata` 
        WHERE TIMESTAMP_TRUNC(lpep_pickup_datetime, DAY) >= TIMESTAMP("2020-01-01")
        AND TIMESTAMP_TRUNC(lpep_pickup_datetime, DAY) < TIMESTAMP("2021-01-01")
        ```
    - 1733999
5. How many rows are there for the Yellow Taxi data for the March 2021 CSV file?
    - Look in GCS at `yellow_tripdata_2021_03`, go to the details tab and look at the number of rows:
    - 1,925,152
6. How would you configure the timezone to New York in a Schedule trigger?
    - add the timezone property to the trigger: `timezone: America/New_York`
