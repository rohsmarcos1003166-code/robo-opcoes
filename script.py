import yfinance as yf
import pandas as pd
import smtplib
from email.message import EmailMessage
import os

def buscar_dados(ticker_nome):
    print(f"Tentando extrair dados para {ticker_nome}...")
    try:
        ativo = yf.Ticker(ticker_nome)
        vencimentos = ativo.options
        
        if not vencimentos:
            print(f"Aviso: Sem opções para {ticker_nome} no momento.")
            return None
        
        # Pega o vencimento mais próximo
        proximo_vencimento = vencimentos[0]
        opcoes = ativo.option_chain(proximo_vencimento)
        df = opcoes.calls[['lastPrice', 'strike', 'percentChange']].head(10)
        
        return f"<h3>Ativo: {ticker_nome} (Vencimento: {proximo_vencimento})</h3>" + df.to_html(index=False)
    except Exception as e:
        print(f"Erro técnico no yfinance: {e}")
        return None

# --- Fluxo Principal ---
# 1. Tenta Petrobras
corpo_html = buscar_dados("PETR4.SA")

# 2. Se falhar, tenta Vale (Teste de Sanidade)
if corpo_html is None:
    print("Iniciando teste alternativo com VALE3.SA...")
    corpo_html = buscar_dados("VALE3.SA")

# 3. Envio do E-mail (Se houver algum dado)
if corpo_html:
    msg = EmailMessage()
    msg['Subject'] = "RELATÓRIO DE OPÇÕES - TESTE"
    msg['From'] = "rohsmarcos1003166@gmail.com"
    msg['To'] = "rohsmarcos1003166@gmail.com"
    msg.add_alternative(f"<html><body>{corpo_html}</body></html>", subtype='html')

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            # Pega a senha das Secrets do GitHub
            senha = os.environ.get('EMAIL_PASSWORD')
            smtp.login(msg['From'], senha)
            smtp.send_message(msg)
            print("E-mail enviado com sucesso!")
    except Exception as e:
        print(f"Erro no envio do e-mail: {e}")
else:
    print("Nenhum dado extraído. O e-mail não foi enviado para evitar mensagens vazias.")
