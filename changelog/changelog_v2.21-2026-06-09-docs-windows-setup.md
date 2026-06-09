## v2.21 — 2026-06-09

### Tipo da mudança
docs

### Arquivos alterados
- README.md
- requirements.txt

### Impacto técnico/funcional
Adicionada seção completa "Windows 11" em Como Rodar Localmente, cobrindo: pré-requisitos (Python python.org, Node.js, ffmpeg via winget), ativação de virtualenv no PowerShell, variáveis .env específicas para Windows 16GB RAM (INSIGHTFACE_INTRA_OP_NUM_THREADS, INSIGHTFACE_PROVIDERS, DET_SIZE), criação de diretórios de storage, aviso obrigatório --workers 1, tabela de troubleshooting para erros comuns no Windows. Removido python-magic do requirements.txt (nunca importado no código, causa erro no Windows por exigir libmagic DLL). Stack table atualizada de face_recognition/dlib para insightface/onnxruntime.
