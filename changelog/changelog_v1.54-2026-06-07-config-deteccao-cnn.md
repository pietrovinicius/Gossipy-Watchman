## v1.54 — 2026-06-07

### Tipo da mudança
feat

### Arquivos alterados
- app/core/settings.py
- .env
- .env.example
- tests/unit/test_settings.py

### Impacto técnico/funcional
Adiciona constantes de configuração FACE_DETECTION_MODEL ("cnn", padrão) e
FACE_UPSAMPLE (1, padrão) ao Settings, preparando troca do modelo de detecção
facial de HOG para CNN no pipeline de visão computacional. 3 novos testes
unitários cobrindo defaults e aceitação de "hog" como alternativa.
