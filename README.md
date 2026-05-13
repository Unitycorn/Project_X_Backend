# FlowVid Backend

FlowVid Backend is a REST API built with Flask and SQLAlchemy, serving as the backbone for the FlowVid video platform. It handles user authentication, media uploads, and data persistence.

## Features

- User registration and login with custom-built JWT authentication
- Secure password handling via Fernet encryption
- Media upload and management via ImageKit
- RESTful API endpoints for users, videos, and channels
- CORS support for frontend integration
- Production-ready with Gunicorn

## Tech Stack

- Python · Flask · SQLAlchemy
- PyJWT · Cryptography (Fernet)
- ImageKit for media storage
- Gunicorn for deployment

## Requirements

- Python 3.10 or newer
- A running database (SQLite for development)
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
app.py                  Entry point
models/                 SQLAlchemy models
routes/                 Route handlers per resource
services/               Business logic (auth, upload)
utils/                  Helper functions
.env                    Environment variables (not committed)
requirements.txt        Python dependencies
```

## Frontend

The matching React frontend can be found here: [FlowVid Frontend](https://github.com/Unitycorn/Project_X_Frontend)
