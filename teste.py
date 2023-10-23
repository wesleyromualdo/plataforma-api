import boto3
import botocore
import os

AWS_ACCESS_KEY_ID = "AKIA6QMTKAZTWFYI35N7"
AWS_SECRET_ACCESS_KEY = "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"
AWS_REGION = "sa-east-1"

def upload_file():
    s3_client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

    file_name = 'aneel.zip'

    object_name = f"arquivos/cna/{file_name}"

    #dir_atual = os.getcwd()
    dir_atual = "D:/Zello/CNA/anexos_tarefa"
    dir_atual = f"{dir_atual}/{file_name}"

    try:
        response = s3_client.upload_file(dir_atual, 'rpa-console', object_name)
        print(response)
        #if os.path.exists(dir_atual):
        #    os.remove(dir_atual)
    except botocore.exceptions.ClientError as e:
        print(e)

def download_file():
    s3_client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    file_name = 'aneel.zip'

    object_name = f"arquivos/{file_name}"
    
    s3_client.download_file(
        Bucket='rpa-console',
        Key=object_name,
        Filename=file_name
    )

    '''file_name = 'aneel.zip'
    link = f"https://rpa-console.s3.amazonaws.com/arquivos/{file_name}"

    with open('teste.zip', 'wb') as data:
        bucket.download_fileobj(link, data)
        #s3://rpa-console/arquivos/aneel.zip'''

upload_file()