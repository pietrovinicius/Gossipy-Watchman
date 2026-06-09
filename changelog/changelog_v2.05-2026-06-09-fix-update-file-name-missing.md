## v2.05 — 2026-06-09

### Tipo da mudança
fix

### Arquivos alterados
- app/services/video_service.py
- app/api/v1/upload.py
- tests/unit/test_video_service.py

### Impacto técnico/funcional

**fix(video_service): update_file_name não existia — upload de formatos convertíveis retornava 422**
- `upload.py` chamava `video_service.update_file_name()` após conversão bem-sucedida, mas a
  função nunca foi implementada em `video_service.py`. Resultado: toda conversão bem-sucedida
  de .dav/.mkv/.mov/.ts terminava em AttributeError → 422.
- Implementado `update_file_name(db, video_id, file_name) → Video | None` seguindo o mesmo
  padrão de `update_file_path`.

**fix(upload): erro de metadados pós-conversão deletava o arquivo convertido**
- Bloco `except` da conversão deletava `*_converted.mp4` mesmo quando ffmpeg havia concluído
  com sucesso e o erro era em operação posterior (ex.: `update_file_name` inexistente).
- Reestruturado: o `except` agora envolve apenas `convert_to_mp4`. Operações de metadados
  (`unlink` do original, `update_file_name`) ficam fora do `try` — falha nelas não destrói
  o arquivo convertido.
