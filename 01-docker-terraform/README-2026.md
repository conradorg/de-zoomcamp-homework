# Homework 01 - Docker & Terraform (for 2026 cohort)

## Question 1. Understanding docker first run
Run docker with the `python:3.13` image in an interactive mode, use the entrypoint `bash`.

What's the version of pip in the image?

```bash
docker run -it --entrypoint bash python:3.13 
```
```bash
pip --version
# pip 25.3 from /usr/local/lib/python3.13/site-packages/pip (python 3.13)
```

## Question 2. Understanding Docker networking and docker-compose
Given the following docker-compose.yaml, what is the hostname and port that pgadmin should use to connect to the postgres database?
(see compose.yaml, it is the same for 2025 and 2026 cohort)

### Solution:
Let's execute the compose.yaml in `01-docker-terraform/`.
```bash
docker compose up -d
```

In the browser go to: `localhost:8080` and login into pgadmin.

Then, click `Add Server`
- Add `db` or `postgres` as host
- Add port `5432`
- Add the database password and connect
- so, both `db:5432` or `postgres:5432` is correct


## Question 3. Trip Segmentation Count
Download files:
```bash
wget https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2025-11.parquet
wget https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv
```
Download this data and put it into Postgres.

---

### Question:
For the trips in November 2025 (lpep_pickup_datetime between '2025-11-01' and '2025-12-01', exclusive of the upper bound), how many trips had a `trip_distance` of less than or equal to 1 mile?

Setup:
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install SQLAlchemy pandas psycopg2-binary pyarrow tqdm
```
Execute ingestion script:
```bash
python3 ingest-postgres-2026.py
```

In pgadmin:
- go to `Postgres` > `Databases` > `ny_taxi` > `Schemas` > `public` > `Tables`
- right click on `ny_taxi` > `Scripts` > `SELECT script`
- now a select statement can be used/modified to view the data in the  `ny_taxi` table

```sql
SELECT COUNT(*) FROM ny_taxi
WHERE trip_distance <= 1
	AND lpep_pickup_datetime > '2025-11-01'
	AND lpep_pickup_datetime <= '2025-12-01'
;
```

Solution: 8007




## Question 4. Longest trip for each day
Which was the pick up day with the longest trip distance? Only consider trips with `trip_distance` less than 100 miles (to exclude data errors).

Use the pick up time for your calculations.

```sql
SELECT lpep_pickup_datetime::DATE, MAX(trip_distance) as max_trip_distance
FROM ny_taxi
WHERE lpep_pickup_datetime::DATE >= '2025-11-01' 
	AND lpep_pickup_datetime::DATE < '2025-12-01'
	AND trip_distance < 100
GROUP BY lpep_pickup_datetime::DATE
ORDER BY max_trip_distance DESC
LIMIT 1
;
```

Result: 2025-11-14 (with 88.03 miles)



## Question 5. Three biggest pickup zones
Which was the pickup zone with the largest `total_amount` (sum of all trips) on November 18th, 2025?

```sql
SELECT nt."PULocationID", zpu."Zone", SUM(nt.total_amount) as sum_total_amount
FROM ny_taxi as nt
LEFT JOIN zone_lookup as zpu
	ON nt."PULocationID" = zpu."LocationID"
WHERE lpep_pickup_datetime::DATE = '2025-11-18'
GROUP BY nt."PULocationID", zpu."Zone"
ORDER BY sum_total_amount DESC
;
```
Result:
"PULocationID"	"Zone"	"sum_total_amount"
74	"East Harlem North"	9281.920000000004


## Question 6. Largest tip
For the passengers picked up in the zone named "East Harlem North" in November 2025, which was the drop off zone that had the largest tip?

```sql
SELECT
	zdo."Zone" as dropoff,
	MAX(ny_taxi.tip_amount) as max_tip_amount
FROM ny_taxi
LEFT JOIN zone_lookup as zpu
	ON ny_taxi."PULocationID" = zpu."LocationID"
LEFT JOIN zone_lookup as zdo
	ON ny_taxi."DOLocationID" = zdo."LocationID"
WHERE zpu."Zone" = 'East Harlem North'
	AND ny_taxi.lpep_pickup_datetime::DATE >= '2025-11-01'
	AND ny_taxi.lpep_pickup_datetime::DATE < '2025-12-01'
GROUP BY zdo."Zone"
ORDER BY max_tip_amount DESC
;
```

Solution:
|"dropoff"          | "max_tip_amount"  |
|-------------------|-------------------|
|"Yorkville West"	| 81.89             |


## Question 7. Terraform Workflow
Which of the following sequences, respectively, describes the workflow for:

    Downloading the provider plugins and setting up backend,
    Generating proposed changes and auto-executing the plan
    Remove all resources managed by terraform

Answers:

    terraform import, terraform apply -y, terraform destroy
    teraform init, terraform plan -auto-apply, terraform rm
    terraform init, terraform run -auto-approve, terraform destroy
    terraform init, terraform apply -auto-approve, terraform destroy
    terraform import, terraform apply -y, terraform rm

### Solution
Withing the `01-docker-terraform/terraform/` directory execute one of the following sequences:
```bash
# Refresh service-account's auth-token for this session
gcloud auth application-default login

# Initialize state file (.tfstate)
terraform init

# Check changes to new infra plan
terraform plan -var="project=<your-gcp-project-id>"
```

Alternatively, specify a credentials file path
```bash
# Initialize state file (.tfstate)
terraform init

# Check changes to new infra plan
terraform plan -var "project=<your-gcp-project-id>" -var "credentials=<your-credentials-file>"
```

---

Then apply
```bash
terraform plan -var "project=<your-gcp-project-id>"
# OR
terraform plan -var "project=<your-gcp-project-id>" -var "credentials=<your-credentials-file>"
```

Alternatively, with auto-approve
```bash
terraform plan -auto-approve -var "project=<your-gcp-project-id>"
# OR
terraform plan -auto-approve -var "project=<your-gcp-project-id>" -var "credentials=<your-credentials-file>"
```


---

Then destroy
```bash
terraform destroy
# OR
terraform destory -var "credentials=<your-credentials-file>"
```
---
### Answer to the question
Please do not do auto-approve in practise unless you are really sure!
```bash
terraform init 
terraform apply -auto-approve 
terraform destroy
```