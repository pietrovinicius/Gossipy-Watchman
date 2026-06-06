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

## [1.1.0] — 2026-06-06

### Adicionado

#### Sprint 5 — Hardening de Segurança

- `app/services/auth_service.py` — JWT com `python-jose`: `create_access_token()`, `verify_token()`, `verify_password()` / `hash_password()` via `bcrypt`, `get_current_user()` injetável via `Depends(oauth2_scheme)`
- `app/api/v1/auth.py` — `POST /api/v1/auth/login`: valida credenciais contra `settings.ADMIN_USERNAME` e `ADMIN_PASSWORD_HASH`; fallback `"watchman"` com `logger.warning` quando hash não configurado; retorna JWT Bearer
- `app/api/v1/faces.py` — `GET /api/v1/faces/{filename}`: requer JWT, valida que `filename` não contém `..`/`/`/`\\`, confinamento via `resolve().relative_to()`, `FileResponse` com `media_type="image/jpeg"`, HTTP 400 em violação, HTTP 404 se ausente
- `.env.example` — template com todas as variáveis documentadas; comandos de geração de `JWT_SECRET_KEY` e `ADMIN_PASSWORD_HASH` inline
- `tests/integration/test_auth.py` — 6 testes: login válido, senha errada (401), endpoints sem token (401), token inválido (401), `/health` público (200)
- `tests/integration/test_upload_security.py` — 7 testes: path traversal → UUID, magic bytes MP4/AVI corretos (202), texto mascarado como MP4 (415), upload acima do limite (413), arquivo parcial deletado
- `tests/integration/test_faces.py` — 5 testes: sem token (401), path traversal (400), inexistente (404), arquivo válido (200), percent-encoded traversal (400/404)
- `tests/integration/test_security_headers.py` — 5 testes: um por header (`X-Content-Type-Options`, `X-Frame-Options`, `X-XSS-Protection`, `Referrer-Policy`, `Content-Security-Policy`)
- `requirements.txt` — `python-jose[cryptography]`, `passlib[bcrypt]`, `python-magic`, `python-dotenv`

### Alterado

#### Sprint 5 — Hardening de Segurança

- `app/core/settings.py` — reescrito com `SettingsConfigDict(env_file=".env")`; novas constantes: `JWT_SECRET_KEY` (fallback para testes), `JWT_ALGORITHM`, `JWT_EXPIRE_MINUTES`, `ADMIN_USERNAME`, `ADMIN_PASSWORD_HASH`, `MAX_UPLOAD_SIZE_MB`, `MAX_UPLOAD_SIZE_BYTES` (calculado via `@model_validator`), `DOCS_ENABLED`
- `app/main.py` — `StaticFiles /faces` removido; `docs_url`/`redoc_url` condicionais via `DOCS_ENABLED`; `security_headers_middleware` adicionado (5 headers); router `faces_router` e `auth_router` incluídos
- `app/api/v1/upload.py` — 3 correções críticas: (1) nome em disco = `uuid4().hex + ext` (elimina path traversal); (2) primeiros 12 bytes validados como magic bytes antes de gravar (MP4: `bytes[4:8]==b'ftyp'`; AVI: `bytes[0:4]==b'RIFF'` e `bytes[8:12]==b'AVI '`), HTTP 415 em falha; (3) acúmulo de bytes durante leitura, arquivo parcial deletado ao exceder `MAX_UPLOAD_SIZE_BYTES`, HTTP 413
- `app/api/v1/videos.py`, `people.py`, `timeline.py` — `Depends(get_current_user)` adicionado em todos os endpoints
- `tests/integration/conftest.py` — fixtures `auth_token` e `auth_headers` adicionados
- `tests/integration/test_upload.py`, `test_videos.py`, `test_people.py`, `test_timeline.py` — `auth_headers` adicionado em todas as chamadas autenticadas; conteúdo de upload atualizado para magic bytes reais
- `frontend/src/services/api.js` — interceptor de request envia `Authorization: Bearer {token}` automaticamente
- `frontend/src/pages/Login.jsx` — autenticação real via `POST /api/v1/auth/login`; token JWT salvo em `sessionStorage`
- `frontend/src/pages/People.jsx` + `PersonDetail.jsx` — `FACES_BASE` atualizado para `/api/v1/faces`
- `.gitignore` — entradas `storage/videos/*`, `storage/faces/*`, `*.db`, `frontend/node_modules/`, `frontend/dist/` adicionadas

### Infraestrutura

- `Documentos/Cronograma de Sprints - Gossipy Watchman.docx` — Sprint 5 adicionada com objetivo e 8 itens de hardening
- Verificação Sprint 5: 125 testes passando, build frontend 506ms sem erros

---

## [1.2.0] — 2026-06-06

### Adicionado

#### Sprint 6 — Gestão de Pessoas

**Backend**
- `app/models/person.py` — `PersonCategory` enum Python (Funcionário, Visitante, Desconhecido, Monitorado); colunas `notes` (TEXT NULL) e `category` (VARCHAR(20) NOT NULL DEFAULT 'Desconhecido') no modelo `Person`
- `app/db/migrations/migration_v1_13.py` — migração idempotente via `pragma_table_info`; adiciona `notes` e `category` sem recriar tabela; executada no lifespan antes de `init_db()`
- `app/services/person_service.py` — `update_person_details(db, person_id, name, notes, category)`: atualiza apenas campos não-None; `get_person_stats(db, person_id)`: retorna `video_count`, `total_seconds`, `first_seen`, `last_seen` a partir de `appearances` + JOIN em `videos`; `merge_people(db, primary_id, secondary_ids)`: reassocia appearances do secundário para o primário, deleta `.npy` e `.jpg` do secundário, exclui `Person` secundário, HTTP 400 para self-merge, HTTP 404 para IDs inexistentes
- `app/schemas/person.py` — `PersonCategory` como `str, Enum`; `PersonUpdate` com todos os campos opcionais + `@model_validator` exigindo ao menos um campo; `PersonStatsResponse` (video_count, total_seconds, first_seen, last_seen); `MergeRequest` com validação de secondary_ids não vazio e não contendo primary_id
- `app/api/v1/people.py` — `POST /people/merge` registrado **antes** de `GET /people/{id}` (evita colisão de rota FastAPI com literal "merge"); `GET /people/{id}/stats`; `PATCH /people/{id}` usa `update_person_details` (parcial)

**Frontend**
- `frontend/src/components/InlineEdit.jsx` — edição inline de texto: clique ativa input, Enter/blur salva via callback `onSave`, Escape cancela, valor vazio não dispara save
- `frontend/src/components/CategoryBadge.jsx` — badge com cor distinta por categoria: Funcionário (azul), Visitante (roxo), Monitorado (vermelho), Desconhecido (cinza)
- `frontend/src/components/MergeActionBar.jsx` — action bar flutuante: contagem de selecionados, botão "Definir principal", botão "Mesclar" (desabilitado sem primary), botão "Cancelar"
- `frontend/src/pages/People.jsx` — `InlineEdit` no nome de cada card (renomear sem navegar); `CategoryBadge` abaixo do nome; botão "Mesclar perfis" ativa modo multi-seleção com checkboxes visuais e `MergeActionBar`; `POST /people/merge` + refetch após sucesso
- `frontend/src/pages/PersonDetail.jsx` — painel 4-grid com stats (video_count, total_seconds, first_seen, last_seen) via `GET /people/{id}/stats`; edição de `notes` (textarea) e `category` (select) via `PATCH /people/{id}`

**Testes**
- `tests/unit/test_migration_v1_13.py` — 4 testes (idempotência, colunas, default)
- `tests/unit/test_models.py` — 7 testes Sprint 6 (PersonCategory, notes/category no modelo)
- `tests/unit/test_schemas.py` — 6 testes Sprint 6 (PersonUpdate, PersonStatsResponse, MergeRequest)
- `tests/unit/test_person_service.py` — 11 testes (update_person_details ×5, get_person_stats ×2, merge_people ×4)
- `tests/integration/test_people.py` — 6 novos testes (PATCH parcial, stats, merge, self-merge 422, 404)
- `frontend/src/components/InlineEdit.test.jsx` — 6 testes TDD
- `frontend/src/components/PersonCard.test.jsx` — 5 testes TDD (CategoryBadge)
- `frontend/src/components/PeopleMerge.test.jsx` — 6 testes TDD (MergeActionBar)

### Corrigido

- `frontend/src/pages/People.jsx` + `Dashboard.jsx` — `limit=500` → `limit=200` (backend aceita `le=200`); evitava HTTP 422 no carregamento inicial
- `frontend/src/hooks/useAuthImage.js` (novo) — `<img src>` não envia JWT; substituído por `api.get` com `responseType: 'blob'` + `URL.createObjectURL`; cleanup via `URL.revokeObjectURL` no `useEffect`
- `frontend/src/utils/sanitizeFileName.js` (novo) — extrai último segmento do path, strip de `..`, fallback `[arquivo]`; aplicado em `PersonDetail` e `Dashboard`

### Infraestrutura

- `Documentos/Cronograma de Sprints - Gossipy Watchman.docx` — Sprint 6 adicionada
- Verificação Sprint 6: 159 testes pytest + 31 testes vitest passando; build de produção frontend limpo

---

*Fragmentos individuais disponíveis em `changelog/` para rastreabilidade por tarefa.*
