## v1.55 — 2026-06-07

### Tipo da mudança
fix

### Arquivos alterados
- app/services/face_service.py
- tests/unit/test_face_service.py

### Impacto técnico/funcional
Troca o modelo de detecção facial de HOG (padrão do face_recognition) para CNN
em extract_embeddings(), passando number_of_times_to_upsample e model vindos de
settings.FACE_UPSAMPLE / settings.FACE_DETECTION_MODEL. Aumenta taxa de detecção
em faces pequenas, de perfil ou com iluminação adversa. 1 novo teste cobrindo
os kwargs da chamada a face_recognition.face_locations; testes existentes de
extract_embeddings/find_matching_person continuam passando (8/8).
