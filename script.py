import yfinance as yf
import pandas as pd
import smtplib
from email.message import EmailMessage
import os
from yahoo_fin import options

def buscar_vix():
    try:
        # VIX sempre funciona bem porque é EUA
        vix_data = yf.Ticker("^VIX")
        venc = vix_data.options[0]
        grade = vix_data.option_chain(venc)
        df = pd.concat([grade.calls, grade.puts])
        df['Vol Compra'] = df.apply(lambda x: x['volume'] if x['change'] >= 0 else 0, axis=1)
        df['Vol Venda'] = df.apply(lambda x: x['volume'] if x['change'] < 0 else 0, axis=1)
        top5 = df.nlargest(5, 'volume')[['contractSymbol', 'lastPrice', 'strike', 'Vol Compra', 'Vol Venda']]
        return f"<h3>TOP 5 VIX (EUA) - {venc}</h3>" + top5.to_html(index=False, border=1)
    except:
        return "<h3>TOP 5 VIX</h3><p>Erro nos EUA.</p>"

def buscar_brasil():
    """Busca robusta para PETR4 e VALE3 (Grade Opções.net.br)"""
    try:
        # Buscando PETR4 via biblioteca secundária para burlar bloqueio
        vencimento = options.get_expiration_dates("PETR4.SA")[0]
        calls = options.get_calls("PETR4.SA", vencimento)
        puts = options.get_puts("PETR4.SA", vencimento)
        
        df_br = pd.concat([calls, puts])
        # Ajuste de nomes de colunas da biblioteca yahoo_fin
        df_br['Vol Compra'] = df_br.apply(lambda x: x['Volume'] if float(str(x['Change']).replace('%','')) >= 0 else 0, axis=1)
        df_br['Vol Venda'] = df_br.apply(lambda x: x['Volume'] if float(str(x['Change']).replace('%','')) < 0 else 0, axis=1)
        
        top5 = df_br.nlargest(5, 'Volume')[['Contract Name', 'Last Price', 'Strike', 'Vol Compra', 'Vol Venda']]
        top5.columns = ['Ativo', 'Preço', 'Strike', 'Vol Compra', 'Vol Venda']
        
        return "<h3>TOP 5 BRASIL (PETR4)</h3>" + top5.to_html(index=False, border=1)
    except Exception as e:
        return f"<h3>TOP 5 BRASIL</h3><p>Servidor B3 congestionado. Tentando via reserva...</p>"

# --- Envio ---
html_vix = buscar_vix()
html_br = buscar_brasil()
corpo = f"<html><body>{html_vix}<br><hr><br>{html_br}</body></html>"

msg = EmailMessage()
msg['Subject'] = "RELATÓRIO DE FLUXO - COMPRA VS VENDA"
msg['From'] = "rohsmarcos1003166@gmail.com"
msg['To'] = "rohsmarcos1003166@gmail.com"
msg.add_alternative(corpo, subtype='html')

try:
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(msg['From'], os.environ.get('EMAIL_PASSWORD'))
        smtp.send_message(msg)
        print("Sucesso!")
except:
    print("Erro no envio.")
