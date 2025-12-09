# 🚀 Links de Acesso ao Dashboard

## ✅ Backend (API) - RODANDO

O servidor backend está rodando na porta 8000.

### Links Disponíveis:

- **API Principal**: http://localhost:8000
- **Documentação Swagger**: http://localhost:8000/docs
- **API ReDoc**: http://localhost:8000/redoc
- **WebSocket**: ws://localhost:8000/ws

### Endpoints da API:

- `GET /` - Informações da API
- `GET /opportunities` - Lista oportunidades de arbitragem
- `GET /markets` - Lista todos os mercados
- `GET /stats` - Estatísticas gerais
- `WebSocket /ws` - Atualizações em tempo real

## ⚠️ Frontend - PRECISA INSTALAR DEPENDÊNCIAS

O frontend ainda não está rodando. Para iniciar:

### Passo 1: Instalar dependências do frontend

```powershell
cd frontend
npm install
```

### Passo 2: Iniciar o servidor de desenvolvimento

```powershell
npm start
```

### Após iniciar, o frontend estará disponível em:

- **Dashboard**: http://localhost:3000

## 📋 Resumo dos Links

| Serviço | URL | Status |
|---------|-----|--------|
| Backend API | http://localhost:8000 | ✅ Rodando |
| API Docs | http://localhost:8000/docs | ✅ Disponível |
| Frontend Dashboard | http://localhost:3000 | ⚠️ Precisa iniciar |

## 🎯 Como Usar

1. **Backend já está rodando** - você pode acessar a documentação da API em http://localhost:8000/docs

2. **Para iniciar o frontend**, abra um novo terminal e execute:
   ```powershell
   cd frontend
   npm install
   npm start
   ```

3. **Acesse o dashboard** em http://localhost:3000 quando o frontend estiver rodando

## 🔍 Verificar Status

Para verificar se os servidores estão rodando:

```powershell
netstat -ano | findstr ":8000 :3000"
```

Você deve ver:
- Porta 8000: Backend (FastAPI)
- Porta 3000: Frontend (React) - quando iniciado

