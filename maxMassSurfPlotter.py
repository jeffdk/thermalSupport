

import sqlite3
from numpy import *
from sqlUtils import queryDBGivenParams
MAYAVI_OFF=False
if not MAYAVI_OFF:
    import mayavi.mlab as mlab


columnsString=''' (pointNum int, point text, gradDict text, projGrad text, normProj real,
              eos text, rollMid real, rollScale real, a real, T real,
              omega_c real,  J real, gravMass real, edMax real, baryMass real,
              ToverW real, arealR real, VoverC real, omg_c_over_Omg_c real,
              rpoe real,  Z_p real, Z_b real, Z_f real,  h_direct real,
              h_retro real, e_over_m real, shed real,
              RedMax real, propRe real, runType int, runID text, lineNum int) '''
#  Omega_c    cJ/GMs^2    M/Ms       Eps_c      Mo/Ms      T/W        R_c        v/c     omg_c/Omg_c     rp       Z_p        Z_b        Z_f      h-direct   h-retro     e/m  Shed RedMax

#ASSUMES TABLE NAME IS MODELS

class surfacePlotter(object):


    dbFile=None
    independentVars=()
    dependentVar=None
    colorVar=None
    dbConnection=None

    def __init__(self, dbFile, independentVars,dependentVar,colorVar=None ):

        assert isinstance(dbFile,str)
        assert len(independentVars) == 2, "Surface plot has two independent variables"
        assert isinstance(dependentVar,str)

        self.independentVars=independentVars
        self.dependentVar=dependentVar
        self.colorVar=colorVar

        self.dbConnection = sqlite3.connect(dbFile)

    def plotWithCondition(self, condition):
        assert isinstance(condition,str), "must enter a condition!"

        cursor=self.dbConnection.cursor()

        xname = self.independentVars[0]
        yname = self.independentVars[1]
        xs=[]

        for i in cursor.execute("SELECT DISTINCT " + xname + " FROM models ORDER BY "
                                + xname):
            val = i[0]
            if xname == "edMax":
                val = val#/1.0e15
            xs.append(val)
        ys=[]
        for i in cursor.execute("SELECT DISTINCT " + yname + " FROM models ORDER BY "
                                + yname):
            val = i[0]
            if yname == "edMax":
                val = val#/1.0e15
            ys.append(val)
        #print xs
        #print ys

        #####
        #
        xs, ys =  meshgrid(xs,ys)
        # reverse order since mlab uses mgrid format which returns transpose of matrices in meshgrid style
        xs = xs.transpose()
        ys = ys.transpose()
        #
        #####

        def lookup(x,y):
            assert x >= 0.,  "Lookup only well defined for x >=0"
            assert y >= 0.,  "Lookup only well defined for y >=0"
            tolerance = 1.0001
            additionalConditions=[]
            if not x == 0:
                additionalConditions.append( xname + ">" + str(x/tolerance) )
                additionalConditions.append( xname + "<" + str(x*tolerance) )
            else:
                additionalConditions.append(xname + "=" + str(x))
            if not y == 0:
                additionalConditions.append(yname + ">" + str(y/tolerance))
                additionalConditions.append( yname + "<" + str(y*tolerance))
            else:
                additionalConditions.append(yname + "=" + str(y))
            additionalConditions.append(condition)
            #print additionalConditions
            value= queryDBGivenParams(self.dependentVar,
                {},
                cursor,"models", tuple( additionalConditions ))
            #print x,y, value
            if value:
                if len(value[0]) > 1 :
                    print "WARNING MORE THAN ONE VALUE FOUND!!!"
                return value[0][0]
            else:
                print "WARNING: no value"
                return 0.0

        zs = zeros(xs.shape)

        for i in range(len(xs)):
            row = xs[i]
            #print row
            for j in range(len(row)):
                #print xs[i][j], ys[i][j]
                zs[i][j] = lookup(xs[i][j], ys[i][j] )

        if xname == "edMax":
            xs = array(xs*1e-15)
        else:
            xs = array(xs)

        if yname == "edMax":
            ys=array(ys*1e-15)
        else:
            ys = array(ys)
        zs = array(zs)
        #print xs
        #print ys
        #print zs
        #print size(xs)
        #print size(ys)
        #print size(zs)
        fig=mlab.figure(bgcolor=(.5,.5,.5))
        extents=[xs.min(),xs.max(),
                 ys.min(),ys.max(),
                 zs.min(),zs.max()]

        mlab.surf(xs,ys,zs, colormap="bone",representation='wireframe',
            extent=extents
        )

        mlab.axes(extent=extents,nb_labels=6)
        mlab.outline(extent=extents)
        mlab.xlabel(xname)
        mlab.ylabel(yname)
        mlab.zlabel(self.dependentVar)
        #mlab.show()

