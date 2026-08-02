from datetime import datetime

from monitoring.db import get_connection


def log_request(question, result, latency):

    conn = get_connection()

    with conn.cursor() as cur:

        cur.execute(
            """
            INSERT INTO requests (

                timestamp,
                question,
                answer,
                model_name,
                top_k,
                latency_seconds,
                input_tokens,
                output_tokens,
                total_tokens,
                estimated_cost

            )

            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)

            RETURNING id
            """,
            (
                datetime.now(),
                question,
                result["answer"],
                result["model"],
                result["top_k"],
                latency,
                result["usage"]["input_tokens"],
                result["usage"]["output_tokens"],
                result["usage"]["total_tokens"],
                result["cost_usd"],
            ),
        )

        request_id = cur.fetchone()[0]

        for rank, chunk in enumerate(result["sources"], start=1):

            cur.execute(
                """
                INSERT INTO retrievals (

                    request_id,
                    chunk_id,
                    document_name,
                    rank

                )

                VALUES (%s, %s, %s, %s)
                """,
                (
                    request_id,
                    chunk["id"],
                    chunk["filename"],
                    rank,
                ),
            )

    conn.commit()
    conn.close()