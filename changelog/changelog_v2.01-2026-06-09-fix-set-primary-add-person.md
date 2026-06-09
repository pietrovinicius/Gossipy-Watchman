## v2.01 — 2026-06-09

### Tipo da mudança
fix + feat

### Arquivos alterados
- app/services/person_service.py
- app/services/appearance_service.py
- app/schemas/appearance.py
- app/api/v1/videos.py
- frontend/src/components/PersonFrames.jsx
- frontend/src/pages/VideoDetail.jsx
- tests/unit/test_person_service.py
- tests/unit/test_appearance_service.py
- tests/integration/test_people.py

### Impacto técnico/funcional

**fix: set_primary_photo não destrói mais a foto anterior**
- `set_primary_photo` atualizava `profile_image_path` via `shutil.copy2` para `{id}.jpg`, sobrescrevendo o conteúdo anterior e destruindo a imagem original.
- Corrigido: `profile_image_path` agora aponta diretamente para o arquivo selecionado (sem cópia), preservando `{id}.jpg` intacto.

**fix: delete_face_frame verifica primary real**
- `delete_face_frame` bloqueava delete de `{id}.jpg` com check hardcoded, sem considerar o primary atual.
- Corrigido: verifica `Path(person.profile_image_path).name` para identificar o frame principal atual.

**fix: sem delay ao trocar foto principal**
- `PersonFrames.jsx` bumpa `refreshCounter` em toda chamada de `fetchFrames`, causando redownload de todas as imagens.
- Corrigido: optimistic update imediato (flip de `is_primary` local), sem bump de counter. Counter bumpa apenas ao deletar frame. `key` do `FrameThumb` usa só `filename` (sem `is_primary`).

**feat: adicionar pessoa catalogada a vídeo já processado**
- Novo endpoint `POST /videos/{video_id}/appearances` cria aparição manual com `person_id`, `timestamp_start`, `timestamp_end`.
- Frontend: botão "Adicionar pessoa" visível em vídeos com status `Concluído`. Modal com busca de pessoa + campos de timestamp. Após submissão, detalhe do vídeo é atualizado.
