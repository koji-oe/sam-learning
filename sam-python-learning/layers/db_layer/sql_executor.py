class SqlExecutor:
    def __init__(self, conn):
        self.conn = conn

    def execute(self, sql: str, params=None):
        with self.conn.cursor() as cur:
            cur.execute(sql, params or ())
            # return cur.fetchall()
