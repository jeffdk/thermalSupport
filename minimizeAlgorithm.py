#!/usr/bin/python
from copy import deepcopy
import itertools
import sqlite3

from numpy import *
from numpy import testing as npt
from modelGeneration import modelGenerator
from sqlUtils import queryDBGivenParams

class basis(object):
    dim=0
    basis=empty((0))
    axesNames=['T','a','edMax','rpoe']
    def __init__(self,vectors):
        assert vectors.dtype == array([0.0]).dtype, "Input must be of type floats!!"

        assert vectors.any(), "Array of input vectors to basis must not be empty!"
        assert vectors.ndim==2, "Array of input vectors to basis must have 2 axes (indexes)"
        assert all([vector.size==vectors[0].size for vector in vectors]), \
               "Array of input vectors must each have the same size"
        assert linalg.det(vectors),  "Your basis vectors are linearly dependent"

        self.dim = vectors[0].size
#        print "dim",self.dim

        self.basis = vectors
 #       print "ORTHOGONA?: ",self.isOrthogonal()

#        print "Xx_gsmitt in da house_xX"
        self.basis=stableGramSchmidt(self.basis)
#        print self.basis
#        print "ORTHOGONA? NOW BITCH?: ",self.isOrthogonal()

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

def stableGramSchmidt(inVectors):
    assert inVectors.dtype == array([0.0]).dtype, "Input must be of type floats!!"
    assert inVectors.ndim==2, "Array of input vectors to basis must have 2 axes (indexes)"

    vectors=inVectors.copy()
    dim = len(vectors)
    for i in range(dim):
        assert norm(vectors[i]), "One of your basis vectors has become zero! Retry with a linearly independent set!"
        vectors[i]=vectors[i]/norm(vectors[i])
        for j in range(i+1,dim):
            vectors[j]=vectors[j] - project(vectors[j],vectors[i])
    return vectors

def norm(vect):
    return sqrt(reduce(lambda x, y: x+y,vect*vect))

def project(vector,ontoVector):
    return dot(vector,ontoVector)/norm(ontoVector)*ontoVector

def removeSubspace(inputBasis, inVectorsToRemove):
    assert inVectorsToRemove.dtype == array([0.0]).dtype, "Input must be of type floats!!"
    assert len(inVectorsToRemove) < inputBasis.dim, "Can't remove more vectors than there are basis vectors!"
    vectorsToRemove=stableGramSchmidt(inVectorsToRemove)

    #It's possible that we may select the 'wrong' set of basis vectors such that replacing
    # them with the vectorsToRemoves results in a linearly dependent set.
    # in this case Gram-Schmidt will fail.
    # This can be caused by the vectorsToRemove being linearly dependent, or
    # by vectorsToRemove being linearly dependent with a basis vector not removed

    #Thus, we try every replacing every combination of basis vectors before giving up
    allCombosSingular = True
    replaceTry=()
    for replaceTry in itertools.combinations(range(inputBasis.dim), len(vectorsToRemove)):
        testBasis = deepcopy(inputBasis)

        #replace the designated vectors with the vectors to remove
        for vectorIndex,basisIndex in enumerate(replaceTry):
            testBasis.basis[basisIndex]=vectorsToRemove[vectorIndex]
        #check testBasis is not singular
        if linalg.det(testBasis.basis)==0.0:
            #print "Your new basis is not linearly independent... trying next combination"
            pass
        else:
            #if it's not singular, we're done!
            allCombosSingular = False
            break
    assert not allCombosSingular, "Wow, all replacement combinations of the orig basis result in linear \"" \
                                  "dependence.  Perhaps your input vectors are linearly dependent?"

    #now that we know which of the basis vectors we can replace, we want to put those first,
    #  replace them with our orthogonal vectorsToRemove, call gram schmidt, then remove them.
    #  this ensures the remaining vectors are orthogonal to the subspace we want to remove

    goodBasisVectors=range(inputBasis.dim)
    for i in replaceTry:
        goodBasisVectors.remove(i)


    newSet=[]
    for vec in vectorsToRemove:
        newSet.append(vec)
    for i in goodBasisVectors:
        newSet.append(inputBasis.basis[i])


    newBasis=basis( array(newSet) )

    newBasis.basis=stableGramSchmidt(newBasis.basis)

    reducedSpace = []
    for i in range(len(vectorsToRemove),inputBasis.dim):
        reducedSpace.append(newBasis.basis[i])

    reducedSpace = zeroRoundOffValues( array(reducedSpace), 1e-15)

    return reducedSpace

def zeroRoundOffValues(inArray,eps):
    assert inArray.dtype == array([0.0]).dtype, "Input must be of type floats!!"
    theShape=inArray.shape
    temp = list(inArray.flat)
    for i, val in enumerate(temp):
        if abs(val) < eps:
            temp[i] = 0.0
    inArray= array(temp).reshape(theShape)
    return inArray
roundArray=frompyfunc(round,2,1)

def steepestDescent(funcName,fixedNames,inBasis,firstDeriv,p0,deltas,sqliteConnection,modelGen,stationaryParamsDict):
    assert isinstance(funcName,str)
    assert isinstance(fixedNames,list)
    assert isinstance(fixedNames[0], str)
    assert isinstance(inBasis,basis)
    assert isinstance(firstDeriv, deriv)
    assert isinstance(deltas, tuple)
    assert inBasis.dim == len(deltas), "Dimension of your deltas must be same as input basis!"
    assert isinstance(sqliteConnection,sqlite3.Connection)
    assert isinstance(modelGen,modelGenerator)
    assert isinstance(p0,tuple)
    assert inBasis.dim == len(p0), "Dimension of your starting point must be same as input basis!"
    assert isinstance(stationaryParamsDict,dict)

    dim = inBasis.dim

    stencil = firstDeriv.stencil.indices[0]
    continueStepping = True
    maxSteps = 50
    step = 0
    currentBasis=deepcopy(inBasis)
    currentPoint = p0
    pointList=[p0]
    funcNamesList={funcName:[]}
    funcNamesList.update({key:[] for key in fixedNames})
    while continueStepping:
        step +=1
        if step > maxSteps:
            print "Maximum steps reached in steepestDescent"
            continueStepping = False
            break
        paramsDict = stationaryParamsDict.copy()

        paramsToRun=[]
        paramsNeededForIthBasisVector = []
        for i in range(dim):
            ithPointsDesired = array(currentPoint) +[index*currentBasis.basis[i]*deltas for index in stencil]
            ithPointsDesired = roundArray(ithPointsDesired,10)
            ithParamsNeeded = []
            for j in ithPointsDesired:
                dictUpdate = {currentBasis.axesNames[k] : j[k]  for k in range(dim)}
                paramsDict.update(dictUpdate)
                ithParamsNeeded.append(paramsDict.copy ())
                if paramsDict in paramsToRun:
                    print "ARRR MATEY, ALREAYD GOT THAT ONE"
                    print paramsDict
                else:
                    paramsToRun.append(paramsDict.copy())
            paramsNeededForIthBasisVector.append(ithParamsNeeded)
        modelGen.generateModels(modelGen.runRotNS, paramsToRun,sqliteConnection)

        gradientDict={funcName : [] }
        gradientDict.update({ key:[] for key in fixedNames})

        funcsDesired = [funcName] + fixedNames
        sqliteConnection.commit()
        sqliteCursor=sqliteConnection.cursor()
        for i in range(dim):
            for j in paramsNeededForIthBasisVector[i]:
                funcs = queryDBGivenParams(funcsDesired,j,sqliteCursor,tableName="models")
                assert len(funcs), "QUERY RETURNED NO ENTRIES, MATCHING PARAMS: %s" % str(j)
                if len(funcs) > 1:
                    print "WWWARNING, MORE THAN ONE MODEL WITH PARAMS: ", j
                    print "results of models with those params in %s form: " %funcsDesired, funcs
                    last = funcs[0]
                    for k in range(len(funcs)):
                        if not last==funcs[k]:
                            print "OH WOW AND THEY HAVE DIFFERENT RESULTS... REALLY SHOULD ABORT"
                        last = funcs[k]

                newEntries = dict([ (funcsDesired[key],newVal)
                                     for key,newVal
                                       in enumerate(
                                        queryDBGivenParams(funcsDesired,j,sqliteCursor,tableName="models")[0]
                                       )
                                   ])
                j.update(newEntries)
            #print paramsNeededForIthBasisVector[i]

            #following yields the step for the derivative
            stepInIthDir = dot(currentBasis.basis[i],deltas)
            #here we save the function values and calculate their derivative
            #the function value at the point we are evaluating has stencil index0
            for func in funcsDesired:
                funcVals = [ paramsDict[func] for paramsDict in paramsNeededForIthBasisVector[i]]
                k = len(firstDeriv.coeffs)/2  #default assume centered list
                for k,stencilIndex in enumerate(*firstDeriv.stencil.indices):
                    if stencilIndex == 0:
                        break
                if i  == 0:  #only do this once
                    funcNamesList[func].append(funcVals[k])
                #print funcVals
                gradientDict[func].append( dot(firstDeriv.coeffs, funcVals)/stepInIthDir  )
        #print gradientDict
        
        badSubspace =  array([gradientDict[fixedName] for fixedName in fixedNames])
        fixedSubspace=removeSubspace(currentBasis, badSubspace )
        #print fixedSubspace
        projectedGradFunc=zeros(dim)
        for projection in [project(gradientDict[funcName],vec) for vec in fixedSubspace ]:
            projectedGradFunc += projection
        projectedGradFunc = projectedGradFunc/norm(projectedGradFunc)
        #print projectedGradFunc

        newBasisVectors=[]
        for i in badSubspace:
            newBasisVectors.append(i)
        for i in fixedSubspace:
            newBasisVectors.append(i)

        #currentBasis = basis(array(newBasisVectors))

        print currentBasis.basis, currentBasis.isOrthogonal()

        currentPoint += -projectedGradFunc * deltas
        pointList.append(deepcopy(currentPoint))
        print "-----------NEW POINT---------------"
        print currentPoint
        print
        print "   CURRENT POINT LIST         "
        print array(pointList)
        print "----------DONE THIS STEP-----------"
        print

    
    print "-----------------FINAL POINT LIST ---------------"
    print 
    print array(pointList)
    print funcNamesList
    print 
    print "-------------------------------------------------"
    return array(pointList)


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
