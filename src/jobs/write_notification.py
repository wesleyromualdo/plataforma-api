from src.utils import utils

def write_notification(email: str, message=""):
    with open("log.txt", mode="w") as email_file:
        content = f"notification for {email}: {message}"
        email_file.write(content)

def envio_email(subject, html_corpo):
    from datetime import datetime, date
    import pathlib
    from email import encoders
    from email.mime.base import MIMEBase
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    import smtplib
    import traceback

    try:
        json_config = utils.pega_dados_configuracao()
        with open("log.txt", mode="w") as email_file:
            email_file.write(str(json_config))
        fromaddr = json_config['config_email']['fromaddr']
        password = json_config['config_email']['password']
        toaddr = json_config['config_email']['toaddr']
        cc = json_config['config_email']['cc']
        host = json_config['config_email']['host']
        port = json_config['config_email']['port']
        msg = MIMEMultipart()
        
        msg['From'] = fromaddr
        msg['To'] = toaddr
        msg['Subject'] = subject

        body = html_corpo

        msg.attach(MIMEText(body, 'html'))

        #dir_atual = os.getcwd()

        #filename = "Registro_Atividade_" + str(date.today()) + '.csv'
        #arquivolog = [fr'{dir_atual}\logs\{filename}']                        

        #print(arquivolog)
        '''for f in arquivolog:
            attachment = open(f, 'rb')
            part = MIMEBase('application', 'octet-stream')
            part.set_payload((attachment).read())
            encoders.encode_base64(part)
            #part.add_header('Content-Disposition',"attachment; filename= %s" % filename)
            part.add_header('Content-Disposition','attachment; filename="%s"'% os.path.basename(f))

            msg.attach(part)
            attachment.close()'''

        server = smtplib.SMTP(host, port)
        server.starttls()
        server.login(fromaddr, password)
        text = msg.as_string()
        toaddrs = [toaddr] + cc 
        retorno = server.sendmail(fromaddr, toaddrs, text)
        #print(retorno)
        server.quit()
    except Exception as error:
        #self.gerar_logs(f"ERRO AO ENVIAR EMAIL! {error}")
        print(error)
        print('')
        print('')
        message=f'Error on line {traceback.format_exc()}'
        print(message)
        return error