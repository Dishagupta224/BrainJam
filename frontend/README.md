# BrainJam Frontend

Fresh React/Vite frontend for the Flask BrainJam app.

This folder is inspired by `frontend_demo` but is intentionally separate so the demo remains unchanged.

## Scripts

- `npm run dev` starts Vite.
- `npm run build` creates a production build.
- `npm run lint` runs ESLint.

## Environment

Create `.env` if your Flask API is not on the defaults:

```bash
VITE_API_BASE_URL=http://localhost:5000/api
VITE_WS_BASE_URL=ws://localhost:5000
```
