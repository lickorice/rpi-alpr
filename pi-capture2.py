import cv2
import time
import easyocr
import numpy as np
import tensorflow as tf
import sys




def main(video, licenc_plate):

    reader = easyocr.Reader(['en'])
    cap = cv2.VideoCapture(video)
    i = 0
    interpreter = tf.lite.Interpreter(model_path="detect4ph.tflite")
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    print(output_details)


    licence_plates = set([])

    def get_x1x2y1y2(boxes):
        return boxes[1],boxes[3],boxes[0],boxes[2]
    print(video)
    while cap.isOpened():
        start = time.perf_counter()
        ret, frame = cap.read()
        i += 1
        if not ret:
            break
        if cv2.waitKey(1)==ord('q'):
            break
        if i % 2 ==0:
            print('{} Frames'.format(i))
            sys.stdout.flush()
            frame = frame[:900]
            resized=cv2.resize(frame, (320,320), interpolation=cv2.INTER_AREA)
            x = resized.astype(np.float32)
            x /= 255.
            x = np.expand_dims(x, axis=0)
            input_data = x
            interpreter.set_tensor(input_details[0]['index'], input_data)
            interpreter.invoke()
            output_data = interpreter.get_tensor(output_details[0]['index'])
            boxes = interpreter.get_tensor(output_details[1]['index'])
            print(time.perf_counter()-start)
            for j in range(len(output_data[0])):
                if output_data[0][j] > 0.3:
                    print('Frame{} Confidence: {}'.format(i,output_data[0][j]),boxes[0][j] * 320)
                    x1,x2,y1,y2 = get_x1x2y1y2(boxes[0][j])
                    save_frame = frame[max(0,int(y1*899)):min(899,int(y2*899)),max(int(x1*1920),0):min(int(x2*1920),1919)]
                    conf=int(output_data[0][j] * 100)
                    text = reader.readtext(save_frame, allowlist='ABCDEFGHIJKLMNOPQRSTUVWXYZ0987654321 ')
                    if len(text):
                        print(text[0][1])
                        licence_plates.add(text[0][1].upper())
                        cv2.imwrite('./frame_data//{}-{}.png'.format(text[0][1].upper(),conf),save_frame)
                        cv2.rectangle(frame,(int(x1*1920),int(y1*900)),(int(x2*1920),int(y2*900)),(255,0,0), 2)
                    print(time.perf_counter()-start)
                    #print(frame)
                    #print(max(0,int(y1*899)),min(899,int(y2*899)),max(int(x1*1920),0),min(int(x2*1920),1919))
        #cv2.imshow('window',frame)
    cap.release()
    #cv2.destroyAllWindows()
    if licenc_plate in licence_plates:
        print(licenc_plate)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])