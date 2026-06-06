# Changelog — Gossipy Watchman

Todas as mudanças notáveis neste projeto estão documentadas aqui.
Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/).

---

## [1.0.0] — 2026-06-06

### Adicionado

#### Sprint 1 — Fundação do Backend e Banco de Dados
- `app/core/settings.py` — configurações centralizadas com pydantic-settings: `DATABASE_URL`, `STORAGE_VIDEOS`, `STORAGE_FACES`, `FACE_RECOGNITION_TOLERANCE` (0.6), `FRAMES_PER_SECOND_SAMPLE` (1), `APP_NAME`, `API_V1_PREFIX`
- `app/models/` — modelos SQLAlchemy: `Person` (tabela `people`), `Video` com `VideoStatus` Enum (tabela `videos`), `Appearance` com ForeignKeys (tabela `appearances`)
- `app/db/session.py` + `app/db/init_db.py` — engine SQLAlchemy, `get_db()` injetável via `Depends()`, `get_db_with_engine()` para testes, `init_db()` cria tabelas via `Base.metadata.create_all()`
- `app/main.py` — instância FastAPI com lifespan, CORS para `localhost:3000` e `localhost:5173`, mount de `/faces` como `StaticFiles`
- `app/api/v1/health.py` — `GET /api/v1/health` retorna `{"status": "ok", "app": "Gossipy Watchman"}`
- `pytest.ini` — `asyncio_mode = auto` para pytest-asyncio 0.23+

#### Sprint 2 — Core de Visão Computacional
- `app/schemas/video.py` — `VideoCreate`, `VideoResponse`, `VideoStatusResponse` com `from_attributes=True`
- `app/schemas/person.py` — `PersonResponse` com `from_attributes=True`
- `app/services/frame_service.py` — `extract_frames()`: amostragem configurável, `frame_interval = max(1, round(fps_real / fps_sample))`, `VideoCapture.release()` garantido via `finally`
- `app/services/face_service.py` — `extract_embeddings()` com conversão BGR→RGB antes do processamento; `find_matching_person()` via `face_recognition.face_distance()`, retorna match mais próximo abaixo do tolerance
- `app/services/person_service.py` — `get_all_embeddings()` carrega embeddings `.npy` por `person_id`; `save_new_person()` persiste `Person` + `.jpg` + `.npy` em `storage/faces/`
- `app/services/appearance_service.py` — `upsert_appearance()` com tolerância de gap de 2s; lógica de gap usa `timestamp_start` para `timestamp_end=None` (evita match incorreto de aparições antigas)
- `app/workers/video_worker.py` — `process_video()` orquestra pipeline completo: `extract_frames` → `extract_embeddings` → `find_matching_person` → `save_new_person` ou `upsert_appearance`; aceita `_engine` opcional para injeção em testes
- `app/services/__init__.py` — expõe `face_service`, `frame_service`, `person_service`, `appearance_service` como módulos

#### Sprint 3 — API REST Completa
- `app/services/video_service.py` — `create_video_record`, `get_video_by_id`, `list_videos` (paginação skip/limit, `uploaded_at DESC`), `update_video_status`, `update_file_path`
- `app/api/v1/upload.py` — `POST /api/v1/videos/upload`: valida `.mp4`/`.avi`, salva em chunks de 1 MB, registra no banco, dispara `process_video` como `BackgroundTask`, retorna HTTP 202
- `app/api/v1/videos.py` — `GET /api/v1/videos`, `GET /api/v1/videos/{id}`, `GET /api/v1/videos/{id}/status`; paginação via `Query`; HTTP 404 com mensagem em português
- `app/api/v1/people.py` — `GET /api/v1/people`, `GET /api/v1/people/{id}`, `PATCH /api/v1/people/{id}`; `PersonUpdate` rejeita string vazia via `field_validator` → HTTP 422
- `app/api/v1/timeline.py` — `GET /api/v1/people/{id}/timeline`: aparições com `file_name` do vídeo via JOIN, ordenadas por `video_id ASC`, `timestamp_start ASC`
- `app/schemas/appearance.py` — `AppearanceResponse` com `file_name`
- `app/schemas/person.py` + `PersonUpdate` — validação de nome não vazio
- `appearance_service.get_timeline()` — `AppearanceWithVideo` dataclass de projeção com JOIN explícito
- `tests/integration/conftest.py` — fixture `client` com `dependency_overrides[get_db]` e `StaticPool`

#### Sprint 4 — Frontend React
- `frontend/` — projeto Vite + React inicializado com Tailwind CSS 3, Lucide React, Axios, React Router DOM
- `frontend/tailwind.config.js` — design system Dark Mode OLED: primária `#3B82F6`, acento `#DC2626`, fundo `#0A0A0F`, fontes Fira Code + Fira Sans
- `frontend/src/services/api.js` — Axios `baseURL http://localhost:8000/api/v1`, timeout 30s, interceptor de erro extraindo `data.detail`
- `frontend/src/pages/Login.jsx` — autenticação local (admin/watchman), `sessionStorage`, toggle de senha, focus states, role alert
- `frontend/src/components/ProtectedRoute.jsx` — redireciona para `/` se sem token
- `frontend/src/router.jsx` — 5 rotas com lazy loading via `React.lazy` + `Suspense`
- `frontend/src/components/Layout.jsx` — sidebar fixa desktop + drawer mobile com overlay; `NavLink` com highlight ativo; botão Sair; transições 300ms; ícones Lucide
- `frontend/src/pages/Dashboard.jsx` — 4 cards de métricas, tabela 10 vídeos recentes com badges de status, auto-refresh 15s via `setInterval` com cleanup, skeleton loading
- `frontend/src/pages/Upload.jsx` — drag-and-drop, input alternativo, validação de extensão client-side, barra de progresso (`onUploadProgress`), spinner no botão, card de sucesso
- `frontend/src/pages/People.jsx` — galeria 3/2/1 colunas responsiva, busca client-side por nome, avatar com fallback `UserCircle`
- `frontend/src/pages/PersonDetail.jsx` — foto ampliada, nome editável inline via `PATCH`, validação não vazio, timeline em tabela com confiança (3 casas decimais)

### Alterado

- `app/db/session.py` — refatorado: `get_db()` sem parâmetro (compatível com `Depends()`); `get_db_with_engine()` separado para testes de integração
- `tests/integration/test_db.py` — atualizado para usar `get_db_with_engine` após refactor

### Infraestrutura

- Estrutura de diretórios canônica criada: `app/{api,core,db,models,schemas,services,workers}`, `tests/{unit,integration}`, `storage/{videos,faces}`, `changelog/`
- `requirements.txt` — dependências Sprint 1: FastAPI, Uvicorn, SQLAlchemy, Pydantic, pytest, pytest-asyncio, httpx
- `requirements.txt` — dependências Sprint 2: `opencv-python>=4.9.0`, `numpy>=1.26.0`, `face-recognition>=1.3.0`, `setuptools<71` (pin necessário: `face-recognition-models` usa `pkg_resources`, removido do setuptools≥71 — incompatível com Python 3.14)
- `pytest.ini` — `asyncio_mode = auto`
- Verificação Sprint 1: 27 testes passando
- Verificação Sprint 2: 64 testes passando
- Verificação Sprint 3: 95 testes passando
- Verificação Sprint 4: 95 testes passando, build de produção frontend 1.06s sem erros

---

*Fragmentos individuais disponíveis em `changelog/` para rastreabilidade por tarefa.*
