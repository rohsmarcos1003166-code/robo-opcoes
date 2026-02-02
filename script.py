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
                # Pega as Calls (opções de compra)
                calls = ticker.option_chain(prox_vencimento).calls
                # Filtra apenas as que tiveram negociação (Volume > 0)
                ativas = calls[calls['volume'] > 0].copy()
                
                if not ativas.empty:
                    for _, linha in ativas.iterrows():
                        todas_opcoes.append({
                            'Ativo': t,
                            'Simbolo': linha['contractSymbol'],
                            'Valorizacao': linha['percentChange'],
                            'Preco': linha['lastPrice'],
                            'Volume': linha['volume']
                        })

        # Transforma em tabela e pega as 5 melhores
        df = pd.DataFrame(todas_opcoes)
        top5 = df.sort_values(by='Valorizacao', ascending=False).head(5)

        # Monta o corpo do e-mail
        relatorio = "🏆 TOP 5 OPÇÕES QUE MAIS VALORIZARAM HOJE\n"
        relatorio += "(Considerando PETR4, VALE3, BBDC4 e ITUB4)\n\n"
        
        for i, (index, row) in enumerate(top5.iterrows(), 1):
            relatorio += f"{i}º Lugar: {row['Simbolo']} ({row['Ativo']})\n"
            relatorio += f"📈 Valorização: +{row['Valorizacao']:.2f}%\n"
            relatorio += f"💰 Preço do Prêmio: R$ {row['Preco']:.2f}\n"
            relatorio += f"📊 Volume: {int(row['Volume'])}\n"
            relatorio += "-" * 35 + "\n"

    except Exception as e:
        relatorio = f"Erro ao processar o ranking: {e}"

    # Envio do e-mail
    msg = MIMEMultipart()
    msg['Subject'] = "🔥 TOP 5: Maiores Valorizações em Opções"
    msg['From'] = meu_email
    msg['To'] = meu_email
    msg.attach(MIMEText(relatorio, 'plain'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(meu_email, senha)
            server.send_message(msg)
        print("Ranking Top 5 enviado!")
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    buscar_top5_opcoes()
