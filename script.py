Import yfinance as yf
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
        # Lógica de Agressão
        df['Vol Compra'] = df.apply(lambda x: x['volume'] if x['change'] >= 0 else 0, axis=1)
        df['Vol Venda'] = df.apply(lambda x: x['volume'] if x['change'] < 0 else 0, axis=1)
        top5 = df.nlargest(5, 'volume')[['contractSymbol', 'lastPrice', 'strike', 'Vol Compra', 'Vol Venda']]
        return f"<h3>TOP 5 VIX (EUA)</h3>" + top5.to_html(index=False, border=1)
    except:
        return "<h3>TOP 5 VIX</h3><p>Erro nos dados EUA.</p>"

def buscar_brasil_opcoes_net():
    try:
        # Puxa PETR4 que é o termômetro do Opções.net.br
        petr = yf.Ticker("PETR4.SA")
        venc = petr.options[0]
        grade = petr.option_chain(venc)
        df = pd.concat([grade.calls, grade.puts])
        
        # Filtro de Volume e Agressão (Compra vs Venda)
        df['Vol Compra'] = df.apply(lambda x: x['volume'] if x['change'] >= 0 else 0, axis=1)
        df['Vol Venda'] = df.apply(lambda x: x['volume'] if x['change'] < 0 else 0, axis=1)
        
        # Seleciona as 5 mais negociadas
        top5 = df.nlargest(5, 'volume')[['contractSymbol', 'lastPrice', 'strike', 'Vol Compra', 'Vol Venda']]
        
        # Formata o nome igualzinho ao site Opções.net.br (Ex: PETRB360)
        top5['contractSymbol'] = top5['contractSymbol'].str.extract(r'([A-Z]{5}\d{1,3})')
        top5.columns = ['Ativo', 'Preço', 'Strike', 'Vol Compra', 'Vol Venda']
        
        return f"<h3>TOP 5 BRASIL (Fonte: Opções.net.br/B3)</h3>" + top5.to_html(index=False, border=1)
    except:
        return "<h3>TOP 5 BRASIL</h3><p>Dados ainda não disponíveis no site.</p>"

# --- Montagem do Relatório ---
h_vix = buscar_vix()
h_br = buscar_brasil_opcoes_net()
corpo = f"<html><body>{h_vix}<br><hr><br>{h_br}</body></html>"

msg = EmailMessage()
msg['Subject'] = "FLUXO DE OPÇÕES: COMPRA vs VENDA"
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
Esse código aqui ele responde normalmente acabei de testar ele ele responde muito bem
