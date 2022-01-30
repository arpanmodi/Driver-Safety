from flask import Flask,render_template,Response,request
import cv2
import os
import time

sound = 'Buzzer.wav'

app=Flask(__name__)

camera=cv2.VideoCapture(0)

def gen_frames():
    eyes_closed = 0
    counter_1 = 0
    counter_2 = 0
    yawn_counter = 0
    not_attentive = 0
    notyawn_counter = 0
    nosleep_counter = 0
    while True:
         ## read the camera frame
        success,img = camera.read()
        if not success:
            break
        else:
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
            phone_cascade = cv2.CascadeClassifier('haarcascade/Phone_Cascade.xml')
            mouth_cascade = cv2.CascadeClassifier('haarcascade/haarcascade_mcs_mouth.xml')

            ret, img = camera.read()
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            phones = phone_cascade.detectMultiScale(gray, 2, 9)

            if len(faces) == 0:
                not_attentive += 1

            if not_attentive > 25:
                font = cv2.FONT_HERSHEY_SIMPLEX
                cv2.putText(img, 'PAY ATTENTION!!', (10, 250), font, 2, (0, 0, 255), 2)
                os.system('start Buzzer.wav')
                not_attentive = 0

            for (x, y, w, h) in phones:
                cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 255), 2)
                font = cv2.FONT_HERSHEY_SIMPLEX
                cv2.putText(img, 'HANDS ON WHEELS!', (x - w, y - h), font, 0.5, (11, 255, 255), 2, cv2.LINE_AA)

            for (x, y, w, h) in faces:
                cv2.rectangle(img, (x, y),(x + w, y + h), (255, 0, 0), 2)
                roi_gray = gray[y:y+h, x:x+w]
                roi_color = img[y:y+h, x:x+w]
                roi_gray_mouth = gray[y + (h // 2): y + h, x:x + w]
                roi_color_mouth = img[y + (h // 2): y + h, x:x + w]
                roi_color = img[y:y + h, x:x + w]
                eyes = eye_cascade.detectMultiScale(roi_gray)

                for (ex,ey,ew,eh) in eyes:
                    cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)

                if eyes_closed > 0:
                    nosleep_counter += 1

                if (nosleep_counter - eyes_closed) > 10:
                    eyes_closed = 0
                    nosleep_counter = 0

                if len(eyes) == 0:
                    eyes_closed += 1
                    print('close:', eyes_closed)
                    if eyes_closed > 5:
                        font = cv2.FONT_HERSHEY_SIMPLEX
                        cv2.putText(img, 'SLEEPING!!!', (10, 250), font, 4, (0, 0, 255), 2)
                        os.system('start Buzzer.wav')
                        time.sleep(1)
                        eyes_closed = 0
                        nosleep_counter = 0

                        esc = cv2.waitKey(100) & 0xFF  # if esc is pressed
                        if esc == 27:
                            eyes_closed = 0



            #cv2.imshow('img', img)
            #k = cv2.waitKey(30) & 0xFF
            #cv2.imshow('img', img)
            #k = cv2.waitKey(30) & 0xFF


        ret,buffer=cv2.imencode('.jpg',img)
        frame=buffer.tobytes()

        yield(b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/')
def index():
    if request.method == 'POST':
        if request.form.get('action1') == 'VALUE1':
            pass  # do something
        elif request.form.get('action2') == 'VALUE2':
            pass  # do something else
        else:
            pass  # unknown
    elif request.method == 'GET':
        return render_template('index.html')
'''@app.route('/action')
def stopStream():
    if request.method == 'POST':
        print("inside function")
        camera.release()'''



def gen():
    frame = camera.read()
    yield (b'--img\r\n'
    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/action", methods = ['POST'])
def action():
    success,frame= camera.read()

if __name__=="__main__":
    app.run(debug=False)