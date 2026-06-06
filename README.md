# Gossipy Watchman

Sistema web de análise de vídeo para identificação, catalogação e registro temporal de pessoas via reconhecimento facial — portfólio técnico demonstrando arquitetura assíncrona, visão computacional e separação limpa de camadas.

---

## Telas do Sistema

| Tela | Descrição visual |
|------|-----------------|
| **Login** | Fundo preto OLED, logo com ícone de escudo vermelho, campos de usuário/senha com toggle de visibilidade, botão primário azul |
| **Dashboard** | 4 cards de métricas (vídeos processados, fila, pessoas, desconhecidos), tabela dos 10 vídeos mais recentes com badges coloridos por status, auto-refresh a cada 15s |
| **Upload** | Área de drag-and-drop com borda tracejada, barra de progresso animada durante envio, card de sucesso com link para o Dashboard |
| **Pessoas** | Galeria em grid 3 colunas (responsiva), avatar de rosto extraído pelo pipeline, campo de busca em tempo real por nome |
| **Detalhe da Pessoa** | Foto ampliada, nome editável inline com confirmação/cancelamento, tabela de timeline com vídeo, início, fim e confiança de cada aparição |

---

## Business Case — Cenários de Uso

- **Auditoria de acesso a áreas restritas**: identifica automaticamente quais funcionários ou visitantes acessaram salas de UTI, centro cirúrgico ou farmácia, com registro de horário exato
- **Compliance de atendimento**: confirma presença de profissionais habilitados nos atendimentos, gerando evidência auditável para órgãos reguladores (ANS, CFM, ANVISA)
- **Monitoramento de pacientes de alto risco**: detecta quando pacientes com histórico de evasão ou risco de queda aparecem em áreas não autorizadas e registra todos os eventos temporalmente

---

## Stack

| Camada | Tecnologia |
|--------|-----------|
| **Backend** | Python 3.11+, FastAPI 0.111+, Uvicorn |
| **Frontend** | React 18, Vite, Tailwind CSS 3, Axios, React Router v6, Lucide React |
| **Banco de dados** | SQLite (dev) via SQLAlchemy 2.x |
| **Visão computacional** | OpenCV 4.13, face_recognition 1.3, dlib 20, NumPy 2.x |
| **Testes** | pytest 8, pytest-asyncio 0.23, httpx |

---

## Como Rodar Localmente

### Backend

```bash
# Criar e ativar virtualenv
python3 -m venv venv
source venv/bin/activate          # Linux/Mac
# venv\Scripts\activate           # Windows

# Instalar dependências
pip install -r requirements.txt

# Iniciar servidor de desenvolvimento
uvicorn app.main:app --reload --port 8000
```

A API estará disponível em `http://localhost:8000`.
Documentação interativa (Swagger): `http://localhost:8000/docs`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

O frontend estará disponível em `http://localhost:5173`.

**Credenciais de acesso (portfólio):** `admin` / `watchman`

### Testes

```bash
# Na raiz do projeto, com virtualenv ativo
pytest tests/ -v
```

---

## Estrutura de Diretórios

```
gossipy-watchman/
├── app/
│   ├── api/v1/          # Routers FastAPI (health, upload, videos, people, timeline)
│   ├── core/            # settings.py — todas as constantes de configuração
│   ├── db/              # session.py, init_db.py
│   ├── models/          # Person, Video (VideoStatus Enum), Appearance
│   ├── schemas/         # Pydantic: VideoCreate/Response, PersonResponse/Update, AppearanceResponse
│   ├── services/        # Lógica de negócio: video, person, appearance, frame, face
│   ├── workers/         # video_worker.py — pipeline CV assíncrono
│   └── main.py          # App FastAPI, CORS, StaticFiles /faces
├── frontend/            # Vite + React
│   └── src/
│       ├── pages/       # Login, Dashboard, Upload, People, PersonDetail
│       ├── components/  # Layout, ProtectedRoute
│       └── services/    # api.js (Axios)
├── storage/
│   ├── videos/          # Vídeos enviados pelo usuário
│   └── faces/           # Recortes de rostos (.jpg) e embeddings (.npy)
├── tests/
│   ├── unit/            # 7 módulos de testes unitários
│   └── integration/     # 5 módulos de testes de integração
├── changelog/           # Fragmentos de changelog por tarefa (v0.01–v0.28)
├── CHANGELOG.md         # Histórico consolidado (gerado em releases)
├── CLAUDE.md            # Guia operacional para agentes de IA
└── requirements.txt
```

---

## Endpoints da API

| Método | Path | Descrição |
|--------|------|-----------|
| `GET` | `/api/v1/health` | Health check |
| `POST` | `/api/v1/videos/upload` | Upload de vídeo (multipart, HTTP 202, dispara pipeline em background) |
| `GET` | `/api/v1/videos` | Listagem paginada de vídeos (`?skip=0&limit=50`) |
| `GET` | `/api/v1/videos/{id}` | Detalhe de vídeo |
| `GET` | `/api/v1/videos/{id}/status` | Status do processamento (polling) |
| `GET` | `/api/v1/people` | Listagem paginada de pessoas catalogadas |
| `GET` | `/api/v1/people/{id}` | Detalhe de pessoa |
| `PATCH` | `/api/v1/people/{id}` | Renomear pessoa (body: `{"name": "..."}`) |
| `GET` | `/api/v1/people/{id}/timeline` | Timeline de aparições com `file_name` do vídeo |
| `GET` | `/faces/{person_id}.jpg` | Imagem de rosto (estático) |

---

## Decisões Arquiteturais Relevantes

**`FACE_RECOGNITION_TOLERANCE = 0.6` como constante nomeada**
Centralizada em `app/core/settings.py`. Permite ajuste sem alterar código de lógica — qualquer engenheiro encontra e modifica em um único lugar.

**Embeddings em `.npy` por `person_id`**
Cada pessoa tem seu embedding salvo em `storage/faces/{id}_embedding.npy`. Evita armazenar vetores de 128 floats no banco relacional; carregamento via `np.load` é O(1) por pessoa.

**`AppearanceWithVideo` dataclass**
O modelo `Appearance` (ORM) não carrega `file_name` (campo de `Video`). Em vez de relationship lazy ou coluna redundante, o `get_timeline()` faz JOIN explícito e projeta numa dataclass, mantendo os modelos ORM limpos e o SQL auditável.

**`StaticPool` nos fixtures de testes de integração**
SQLite in-memory cria banco isolado por conexão. Sem `StaticPool`, o fixture e o endpoint veem bancos diferentes. Com `StaticPool`, uma conexão única é compartilhada entre todas as sessions do mesmo engine de teste.

**`setuptools<71` pinado no `requirements.txt`**
`face-recognition-models` importa `pkg_resources` (removido do setuptools ≥ 71). Python 3.14 não tem `pkg_resources` na stdlib. O pin garante compatibilidade sem patch no código de terceiros.

**`_engine` opcional no `process_video()`**
O worker cria seu próprio engine (roda em thread separada, fora do ciclo de vida da requisição FastAPI). O parâmetro `_engine` permite injeção de engine de teste sem monkey-patch de `create_engine` — padrão mais seguro e explícito.

**`get_db()` sem parâmetro + `get_db_with_engine()`**
FastAPI `Depends()` não aceita parâmetros extras na função injetada. Separar as duas funções permite `dependency_overrides` limpo nos testes de integração sem alterar a assinatura de produção.

---

## Próximos Passos

1. **Auth real** — JWT no backend (FastAPI + python-jose) + refresh token no frontend
2. **WebSocket** — progresso de processamento em tempo real sem polling a cada 15s
3. **Threshold ajustável** — endpoint para alterar `FACE_RECOGNITION_TOLERANCE` em runtime via UI
4. **Vídeo player** — exibir o vídeo com marcadores temporais sobrepostos nas aparições
5. **Export** — endpoint de download CSV/JSON da timeline para análise externa
6. **Docker** — `docker-compose.yml` para rodar backend + frontend com um único `docker compose up`
7. **CI/CD** — GitHub Actions com `pytest` + `npm run build` em cada push para `main`

---

## Licença

MIT © 2026 Pietro Lima
