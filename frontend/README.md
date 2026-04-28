# Frontend — Enterprise RAG Document Assistant

React + TypeScript + Vite + Tailwind CSS dashboard.

## Quick Start

```bash
# Install dependencies
npm install

# Copy environment (optional — defaults to localhost:8000)
cp .env.example .env.local

# Start development server
npm run dev
```

Opens at: http://localhost:5173

Backend must be running at http://localhost:8000.

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `VITE_API_URL` | `http://localhost:8000` | Backend API base URL |

## Build for Production

```bash
npm run build      # Outputs to dist/
npm run preview    # Preview production build
```

## Project Structure

```
src/
├── components/
│   ├── Layout.tsx            # App shell with sidebar navigation
│   ├── UploadPanel.tsx       # Drag-and-drop PDF upload
│   ├── DocumentList.tsx      # Document table with status badges
│   ├── ChatPanel.tsx         # Chat interface with citations
│   ├── CitationCard.tsx      # Collapsible source citation
│   └── EvaluationDashboard.tsx  # Metrics and per-question results
├── pages/
│   ├── Dashboard.tsx         # Main page: upload + documents + chat
│   └── Evaluation.tsx        # Evaluation runner page
├── services/
│   └── api.ts                # All HTTP calls to backend
└── types/
    └── index.ts              # TypeScript interfaces
```
