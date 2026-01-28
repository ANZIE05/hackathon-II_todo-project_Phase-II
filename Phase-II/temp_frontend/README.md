# Todo Application Frontend

This is the frontend for the Phase-II Todo Application built with Next.js, featuring JWT-based authentication, responsive design, and secure API integration.

## Features

- **Authentication**: Secure login and signup with JWT token management
- **Task Management**: Create, read, update, and delete tasks with priority and status tracking
- **Responsive Design**: Mobile-first design that works on all device sizes
- **Offline Capability**: Network error handling and offline status indicators
- **Accessibility**: WCAG 2.1 compliant with proper focus management and keyboard navigation

## Getting Started

First, install the dependencies:

```bash
npm install
```

Then, run the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the application.

## Environment Variables

Create a `.env.local` file in the frontend directory with the following variables:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_JWT_SECRET=your_jwt_secret_here
```

## Available Scripts

- `npm run dev`: Starts the development server
- `npm run build`: Builds the application for production
- `npm run start`: Starts the production server
- `npm run lint`: Runs the linter

## Architecture

- **Framework**: Next.js 14+ with App Router
- **Styling**: Tailwind CSS for utility-first styling
- **State Management**: React Context API for authentication state
- **API Integration**: Custom hooks for data fetching with error and loading states
- **Authentication**: JWT-based with secure token storage and expiration handling

## Security

- JWT tokens are stored securely and validated on both client and server
- All API requests include proper authentication headers
- Protected routes automatically redirect unauthenticated users
- Session expiration is handled gracefully with appropriate notifications

## Responsive Design

- Mobile-first approach with progressive enhancement
- Touch-friendly controls with appropriate sizing
- Flexible layouts that adapt to different screen sizes
- Optimized forms for mobile input

## Learn More

This project uses Next.js. Check out the following resources:

- [Next.js Documentation](https://nextjs.org/docs)
- [Learn Next.js](https://nextjs.org/learn)