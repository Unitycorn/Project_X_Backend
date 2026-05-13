# FlowVid Backend

FlowVid Backend is a REST API built with Flask and SQLAlchemy, serving as the backbone for the FlowVid video platform. It handles user authentication, media uploads, and data persistence.

## Features

- User registration and login with custom-built JWT authentication
- Secure password handling via Fernet encryption
- Media upload and management via ImageKit
- RESTful API endpoints for users, videos, and channels
- CORS support for frontend integration
- CI pipeline via GitHub Actions
- Production-ready with Gunicorn

## Tech Stack

- Python · Flask · SQLAlchemy
- PostgreSQL hosted on NeonDB (serverless Postgres)
- PyJWT · Cryptography (Fernet)
- ImageKit for media storage
- GitHub Actions for CI
- Gunicorn for deployment

## Requirements

- Python 3.10 or newer
- A NeonDB (PostgreSQL) connection string, or any PostgreSQL-compatible database
- ImageKit account and API credentials

## Installation

```bash
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your_jwt_secret_key
FERNET_KEY=your_fernet_key
DATABASE_URL=your_neondb_postgres_connection_string
IMAGEKIT_PUBLIC_KEY=your_imagekit_public_key
IMAGEKIT_PRIVATE_KEY=your_imagekit_private_key
IMAGEKIT_URL_ENDPOINT=your_imagekit_url_endpoint
```

## Start Development

```bash
flask run
```

## Production

```bash
gunicorn app:app
```

## API Endpoints

| Method | Endpoint | Description | Auth required |
|--------|----------|-------------|---------------|
| POST | `/register` | Register a new user | No |
| POST | `/login` | Login and receive JWT | No |
| POST | `/upload` | Upload a video | Yes |
| GET | `/video/:id` | Get video details | No |
| GET | `/channel/:id` | Get channel details | No |

## Authentication

Authentication is custom-built without third-party auth libraries. On login, the API returns a signed JWT containing the user ID and a 24-hour expiry. Protected routes validate the token on every request.

## Project Structure

```text
app.py                          Entry point
data_manager/                   Business logic for channels and data handling
  channel_manager.py            Channel-specific operations
  data_manager.py               Core data access layer
  id_generator.py               ID generation utilities
data_models/
  models.py                     SQLAlchemy models
user_profiles/
  user_profiles.py              User profile logic and auth
.github/workflow/ci.yml         GitHub Actions CI pipeline
static/                         Static assets
templates/                      Flask templates
uploads/                        Local upload staging
.env                            Environment variables (not committed)
requirements.txt                Python dependencies
```

## Frontend

The matching React frontend can be found here: [FlowVid Frontend](https://github.com/Unitycorn/Project_X_Frontend)
