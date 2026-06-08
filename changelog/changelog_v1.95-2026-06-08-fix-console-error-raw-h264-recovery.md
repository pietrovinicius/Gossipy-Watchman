## v1.9.5 — 2026-06-08

### Tipo da mudança
fix

### Arquivos alterados
- app/services/conversion_service.py
- tests/unit/test_conversion_service.py

### Impacto técnico/funcional
Corrige o erro de falha no reparo (exit status 183) ao processar vídeos MP4 cujos cabeçalhos/metadados "moov atom" foram completamente omitidos ou perdidos (gravações de câmeras de segurança interrompidas de maneira abrupta). Adiciona uma rotina de recuperação por fallback que extrai a stream H.264 crua (Annex B) do bloco "mdat" do arquivo e a reconstrói usando ffmpeg, tornando o vídeo legível pelo OpenCV e restaurando seu processamento.
