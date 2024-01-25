# Importamos librerias
import torch
import cv2
import argparse
#import numpy as np
import os
import glob
import mysql.connector
from mysql.connector import errorcode
from config import DB_CONFIG

# Leemos el modelo
def evaluarDefectos(img, conf_thres):
    model = torch.hub.load('./','custom','./best.pt',source='local', force_reload=True)

    results = model(img)
    data = results.pandas().xyxy[0]

    return (data)

def insertarResultadosEnBD(resultados, img):
    try:
        # Establecer la conexión a la base de datos
        conn = mysql.connector.connect(**DB_CONFIG)
        
        cursor = conn.cursor()

        # Insertar resultados en la base de datos
        for i in range(len(resultados['name'])):
            label = resultados['name'][i]
            confidence = resultados['confidence'][i]

            query = "INSERT INTO resultados (label, confidence, model, img) VALUES (%s, %s, %s, %s)"
            values = (label, confidence, 'Blur - Best_p', img)

            cursor.execute(query, values)

        # Confirmar la transacción y cerrar la conexión
        conn.commit()
        cursor.close()
        conn.close()

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Error: Acceso denegado. Verifica las credenciales.")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Error: Base de datos no existe.")
        else:
            print(f"Error: {err}")
    finally:
        if conn.is_connected():
            conn.close()

def evaluarDefectosEnCarpeta(carpetapath, conf_thres):

    for imagen_path in glob.glob(os.path.join(carpetapath, '*.jpg')):
        imagen = cv2.imread(imagen_path)

        # Evaluar el enfoque de la imagen
        resultados = evaluarDefectos(imagen, conf_thres)

        try:
            for i in range(len(resultados['name'])):
                print(resultados['name'][i], ": ", round(resultados['confidence'][i] * 100, 1), "%")
        except Exception as e:
            print(e)

        # Insertar resultados en la base de datos
        insertarResultadosEnBD(resultados, imagen_path)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=str, default='inference/images', help='source')  # file/folder, 0 for webcam
    parser.add_argument('--conf_thres', type=int, default=0.5, help='confidence threshold')
    opt = parser.parse_args()
    #print(opt)

    # Si se proporciona una carpeta como fuente, procesar todas las imágenes en la carpeta
    if os.path.isdir(opt.source):
        evaluarDefectosEnCarpeta(opt.source, opt.conf_thres)
    else:
        # Carga la imagen
        imagen_path = opt.source
        imagen = cv2.imread(imagen_path)

        # Evalúa el enfoque de la imagen
        resultado = evaluarDefectos(imagen,opt.conf_thres)

        confidence = resultado['confidence']
        label = resultado['name']

        #print(resultado)
        try:
            for i in range(len(label)):
                print(label[i],": ",round(confidence[i]*100,1),"%")
        except Exception as e:
                print(e)
            
        # Insertar resultados en la base de datos
        insertarResultadosEnBD(resultado, imagen_path)


        