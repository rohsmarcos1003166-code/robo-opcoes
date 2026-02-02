import yfinance as yf
import pandas as pd
import smtplib
import os
from email.message import EmailMessage
from datetime import datetime, timedelta

def executar_robo():
    try:
        meu_email = "rohsmarcos1003166@gmail.com"
        senha_app = os.getenv("EMAIL_PASSWORD")
        
        ativos = ["PETR4", "VALE3", "BBDC4", "ITUB4", "MGLU3"]
        relatorio = f"📊 OPÇÕES: VENCIMENTO MENSAL PRINCIPAL\n" + "="*40 + "\n"

        for t in ativos:
            ticker = yf.Ticker(f"{t}.SA")
            if not ticker.options: continue
            
            # FILTRO MENSAL: Pula vencimentos com menos de 7 dias (semanais/fim de série)
            vencimento_alvo = None
            for v in ticker.options:
                dt_venc = datetime.strptime(v, '%Y-%m-%d')
                if (dt_venc - datetime.now()).days > 7:
                    vencimento_alvo = v
                    break
            
            if not vencimento_alvo: vencimento_alvo = ticker.options[0]

            opt = ticker.option_chain(vencimento_alvo)
            df = pd.concat([opt.calls, opt.puts])
            
            # Top 5 em Volume do mês
            maior_volume = df.sort_values(by='volume', ascending=False).head(5)

            relatorio += f"\n🔹 {t} | Vencimento: {vencimento_alvo}\n"
            relatorio += maior_volume[['strike', 'lastPrice', 'volume']].to_string(index=False) + "\n"
            relatorio += "-"*30 + "\n"

        msg = EmailMessage()
        msg['Subject'] = "📈 Opções Mensais: PETR, VALE, BBDC, ITUB, MGLU"
        msg['From'] = meu_email
        msg['To'] = meu_email
        msg.set_content(relatorio)

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(meu_email, senha_app)
            smtp.send_message(msg)
        print("✅ Relatório mensal enviado!")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    executar_robo()
