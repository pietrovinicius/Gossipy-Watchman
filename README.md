# Gossipy Watchman

Web-based video analysis system for identifying, cataloging, and tracking the temporal appearance of people via facial recognition — a technical portfolio project demonstrating asynchronous architecture, computer vision, and clean layer separation.

---

## System Screens

| Screen | Visual description |
|------|-----------------|
| **Login** | OLED black background, logo with red shield icon, username/password fields with visibility toggle, primary blue button |
| **Dashboard** | 4 metric cards (processed videos, queue, people, unknowns), table of the 10 most recent videos with color-coded status badges, auto-refresh every 15s |
| **Upload** | Drag-and-drop area with dashed border, animated progress bar during upload, success card with link to the Dashboard |
| **People** | 3-column responsive grid gallery, face thumbnail extracted by the pipeline, real-time name search field |
| **Person Detail** | Enlarged photo, inline-editable name with confirm/cancel, timeline table with video, start, end, and confidence for each appearance |

---

## Business Case — Use Scenarios

- **Restricted area access auditing**: automatically identifies which employees or visitors accessed ICU rooms, surgical centers, or pharmacies, with exact timestamps
- **Care compliance**: confirms the presence of qualified professionals during care, generating auditable evidence for regulatory bodies (ANS, CFM, ANVISA)
- **High-risk patient monitoring**: detects when patients with a history of elopement or fall risk appear in unauthorized areas and logs all events with timestamps

---

## Stack

| Layer | Technology |
|--------|-----------|
| **Backend** | Python 3.11+, FastAPI 0.111+, Uvicorn |
| **Frontend** | React 18, Vite, Tailwind CSS 3, Axios, React Router v6, Lucide React |
| **Database** | SQLite (dev) via SQLAlchemy 2.x |
| **Computer Vision** | OpenCV 4.9+, InsightFace 0.7+ (buffalo_l), ONNX Runtime 1.17+, NumPy 2.x |
| **Testing** | pytest 8, pytest-asyncio 0.23, httpx |

---

## Running Locally

### macOS / Linux

```bash
# Create and activate virtualenv
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env and fill in JWT_SECRET_KEY and ADMIN_PASSWORD_HASH using
# the commands documented in .env.example itself

# Create storage directories (if they don't exist)
mkdir -p storage/videos storage/faces storage/models

# Start the development server
uvicorn app.main:app --reload --workers 1 --host 0.0.0.0 --port 8000
```

---

### Windows 11

#### 1. Prerequisites

| Tool | Minimum version | Download |
|-----------|--------------|---------|
| Python | 3.11 | [python.org/downloads](https://www.python.org/downloads/) — **do NOT use the Microsoft Store version** |
| Node.js | 18 LTS | [nodejs.org](https://nodejs.org/) |
| ffmpeg | any | `winget install ffmpeg` or [ffmpeg.org/download.html](https://ffmpeg.org/download.html) — add to PATH |
| Git | any | [git-scm.com](https://git-scm.com/) |

> **Python warning:** During installation, check **"Add Python to PATH"**. Use the installer from [python.org](https://python.org), not the Microsoft Store — the Store version causes errors with C extensions (OpenCV, ONNX Runtime).

#### 2. Clone and set up the environment

Open **PowerShell** (or Terminal) in the folder where you want to install:

```powershell
git clone https://github.com/pietrovinicius/Gossipy-Watchman.git
cd "Gossipy-Watchman"

# Create and activate virtualenv
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

> If you get the error `Microsoft Visual C++ 14.0 is required`, install the [Build Tools for Visual Studio](https://visualstudio.microsoft.com/visual-cpp-build-tools/) with the **"C++ build tools"** workload before running pip.

#### 3. Configure environment variables

```powershell
copy .env.example .env
```

Open `.env` in any editor and configure the required fields:

```env
# Generate with: python -c "import secrets; print(secrets.token_hex(32))"
JWT_SECRET_KEY=PASTE-YOUR-KEY-HERE

# Generate with: python -c "from passlib.context import CryptContext; print(CryptContext(['bcrypt']).hash('watchman'))"
ADMIN_PASSWORD_HASH=PASTE-THE-HASH-HERE
```

Add the following Windows 16 GB RAM optimizations to the end of `.env`:

```env
# Windows optimizations
INSIGHTFACE_DET_SIZE=640
INSIGHTFACE_INTRA_OP_NUM_THREADS=4
INSIGHTFACE_PROVIDERS=["CPUExecutionProvider"]
```

#### 4. Create storage directories

```powershell
New-Item -ItemType Directory -Force -Path storage\videos, storage\faces, storage\models
```

#### 5. Verify ffmpeg

```powershell
ffmpeg -version
```

If the command isn't recognized, add the ffmpeg `bin/` directory to PATH:
`System Settings → Environment Variables → Path → New → C:\ffmpeg\bin`

#### 6. Start the backend

```powershell
# With the virtualenv active (venv\Scripts\activate)
uvicorn app.main:app --reload --workers 1 --host 0.0.0.0 --port 8000
```

> **`--workers 1` is mandatory on Windows.** Windows doesn't support `fork` — multiple workers cause a silent failure during ONNX Runtime initialization.

The API will be available at `http://localhost:8000`.
Swagger docs: `http://localhost:8000/docs`.

#### 7. Start the frontend

```powershell
cd frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:5173`.

#### 8. On first run

InsightFace automatically downloads the `buffalo_l` model (~200 MB) on the first video processing call. The download goes to `%USERPROFILE%\.insightface\models\buffalo_l\`. This may take a few minutes depending on your connection.

#### Common Windows troubleshooting

| Error | Cause | Solution |
|------|-------|---------|
| `PermissionError: [WinError 32] The process cannot access the file` | Windows keeps a handle open on a recently closed file | Wait and retry; the system already has automatic retry (safe_unlink) |
| `OnnxRuntimeError: No such file or directory` | buffalo_l model not yet downloaded | Check your connection; delete `%USERPROFILE%\.insightface\models\buffalo_l\` and let it download again |
| `uvicorn: error: unrecognized arguments: --workers` | Outdated uvicorn version | `pip install --upgrade uvicorn[standard]` |
| `Error loading shared library libmagic` | Leftover from a previous install | Ignore; python-magic was removed from requirements.txt (not used) |
| Port 8000 already in use | Another process on the port | `netstat -ano \| findstr :8000` to find the PID, then `taskkill /PID <number> /F` |

---

### Frontend (all platforms)

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:5173`.

**Login credentials (portfolio):** `admin` / `watchman`

### Tests

```bash
# From the project root, with virtualenv active
python -m pytest tests/unit/ -v
```

---

## Directory Structure

```
gossipy-watchman/
├── app/
│   ├── api/v1/          # FastAPI routers (health, upload, videos, people, timeline)
│   ├── core/            # settings.py — all configuration constants
│   ├── db/              # session.py, init_db.py
│   ├── models/          # Person, Video (VideoStatus Enum), Appearance
│   ├── schemas/         # Pydantic: VideoCreate/Response, PersonResponse/Update, AppearanceResponse
│   ├── services/        # Business logic: video, person, appearance, frame, face
│   ├── workers/         # video_worker.py — async CV pipeline
│   └── main.py          # FastAPI app, CORS, /faces StaticFiles
├── frontend/            # Vite + React
│   └── src/
│       ├── pages/       # Login, Dashboard, Upload, People, PersonDetail
│       ├── components/  # Layout, ProtectedRoute
│       └── services/    # api.js (Axios)
├── storage/
│   ├── videos/          # Videos uploaded by users
│   └── faces/           # Face crops (.jpg) and embeddings (.npy)
├── tests/
│   ├── unit/            # 7 unit test modules
│   └── integration/     # 5 integration test modules
├── changelog/           # Per-task changelog fragments (v0.01–v0.28)
├── CHANGELOG.md         # Consolidated history (generated at releases)
├── CLAUDE.md            # Operational guide for AI agents
└── requirements.txt
```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-----------|
| `GET` | `/api/v1/health` | Health check |
| `POST` | `/api/v1/videos/upload` | Video upload (multipart, HTTP 202, triggers background pipeline) |
| `GET` | `/api/v1/videos` | Paginated video listing (`?skip=0&limit=50`) |
| `GET` | `/api/v1/videos/{id}` | Video detail |
| `GET` | `/api/v1/videos/{id}/status` | Processing status (polling) |
| `GET` | `/api/v1/people` | Paginated listing of cataloged people |
| `GET` | `/api/v1/people/{id}` | Person detail |
| `PATCH` | `/api/v1/people/{id}` | Rename person (body: `{"name": "..."}`) |
| `GET` | `/api/v1/people/{id}/timeline` | Appearance timeline with the video's `file_name` |
| `GET` | `/faces/{person_id}.jpg` | Face image (static) |

---

## Relevant Architectural Decisions

**`FACE_RECOGNITION_TOLERANCE = 0.6` as a named constant**
Centralized in `app/core/settings.py`. Allows tuning without touching logic code — any engineer can find and adjust it in a single place.

**Embeddings as `.npy` per `person_id`**
Each person's embedding is saved at `storage/faces/{id}_embedding.npy`. Avoids storing 128-float vectors in the relational database; loading via `np.load` is O(1) per person.

**`AppearanceWithVideo` dataclass**
The `Appearance` ORM model doesn't carry `file_name` (a field of `Video`). Instead of a lazy relationship or a redundant column, `get_timeline()` performs an explicit JOIN and projects the result into a dataclass, keeping ORM models clean and the SQL auditable.

**`StaticPool` in integration test fixtures**
SQLite in-memory creates an isolated database per connection. Without `StaticPool`, the fixture and the endpoint see different databases. With `StaticPool`, a single connection is shared across all sessions of the same test engine.

**`setuptools<71` pinned in `requirements.txt`**
`face-recognition-models` imports `pkg_resources` (removed from setuptools ≥ 71). Python 3.14 doesn't ship `pkg_resources` in the stdlib. The pin guarantees compatibility without patching third-party code.

**Optional `_engine` in `process_video()`**
The worker creates its own engine (runs in a separate thread, outside the FastAPI request lifecycle). The `_engine` parameter allows injecting a test engine without monkey-patching `create_engine` — a safer, more explicit pattern.

**`get_db()` without parameters + `get_db_with_engine()`**
FastAPI's `Depends()` doesn't accept extra parameters on the injected function. Splitting the two functions allows clean `dependency_overrides` in integration tests without changing the production signature.

---

## Next Steps

1. **Real auth** — JWT on the backend (FastAPI + python-jose) + refresh token on the frontend
2. **WebSocket** — real-time processing progress without polling every 15s
3. **Adjustable threshold** — endpoint to change `FACE_RECOGNITION_TOLERANCE` at runtime via UI
4. **Video player** — display the video with temporal markers overlaid on appearances
5. **Export** — CSV/JSON timeline download endpoint for external analysis
6. **Docker** — `docker-compose.yml` to run backend + frontend with a single `docker compose up`
7. **CI/CD** — GitHub Actions running `pytest` + `npm run build` on every push to `main`

---

## License

MIT © 2026 Pietro Lima
