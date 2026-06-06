## v0.11 — 2026-06-06

### Tipo da mudança
feat

### Arquivos alterados
- app/services/face_service.py
- tests/unit/test_face_service.py
- requirements.txt

### Impacto técnico/funcional
Implementa extract_embeddings() com conversão BGR→RGB antes do processamento e
find_matching_person() com distância euclidiana via face_recognition.face_distance().
Decisão arquitetural: setuptools<71 adicionado ao requirements.txt porque
face-recognition-models usa pkg_resources, que foi removido do setuptools>=71.
Python 3.14 + setuptools 82+ quebra o import sem este pin.
TDD: 7 testes com mock de face_recognition, todos passando.
