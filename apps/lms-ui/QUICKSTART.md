# Quick Start Guide - Library Management System UI

## Prerequisites

- Node.js 20 or higher
- npm or yarn package manager
- Running LMS API backend (Port 5000)

## Installation & Setup

### 1. Navigate to the UI directory

```bash
cd apps/lms-ui
```

### 2. Install dependencies

```bash
npm install
```

### 3. Configure environment

Create a `.env.local` file in the `apps/lms-ui` directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:5000/api
```

### 4. Start the API Backend

Make sure your Flask JSON-RPC API is running:

```bash
# In a separate terminal
cd apps/lms-api
python run.py
```

The API should be running at `http://localhost:5000`

### 5. Start the Development Server

```bash
npm run dev
```

The UI will be available at `http://localhost:3000`

## First Steps

### 1. View the Dashboard
Open your browser to `http://localhost:3000` to see the dashboard with statistics and quick actions.

### 2. Add a Branch
1. Navigate to "Branches" in the sidebar
2. Click "Add Branch"
3. Fill in branch information (name, address, phone, email)
4. Click "Create Branch"

### 3. Add a Patron
1. Navigate to "Patrons" in the sidebar
2. Click "Add Patron"
3. Fill in patron information (name, email, select branch)
4. Click "Create Patron"

### 4. Add Catalog Items
1. Navigate to "Catalog" in the sidebar
2. Click "Add Item"
3. Fill in item details (title, author, ISBN, etc.)
4. Click "Create Item"

### 5. Check Out an Item
1. Navigate to "Circulation" in the sidebar
2. Click "Check Out Item"
3. Select a patron, enter copy ID, and select staff member
4. Click "Check Out"

## Production Build

To create a production-ready build:

```bash
npm run build
npm start
```

The production server will run at `http://localhost:3000`

## Troubleshooting

### API Connection Issues

If you see errors about API connection:
1. Verify the API is running at `http://localhost:5000`
2. Check the `.env.local` file has the correct `NEXT_PUBLIC_API_URL`
3. Ensure CORS is configured in the Flask API to allow requests from `http://localhost:3000`

### Build Errors

If the build fails:
1. Delete `.next` folder: `rm -rf .next`
2. Delete `node_modules`: `rm -rf node_modules`
3. Reinstall dependencies: `npm install`
4. Try building again: `npm run build`

### Port Already in Use

If port 3000 is already in use:
```bash
# Run on a different port
PORT=3001 npm run dev
```

## Development Tips

- **Hot Reload**: Changes to files will automatically reload in development mode
- **Type Checking**: TypeScript errors will show in your editor and terminal
- **Browser DevTools**: Use React DevTools for component inspection
- **Network Tab**: Monitor API calls in browser DevTools Network tab

## Available Pages

- `/` - Dashboard with statistics
- `/catalog` - Catalog item listing
- `/catalog/new` - Add new catalog item
- `/patrons` - Patron directory
- `/patrons/new` - Register new patron
- `/circulation` - Loans and holds overview
- `/circulation/checkout` - Check out items
- `/branches` - Branch directory
- `/staff` - Staff directory

## Common Tasks

### Adding New Features

1. Create Zod schema in `lib/schemas.ts`
2. Add API methods in `lib/api/`
3. Create page component in `app/`
4. Use existing UI components from `components/ui/`

### Styling Components

Use Tailwind CSS utility classes:
```tsx
<div className="flex items-center gap-4 rounded-lg bg-blue-50 p-4">
  <Button className="bg-blue-600 hover:bg-blue-700">
    Click Me
  </Button>
</div>
```

### Making API Calls

Use React Query hooks:
```tsx
const { data, isLoading, error } = useQuery({
  queryKey: ['patrons'],
  queryFn: patronsApi.list,
});
```

## Support

For issues or questions:
1. Check the `IMPLEMENTATION.md` for detailed documentation
2. Review the `README.md` for general information
3. Inspect browser console for errors
4. Check API backend logs for server-side issues

## Next Steps

- Explore all pages and features
- Customize the UI theme in `app/globals.css`
- Add more pages as needed
- Implement authentication
- Add advanced search and filtering
