import os
import cv2
import numpy as np
from keras.models import load_model
from keras.preprocessing.image import img_to_array

def xrayhello() :
    model_path = "tahir_bhai_model/xray/Xrays.h5"

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found: {model_path}")

    model = load_model(model_path)

    def preprocess_frame(frame):
        frame = cv2.resize(frame, (100, 100))
        frame = img_to_array(frame)
        frame = frame / 255.0
        frame = np.expand_dims(frame, axis=0)
        return frame

    cap = cv2.VideoCapture(0)



    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        processed_frame = preprocess_frame(frame)
        
        prediction = model.predict(processed_frame)
        probability = prediction[0][0]
        
        if probability < 0.5:
            return "covid"


    cap.release()
    cv2.destroyAllWindows()


