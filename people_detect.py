import numpy as np
import cv2
import argparse
import Person

ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", help="path to the video file")
ap.add_argument("-a", "--min-area", type=int, default=1600, help="minimum area size")
args = vars(ap.parse_args())

if args.get("video", None) is None:
	cap = cv2.VideoCapture(0)
	time.sleep(0.25)
else:
	cap = cv2.VideoCapture(args["video"])

fgbg = cv2.BackgroundSubtractorMOG() #Create the background substractor

kernelOp = np.ones((3,3),np.uint8)
kernelCl = np.ones((11,11),np.uint8)

#Variables
font = cv2.FONT_HERSHEY_SIMPLEX
persons = []
max_p_age = 5
pid = 1
people = 0

while(cap.isOpened()):
    #people = 0
    ret, frame = cap.read() #read a frame
    fgmask = fgbg.apply(frame) #Use the substractor

    try:
        ret,imBin= cv2.threshold(fgmask,200,255,cv2.THRESH_BINARY)#Opening (erode->dilate) para quitar ruido.
        mask = cv2.morphologyEx(imBin, cv2.MORPH_OPEN, kernelOp)#Closing (dilate -> erode) para juntar regiones blancas.
        mask = cv2.morphologyEx(mask , cv2.MORPH_CLOSE, kernelCl)
    except:
        #if there are no more frames to show...
        print('EOF')
        break

    #_, contours0, hierarchy = cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    (cnts, _) = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    for cnt in cnts:
        cv2.drawContours(frame, cnt, -1, (0,255,0), 3, 8)
        area = cv2.contourArea(cnt)
        if area > args["min_area"]:
            #people = people + 1
            M = cv2.moments(cnt)
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])
            x,y,w,h = cv2.boundingRect(cnt)

            new = True

            for i in persons:
                if abs(x-i.getX()) <= w and abs(y-i.getY()) <= h:
                    new = False
                    i.updateCoords(cx,cy)
                    break

                if new == True:
                    p = Person.MyPerson(pid,cx,cy, max_p_age)
                    persons.append(p)
                    people = people + 1
                    pid += 1
                    cv2.circle(frame,(cx,cy), 5, (0,0,255), -1)
                    img = cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
                    cv2.drawContours(frame, cnt, -1, (0,255,0), 3)

            for i in persons:
                if len(i.getTracks()) >= 2:
                    pts = np.array(i.getTracks(), np.int32)
                    pts = pts.reshape((-1,1,2))
                    frame = cv2.polylines(frame,[pts],False,i.getRGB())

                if i.getId() == 9:
                    print str(i.getX()), ',', str(i.getY())

                cv2.putText(frame, str(i.getId()),(i.getX(),i.getY()),font,0.3,i.getRGB(),1,cv2.CV_AA)

    cv2.putText(frame, "Personnes dans la salle d'attente: {}".format(people), (10, 20),
        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    cv2.imshow("Camera - Salle d'attente",frame)

    #Abort and exit with 'Q' or ESC
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break

cap.release() #release video file
cv2.destroyAllWindows() #close all openCV windows
