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
    last_max_id = None
    total_updated = 0

    while True:
        if last_max_id:
            cur.execute(
                """
                update users
                set password = 'newpassword'
                where id in (
                    select id from users
                    where id > %s
                    order by id
                    limit %s
                )
                returning id
                """,
                (last_max_id, batch_size)
            )
        else:
            # 初回はlast_max_idなし
            cur.execute(
                """
                update users
                set password = 'newpassword'
                where id in (
                    select id from users
                    order by id
                    limit %s
                )
                returning id
                """,
                (batch_size,)
            )
        updated_rows = cur.fetchall()
        if not updated_rows:
            break

        last_max_id = max(row[0] for row in updated_rows)
        total_updated += len(updated_rows)

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Database updated successfully"})
    }
