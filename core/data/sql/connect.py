import psycopg2


def connect(config):
    """ Create a database connection and return the connection object """
    try:
        conn = psycopg2.connect(
            user = config.DATABASE_USER,
            password = config.DATABASE_PASS,
            host = config.DATABASE_HOST,
            port = config.DATABASE_PORT,
            dbname = config.DATABASE_NAME
        )
        return conn
    except psycopg2.OperationalError as e:
        print(f"Error: {e}")
        return None
