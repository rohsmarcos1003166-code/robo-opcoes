import yfinance as yf
import smtplib
import os
import pandas as pd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def buscar_top5_opcoes():
    meu_email = "rohsmarcos1003166@gmail.com"
    senha = os.getenv("EMAIL_PASSWORD")
    ativos = ["PETR4", "VALE3", "BBDC4", "ITUB4"]
    todas_opcoes = []
    
    try:
        for t in ativos:
            ticker = yf.Ticker(f"{t}.SA")
            vencimentos = ticker.options
            if vencimentos:
                prox_vencimento = vencimentos[0]
                calls = ticker.option_chain(prox_vencimento).calls
                # Filtra opções com volume para garantir que pegamos dados reais
                ativas = calls[calls['volume'] > 0].copy()
                
                for _, linha in ativas.iterrows():
                    todas_opcoes.append({
                        'Ativo': t,
                        'Simbolo': linha['contractSymbol'],
                        'Var': linha['percentChange'],
                        'Preco': linha['lastPrice'],
                        'Vol': linha['volume']
                    })

        if todas_opcoes:
            df = pd.DataFrame(todas_opcoes)
            top5 = df.sort_values(by='Var', ascending=False).head(5)
            relatorio = "🏆 TOP 5 OPÇÕES - MAIORES VALORIZAÇÕES\n\n"
            for i, (index, row) in enumerate(top5.iterrows(), 1):
                relatorio += f"{i}º {row['Simbolo']} ({row['Ativo']}): +{row['Var']:.2f}% | R$ {row['Preco']:.2f}\n"
        else:
            relatorio = "Aguardando abertura do mercado para novos dados."

    except Exception as e:
        relatorio = f"Erro ao processar: {str(e)}"

    msg = MIMEMultipart()
    msg['Subject'] = "🔥 Ranking Top 5 Opções"
    msg['From'] = meu_email
    msg['To'] = meu_email
    msg.attach(MIMEText(relatorio, 'plain'))

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(meu_email, senha)
        server.send_message(msg)

if __name__ == "__main__":
    buscar_top5_opcoes()
