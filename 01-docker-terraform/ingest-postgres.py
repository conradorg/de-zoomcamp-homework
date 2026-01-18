from sqlalchemy import create_engine
import pandas as pd

user = "postgres"
password = "postgres"
database_name = "ny_taxi"
host = "localhost"
port = "5433"
engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{database_name}')
engine.connect()
# print(pd.io.sql.get_schema(df, name='ny_taxi', con=engine))  # print schema which will be used for table when it is created


# df = pd.read_csv('green_tripdata_2019-10.csv', nrows=10)
# print(df)
# print(df.head(n=0).to_sql(name='ny_taxi', con=engine, if_exists='replace'))  # create empty table but then you need to add data of this chunk separately

df_iter = pd.read_csv('green_tripdata_2019-10.csv', iterator=True, chunksize=100000, parse_dates=[1,2])
first = True
for df in df_iter:
    # TODO do data type conversions HERE ...

    if first:
        df.to_sql(name='ny_taxi', con=engine, if_exists='replace', index=False)  # create table and add first data chunk 
        first = False
    else:
        df.to_sql(name='ny_taxi', con=engine, if_exists='append', index=False)  # append additional data


df_iter = pd.read_csv('taxi_zone_lookup.csv', iterator=True, chunksize=100000)
first = True
for df in df_iter:
    # TODO do data type conversions HERE ...

    if first:
        df.to_sql(name='zone_lookup', con=engine, if_exists='replace', index=False)  # create table and add first data chunk 
        first = False
    else:
        df.to_sql(name='zone_lookup', con=engine, if_exists='append', index=False)  # append additional data


