#!/usr/bin/env python

import sys
import collections
import argparse
import numpy
import imutils
import cv2
import yaml

class PeopleDetector:

    def __init__(self, config):

        try:

            self.on = True
            self.empty_room = None
            self.cptPeople = 0

            self.detectionThreshold = config['minArea']
            self.frameWidth = config['frameWidth']
            self.edgePercentage = config['edgePercentage']
            self.cacheSize = config['cacheSize']
            self.display = config['display']
            self.stream = cv2.VideoCapture(config['stream']) if 'stream' in config else cv2.VideoCapture(0)

            self.frameHeight = int(self.stream.get(4) * (self.frameWidth / self.stream.get(3)))
            self.leftEdge = (self.frameWidth / 100) * self.edgePercentage
            self.rightEdge = (self.frameWidth / 100) * (100 - self.edgePercentage)

            self.motionPersistence = collections.deque(self.cacheSize * [0], self.cacheSize)
            self.edgePersistence = collections.deque(self.cacheSize * [0], self.cacheSize)

        except cv2.error as e:

            print "Invalid input detected. Exiting"
            sys.exit(1)

        except KeyError as e:

            print 'Missing parameter in configuration file. Exiting'
            sys.exit(1)

    def optimize(self):

        self.frame = imutils.resize(self.frame, width = self.frameWidth)
        self.room = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        self.room = cv2.GaussianBlur(self.room, (21, 21), 0)

    def computeDelta(self):

        self.frameDelta = cv2.absdiff(self.empty_room, self.room)
        self.thresh = cv2.threshold(self.frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
        kernel = numpy.array([[0, 1, 0], [0, 1, 0], [0, 1, 0]], numpy.uint8)
        self.thresh = cv2.dilate(self.thresh, kernel, iterations = 15)

    def analyze(self):

        (self.objects, _) = cv2.findContours(self.thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if len(self.objects) != self.cptPeople:

            self.cache = 0

            for o in self.objects:

                if cv2.contourArea(o) < self.detectionThreshold:

                    continue

                self.filter(o)
                self.cache += 1

            self.motionPersistence.appendleft(self.cache)
            self.update()

    def filter(self, obj):

        (x, y, w, h) = cv2.boundingRect(obj)
        cv2.rectangle(self.frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        if x <  self.leftEdge or x + w < self.leftEdge or x > self.rightEdge or x + w > self.rightEdge:

            self.edgePersistence.appendleft(True)

        else:

            self.edgePersistence.appendleft(False)

    def update(self):

        if self.motionPersistence.count(self.cache) >= self.cacheSize * 0.75 and self.cache > self.cptPeople:

            self.cptPeople = self.cache

        if self.edgePersistence.count(True) >= 1 and self.cache < self.cptPeople:

            self.cptPeople = self.cache

    def render(self):

        cv2.rectangle(self.frame, (self.leftEdge, 0), (self.rightEdge, self.frameHeight), (255, 0, 0), 2)
        cv2.putText(self.frame, "Personnes dans la salle d'attente: {}".format(self.cptPeople), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        cv2.imshow("Salle d'attente - Camera", self.frame)
        cv2.imshow("Salle d'attente - Thresh", self.thresh)

    def run(self):

        while self.on:

            (self.grabbed, self.frame) = self.stream.read()

            if not self.grabbed:

                break

            self.optimize()

            if self.empty_room is None:

                self.empty_room = self.room
                continue

            self.computeDelta()
            self.analyze()
            self.render()

            key = cv2.waitKey(1) & 0xFF
            self.on = not (key == ord("q"))

        self.stream.release()
        cv2.destroyAllWindows()

        sys.exit(0)

def main():

    try:

        with open('config.yml', 'r') as yml:

            config = yaml.load(yml)

    except IOError as e:

            print("Error while opening config file : " + str(e))
            sys.exit(1)

    detector = PeopleDetector(config)
    detector.run()


if __name__ == "__main__":

    main()
