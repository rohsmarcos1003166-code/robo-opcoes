import yfinance as yf
import pandas as pd
import smtplib
from email.message import EmailMessage
import os

def buscar_vix_top5():
    """Busca as 5 maiores (Calls ou Puts) do VIX por volume"""
    try:
        vix = yf.Ticker("^VIX")
        vencimento = vix.options[0]
        grade = vix.option_chain(vencimento)
        
        # Junta Calls e Puts em um único DataFrame
        total = pd.concat([grade.calls, grade.puts])
        
        top5 = total.nlargest(5, 'volume')[['contractSymbol', 'lastPrice', 'strike', 'volume']]
        top5.columns = ['Ativo', 'Preço', 'Strike', 'Volume']
        
        return f"<h3>TOP 5 VIX (EUA) - Calls & Puts (Venc: {vencimento})</h3>" + top5.to_html(index=False, border=1)
    except:
        return "<h3>TOP 5 VIX (EUA)</h3><p>Erro ao extrair dados.</p>"

def buscar_geral_b3_top5():
    """Escaneia Calls e Puts dos ativos mais líquidos da B3"""
    try:
        # Varredura nos "Blue Chips" da B3
        principais_ativos = ["PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBDC4.SA", "BBAS3.SA"]
        lista_geral = []

        for ticker in principais_ativos:
            try:
                ativo = yf.Ticker(ticker)
                venc = ativo.options[0]
                grade = ativo.option_chain(venc)
                # Adiciona tanto calls quanto puts daquele ativo
                lista_geral.append(grade.calls)
                lista_geral.append(grade.puts)
            except:
                continue
        
        # Consolida tudo (Calls e Puts de todos os ativos)
        todas_opcoes = pd.concat(lista_geral)
        
        # Pega as 5 campeãs de volume do Brasil
        top5 = todas_opcoes.nlargest(5, 'volume')[['contractSymbol', 'lastPrice', 'strike', 'volume']]
        
        # Formatação do nome (Ex: PETRB360 ou PETRN360)
        top5['contractSymbol'] = top5['contractSymbol'].str.extract(r'([A-Z]{5}\d{1,3})')
        top5.columns = ['Ativo', 'Preço', 'Strike', 'Volume']
        
        return "<h3>TOP 5 BRASIL (Geral B3) - Calls & Puts Mais Ativas</h3>" + top5.to_html(index=False, border=1)
    except:
        return "<h3>TOP 5 BRASIL (Geral B3)</h3><p>Dados indisponíveis no momento.</p>"

# --- Montagem e Envio ---
html_vix = buscar_vix_top5()
html_b3 = buscar_geral_b3_top5()

corpo_email = f"""
<html>
<body style="font-family: Arial, sans-serif; color: #333;">
    <h2 style="color: #2c3e50;">Radar de Volume: TOP 5 Opções (Calls e Puts)</h2>
    <p>Este relatório identifica onde está o maior dinheiro do mercado agora.</p>
    <hr>
    {html_vix}
    <br><br>
    {html_b3}
    <br>
    <p style="font-size: 11px; color: gray;">Fonte: B3 / Yahoo Finance / Opções.net.br</p>
</body>
</html>
"""

msg = EmailMessage()
msg['Subject'] = "ALERTA: TOP 5 GERAL (CALLS & PUTS)"
msg['From'] = "rohsmarcos1003166@gmail.com"
msg['To'] = "rohsmarcos1003166@gmail.com"
msg.add_alternative(corpo_email, subtype='html')

try:
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(msg['From'], os.environ.get('EMAIL_PASSWORD'))
        smtp.send_message(msg)
        print("Radar de Calls e Puts enviado!")
except Exception as e:
    print(f"Erro no envio: {e}")
