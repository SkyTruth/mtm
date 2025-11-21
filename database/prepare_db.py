import sqlalchemy
from mtm_utils.cloud_sql_utils import connect_tcp_socket


def add_postgis():
    engine = connect_tcp_socket()

    # Example table schema
    create_stmt = """
    CREATE EXTENSION IF NOT EXISTS postgis
    """

    with engine.connect() as conn:
        conn.execute(sqlalchemy.text(create_stmt))
        conn.commit()
        print("postgis extension added.")

if __name__ == "__main__":
    add_postgis()