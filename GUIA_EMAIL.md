# Guia de Configuracao de Email

## Sistema de Alertas por Email

O sistema agora envia alertas automaticos por email quando oportunidades de arbitragem sao encontradas!

---

## Configuracao Rapida

### 1. Editar arquivo `.env`

Adicione estas linhas ao arquivo `.env` na raiz do projeto:

```env
# Configuracao de Email
EMAIL_FROM=seu_email@gmail.com
EMAIL_PASSWORD=sua_senha_ou_app_password
EMAIL_TO=destino@email.com

# Servidor SMTP (opcional - padrao Gmail)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

---

## Configuracao por Provedor

### Gmail (Recomendado)

#### Passo 1: Criar App Password
1. Acesse: https://myaccount.google.com/apppasswords
2. Digite um nome (ex: "Arbitragem Bot")
3. Clique em "Gerar"
4. Copie a senha gerada (16 caracteres)

#### Passo 2: Configurar `.env`
```env
EMAIL_FROM=seu_email@gmail.com
EMAIL_PASSWORD=abcd efgh ijkl mnop  # App Password gerado
EMAIL_TO=destino@email.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

**Importante:** Use App Password, NAO sua senha normal!

---

### Outlook/Hotmail

#### Configuracao `.env`:
```env
EMAIL_FROM=seu_email@outlook.com
EMAIL_PASSWORD=sua_senha
EMAIL_TO=destino@email.com
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
```

**Nota:** Pode precisar habilitar "Less secure app access" nas configuracoes.

---

### Yahoo Mail

#### Configuracao `.env`:
```env
EMAIL_FROM=seu_email@yahoo.com
EMAIL_PASSWORD=sua_senha_app
EMAIL_TO=destino@email.com
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
```

**Nota:** Gere uma senha de app em: https://login.yahoo.com/account/security

---

### Outros Provedores

Para SMTP customizado:
```env
EMAIL_FROM=seu_email@dominio.com
EMAIL_PASSWORD=sua_senha
EMAIL_TO=destino@email.com
SMTP_SERVER=smtp.seu-provedor.com
SMTP_PORT=587  # ou 465 para SSL
```

---

## Testar Configuracao

### Teste Rapido
```powershell
py -3.12 test_email.py
```

Este script:
1. Verifica se email esta configurado
2. Testa conexao SMTP
3. Envia email de teste com oportunidade fake
4. Envia resumo diario de teste

### Resultado Esperado
```
==================================================
  TESTE DO SISTEMA DE EMAIL
==================================================

1. Testando conexao SMTP...
✓ Conexao SMTP OK (smtp.gmail.com:587)

2. Criando oportunidade de exemplo...

3. Enviando email de teste...
✓ Email enviado com sucesso para destino@email.com

==================================================
  ✓ EMAIL ENVIADO COM SUCESSO!
==================================================

Verifique sua caixa de entrada: destino@email.com
```

---

## Tipos de Email

### 1. Alerta de Oportunidade
Enviado automaticamente quando oportunidades sao encontradas.

**Conteudo:**
- Numero de oportunidades
- Detalhes de cada oportunidade (ate 5)
- Exchange A e B
- Precos
- Lucro liquido e ROI
- Similaridade
- Link para dashboard

### 2. Resumo Diario
Enviado uma vez por dia com estatisticas.

**Conteudo:**
- Total de mercados monitorados
- Oportunidades encontradas
- Melhor ROI do dia
- Link para dashboard

---

## Integracao com Monitor

O sistema automaticamente envia alertas quando usado com:

### Monitor Manual
```powershell
py -3.12 monitor.py
```

### Monitor Diario Automatico
```powershell
.\start_daily_monitor.ps1
```

### API/Dashboard
```powershell
py -3.12 run_server.py
```

---

## Troubleshooting

### Email nao chega

1. **Verifique spam/lixo eletronico**
   - Marque como "Nao e spam"
   - Adicione remetente aos contatos

2. **Verifique credenciais**
   ```powershell
   py -3.12 test_email.py
   ```

3. **Gmail: Use App Password**
   - NAO use sua senha normal
   - Gere em: https://myaccount.google.com/apppasswords

4. **Verifique firewall/antivirus**
   - Pode estar bloqueando porta 587

### Erro: Authentication failed

**Gmail:**
- Use App Password (16 caracteres)
- Habilite 2FA primeiro
- Acesse: https://myaccount.google.com/apppasswords

**Outlook:**
- Habilite "Less secure app access"
- Ou use senha de app

**Yahoo:**
- Gere senha de app
- Acesse: https://login.yahoo.com/account/security

### Erro: Connection refused

- Verifique SMTP_SERVER esta correto
- Verifique SMTP_PORT (587 ou 465)
- Firewall pode estar bloqueando

### Erro: Timeout

- Conexao de internet lenta
- Servidor SMTP indisponivel
- Aumentar timeout no codigo

---

## Personalizacao

### Mudar Formato do Email

Edite `email_notifier.py`:

```python
def _create_html_body(self, opportunities: List[dict]) -> str:
    # Customize HTML aqui
    pass
```

### Adicionar Mais Destinatarios

```env
EMAIL_TO=email1@gmail.com,email2@outlook.com,email3@yahoo.com
```

### Mudar Frequencia de Alertas

Edite `config.py`:
```python
UPDATE_INTERVAL = 60  # Segundos entre verificacoes
```

---

## Seguranca

### Proteja suas Credenciais

1. **NUNCA commite `.env`**
   ```
   # .gitignore
   .env
   ```

2. **Use App Passwords**
   - Mais seguro que senha principal
   - Pode ser revogado sem afetar conta

3. **Permissoes minimas**
   - Somente envio de email
   - Sem acesso a outros dados

### Boas Praticas

- ✓ Use email dedicado para o bot
- ✓ Habilite 2FA
- ✓ Use App Passwords
- ✓ Revise emails enviados regularmente
- ✗ NAO compartilhe credenciais
- ✗ NAO use senha principal

---

## Exemplo Completo

### Arquivo `.env`:
```env
# Email Configuration
EMAIL_FROM=meu.bot.arbitragem@gmail.com
EMAIL_PASSWORD=abcd efgh ijkl mnop
EMAIL_TO=meu.email.pessoal@gmail.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

### Teste:
```powershell
py -3.12 test_email.py
```

### Monitor com Email:
```powershell
.\start_daily_monitor.ps1
```

### Resultado:
- ✓ Alertas automaticos quando oportunidades aparecem
- ✓ Email bonito em HTML
- ✓ Resumo diario as 20h
- ✓ Links diretos para dashboard

---

## FAQ

**P: Preciso deixar o computador ligado?**
R: Sim, para o monitor continuo. Ou use servidor/VPS.

**P: Quantos emails serao enviados?**
R: Somente quando oportunidades sao encontradas + 1 resumo diario.

**P: Posso usar email corporativo?**
R: Sim, se SMTP for acessivel e permitido pela empresa.

**P: Funciona com 2FA?**
R: Sim! Use App Password em vez da senha normal.

**P: Email esta em spam?**
R: Normal no inicio. Marque como "Nao e spam" e adicione aos contatos.

**P: Posso enviar para varios emails?**
R: Sim, separe por virgula no EMAIL_TO.

---

## Suporte

Se problemas persistirem:

1. Execute: `py -3.12 test_email.py`
2. Verifique output completo
3. Confirme credenciais no `.env`
4. Teste com outro provedor

---

**Sistema de alertas pronto para notificar oportunidades em tempo real!** 📧🚨

