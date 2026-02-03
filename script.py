import yfinance as yf
import pandas as pd
import smtplib
from email.message import EmailMessage
import os

def processar_opcoes(ticker_simbolo, nome_exibicao):
    try:
        ativo = yf.Ticker(ticker_simbolo)
        venc = ativo.options[0]
        grade = ativo.option_chain(venc)
        
        # Junta Calls e Puts
        df = pd.concat([grade.calls, grade.puts])
        
        # Lógica de Agressão (Volume Compra vs Venda)
        df['Vol Compra'] = df.apply(lambda x: x['volume'] if x['change'] >= 0 else 0, axis=1)
        df['Vol Venda'] = df.apply(lambda x: x['volume'] if x['change'] < 0 else 0, axis=1)
        
        # Pega as 5 maiores em volume (pode ser Call ou Put)
        top5 = df.nlargest(5, 'volume')[['contractSymbol', 'lastPrice', 'strike', 'Vol Compra', 'Vol Venda']]
        
        # Formatação padrão Opções.net.br (Ex: PETRB360 ou VALEB720)
        top5['contractSymbol'] = top5['contractSymbol'].str.extract(r'([A-Z]{5}\d{1,3})')
        top5.columns = ['Ativo', 'Preço', 'Strike', 'Vol Compra', 'Vol Venda']
        
        return f"<h3>TOP 5 {nome_exibicao} - Venc: {venc}</h3>" + top5.to_html(index=False, border=1)
    except:
        return f"<h3>TOP 5 {nome_exibicao}</h3><p>Dados ainda não consolidados.</p>"

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
        return "<h3>TOP 5 VIX (EUA)</h3>" + top5.to_html(index=False, border=1)
    except:
        return "<h3>TOP 5 VIX</h3><p>Erro nos dados EUA.</p>"

# --- Execução das Buscas ---
html_vix = buscar_vix()
html_petr = processar_opcoes("PETR4.SA", "BRASIL (PETR4)")
html_vale = processar_opcoes("VALE3.SA", "BRASIL (VALE3)")

# --- Montagem do E-mail ---
corpo = f"""
<html>
<body style='font-family: Arial;'>
    <h2>Relatório de Fluxo de Opções (Referência: Opções.net.br)</h2>
    <hr>
    {html_vix}
    <br>{html_petr}
    <br>{html_vale}
    <br>
    <p style='font-size: 10px;'>Nota: O volume de Compra/Venda é calculado com base na variação de preço (Agressão).</p>
</body>
</html>
"""

msg = EmailMessage()
msg['Subject'] = "FLUXO DE OPÇÕES: PETR4, VALE3 e VIX"
msg['From'] = "rohsmarcos1003166@gmail.com"
msg['To'] = "rohsmarcos1003166@gmail.com"
msg.add_alternative(corpo, subtype='html')

try:
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(msg['From'], os.environ.get('EMAIL_PASSWORD'))
        smtp.send_message(msg)
        print("Enviado com sucesso!")
except Exception as e:
    print(f"Erro: {e}")
