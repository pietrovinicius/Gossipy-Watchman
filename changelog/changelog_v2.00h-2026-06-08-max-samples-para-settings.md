## v2.00h — 2026-06-08

### Tipo da mudança
refactor

### Arquivos alterados
- app/core/settings.py
- app/services/person_service.py
- tests/unit/test_person_service.py

### Impacto técnico/funcional
`save_face_sample` usava `MAX_FACE_SAMPLES = 10` hardcoded como constante de
módulo. Movido para `settings.FACE_MAX_SAMPLES_PER_PERSON = 10` (default igual),
permitindo sobrescrever via variável de ambiente sem alterar código. Constante
`MAX_FACE_SAMPLES` removida. Versão bumped para 2.00.0. Novo teste RED→GREEN
confirma que o limite custom (=3) via settings é respeitado. Três testes
existentes atualizados para incluir `FACE_MAX_SAMPLES_PER_PERSON` no mock.
