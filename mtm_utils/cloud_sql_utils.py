import sqlalchemy
from shapely import to_wkb, from_wkb
from config import CSQL_UN, CSQL_PW, CSQL_DB, LOCAL_HOST, LOCAL_PORT


def connect_tcp_socket() -> sqlalchemy.engine.base.Engine:
    """Initializes a TCP connection pool for a Cloud SQL instance of Postgres."""
    # Note: Saving credentials in environment variables is convenient, but not
    # secure - consider a more secure solution such as
    db_host = LOCAL_HOST
    db_user = CSQL_UN
    db_pass = CSQL_PW
    db_name = CSQL_DB
    db_port = LOCAL_PORT

    pool = sqlalchemy.create_engine(
        # Equivalent URL:
        # postgresql+pg8000://<db_user>:<db_pass>@<db_host>:<db_port>/<db_name>
        sqlalchemy.engine.url.URL.create(
            drivername="postgresql+pg8000",
            username=db_user,
            password=db_pass,
            host=db_host,
            port=db_port,
            database=db_name,
        ),
    )
    return pool


def geom_convert_3d_to_2d(geom):
    if geom is None:
        return None
    # force output_dimension=2
    return from_wkb(to_wkb(geom, output_dimension=2))
