import yfinance as yf
import pandas as pd
import smtplib
from email.message import EmailMessage
import os
import time

def buscar_dados_com_agressao():
    """Busca dados e separa o volume entre estimativa de Compra e Venda"""
    try:
        # --- BRASIL (PETR4 como base B3) ---
        petr = yf.Ticker("PETR4.SA")
        venc_br = petr.options[0]
        grade_br = petr.option_chain(venc_br)
        df_br = pd.concat([grade_br.calls, grade_br.puts])

        if df_br['volume'].sum() <= 0:
            return None

        # Lógica de Agressão: Se 'change' > 0 (Compra), senão (Venda)
        df_br['Vol_Compra'] = df_br.apply(lambda x: x['volume'] if x['change'] >= 0 else 0, axis=1)
        df_br['Vol_Venda'] = df_br.apply(lambda x: x['volume'] if x['change'] < 0 else 0, axis=1)

        top5_br = df_br.nlargest(5, 'volume')[['contractSymbol', 'lastPrice', 'strike', 'Vol_Compra', 'Vol_Venda']]
        top5_br['contractSymbol'] = top5_br['contractSymbol'].str.extract(r'([A-Z]{5}\d{1,3})')
        top5_br.columns = ['Ativo', 'Preço', 'Strike', 'Vol Compra', 'Vol Venda']
        html_br = f"<h3>TOP 5 BRASIL (Opções.net.br/B3) - Venc: {venc_br}</h3>" + top5_br.to_html(index=False, border=1)

        # --- EUA (^VIX) ---
        vix = yf.Ticker("^VIX")
        venc_vix = vix.options[0]
        grade_vix = vix.option_chain(venc_vix)
        df_vix = pd.concat([grade_vix.calls, grade_vix.puts])

        df_vix['Vol_Compra'] = df_vix.apply(lambda x: x['volume'] if x['change'] >= 0 else 0, axis=1)
        df_vix['Vol_Venda'] = df_vix.apply(lambda x: x['volume'] if x['change'] < 0 else 0, axis=1)

        top5_vix = df_vix.nlargest(5, 'volume')[['contractSymbol', 'lastPrice', 'strike', 'Vol_Compra', 'Vol_Venda']]
        top5_vix.columns = ['Ativo', 'Preço', 'Strike', 'Vol Compra', 'Vol Venda']
        html_vix = f"<h3>TOP 5 VIX (EUA) - Venc: {venc_vix}</h3>" + top5_vix.to_html(index=False, border=1)

        return html_vix, html_br
    except:
        return None

# --- Lógica de 3 Tentativas ---
tentativas = 3
sucesso = False
h_vix, h_br = "", ""

for i in range(tentativas):
    print(f"Tentativa {i+1}...")
    res = buscar_dados_com_agressao()
    if res:
        h_vix, h_br = res
        sucesso = True
        break
    time.sleep(300)

if not sucesso:
    h_vix = "<h3>VIX</h3><p>Erro após 3 tentativas.</p>"
    h_br = "<h3>BRASIL</h3><p>Erro após 3 tentativas.</p>"

# --- Envio do E-mail ---
corpo = f"<html><body style='font-family: Arial;'><h2>Relatório de Fluxo de Opções</h2>{h_vix}<br><hr><br>{h_br}</body></html>"
msg = EmailMessage()
msg['Subject'] = "FLUXO DE VOLUME: COMPRA vs VENDA"
msg['From'] = "rohsmarcos1003166@gmail.com"
msg['To'] = "rohsmarcos1003166@gmail.com"
msg.add_alternative(corpo, subtype='html')

try:
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(msg['From'], os.environ.get('EMAIL_PASSWORD'))
        smtp.send_message(msg)
        print("E-mail enviado com sucesso!")
except Exception as e:
    print(f"Erro: {e}")
