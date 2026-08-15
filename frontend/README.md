# Frontend

React + TypeScript + Vite dashboard for the supply-chain ops demo.

## Setup

```bash
npm install
cp .env.example .env   # set VITE_API_BASE_URL to point at the backend
npm run dev
```

Requires the backend running (see [../backend/README.md](../backend/README.md))
— the dashboard has nothing to show without it.

## Routes

| Path | Shows |
|---|---|
| `/` | Overview: scenario runner, delivery summary, inventory, orders, recommendations |
| `/suppliers` | Supplier list (name, products, reliability, contact) |
| `/orders` | Orders table |
| `/deliveries` | Orders with delivery-focused columns (ETA, delay info) |
| `/inventory` | Inventory status table |
| `/risks` | At-risk/critical inventory + open recommendations |
| `/recommendations` | Full AI Operations Center (accept recommendations, accepted log) |

## Scripts

```bash
npm run dev       # dev server
npm run build     # typecheck + production build
npm run test      # vitest
npm run lint      # oxlint
npm run preview   # preview a production build
```

## Notes

- API calls go through `src/api/client.ts`, which requires `VITE_API_BASE_URL`
  to be set (build fails fast otherwise — see `apiClient.test.ts`).
- When built into the [root Dockerfile](../Dockerfile), the frontend is served
  as static files from the FastAPI backend on the same origin/port, so no
  `VITE_API_BASE_URL` configuration is needed at deploy time.
