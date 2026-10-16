# Tandem frontend

The happy-path clothing marketplace demo: a menswear buyer selects Casual and Athletic, chooses three lounge looks, answers a short context chat, and compares five bundles. The seller reviews the selected bundle and accepts; the buyer confirms.

## Run

From this folder, with Node.js 22.12 or newer:

```sh
npm ci
npm run dev
```

Open `?role=buyer` and `?role=seller` in two tabs or windows of the same browser, origin, and profile. **Reset demo** clears both workspaces. Default buyer preferences are Los Angeles, medium tops and bottoms, relaxed fit, and a $200 budget. The recommended bundle is $149; other offers expose price, size, and style tradeoffs.

## Deploy on Vercel

Set the Vercel project's **Root Directory** to `frontend`, use the Vite preset, build with `npm run build`, and serve `dist`. This folder's `vercel.json` contains the standalone frontend configuration. The repository's existing root configuration and backend files are unchanged.

The optional `deployment/vercel.integrated.json` is a future combined-deployment template; it is not active and does not replace the root configuration.

## Demo boundaries

Agent activity and bundle scores are simulated. Shared browser storage and BroadcastChannel synchronize the two workspaces. There is no authentication, payment, shipment, or live calendar/email/weather connection. Catalog prices, tags, and stock are demo data; product photography is illustrative. See `ASSET-CREDITS.md` for sources.

