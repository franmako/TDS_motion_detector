class Personne:

    def __init__(self, pId,pX,pY):
        super( self).__init__()
        self.personId = pId
        self.posX = pX
        self.posY = pY

    def getId(self):
        return self.personId

    def getPos(self):
        return (self.posX,self.posY)

    def updateCoord(self,x,y):
        self.posX = x
        self.posY = y
