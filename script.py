import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def testar_envio():
    meu_email = "rohmarcos1003166@gmail.com"
    # Usando sua senha mais recente da foto
    senha_app = "wvsj hkyd ywtc bcye" 
    
    msg = MIMEMultipart()
    msg['Subject'] = "🚀 TESTE DE CONEXÃO DO ROBÔ"
    msg['From'] = meu_email
    msg['To'] = meu_email
    
    corpo = "Se você está lendo isso, o robô conseguiu logar e enviar o e-mail com sucesso!"
    msg.attach(MIMEText(corpo, 'plain'))

    try:
        print("Tentando conectar ao Gmail...")
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(meu_email, senha_app)
        server.send_message(msg)
        server.quit()
        print("✅ E-mail enviado! Verifique sua caixa de entrada agora.")
    except Exception as e:
        print(f"❌ Erro crítico: {e}")

if __name__ == "__main__":
    testar_envio()
