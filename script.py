import yfinance as yf
import pandas as pd
import smtplib
from email.message import EmailMessage
import os

def testar_e_gerar_relatorio():
    print("Iniciando extração de dados do Yahoo Finance...")
    try:
        # Busca o ativo com o sufixo correto para o mercado brasileiro
        petr = yf.Ticker("PETR4.SA")
        
        # Obtém as datas de vencimento disponíveis
        vencimentos = petr.options
        if not vencimentos:
            return None, "Erro: Nenhuma opção encontrada para PETR4.SA. Verifique a conexão com o Yahoo."

        # Pega o primeiro vencimento disponível (mais próximo)
        data_vencimento = vencimentos[0]
        opcoes = petr.option_chain(data_vencimento)
        
        # Filtra as colunas principais das CALLS
        df_calls = opcoes.calls[['lastPrice', 'strike', 'percentChange']].head(10)
        
        # Cria a tabela em HTML para o e-mail
        html = f"""
        <html>
            <body>
                <h2>Relatório de Teste - Opções PETR4</h2>
                <p><b>Vencimento Selecionado:</b> {data_vencimento}</p>
                {df_calls.to_html(index=False)}
                <p><i>Este é um envio de teste manual.</i></p>
            </body>
        </html>
        """
        return html, None
    except Exception as e:
        return None, f"Falha técnica: {str(e)}"

# --- Processo de Envio ---
corpo_html, erro = testar_e_gerar_relatorio()

if erro:
    print(erro)
else:
    msg = EmailMessage()
    msg['Subject'] = "TESTE MANUAL: Opções PETR4"
    msg['From'] = "rohsmarcos1003166@gmail.com"
    msg['To'] = "rohsmarcos1003166@gmail.com"
    msg.add_alternative(corpo_html, subtype='html')

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            # O EMAIL_PASSWORD deve estar configurado nos Secrets do GitHub
            senha = os.environ.get('EMAIL_PASSWORD')
            smtp.login(msg['From'], senha)
            smtp.send_message(msg)
            print("Sucesso: E-mail de teste enviado!")
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")
