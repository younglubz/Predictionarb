# -*- coding: utf-8 -*-
"""Sistema de notificacao por email para alertas de arbitragem"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()


class EmailNotifier:
    """
    Envia alertas por email quando oportunidades sao encontradas
    
    Suporta:
    - Gmail
    - Outlook/Hotmail
    - Yahoo
    - SMTP customizado
    """
    
    def __init__(self):
        # Configuracoes de email do .env
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.email_from = os.getenv("EMAIL_FROM", "")
        self.email_password = os.getenv("EMAIL_PASSWORD", "")
        self.email_to = os.getenv("EMAIL_TO", "")
        
        # Validacao
        self.enabled = bool(self.email_from and self.email_password and self.email_to)
        
        if not self.enabled:
            print("Email notifier desabilitado - configure EMAIL_FROM, EMAIL_PASSWORD e EMAIL_TO no .env")
    
    def send_opportunity_alert(self, opportunities: List[dict]) -> bool:
        """
        Envia alerta com oportunidades encontradas
        
        Args:
            opportunities: Lista de oportunidades com detalhes
        
        Returns:
            True se enviado com sucesso
        """
        if not self.enabled:
            return False
        
        if not opportunities:
            return False
        
        try:
            # Cria mensagem
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"🚨 {len(opportunities)} Oportunidades de Arbitragem Encontradas!"
            msg['From'] = self.email_from
            msg['To'] = self.email_to
            
            # Corpo do email (texto simples)
            text_body = self._create_text_body(opportunities)
            
            # Corpo do email (HTML)
            html_body = self._create_html_body(opportunities)
            
            # Anexa ambas as versoes
            part1 = MIMEText(text_body, 'plain')
            part2 = MIMEText(html_body, 'html')
            
            msg.attach(part1)
            msg.attach(part2)
            
            # Envia email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_from, self.email_password)
                server.send_message(msg)
            
            print(f"✓ Email enviado com sucesso para {self.email_to}")
            return True
            
        except Exception as e:
            print(f"✗ Erro ao enviar email: {e}")
            return False
    
    def send_daily_summary(self, stats: dict) -> bool:
        """
        Envia resumo diario do monitoramento
        
        Args:
            stats: Estatisticas do dia
        
        Returns:
            True se enviado com sucesso
        """
        if not self.enabled:
            return False
        
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"📊 Resumo Diario - Arbitragem Prediction Markets"
            msg['From'] = self.email_from
            msg['To'] = self.email_to
            
            # Corpo texto
            text_body = f"""
Resumo Diario - {datetime.now().strftime('%d/%m/%Y')}

Mercados Monitorados: {stats.get('total_markets', 0)}
Oportunidades Encontradas: {stats.get('opportunities', 0)}
Melhor ROI: {stats.get('best_roi', 0):.1f}%

Dashboard: http://localhost:8000
"""
            
            # Corpo HTML
            html_body = f"""
<html>
<head>
<style>
    body {{ font-family: Arial, sans-serif; }}
    .header {{ background: #4CAF50; color: white; padding: 20px; }}
    .stats {{ margin: 20px; }}
    .stat-box {{ display: inline-block; margin: 10px; padding: 15px; background: #f5f5f5; border-radius: 5px; }}
</style>
</head>
<body>
    <div class="header">
        <h1>📊 Resumo Diario</h1>
        <p>{datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
    </div>
    <div class="stats">
        <div class="stat-box">
            <h3>Mercados</h3>
            <p>{stats.get('total_markets', 0)}</p>
        </div>
        <div class="stat-box">
            <h3>Oportunidades</h3>
            <p>{stats.get('opportunities', 0)}</p>
        </div>
        <div class="stat-box">
            <h3>Melhor ROI</h3>
            <p>{stats.get('best_roi', 0):.1f}%</p>
        </div>
    </div>
    <p><a href="http://localhost:8000">Ver Dashboard</a></p>
</body>
</html>
"""
            
            part1 = MIMEText(text_body, 'plain')
            part2 = MIMEText(html_body, 'html')
            
            msg.attach(part1)
            msg.attach(part2)
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_from, self.email_password)
                server.send_message(msg)
            
            print(f"✓ Resumo diario enviado para {self.email_to}")
            return True
            
        except Exception as e:
            print(f"✗ Erro ao enviar resumo: {e}")
            return False
    
    def _create_text_body(self, opportunities: List[dict]) -> str:
        """Cria corpo do email em texto simples"""
        lines = [
            f"🚨 ALERTA DE ARBITRAGEM",
            f"",
            f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            f"",
            f"{len(opportunities)} oportunidades encontradas:",
            f"",
        ]
        
        for i, opp in enumerate(opportunities[:5], 1):
            m1 = opp['market1']
            m2 = opp['market2']
            
            lines.extend([
                f"--- Oportunidade #{i} ---",
                f"",
                f"Exchange A: {m1.exchange}",
                f"Mercado: {m1.question[:60]}...",
                f"Preco: ${m1.price:.3f}",
                f"",
                f"Exchange B: {m2.exchange}",
                f"Mercado: {m2.question[:60]}...",
                f"Preco: ${m2.price:.3f}",
                f"",
                f"Lucro Liquido: ${opp.get('net_profit', 0):.3f} ({opp.get('net_profit_pct', 0):.1f}% ROI)",
                f"Similaridade: {opp.get('similarity', 0)*100:.0f}%",
                f"",
            ])
        
        lines.append(f"Dashboard: http://localhost:8000")
        
        return "\n".join(lines)
    
    def _create_html_body(self, opportunities: List[dict]) -> str:
        """Cria corpo do email em HTML"""
        html = f"""
<html>
<head>
<style>
    body {{
        font-family: Arial, sans-serif;
        margin: 0;
        padding: 0;
        background-color: #f5f5f5;
    }}
    .container {{
        max-width: 800px;
        margin: 20px auto;
        background: white;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }}
    .header {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 30px;
        text-align: center;
    }}
    .content {{
        padding: 30px;
    }}
    .opportunity {{
        border: 2px solid #e0e0e0;
        border-radius: 8px;
        padding: 20px;
        margin: 20px 0;
        background: #fafafa;
    }}
    .market {{
        margin: 15px 0;
        padding: 15px;
        background: white;
        border-radius: 5px;
        border-left: 4px solid #667eea;
    }}
    .market-label {{
        font-weight: bold;
        color: #667eea;
        margin-bottom: 5px;
    }}
    .profit {{
        background: #4CAF50;
        color: white;
        padding: 10px 20px;
        border-radius: 5px;
        text-align: center;
        font-size: 18px;
        font-weight: bold;
        margin: 15px 0;
    }}
    .stats {{
        display: flex;
        justify-content: space-around;
        margin: 15px 0;
    }}
    .stat {{
        text-align: center;
    }}
    .stat-value {{
        font-size: 24px;
        font-weight: bold;
        color: #667eea;
    }}
    .stat-label {{
        color: #666;
        font-size: 12px;
    }}
    .footer {{
        background: #f5f5f5;
        padding: 20px;
        text-align: center;
        color: #666;
    }}
    .button {{
        display: inline-block;
        background: #667eea;
        color: white;
        padding: 12px 30px;
        text-decoration: none;
        border-radius: 5px;
        margin: 10px;
    }}
</style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚨 ALERTA DE ARBITRAGEM</h1>
            <p>{datetime.now().strftime('%d de %B de %Y - %H:%M')}</p>
        </div>
        
        <div class="content">
            <h2>{len(opportunities)} Oportunidades Encontradas!</h2>
"""
        
        for i, opp in enumerate(opportunities[:5], 1):
            m1 = opp['market1']
            m2 = opp['market2']
            
            html += f"""
            <div class="opportunity">
                <h3>Oportunidade #{i}</h3>
                
                <div class="market">
                    <div class="market-label">Exchange A: {m1.exchange}</div>
                    <div><strong>Mercado:</strong> {m1.question[:80]}...</div>
                    <div><strong>Outcome:</strong> {m1.outcome}</div>
                    <div><strong>Preco:</strong> ${m1.price:.3f}</div>
                    <div><strong>Liquidez:</strong> ${m1.liquidity:.0f}</div>
                </div>
                
                <div class="market">
                    <div class="market-label">Exchange B: {m2.exchange}</div>
                    <div><strong>Mercado:</strong> {m2.question[:80]}...</div>
                    <div><strong>Outcome:</strong> {m2.outcome}</div>
                    <div><strong>Preco:</strong> ${m2.price:.3f}</div>
                    <div><strong>Liquidez:</strong> ${m2.liquidity:.0f}</div>
                </div>
                
                <div class="profit">
                    💰 Lucro Liquido: ${opp.get('net_profit', 0):.3f} ({opp.get('net_profit_pct', 0):.1f}% ROI)
                </div>
                
                <div class="stats">
                    <div class="stat">
                        <div class="stat-value">{opp.get('similarity', 0)*100:.0f}%</div>
                        <div class="stat-label">Similaridade</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">${opp.get('gross_profit', 0):.3f}</div>
                        <div class="stat-label">Lucro Bruto</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">${opp.get('total_fees', 0):.3f}</div>
                        <div class="stat-label">Taxas</div>
                    </div>
                </div>
            </div>
"""
        
        html += """
        </div>
        
        <div class="footer">
            <a href="http://localhost:8000" class="button">Ver Dashboard Completo</a>
            <p>Sistema de Arbitragem em Prediction Markets</p>
        </div>
    </div>
</body>
</html>
"""
        
        return html
    
    def test_connection(self) -> bool:
        """Testa conexao SMTP"""
        if not self.enabled:
            print("✗ Email nao configurado")
            return False
        
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10) as server:
                server.starttls()
                server.login(self.email_from, self.email_password)
            
            print(f"✓ Conexao SMTP OK ({self.smtp_server}:{self.smtp_port})")
            return True
            
        except Exception as e:
            print(f"✗ Erro na conexao SMTP: {e}")
            return False


# Teste rapido
if __name__ == "__main__":
    print("\nTestando Email Notifier...\n")
    
    notifier = EmailNotifier()
    
    if notifier.enabled:
        print("Testando conexao SMTP...")
        if notifier.test_connection():
            print("\n✓ Sistema de email configurado corretamente!")
        else:
            print("\n✗ Erro na configuracao de email")
    else:
        print("Email nao configurado. Adicione ao .env:")
        print("\nEMAIL_FROM=seu_email@gmail.com")
        print("EMAIL_PASSWORD=sua_senha_ou_app_password")
        print("EMAIL_TO=destino@email.com")
        print("\n# Opcional:")
        print("SMTP_SERVER=smtp.gmail.com")
        print("SMTP_PORT=587")

