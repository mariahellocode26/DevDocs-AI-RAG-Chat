from monitoring.db import get_connection


def get_total_requests():

    conn = get_connection()

    with conn.cursor() as cur:

        cur.execute(
            "SELECT COUNT(*) FROM requests"
        )

        total = cur.fetchone()[0]

    conn.close()

    return total