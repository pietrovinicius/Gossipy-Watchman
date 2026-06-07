## v1.51 — 2026-06-06

### Tipo da mudança
feat

### Arquivos alterados
- app/services/person_service.py (set_primary_photo, _is_safe_face_filename)
- app/schemas/person.py (PrimaryPhotoRequest)
- app/api/v1/people.py (PATCH /people/{id}/primary-photo)
- app/core/settings.py, frontend/package.json (bump 1.5.1)
- tests/unit/test_person_service.py, tests/integration/test_people.py

### Impacto técnico/funcional
Novo endpoint PATCH /people/{person_id}/primary-photo permite definir
qualquer amostra facial da galeria como foto principal do perfil.

set_primary_photo() segue cadeia de validação 400 (caminho inseguro,
mesma lógica de _is_safe_filename de faces.py) → 404 (arquivo
inexistente ou pessoa inexistente) → 403 (arquivo pertence a outra
pessoa, validado por prefixo {person_id}_). Cópia via shutil.copy2
preserva o arquivo original e grava em {person_id}.jpg, atualizando
profile_image_path.

8 novos testes (4 unitários de serviço + 4 de integração de endpoint).
236/236 testes passando.
