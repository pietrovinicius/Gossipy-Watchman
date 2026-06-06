## v1.12 — 2026-06-06

### Tipo da mudança
fix

### Arquivos alterados
- frontend/src/hooks/useAuthImage.js (novo)
- frontend/src/utils/sanitizeFileName.js (novo)
- frontend/src/services/api.js (+ export BACKEND_URL)
- frontend/src/pages/People.jsx (usa useAuthImage; remove FACES_BASE hardcoded)
- frontend/src/pages/PersonDetail.jsx (usa useAuthImage + sanitizeFileName)
- frontend/src/pages/Dashboard.jsx (usa sanitizeFileName)
- frontend/src/test/useAuthImage.test.jsx (novo — 6 testes)
- frontend/src/test/sanitizeFileName.test.js (novo — 6 testes)

### Impacto técnico/funcional
Fix 1 — miniaturas de rostos: <img src> não envia JWT, causando 401 no endpoint
/api/v1/faces/* (autenticado desde v1.07). Solução: hook useAuthImage busca a imagem
via api.get com Bearer token, cria object URL via URL.createObjectURL e revoga no
cleanup do useEffect. Aplicado em People.jsx (PersonCard) e PersonDetail.jsx.
A extração do filename usa profile_image_path.split('/').pop() ao invés de person.id.jpg.

Fix 2 — sanitização de file_name: "../../etc/passwd.mp4" exibido raw no Dashboard e
na timeline da PersonDetail. Função sanitizeFileName extrai o último segmento após
/ ou \, remove sequências de ".." e retorna "[arquivo]" para strings vazias ou suspeitas.
Aplicada em Dashboard.jsx e PersonDetail.jsx.

TDD: 6 testes useAuthImage + 6 testes sanitizeFileName. Total frontend: 14 testes.
