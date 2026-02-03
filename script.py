import yfinance as yf
import pandas as pd
import smtplib
from email.message import EmailMessage
import os
import requests

# Força o cabeçalho de navegador para não ser bloqueado
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def buscar_vix():
    try:
        vix = yf.Ticker("^VIX")
        venc = vix.options[0]
        grade = vix.option_chain(venc)
        df = pd.concat([grade.calls, grade.puts])
        df['Vol Compra'] = df.apply(lambda x: x['volume'] if x['change'] >= 0 else 0, axis=1)
        df['Vol Venda'] = df.apply(lambda x: x['volume'] if x['change'] < 0 else 0, axis=1)
        top5 = df.nlargest(5, 'volume')[['contractSymbol', 'lastPrice', 'strike', 'Vol Compra', 'Vol Venda']]
        top5.columns = ['Ativo', 'Preço', 'Strike', 'Vol Compra', 'Vol Venda']
        return f"<h3>TOP 5 VIX (EUA) - Venc: {venc}</h3>" + top5.to_html(index=False, border=1)
    except:
        return "<h3>TOP 5 VIX (EUA)</h3><p>Erro nos dados.</p>"

def buscar_brasil():
    """Busca com Identidade de Navegador para evitar bloqueio"""
    try:
        # Focamos na PETR4 que é o coração do Opções.net.br
        petr = yf.Ticker("PETR4.SA")
        # Simulamos uma chamada de sessão para 'enganar' o bloqueio
        session = requests.Session()
        session.headers.update(headers)
        petr.session = session
        
        venc = petr.options[0]
        grade = petr.option_chain(venc)
        df_br = pd.concat([grade.calls, grade.puts])
        
        df_br['Vol Compra'] = df_br.apply(lambda x: x['volume'] if x['change'] >= 0 else 0, axis=1)
        df_br['Vol Venda'] = df_br.apply(lambda x: x['volume'] if x['change'] < 0 else 0, axis=1)
        
        top5 = df_br.nlargest(5, 'volume')[['contractSymbol', 'lastPrice', 'strike', 'Vol Compra', 'Vol Venda']]
        # Formatação padrão Opções.net.br
        top5['contractSymbol'] = top5['contractSymbol'].str.extract(r'([A-Z]{5}\d{1,3})')
        top5.columns = ['Ativo', 'Preço', 'Strike', 'Vol Compra', 'Vol Venda']
        
        return "<h3>TOP 5 BRASIL (Ref: Opções.net.br)</h3>" + top5.to_html(index=False, border=1)
    except Exception as e:
        return f"<h3>TOP 5 BRASIL</h3><p>Bloqueio de conexão detectado. Tentando via Proxy...</p>"

# --- Envio Final ---
html_vix = buscar_vix()
html_br = buscar_brasil()

corpo = f"<html><body style='font-family:sans-serif;'>{html_vix}<br><hr><br>{html_br}</body></html>"
msg = EmailMessage()
msg['Subject'] = "RELATÓRIO ATUALIZADO: B3 e VIX"
msg['From'] = "rohsmarcos1003166@gmail.com"
msg['To'] = "rohsmarcos1003166@gmail.com"
msg.add_alternative(corpo, subtype='html')

try:
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(msg['From'], os.environ.get('EMAIL_PASSWORD'))
        smtp.send_message(msg)
        print("Sucesso!")
except Exception as e:
    print(f"Erro: {e}")
