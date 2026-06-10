## v2.22 — 2026-06-10

### Tipo da mudança
feat

### Arquivos alterados
- src/pages/People.jsx
- src/pages/PersonDetail.jsx
- src/pages/Employees.jsx
- src/i18n/locales/en/translation.json
- src/i18n/locales/pt-BR/translation.json
- src/test/PeopleDelete.test.jsx
- src/test/PeopleTableView.test.jsx
- src/test/PersonDetail.test.jsx
- src/test/PersonDetailActions.test.jsx

### Impacto técnico/funcional
Migra People, PersonDetail e Employees para react-i18next (Sprint 17, Prioridade 1).
Categoria de pessoa exibida via mapa CATEGORY_KEY → people.category.* (valores de
backend permanecem em português). Datas formatadas via locale (pt-BR/en-US).
Corrigido personDetail.deleteConfirmWord (pt-BR) de "delete" para "excluir",
alinhando com confirmWord original do PersonDetail. Testes atualizados para
asserções em inglês (idioma padrão). Suite: 234/235 passando (1 falha
pré-existente em PersonFrames.test.jsx, não relacionada).
