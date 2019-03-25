
import cv2
import numpy as np
import serial
import queue
from statistics import mean
import re # for float extraction from serial output
import time

LOWTAR = 14
HIGHTAR = 1000

SHOW = False
QUEUELEN = 20
BTNTHRES = int(LOWTAR*(QUEUELEN*0.5))
SERIALLOC = 1410
VIDLENGTH = 20

vidSavePath = 'tstVid/'

def qMean(qq):
    """ get mode of btn val queue rtn True if above threshold """
    # get mode and return true if more zeros(btn press signals) than threshold
    s, numVals = 0, 0
    for f in list(qq.queue):
        print("This is the val: ", f)
        s+=f
        numVals+=1
    print("s/NumVals: {}, this is BTTHRESH: {}".format((s/numVals), BTNTHRES))

    if ((s/numVals)<BTNTHRES) and numVals==QUEUELEN:
        return True
    else:
        return False

def btnPush(s, q):
    """ check if button is pressed for significant amount of time, if so rtn True """
    # t1 = time.time()
    # t2 = time.time()
    # print("time taken: {}".format(round(t2-t1, 2)))

    print("NORM s: ", s)

    # find float val in arduino btn return
    ans = re.findall(r'-?\d+\.?\d*', str(s))

    # add 0 val to list if none returned
    if len(ans)==0:
        ans.append(0)

    # take average of btn vals to ensure no false positives
    if len(ans)<2:
        # FIFO remove val to make room for new val if queue full
        if q.qsize()==QUEUELEN:
            q.get()

        # add in new val
        q.put(float(ans.pop()))

        res = qMean(q)


        print("The mode func returns: ", res)
        return res

    else:
        # make sure only one vals in serial return
        print("Error: more than one button values returned. Exiting..")
        exit()


que = queue.Queue(maxsize=QUEUELEN)

m = 0 # mean of of past x btn vals
cnt = 0 # fps counter
vidCnt = 0 # vid counter


while True:

    # Setup Serial port on first go around
    if cnt==0:
        ser = serial.Serial('/dev/tty.usbserial-'+str(SERIALLOC), 19200)

    serOut = ser.readline()

    if btnPush(serOut, que):
        print("Starting to collect video")
        time.sleep(1)

        cap = cv2.VideoCapture(0)
        frame_width = int(cap.get(3))
        frame_height = int(cap.get(4))

        out = cv2.VideoWriter((vidSavePath +'output'+str(vidCnt)+'.avi'), cv2.VideoWriter_fourcc('M','J','P','G'), 10, (frame_width, frame_height))
        vidCnt+=1


        ts = time.time()

        # if button pushed then continue collecting frames otherwise stop
        while True:
            ret, frame = cap.read(1)

            if ret == True:
                if SHOW:
                    cv2.imshow("frame", frame)

                out.write(frame)
                tc = time.time()

                print("This is tc: {}, ts: {}, Diff: {}, VIDLENGTH: {}".format(tc, ts, (tc-ts), VIDLENGTH))
                cv2.waitKey(20)
                if (tc-ts)>VIDLENGTH:
                    print("breaking...")
                    break


        print("\n\n\n releasing...")
        out.release()
        cap.release()
        cv2.destroyAllWindows()


        # Clear queue
        with que.mutex:
            que.queue.clear()

        # reset serial port to avoid buffer conflicts with camera
        ser = serial.Serial('/dev/tty.usbserial-'+str(SERIALLOC), 19200)

    cnt+=1









