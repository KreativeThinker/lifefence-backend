# LifeFence Backend

This repository contains the backend for the LifeFence project, a geofencing-based faculty attendance management system. The backend is built using **Python** and **FastAPI**, leveraging **Supabase** as the database solution.

## Features

- **Geofencing API**: Determine when a faculty member enters or exits a geofenced zone.
- **Attendance Tracking**: Automate attendance marking based on real-time location data.
- **Authentication**: JWT-based user authentication and authorization.
- **Supabase Integration**: Seamless integration with the Supabase database for storing user data, attendance logs, and geofencing information.

## Installation

### Prerequisites

Ensure you have the following installed on your system:

- Python 3.12+
- Poetry (for dependency management)
- Supabase account & project setup
- Supabase CLI (for managing the database)

### Backend Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-org/lifefence-backend.git
   cd lifefence-backend
   ```

2. **Install Dependencies**
   Using Poetry to install required dependencies:
   ```bash
   poetry install
   ```

3. **Setup Environment Variables**

   Create a `.env` file in the root directory and add the following environment variables:
   ```env
   DATABASE_URL=<your-supabase-database-url>
   SUPABASE_API_KEY=<your-supabase-api-key>
   JWT_SECRET=<your-secret-key>
   ```

4. **Run Database Migrations**
   Use the Supabase CLI or direct SQL scripts to set up your database schema.

   If you're using Supabase CLI:
   ```bash
   supabase db push
   ```

5. **Start the Backend**
   Start the FastAPI development server:
   ```bash
   poetry run uvicorn app.main:app --reload
   ```

   The API will be available at `http://localhost:8000`.

### API Documentation

Once the server is running, you can access the interactive API documentation (Swagger UI) at:
```
http://localhost:8000/docs
```

### Running Tests

To run the test suite using `pytest` and `pytest-asyncio`, run:
```bash
poetry run pytest
```

### Supabase Configuration

- **Supabase** is used for data storage. Ensure your Supabase instance has the necessary schema and tables for the application (e.g., users, attendance logs, geofenced areas).
- More details on Supabase configuration and database schema will be found in the `docs/` directory.

## Project Structure

```
lifefence-backend/
├── app/
│   ├── api/                 # API routes
│   ├── models/              # Pydantic models and Tortoise ORM models
│   ├── services/            # Business logic (geofencing, attendance tracking)
│   ├── main.py              # FastAPI app entry point
├── tests/                   # Unit tests
├── .env.example             # Example environment variables file
├── pyproject.toml           # Poetry configuration
└── README.md                # This file
```

## Contributing

We welcome contributions! Please follow these steps for making contributions:

1. Fork the repository
2. Create a new branch for your feature or bugfix
3. Submit a pull request with a clear description of your changes

## License

This project is licensed under the MIT License. See the [LICENSE](../LICENSE) file for details.