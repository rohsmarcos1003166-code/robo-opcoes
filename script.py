import yfinance as yf
import pandas as pd
import smtplib
from email.message import EmailMessage
import os

def formatar_tabela_html(titulo, ticker, df):
    if df.empty:
        return f"<h3>{titulo} ({ticker})</h3><p>Dados não disponíveis no momento.</p>"
    
    # Renomeando as colunas para o seu padrão
    df_fmt = df.copy()
    html_table = df_fmt.to_html(index=False, border=1, justify='center')
    
    return f"<h3>{titulo} - {ticker}</h3>{html_table}"

def buscar_dados_vix():
    try:
        vix = yf.Ticker("^VIX")
        vencimento = vix.options[0]
        opcoes = vix.option_chain(vencimento).calls[['contractSymbol', 'strike', 'volume']].head(10)
        opcoes.columns = ['Ativo', 'Strike', 'Volume'] # Padrão solicitado
        return formatar_tabela_html("Mercado Americano", "^VIX", opcoes)
    except:
        return "<h3>Mercado Americano (VIX)</h3><p>Falha ao extrair dados.</p>"

def buscar_dados_brasil():
    try:
        # Buscando PETR4 para extrair a cadeia de opções brasileira
        petr = yf.Ticker("PETR4.SA")
        vencimento = petr.options[0]
        opcoes = petr.option_chain(vencimento).calls[['contractSymbol', 'strike', 'volume']].head(10)
        
        # Ajustando nomes para o padrão: Ativo, Strike, Volume
        opcoes.columns = ['Ativo', 'Strike', 'Volume']
        
        # O 'strike' da B3 no Yahoo vem multiplicado por 1 ou 100, ajustamos conforme seu exemplo (36.00 ou 3600)
        return formatar_tabela_html("Mercado Brasileiro", "PETR4", opcoes)
    except:
        return "<h3>Mercado Brasileiro (PETR4)</h3><p>Falha ao extrair dados da B3.</p>"

# Montagem do corpo do e-mail
html_vix = buscar_dados_vix()
html_brasil = buscar_dados_brasil()

corpo_email = f"""
<html>
<body style="font-family: Arial, sans-serif;">
    <h2>Relatório Consolidado de Opções</h2>
    <div style="margin-bottom: 20px;">
        {html_vix}
    </div>
    <hr>
    <div style="margin-top: 20px;">
        {html_brasil}
    </div>
    <br>
    <p style="font-size: 10px; color: gray;">Exemplo de formato processado: Ativo PETRB360 | Strike 36.00 | Volume 18767</p>
</body>
</html>
"""

# Envio
msg = EmailMessage()
msg['Subject'] = "TABELA DE OPÇÕES: VIX & PETR4"
msg['From'] = "rohsmarcos1003166@gmail.com"
msg['To'] = "rohsmarcos1003166@gmail.com"
msg.add_alternative(corpo_email, subtype='html')

try:
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(msg['From'], os.environ.get('EMAIL_PASSWORD'))
        smtp.send_message(msg)
        print("Relatório enviado com sucesso!")
except Exception as e:
    print(f"Erro no envio: {e}")
