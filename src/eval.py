import pygame
from logic import SnakeEnv
from main import moves
import numpy as np
import tensorflow as tf
import cv2

# Hier wird das TFLite Modell geladen
interpreter = tf.lite.Interpreter(model_path="model_unquant.tflite")
interpreter.allocate_tensors()

# Ermitteln Sie die Ein- und Ausgabe-Details
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Hier werden die Namen für die Klassen geladen
class_names = open("labels.txt", "r").readlines()

# Startet die Webcam
camera = cv2.VideoCapture(0)

env = SnakeEnv(render_mode="human", fps=7)

game_running = True

while game_running:
    # Escape für Spiel beenden
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                game_running = False
        elif event.type == pygame.QUIT:
            game_running = False

        # Hier wird das Bild der Kamera eingelesen
        ret, image = camera.read()
        image = cv2.resize(image, (224, 224), interpolation=cv2.INTER_AREA)

        # Zeigt das Bild der Webcam an
        cv2.imshow("Webcam Image", image)
        image = np.asarray(image, dtype=np.float32).reshape(1, 224, 224, 3)
        image = (image / 127.5) - 1

        # Hier wird das Bild in das TFLite Modell gegeben
        interpreter.set_tensor(input_details[0]['index'], image)
        interpreter.invoke()
        prediction = interpreter.get_tensor(output_details[0]['index'])

        index = np.argmax(prediction)
        class_name = class_names[index].strip()
        confidence_score = prediction[0][index]
        print("class:", class_name, end=" ")
        print("conf:", str(np.round(confidence_score * 100))[:-2], "%")

        if class_name.startswith("0"):
            env.step(0)
        elif class_name.startswith("1"):
            env.step(1)
        elif class_name.startswith("2"):
            env.step(2)
        elif class_name.startswith("3"):
            env.step(3)
        else:
            env.step(moves[env.current_dir])

camera.release()
cv2.destroyAllWindows()

pygame.display.update()
pygame.time.delay(2000)