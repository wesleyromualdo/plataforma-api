import string, boto3, requests, os

def set_credentials():
    response = requests.get(f"169.254.170.2{os.environ['AWS_CONTAINER_CREDENTIALS_RELATIVE_URI']}")

    if response.status_code == 200:
        data = response.json()
        session = boto3.Session(
            aws_access_key_id=data['AccessKeyId'],
            aws_secret_access_key=data['SecretAccessKey'],
            aws_session_token=data['Token']
        )

        event_bridge_client = session.client('events')
        lambda_client = session.client('lambda')
        s3_client = session.client('s3')

        '''filename_s3 = str(dados.tx_nome)+'.zip'
        object_name = f"arquivos/workers/{tx_sigla}/{filename_s3}"
        print(object_name)
        #s3_client = boto3.client('s3', aws_access_key_id=configJson['AWS_ACCESS_KEY_ID'], aws_secret_access_key=configJson['AWS_SECRET_ACCESS_KEY'])
        response = self.s3_client.upload_file(dir_cliente, configJson['S3_BUCKET'], object_name)
        print(response)'''
        
    else:
        raise Exception('Credentials request failed')
    
set_credentials()
    