CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email TEXT unique not null,
    username TEXT,
    password TEXT not null,
    role TEXT default 'student', -- student / admin
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    batch TEXT
);

CREATE TABLE interview_submissions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    company VARCHAR(150),
    role VARCHAR(150),
    interview_round VARCHAR(50),
    mode VARCHAR(20),
    experience_level VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE questions (
    id SERIAL PRIMARY KEY,
    submission_id INTEGER REFERENCES interview_submissions(id) ON DELETE CASCADE,
    question TEXT,
    topic VARCHAR(100),
    answered VARCHAR(10)
);
