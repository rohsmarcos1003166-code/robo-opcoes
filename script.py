import yfinance as yf
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def executar_robo():
    # --- DADOS DE ACESSO ---
    meu_email = "rohmarcos1003166@gmail.com"
    senha_app = "wvsj hkyd ywtc bcye"  # Sua última senha gerada
    
    ativos = ["PETR4", "VALE3", "BBDC4", "ITUB4"]
    relatorio = "🚀 RELATÓRIO DE OPÇÕES - B3\n" + "="*40 + "\n"
    encontrou_dados = False

    for t in ativos:
        try:
            print(f"Buscando: {t}...")
            ticker = yf.Ticker(f"{t}.SA")
            vencimentos = ticker.options

            if vencimentos:
                prox_vencimento = vencimentos[0]
                chain = ticker.option_chain(prox_vencimento)
                
                # Junta Calls e Puts
                todas = pd.concat([chain.calls, chain.puts])

                # FILTRO CORRIGIDO: Se tiver preço, ele captura (ignora erro de volume zerado)
                ativas = todas[todas['lastPrice'] > 0].copy()

                if not ativas.empty:
                    encontrou_dados = True
                    # Pega as 5 com maior preço de mercado para o relatório
                    top5 = ativas.sort_values(by='lastPrice', ascending=False).head(5)
                    
                    relatorio += f"\nAtivo: {t} | Vencimento: {prox_vencimento}\n"
                    for _, row in top5.iterrows():
                        relatorio += f"- {row['contractSymbol']} | R$ {row['lastPrice']:.2f}\n"
                    relatorio += "-"*40 + "\n"

        except Exception as e:
            print(f"Erro em {t}: {e}")
            continue

    if not encontrou_dados:
        relatorio += "\nO mercado ainda não consolidou os dados de volume/preço para hoje."

    # --- ENVIO DO E-MAIL ---
    msg = MIMEMultipart()
    msg['Subject'] = "📊 Relatório de Opções Atualizado"
    msg['From'] = meu_email
    msg['To'] = meu_email
    msg.attach(MIMEText(relatorio, 'plain'))

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(meu_email, senha_app)
        server.send_message(msg)
        server.quit()
        print("E-mail enviado com sucesso!")
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")

if __name__ == "__main__":
    executar_robo()
