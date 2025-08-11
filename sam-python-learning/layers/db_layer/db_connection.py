import boto3
import psycopg


class DBConnection:
    def __init__(self, region: str, cluster_endpoint: str, dbname="postgres", user="admin"):
        self.region = region
        self.cluster_endpoint = cluster_endpoint
        self.dbname = dbname
        self.user = user
        self.conn = None

    def __enter__(self):
        client = boto3.client('dsql', region_name=self.region)
        password_token = client.generate_db_connect_admin_auth_token(
            self.cluster_endpoint, self.region
        )
        self.conn = psycopg.connect(
            dbname=self.dbname,
            user=self.user,
            host=self.cluster_endpoint,
            password=password_token,
            sslmode='require',
            autocommit=True
        )
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()
