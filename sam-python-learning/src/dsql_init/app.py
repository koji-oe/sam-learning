import os
import json
from db_connection import DBConnection
from sql_executor import SqlExecutor


REGION = os.environ['REGION']
CLUSTER_ENDPOINT = os.environ['CLUSTER_ENDPOINT']


def lambda_handler(event, context):

    with DBConnection(REGION, CLUSTER_ENDPOINT) as conn:
        executor = SqlExecutor(conn)

        executor.execute(
            """
            drop table if exists users
            """)

        executor.execute(
            """
            create table if not exists users (
                id uuid not null default gen_random_uuid(),
                username varchar(50) not null,
                password varchar(255) not null,
                created_datetime timestamp default current_timestamp,
                primary key (id)
            )
            """)

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Database initialized successfully"})
    }
