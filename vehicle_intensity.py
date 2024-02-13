import cv2
from super_gradients.training import models
import numpy as np
import math
import torch


cap = cv2.VideoCapture("Video\VehiclesEnteringandLeaving.mp4")

frame_width = int(cap.get(3))

frame_height = int(cap.get(4))

device = torch.device("cuda:0") if torch.cuda.is_available() else torch.device("cpu")

model = models.get("yolo_nas_s", pretrained_weights="coco")

count = 0

classNames = ["person", "bicycle", "car", "motorbike", "aeroplane", "bus", "train", "truck", "boat",
              "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat",
              "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella",
              "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball", "kite", "baseball bat",
              "baseball glove", "skateboard", "surfboard", "tennis racket", "bottle", "wine glass", "cup",
              "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange", "broccoli",
              "carrot", "hot dog", "pizza", "donut", "cake", "chair", "sofa", "pottedplant", "bed",
              "diningtable", "toilet", "tvmonitor", "laptop", "mouse", "remote", "keyboard", "cell phone",
              "microwave", "oven", "toaster", "sink", "refrigerator", "book", "clock", "vase", "scissors",
              "teddy bear", "hair drier", "toothbrush"
              ]

out = cv2.VideoWriter('output.avi', cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 10, (frame_width, frame_height))
global_img_array = None
w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
print("Frane Width", w)
h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
print("Frame Height", h)
global_img_array = np.ones([int(h), int(w)], dtype = np.uint32)

print("Global Image Numpy Array", global_img_array)
print("Global Image Numpy Array Shape", global_img_array.shape)



while True:
    ret, frame = cap.read()
    count+=1
    if ret:
        result = list(model.predict(frame, conf=0.35))[0]
        bbox_xyxys = result.prediction.bboxes_xyxy.tolist()
        confidences   = result.prediction.confidence
        labels = result.prediction.labels.tolist()
        for (bbox_xyxy, confidence, cls) in zip(bbox_xyxys,confidences, labels):
            bbox = np.array(bbox_xyxy)
            x1, y1, x2, y2 = bbox[0], bbox[1], bbox[2], bbox[3]
            x1, y1, x2, y2 =  int(x1), int(y1), int(x2), int(y2)
            classname = int(cls)
            class_name = classNames[classname]
            conf = math.ceil((confidence*100))/100
            label = f'{class_name}{conf}'
            print("Frame N", count, "", x1, x2, y1, y2)
            t_size = cv2.getTextSize(label, 0, fontScale=1, thickness=2)[0]
            c2 = x1 + t_size[0], y1 - t_size[1] -3
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 3)
            cv2.rectangle(frame, (x1, y1), c2, [255, 144, 30], -1, cv2.LINE_AA)
            cv2.putText(frame, label, (x1, y1-2), 0,1, [255, 255, 255], thickness=1, lineType = cv2.LINE_AA)
            global_img_array[y1:y2, x1:x2] += 1
            print("Global Image Array after While Loop",global_img_array)
            print("Global Image Array after While Loop Shape", global_img_array.shape)
        global_img_array_norm = (global_img_array - global_img_array.min()) / (global_img_array.max() - global_img_array.min()) * 255
        global_img_array_norm = global_img_array_norm.astype('uint8')
        global_img_array_norm = cv2.GaussianBlur(global_img_array_norm, (9,9), 0)
        heatmap_img = cv2.applyColorMap(global_img_array_norm, cv2.COLORMAP_JET)
        super_imposed_img = cv2.addWeighted(heatmap_img, 0.5, frame, 0.5, 0)


        resize_frame = cv2.resize(super_imposed_img, (0,0), fx=0.5, fy=0.5, interpolation = cv2.INTER_AREA)
        out.write(super_imposed_img)
        cv2.imshow("Output Video", resize_frame)
        if cv2.waitKey(1) & 0xFF==ord('1'):
            break
    else:
        break

out.release()
cap.release()
cv2.destroyAllWindows()