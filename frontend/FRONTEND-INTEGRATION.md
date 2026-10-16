# Frontend integration

This workspace contains the TANDEM Vite/React frontend. Buyer, seller, and A2A services remain outside its implementation. The frontend currently completes the demo through seeded bundles and a shared same-browser session.

## Deployment configurations

| File | Intended use |
| --- | --- |
| `vercel.json` | Standalone frontend checkout: `npm run build`, output `dist/`, no Python function declaration. |
| `deployment/vercel.integrated.json` | Template for the combined repository when `api/index.py` and its backend dependencies are present. |

For a future combined deployment, merge the template into the repository's root `vercel.json`. It installs and builds the app from `frontend/` and serves `frontend/dist/`. Vercel will not automatically read the nested template. Keep any additional backend settings required by that repository. The current frontend addition does not change that existing root configuration.

The template retains the existing `/api/(.*)` → `/api/index` rewrite and `api/index.py` maximum duration of 300 seconds. It adds the Vite build/output settings and a frontend fallback that excludes `/api`, `/assets/`, `/images/`, and the favicon. API requests must reach the backend rather than return frontend HTML. Do not use this template as the standalone checkout's root configuration while the Python function is absent.

Configuration fields and negative-lookahead rewrite syntax follow [Vercel's configuration documentation](https://vercel.com/docs/project-configuration/vercel-json). The combined application has not been built or deployed here; API behavior and hosted function availability still require verification in that repository.

## Connection points

- `src/catalog.ts` owns the seeded inventory, profile defaults, bundle types, and simulated bundle scoring.
- `src/store.ts` owns the shared session and local browser synchronization.
- `src/main.tsx` owns onboarding, the simulated exchange, bundle selection, seller acceptance, and final buyer confirmation.

Replace simulated bundle generation and progress with the team's service responses when the backend contract is ready. Keep the explicit sequence: buyer selection → seller acceptance → buyer confirmation. Store and validate the selected bundle and agreed total consistently on both sides.

The current store only synchronizes tabs/windows sharing the same browser profile and origin. A backend integration will need a shared session identifier and server updates for separate devices or browser profiles. Preset role buttons provide no authenticated identity.
