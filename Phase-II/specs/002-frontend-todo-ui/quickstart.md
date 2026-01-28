# Quickstart Guide: Frontend UI for Phase-II Todo Application

## Prerequisites
- Node.js 18.x or higher
- npm or yarn package manager
- Access to backend API endpoints

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <repository-url>
cd <repository-name>
```

### 2. Navigate to Frontend Directory
```bash
cd frontend
```

### 3. Install Dependencies
```bash
npm install
# or
yarn install
```

### 4. Environment Configuration
Create a `.env.local` file in the frontend directory:
```env
NEXT_PUBLIC_API_BASE_URL=<backend-api-url>
NEXT_PUBLIC_JWT_SECRET=<jwt-secret-for-validation>
```

### 5. Run Development Server
```bash
npm run dev
# or
yarn dev
```

The application will be available at `http://localhost:3000`.

## Key Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run linter
- `npm run test` - Run tests

## Architecture Overview

### Folder Structure
- `app/` - Next.js App Router pages and layouts
- `components/` - Reusable React components organized by category
- `lib/` - Utility functions and shared logic
- `hooks/` - Custom React hooks for state management
- `services/` - API service implementations

### Key Technologies
- Next.js 14+ with App Router
- React 18+ with TypeScript
- Tailwind CSS for styling
- React Hook Form for form handling
- React Query for data fetching
- Zod for schema validation

## API Integration

The frontend communicates with the backend through REST API endpoints defined in the contract specifications. All requests must include a valid JWT token in the Authorization header.

Example API call:
```javascript
const response = await fetch('/api/tasks', {
  headers: {
    'Authorization': `Bearer ${jwtToken}`,
    'Content-Type': 'application/json'
  }
});
```

## Authentication Flow

1. User accesses `/login` or `/signup` pages
2. Credentials are sent to backend API
3. On successful authentication, JWT token is received and stored
4. Token is attached to all subsequent API requests
5. Protected routes are accessible only with valid JWT

## Running Tests

Unit tests:
```bash
npm run test:unit
```

Integration tests:
```bash
npm run test:integration
```

End-to-end tests:
```bash
npm run test:e2e
```

## Building for Production

```bash
npm run build
npm run start
```

## Troubleshooting

### Common Issues
- **Invalid token errors**: Ensure backend is running and JWT is properly configured
- **API connection failures**: Check that NEXT_PUBLIC_API_BASE_URL is set correctly
- **Styles not loading**: Verify Tailwind CSS is properly configured

### Development Tips
- Use the Next.js development server for hot reloading
- Leverage the React Developer Tools for debugging
- Check browser console for client-side errors
- Use network tab to inspect API requests