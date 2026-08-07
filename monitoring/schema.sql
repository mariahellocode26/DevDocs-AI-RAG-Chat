CREATE TABLE requests (

    id SERIAL PRIMARY KEY,

    timestamp TIMESTAMP NOT NULL,

    question TEXT NOT NULL,

    answer TEXT NOT NULL,

    model_name VARCHAR(100),

    top_k INTEGER,

    latency_seconds FLOAT,

    input_tokens INTEGER,

    output_tokens INTEGER,

    total_tokens INTEGER,

    estimated_cost NUMERIC(10, 6)

);


CREATE TABLE retrievals (

    id SERIAL PRIMARY KEY,

    request_id INTEGER REFERENCES requests(id),

    chunk_id VARCHAR(255),

    document_name VARCHAR(255),

    rank INTEGER

);


CREATE TABLE feedback (

    id SERIAL PRIMARY KEY,

    request_id INTEGER REFERENCES requests(id) UNIQUE,

    rating INTEGER,

    created_at TIMESTAMP DEFAULT NOW()

);