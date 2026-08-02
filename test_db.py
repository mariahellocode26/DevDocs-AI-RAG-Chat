from monitoring.db import get_connection


def main():
    conn = get_connection()

    cur = conn.cursor()

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
        VALUES (
            NOW(),
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
        """,
        (
            "What is authentication?",
            "Authentication uses API keys.",
            "gpt-5.4-mini",
            5,
            1.23,
            300,
            100,
            400,
            0.002,
        ),
    )

    conn.commit()

    print("Inserted successfully!")

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()