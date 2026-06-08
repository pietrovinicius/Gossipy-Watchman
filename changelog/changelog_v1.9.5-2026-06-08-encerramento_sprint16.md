## v1.9.5 — 2026-06-08

### Tipo da mudança
chore

### Arquivos alterados
- Anotacoes.txt
- changelog/changelog_v1.9.5-2026-06-08-encerramento_sprint16.md

### Impacto técnico/funcional
Encerramento da Sprint 16 (Melhorias de Precisão no Reconhecimento Facial).

Verificação final executada:
- `pytest`: 398 testes passando (suíte completa, backend)
- `npm test`: 195 testes passando (33 arquivos, frontend)
- `npm run build`: build de produção concluído sem erros
- Teste manual de processamento (vídeo id=5, engine isolada em memória):
  5 tracks formados, 0 descartados por amostra insuficiente, 0 frames
  descartados pelo filtro de qualidade (footage de boa qualidade — não houve
  rosto pequeno/borrado nesta amostra), 1 pessoa nova + 4 aparições
  conhecidas resolvidas via votação k-NN

`Anotacoes.txt` atualizado com seção dedicada à Sprint 16, documentando as
três melhorias entregues (filtro de qualidade, FaceTracker por aparição
contínua, votação k-NN) e os resultados do teste manual.
