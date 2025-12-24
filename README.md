# TrainLLM - System Proof Dashboard

Self-healing AI with attestations, proof-gated governance, and supporting infrastructure.


This repository is a scaffold for the System Proof Dashboard (backend + frontend + Docker) implementing attestations, proof-gated governance, a simple Next.js frontend, and supporting infra to deploy locally or with Docker.

Repository structure

```
system-proof-dashboard-repo/
├─ .gitignore
├─ .env.example
├─ README.md
├─ docker-compose.yml
├─ Dockerfile
├─ backend/
│  ├─ package.json
│  ├─ tsconfig.json
│  └─ src/
│     ├─ types.ts
│     ├─ attestor.ts
│     └─ server.ts
└─ frontend/
   ├─ package.json
   └─ pages/
      ├─ index.tsx
      └─ api/governance.ts
```

Quickstart (local)

1. Copy env:

   cp .env.example .env

2. Backend: install and run

   cd backend && npm install
   npm run dev

3. Frontend: install and run

   cd frontend && npm install
   npm run dev

4. Visit the frontend: http://localhost:3000

Or run both with Docker Compose:

  docker-compose up -d --build

Endpoints

- Frontend: http://localhost:3000
- Backend API: http://localhost:4000
- Attestation: GET /api/attestation
- Governance: POST /api/governance/scale

Docker commands (examples)

```bash
# build locally
docker build -t system-proof-dashboard -f Dockerfile .
# run interactively
docker run -p 3000:3000 -p 4000:4000 --env-file .env system-proof-dashboard
```

Notes

- The attestor and governance in the backend are minimal demos; replace or extend attestation signing, RBAC, ZK proofs, and verification with production-grade implementations.
- The frontend includes a simple proxy API route to the backend at `/api/governance`.
- Customize `.env.example` for region or local override values (e.g., `REGION`, `NEXTPUBLICBACKEND_URL`).
---

## CI & Troubleshooting

A GitHub Actions workflow is included at `.github/workflows/ci.yml` that runs on push and pull requests to `main` and executes the root and backend tests plus the smoke script.

Troubleshooting checklist (common failing test scenarios):

1. "module not found" or "Cannot find module 'express'" errors
   - Ensure deps are installed: from repo root run `npm ci` and `cd backend && npm ci`.
   - If CI shows these errors, verify `package.json` and `package-lock.json` were checked in.

2. TypeScript "Cannot find name 'process'" or missing types
   - Ensure `@types/node` and relevant `@types/*` are installed (we added them as dev deps).
   - Run `npm ci` and re-run `npm test`.

3. Jest errors, tests timeout or cannot resolve `supertest`
   - Ensure backend devDeps include jest and supertest (we added them).
   - Run backend tests locally: `cd backend && npm test`.
   - If tests time out, run with `--runInBand`.

4. Smoke script reports "No attestation found"
   - Create an attestation: `npx ts-node attestor.ts` or start the backend and the endpoint will create a genesis attestation on first request.

5. Docker / Compose failures
   - Copy `.env.example` to `.env` and ensure variables are set, then `docker-compose up -d --build`.
   - Check container logs: `docker-compose logs backend`.

6. Lint / Type errors in CI
   - Run `npm run build` to reproduce TypeScript errors locally and fix the failed files.

If a CI job fails, paste the failing step output here and I will analyze the exact stack trace and propose the minimal code or dependency fix.
