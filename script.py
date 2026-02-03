import yfinance as yf
import pandas as pd
import smtplib
from email.message import EmailMessage
import os

def buscar_vix():
    try:
        vix = yf.Ticker("^VIX")
        venc = vix.options[0]
        grade = vix.option_chain(venc)
        df = pd.concat([grade.calls, grade.puts])
        df['Vol Compra'] = df.apply(lambda x: x['volume'] if x['change'] >= 0 else 0, axis=1)
        df['Vol Venda'] = df.apply(lambda x: x['volume'] if x['change'] < 0 else 0, axis=1)
        top5 = df.nlargest(5, 'volume')[['contractSymbol', 'lastPrice', 'strike', 'Vol Compra', 'Vol Venda']]
        return f"<h3>TOP 5 VIX (EUA) - Venc: {venc}</h3>" + top5.to_html(index=False, border=1)
    except:
        return "<h3>TOP 5 VIX (EUA)</h3><p>Erro nos dados.</p>"

def buscar_brasil():
    """Busca simplificada para evitar bloqueio da B3"""
    try:
        # Focamos nos dois maiores volumes para garantir a entrega
        ativos = ["PETR4.SA", "VALE3.SA"]
        lista = []
        for t in ativos:
            try:
                # Usamos um timeout curto para ser rápido
                ticker = yf.Ticker(t)
                venc = ticker.options[0]
                grade = ticker.option_chain(venc)
                lista.append(pd.concat([grade.calls, grade.puts]))
            except:
                continue
        
        df_geral = pd.concat(lista)
        df_geral['Vol Compra'] = df_geral.apply(lambda x: x['volume'] if x['change'] >= 0 else 0, axis=1)
        df_geral['Vol Venda'] = df_geral.apply(lambda x: x['volume'] if x['change'] < 0 else 0, axis=1)
        
        top5 = df_geral.nlargest(5, 'volume')[['contractSymbol', 'lastPrice', 'strike', 'Vol Compra', 'Vol Venda']]
        # Formata o Ticker padrão Opções.net.br
        top5['contractSymbol'] = top5['contractSymbol'].str.extract(r'([A-Z]{5}\d{1,3})')
        top5.columns = ['Ativo', 'Preço', 'Strike', 'Vol Compra', 'Vol Venda']
        
        return "<h3>TOP 5 BRASIL (Ref: Opções.net.br)</h3>" + top5.to_html(index=False, border=1)
    except:
        return "<h3>TOP 5 BRASIL</h3><p>A B3 ainda não liberou os dados. Tente novamente em instantes.</p>"

# --- Envio ---
html_vix = buscar_vix()
html_br = buscar_brasil()

corpo = f"<html><body style='font-family:sans-serif;'>{html_vix}<br><hr><br>{html_br}</body></html>"
msg = EmailMessage()
msg['Subject'] = "RELATÓRIO DE FLUXO - B3 e VIX"
msg['From'] = "rohsmarcos1003166@gmail.com"
msg['To'] = "rohsmarcos1003166@gmail.com"
msg.add_alternative(corpo, subtype='html')

try:
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(msg['From'], os.environ.get('EMAIL_PASSWORD'))
        smtp.send_message(msg)
        print("Enviado!")
except Exception as e:
    print(f"Erro: {e}")
