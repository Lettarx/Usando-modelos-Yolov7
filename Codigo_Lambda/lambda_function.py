import json
import boto3

def lambda_handler(event, context):
    # Configura el cliente de Lambda
    lambda_client = boto3.client('lambda', region_name='us-east-1')

    # Nombre de la siguiente función Lambda a invocar
    NEXT_STEP_API = "NombreFuncionLambda"

    # Llama a la siguiente función Lambda de forma síncrona
    if NEXT_STEP_API:
        print(f'Invocando la función Lambda: {NEXT_STEP_API}')
        response = lambda_client.invoke(
            FunctionName=NEXT_STEP_API,
            InvocationType='RequestResponse'
        )
        result_payload = json.loads(response['Payload'].read())

        print('Resultado de la invocación:', result_payload)

    
