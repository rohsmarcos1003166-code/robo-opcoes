import yfinance as yf
import smtplib
import os
import pandas as pd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def buscar_dados_com_fallback():
    meu_email = "rohsmarcos1003166@gmail.com"
    senha = os.getenv("EMAIL_PASSWORD")
    ativos = ["PETR4", "VALE3", "BBDC4", "ITUB4"]
    todas_opcoes = []
    
    try:
        for t in ativos:
            ticker = yf.Ticker(f"{t}.SA")
            vencimentos = ticker.options
            
            if vencimentos:
                prox = vencimentos[0]
                chain = ticker.option_chain(prox)
                
                # Une Calls e Puts
                calls, puts = chain.calls, chain.puts
                calls['Tipo'], puts['Tipo'] = 'CALL (Compra)', 'PUT (Venda)'
                todas = pd.concat([calls, puts])
                
                # Filtra apenas quem teve negociação (Volume > 0)
                # O yfinance mantém os dados do último pregão se o mercado estiver fechado
                ativas = todas[todas['volume'] > 0].copy()
                
                for _, linha in ativas.iterrows():
                    todas_opcoes.append({
                        'Ativo': t,
                        'Simbolo': linha['contractSymbol'],
                        'Tipo': linha['Tipo'],
                        'Var': linha['percentChange'],
                        'Preco': linha['lastPrice'],
                        'Vol': linha['volume']
                    })

        if todas_opcoes:
            df = pd.DataFrame(todas_opcoes)
            
            # 1. Ranking de Valorização (Top 5)
            top5_alta = df.sort_values(by='Var', ascending=False).head(5)
            
            # 2. A Mais Negociada do Dia (Maior Volume)
            mais_negociada = df.sort_values(by='Vol', ascending=False).iloc[0]

            relatorio = "📊 RELATÓRIO DO ÚLTIMO PREGÃO (Sexta-feira/Hoje)\n"
            relatorio += "="*45 + "\n\n"
            relatorio += "💎 A OPÇÃO MAIS NEGOCIADA:\n"
            relatorio += f"Ativo: {mais_negociada['Ativo']} | Símbolo: {mais_negociada['Simbolo']}\n"
            relatorio += f"Tipo: {mais_negociada['Tipo']}\n"
            relatorio += f"Volume: {int(mais_negociada['Vol']):,} contratos\n"
            relatorio += f"Fechamento: R$ {mais_negociada['Preco']:.2f} ({mais_negociada['Var']:+.2f}%)\n"
            relatorio += "\n" + "-"*45 + "\n\n"
            
            relatorio += "🚀 TOP 5 MAIORES ALTAS:\n"
            for i, (index, row) in enumerate(top5_alta.iterrows(), 1):
                relatorio += f"{i}º {row['Simbolo']} ({row['Ativo']}): +{row['Var']:.2f}% | R$ {row['Preco']:.2f}\n"
        else:
            relatorio = "Erro: Não foram encontrados dados de negociação recentes."

    except Exception as e:
        relatorio = f"Erro no processamento: {str(e)}"

    # Configuração do E-mail
    msg = MIMEMultipart()
    msg['Subject'] = "📈 Resultado Opções: Mais Negociada + Top 5"
    msg['From'] = meu_email
    msg['To'] = meu_email
    msg.attach(MIMEText(relatorio, 'plain'))

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(meu_email, senha)
        server.send_message(msg)
    print("E-mail enviado!")

if __name__ == "__main__":
    buscar_dados_com_fallback()
