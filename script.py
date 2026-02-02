import yfinance as yf
import pandas as pd
import smtplib
import os
from email.message import EmailMessage
from datetime import datetime

def executar_robo():
    try:
        meu_email = "rohsmarcos1003166@gmail.com"
        senha_app = os.getenv("EMAIL_PASSWORD")
        
        ativos = ["PETR4", "VALE3", "BBDC4", "ITUB4", "MGLU3"]
        relatorio = f"📊 OPÇÕES - VENCIMENTOS MENSAIS\n" + "="*40 + "\n"

        for t in ativos:
            ticker = yf.Ticker(f"{t}.SA")
            
            if not ticker.options:
                continue
            
            # Filtra para evitar as semanais: pegamos os vencimentos 
            # e buscamos aquele que tem o maior volume total acumulado,
            # que historicamente é o vencimento mensal.
            vencimentos = ticker.options
            
            # Seleciona o primeiro vencimento que tenha pelo menos 10 dias de vida
            # (para evitar pegar opções que vencem amanhã ou semanais irrelevantes)
            target_vencimento = vencimentos[0]
            for v in vencimentos:
                dt_venc = datetime.strptime(v, '%Y-%m-%d')
                dias_restantes = (dt_venc - datetime.now()).days
                if dias_restantes > 5: # Pula o que está vencendo em cima da hora (semanais)
                    target_vencimento = v
                    break

            opt = ticker.option_chain(target_vencimento)
            df = pd.concat([opt.calls, opt.puts])
            
            # Pega as 5 opções com MAIOR VOLUME (Sinal de liquidez do mês)
            maior_volume = df.sort_values(by='volume', ascending=False).head(5)

            relatorio += f"\n🔹 {t} | MENSAL: {target_vencimento}\n"
            relatorio += maior_volume[['strike', 'lastPrice', 'volume']].to_string(index=False) + "\n"
            relatorio += "-"*30 + "\n"

        msg = EmailMessage()
        msg['Subject'] = "📈 Resumo Mensal: PETR, VALE, BBDC, ITUB, MGLU"
        msg['From'] = meu_email
        msg['To'] = meu_email
        msg.set_content(relatorio)

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(meu_email, senha_app)
            smtp.send_message(msg)
            
        print("✅ Relatório de vencimentos mensais enviado!")

    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    executar_robo()
