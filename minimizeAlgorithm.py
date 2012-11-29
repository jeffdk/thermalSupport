#!/usr/bin/python


from numpy import *
import math


def stepDown(func,point, delta):


    
    newPoint=point



    


    return newPoint


class deriv:
    stencil =None
    dim   =0 
    order =0
    step  =0
    coeffs=[]
    name  ="NULL"
    points =[]
    currentPoint=0

    def __str__(self):
        return self.name
    def __init__(self, dim, order, step, stencil, coeffs, name="NULL"):
        
        self.stencil = stencil
        self.coeffs  = coeffs
        self.order   = order
        self.step    = step
        self.dim     = dim
        self.coeffs  = coeffs
        self.name    = name

    def setupPoints(self, point):
        self.points =  self.stencil.get()*self.step + point
        self.currentPoint = point

    def getPoints(self):
        return self.points

    def setStep(self,newStep):
        self.step=newStep
        self.setupPoints(self.currentPoint)


class fdStencil:

    dim=0       #spatial dimensions of stencil
    size = []   #length of stencil in each dimension
    offset = [] #offset of stencil in each direction
    indices =[] #list of stencil step indicies

    def get(self):
        return self.indices
    def __init__(self,dimIn,sizeIn,offsetIn=None ):
        #default offset is just an array of zeros
        if offsetIn==None:
            offsetIn= zeros( dimIn)

        if len(sizeIn) != dimIn:
            print "Error in class stencil: "
            print "  length of stencil sizes must equal stencil dimension!"
            exit(-1)
        if len(offsetIn) != dimIn:
            print "Error in class stencil: "
            print "  length of stencil offsets must equal stencil dimension!"
            exit(-1)    
        for i in sizeIn:
            if i < 2:
                  print "Error in class stencil: "
                  print "  can't have a one point stencil in any dimension!"
                  exit(-1)    
        
        self.dim    = dimIn
        self.size   = sizeIn
        self.offset = offsetIn
        
        singleDimIndexList=[]
        for d in range(self.dim):
            thisDimList = arange(self.size[d]) - ones(self.size[d])*self.size[d]/2. + ones(self.size[d])/2. 
            print self.offset[d]
            thisDimList +=  ones(self.size[d])*self.offset[d]
            singleDimIndexList.append( thisDimList )
       
        print singleDimIndexList
        self.indices = multigrid(singleDimIndexList)
        print self.indices


#no data validation here
def multigrid( pointsAlongAxes ):
    dim = len(pointsAlongAxes)


    sizes=[]
    for d in range(dim):
        sizes.append(len( pointsAlongAxes[d] ))

    result=[]
    ## indexArray is the same size as our multigrid, but contains indicies
    indexArray = indices( sizes) 
    for d in range(dim):
        ##intialize a FLOAT version of the index array for this dimension
        resultArray=indexArray[d]*1.0  
        #print resultArray
        ##loop over grid points we want to populate along this axis
        for i in range(len(pointsAlongAxes[d])):
            #print (indexArray[d]==i), i, pointsAlongAxes[d][i]
            ##
            # following says: if our entry in the index array is the same
            #  as the index for the point along this axis, then populate
            #  the result array with the point value
            place(resultArray,indexArray[d]==i,pointsAlongAxes[d][i])
            #print resultArray
            #print "--------------------------------------"
        result.append(resultArray)

    return array(result)
