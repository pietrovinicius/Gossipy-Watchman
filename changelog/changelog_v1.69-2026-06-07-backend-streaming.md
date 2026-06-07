## v1.69 — 2026-06-07

### Tipo da mudança
feat

### Arquivos alterados
- app/api/v1/videos.py
- tests/integration/test_videos.py

### Impacto técnico/funcional

**Backend - Endpoint de Streaming com Range Requests (HTTP 206):**

Adicionado GET /api/v1/videos/{video_id}/stream?token=JWT:
- Autenticação via query param token (JWT decoded via verify_token)
- HTTP 401 se token ausente ou inválido
- HTTP 404 se vídeo não existe em banco
- HTTP 404 se arquivo físico não existe em disco
- HTTP 410 Gone se vídeo soft-deleted (deleted_at not null)

Suporte completo a Range requests (RFC 7233):
- Header Range: bytes=start-end
- HTTP 206 Partial Content com Content-Range
- StreamingResponse com iterfile() para não carregar tudo na memória
- Content-Length correto para seekbar
- Accept-Ranges: bytes header em ambos os casos

Sem Range:
- HTTP 200 com FileResponse
- Accept-Ranges: bytes header

Rota registrada ANTES de /videos/{id} genérico para evitar conflito.

TDD: 7 testes de integração — token, deleted, 404, 200 sem Range, 206 com Range.
Total de testes: 332 passando.

### Próximo passo
Frontend 13.2: VideoPlayer component com src autenticado.
