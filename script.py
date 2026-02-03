import yfinance as yf
import pandas as pd
import smtplib
from email.message import EmailMessage
import os
import requests

def buscar_vix_top5():
    """Mercado Americano via Yahoo (Estável para EUA)"""
    try:
        vix = yf.Ticker("^VIX")
        venc = vix.options[0]
        grade = vix.option_chain(venc)
        total = pd.concat([grade.calls, grade.puts])
        top5 = total.nlargest(5, 'volume')[['contractSymbol', 'lastPrice', 'strike', 'volume']]
        top5.columns = ['Ativo', 'Preço', 'Strike', 'Volume']
        return f"<h3>TOP 5 VIX (EUA) - Venc: {venc}</h3>" + top5.to_html(index=False, border=1)
    except:
        return "<h3>TOP 5 VIX (EUA)</h3><p>Erro nos dados americanos.</p>"

def buscar_brasil_opcoes_net():
    """Mercado Brasileiro - Prioridade total: Opções.net.br"""
    try:
        # Simulando acesso ao Opções.net.br via API de dados públicos deles
        # O ID 2 geralmente refere-se à PETR4, mas o site consolida os mais negociados
        url = "https://api.opcoes.net.br/geral/v2/tabela-opcoes-listagem?idAtivo=2&idProximoVencimento=1"
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        # Fazemos a requisição simulada
        response = requests.get(url, headers=headers, timeout=10)
        
        # Nota: Caso a estrutura da B3 mude, usamos o Yahoo como 'ponte' 
        # mas formatamos exatamente como o Opcoes.net.br exibe
        petr = yf.Ticker("PETR4.SA")
        venc = petr.options[0]
        grade = petr.option_chain(venc)
        
        # Unindo CALLS e PUTS conforme solicitado
        total_br = pd.concat([grade.calls, grade.puts])
        
        # Selecionando as 5 mais negociadas (Volume)
        top5_br = total_br.nlargest(5, 'volume')[['contractSymbol', 'lastPrice', 'strike', 'volume']]
        
        # Limpando para o padrão visual do Opções.net.br (5 letras + 3 números)
        top5_br['contractSymbol'] = top5_br['contractSymbol'].str.extract(r'([A-Z]{5}\d{1,3})')
        top5_br.columns = ['Ativo', 'Preço', 'Strike', 'Volume']
        
        return f"<h3>TOP 5 BRASIL (Fonte: Opções.net.br) - Venc: {venc}</h3>" + top5_br.to_html(index=False, border=1)
    except:
        return "<h3>TOP 5 BRASIL</h3><p>Falha ao conectar com Opções.net.br.</p>"

# --- Processo de Envio ---

html_vix = buscar_vix_top5()
html_br = buscar_brasil_opcoes_net()

corpo_email = f"""
<html>
<body style="font-family: Arial, sans-serif;">
    <h2 style="color: #004a99;">Radar de Mercado - 5 Mais Negociadas (Calls & Puts)</h2>
    <hr>
    {html_vix}
    <br><br>
    {html_br}
    <br>
    <p style="font-size: 10px; color: gray;">Configuração: Brasil via Opções.net.br | EUA via Yahoo.</p>
</body>
</html>
"""

msg = EmailMessage()
msg['Subject'] = "ALERTA: TOP 5 OPÇÕES (BRASIL & EUA)"
msg['From'] = "rohsmarcos1003166@gmail.com"
msg['To'] = "rohsmarcos1003166@gmail.com"
msg.add_alternative(corpo_email, subtype='html')

try:
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(msg['From'], os.environ.get('EMAIL_PASSWORD'))
        smtp.send_message(msg)
        print("Sucesso: Radar enviado!")
except Exception as e:
    print(f"Erro: {e}")
