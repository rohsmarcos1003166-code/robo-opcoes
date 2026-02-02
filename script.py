import yfinance as yf
import pandas as pd
import smtplib
import os
import time
from email.message import EmailMessage

def executar_robo():
    meu_email = "rohmarcos1003166@gmail.com"
    senha_app = os.getenv("EMAIL_PASSWORD")
    
    # Lista completa com os 4 ativos que você quer
    ativos = ["PETR4", "VALE3", "BBDC4", "ITUB4"]
    relatorio = "📊 RELATÓRIO DE OPÇÕES (STRIKE E VOLUME)\n" + "="*50 + "\n"

    for t in ativos:
        ticker = yf.Ticker(f"{t}.SA")
        relatorio += f"\n🔹 ATIVO: {t}\n"
        achou = False

        # Tenta nos 3 meses de vencimento mais próximos
        for data in ticker.options[:3]:
            if achou: break
            for tentativa in range(3):
                try:
                    opt = ticker.option_chain(data)
                    df = pd.concat([opt.calls, opt.puts])
                    # Filtra negociações reais e ordena por volume
                    ativas = df[df['volume'] > 0].sort_values(by='volume', ascending=False).head(5)

                    if not ativas.empty:
                        relatorio += f"📅 Vencimento: {data}\n"
                        relatorio += ativas[['contractSymbol', 'strike', 'lastPrice', 'volume']].to_string(index=False) + "\n"
                        achou = True
                        break
                except:
                    time.sleep(5)

    msg = EmailMessage()
    msg['Subject'] = "📈 Relatório de Opções: Strike e Volume"
    msg['From'] = meu_email
    msg['To'] = meu_email
    msg.set_content(relatorio)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(meu_email, senha_app)
        smtp.send_message(msg)
    print("✅ Relatório enviado com os 4 ativos!")

if __name__ == "__main__":
    executar_robo()
