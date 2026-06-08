## v1.8.9 — 2026-06-07

### Adicionado

**Thumbnails de vídeos:**
- Modelo Video: novo campo `thumbnail_path`
- Worker: extrai e salva 1º frame de cada vídeo processado como JPEG
- API: endpoint GET `/videos/{id}/thumbnail` retorna imagem JPEG
- Frontend: exibe thumbnail no card de vídeos (fallback: ícone de filme)

**Schemas:**
- VideoResponse + VideoCardResponse: incluem `thumbnail_path`

**Migration:**
- ALTER TABLE videos ADD COLUMN thumbnail_path VARCHAR(512) DEFAULT NULL

**Impacto:**
- /videos: cards exibem preview visual do vídeo (1º frame)
- Usuário reconhece vídeos visualmente sem ler nome

**Testes:** 375 passam (0 regressões).
