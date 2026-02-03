import yfinance as yf
import pandas as pd
import smtplib
from email.message import EmailMessage
import os
import time

def buscar_dados_consolidado():
    """Tenta buscar VIX e B3. Retorna os HTMLs se sucesso, ou None se falhar."""
    try:
        # 1. Busca VIX (EUA)
        vix = yf.Ticker("^VIX")
        venc_vix = vix.options[0]
        grade_vix = vix.option_chain(venc_vix)
        total_vix = pd.concat([grade_vix.calls, grade_vix.puts])
        top5_vix = total_vix.nlargest(5, 'volume')[['contractSymbol', 'lastPrice', 'strike', 'volume']]
        top5_vix.columns = ['Ativo', 'Preço', 'Strike', 'Volume']
        html_vix = f"<h3>TOP 5 VIX (EUA) - Venc: {venc_vix}</h3>" + top5_vix.to_html(index=False, border=1)

        # 2. Busca B3 (Brasil - Padrão Opções.net.br)
        # Tentamos PETR4 como termômetro da B3
        petr = yf.Ticker("PETR4.SA")
        venc_br = petr.options[0]
        grade_br = petr.option_chain(venc_br)
        total_br = pd.concat([grade_br.calls, grade_br.puts])
        
        # Se o volume total for 0, significa que a API ainda não atualizou
        if total_br['volume'].sum() <= 0:
            return None # Força a re-tentativa
            
        top5_br = total_br.nlargest(5, 'volume')[['contractSymbol', 'lastPrice', 'strike', 'volume']]
        top5_br['contractSymbol'] = top5_br['contractSymbol'].str.extract(r'([A-Z]{5}\d{1,3})')
        top5_br.columns = ['Ativo', 'Preço', 'Strike', 'Volume']
        html_br = f"<h3>TOP 5 BRASIL (Fonte: Opções.net.br) - Venc: {venc_br}</h3>" + top5_br.to_html(index=False, border=1)

        return html_vix, html_br
    except:
        return None

# --- Lógica de Tentativas (Loop) ---
tentativas = 3
sucesso = False
html_final_vix = ""
html_final_br = ""

for i in range(tentativas):
    print(f"Tentativa {i+1} de {tentativas}...")
    resultado = buscar_dados_consolidado()
    
    if resultado:
        html_final_vix, html_final_br = resultado
        sucesso = True
        print("Dados capturados com sucesso!")
        break # Sai do loop e vai para o envio
    else:
        if i < tentativas - 1: # Se não for a última tentativa, espera
            print("Falha na captura. Aguardando 5 minutos para tentar novamente...")
            time.sleep(300) # Espera 300 segundos (5 minutos)

# Se após 3 tentativas ainda falhar, usamos o Fallback para não ficar sem e-mail
if not sucesso:
    html_final_vix = "<h3>VIX (EUA)</h3><p>Indisponível após 3 tentativas.</p>"
    html_final_br = "<h3>BRASIL (B3)</h3><p>Site Opções.net.br não respondeu. Verifique o fechamento manual.</p>"

# --- Envio do E-mail ---
corpo_email = f"<html><body>{html_final_vix}<br><hr><br>{html_final_br}</body></html>"
msg = EmailMessage()
msg['Subject'] = "RELATÓRIO FINAL: TOP 5 OPÇÕES"
msg['From'] = "rohsmarcos1003166@gmail.com"
msg['To'] = "rohsmarcos1003166@gmail.com"
msg.add_alternative(corpo_email, subtype='html')

try:
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(msg['From'], os.environ.get('EMAIL_PASSWORD'))
        smtp.send_message(msg)
        print("E-mail enviado!")
except Exception as e:
    print(f"Erro no envio: {e}")
