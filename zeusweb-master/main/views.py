from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators import gzip
from django.http import StreamingHttpResponse, JsonResponse, HttpResponse, HttpResponseRedirect
import cv2
import threading
from django.urls import reverse
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from playsound import playsound
from sensor_msgs.msg import Image
from std_msgs.msg import Int16, Int32MultiArray
from cv_bridge import CvBridge
import rospy
import mediapipe as mp


product_name = ['AlmondMilk', 'AppleJuice', 'Carrot', 'ChocolateMilk', 'Clock', 'Doraemon', 'Egg', 'Fish', 'GardeningSet',
                'JellO', 'RoundBread', 'Soap', 'Sponge', 'SquareBread','StrawberryMilk', 'SweetPotato', 'Tea', 'Tomato', 'WetTissue']
product_price = [1500, 1200, 1700, 1300, 2000, 1600, 2000, 3200, 1800, 2000, 4800, 2000, 1500, 3500, 800, 1400, 4500, 4200, 3000]

total_price = 0
products = []
object_list = []
page = 1
user = 0 # default = 0(비회원)

def main(request):
    global page, total_price, products, object_list, user
    if request.method == 'POST': # 지금은 버튼 이벤트로 1을 받아오도록 구현
        #page = subscribe_tester.page
        if request.POST.get("move_page") != None: # python request test용
            # User 정보 받아오는거 구현
            user = subscribe_tester.user_id
            page = int(request.POST.get("move_page"))
            print('Python request: '+ str(page))
            if page == 1:
                # 초기화
                user = 0
                total_price = 0
                products = []
                object_list = []

    return render(request, 'main/main.html', {'products': products, 'total': total_price, 'page': page, 'user': user})

class SubscribeTester:
    def __init__(self):
        rospy.init_node('ui_image_ros_subscriber')
        self.cv_bridge = CvBridge()
        detectron_topic = '/detectron_img'
        object_label_topic = '/object_labels'
        user_id_topic = '/user_id'
        self.user_id = 0
        _image_sub = rospy.Subscriber(detectron_topic, Image, self._rgb_callback)
        _image_sub2 = rospy.Subscriber(object_label_topic, Int32MultiArray, self._object_label_callback)
        _user_id_topic_sub = rospy.Subscriber(user_id_topic, Int16, self._user_id_topic_callback)

    def _rgb_callback(self, img_msg):
        self.cv_image = self.cv_bridge.imgmsg_to_cv2(img_msg, 'passthrough')
        # cv2.imshow('detecron_img', self.cv_image)
        # cv2.waitKey(1)

    # @api_view(['GET', 'POST', ])
    def _user_id_topic_callback(self, data):
        self.user_id = int(data.data)
        print('user_id', self.user_id)

    def _object_label_callback(self, data):
        self.object_label_list = list(data.data)
        global page
        if page == 3:
            for i in self.object_label_list:
                if i not in object_list:
                    object_list.append(i)
                    products.append([product_name[i], 1, product_price[i]])
                    playsound("/home/snubi/PycharmProjects/snubi_zeus2022/zeusweb-master/beep.mp3")
                    global total_price
                    total_price += product_price[i]

                    print(products)

subscribe_tester = SubscribeTester()


# detectron camera
class DetectronVideoCamera(object):
    def __init__(self):
        self.frame = subscribe_tester.cv_image
        threading.Thread(target=self.update, args=()).start()

    def get_frame(self):
        image = self.frame
        _, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()

    def update(self):
        while True:
            self.frame = subscribe_tester.cv_image

class FaceVideoCamera(object):

    def __init__(self):
        self.video = cv2.VideoCapture(0)
        (self.grabbed, self.frame) = self.video.read()
        self.mpDraw = mp.solutions.drawing_utils
        self.mpFaceMesh = mp.solutions.face_mesh
        self.faceMesh = self.mpFaceMesh.FaceMesh(max_num_faces=1)
        self.drawSpec = self.mpDraw.DrawingSpec(thickness=1, circle_radius=1)
        threading.Thread(target=self.update, args=()).start()

    def __del__(self):
        self.video.release()

    def get_frame(self):
        image = self.frame
        _, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()

    def update(self):
        while True:
            (self.grabbed, self.frame) = self.video.read()
            imgRGB = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
            results = self.faceMesh.process(imgRGB)
            if results.multi_face_landmarks:
                for faceLms in results.multi_face_landmarks:
                    self.mpDraw.draw_landmarks(self.frame, faceLms, self.mpFaceMesh.FACEMESH_CONTOURS, self.drawSpec, self.drawSpec)
                    for id, lm in enumerate(faceLms.landmark):
                        ih, iw, ic = self.frame.shape
                        x, y = int(lm.x * iw), int(lm.y * ih)
                        #print(id, x, y)

            #cv2.imshow("Image", img)
            #cv2.waitKey(1)

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield(b'--frame\r\n'
              b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@gzip.gzip_page
def camera(request):
    try:
        cam = DetectronVideoCamera()
        return StreamingHttpResponse(gen(cam), content_type="multipart/x-mixed-replace;boundary=frame")
    except:  # This is bad! replace it with proper handling
        print("에러입니다...")
        pass

@gzip.gzip_page
def face(request):
    try:
        facecam = FaceVideoCamera()
        return StreamingHttpResponse(gen(facecam), content_type="multipart/x-mixed-replace;boundary=frame")
    except:  # This is bad! replace it with proper handling
        print("에러입니다...")
        pass

