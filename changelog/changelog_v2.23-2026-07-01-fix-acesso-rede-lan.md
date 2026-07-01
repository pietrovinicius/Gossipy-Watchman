## v2.23 — 2026-07-01

### Tipo da mudança
fix

### Arquivos alterados
- frontend/src/services/api.js
- frontend/src/pages/Login.jsx
- frontend/src/components/VideoPlayer.jsx
- app/main.py
- Anotacoes.txt

### Impacto técnico/funcional
Corrige falha de acesso via rede local: o fallback de URL do backend
(`http://localhost:8002`) estava hardcoded no frontend, fazendo com que
outros computadores da rede tentassem chamar a API no próprio `localhost`
deles (backend inexistente ali) em vez do IP do servidor. Trocado para
`${window.location.protocol}//${window.location.hostname}:8002`,
resolvendo o host dinamicamente a partir da URL usada para abrir a página.

CORS em `app/main.py` só liberava o IP `192.168.100.70`; adicionado
`allow_origin_regex` cobrindo qualquer IP de rede local nas portas
5173/5174, já que a máquina pode ter múltiplas interfaces (Wi-Fi, VPN,
Ethernet) com IPs diferentes.

`Anotacoes.txt` atualizado: comando de start do uvicorn não usava
`--host 0.0.0.0`, então o backend escutava apenas em loopback
(127.0.0.1) e era inacessível de outras máquinas mesmo com o frontend
corrigido. Adicionada também seção de troubleshooting sobre Firewall do
Windows bloqueando as portas 5174/8002.
