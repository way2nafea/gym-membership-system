# Gym Management System

A web-based gym management system built with Flask, MySQL, and Bootstrap.

## Features

- User registration and login
- Membership plans and purchases
- Admin dashboard with analytics
- User management
- Plan management
- Membership tracking

## Setup

1. Clone the repository
2. Create a virtual environment: `python -m venv .venv`
3. Activate the environment: `.venv\Scripts\activate` (Windows)
4. Install dependencies: `pip install -r requirements.txt`
5. Set up the database:
   - Create MySQL database
   - Run the SQL script in `database.sql`
6. Configure environment variables in `.env`
7. Run the app: `python app.py`

## Usage

- User login: /
- Admin login: /admin
- Default admin credentials: admin/admin123

## Security Notes

- Passwords are stored in plain text (for demo purposes)
- Use environment variables for sensitive data
- Implement password hashing in production