import argparse
import time
from pathlib import Path

import csv
import cv2
import torch
import torch.backends.cudnn as cudnn
from numpy import random
import numpy as np

from models.experimental import attempt_load
from utils.datasets import LoadStreams, LoadImages
from utils.general import check_img_size, check_requirements, check_imshow, non_max_suppression, apply_classifier, \
    scale_coords, xyxy2xywh, strip_optimizer, set_logging, increment_path
from utils.plots import plot_one_box
from utils.torch_utils import select_device, load_classifier, time_synchronized, TracedModel
import joblib
import pandas as pd

def detect(save_img=False):
    source, weights, view_img, save_txt, imgsz, trace = opt.source, opt.weights, opt.view_img, opt.save_txt, opt.img_size, not opt.no_trace
    save_img = not opt.nosave and not source.endswith('.txt')  # save inference images
    webcam = source.isnumeric() or source.endswith('.txt') or source.lower().startswith(
        ('rtsp://', 'rtmp://', 'http://', 'https://'))

    # Directories
    save_dir = Path(increment_path(Path(opt.project) / opt.name, exist_ok=opt.exist_ok))  # increment run
    (save_dir / 'labels' if save_txt else save_dir).mkdir(parents=True, exist_ok=True)  # make dir

    # Initialize
    set_logging()
    device = select_device(opt.device)
    half = device.type != 'cpu'  # half precision only supported on CUDA

    # Load model
    model = attempt_load(weights, map_location=device)  # load FP32 model
    stride = int(model.stride.max())  # model stride
    imgsz = check_img_size(imgsz, s=stride)  # check img_size

    if trace:
        model = TracedModel(model, device, opt.img_size)

    if half:
        model.half()  # to FP16

    # Second-stage classifier
    classify = False
    if classify:
        modelc = load_classifier(name='resnet101', n=2)  # initialize
        modelc.load_state_dict(torch.load('weights/resnet101.pt', map_location=device)['model']).to(device).eval()

    # Set Dataloader
    vid_path, vid_writer = None, None
    if webcam:
        view_img = check_imshow()
        cudnn.benchmark = True  # set True to speed up constant image size inference
        dataset = LoadStreams(source, img_size=imgsz, stride=stride)
    else:
        dataset = LoadImages(source, img_size=imgsz, stride=stride)

    # Get names and colors
    names = model.module.names if hasattr(model, 'module') else model.names
    colors = [[random.randint(0, 255) for _ in range(3)] for _ in names]

    # Run inference
    if device.type != 'cpu':
        model(torch.zeros(1, 3, imgsz, imgsz).to(device).type_as(next(model.parameters())))  # run once
    old_img_w = old_img_h = imgsz
    old_img_b = 1

    t0 = time.time()
    for path, img, im0s, vid_cap in dataset:
        img = torch.from_numpy(img).to(device)
        img = img.half() if half else img.float()  # uint8 to fp16/32
        img /= 255.0  # 0 - 255 to 0.0 - 1.0
        if img.ndimension() == 3:
            img = img.unsqueeze(0)

        # Warmup
        if device.type != 'cpu' and (old_img_b != img.shape[0] or old_img_h != img.shape[2] or old_img_w != img.shape[3]):
            old_img_b = img.shape[0]
            old_img_h = img.shape[2]
            old_img_w = img.shape[3]
            for i in range(3):
                model(img, augment=opt.augment)[0]

        # Inference
        t1 = time_synchronized()
        with torch.no_grad():   # Calculating gradients would cause a GPU memory leak
            pred = model(img, augment=opt.augment)[0]
        t2 = time_synchronized()

        # Apply NMS
        pred = non_max_suppression(pred, opt.conf_thres, opt.iou_thres, classes=opt.classes, agnostic=opt.agnostic_nms)
        t3 = time_synchronized()

        # Apply Classifier
        if classify:
            pred = apply_classifier(pred, modelc, img, im0s)

        # Process detections
        for i, det in enumerate(pred):  # detections per image
            if webcam:  # batch_size >= 1
                p, s, im0, frame = path[i], '%g: ' % i, im0s[i].copy(), dataset.count
            else:
                p, s, im0, frame = path, '', im0s, getattr(dataset, 'frame', 0)

            p = Path(p)  # to Path
            save_path = str(save_dir / p.name)  # img.jpg
            txt_path = str(save_dir / p.stem) + ("" if dataset.mode == 'image' else f'_{frame}') + (".csv")
            gn = torch.tensor(im0.shape)[[1, 0, 1, 0]]  # normalization gain whwh
            if len(det):
                # Rescale boxes from img_size to im0 size
                det[:, :4] = scale_coords(img.shape[2:], det[:, :4], im0.shape).round()
                # Print results
                z1 = []
                z = []
                k = []
                l = []
                area = []
                
                # polygon = np.array([
                #     [960, 715],
                #     [1280, 330],
                #     [40, 450], 
                #     [775, 215],
                #     [210,715]
                # ])
                # cv2.line(im0,polygon[0],polygon[1],(0,255,0),2)
                # cv2.line(im0,polygon[0],polygon[4],(0,255,0),2)
                # cv2.line(im0,polygon[2],polygon[4],(0,255,0),2)
                # cv2.line(im0,polygon[2],polygon[3],(0,255,0),2)
                # cv2.line(im0,polygon[3],polygon[1],(0,255,0),2)
                jumlahkend = 0
                for kendaraan in det:
                    if kendaraan[5] == 1:
                        area.append(kendaraan[0])
                        area.append(kendaraan[2])
                        area.append(kendaraan[1])
                        area.append(kendaraan[3])
                        jumlahkend +=1
                        
                saveNB = []
                for kotak in det:
                    print(kotak)
                    center_x = (int(kotak[0])+int(kotak[2])) / 2
                    center_y = (int(kotak[1])+int(kotak[3])) / 2

                    for i in range(jumlahkend):
                        x1 = int(area[(i*4)+0])
                        y1 = int(area[(i*4)+2])
                        x2 = int(area[(i*4)+1])
                        y2 = int(area[(i*4)+3])
                        print(x1,y1,x2,y2,center_x,center_y,i)
                        if x1 < center_x < x2 and y1 < center_y < y2:
                            saveNB.append(kotak.tolist())
                            saveNB.append(i)
                            break
                
                print(len(saveNB))
                print(saveNB,"ini adalah saveNB")
                print(names)
                
                motor_indexs = [index for index in range(jumlahkend)] # [0, 1]
                motors = []
                label_indexs = []


                for motor_index in motor_indexs:
                    new_motor = []
                    new_label_index = []
                    for index, _ in enumerate(saveNB):
                        if index % 2 == 1:
                            if motor_index == saveNB[index]:
                                new_motor.append(saveNB[index-1])
                                new_label_index.append(saveNB[index-1][-1])
                    motors.append(new_motor)
                    label_indexs.append(new_label_index)
                                
            
                with open(txt_path,mode='w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(names[:1] + names[2:]) #perulangan pertama
                    for index in label_indexs:
                        row_text = "{}{}{}{}{}{}{}".format(
                            index.count(0.0),
                            index.count(2.0),
                            index.count(3.0),
                            index.count(4.0),
                            index.count(5.0),
                            index.count(6.0),
                            index.count(7.0),
                        )
                        
                        writer.writerow(row_text)
                # for c in det[:, -1].unique():
                #     z.append(names[int(c)])
                #     x = [name for name in names if name not in z]
                #     n = (det[:, -1] == c).sum()  # detections per class
                #     s += f"{n} {names[int(c)]}, "
                # for v in x:
                #     s += f"{0} {v}, "
                # for i2 in range(jumlahkend):
                #     saveNB1 = []
                #     for i1 in range(len(saveNB)):
                #         if saveNB[i1] == i2 and int(saveNB[i1-1][5]) != 1:
                #             saveNB1.append(saveNB[i1-1])
                #     saveNB1 = np.array(saveNB1)
                #     print(saveNB1)
                #     print(np.unique(saveNB1[:, -1]))
                #     print(f"{det[:, -1].unique()}")
                #     for c1 in np.unique(saveNB1[:, -1]):
                #         z1.append(names[int(c1)])
                #         v1 = [name for name in names if name not in z1]
                #         n1 = (saveNB1[:, -1] == c1).sum()
                #         k.append(names[int(c1)])
                #         l.append(f"{n1}")
                #     for v in v1:
                #         k.append(v)
                #         l.append("0")
                #     # l.append(\n)
                #     with open(txt_path + str(jumlahkend) + (".csv") ,mode='w', newline='') as f:
                #         writer = csv.writer(f)
                #         writer.writerow(k) #perulangan pertama
                #         writer.writerow(l)
                #     print("x")
                NBsave = "C:\TA\yolov7\pipeline_filenameTrain2.pkl"
                loaded_pipeline = joblib.load(NBsave)
                readNB = pd.read_csv(txt_path)
                predictions = loaded_pipeline.predict(readNB)
                print(predictions)
                for warnapredictions in range(jumlahkend):
                    cek_helm=label_indexs[warnapredictions].count(0.0)+label_indexs[warnapredictions].count(6.0)
                    if(cek_helm > 2):
                        cv2.rectangle(im0,(int(area[(warnapredictions*4)+0]),int(area[(warnapredictions*4)+2])),(int(area[(warnapredictions*4)+1]),int(area[(warnapredictions*4)+3])),(255,0,0),2)
                    elif int(predictions[warnapredictions-1]) == 1 :
                        cv2.rectangle(im0,(int(area[(warnapredictions*4)+0]),int(area[(warnapredictions*4)+2])),(int(area[(warnapredictions*4)+1]),int(area[(warnapredictions*4)+3])),(0,255,0),2)
                    else :
                        cv2.rectangle(im0,(int(area[(warnapredictions*4)+0]),int(area[(warnapredictions*4)+2])),(int(area[(warnapredictions*4)+1]),int(area[(warnapredictions*4)+3])),(0,0,255),2)
                
                for *xyxy, conf, cls in reversed(det):
                    if save_txt:  # Write to file
                        s
                        

                    if save_img or view_img:  # Add bbox to image
                        if cls != 1:
                            label = f'{names[int(cls)]} {conf:.2f}'
                            plot_one_box(xyxy, im0, label=label, color=colors[int(cls)], line_thickness=1)

            # Print time (inference + NMS)
            print(f'{s}Done. ({(1E3 * (t2 - t1)):.1f}ms) Inference, ({(1E3 * (t3 - t2)):.1f}ms) NMS')

            # Stream results
            if view_img:
                cv2.imshow(str(p), im0)
                cv2.waitKey(1)  # 1 millisecond

            # Save results (image with detections)
            if save_img:
                if dataset.mode == 'image':
                    cv2.imwrite(save_path, im0)
                    print(f" The image with the result is saved in: {save_path}")
                else:  # 'video' or 'stream'
                    if vid_path != save_path:  # new video
                        vid_path = save_path
                        if isinstance(vid_writer, cv2.VideoWriter):
                            vid_writer.release()  # release previous video writer
                        if vid_cap:  # video
                            fps = vid_cap.get(cv2.CAP_PROP_FPS)
                            w = int(vid_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                            h = int(vid_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                        else:  # stream
                            fps, w, h = 30, im0.shape[1], im0.shape[0]
                            save_path += '.mp4'
                        vid_writer = cv2.VideoWriter(save_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (w, h))
                    vid_writer.write(im0)

    if save_txt or save_img:
        s = f"\n{len(list(save_dir.glob('labels/*.txt')))} labels saved to {save_dir / 'labels'}" if save_txt else ''
        #print(f"Results saved to {save_dir}{s}")

    print(f'Done. ({time.time() - t0:.3f}s)')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--weights', nargs='+', type=str, default='yolov7.pt', help='model.pt path(s)')
    parser.add_argument('--source', type=str, default='inference/images', help='source')
    parser.add_argument('--img-size', type=int, default=640, help='inference size (pixels)')
    parser.add_argument('--conf-thres', type=float, default=0.25, help='object confidence threshold')
    parser.add_argument('--iou-thres', type=float, default=0.45, help='IOU threshold for NMS')
    parser.add_argument('--device', default='', help='cuda device, i.e. 0 or 0,1,2,3 or cpu')
    parser.add_argument('--view-img', action='store_true', help='display results')
    parser.add_argument('--save-txt', action='store_true', help='save results to *.txt')
    parser.add_argument('--save-conf', action='store_true', help='save confidences in --save-txt labels')
    parser.add_argument('--nosave', action='store_true', help='do not save images/videos')
    parser.add_argument('--classes', nargs='+', type=int, help='filter by class: --class 0, or --class 0 2 3')
    parser.add_argument('--agnostic-nms', action='store_true', help='class-agnostic NMS')
    parser.add_argument('--augment', action='store_true', help='augmented inference')
    parser.add_argument('--update', action='store_true', help='update all models')
    parser.add_argument('--project', default='runs/detect', help='save results to project/name')
    parser.add_argument('--name', default='exp', help='save results to project/name')
    parser.add_argument('--exist-ok', action='store_true', help='existing project/name ok, do not increment')
    parser.add_argument('--no-trace', action='store_true', help='don`t trace model')
    opt = parser.parse_args()
    print(opt)
    #check_requirements(exclude=('pycocotools', 'thop'))

    with torch.no_grad():
        if opt.update:  # update all models (to fix SourceChangeWarning)
            for opt.weights in ['yolov7.pt']:
                detect()
                strip_optimizer(opt.weights)
        else:
            detect()
