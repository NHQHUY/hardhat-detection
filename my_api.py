from flask import Flask,render_template,Response, request,url_for,redirect
import pickle
import cv2
import os
from random import random
from sv_model import infer
app=Flask(__name__)
app.config['UPLOAD_FOLDER'] = "static"
camera=cv2.VideoCapture(0)

def generate_frames():
    while True:
            
        ## read the camera frame
        
        ret, frame = camera.read()
        # Hiển thị
        img0 = infer(frame)
        ret,buffer=cv2.imencode('.jpg',img0)
        frame=buffer.tobytes()

        yield(b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                   

@app.route("/", methods=['GET', 'POST'])
def home_page():
    # Nếu là POST (gửi file)
    if request.method == "POST":
         try:
            # Lấy file gửi lên
            image = request.files['file']
            print("loi = ",image)
            if image:
                # Lưu file
                path_to_save = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
                print("Save = ", path_to_save)
                image.save(path_to_save)

                # Convert image to dest size tensor
                frame = cv2.imread(path_to_save)

                frame = infer(frame)
                cv2.imwrite(path_to_save, frame)
                
                    

                return render_template("index1.html", user_image = image.filename , rand = str(random()),
                                           msg="Tải file lên thành công")
                
            else:
                # Nếu không có file thì yêu cầu tải file
                return redirect(url_for('index'))#render_template('index1.html', msg='Hãy chọn file để tải lên')

         except Exception as ex:
            # Nếu lỗi thì thông báo
            print(ex)
            return render_template('index1.html', msg='Không nhận diện được vật thể')
        #redirect(url_for('video'))
    else:
        # Nếu là GET thì hiển thị giao diện upload
        return render_template('index1.html')

@app.route('/video')
def index():
    return render_template('index0.html')

@app.route('/video/infer')
def video():
    #render_template('index0.html')
    return Response(generate_frames(),mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__=="__main__":
    app.run(debug=True)

