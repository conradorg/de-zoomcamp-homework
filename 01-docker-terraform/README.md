# Homework 01 - Docker & Terraform

## Question 1. Understanding docker first run
Run docker with the `python:3.12.8` image in an interactive mode, use the entrypoint `bash`.

What's the version of pip in the image?

```bash
docker run -it --entrypoint bash python:3.12.8 
```
```bash
pip --version
# pip 24.3.1 from /usr/local/lib/python3.12/site-packages/pip (python 3.12)
```

## Question 2. Understanding Docker networking and docker-compose
Given the following docker-compose.yaml, what is the hostname and port that pgadmin should use to connect to the postgres database?
(see compose.yaml)

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
wget https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2019-10.csv.gz
gzip -d ./green_tripdata_2019-10.csv.gz
wget https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv
```
Download this data and put it into Postgres.

### Solution:
Setup:
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install SQLAlchemy pandas psycopg2-binary
```
Execute ingestion script:
```bash
python3 ingest-postgres.py
```

In pgadmin:
- go to `Postgres` > `Databases` > `ny_taxi` > `Schemas` > `public` > `Tables`
- right click on `ny_taxi` > `Scripts` > `SELECT script`
- now a select statement can be used/modified to view the data in the  `ny_taxi` table

Questions: During the period of October 1st 2019 (inclusive) and November 1st 2019 (exclusive), how many trips, respectively, happened:
1. Up to 1 mile
	```sql
	SELECT COUNT(*)
		FROM public.ny_taxi
		WHERE lpep_pickup_datetime >= '2019-10-01 00:00'::timestamp 
			AND lpep_dropoff_datetime < '2019-11-01 00:00'::timestamp 
			AND trip_distance <=1;

	```
2. Combine the categories in on query: Up to 1 mile, In between 1 (exclusive) and 3 miles (inclusive), In between 3 (exclusive) and 7 miles (inclusive), In between 7 (exclusive) and 10 miles (inclusive), Over 10 miles
	```sql
	SELECT 
		CASE 
			WHEN trip_distance <= 1 THEN 'Up to 1 mile'
			WHEN trip_distance > 1 AND trip_distance <= 3 THEN '1-3 miles'
			WHEN trip_distance > 3 AND trip_distance <= 7 THEN '3-7 miles'
			WHEN trip_distance > 7 AND trip_distance <= 10 THEN '7-10 miles'
			WHEN trip_distance > 10 THEN 'Over 10 miles'
		END as category,
		COUNT(*)  -- count all rows within group
	FROM ny_taxi
	WHERE lpep_pickup_datetime >= '2019-10-01 00:00'::timestamp 
			AND lpep_dropoff_datetime < '2019-11-01 00:00'::timestamp 
	GROUP BY category
	ORDER BY category;
	```

## Question 4. Longest trip for each day
Which was the pick up day with the longest trip distance? Use the pick up time for your calculations.

Note: The following condition should not be tested... (But only the pickup time will be tested)
```sql
lpep_pickup_datetime >= '2019-10-01 00:00' AND lpep_dropoff_datetime < '2019-11-01 00:00'
```

Option 1 (Only sort)
```sql
SELECT lpep_pickup_datetime::DATE, trip_distance
FROM ny_taxi
WHERE lpep_pickup_datetime::DATE >= '2019-10-01' 
	AND lpep_pickup_datetime::DATE < '2019-11-01'
ORDER BY trip_distance DESC
LIMIT 1
;
```

Option 2 (group by pickup *date*, calculate maximum trip distance for every day)
```sql
SELECT lpep_pickup_datetime::DATE, MAX(trip_distance) as max_trip_distance
FROM ny_taxi
WHERE lpep_pickup_datetime::DATE >= '2019-10-01' 
	AND lpep_pickup_datetime::DATE < '2019-11-01'
GROUP BY lpep_pickup_datetime::DATE
ORDER BY max_trip_distance DESC
LIMIT 1
;
```

Solution:
"2019-10-31"	515.89

## Question 5. Three biggest pickup zones

Which were the top pickup locations with over 13,000 in `total_amount` (across all trips) for 2019-10-18?

Consider only `lpep_pickup_datetime` when filtering by date.

Partial Solution without condition for `sum_total_amount > 13000`
```sql
SELECT lpep_pickup_datetime::DATE, "PULocationID", SUM(total_amount) as sum_total_amount, zone_lookup."Zone"
	FROM ny_taxi
LEFT JOIN zone_lookup 
	ON ny_taxi."PULocationID"=zone_lookup."LocationID"
WHERE lpep_pickup_datetime::DATE='2019-10-18'
GROUP BY "PULocationID", zone_lookup."Zone", lpep_pickup_datetime::DATE
;
```

Solution 1 using `HAVING`
```sql
SELECT lpep_pickup_datetime::DATE, "PULocationID", SUM(total_amount::NUMERIC(20, 2)) as sum_total_amount, zone_lookup."Zone"
	FROM ny_taxi
LEFT JOIN zone_lookup 
	ON ny_taxi."PULocationID"=zone_lookup."LocationID"
WHERE lpep_pickup_datetime::DATE='2019-10-18'
GROUP BY "PULocationID", zone_lookup."Zone", lpep_pickup_datetime::DATE
HAVING SUM(total_amount) > 13000
;
```

Solution 2 using subquery
```sql
SELECT * 
FROM (
	SELECT lpep_pickup_datetime::DATE, "PULocationID", SUM(total_amount::NUMERIC(20, 2)) as sum_total_amount, zone_lookup."Zone"
		FROM ny_taxi
	LEFT JOIN zone_lookup 
		ON ny_taxi."PULocationID"=zone_lookup."LocationID"
	WHERE lpep_pickup_datetime::DATE='2019-10-18'
	GROUP BY "PULocationID", zone_lookup."Zone", lpep_pickup_datetime::DATE
)
WHERE sum_total_amount > 13000
;
```

Solution 3 using CTEs (Common Table Expressions)
```sql
WITH sum_total_amount_for_day AS (
	SELECT lpep_pickup_datetime::DATE, "PULocationID", SUM(total_amount::NUMERIC(20, 2)) as sum_total_amount, zone_lookup."Zone"
		FROM ny_taxi
	LEFT JOIN zone_lookup 
		ON ny_taxi."PULocationID"=zone_lookup."LocationID"
	WHERE lpep_pickup_datetime::DATE='2019-10-18'
	GROUP BY "PULocationID", zone_lookup."Zone", lpep_pickup_datetime::DATE
)

SELECT * 
FROM sum_total_amount_for_day
WHERE sum_total_amount > 13000
;
```


Result: 
- "East Harlem North", "East Harlem South", "Morningside Heights"


## Question 6. Largest tip
For the passengers picked up in October 2019 in the zone named "East Harlem North" which was the drop off zone that had the largest tip?

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
	AND ny_taxi.lpep_pickup_datetime::DATE >= '2019-10-01'
	AND ny_taxi.lpep_pickup_datetime::DATE < '2019-11-01'
GROUP BY zdo."Zone"
ORDER BY max_tip_amount DESC
;
```

Solution:
"JFK Airport"	87.3


## Question 7. Terraform Workflow
Which of the following sequences, respectively, describes the workflow for:

    Downloading the provider plugins and setting up backend,
    Generating proposed changes and auto-executing the plan
    Remove all resources managed by terraform`

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