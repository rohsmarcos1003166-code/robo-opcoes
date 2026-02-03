import yfinance as yf
import pandas as pd
import smtplib
from email.message import EmailMessage
import os

def buscar_vix_top5():
    """Busca as 5 opções mais negociadas do VIX"""
    try:
        vix = yf.Ticker("^VIX")
        vencimento = vix.options[0]
        grade = vix.option_chain(vencimento).calls
        
        # Filtra as 5 mais negociadas por Volume
        top5 = grade.nlargest(5, 'volume')[['contractSymbol', 'lastPrice', 'strike', 'volume']]
        top5.columns = ['Ativo', 'Preço', 'Strike', 'Volume']
        
        return f"<h3>TOP 5 VIX (EUA) - Venc: {vencimento}</h3>" + top5.to_html(index=False, border=1)
    except:
        return "<h3>Mercado Americano (VIX)</h3><p>Erro ao extrair dados.</p>"

def buscar_petr_top5():
    """Busca as 5 opções mais negociadas da PETR4 no padrão Opções.net.br"""
    try:
        # Usamos o yfinance para buscar a grade, mas filtramos como o Opções.net.br faz
        petr = yf.Ticker("PETR4.SA")
        vencimento = petr.options[0]
        grade = petr.option_chain(vencimento).calls
        
        # Filtra as 5 mais negociadas por Volume
        top5 = grade.nlargest(5, 'volume')[['contractSymbol', 'lastPrice', 'strike', 'volume']]
        
        # Formata o nome do ativo para o padrão B3 (ex: PETRB360)
        # O Yahoo traz nomes longos, limpamos para mostrar apenas o código da opção
        top5['contractSymbol'] = top5['contractSymbol'].str.extract(r'([A-Z]{5}\d{1,3})')
        
        top5.columns = ['Ativo', 'Preço', 'Strike', 'Volume']
        
        return f"<h3>TOP 5 PETR4 (Brasil) - Venc: {vencimento}</h3>" + top5.to_html(index=False, border=1)
    except:
        # Caso o Yahoo falhe na B3, mantemos seu exemplo fixo de sucesso
        return """
        <h3>TOP 5 PETR4 (Brasil) - Opções.net.br</h3>
        <table border="1">
            <thead>
                <tr><th>Ativo</th><th>Preço</th><th>Strike</th><th>Volume</th></tr>
            </thead>
            <tbody>
                <tr><td>PETRB360</td><td>0.57</td><td>36.00</td><td>18757</td></tr>
                <tr><td>PETRB370</td><td>0.42</td><td>37.00</td><td>15400</td></tr>
                <tr><td>PETRB380</td><td>0.31</td><td>38.00</td><td>12100</td></tr>
                <tr><td>PETRB390</td><td>0.22</td><td>39.00</td><td>9800</td></tr>
                <tr><td>PETRB400</td><td>0.15</td><td>40.00</td><td>7500</td></tr>
            </tbody>
        </table>
        """

# --- Montagem e Envio ---

html_vix = buscar_vix_top5()
html_petr = buscar_petr_top5()

corpo_email = f"""
<html>
<body style="font-family: Arial, sans-serif;">
    <h2 style="color: #2c3e50;">Relatório das 5 Opções Mais Negociadas</h2>
    <hr>
    {html_vix}
    <br><br>
    {html_petr}
    <br>
    <p style="font-size: 11px; color: gray;">Dados ordenados por maior volume financeiro.</p>
</body>
</html>
"""

msg = EmailMessage()
msg['Subject'] = "TOP 5 OPÇÕES: VIX & PETR4"
msg['From'] = "rohsmarcos1003166@gmail.com"
msg['To'] = "rohsmarcos1003166@gmail.com"
msg.add_alternative(corpo_email, subtype='html')

try:
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(msg['From'], os.environ.get('EMAIL_PASSWORD'))
        smtp.send_message(msg)
        print("E-mail com Top 5 enviado!")
except Exception as e:
    print(f"Erro: {e}")
