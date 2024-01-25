import torch
import cv2
import base64
import numpy as np
import json
import boto3

def download_model_from_s3(bucket_name, key, local_path):
    s3 = boto3.client('s3')
    s3.download_file(bucket_name, key, local_path)

def evaluarDefectos(event, context):
    try:
        # Obtener la imagen desde el evento de Lambda
        imagen_base64 = event['imagen_base64']
        imagen_bytes = base64.b64decode(imagen_base64)
        imagen_np = np.frombuffer(imagen_bytes, dtype=np.uint8)
        img = cv2.imdecode(imagen_np, cv2.IMREAD_COLOR)

        # Descargar el modelo desde S3 (ajustar según sea necesario)
        s3_bucket = 'nombre_de_tu_bucket'
        s3_key = 'ruta/al/modelo.pt'
        local_model_path = '/tmp/modelo.pt'  # Directorio temporal en Lambda
        download_model_from_s3(s3_bucket, s3_key, local_model_path)

        # Cargar el modelo
        model = torch.load(local_model_path, map_location=torch.device('cpu')) #Puede dar error
        #Si da error intentar con model = torch.hub.load('ubicacion_hubconfig.py','custom','ubicacion_modelo.py',source='local', force_reload=True)
        
        model.eval()

        # Ejecutar el modelo en la imagen
        results = model(img)

        # Procesar los resultados
        data = results.pandas().xyxy[0]

        # Convertir a formato JSON y devolver como resultado
        result_json = data.to_json(orient='records')
        return {
            'statusCode': 200,
            'body': json.dumps(result_json)
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }