## v2.02 — 2026-06-09

### Tipo da mudança
fix

### Arquivos alterados
- app/workers/video_worker.py
- app/services/video_service.py
- tests/unit/test_worker_adaptive_cnn.py
- tests/unit/test_video_service.py

### Impacto técnico/funcional

**fix(worker): nova pessoa sem appearance no vídeo**
- Em `_process_track`, quando `person_id is None` (nova pessoa detectada), o worker
  criava o registro em `people` mas não chamava `upsert_appearance`, deixando a pessoa
  sem vínculo com o vídeo na tabela `appearances`.
- Resultado: `/videos/{id}/detail` mostrava N-1 pessoas enquanto `/people` mostrava N.
- Corrigido: adicionado `upsert_appearance` no branch de nova pessoa com `confidence=0.0`
  e os timestamps do track.

**fix(videos): limpeza de arquivos físicos ao deletar vídeo**
- `soft_delete_video` agora remove o arquivo de vídeo (`file_path`) e o thumbnail
  (`thumbnail_path`) do disco ao realizar o soft-delete.
- Se arquivo não existir, ignora silenciosamente (sem exceção).
- DB record preservado com `deleted_at` (soft delete). Face crops não são removidos
  pois pertencem a pessoas, não ao vídeo específico.
