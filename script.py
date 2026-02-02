import yfinance as yf
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def buscar_e_enviar():
    # --- CONFIGURAÇÕES FIXAS ---
    meu_email = "rohmarcos1003166@gmail.com"
    # Senha de App que você acabou de confirmar:
    senha_app = "evnzgzgvypabmiee"  
    
    ativos = ["PETR4", "VALE3", "BBDC4", "ITUB4"]
    relatorio = "🚀 RELATÓRIO DE OPÇÕES ATUALIZADO\n"
    relatorio += "="*40 + "\n"
    encontrou_dados = False

    for t in ativos:
        try:
            print(f"Buscando: {t}...")
            ticker = yf.Ticker(f"{t}.SA")
            vencimentos = ticker.options

            if vencimentos:
                prox = vencimentos[0]
                chain = ticker.option_chain(prox)
                
                # Junta Calls e Puts
                todas = pd.concat([chain.calls, chain.puts])

                # FILTRO SEGURO: Se tiver preço (lastPrice), ele captura.
                # Removemos a trava do Volume > 0 para o e-mail não ir vazio.
                ativas = todas[todas['lastPrice'] > 0].copy()

                if not ativas.empty:
                    encontrou_dados = True
                    # Pega as 5 opções com preços mais relevantes para o relatório
                    top5 = ativas.sort_values(by='lastPrice', ascending=False).head(5)
                    
                    relatorio += f"\nAtivo: {t} | Vencimento: {prox}\n"
                    for _, row in top5.iterrows():
                        simbolo = row['contractSymbol']
                        preco = row['lastPrice']
                        relatorio += f"- {simbolo}: R$ {preco:.2f}\n"
                    relatorio += "-"*40 + "\n"

        except Exception as e:
            print(f"Erro em {t}: {e}")
            continue

    if not encontrou_dados:
        relatorio += "\nNota: Dados não disponíveis no Yahoo Finance neste momento."

    # --- PROCESSO DE ENVIO ---
    msg = MIMEMultipart()
    msg['Subject'] = "📊 Relatório Diário de Opções"
    msg['From'] = meu_email
    msg['To'] = meu_email
    msg.attach(MIMEText(relatorio, 'plain'))

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(meu_email, senha_app)
        server.send_message(msg)
        server.quit()
        print("✅ E-mail enviado com sucesso!")
    except Exception as e:
        print(f"❌ Erro no login ou envio: {e}")

if __name__ == "__main__":
    buscar_e_enviar()
