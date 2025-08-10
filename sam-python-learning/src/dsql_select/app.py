import psycopg
import boto3
import json


def lambda_handler(event, context):
    region = 'ap-northeast-1'
    cluster_endpoint = 'xeabujrmkotnpo753srtuty27q.dsql.ap-northeast-1.on.aws'

    client = boto3.client('dsql', region_name=region)
    password_token = client.generate_db_connect_admin_auth_token(
        cluster_endpoint, region)

    # Make a connection to the cluster
    conn = psycopg.connect(
        dbname='postgres',
        user='admin',
        host=cluster_endpoint,
        password=password_token,
        sslmode='require',
        autocommit=True
    )

    cur = conn.cursor()

    cur.execute(
        """
        select count(*) from users
        """
    )
    row = cur.fetchone()
    print(f"Inserted row count: {row}")

    cur.execute(
        """
        select * from users
        """
    )
    row = cur.fetchall()
    print(f"Selected rows: {row}")

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Database selected successfully"})
    }
