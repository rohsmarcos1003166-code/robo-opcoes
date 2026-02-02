import yfinance as yf
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def buscar_e_enviar():
    # 1. Configurações
    meu_email = "rohsmarcos1003166@gmail.com"
    senha = os.getenv("EMAIL_PASSWORD")
    
    # 2. Busca o preço real da PETR4 na bolsa
    try:
        petr = yf.Ticker("PETR4.SA")
        preco = petr.history(period="1d")['Close'].iloc[-1]
        mensagem_texto = f"Relatório do Robô:\n\nPETR4 está custando: R$ {preco:.2f}"
    except Exception as e:
        mensagem_texto = f"Erro ao buscar dados: {e}"

    # 3. Prepara o e-mail
    msg = MIMEMultipart()
    msg['Subject'] = "Dados da Bolsa - PETR4"
    msg['From'] = meu_email
    msg['To'] = meu_email
    msg.attach(MIMEText(mensagem_texto, 'plain'))

    # 4. Envia
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(meu_email, senha)
            server.send_message(msg)
        print("E-mail com informações enviado com sucesso!")
    except Exception as e:
        print(f"Erro no envio: {e}")

if __name__ == "__main__":
    buscar_e_enviar()
