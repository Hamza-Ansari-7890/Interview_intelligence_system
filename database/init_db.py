from config import get_connection

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # Do NOT drop tables here to avoid accidental data loss.
    # The schema is created idempotently below.

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
    username VARCHAR(100),
    email VARCHAR(150) UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role VARCHAR(20) DEFAULT 'student',
    batch VARCHAR(50),
        registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    # Ensure a default admin exists (idempotent)
    cur.execute("""
    INSERT INTO users (username, password, role, email, batch)
    VALUES ('boss', '@Hamza1234', 'admin', 'hamzaansari@acciojob.com', 'master')
    ON CONFLICT (email) DO NOTHING;
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS interview_submissions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    company VARCHAR(150),
    role VARCHAR(150),
    interview_round VARCHAR(50),
    mode VARCHAR(20),
    experience_level VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS questions (
    id SERIAL PRIMARY KEY,
    submission_id INTEGER REFERENCES interview_submissions(id) ON DELETE CASCADE,
    question TEXT,
    topic VARCHAR(100),
    answered VARCHAR(10)
);
    """)


    conn.commit()
    conn.close()
