# Importamos librerias
import torch
import cv2
import argparse
import os

# Leemos el modelo
def evaluarDefectos(img, conf_thres, modelo):
    model = torch.hub.load('./', 'custom', modelo, source='local', force_reload=True)
    results = model(img)
    data = results.pandas().xyxy[0]
    return data

def evaluarDefectosEnCarpeta(carpetapath, conf_thres, modelo):
    for imagen_path in os.listdir(carpetapath):
        if imagen_path.endswith(('.jpg', '.jpeg', '.png')):
            imagen_path = os.path.join(carpetapath, imagen_path)
            imagen = cv2.imread(imagen_path)

            # Evalúa el enfoque de la imagen
            resultado = evaluarDefectos(imagen, conf_thres, modelo)

            confidence = resultado['confidence']
            label = resultado['name']

            try:
                print(f"\nResultados para la imagen {imagen_path}:")
                for i in range(len(label)):
                    print(f"{label[i]}: {round(confidence[i] * 100, 1)}%")

                # Guarda la información en un archivo de texto en el mismo directorio que la imagen
                output_file = f'resultados_{os.path.basename(imagen_path)}.txt'
                with open(output_file, 'w') as file:
                    for l, c in zip(label, confidence):
                        file.write(f"{l}: {round(c * 100, 1)}%\n")

                print(f"La información se ha guardado en {os.path.abspath(output_file)}")

            except Exception as e:
                print(e)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=str, default='inference/images', help='source')  # file/folder, 0 for webcam
    parser.add_argument('--conf_thres', type=int, default=0.5, help='confidence threshold')
    parser.add_argument('--model', type=str, default='ModelBlur.pt', help='ubicacion modelo')
    opt = parser.parse_args()

    # Si se proporciona una carpeta como fuente, procesar todas las imágenes en la carpeta
    if os.path.isdir(opt.source):
        evaluarDefectosEnCarpeta(opt.source, opt.conf_thres, opt.model)
    else:
        # Carga la imagen
        imagen_path = opt.source
        imagen = cv2.imread(imagen_path)

        # Evalúa el enfoque de la imagen
        resultado = evaluarDefectos(imagen, opt.conf_thres, opt.model)

        confidence = resultado['confidence']
        label = resultado['name']

        try:
            print(f"\nResultados para la imagen {imagen_path}:")
            for i in range(len(label)):
                print(f"{label[i]}: {round(confidence[i] * 100, 1)}%")

            # Guarda la información en un archivo de texto en el mismo directorio que la imagen
            output_file = f'resultados_{os.path.basename(imagen_path)}.txt'
            with open(output_file, 'w') as file:
                for l, c in zip(label, confidence):
                    file.write(f"{l}: {round(c * 100, 1)}%\n")

            print(f"La información se ha guardado en {os.path.abspath(output_file)}")

        except Exception as e:
            print(e)
