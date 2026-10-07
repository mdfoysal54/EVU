# EVU AI Frontend

This is the frontend for the recovered EVU FastAPI backend.

## Stack

- Next.js App Router
- React
- TypeScript
- Plain CSS
- No UI framework
- No Tailwind dependency
- Browser `fetch()` for backend communication

## Backend contract used

The frontend is wired to the current backend routes:

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`
- `GET /health`
- `POST /api/v1/conversations`
- `GET /api/v1/conversations`
- `GET /api/v1/conversations/{id}`
- `POST /api/v1/conversations/{id}/stream`
- `GET /api/v1/documents`
- `POST /api/v1/documents/upload`
- `DELETE /api/v1/documents/{id}`
- `GET /api/v1/memory`
- `POST /api/v1/memory`
- `PATCH /api/v1/memory/{id}`
- `DELETE /api/v1/memory/{id}`
- `GET /api/v1/providers`
- `GET /api/v1/models/local`
- `POST /api/v1/web/search`

## Requirements

- Node.js 20.9+ recommended
- npm
- EVU backend running on `http://127.0.0.1:8000`

## Setup

```powershell
cd C:\coding\EVU
mkdir frontend
```

Copy this frontend into:

```text
C:\coding\EVU\frontend
```

Then:

```powershell
cd C:\coding\EVU\frontend
Copy-Item .env.example .env.local
npm install
npm run dev
```

Open:

```text
http://localhost:3000
```

## Environment

`.env.local`:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
NEXT_PUBLIC_APP_NAME=EVU
```

The backend already defaults to:

```text
FRONTEND_URL=http://localhost:3000
```

so this matches the frontend development URL.

## Authentication

The backend login endpoint expects OAuth2 form fields:

```text
username=<email>
password=<password>
```

The frontend handles this automatically.

The returned bearer token is stored in browser localStorage under:

```text
evu_access_token
```

The token is attached to authenticated API requests.

## Chat streaming

The chat page uses:

```text
POST /api/v1/conversations/{conversation_id}/stream
```

and parses the backend SSE format:

```text
data: {"delta":"..."}

data: {"done":true,...}

data: [DONE]
```

## Logo

No generated logo is included.

Add your own asset manually:

```text
public/logo/evu-logo.svg
```

You can later replace the `EVU` text mark in `components/AppShell.tsx` and the auth pages with your real logo.

## Production build

```powershell
npm run build
npm start
```

If the backend is deployed elsewhere, change:

```env
NEXT_PUBLIC_API_URL=https://your-backend.example.com
```

and set the backend:

```env
FRONTEND_URL=https://your-frontend.example.com
```

## Important

Do not replace the backend with this project.

This is a frontend-only project designed to sit on top of the recovered EVU backend.
