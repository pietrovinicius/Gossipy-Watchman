## v1.55 — 2026-06-07

### Tipo da mudança
docs

### Arquivos alterados
- Anotacoes.txt

### Impacto técnico/funcional
Verificação final da troca HOG→CNN: 252/252 testes passando, .env e .env.example
com FACE_DETECTION_MODEL/FACE_UPSAMPLE confirmados. Teste empírico com 6 frames
amostrados de vídeo real: HOG detectou 0 faces, CNN detectou 6 faces nos mesmos
frames (tempo médio 0.08s/frame com HOG vs 0.88s/frame com CNN — ~11x mais lento,
dentro da faixa 3-5x+ esperada para upsample=1 em CPU). Documenta Decisão #11
em Anotacoes.txt sobre a troca de modelo de detecção facial para CNN.
