from monitoring.db import get_connection


def get_total_requests():

    conn = get_connection()

    with conn.cursor() as cur:

        cur.execute(
            """
            SELECT COUNT(*)
            FROM requests
            """
        )

        total = cur.fetchone()[0]

    conn.close()

    return total


def get_average_latency():

    conn = get_connection()

    with conn.cursor() as cur:

        cur.execute(
            """
            SELECT AVG(latency_seconds)
            FROM requests
            """
        )

        avg = cur.fetchone()[0]

    conn.close()

    return round(avg or 0, 2)


def get_total_cost():

    conn = get_connection()

    with conn.cursor() as cur:

        cur.execute(
            """
            SELECT SUM(estimated_cost)
            FROM requests
            """
        )

        total = cur.fetchone()[0]

    conn.close()

    return round(total or 0, 6)


def get_total_tokens():

    conn = get_connection()

    with conn.cursor() as cur:

        cur.execute(
            """
            SELECT SUM(total_tokens)
            FROM requests
            """
        )

        total = cur.fetchone()[0]

    conn.close()

    return total or 0


def get_requests_over_time():

    conn = get_connection()

    with conn.cursor() as cur:

        cur.execute(
            """
            SELECT
                DATE(timestamp) AS day,
                COUNT(*) AS requests
            FROM requests
            GROUP BY day
            ORDER BY day
            """
        )

        rows = cur.fetchall()

    conn.close()

    return rows



def get_latency_over_time():

    conn = get_connection()

    with conn.cursor() as cur:

        cur.execute(
            """
            SELECT
                DATE(timestamp) AS day,
                AVG(latency_seconds) AS avg_latency
            FROM requests
            GROUP BY day
            ORDER BY day
            """
        )

        rows = cur.fetchall()

    conn.close()

    return rows



def get_cost_over_time():

    conn = get_connection()

    with conn.cursor() as cur:

        cur.execute(
            """
            SELECT
                DATE(timestamp) AS day,
                SUM(estimated_cost) AS cost
            FROM requests
            GROUP BY day
            ORDER BY day
            """
        )

        rows = cur.fetchall()

    conn.close()

    return rows


def get_top_documents(limit=5):

    conn = get_connection()

    with conn.cursor() as cur:

        cur.execute(
            """
            SELECT
                document_name,
                COUNT(*) AS retrieval_count
            FROM retrievals
            GROUP BY document_name
            ORDER BY retrieval_count DESC
            LIMIT %s
            """,
            (limit,),
        )

        rows = cur.fetchall()

    conn.close()

    return rows


def get_average_retrieved_chunks():

    conn = get_connection()

    with conn.cursor() as cur:

        cur.execute(
            """
            SELECT AVG(chunk_count)
            FROM (
                SELECT
                    request_id,
                    COUNT(*) AS chunk_count
                FROM retrievals
                GROUP BY request_id
            ) t
            """
        )

        avg = cur.fetchone()[0]

    conn.close()

    return round(avg or 0, 2)

def get_tokens_over_time():

    conn = get_connection()

    with conn.cursor() as cur:

        cur.execute(
            """
            SELECT
                DATE(timestamp) AS day,
                SUM(total_tokens) AS tokens
            FROM requests
            GROUP BY day
            ORDER BY day
            """
        )

        rows = cur.fetchall()

    conn.close()

    return rows

def get_feedback_counts():

    conn = get_connection()

    with conn.cursor() as cur:

        cur.execute(
            """
            SELECT
                rating,
                COUNT(*)
            FROM feedback
            GROUP BY rating
            """
        )

        rows = cur.fetchall()

    conn.close()

    return rows



def get_feedback_rate():

    conn = get_connection()

    with conn.cursor() as cur:

        cur.execute(
            """
            SELECT

                COUNT(*) FILTER (WHERE rating = 1),
                COUNT(*) FILTER (WHERE rating = -1)

            FROM feedback
            """
        )

        positive, negative = cur.fetchone()

    conn.close()

    total = positive + negative

    if total == 0:

        return 0

    return round(positive / total * 100, 1)