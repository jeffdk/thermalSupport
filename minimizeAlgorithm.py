#!/usr/bin/python


from numpy import *
from numpy import testing as npt

class basis(object):
    dim=0
    basis=empty((0))
    def __init__(self,vectors):
        assert vectors.dtype == array([0.0]).dtype, "Input must be of type floats!!"

        assert vectors.any(), "Array of input vectors to basis must not be empty!"
        assert vectors.ndim==2, "Array of input vectors to basis must have 2 axes (indexes)"
        assert all([vector.size==vectors[0].size for vector in vectors]), \
               "Array of input vectors must each have the same size"
        assert linalg.det(vectors),  "Your basis vectors are linearly dependent"

        self.dim = vectors[0].size
        print "dim",self.dim

        self.basis = vectors
        print "ORTHOGONA?: ",self.isOrthogonal()

        print "Xx_gsmitt in da house_xX"
        print self.stableGramSchmidt()
        print "ORTHOGONA? NOW BITCH?: ",self.isOrthogonal()
        print dot(self.basis[0],self.basis[1])
    def isOrthogonal(self):

        dotSum=0.
        for i in range(self.dim):
            for j in range(i+1,self.dim):
                dotSum+=dot(self.basis[i],self.basis[j])

        try:
            npt.assert_almost_equal(dotSum,0.0,14)
        except AssertionError as error:
            print error
            return False
        else:
            return True

    def stableGramSchmidt(self):

        for i in range(self.dim):
            self.basis[i]=self.basis[i]/norm(self.basis[i])
            for j in range(i+1,self.dim):
                self.basis[j]=self.basis[j] - dot(self.basis[i],self.basis[j])/norm(self.basis[i])*self.basis[i]
        return self.basis

def norm(vect):
    return sqrt(reduce(lambda x, y: x+y,vect*vect))

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
            #print self.offset[d]
            thisDimList +=  ones(self.size[d])*self.offset[d]
            singleDimIndexList.append( thisDimList )

        #print singleDimIndexList
        self.indices = multigrid(singleDimIndexList)
        #print self.indices


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
