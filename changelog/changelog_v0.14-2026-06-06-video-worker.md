## v0.14 — 2026-06-06

### Tipo da mudança
feat

### Arquivos alterados
- app/workers/video_worker.py
- app/services/__init__.py
- tests/integration/test_video_worker.py

### Impacto técnico/funcional
Implementa process_video() orquestrando frame_service, face_service, person_service e
appearance_service. Status Processando → Concluído ao final; Erro em qualquer exceção.
Decisão arquitetural: _engine opcional no process_video() para injeção de dependência
em testes sem patch de create_engine. StaticPool usado nos fixtures de teste para garantir
conexão única compartilhada em SQLite in-memory.
engine.dispose() chamado apenas quando o worker criou o engine (_owns_engine=True).
TDD: 4 testes de integração, todos passando.
