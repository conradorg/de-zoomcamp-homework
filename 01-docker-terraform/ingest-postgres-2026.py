from sqlalchemy import create_engine
import pandas as pd
import pyarrow.parquet as pq
from tqdm import tqdm

user = "postgres"
password = "postgres"
database_name = "ny_taxi"
host = "localhost"
port = "5433"
engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{database_name}')
engine.connect()
# print(pd.io.sql.get_schema(df, name='ny_taxi', con=engine))  # print schema which will be used for table when it is created


parquet_file = pq.ParquetFile("green_tripdata_2025-11.parquet")
print(parquet_file)

first = True
for batch in tqdm(parquet_file.iter_batches(batch_size=100000)):
    df = batch.to_pandas()
    print(df.head())
    # TODO do data type conversions HERE ...

    if first:
        df.to_sql(name='ny_taxi', con=engine, if_exists='replace', index=False)  # create table and add first data chunk 
        first = False
    else:
        df.to_sql(name='ny_taxi', con=engine, if_exists='append', index=False)  # append additional data


df_iter = pd.read_csv('taxi_zone_lookup.csv', iterator=True, chunksize=100000)
first = True
for df in tqdm(df_iter):
    # TODO do data type conversions HERE ...

    if first:
        df.to_sql(name='zone_lookup', con=engine, if_exists='replace', index=False)  # create table and add first data chunk 
        first = False
    else:
        df.to_sql(name='zone_lookup', con=engine, if_exists='append', index=False)  # append additional data


