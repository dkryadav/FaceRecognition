# -*- coding: utf-8 -*-
"""FaceRecognition.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1UxUHycYo8qe-nP_k1D4lPfvcGg1YTQBO

FACE RECOGNITION USING OPEN CV IN PYTHON
"""

from google.colab import drive
drive.mount('/content/drive')

"""GDRIVE MOUNTING CoDE"""

!cp drive/'My Drive'/HaarCascade.xml .
!cp -r /content/drive/'My Drive'/TrainImages .
!cp -r /content/drive/'My Drive'/TestImages .
# !cp drive/'My Drive'/DK1.jpg .
# !cp drive/'My Drive'/ZK12.jpg .

"""Import All Packages"""

import cv2
import os
import numpy as np

def faceDetection(test_img):
  gray_img = cv2.cvtColor(test_img,cv2.COLOR_BGR2GRAY)
  face_haar_cascade = cv2.CascadeClassifier('HaarCascade.xml')
  faces = face_haar_cascade.detectMultiScale(gray_img,scaleFactor=1.3,minNeighbors=5)
  return faces, gray_img

"""DETECT FACE OFF TEST IMAGE IN RECTANGLE FORMAT"""

test_img = cv2.imread('TestImages/DK3.jpg')
faces_detected,gray_img= faceDetection(test_img)
print("Faces Detected:",faces_detected)

"""DETECT AND DISPLAY  THE IMAGEs FRAME AS PER CONVENTION"""

for (x,y,w,h) in faces_detected:
  cv2.rectangle(test_img,(x,y),(x+w,y+h),(255,0,0),thickness=5)

  resized_img=cv2.resize(test_img,(600,600))

  from google.colab.patches import cv2_imshow
  cv2_imshow(resized_img)
  cv2.waitKey(0)
  cv2.destroyAllWindows

"""TRAINING FUNCTION FOR LABEL AND CONFIDENCE OF IMAGES"""

def labels_for_training_data(directory):

  faces = []
  faceId = []

  for path,subdirnames,filenames in os.walk(directory):
    for filename in filenames:
      # if filename.startwith("."):
      #   print("skipping system file")
      #   continue
      id = os.path.basename(path)
      img_path=os.path.join(path,filename)
      print("img_path:",img_path)
      print("id:",id)
      test_img = cv2.imread(img_path)

      if test_img is None:
        print("Image not loaded Properly")
        
      faces_rect,gray_img = faceDetection(test_img)

      if len(faces_rect)!=1:
        continue #we assume single person
      (x,y,w,h) = faces_rect[0]
      roi_gray = gray_img[y:y+w,x:x+h]
      faces.append(roi_gray)
      faceId.append(int(id))
      
  return faces,faceId

"""CLASSIFIER FUCTION BASED ON IMAGES HISTOGRAMM USING LBPH"""

def train_classifier(faces,faceID):
  facerecognizer = cv2.face.LBPHFaceRecognizer_create()
  facerecognizer.train(faces,np.array(faceID))
  return facerecognizer

"""DRAW RECT ACROSS FACE DETECTED AND PUT NAMES OFF OBJECT"""

def draw_rect(test_img,face):
  (x,y,w,h)=face
  cv2.rectangle(test_img,(x,y),(x+w,y+h),(255,0,0),thickness=5)

def put_text(test_img,text,x,y):
  cv2.putText(test_img,text,(x,y),cv2.FONT_HERSHEY_DUPLEX,5,(255,0,0),6)

"""SAVE TRAINING MODEL and THEN USE FOR PREDICTION OFF NEW IMAGES ACCORDING TO LABEL CONFIDENCE"""

# faces, faceID = labels_for_training_data('TrainImages')

# facerecognizer = train_classifier(faces,faceID)
# facerecognizer.save('TrainingData.json')

facerecognizer = cv2.face.LBPHFaceRecognizer_create()
facerecognizer.read('TrainingData.json')

# Camera Capture from real camera 
from IPython.display import Image
try:
  filename = take_photo()
  print('Saved to {}'.format(filename))
  
  # Show the image which was just taken.
  display(Image(filename))
except Exception as err:
  # Errors will be thrown if the user does not have a webcam or if they do not
  # grant the page permission to access it.
  print(str(err))

# -------------------------

# cap = cv2.VideoCapture(0)

# while True:
#   ret,test_img=cap.read()
#   faces_detected,gray_img = faceDetection(test_img)


name = {0:"Zack Knight",1:"D K YADAV"}

for face in faces_detected:
  (x,y,w,h)=face
  roi_gray=gray_img[y:y+h,x:x+h]
  label,confidence = facerecognizer.predict(roi_gray)
  print("Confidence:",confidence)
  print("label:",label)

  draw_rect(test_img,face)
  predicted_name = name[label]
  if (confidence>37):
    continue
  # if confidence>39:
  #   put_text(test_img,predicted_name,x,y)
  put_text(test_img,predicted_name,x,y)

  resized_img = cv2.resize(test_img,(700,500))
  cv2_imshow(resized_img)
  cv2.waitKey(0)
  # if cv2.waitKey(10) == ord('q'):
  #   break
  
  # cap.release()
  cv2.destroyAllWindows

"""GOOGLE COLAB JAVASCRIPT API FOR CAMERA CAPTURE"""

from IPython.display import display, Javascript
from google.colab.output import eval_js
from base64 import b64decode

def take_photo(filename='photo.jpg', quality=0.8):
  js = Javascript('''
    async function takePhoto(quality) {
      const div = document.createElement('div');
      const capture = document.createElement('button');
      capture.textContent = 'Capture';
      div.appendChild(capture);

      const video = document.createElement('video');
      video.style.display = 'block';
      const stream = await navigator.mediaDevices.getUserMedia({video: true});

      document.body.appendChild(div);
      div.appendChild(video);
      video.srcObject = stream;
      await video.play();

      // Resize the output to fit the video element.
      google.colab.output.setIframeHeight(document.documentElement.scrollHeight, true);

      // Wait for Capture to be clicked.
      await new Promise((resolve) => capture.onclick = resolve);

      const canvas = document.createElement('canvas');
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      canvas.getContext('2d').drawImage(video, 0, 0);
      stream.getVideoTracks()[0].stop();
      div.remove();
      return canvas.toDataURL('image/jpeg', quality);
    }
    ''')
  display(js)
  data = eval_js('takePhoto({})'.format(quality))
  binary = b64decode(data.split(',')[1])
  with open(filename, 'wb') as f:
    f.write(binary)
  return filename