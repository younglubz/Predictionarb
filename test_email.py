# -*- coding: utf-8 -*-
"""Teste do sistema de email"""
from email_notifier import EmailNotifier
from exchanges.base import Market
from datetime import datetime

print("\n" + "="*50)
print("  TESTE DO SISTEMA DE EMAIL")
print("="*50 + "\n")

# Inicializa notifier
notifier = EmailNotifier()

if not notifier.enabled:
    print("Email nao configurado!")
    print("\nPara configurar, adicione ao arquivo .env:\n")
    print("# Configuracao de Email")
    print("EMAIL_FROM=seu_email@gmail.com")
    print("EMAIL_PASSWORD=sua_senha_app")
    print("EMAIL_TO=destino@email.com")
    print("\n# Para Gmail:")
    print("SMTP_SERVER=smtp.gmail.com")
    print("SMTP_PORT=587")
    print("\n# Para Outlook/Hotmail:")
    print("SMTP_SERVER=smtp-mail.outlook.com")
    print("SMTP_PORT=587")
    print("\n# Para Yahoo:")
    print("SMTP_SERVER=smtp.mail.yahoo.com")
    print("SMTP_PORT=587")
    print("\nIMPORTANTE:")
    print("- Gmail: Use 'App Password' (nao sua senha normal)")
    print("  https://myaccount.google.com/apppasswords")
    print("- Outlook: Habilite 'Less secure app access'")
    print()
    exit(1)

# Testa conexao
print("1. Testando conexao SMTP...")
if not notifier.test_connection():
    print("\nFalha na conexao. Verifique:")
    print("- EMAIL_FROM esta correto")
    print("- EMAIL_PASSWORD esta correto")
    print("- SMTP_SERVER e SMTP_PORT estao corretos")
    print("- Firewall/antivirus nao esta bloqueando")
    exit(1)

# Cria oportunidade de exemplo
print("\n2. Criando oportunidade de exemplo...")
market1 = Market(
    exchange="polymarket",
    market_id="test1",
    question="Trump wins 2024 election?",
    outcome="YES",
    price=0.60,
    volume_24h=10000,
    liquidity=50000,
    expires_at=datetime(2024, 11, 5),
    url="https://polymarket.com/test1"
)

market2 = Market(
    exchange="kalshi",
    market_id="test2",
    question="Trump wins 2024 election?",
    outcome="YES",
    price=0.65,
    volume_24h=8000,
    liquidity=30000,
    expires_at=datetime(2024, 11, 5),
    url="https://kalshi.com/test2"
)

opportunities = [{
    'market1': market1,
    'market2': market2,
    'similarity': 0.95,
    'gross_profit': 0.05,
    'total_fees': 0.024,
    'net_profit': 0.026,
    'net_profit_pct': 4.3
}]

print("\n3. Enviando email de teste...")
success = notifier.send_opportunity_alert(opportunities)

if success:
    print("\n" + "="*50)
    print("  ✓ EMAIL ENVIADO COM SUCESSO!")
    print("="*50)
    print(f"\nVerifique sua caixa de entrada: {notifier.email_to}")
    print("\nSe nao recebeu:")
    print("- Verifique spam/lixo eletronico")
    print("- Aguarde alguns minutos")
    print("- Verifique se EMAIL_TO esta correto")
    print()
else:
    print("\n" + "="*50)
    print("  ✗ FALHA AO ENVIAR EMAIL")
    print("="*50)
    print("\nPossiveis causas:")
    print("- Senha incorreta")
    print("- 2FA habilitado sem App Password")
    print("- SMTP bloqueado pelo provedor")
    print()

# Teste de resumo diario
print("\n4. Testando resumo diario...")
stats = {
    'total_markets': 1177,
    'opportunities': 3,
    'best_roi': 4.3
}

notifier.send_daily_summary(stats)

