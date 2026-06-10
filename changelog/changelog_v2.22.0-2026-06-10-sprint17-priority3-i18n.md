## v2.22.0 — 2026-06-10

### Tipo da mudança
feat | test

### Arquivos alterados
- frontend/src/components/ConfirmModal.jsx
- frontend/src/components/MergeActionBar.jsx
- frontend/src/components/PhotoModal.jsx
- frontend/src/components/VideoPlayer.jsx
- frontend/src/i18n/locales/en/translation.json
- frontend/src/i18n/locales/pt-BR/translation.json
- frontend/src/test/ConfirmModal.test.jsx
- frontend/src/components/PeopleMerge.test.jsx
- frontend/src/test/PhotoModal.test.jsx
- frontend/src/test/VideoPlayer.test.jsx
- frontend/src/test/PeopleDelete.test.jsx

### Impacto técnico/funcional
Migração da Prioridade 3 (17.4) para react-i18next em componentes compartilhados:

- `ConfirmModal`: `confirmLabel`/`cancelLabel` agora têm fallback via
  `confirmModal.confirm`/`confirmModal.cancel`; placeholder de digitação usa
  `confirmModal.typeToConfirm`.
- `MergeActionBar`: contagem de selecionados, "Definir principal", "Principal: #ID"
  e ações de mesclar/cancelar usam novas chaves em `people.*`
  (`selectedCount`/`selectedCount_other`, `setPrimary`, `primaryLabel`,
  `mergeSelectedAria`, `cancelSelectionAria`).
- `PhotoModal`: aria-label do botão fechar usa `common.close`.
- `VideoPlayer`: mensagem de erro de carregamento e legenda de presença usam novas
  chaves `videoDetail.loadError`, `videoDetail.hideLegend`, `videoDetail.showLegend`.

`CategoryBadge.jsx` e `InlineEdit.jsx` (citados no plano original) não existem no
projeto — não aplicável.

Testes ajustados para asserts em inglês (locale padrão): ConfirmModal, PeopleMerge,
PhotoModal, VideoPlayer, PeopleDelete. Suite completa: PASS(234) FAIL(1) — única
falha pré-existente e não relacionada (`PersonFrames.test.jsx`).
