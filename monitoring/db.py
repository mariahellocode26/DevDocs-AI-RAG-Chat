import psycopg2


def get_connection():
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="devdocs",
        user="postgres",
        password="postgres",
    )

    return conn