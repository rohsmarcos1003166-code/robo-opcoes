import yfinance as yf
import pandas as pd
import smtplib
from email.message import EmailMessage
import os

def buscar_dados_vix():
    print("Iniciando extração de dados do VIX...")
    try:
        # O ticker para o índice VIX no Yahoo Finance é ^VIX
        vix = yf.Ticker("^VIX")
        
        # Obtém as datas de vencimento de opções disponíveis
        vencimentos = vix.options
        
        if not vencimentos:
            print("Aviso: Nenhuma opção encontrada para ^VIX no momento.")
            return None
        
        # Pega o primeiro vencimento disponível
        data_vencimento = vencimentos[0]
        opcoes = vix.option_chain(data_vencimento)
        
        # Seleciona as CALLS e as colunas principais
        df_calls = opcoes.calls[['lastPrice', 'strike', 'volume', 'openInterest']].head(15)
        
        html = f"""
        <html>
            <body>
                <h2>Relatório de Opções - Mercado Americano (VIX)</h2>
                <p><b>Ativo:</b> ^VIX (CBOE Volatility Index)</p>
                <p><b>Vencimento Selecionado:</b> {data_vencimento}</p>
                {df_calls.to_html(index=False)}
                <p><i>Dados extraídos via Yahoo Finance.</i></p>
            </body>
        </html>
        """
        return html
    except Exception as e:
        print(f"Erro ao buscar dados do VIX: {e}")
        return None

# --- Fluxo de Envio ---
corpo_email = buscar_dados_vix()

if corpo_email:
    msg = EmailMessage()
    msg['Subject'] = "OPÇÕES VIX: MERCADO AMERICANO"
    msg['From'] = "rohsmarcos1003166@gmail.com"
    msg['To'] = "rohsmarcos1003166@gmail.com"
    msg.add_alternative(corpo_email, subtype='html')

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            senha = os.environ.get('EMAIL_PASSWORD')
            smtp.login(msg['From'], senha)
            smtp.send_message(msg)
            print("Sucesso: E-mail com dados do VIX enviado!")
    except Exception as e:
        print(f"Erro no envio do e-mail: {e}")
else:
    print("Falha na extração. O e-mail não foi enviado.")
