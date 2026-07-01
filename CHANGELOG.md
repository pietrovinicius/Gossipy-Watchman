# Changelog — Gossipy Watchman

This is a summarized, English-language changelog highlighting major milestones.
For the full, detailed history (in Portuguese), see [CHANGELOG.pt-BR.md](CHANGELOG.pt-BR.md).

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [2.25.0] — 2026-07-01 — One-Click Dev Launcher

- Added `iniciar.bat` at project root: starts backend (`uvicorn --host 0.0.0.0 --port 8002`) and frontend (`npm run dev`) in separate windows with a double-click.
- Pre-flight checks for `venv`, `.env`, and `frontend/node_modules` with clear error messages if missing.

## [2.24.0] — 2026-07-01 — React Crash Mitigation

- Fixed an app-wide crash (React `insertBefore` `NotFoundError`) caused by browser translation extensions (e.g. Google Translate) mutating the DOM outside React's reconciliation cycle, typically triggered by rapid re-renders (upload progress bar).
- Root `<div id="root">` marked `translate="no"` / `notranslate` to stop the browser from touching the React-managed subtree.
- Added `errorElement` (`RouteError` component) to every route, replacing the blank dev-overlay screen with a friendly fallback + "Try again" reload button on unexpected errors.

## [2.23.0] — 2026-07-01 — LAN Access Fix

- Fixed hardcoded `http://localhost:8002` fallback in the frontend (`api.js`, `Login.jsx`, `VideoPlayer.jsx`) that made other machines on the network call their own `localhost` instead of the server — now resolved dynamically via `window.location.hostname`.
- Backend CORS now accepts any LAN IP on ports 5173/5174 via `allow_origin_regex`, instead of a single hardcoded IP.
- Documented the required `--host 0.0.0.0` flag for `uvicorn` (previously bound to loopback only) and Windows Firewall rules in `Anotacoes.txt`.

## [2.22.1]–[2.22.3] — 2026-07-01 — Port Conflict Resolution

- Backend port moved 8000 → 8001 → 8002, frontend 5173 → 5174, to avoid conflicts with other local apps (incl. a local Django instance on 8001).
- CORS and `Anotacoes.txt` updated to match the new ports at each step.
- Windows path test fix: `str()` → `.as_posix()` for platform-independent path assertions.

## [2.22.0] — 2026-06-10 — Sprint 17: Internationalization (EN / pt-BR)

- Full i18n migration via `react-i18next`: 392 translation keys across 15 pages/components, English as default with pt-BR fallback.
- Language toggle in the sidebar with `localStorage` persistence.
- Locale-aware date formatting (`DD/MM/YYYY HH:mm` for pt-BR, `M/D/YYYY h:mm AM/PM` for en).
- Critical fix: i18next v26 dropped the legacy `_plural` suffix in favor of `_other` — renamed globally across both translation catalogs.
- Docs: split changelog into a concise English `CHANGELOG.md` (recruiter-facing) and a full Portuguese history in `CHANGELOG.pt-BR.md` (renamed via `git mv`, no content loss).
- Chore: `.gitignore` now excludes local AI-agent config/state (`.agents/`, `.antigravitycli/`, `skills-lock.json`).

## [2.21.0] — 2026-06-09 — Windows 11 Compatibility & Memory Optimization

- Replaced hardcoded CoreML execution providers with configurable `INSIGHTFACE_PROVIDERS` (CPU-only on Windows).
- SQLite WAL mode for concurrent reads without blocking writes.
- `safe_unlink()` with automatic retry for Windows file-handle locks.
- Single-video processing semaphore + forced garbage collection to control RAM spikes (~1–2GB per InsightFace instance).
- Full "Windows 11" setup guide added to README.

## [2.00.0]–[2.20.0] — Surveillance UX & Video Player Overhaul

- Two-column split layout for video detail (sticky player + scrollable people cards).
- Presence bar with color-coded segments, clickable seek, and collapsible legend.
- Playback speeds up to 100x via `setInterval`-based override of browser limits.
- Clickable timeline timestamps with seek+pause and auto-scroll to person card.
- CCTV-oriented CSV export (20 columns, `;` delimiter for Excel/BR).
- Manual appearance creation, employee promotion flow, grid/table toggle for People.
- Multiple face-recognition pipeline fixes: track-based identity resolution, embedding normalization, complete-linkage clustering, multi-embedding merge handling.

## [1.95.0]–[1.99.0] — Sprint 16: Face Recognition Accuracy Overhaul

- Migrated from dlib/`face_recognition` to **InsightFace buffalo_l** (RetinaFace + ArcFace, 512-dim embeddings, cosine distance).
- Multi-face tracking via IoU association, pose filtering (yaw/pitch), and motion gating to skip static frames.
- k-NN voting for identity matching, multiple embeddings per person, automatic MP4 repair for moov-atom-less security camera recordings (HEVC/H.264).

## [1.6.4]–[1.8.7] — Sprints 8–15: Core Feature Buildout

- Watchlist alerts, face-similarity search, analytics dashboard (Recharts), light/dark theme.
- Advanced person profiles: face sample gallery, primary photo selection, profile quality scoring.
- Video detail page with timeline sync, video catalog with search/filters/pagination.
- Real-time HTTP range-request video streaming and player with timeline sync.
- Automatic format conversion (`.ts`/`.mkv`/`.mov`/`.dav` → `.mp4`), adaptive CNN parameters by video length.
- Soft delete & restore for people/videos, reprocessing, employee registration with face enrollment.

## [1.0.0]–[1.6.4] — Foundation: Backend, Frontend, Security

- FastAPI backend with SQLAlchemy models (`Person`, `Video`, `Appearance`), async video processing pipeline (frame extraction → face embeddings → matching/clustering).
- React + Vite + Tailwind frontend: Login, Dashboard, Upload, People, Person Detail.
- JWT authentication, upload validation (magic bytes, size limits, path traversal protection), security headers, person merge/categorization, CSV export, real-time WebSocket updates.

---

## Test Suite

- **Backend**: 525 pytest tests
- **Frontend**: 239 vitest tests (238 passing, 1 pre-existing unrelated failure)
