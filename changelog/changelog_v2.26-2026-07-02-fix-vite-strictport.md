## v2.26 — 2026-07-02

### Tipo da mudança
fix

### Arquivos alterados
- frontend/vite.config.js

### Impacto técnico/funcional
Corrige degradação silenciosa de acesso via rede quando a porta 5174
já está em uso (ex.: instância anterior do `npm run dev` não encerrada,
ou `iniciar.bat` executado com outro processo já de pé). Nesse caso o
Vite fazia fallback automático para a próxima porta livre (ex.: 5175),
mas ao fazer isso o binding de rede (`host: true`) deixava de ser
aplicado — o servidor passava a escutar apenas `127.0.0.1`, tornando o
app inacessível para outras máquinas da rede sem nenhum erro visível,
só a mensagem discreta "Network: use --host to expose".

Adicionado `strictPort: true` em `server` — agora, se a porta 5174
estiver ocupada, o Vite falha imediatamente com erro claro
(`Port 5174 is already in use`) em vez de subir silenciosamente em
outra porta sem expor rede. Torna o problema visível e óbvio de
diagnosticar (matar o processo antigo) em vez de um "funciona só em
localhost" silencioso.
