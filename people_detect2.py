#!/usr/bin/env python

import sys
import collections
import argparse
import numpy
import imutils
import cv2

## --------------------------------------------------------------------------- #
# Program initialization
## --------------------------------------------------------------------------- #
parser = argparse.ArgumentParser()

parser.add_argument( "-v", "--video", help = "Path to video file" )
parser.add_argument( "-a", "--min-area", type = int, default = 2000, help = "Minimum area size" )

args = vars( parser.parse_args() )
video = args["video"]
detectionThreshold = args["min_area"]

try:
    if video is None :
        input = cv2.VideoCapture(0)
    else:
        input = cv2.VideoCapture(video)

except cv2.error as e:

    print "\nInvalid input detected. Exiting."
    sys.exit(1)
# ---------------------------------------------------------------------------- #

## --------------------------------------------------------------------------- #
# Program main function
## --------------------------------------------------------------------------- #
on = True
frameSize = 500

empty_room = None
cptPeople = 0

memory = 15
persistence = collections.deque(memory*[0], memory)

while on:

    # Loop iteration initialization ------------------------------------------ #
    (grabbed, frame) = input.read()

    # Frame optimizations.
    frame = imutils.resize( frame, width = 500 )
    room = cv2.cvtColor( frame, cv2.COLOR_BGR2GRAY )
    room = cv2.GaussianBlur( room, (21, 21), 0 )

    # If the empty room variable is empty, we're standing at the first video
    # frame and we assign the room frame variable to the empty room variable.
    if empty_room is None:
        empty_room = room
        continue
    # ------------------------------------------------------------------------ #


    # Observes the differences between the empty room and the room as it is now.
    frameDelta = cv2.absdiff( empty_room, room )
    thresh = cv2.threshold( frameDelta, 25, 255, cv2.THRESH_BINARY )[1]
    thresh = cv2.dilate( thresh, numpy.array([[0, 1, 0], [0, 1, 0], [0, 1, 0]], numpy.uint8), iterations = 20 ) # Image dilatation (~= hole filling).

    # Objects analysis ------------------------------------------------------- #
    (objects, _) = cv2.findContours( thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE )
    if len(objects) != cptPeople:

        cache = 0
        x = y = w = h = 0
        edge = False

        for o in objects:

            # If the object is too small, we dismiss its study
            if cv2.contourArea( o ) < detectionThreshold:
                continue

            (x, y, w, h) = cv2.boundingRect( o )
            cv2.rectangle( frame, (x, y), (x + w, y + h), (0, 255, 0), 2 )

            # If the shift appeared within the center of the picture,
            # it's a false positive
            if x < 20 or x + w > 480:
                print "edge"
                edge = True

            cache += 1

        # If after analysing the objects, we still have a different counter,
        # we modify the people counter.
        persistence.appendleft(cache)
        if persistence.count(cache) >= memory*0.8: # Maybe we could include some ratio here
            cptPeople = cache

        if edge == True and cache < cptPeople:
            cptPeople = cache

    # ------------------------------------------------------------------------ #

    cv2.putText(frame, "Personnes dans la salle d'attente: {}".format(cptPeople), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    cv2.imshow("Salle d'attente - Camera", frame)
    cv2.imshow("Salle d'attente - Thresh", thresh)

    key = cv2.waitKey(1) & 0xFF
    on = not ( key == ord("q") )
# ---------------------------------------------------------------------------- #

input.release()
cv2.destroyAllWindows()

sys.exit(0)
