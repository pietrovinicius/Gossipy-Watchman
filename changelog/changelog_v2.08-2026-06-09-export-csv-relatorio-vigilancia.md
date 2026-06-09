## v2.08 — 2026-06-09

### Tipo da mudança
feat

### Arquivos alterados
- app/services/export_service.py
- tests/unit/test_export_service.py
- app/core/settings.py
- frontend/package.json

### Impacto técnico/funcional

**feat(export): reformula CSV para relatório de vigilância CCTV**

O CSV anterior exportava 9 colunas com dados brutos e sem contexto agregado.
O novo relatório tem 20 colunas organizadas para uso operacional por vigilante de circuito interno.

**Colunas adicionadas (delimitador agora é `;` para compatibilidade com Excel/BR):**

| Coluna | Descrição |
|---|---|
| `aparicao_num` | Número sequencial da aparição (1ª, 2ª, 3ª...) |
| `inicio_formatado` | Início em MM:SS (ex.: 02:05) |
| `fim_formatado` | Fim em MM:SS |
| `presente_por_s` / `presente_por_formatado` | Duração da aparição |
| `primeira_vez_s` / `primeira_vez_formatado` | Primeira vez que a pessoa apareceu no vídeo |
| `ultima_vez_s` / `ultima_vez_formatado` | Última vez que a pessoa apareceu |
| `total_aparicoes_no_video` | Quantas vezes a pessoa passou pelo campo |
| `total_presente_no_video_s` | Tempo total acumulado da pessoa no vídeo |
| `video_data_upload` | Data/hora do upload (DD/MM/YYYY HH:MM:SS) |

**Colunas renomeadas para clareza:**
- `entrada_segundos` → `inicio_s`
- `saida_segundos` → `fim_s`
- `duracao_segundos` → `presente_por_s`

Subquery SQLAlchemy calcula agregados (first_seen, last_seen, total_aprs, total_secs)
por (pessoa, vídeo) em uma única passagem pelo banco.
