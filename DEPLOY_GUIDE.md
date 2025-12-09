# 🚀 Guia de Deploy - Backend Gratuito

Este guia mostra como hospedar o backend de forma gratuita.

## 📋 Opções Gratuitas

### 1. Render.com (Recomendado) ⭐

**Vantagens:**
- 750 horas gratuitas por mês
- Deploy automático do GitHub
- SSL gratuito
- Fácil configuração

**Passos:**

1. **Crie uma conta:**
   - Acesse: https://render.com
   - Faça login com GitHub

2. **Crie um novo Web Service:**
   - Clique em "New" > "Web Service"
   - Conecte seu repositório GitHub
   - Selecione: `younglubz/Predictionarb`

3. **Configure o serviço:**
   - **Name:** `prediction-arbitrage-api` (ou qualquer nome)
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python run_server.py`
   - **Plan:** `Free`

4. **Variáveis de Ambiente (opcional):**
   - `PORT` - Render define automaticamente
   - `ENV=production` - Para desabilitar reload

5. **Deploy:**
   - Clique em "Create Web Service"
   - Aguarde o build (5-10 minutos)
   - Copie a URL: `https://seu-app.onrender.com`

### 2. Railway.app

**Vantagens:**
- $5 créditos gratuitos por mês
- Deploy automático
- Muito simples

**Passos:**

1. Acesse: https://railway.app
2. Faça login com GitHub
3. Clique em "New Project"
4. Selecione "Deploy from GitHub repo"
5. Escolha `younglubz/Predictionarb`
6. Railway detecta automaticamente e faz o deploy
7. Copie a URL gerada

### 3. Fly.io

**Vantagens:**
- 3 VMs compartilhadas gratuitas
- Muito rápido

**Passos:**

1. Instale o CLI: https://fly.io/docs/getting-started/installing-flyctl/
2. Execute: `fly launch`
3. Siga as instruções

## 🔧 Após o Deploy

### 1. Atualizar Frontend

Após obter a URL do backend (ex: `https://prediction-arbitrage-api.onrender.com`):

1. Edite `frontend/src/components/DashboardModern.js`
2. Encontre a linha com `API_URL`
3. Substitua pela URL do seu backend:

```javascript
const API_URL = process.env.NODE_ENV === 'production' 
  ? 'https://prediction-arbitrage-api.onrender.com' // SUA URL AQUI
  : 'http://localhost:8000';
```

4. Faça novo deploy do frontend:
```bash
cd frontend
npm run deploy
```

### 2. Testar

1. Acesse: https://younglubz.github.io/Predictionarb
2. O frontend deve conectar ao backend em produção
3. Verifique se as oportunidades aparecem

## ⚠️ Notas Importantes

- **Render:** O serviço pode "dormir" após 15 minutos de inatividade. O primeiro request pode demorar ~30s.
- **Railway:** Tem limite de créditos. Monitore o uso.
- **CORS:** Já está configurado para aceitar requisições de qualquer origem (`*`).

## 🔍 Troubleshooting

### Backend não inicia:
- Verifique os logs no painel do Render/Railway
- Confirme que `requirements.txt` está completo
- Verifique se a porta está correta (Render usa variável `PORT`)

### Frontend não conecta:
- Verifique se a URL da API está correta
- Confirme que o backend está rodando (acesse `/health`)
- Verifique o CORS no backend

### Erro 502/503:
- Pode ser que o serviço esteja "dormindo" (Render)
- Faça uma requisição e aguarde ~30s

## 📞 Suporte

Se tiver problemas, verifique:
1. Logs do backend no painel da plataforma
2. Console do navegador (F12)
3. Network tab para ver requisições

