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
| **Visão computacional** | OpenCV 4.9+, InsightFace 0.7+ (buffalo_l), ONNX Runtime 1.17+, NumPy 2.x |
| **Testes** | pytest 8, pytest-asyncio 0.23, httpx |

---

## Como Rodar Localmente

### macOS / Linux

```bash
# Criar e ativar virtualenv
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# Edite .env preenchendo JWT_SECRET_KEY e ADMIN_PASSWORD_HASH conforme
# os comandos documentados no próprio .env.example

# Criar diretórios de storage (se não existirem)
mkdir -p storage/videos storage/faces storage/models

# Iniciar servidor de desenvolvimento
uvicorn app.main:app --reload --workers 1 --host 0.0.0.0 --port 8000
```

---

### Windows 11

#### 1. Pré-requisitos

| Ferramenta | Versão mínima | Download |
|-----------|--------------|---------|
| Python | 3.11 | [python.org/downloads](https://www.python.org/downloads/) — **NÃO usar a versão da Microsoft Store** |
| Node.js | 18 LTS | [nodejs.org](https://nodejs.org/) |
| ffmpeg | qualquer | `winget install ffmpeg` ou [ffmpeg.org/download.html](https://ffmpeg.org/download.html) — adicionar ao PATH |
| Git | qualquer | [git-scm.com](https://git-scm.com/) |

> **Atenção Python:** Durante a instalação, marque **"Add Python to PATH"**. Use o instalador de [python.org](https://python.org), não a Microsoft Store — a versão da Store causa erros com extensões C (OpenCV, ONNX Runtime).

#### 2. Clonar e configurar ambiente

Abra o **PowerShell** (ou Terminal) na pasta onde deseja instalar:

```powershell
git clone https://github.com/pietrovinicius/Gossipy-Watchman.git
cd "Gossipy-Watchman"

# Criar e ativar virtualenv
python -m venv venv
venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt
```

> Se aparecer erro `Microsoft Visual C++ 14.0 is required`, instale o [Build Tools for Visual Studio](https://visualstudio.microsoft.com/visual-cpp-build-tools/) com workload **"C++ build tools"** antes de rodar o pip.

#### 3. Configurar variáveis de ambiente

```powershell
copy .env.example .env
```

Abra o `.env` em qualquer editor e configure os campos obrigatórios:

```env
# Gere com: python -c "import secrets; print(secrets.token_hex(32))"
JWT_SECRET_KEY=COLE-SUA-CHAVE-AQUI

# Gere com: python -c "from passlib.context import CryptContext; print(CryptContext(['bcrypt']).hash('watchman'))"
ADMIN_PASSWORD_HASH=COLE-O-HASH-AQUI
```

Adicione ao final do `.env` as otimizações para Windows 16 GB RAM:

```env
# Otimizações Windows
INSIGHTFACE_DET_SIZE=640
INSIGHTFACE_INTRA_OP_NUM_THREADS=4
INSIGHTFACE_PROVIDERS=["CPUExecutionProvider"]
```

#### 4. Criar diretórios de storage

```powershell
New-Item -ItemType Directory -Force -Path storage\videos, storage\faces, storage\models
```

#### 5. Verificar ffmpeg

```powershell
ffmpeg -version
```

Se não reconhecer o comando, adicione o diretório `bin/` do ffmpeg ao PATH:
`Configurações do Sistema → Variáveis de Ambiente → Path → Novo → C:\ffmpeg\bin`

#### 6. Iniciar backend

```powershell
# Com virtualenv ativo (venv\Scripts\activate)
uvicorn app.main:app --reload --workers 1 --host 0.0.0.0 --port 8000
```

> **`--workers 1` é obrigatório no Windows.** O Windows não suporta `fork` — múltiplos workers causam falha silenciosa na inicialização do ONNX Runtime.

A API estará disponível em `http://localhost:8000`.  
Documentação Swagger: `http://localhost:8000/docs`.

#### 7. Iniciar frontend

```powershell
cd frontend
npm install
npm run dev
```

O frontend estará disponível em `http://localhost:5173`.

#### 8. Na primeira execução

O InsightFace baixa automaticamente o modelo `buffalo_l` (~200 MB) na primeira chamada de processamento de vídeo. O download ocorre para `%USERPROFILE%\.insightface\models\buffalo_l\`. Aguarde — pode levar alguns minutos dependendo da conexão.

#### Solução de problemas comuns no Windows

| Erro | Causa | Solução |
|------|-------|---------|
| `PermissionError: [WinError 32] The process cannot access the file` | Windows mantém handle aberto em arquivo recém-fechado | Aguardar e tentar novamente; o sistema já tem retry automático (safe_unlink) |
| `OnnxRuntimeError: No such file or directory` | Modelo buffalo_l não baixado ainda | Verificar conexão; deletar `%USERPROFILE%\.insightface\models\buffalo_l\` e deixar baixar novamente |
| `uvicorn: error: unrecognized arguments: --workers` | Versão antiga do uvicorn | `pip install --upgrade uvicorn[standard]` |
| `Error loading shared library libmagic` | Resíduo de instalação anterior | Ignorar; python-magic foi removido do requirements.txt (não é usado) |
| Porta 8000 já em uso | Outro processo na porta | `netstat -ano \| findstr :8000` para identificar PID, depois `taskkill /PID <numero> /F` |

---

### Frontend (todas as plataformas)

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
python -m pytest tests/unit/ -v
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
