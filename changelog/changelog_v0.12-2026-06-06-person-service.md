## v0.12 — 2026-06-06

### Tipo da mudança
feat

### Arquivos alterados
- app/services/person_service.py
- tests/unit/test_person_service.py

### Impacto técnico/funcional
Implementa get_all_embeddings() com carregamento de .npy por person_id e
save_new_person() que persiste Person no banco e salva .jpg + .npy em storage/faces/.
Pessoas sem arquivo .npy em disco são ignoradas com log de aviso.
TDD: 6 testes com banco em memória e mock de cv2.imwrite/np.save, todos passando.
