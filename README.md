# Library Management System (LMS)

A modern, full-stack library management system built with Flask JSON-RPC API and Next.js UI in a monorepo architecture.

## 🚀 Overview

This project provides a complete solution for managing library operations including catalog management, patron registration, circulation (checkouts/returns), branch management, staff administration, and more.

### Architecture

- **Backend**: Flask-based JSON-RPC 2.0 API (`apps/lms-api`)
- **Frontend**: Next.js 16 with React 19 and TypeScript (`apps/lms-ui`)
- **Monorepo**: Organized structure with independent apps sharing common infrastructure

## 📦 Project Structure

```
flask-jsonrpc-sample/
├── apps/
│   ├── lms-api/          # Flask JSON-RPC API backend
│   │   ├── src/lms/      # Application source code
│   │   ├── migrations/   # Database migrations
│   │   └── README.md     # API documentation
│   └── lms-ui/           # Next.js frontend
│       ├── app/          # Next.js app router pages
│       ├── components/   # Reusable React components
│       ├── lib/          # API clients, schemas, utilities
│       └── README.md     # UI documentation
├── compose.yml           # Docker Compose configuration
└── README.md             # This file
```

## ✨ Features

### Core Modules

- **📚 Catalog Management**: Manage books, DVDs, magazines, and other library materials
- **👥 Patron Management**: Register and manage library members with card tracking
- **🔄 Circulation**: Handle checkouts, returns, renewals, and holds
- **🏢 Branch Management**: Manage multiple library locations
- **👔 Staff Management**: Administer library employees with role-based access
- **📦 Acquisitions**: Manage purchase orders and vendors
- **📰 Serials Management**: Track magazines, journals, and subscriptions
- **📊 Reports**: Generate statistics and usage reports
- **💰 Fines Management**: Track and manage patron fines

### Technical Features

- **JSON-RPC 2.0**: Standardized API communication protocol
- **Type-Safe**: Full TypeScript implementation with Zod validation
- **Modern UI**: Responsive design with Tailwind CSS
- **Real-time Updates**: React Query for efficient data synchronization
- **Modular Architecture**: Clean separation of concerns
- **Docker Support**: Easy deployment with Docker Compose

## 🛠️ Tech Stack

### Backend (lms-api)

- **Framework**: Flask 3.x
- **API**: Flask-JSONRPC
- **Database**: SQLAlchemy ORM (PostgreSQL/MySQL/SQLite)
- **Validation**: Pydantic/Marshmallow schemas
- **Architecture**: Clean Architecture (Entities, Repositories, Services)

### Frontend (lms-ui)

- **Framework**: Next.js 16 (App Router)
- **Language**: TypeScript with strict mode
- **Styling**: Tailwind CSS 4
- **State Management**: TanStack Query (React Query)
- **Validation**: Zod schemas
- **API Client**: Axios with JSON-RPC support
- **Icons**: Lucide React

## 🚦 Quick Start

### Prerequisites

- **Backend**: Python 3.10+, uv or pip
- **Frontend**: Node.js 20+, npm or yarn
- **Optional**: Docker & Docker Compose

### Option 1: Docker Compose (Recommended)

1. Clone the repository:

```bash
git clone <repository-url>
cd flask-jsonrpc-sample
```

2. Start all services:

```bash
docker-compose up --build
```

3. Access the applications:
   - **API**: http://localhost:5000/api
   - **UI**: http://localhost:3000

### Option 2: Manual Setup

#### Backend Setup

```bash
cd apps/lms-api

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .

# Run migrations
flask db upgrade

# Start the server
flask --app run run --debug
```

The API will be available at http://localhost:5000/api

#### Frontend Setup

```bash
cd apps/lms-ui

# Install dependencies
npm install

# Configure environment
cp .env.example .env.local
# Edit .env.local and set NEXT_PUBLIC_API_URL=http://localhost:5000/api

# Start development server
npm run dev
```

The UI will be available at http://localhost:3000

## 📖 API Documentation

The API follows JSON-RPC 2.0 specification. Key namespaces:

### Organizations
- `Branches.*` - Branch management (list, get, create, update, delete)
- `Staff.*` - Staff management

### Patrons
- `Patrons.*` - Patron management

### Catalog
- `Items.*` - Bibliographic items (books, DVDs, etc.)
- `Copies.*` - Physical copies of items

### Circulation
- `Loans.*` - Checkout/checkin/renewal operations
- `Holds.*` - Reservation management

### Acquisitions
- `Vendors.*` - Vendor management
- `AcquisitionOrders.*` - Purchase order management

### Serials
- `Serials.*` - Serial publication management
- `SerialIssues.*` - Individual issue tracking

For detailed API documentation, see [apps/lms-api/README.md](./apps/lms-api/README.md)

## 🎨 UI Pages

- **Dashboard** (`/`) - Library statistics and quick actions
- **Catalog** (`/catalog`) - Browse and manage items
- **Patrons** (`/patrons`) - Member management
- **Circulation** (`/circulation`) - Loans and holds
- **Branches** (`/branches`) - Location management
- **Staff** (`/staff`) - Employee directory

For UI documentation, see [apps/lms-ui/README.md](./apps/lms-ui/README.md)

## 🧪 Development

### Backend Development

```bash
cd apps/lms-api

# Run tests
pytest

# Format code
black src/

# Lint code
flake8 src/

# Type checking
mypy src/
```

### Frontend Development

```bash
cd apps/lms-ui

# Run in development mode
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Run linting
npm run lint

# Type checking
npx tsc --noEmit
```

## 🐳 Docker Support

### Build and run with Docker Compose:

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Individual container builds:

```bash
# Backend only
docker build -f apps/lms-api/Dockerfile -t lms-api .
docker run -p 5000:5000 lms-api

# Frontend only
docker build -f apps/lms-ui/Dockerfile -t lms-ui .
docker run -p 3000:3000 lms-ui
```

## 📝 Environment Variables

### Backend (.env)

```env
DATABASE_URL=sqlite:///lms.db
SECRET_KEY=your-secret-key
DEBUG=True
FLASK_APP=run
```

### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:5000/api
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please read [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md) for details on our code of conduct.

## 📄 License

This project is licensed under the terms specified in [LICENSE.txt](./LICENSE.txt).

## 👥 Authors

See [AUTHORS](./AUTHORS) for the list of contributors.

## 🔗 Links

- **API Documentation**: [apps/lms-api/README.md](./apps/lms-api/README.md)
- **UI Documentation**: [apps/lms-ui/README.md](./apps/lms-ui/README.md)
- **Implementation Guide**: [apps/lms-ui/IMPLEMENTATION.md](./apps/lms-ui/IMPLEMENTATION.md)
- **Quick Start Guide**: [apps/lms-ui/QUICKSTART.md](./apps/lms-ui/QUICKSTART.md)

## 🆘 Support

For issues, questions, or contributions, please open an issue on the repository.

---

**Built with ❤️ using Flask, Next.js, and modern web technologies**
