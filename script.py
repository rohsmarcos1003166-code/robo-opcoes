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
                # Pega as Calls
                calls = ticker.option_chain(prox_vencimento).calls
                # Filtra apenas quem teve negócio
                ativas = calls[calls['volume'] > 0].copy()
                
                if not ativas.empty:
                    for _, linha in ativas.iterrows():
                        # Usamos 'percentChange' que é o nome padrão do Yahoo Finance
                        todas_opcoes.append({
                            'Ativo': t,
                            'Simbolo': linha['contractSymbol'],
                            'Var': linha['percentChange'],
                            'Preco': linha['lastPrice'],
                            'Vol': linha['volume']
                        })

        if todas_opcoes:
            df = pd.DataFrame(todas_opcoes)
            # Organiza pelas 5 maiores variações
            top5 = df.sort_values(by='Var', ascending=False).head(5)

            relatorio = "🏆 TOP 5 OPÇÕES QUE MAIS VALORIZARAM\n"
            relatorio += "(Dados de PETR4, VALE3, BBDC4 e ITUB4)\n\n"
            
            for i, (index, row) in enumerate(top5.iterrows(), 1):
                relatorio += f"{i}º Lugar: {row['Simbolo']} ({row['Ativo']})\n"
                relatorio += f"📈 Valorização: +{row['Var']:.2f}%\n"
                relatorio += f"💰 Preço do Prêmio: R$ {row['Preco']:.2f}\n"
                relatorio += f"📊 Volume: {int(row['Vol'])}\n"
                relatorio += "-" * 35 + "\n"
        else:
            relatorio = "Atenção: Nenhuma negociação de opção encontrada para esses ativos no momento."

    except Exception as e:
        relatorio = f"Erro técnico ao processar: {str(e)}"

    # Envio do e-mail
    msg = MIMEMultipart()
    msg['Subject'] = "🔥 TOP 5: Ranking de Opções Atualizado"
    msg['From'] = meu_email
    msg['To'] = meu_email
    msg.attach(MIMEText(relatorio, 'plain'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(meu_email, senha)
            server.send_message(msg)
        print("E-mail enviado!")
    except Exception as e:
        print(f"Erro no envio: {e}")

if __name__ == "__main__":
    buscar_top5_opcoes()
