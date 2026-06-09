## v2.12 — 2026-06-09

### Tipo da mudança
fix

### Arquivos alterados
- frontend/src/pages/VideoDetail.jsx

### Impacto técnico/funcional

**fix(videodetail): corrige fundo transparente do player sticky**

- `bg-background` não existe no Tailwind config do projeto → wrapper sticky era transparente.
- Substituído por `bg-bg` (token correto: `rgb(var(--color-bg) / 1)`).
- Adicionado `shadow-sm` para separação visual durante o scroll.
- Resultado: conteúdo que passa sob o player não vaza mais visualmente sobre os botões de velocidade.
