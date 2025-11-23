# Library Management System - UI

A modern, responsive web interface for the Library Management System built with Next.js, React, TypeScript, and Tailwind CSS.

## Features

- **Dashboard**: Overview of library statistics and quick actions
- **Catalog Management**: Add, edit, and manage library items (books, DVDs, magazines, etc.)
- **Patron Management**: Register and manage library members
- **Circulation**: Handle checkouts, returns, and holds
- **Branch Management**: Manage multiple library branches
- **Staff Management**: Manage library staff members

## Tech Stack

- **Framework**: Next.js 16 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS 4
- **State Management**: TanStack Query (React Query)
- **API Client**: Axios with JSON-RPC support
- **Validation**: Zod
- **Icons**: Lucide React

## Getting Started

### Prerequisites

- Node.js 20+ 
- npm or yarn
- Running LMS API server (see `apps/lms-api`)

### Installation

1. Install dependencies:

```bash
cd apps/lms-ui
npm install
```

2. Configure environment variables:

Create a `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:5000/api
```

3. Start the development server:

```bash
npm run dev
```

The application will be available at `http://localhost:3000`.

## API Integration

The UI communicates with the LMS API using JSON-RPC 2.0 protocol. The API client is located in `lib/api-client.ts` and provides a type-safe interface for all API endpoints.

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm start` - Start production server
- `npm run lint` - Run ESLint


## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
