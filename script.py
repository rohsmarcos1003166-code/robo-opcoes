import yfinance as yf
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def buscar_dados_com_fallback():
    meu_email = "rohmarcos1003166@gmail.com"
    # ABAIXO: Sua senha de app atualizada
    senha = "wvsj hkyd ywtc bcye" 
    ativos = ["PETR4", "VALE3", "BBDC4", "ITUB4"]
    relatorio = "🚀 RELATÓRIO DE OPÇÕES - MERCADO B3\n" + "-"*45 + "\n"
    encontrou_dados = False

    for t in ativos:
        try:
            ticker = yf.Ticker(f"{t}.SA")
            vencimentos = ticker.options

            if vencimentos:
                prox = vencimentos[0]
                chain = ticker.option_chain(prox)
                
                calls = chain.calls
                puts = chain.puts
                calls['Tipo'] = 'CALL (Compra)'
                puts['Tipo'] = 'PUT (Venda)'
                todas = pd.concat([calls, puts])

                # CORREÇÃO: Filtramos por preço maior que zero para garantir que venha informação
                ativas = todas[todas['lastPrice'] > 0].copy()

                if not ativas.empty:
                    encontrou_dados = True
                    # Pega as 5 opções com maior preço/movimentação
                    top5 = ativas.sort_values(by='lastPrice', ascending=False).head(5)
                    
                    relatorio += f"\nAtivo Principal: {t} | Vencimento: {prox}\n"
                    for _, row in top5.iterrows():
                        relatorio += f"- {row['contractSymbol']} ({row['Tipo']}) | Preço: R$ {row['lastPrice']:.2f}\n"
                    relatorio += "-"*45 + "\n"

        except Exception as e:
            print(f"Erro ao processar {t}: {str(e)}")
            continue

    if not encontrou_dados:
        relatorio = "Atenção: O mercado não retornou dados de negociação para os filtros aplicados no momento."

    # --- CONFIGURAÇÃO E ENVIO DO E-MAIL ---
    msg = MIMEMultipart()
    msg['Subject'] = "📊 Resultado Opções: Atualizado"
    msg['From'] = meu_email
    msg['To'] = meu_email
    msg.attach(MIMEText(relatorio, 'plain'))

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(meu_email, senha)
        server.send_message(msg)
        server.quit()
        print("E-mail enviado com sucesso!")
    except Exception as e:
        print(f"Falha no envio do e-mail: {str(e)}")

if __name__ == "__main__":
    buscar_dados_com_fallback()
