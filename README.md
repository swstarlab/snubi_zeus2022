# snubi_zeus2022
roboworld 2022의 R-BIZ 챌린지를 위한 snubi팀 코드

![server_setting](./assets/figure1.png)  

### Required environment
- Ubuntu 20.04
- Python 3.7
- cuda 11.1

### Download model
detectron model 코드 
- [Google drive link](https://drive.google.com/drive/folders/1Wcq2GfciXhIvtQFdPic6z17PjJzO91z-?usp=sharing)  

### Running Scenario code
기본 구조는, socket통신 기준으로 snubi 컴퓨터가 client, zeus의 controller 가 server 입니다.
따라서 server 파일을 먼저 돌리고, client를 그 뒤 돌려 양쪽간 socket통신을 수행해 줍니다.

### Server Node
1. access to controller
```Shell
   ./connect_robot # ssh i611usr@192.168.0.23 
   pw : i611
   ```
2. python 파일 실행
```Shell
   python controller_receiver.py # i611 로봇 action 코드 
   ```
### Client Node
- 시나리오 코드를 실행할 경우
```Shell
   (venv) python main_client.py 
   >>> what is your name : [시나리오 코드 입력]
   ```

- 테스트 코드를 실행할 경우 

```Shell
   (venv) python test_client.py
   ```
1. 좌우 ad, 앞뒤 ws, 위아래 rf로 간단하게 tcp 이동
2. p,l로 그리퍼 close, open 가능
3. h로 home_pos 이동, gripper로 그리퍼 갈아끼기 모션으로 이동
4. 그밖에 추가적으로 필요하신 기능은 if 문 추가해서 만들어 주세요.

### Running Detectron2 with webcam

```Shell
cd detectron2
python demo/demo.py\
    --config-file configs/COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml\
    --webcam\
    --confidence-threshold 0.5\
    --opts MODEL.WEIGHTS ../models/COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x/137849600/model_final_f10217.pkl

# GPU VRAM COST : 2G 
```
Todo
1. vision 모듈과 연결.
2. 계산대 ui 모듈과 연결
3. stt 모듈과 연결
4. placing 위치에 적절히 놓기.
5. 장바구니 꺼내는 모션 설계.
