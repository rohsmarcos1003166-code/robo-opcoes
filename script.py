import yfinance as yf
import pandas as pd
import smtplib
from email.message import EmailMessage
import os

def capturar_dados(ticker_symbol, nome_exibicao):
    try:
        ativo = yf.Ticker(ticker_symbol)
        venc = ativo.options[0]
        grade = ativo.option_chain(venc)
        df = pd.concat([grade.calls, grade.puts])
        
        # Lógica de Volume Compra/Venda simplificada
        df['Vol Compra'] = df.apply(lambda x: x['volume'] if x['change'] >= 0 else 0, axis=1)
        df['Vol Venda'] = df.apply(lambda x: x['volume'] if x['change'] < 0 else 0, axis=1)
        
        top5 = df.nlargest(5, 'volume')[['contractSymbol', 'lastPrice', 'strike', 'Vol Compra', 'Vol Venda']]
        # Formatação para o padrão Opções.net.br
        if ".SA" in ticker_symbol:
            top5['contractSymbol'] = top5['contractSymbol'].str.extract(r'([A-Z]{5}\d{1,3})')
        
        top5.columns = ['Ativo', 'Preço', 'Strike', 'Vol Compra', 'Vol Venda']
        return f"<h3>TOP 5 {nome_exibicao} - Venc: {venc}</h3>" + top5.to_html(index=False, border=1)
    except:
        return f"<h3>TOP 5 {nome_exibicao}</h3><p>Dados ainda não consolidados pela B3.</p>"

# Execução rápida
html_vix = capturar_dados("^VIX", "EUA (VIX)")
html_br = capturar_dados("PETR4.SA", "BRASIL (Opções.net.br)")

corpo = f"<html><body style='font-family:Arial;'>{html_vix}<br><hr><br>{html_br}</body></html>"

# Envio do e-mail
msg = EmailMessage()
msg['Subject'] = "RELATÓRIO: FLUXO DE OPÇÕES"
msg['From'] = "rohsmarcos1003166@gmail.com"
msg['To'] = "rohsmarcos1003166@gmail.com"
msg.add_alternative(corpo, subtype='html')

try:
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(msg['From'], os.environ.get('EMAIL_PASSWORD'))
        smtp.send_message(msg)
        print("Sucesso!")
except Exception as e:
    print(f"Erro no envio: {e}")
