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
                # Pega o vencimento mais próximo
                prox_vencimento = vencimentos[0]
                calls = ticker.option_chain(prox_vencimento).calls
                # Filtra apenas opções que tiveram movimento
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
            # Pega as 5 que mais valorizaram
            top5 = df.sort_values(by='Var', ascending=False).head(5)

            relatorio = "🏆 TOP 5 OPÇÕES - MAIORES VALORIZAÇÕES DA BOLSA\n"
            relatorio += f"Ativos monitorados: {', '.join(ativos)}\n"
            relatorio += "-" * 45 + "\n\n"
            
            for i, (index, row) in enumerate(top5.iterrows(), 1):
                relatorio += f"{i}º LUGAR: {row['Simbolo']} ({row['Ativo']})\n"
                relatorio += f"📈 Valorização: +{row['Var']:.2f}%\n"
                relatorio += f"💰 Preço: R$ {row['Preco']:.2f} | Volume: {int(row['Vol'])}\n"
                relatorio += "." * 45 + "\n"
        else:
            relatorio = "Aviso: Nenhuma negociação encontrada nos ativos selecionados hoje."

    except Exception as e:
        relatorio = f"Erro ao processar ranking: {str(e)}"

    # Montagem do E-mail
    msg = MIMEMultipart()
    msg['Subject'] = "🔥 Ranking das 5 Opções Explosivas"
    msg['From'] = meu_email
    msg['To'] = meu_email
    msg.attach(MIMEText(relatorio, 'plain'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(meu_email, senha)
            server.send_message(msg)
        print("Relatório enviado com sucesso!")
    except Exception as e:
        print(f"Erro no envio do e-mail: {e}")

if __name__ == "__main__":
    buscar_top5_opcoes()
