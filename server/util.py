import joblib
import json
import numpy as np
import base64
import cv2
from wavelet import w2d

__class_name_to_number = {}
__class_number_to_name = {}

__model = None

def classify_image(img_b64, file_path=None):        #keeping the option of file_path just in case
    imgs = get_cropped_image_if_2_eyes(file_path, img_b64)

    result = []
    for img in imgs:
        scalled_raw_img = cv2.resize(img, (64, 64))
        img_har = w2d(img, 'db1', 5)
        scalled_img_har = cv2.resize(img_har, (64, 64))
        combined_img = np.vstack((scalled_raw_img.reshape(64 * 64 * 3, 1), scalled_img_har.reshape(64 * 64, 1)))

        len_image_array = 64*64*3 + 64*64

        final = combined_img.reshape(1,len_image_array).astype(float)
        #result.append(class_number_to_name(__model.predict(final)[0])) #if you want to print only name
        
        #As we want to predict multiple things, hence creating dictionary
        result.append({
            'class': class_number_to_name(__model.predict(final)[0]),
            'class_probability': np.around(__model.predict_proba(final)*100,2).tolist()[0],
            'class_dictionary': __class_name_to_number
        })

        return result
    
def class_number_to_name(class_num):   #take num and get name
    return __class_number_to_name[class_num]

def load_saved_artifacts():
    print("loading saved artifacts...start")
    global __class_name_to_number
    global __class_number_to_name

    with open("./artifacts/class_dictionary.json", "r") as f:
        __class_name_to_number = json.load(f)
        __class_number_to_name = {v:k for k,v in __class_name_to_number.items()}

    global __model
    if __model is None:
        with open('./artifacts/saved_model.pkl', 'rb') as f:
            __model = joblib.load(f)
    print("loading saved artifacts...done")

def get_cv2_image_from_base64_string(b64str):
    '''
    credit: https://stackoverflow.com/questions/33754935/read-a-base-64-encoded-image-from-memory-using-opencv-python-library
    :param uri:
    :return:
    '''
    encoded_data = b64str.split(',')[1]
    nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img

def get_cropped_image_if_2_eyes(image_path, image_base64_data):
    face_cascade = cv2.CascadeClassifier('./haarcascades/haarcascade_frontalface_default.xml')
    eye_cascade = cv2.CascadeClassifier('./haarcascades/haarcascade_eye.xml')

    if image_path:
        img = cv2.imread(image_path)
    else:
        img = get_cv2_image_from_base64_string(image_base64_data)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    cropped_faces = []   #There may be multiple faces, hence creating list
    for (x,y,w,h) in faces:
            roi_gray = gray[y:y+h, x:x+w]
            roi_color = img[y:y+h, x:x+w]
            eyes = eye_cascade.detectMultiScale(roi_gray)
            if len(eyes) >= 2:
                cropped_faces.append(roi_color)
    return cropped_faces

def get_b64_img():
    with open("b64.txt") as f:
        return f.read()
    
if __name__ == '__main__':
    load_saved_artifacts()
    print(classify_image( get_b64_img() ))