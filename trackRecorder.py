#
# For recording tracks
#
import ast
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

class trackRecorder(object):
    dbFile=None
    trackTableName=None
    dbConnection=None
    pointNumber=0
    doRecording=True
    independentVars=None
    trackMetaTable = None #TODO: IMPLEMENT THIS

    def __init__(self,trackTableName,dbConnection,independentVars):
        assert isinstance(trackTableName,str)
        assert isinstance(dbConnection, sqlite3.Connection)
        assert isinstance(independentVars,tuple)
        assert isinstance(independentVars[0],str)
        print "Initializing track recorder."
        self.trackTableName=trackTableName
        self.dbConnection=dbConnection
        self.independentVars=independentVars

        #Check if table already exists
        curs = self.dbConnection.cursor()
        curs.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='%s'" % trackTableName)
        result=curs.fetchall()

        if not result:
            print "Track table '%s' not found in db; creating now" % trackTableName
            curs.execute("CREATE TABLE %s  %s" %(trackTableName,columnsString) )
        else:
            print "Track table already exists, turning off recording!"
            #self.doRecording = False

        self.dbConnection.commit()
        return


    def record(self,point,gradientDict,projectedGradFunc,normAfterProjection, modelsTable):
        if not self.doRecording:
            return 1

        assert len(point) == len(self.independentVars), "Point length doesnt match # independent vars!"
        roundArray=frompyfunc(round,2,1)
        point = tuple(roundArray(point,10))

        pointAsStr= str(point).replace(" ","")

        gradDictAsStr =str(gradientDict).replace(" ","")

        projGradFuncAsStr=str(tuple(projectedGradFunc)).replace(" ","")


        queryDict = {self.independentVars[i]:point[i] for i in range(len(point))}

        cursor=self.dbConnection.cursor()

        print "Fetching point entry data from database '%s'  for recording" % modelsTable
        entryData = list(queryDBGivenParams("*",queryDict,cursor,modelsTable)[0])

        #Stupid table strings are recorded in type unicode and mess up upon re-insertion...
        for i,ent in enumerate(entryData):
            if isinstance(ent,unicode):
                entryData[i]=str(ent)


        entry = [self.pointNumber, pointAsStr,gradDictAsStr,projGradFuncAsStr,normAfterProjection]
        entry = entry + entryData
        #print str(tuple(entry))

        existingPoint = queryDBGivenParams("pointNum",{'pointNum':self.pointNumber},
            cursor,self.trackTableName)
        if  existingPoint :
            print "POINT NUM %s EXISTS IN RECORD TABLE %s" % (existingPoint[0],self.trackTableName)
        else:
            print "Inserting new point into record table '%s'" % self.trackTableName
            cursor.execute("INSERT INTO "+self.trackTableName+" VALUES "+ str(tuple(entry)) )

        self.pointNumber+=1
        print
        self.dbConnection.commit()
        return

class trackPlotter(object):
    dbFilenames=[]
    trackTableName="track"
    independentVars=()
    trackData=[]

    def __init__(self,dbFilenames,trackTableName,independentVars):

        self.dbFilenames=dbFilenames
        self.trackTableName=trackTableName
        self.independentVars=independentVars

        thisFilesData={}
        for file in self.dbFilenames:
            connection=sqlite3.connect(file)
            c=connection.cursor()
            rawData=queryDBGivenParams(["pointNum","point","gradDict","projGrad","normProj"],
                                       {},c,self.trackTableName,(), " ORDER BY pointNum" )
            pointList=[]
            gradDictList=[]
            projGradList=[]
            normProjList=[]
            for entry in rawData:
                point = ast.literal_eval( entry[1] )
                gradDict = ast.literal_eval( entry[2])
                projGrad = ast.literal_eval( entry[3])
                normProj = entry[4]
                pointList.append(point)
            thisFilesData.update({'points':pointList})
        self.trackData.append(thisFilesData)


    if not MAYAVI_OFF:
        def trackPlotter(self,independentVars):
            #somehow figure out what indices to plot
            plotIndices=(1,2,3)

            for track in self.trackData:
                pointPlot=zip(*track['points'])

                print pointPlot
                print pointPlot[plotIndices[0]]
                print pointPlot[plotIndices[1]]
                print  pointPlot[plotIndices[2]]
                mlab.plot3d(pointPlot[plotIndices[0]], pointPlot[plotIndices[1]],pointPlot[plotIndices[2]], color=(1,1,1) )
            mlab.show()