# Interview Intelligence System - Flask Version

A modern Flask-based interview preparation and analytics platform.

## Features

- **User Authentication**: Secure login system
- **Interview Submission**: Record interview details, questions, and topics
- **Question Bank**: Organize and search through past interview questions
- **Admin Dashboard**: Analytics and user management
- **Optimized Performance**: Efficient database queries and responsive UI

## Installation

1. **Clone/Navigate to project directory**
   ```bash
   cd interview_intelligence_app
   ```

2. **Create a virtual environment** (optional but recommended)
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   - Copy `.env.example` to `.env`
   - Update `DATABASE_URL` with your PostgreSQL connection string
   - Update `SECRET_KEY` with a strong secret key for production

   Example `.env`:
   ```
   SECRET_KEY=your-ultra-secret-key-here
   DATABASE_URL=postgresql://user:password@localhost:5432/interview_db
   FLASK_ENV=development
   ```

## Running the Application
# Interview Intelligence System

A Flask-based interview preparation and analytics app. This README provides safe, minimal setup instructions and an overview — no sensitive information is included here.

## Quick Start

1. Clone or open this repository and create a Python virtual environment (recommended).
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and provide your own values for secrets and the database connection. Do NOT commit `.env` to source control.
4. Run the application:
   ```bash
   python app.py
   ```

## Environment

- Place runtime configuration in a `.env` file. This file should contain at least `DATABASE_URL` and `SECRET_KEY`.
- Example entries are intentionally omitted for security. Use secure, unique values in production.

## Project Layout

Key files and folders:

- `app.py` — Flask application entrypoint and routes
- `config.py` — Database connection loader
- `database/` — DB initialization and schema utilities
- `templates/` — HTML templates used by Flask
- `utils/` — helper modules

## Database

The application expects a PostgreSQL database available via the `DATABASE_URL` environment variable. Run migrations or schema creation only if you control the target database.

## Security Notes

- Never store plaintext secrets or passwords in the repository.
- Use strong `SECRET_KEY` values for session security.
- Consider enabling password hashing (e.g., `bcrypt`) for user passwords.

## Troubleshooting

- If the app fails to connect, check that `DATABASE_URL` in your `.env` is correct and that the database service is reachable from this host.
- For local testing, ensure your virtual environment has the same Python version used in development.

## Contributing

If you want to contribute, open a PR with focused changes and avoid including any secrets or credentials.

---

For more detailed developer notes, consult the repository code and existing comments. If you'd like, I can add a secure admin-seeding mechanism that reads admin credentials from environment variables instead of hardcoding them in the codebase.
✅ **Framework**: Flask instead of Streamlit - more control and customization
