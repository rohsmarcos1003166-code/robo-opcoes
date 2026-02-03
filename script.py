import yfinance as yf
import pandas as pd
import smtplib
from email.message import EmailMessage
import os

def buscar_dados_vix():
    """Busca as 5 mais negociadas do VIX (EUA)"""
    try:
        vix = yf.Ticker("^VIX")
        venc = vix.options[0]
        grade = vix.option_chain(venc)
        df = pd.concat([grade.calls, grade.puts])
        
        # Lógica de agressão (Baseada na variação de preço)
        df['Vol Compra'] = df.apply(lambda x: x['volume'] if x['change'] >= 0 else 0, axis=1)
        df['Vol Venda'] = df.apply(lambda x: x['volume'] if x['change'] < 0 else 0, axis=1)
        
        top5 = df.nlargest(5, 'volume')[['contractSymbol', 'lastPrice', 'strike', 'Vol Compra', 'Vol Venda']]
        top5.columns = ['Ativo', 'Preço', 'Strike', 'Vol Compra', 'Vol Venda']
        return f"<h3>TOP 5 VIX (EUA) - Venc: {venc}</h3>" + top5.to_html(index=False, border=1)
    except:
        return "<h3>TOP 5 VIX (EUA)</h3><p>Dados indisponíveis no momento.</p>"

def buscar_brasil_opcoes_net():
    """Varredura Geral B3: Simula a grade do Opções.net.br"""
    try:
        # Lista dos ativos com maior liquidez em opções na B3
        ativos_foco = ["PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBDC4.SA", "BBAS3.SA", "ELET3.SA"]
        consolidado = []

        for t in ativos_foco:
            try:
                obj = yf.Ticker(t)
                proximo_vencimento = obj.options[0]
                grade = obj.option_chain(proximo_vencimento)
                df_temp = pd.concat([grade.calls, grade.puts])
                consolidado.append(df_temp)
            except:
                continue

        if not consolidado:
            return "<h3>TOP 5 BRASIL</h3><p>Erro ao acessar dados da B3.</p>"

        # Une todos os ativos em uma única lista para achar o TOP 5 Geral
        df_geral = pd.concat(consolidado)
        
        # Cálculo de Volume Compra vs Venda
        df_geral['Vol Compra'] = df_geral.apply(lambda x: x['volume'] if x['change'] >= 0 else 0, axis=1)
        df_geral['Vol Venda'] = df_geral.apply(lambda x: x['volume'] if x['change'] < 0 else 0, axis=1)

        # Seleciona as 5 campeãs de volume da B3 inteira
        top5_br = df_geral.nlargest(5, 'volume')[['contractSymbol', 'lastPrice', 'strike', 'Vol Compra', 'Vol Venda']]
        
        # Limpa o Ticker para o padrão Opções.net.br (ex: PETRB360)
        top5_br['contractSymbol'] = top5_br['contractSymbol'].str.extract(r'([A-Z]{5}\d{1,3})')
        top5_br.columns = ['Ativo', 'Preço', 'Strike', 'Vol Compra', 'Vol Venda']
        
        return "<h3>TOP 5 BRASIL (Grade Geral - Opções.net.br)</h3>" + top5_br.to_html(index=False, border=1)
    except Exception as e:
        return f"<h3>TOP 5 BRASIL</h3><p>Erro na varredura: {e}</p>"

# --- Montagem e Envio ---

html_vix = buscar_dados_vix()
html_br = buscar_brasil_opcoes_net()

corpo_email = f"""
<html>
<body style="font-family: Arial, sans-serif;">
    <h2 style="color: #1a5276;">Radar de Opções: Volume de Compra vs Venda</h2>
    <hr>
    {html_vix}
    <br><br>
    {html_br}
    <br>
    <p style="font-size: 10px; color: gray;">Fonte Brasil: Referência Opções.net.br | Dados processados via Yahoo.</p>
</body>
</html>
"""

msg = EmailMessage()
msg['Subject'] = "ALERTA: TOP 5 BRASIL & EUA (VOLUME COMPRA/VENDA)"
msg['From'] = "rohsmarcos1003166@gmail.com"
msg['To'] = "rohsmarcos1003166@gmail.com"
msg.add_alternative(corpo_email, subtype='html')

try:
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(msg['From'], os.environ.get('EMAIL_PASSWORD'))
        smtp.send_message(msg)
        print("Sucesso: E-mail enviado!")
except Exception as e:
    print(f"Falha no envio: {e}")
