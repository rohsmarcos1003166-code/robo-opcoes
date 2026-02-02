import yfinance as yf
import pandas as pd
import smtplib
import os
from email.message import EmailMessage

def executar_robo():
    # --- E-MAIL CORRIGIDO COM O 'S' ---
    meu_email = "rohsmarcos1003166@gmail.com"
    # Puxa a senha do Segredo do GitHub chamado EMAIL_PASSWORD
    senha_app = os.getenv("EMAIL_PASSWORD") 
    
    if not senha_app:
        print("ERRO: O segredo 'EMAIL_PASSWORD' não foi encontrado no GitHub.")
        return

    relatorio = "🚀 RELATÓRIO DE OPÇÕES B3\n" + "="*35 + "\n"
    encontrou = False

    try:
        for t in ["PETR4", "VALE3", "BBDC4", "ITUB4"]:
            ticker = yf.Ticker(f"{t}.SA")
            vencimentos = ticker.options
            
            if vencimentos:
                chain = ticker.option_chain(vencimentos[0])
                # Filtra opções com preço ativo para o e-mail não ir vazio
                ativas = chain.calls[chain.calls['lastPrice'] > 0].head(3)
                
                if not ativas.empty:
                    encontrou = True
                    relatorio += f"\nAtivo: {t} | Vencimento: {vencimentos[0]}\n"
                    relatorio += ativas[['contractSymbol', 'lastPrice']].to_string(index=False) + "\n"
        
        if not encontrou:
            relatorio += "Nenhum dado de negociação disponível agora."

        # CONFIGURAÇÃO DA MENSAGEM
        msg = EmailMessage()
        msg['Subject'] = "📊 Relatório de Opções Atualizado"
        msg['From'] = meu_email
        msg['To'] = meu_email
        msg.set_content(relatorio)

        # ENVIO
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(meu_email, senha_app)
            smtp.send_message(msg)
        print("✅ Sucesso! E-mail enviado para rohsmarcos1003166@gmail.com")

    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    executar_robo()
