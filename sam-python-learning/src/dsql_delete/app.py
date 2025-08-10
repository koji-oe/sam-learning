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

    batch_size = 3000
    total_deleted = 0

    while True:
        cur.execute(
            """
            delete from users
            where id in (
                select id from users
                order by created_datetime
                limit %s
            )
            returning id
            """, (batch_size,)
        )
        deleted_rows = cur.fetchall()
        if not deleted_rows:
            break
        total_deleted += len(deleted_rows)
        print(
            f"Deleted {len(deleted_rows)} rows, total deleted: {total_deleted}")

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Database deleted successfully"})
    }
