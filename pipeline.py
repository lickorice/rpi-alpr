import cv2
import time, re
import easyocr
import numpy as np
import tensorflow as tf
import sys
from constants import *

lph_pattern = re.compile("^[A-Z][A-Z][A-Z][0-9][0-9][0-9][0-9]?$")

class Pipeline:

    def __init__(self, video_path):
        self.video_path = video_path
        self.reader = easyocr.Reader(['en'])
        self.plates = {}

    def capture_video(self, frames_per_second):
        cap = cv2.VideoCapture(self.video_path)
        interpreter = tf.lite.Interpreter(model_path="detect4ph.tflite")
        interpreter.allocate_tensors()

        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()

        def get_x1x2y1y2(boxes):
            return boxes[1],boxes[3],boxes[0],boxes[2]

        fctr = 0 # Frame counter
        fctrabs = 0 # Absolute frame counter
        while cap.isOpened():
            ret, frame = cap.read()
            fctr += 1 # Increment frame
            fctrabs += 1
            print("[{:06d}] Processing frames...".format(fctrabs), end="\r")
            if not ret:
                print("End of video detected! Capture execution terminating...")
                break # Frame reading error
            
            # Per frame calculation
            every_x_frame = VIDEO_FPS // frames_per_second
            if fctr >= every_x_frame:
                # Reset frame counter
                fctr = 0

                # Execute detection:
                # -- Resize frame to 320x320 square
                resized = cv2.resize(frame, (320,320), interpolation=cv2.INTER_AREA)
                input_data = resized.astype(np.float32)          # Set as 3D RGB float array
                input_data /= 255.                               # Normalize
                input_data = np.expand_dims(input_data, axis=0)  # Batch dimension (wrap in 4D)

                # Initialize input tensor
                interpreter.set_tensor(input_details[0]['index'], input_data)
                interpreter.invoke()

                # Confidence values
                # output_data = [ n = # of classes [ confidence values of boxes ] ]

                # details = [
                #     {"index": [ n = # of classes [ confidence values of boxes ] ]},
                #     {"index": [ n = # of classes [ details of boxes ] ]}
                # ]
                output_data = interpreter.get_tensor(output_details[0]['index'])

                # Bounding boxes
                boxes = interpreter.get_tensor(output_details[1]['index'])

                for j in range(len(output_data[0])): # For each confidence value of first class [0]
                    if output_data[0][j] > BASE_CONFIDENCE: # If confidence > 
                        x1,x2,y1,y2 = get_x1x2y1y2(boxes[0][j]) # Get box points

                        save_frame = frame[max(0,int(y1*1079)):min(1079,int(y2*1079)),max(int(x1*1920),0):min(int(x2*1920),1919)]

                        conf_in_100 = int(output_data[0][j] * 100)

                        # Execute recognition
                        text = self.reader.readtext(save_frame, allowlist='ABCDEFGHIJKLMNOPQRSTUVWXYZ0987654321 ')
                        if len(text):
                            # Preprocess plate text
                            license_plate = text[0][1].upper()
                            license_plate = license_plate.replace(" ", "")

                            # Pattern matching
                            if lph_pattern.match(license_plate):
                                # Assign confidence to self.plates
                                if license_plate in self.plates:
                                    self.plates[license_plate].append(conf_in_100)
                                else:
                                    self.plates[license_plate] = [conf_in_100]

                                # Save image
                                # cv2.imwrite('./frame_data/{}-{}.jpg'.format(text[0][1].upper(),conf_in_100),save_frame)

        # Release capture
        cap.release()

        print()
        # Average confidences in plates:
        for _p in self.plates:
            self.plates[_p] = sum(self.plates[_p]) / len(self.plates[_p])

    def get_target(self, target):
        if target in self.plates:
            print(f"Target ({target}) found with {self.plates[target]}% detection confidence.")
        elif target == "all":
            for _p in self.plates:
                print(_p, f"{self.plates[_p]}%")
        else:
            print(f"Target ({target}) not found.")

