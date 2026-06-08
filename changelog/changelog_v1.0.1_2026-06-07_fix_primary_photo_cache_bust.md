## [1.0.1] — 2026-06-07

### Corrigido

**Bug:** "Definir como principal" não persiste na tela PersonDetail
- **frontend/src/hooks/useAuthImage.js**: adicionado cache-bust parameter (`?t=${cacheTag}`) na URL para forçar refetch da imagem quando o arquivo muda em disco
- **frontend/src/components/PersonFrames.jsx**: reordenado state update para incrementar `refreshCounter` ANTES de `setFrames()`, garantindo que FrameThumb receba cacheTag atualizado
- **frontend/src/test/useAuthImage.test.jsx**: atualizado teste para validar inclusion do cache-bust parameter na URL
- **frontend/src/test/useAuthImage-cache-bust.test.jsx**: adicionado novo teste que valida refetch com mudança de cacheTag

**Causa raiz:** Browser cacheava imagem com URL idêntica mesmo após mudança do arquivo em disco. Solução implementa versioning de URL via query parameter.

**Cobertura:** Testes verificam ambos os cases:
1. URL inclui `?t=` parameter
2. Parameter muda quando `cacheTag` muda → força nova requisição GET
