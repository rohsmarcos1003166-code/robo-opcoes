import yfinance as yf
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def rodar_extracao():
    # --- CONFIGURAÇÃO DE ACESSO ---
    meu_email = "rohmarcos1003166@gmail.com"
    senha_app = "evnzgzgvypabmiee" 
    
    ativos = ["PETR4", "VALE3", "BBDC4", "ITUB4"]
    relatorio = "🚀 RELATÓRIO DE OPÇÕES B3\n" + "="*40 + "\n"
    encontrou_dados = False

    for t in ativos:
        try:
            # Busca o ticker com sufixo da B3
            ticker = yf.Ticker(f"{t}.SA")
            vencimentos = ticker.options
            
            if vencimentos:
                # Pega o primeiro vencimento
                prox = vencimentos[0]
                chain = ticker.option_chain(prox)
                
                # Une Calls e Puts
                todas = pd.concat([chain.calls, chain.puts])
                
                # FILTRO CORRIGIDO: Se tiver preço, o robô captura.
                # Isso resolve o erro de enviar e-mail dizendo que não achou nada.
                ativas = todas[todas['lastPrice'] > 0].copy()

                if not ativas.empty:
                    encontrou_dados = True
                    # Top 5 opções por preço
                    top5 = ativas.sort_values(by='lastPrice', ascending=False).head(5)
                    relatorio += f"\nAtivo: {t} | Vencimento: {prox}\n"
                    for _, row in top5.iterrows():
                        relatorio += f"- {row['contractSymbol']} | R$ {row['lastPrice']:.2f}\n"
                    relatorio += "-"*40 + "\n"
        except:
            continue

    if not encontrou_dados:
        relatorio += "\nDados não consolidados pelo Yahoo Finance no momento."

    # --- ENVIO DO E-MAIL ---
    msg = MIMEMultipart()
    msg['Subject'] = "📊 Relatório de Opções - B3"
    msg['From'] = meu_email
    msg['To'] = meu_email
    msg.attach(MIMEText(relatorio, 'plain'))

    try:
        # Usa porta 465 com SSL para o Gmail
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(meu_email, senha_app)
        server.send_message(msg)
        server.quit()
        print("Sucesso: E-mail enviado!")
    except Exception as e:
        print(f"Erro no envio: {e}")

if __name__ == "__main__":
    rodar_extracao()
