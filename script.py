import yfinance as ticker
import pandas as pd
import smtplib
from email.message import EmailMessage

# --- CONFIGURAÇÃO ---
ATIVOS = ['PETR4.SA', 'VALE3.SA', 'BBDC4.SA', 'ITUB4.SA']
MEU_EMAIL = "seu-email@gmail.com"
MINHA_SENHA = "sua-senha-de-app" # Aquela de 16 dígitos do Google

def coletar_dados():
    relatorio = "Relatório de Opções - Consolidado\n\n"
    encontrou_dados = False

    for acao in ATIVOS:
        try:
            print(f"Coletando dados de {acao}...")
            obj = ticker.Ticker(acao)
            vencimentos = obj.options
            
            if not vencimentos:
                continue

            # Pega o primeiro vencimento disponível
            opcoes = obj.option_chain(vencimentos[0])
            todas = pd.concat([opcoes.calls, codecs.puts])

            # AJUSTE DA LINHA 27-31: Filtro mais flexível (Preço > 0)
            # Aceita dados mesmo que o volume oficial ainda não tenha caído no sistema
            ativas = todas[todas['lastPrice'] > 0.01].copy()

            if not ativas.empty:
                encontrou_dados = True
                relatorio += f"\n--- {acao} (Vencimento: {vencimentos[0]}) ---\n"
                # Pega as 5 mais negociadas ou com maior preço
                top5 = ativas.sort_values(by='lastPrice', ascending=False).head(5)
                for i, row in top5.iterrows():
                    relatorio += f"Opção: {row['contractSymbol']} | Preço: R$ {row['lastPrice']:.2f}\n"

        except Exception as e:
            print(f"Erro ao processar {acao}: {e}")
            continue

    if encontrou_dados:
        enviar_email(relatorio)
    else:
        enviar_email("O mercado não gerou dados processáveis para os filtros atuais.")

def enviar_email(conteudo):
    msg = EmailMessage()
    msg.set_content(conteudo)
    msg['Subject'] = "Relatório de Opções B3"
    msg['From'] = MEU_EMAIL
    msg['To'] = MEU_EMAIL

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(MEU_EMAIL, MINHA_SENHA)
            smtp.send_message(msg)
        print("E-mail enviado com sucesso!")
    except Exception as e:
        print(f"Falha ao enviar e-mail: {e}")

if __name__ == "__main__":
    coletar_dados()
