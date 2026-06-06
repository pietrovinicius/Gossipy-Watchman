## v0.15 — 2026-06-06

### Tipo da mudança
chore

### Arquivos alterados
- Todos os arquivos criados durante a Sprint 2

### Impacto técnico/funcional
Encerramento da Sprint 2. Verificação final:
- 64 testes passando (27 Sprint 1 + 37 Sprint 2)
- Pipeline CV completo: frame_service → face_service → person_service → appearance_service → video_worker
- Zero imports de cv2/face_recognition/numpy em app/main.py ou app/api/
- setuptools<71 pinado para compatibilidade de face-recognition com Python 3.14

Sprint 2 completa sem dívida técnica.
