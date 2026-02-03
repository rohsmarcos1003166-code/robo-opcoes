import yfinance as yf
import pandas as pd
import smtplib
from email.message import EmailMessage
import os

def buscar_dados_opcoes():
    try:
        # Importante: Usar .SA para ativos brasileiros
        ticker = yf.Ticker("PETR4.SA")
        
        # Pega a data de vencimento mais próxima
        vencimentos = ticker.options
        if not vencimentos:
            return None, "Nenhum vencimento encontrado."
        
        # Extrai as chamadas (calls) do primeiro vencimento
        opcoes = ticker.option_chain(vencimentos[0])
        df_calls = opcoes.calls[['lastPrice', 'strike', 'percentChange']]
        return df_calls.head(10).to_html(), None
    except Exception as e:
        return None, str(e)

# --- Execução Principal ---
corpo_email, erro = buscar_dados_opcoes()

if erro:
    print(f"Erro ao buscar dados: {erro}")
else:
    msg = EmailMessage()
    msg['Subject'] = "OPÇÕES: VENCIMENTO MENSAL PETR4"
    msg['From'] = "rohsmarcos1003166@gmail.com"
    msg['To'] = "rohsmarcos1003166@gmail.com"
    msg.set_content("Erro ao processar dados.")
    msg.add_alternative(f"<h3>Relatório de Opções</h3>{corpo_email}", subtype='html')

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        # Usa a secret configurada no GitHub
        smtp.login(msg['From'], os.environ.get('EMAIL_PASSWORD'))
        smtp.send_message(msg)
    print("E-mail enviado com sucesso!")
