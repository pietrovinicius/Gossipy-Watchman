## v1.95 — 2026-06-08

### Tipo da mudança
feat

### Arquivos alterados
- requirements.txt
- .gitignore
- app/main.py
- app/core/model_downloader.py
- app/services/face_service.py
- app/services/employee_service.py
- app/services/search_service.py
- tests/unit/test_face_service.py
- tests/unit/test_employee_service.py
- tests/unit/test_search_service.py
- tests/integration/test_search.py

### Impacto técnico/funcional
- Migrada toda a arquitetura de detecção e reconhecimento facial para rodar nativamente via OpenCV DNN com os modelos ultra-leves **YuNet** (detecção) e **SFace** (reconhecimento/embeddings).
- Adicionada rotina de download automático (`app/core/model_downloader.py`) no lifespan do FastAPI para baixar os pesos dos modelos diretamente do Hugging Face.
- Removidas por completo as dependências das bibliotecas `face_recognition` e `dlib` (e a limitação do `setuptools<71`), reduzindo drasticamente o consumo de memória RAM e processamento de CPU, além de simplificar a compilação e o setup do ambiente local.
- Mantida total compatibilidade de formato com os embeddings de 128 dimensões salvos anteriormente no banco de dados SQLite.
- Atualizados todos os testes unitários e de integração para mockar e validar o novo pipeline nativo do OpenCV.
