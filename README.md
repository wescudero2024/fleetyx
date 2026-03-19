# Transportation Management System (TMS)

A scalable, production-ready Transportation Management System backend built with Python, FastAPI, and Clean Architecture principles.

## 🏗️ Architecture

This system follows **Clean Architecture + Domain-Driven Design (DDD)**:

- **Domain** → Business rules and entities
- **Application** → Use cases and services  
- **Infrastructure** → Database, external APIs
- **Interfaces** → HTTP layer and API contracts

## 📁 Project Structure

```
/app
  /domain
    /entities          # Core business entities (Load, Carrier, Quote)
    /value_objects     # Value objects (Address, etc.)
    /interfaces        # Repository interfaces

  /application
    /use_cases         # Business use cases
    /services          # Application services

  /infrastructure
    /database          # SQLAlchemy models, repositories
    /external          # External API integrations

  /interfaces
    /api
      /routes          # FastAPI routes
      /schemas         # Pydantic schemas
    /dependencies      # FastAPI dependencies

main.py                # FastAPI application entry point
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- PostgreSQL
- Redis (optional, for caching)

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your database configuration
   ```

4. Initialize the database:
   ```bash
   python -m alembic upgrade head
   ```

5. Run the application:
   ```bash
   python main.py
   ```

The API will be available at `http://localhost:8000`

## 📚 API Documentation

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🔌 API Endpoints

### Loads
- `POST /loads` - Create load
- `GET /loads` - List loads (with filters)
- `GET /loads/{id}` - Get load details
- `PUT /loads/{id}` - Update load
- `PATCH /loads/{id}/status` - Update load status
- `POST /loads/{id}/assign` - Assign carrier
- `POST /loads/{id}/cancel` - Cancel load
- `GET /loads/kpis/dashboard` - Get dashboard KPIs

### Quotes
- `POST /quotes` - Create quote
- `GET /quotes?load_id=` - Get quotes for load
- `GET /quotes/{id}` - Get quote details
- `PUT /quotes/{id}` - Update quote
- `POST /quotes/{id}/select` - Select quote and assign carrier
- `DELETE /quotes/{id}` - Delete quote

### Carriers
- `POST /carriers` - Create carrier
- `GET /carriers` - List carriers (with search)
- `GET /carriers/{id}` - Get carrier details
- `PUT /carriers/{id}` - Update carrier
- `DELETE /carriers/{id}` - Delete carrier

### Tracking
- `POST /tracking/update` - Update tracking status
- `GET /tracking/{load_id}` - Get shipment timeline
- `GET /tracking/{load_id}/latest` - Get latest tracking
- `GET /tracking/{load_id}/status/{status}` - Get tracking by status

### Matching
- `POST /matching/invoice-contract` - Fuzzy match invoice vs contract names

## 🧪 Testing

Run tests with:
```bash
pytest
```

## 🔧 Configuration

Key environment variables:

- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `SECRET_KEY` - JWT secret key
- `ENVIRONMENT` - Development/production environment

## 📊 Features

- ✅ Clean Architecture with DDD
- ✅ Async/await support with FastAPI
- ✅ SQLAlchemy ORM with PostgreSQL
- ✅ Pydantic schemas for validation
- ✅ Comprehensive API documentation
- ✅ Error handling and logging
- ✅ Fuzzy string matching for invoice-contract matching
- ✅ Real-time tracking capabilities
- ✅ Scalable repository pattern

## 🎯 Frontend Integration

All API responses follow this consistent format:

```json
{
  "success": true,
  "data": {},
  "error": null
}
```

This makes it easy for frontend applications to handle responses consistently across all endpoints.

## 🚀 Production Deployment

For production deployment:

1. Set `ENVIRONMENT=production`
2. Use a proper database connection pool
3. Set up Redis for caching
4. Configure proper logging
5. Use a production-grade ASGI server like Gunicorn with Uvicorn workers

## 📝 License

This project is licensed under the MIT License.
