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

```bash
python app.py
```

The application will start on `http://localhost:5000`

## Default Login Credentials

- **Username**: boss
- **Password**: @Hamza1234
- **Role**: admin

⚠️ **Change these credentials in production!**

## Project Structure

```
interview_intelligence_app/
├── app.py                 # Main Flask application
├── config.py              # Database configuration
├── requirements.txt       # Project dependencies
├── database/
│   ├── init_db.py        # Database initialization
│   ├── db.py             # Database connection utilities
│   └── models.sql        # SQL schema definitions
├── pages/                 # Legacy Streamlit pages (deprecated)
├── utils/
│   ├── auth_utils.py     # Authentication utilities
│   ├── tagging.py        # Question tagging utilities
│   └── duplicate.py      # Duplicate detection utilities
├── templates/            # HTML templates for Flask
│   ├── base.html         # Base template
│   ├── login.html        # Login page
│   ├── dashboard.html    # Main dashboard
│   ├── submit_interview.html
│   ├── question_bank.html
│   ├── admin_dashboard.html
│   └── error pages
└── data/                 # SQLite database (if using SQLite)
```

## Database

The application uses PostgreSQL (as configured in `config.py`)

### Tables

- **users**: User accounts with roles (admin/student)
- **interview_submissions**: Interview records with company, role, round, mode
- **questions**: Interview questions linked to submissions

## Key Improvements Over Streamlit Version

✅ **Framework**: Flask instead of Streamlit - more control and customization
✅ **Templates**: Proper HTML/CSS templates instead of script-based UI
✅ **Performance**: Optimized database queries
✅ **API Endpoints**: RESTful API endpoints for data access
✅ **Session Management**: Secure server-side session handling
✅ **Responsive Design**: Mobile-friendly UI
✅ **Better UX**: Professional interface with proper form validation

## API Endpoints

- `POST /login` - User authentication
- `GET/POST /submit-interview` - Submit interview details
- `GET /question-bank` - View questions by user
- `GET /api/submissions` - Get user submissions (JSON)
- `GET /api/questions/<submission_id>` - Get questions for a submission

## Development

Debug mode is enabled when `FLASK_ENV=development` is set.

```bash
# With debug/watch mode
python app.py
```

## Production Deployment

1. Set `FLASK_ENV=production`
2. Use a production WSGI server like Gunicorn:
   ```bash
   pip install gunicorn
   gunicorn -w 4 app:app
   ```
3. Use environment variables for sensitive data
4. Set up a reverse proxy (nginx) if needed

## Database Initialization

The database is automatically initialized when the app starts via `init_db()`. 

To reinitialize (WARNING: This deletes all data):
```python
from database.init_db import init_db
init_db()
```

## Troubleshooting

**DATABASE_URL not found error:**
- Ensure `.env` file exists in project root
- Check that `DATABASE_URL` is properly set

**Port 5000 already in use:**
```bash
# Use a different port
python -c "import os; os.environ['FLASK_PORT']='5001'; exec(open('app.py').read())"
```

**PostgreSQL connection errors:**
- Ensure PostgreSQL server is running
- Verify connection string format: `postgresql://user:password@host:port/database`

## License

This project is part of the Interview Intelligence System.

For questions or issues, please contact the development team.
