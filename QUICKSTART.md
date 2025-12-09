# 🚀 Guia Rápido de Inicialização

## Passo a Passo

### 1. Instalar Dependências do Backend

```powershell
pip install -r requirements.txt
```

### 2. Iniciar o Servidor Backend

```powershell
.\start.ps1
```

Ou manualmente:
```powershell
python run_server.py
```

O servidor estará rodando em `http://localhost:8000`

### 3. Instalar Dependências do Frontend

Abra um novo terminal e execute:

```powershell
cd frontend
npm install
```

### 4. Iniciar o Frontend

```powershell
npm start
```

Ou use o script:
```powershell
.\start_frontend.ps1
```

O dashboard estará disponível em `http://localhost:3000`

## Verificação

1. **Backend**: Acesse `http://localhost:8000/docs` para ver a documentação da API
2. **Frontend**: Acesse `http://localhost:3000` para ver o dashboard

## Estrutura de URLs

- **API Backend**: `http://localhost:8000`
  - `/opportunities` - Lista oportunidades
  - `/markets` - Lista mercados
  - `/stats` - Estatísticas
  - `/ws` - WebSocket para atualizações
  - `/docs` - Documentação Swagger

- **Frontend**: `http://localhost:3000`
  - Dashboard principal com todas as visualizações

## Troubleshooting

### Erro: "Module not found"
- Certifique-se de que todas as dependências foram instaladas
- Execute `pip install -r requirements.txt` novamente

### Erro: "Port already in use"
- Altere a porta no `run_server.py` ou pare o processo que está usando a porta

### Frontend não conecta ao backend
- Verifique se o backend está rodando
- Verifique se a URL no `App.js` está correta
- Verifique o CORS no `api.py`

### WebSocket não conecta
- Verifique se o backend está rodando
- Verifique se a porta 8000 está acessível
- Verifique o console do navegador para erros

## Próximos Passos

1. Configure as variáveis de ambiente em `.env` se necessário
2. Ajuste os thresholds em `config.py` conforme necessário
3. Explore as oportunidades de arbitragem no dashboard!

