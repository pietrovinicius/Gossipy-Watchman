# CLAUDE.md — Gossipy Watchman

Guia operacional para agentes de IA neste projeto. Seguir rigorosamente.

---

## 1. Missão do Projeto

Sistema web de análise de vídeo para identificação, catalogação e registro temporal de pessoas via reconhecimento facial.

**Objetivo:** portfólio técnico de nível sênior demonstrando arquitetura assíncrona, visão computacional e separação limpa de camadas.

**Stack:**
- Backend: FastAPI (Python 3.11+)
- Frontend: React (client-side, consumindo a API REST)
- Banco: SQLite local (via SQLAlchemy)
- Processamento de mídia: OpenCV + face_recognition
- Processamento assíncrono: Background Tasks nativas do FastAPI (ou ThreadPoolExecutor)

---

## 2. Estrutura de Diretórios

```
gossipy-watchman/
├── app/
│   ├── api/          # Routers FastAPI (endpoints REST)
│   ├── core/         # Configurações, constantes, settings
│   ├── db/           # Inicialização do banco, conexão, migrations manuais
│   ├── models/       # Modelos de dados (SQLAlchemy)
│   ├── schemas/      # Schemas Pydantic (request/response)
│   ├── services/     # Lógica de negócio e orquestração
│   └── workers/      # Pipeline de visão computacional e background jobs
├── frontend/         # Projeto React
├── storage/
│   ├── videos/       # Arquivos de vídeo enviados
│   └── faces/        # Recortes de rostos detectados
├── tests/
│   ├── unit/         # Testes unitários por módulo
│   └── integration/  # Testes de integração de endpoints e workers
├── changelog/        # Fragmentos de changelog por tarefa
├── CLAUDE.md
├── CHANGELOG.md
└── requirements.txt
```

---

## 3. Modelagem do Banco de Dados (SQLite)

**people**
| Campo | Tipo | Descrição |
|---|---|---|
| id | PK | Identificador único |
| name | VARCHAR | Nome da pessoa (ou `Desconhecido #N`) |
| profile_image_path | VARCHAR | Caminho do recorte facial de referência |
| created_at | TIMESTAMP | Data de cadastro |

**videos**
| Campo | Tipo | Descrição |
|---|---|---|
| id | PK | Identificador único |
| file_name | VARCHAR | Nome original do arquivo |
| file_path | VARCHAR | Caminho em `storage/videos/` |
| status | VARCHAR | `Pendente` \| `Processando` \| `Concluído` \| `Erro` |
| uploaded_at | TIMESTAMP | Data do upload |

**appearances**
| Campo | Tipo | Descrição |
|---|---|---|
| id | PK | Identificador único |
| person_id | FK → people | Pessoa identificada |
| video_id | FK → videos | Vídeo de origem |
| timestamp_start | FLOAT | Início da aparição (segundos) |
| timestamp_end | FLOAT | Fim da aparição (segundos) |
| confidence | FLOAT | Distância euclidiana do embedding (menor = mais confiante) |

---

## 4. Regras de Banco de Dados

- **SELECT:** sempre permitido.
- **INSERT/UPDATE:** permitidos no fluxo normal da aplicação. Qualquer alteração direta fora do código (script ad-hoc, migração manual) exige confirmação explícita do usuário no turno atual.
- **DELETE físico:** proibido. Usar soft delete ou flag de status para preservar histórico.

---

## 5. Pipeline de Visão Computacional

Ciclo de vida completo do processamento de um vídeo:

1. Upload recebido → arquivo salvo em `storage/videos/` → job registrado no banco com status `Pendente`
2. Background worker assume → status muda para `Processando`
3. OpenCV decodifica o vídeo com amostragem de **1 frame por segundo**
4. `face_recognition` extrai embeddings de cada face detectada no frame
5. Sistema compara embeddings com registros existentes usando distância euclidiana com threshold `FACE_RECOGNITION_TOLERANCE = 0.6` (declarado em `app/core/settings.py`):
   - Distância **abaixo** do threshold → mesma pessoa conhecida
   - Distância **acima** do threshold → novo perfil
6. **Face nova** → cadastro com nome temporário (`Desconhecido #N`) + recorte salvo em `storage/faces/`
7. **Face conhecida** → extensão ou encerramento do intervalo temporal (`timestamp_start` / `timestamp_end`) na tabela `appearances`
8. Fim do vídeo → status `Concluído`; exceções → status `Erro` com log da exceção registrado

---

## 6. Padrões de Implementação

### Backend (Python / FastAPI)

- Type hints obrigatórios em toda função nova.
- Schemas Pydantic para todos os inputs e outputs de endpoints.
- Lógica de negócio centralizada em `app/services/`; routers em `app/api/` apenas orquestram chamada e resposta.
- Acesso ao banco centralizado em `app/db/`; sem conexão ad-hoc espalhada pelo código.
- Usar `pathlib.Path` para manipulação de caminhos de arquivo.
- Constantes de configuração (tolerâncias, paths, parâmetros de processamento) centralizadas em `app/core/settings.py`.

### Frontend (React)

- Comunicação com API via Axios com interceptadores base configurados.
- Componentes funcionais com hooks; sem class components.
- Sem dependências desnecessárias; justificar toda biblioteca adicionada ao `package.json`.

---

## 7. TDD — Lei de Ferro

TDD não é opcional. Para qualquer feature, bugfix, refatoração ou mudança de comportamento observável:

1. **RED:** escrever o teste em `tests/` que falha pelo motivo correto (não por sintaxe quebrada, import ausente ou fixture faltando).
2. **GREEN:** implementar o mínimo necessário para o teste passar.
3. **REFACTOR:** limpar o código sem alterar comportamento; todos os testes devem continuar passando.

**Red flags que indicam violação:**
- Código de produção escrito antes do teste
- Teste que passa sem ter falhado antes
- Qualquer variação de "vou testar depois"
- "É simples demais para precisar de teste"

**Framework:** `pytest`. Rodar `pytest` na raiz antes de qualquer commit.

**Exceção única:** código de infraestrutura pura sem comportamento de negócio (criação de tabelas, configuração de CORS, setup de diretórios) pode ser implementado sem teste prévio, com alinhamento explícito do usuário no turno atual.

---

## 8. Comandos Operacionais

```bash
# Backend
python -m venv venv
source venv/bin/activate          # Linux/Mac
venv\Scripts\activate             # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Testes
pytest
pytest tests/unit/                # apenas unitários
pytest tests/integration/         # apenas integração
pytest -v --tb=short              # verbose com traceback resumido

# Frontend
cd frontend
npm install
npm run dev
```

---

## 9. Regra de Commit (Obrigatória e Inegociável)

**Todo ajuste que alterar qualquer arquivo deve terminar com um commit.** Não existe tarefa concluída sem commit. Sem exceção.

**Sequência obrigatória antes de cada commit:**
1. Rodar `pytest` e confirmar que todos os testes passam.
2. Criar o fragmento de changelog (ver seção 10).
3. Fazer o commit com mensagem Conventional Commits em português.
4. Executar `git push`.

**Formato da mensagem:**

```bash
git commit -m "feat(worker): implementa amostragem de frames com OpenCV"
git commit -m "fix(api): corrige status de vídeo não atualizado após erro"
git commit -m "test(services): adiciona testes unitários para lógica de deduplicação"
git commit -m "refactor(db): centraliza criação de sessão em db/session.py"
```

Tipos válidos: `feat`, `fix`, `style`, `refactor`, `test`, `docs`, `chore`.

O push deve ser executado logo após o commit, no mesmo turno. Não acumular commits para push posterior.

---

## 10. Regra de Changelog Fragmentado (Obrigatória)

Toda tarefa com alteração de código, configuração ou documentação técnica deve gerar um fragmento em `changelog/` antes do commit. Sem fragmento, não há commit.

**Formato do nome do arquivo:**

```
changelog/changelog_vX.YY-AAAA-MM-DD-slug.md
```

**Conteúdo obrigatório do fragmento:**

```markdown
## vX.YY — AAAA-MM-DD

### Tipo da mudança
feat | fix | refactor | test | docs | chore

### Arquivos alterados
- app/services/face_service.py
- tests/unit/test_face_service.py

### Impacto técnico/funcional
Descrição objetiva do que mudou e por quê.
```

`CHANGELOG.md` na raiz é o histórico oficial consolidado; não editar diretamente por tarefa, apenas em releases.

---

## 11. Checklist de Execução por Tarefa (Ordem Obrigatória)

1. Confirmar escopo exato da tarefa com o usuário.
2. Mapear contexto mínimo necessário (arquivos e módulos afetados).
3. **Escrever o teste que falha (RED)** — nunca pular esta etapa.
4. Implementar respeitando os padrões da stack definidos neste documento (GREEN).
5. Refatorar mantendo os testes passando (REFACTOR).
6. Rodar `pytest` completo e confirmar aprovação.
7. Criar fragmento de changelog em `changelog/`.
8. Fazer commit com mensagem Conventional Commits em português.
9. Executar `git push`.

---

## 12. Estilo de Resposta do Agente

- Objetivo e direto; sem introdução longa ou redundância.
- Limitar leitura de arquivos ao escopo da tarefa.
- Nunca deixar tarefa concluída sem commit, push e fragmento de changelog.
- Ao propor implementação, sempre declarar qual teste será escrito primeiro.

---

## 13. Skills Recomendadas

As seguintes skills instaladas no ambiente são altamente pertinentes para o desenvolvimento deste projeto e podem ser usadas sempre que necessário para guiar a implementação de funcionalidades, testes e correção de bugs:

1. **`computer-vision-expert`**: Guia para manipulação de mídia com OpenCV, amostragem de frames e extração de embeddings faciais com `face_recognition`.
2. **`fastapi-pro`**: Melhores práticas para roteamento, injeção de dependência, manipulação de Pydantic v2 e estruturação assíncrona.
3. **`test-driven-development`** / **`tdd-workflow`**: Apoio para a Lei de Ferro do TDD, auxiliando na escrita de testes vermelhos (RED), código funcional (GREEN) e refatoração (REFACTOR).
4. **`react-patterns`** / **`react-best-practices`**: Padrões modernos para o frontend em React, hooks customizados, performance de componentes e integração Axios.
5. **`database-admin`**: Boas práticas para o mapeamento objeto-relacional com SQLAlchemy, transações no SQLite e migrações.
6. **`systematic-debugging`** / **`debugger`**: Metodologia sistemática para rastrear e solucionar falhas em background workers ou integração com a API.

*Nota: Estas skills podem ser invocadas/mencionadas a qualquer momento para garantir a aderência técnica recomendada.*

