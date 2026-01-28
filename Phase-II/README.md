# Todo Application Backend - Deployment Guide

## Deployment Options

### 1. Docker Deployment (Recommended)

#### Prerequisites
- Docker and Docker Compose installed
- Environment variables configured in `.env` file

#### Steps
1. Create your `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

2. Build and deploy using Docker Compose:
   ```bash
   docker-compose up -d --build
   ```

### 2. Manual Deployment

#### Prerequisites
- Python 3.9+
- PostgreSQL database
- Redis (optional, for token blacklisting and rate limiting)

#### Steps
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd todo-app-backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables in `.env` file

5. Run database migrations (if using Alembic):
   ```bash
   alembic upgrade head
   ```

6. Start the application:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

### 3. Automated Deployment

Use the provided deployment script:

```bash
# Deploy to production
./deploy/deploy.sh

# Deploy to staging
./deploy/deploy.sh --environment staging

# Deploy without running tests
./deploy/deploy.sh --skip-tests
```

## Environment Variables

Required environment variables:

- `NEON_DB_URL`: PostgreSQL database URL
- `BETTER_AUTH_SECRET`: Secret key for JWT signing (recommended: 32+ characters)
- `JWT_EXPIRATION_HOURS`: JWT token expiration in hours (default: 24)
- `ENVIRONMENT`: Environment (development, staging, production)
- `REDIS_URL`: Redis URL (optional, for advanced features)

## Health Checks

The application provides several health check endpoints:

- `GET /api/health` - Basic health check
- `GET /api/health/database` - Database connectivity check
- `GET /api/health/ready` - Readiness check
- `GET /api/health/live` - Liveness check
- `GET /monitoring/status` - Extended status information
- `GET /monitoring/health/extended` - Extended health check

## Monitoring

Monitor the application using the endpoints under `/monitoring`:

- `GET /monitoring/metrics` - System and application metrics
- `GET /monitoring/dependencies` - Status of external dependencies

## Backup and Maintenance

Regular backups can be performed using the backup script:

```bash
python scripts/backup.py --backup-dir ./backups --retention-days 7
```

## Security Considerations

- Always use HTTPS in production
- Set strong `BETTER_AUTH_SECRET` (32+ characters)
- Configure proper CORS settings
- Use environment-specific configurations
- Enable rate limiting in production
- Regular security updates

## Scaling

For production environments:
- Use a load balancer with multiple application instances
- Use Redis for distributed session management
- Monitor resource usage and scale accordingly
- Use external PostgreSQL database instead of local