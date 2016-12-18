import collections
import cv2

class ObjectInMotion:

    humanTresh = 8000
    humanRatio = 0.6
    shiftStep = 5

    """
    Class constructor.
    """
    def __init__( self, x, y, width, height, direction = None, yesterday = None ):
        self.setDimensions( x, y, width, height )
        self.direction = direction
        self.yesterday = yesterday

    """
    Simply sets the dimensions.
    """
    def setDimensions( x, y, width, height ):
        self.x = x
        self.y = y
        self.width = w
        self.height = h

    """
    Returns wheter this object is human or not.
    """
    def isHuman():
        humanity = false;
        if ( self.w * self.h > humanThresh ) and ( self.x / self.y < humanRatio ):
            return True

        return False

    """
    Attemps to update this object with the given cv2 object.

    @param cv2 object
    @return boolean Wheter the update was successfull
    """
    def updateWith(object):
        ( x, y, w, h ) = cv2.boundingRect( o )

        if ( self.x - x <= self.shiftStep ) and ( self.y - y <= self.shiftStep ):
            if self.x > self.yesterday.x:
                self.direction = "left"
            else
                self.direction = "right"

            self.yesterday = copy(self)
            self.setDimensions( x, y, w, h )

            return True

        return False
