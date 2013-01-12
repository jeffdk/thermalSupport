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

metadataColumns='''(independentVars, minimizedFunc, fixedFuncs, derivName, deltas,
                    stationaryParamsDict, maxSteps, changeBasis)'''

class trackRecorder(object):
    dbFile=None
    trackTableName=None
    dbConnection=None
    pointNumber=0
    doRecording=True
    independentVars=None
    trackMetaTable = None

    def __init__(self,trackTableName,dbConnection,independentVars):
        assert isinstance(trackTableName,str)
        assert isinstance(dbConnection, sqlite3.Connection)
        assert isinstance(independentVars,tuple)
        assert isinstance(independentVars[0],str)
        print "Initializing track recorder."
        self.trackTableName=trackTableName
        self.dbConnection=dbConnection
        self.independentVars=independentVars
        self.trackMetaTable = trackTableName + "Metadata"

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

    def recordTrackMetadata(self,independentVars,funcName,fixedNames,firstDeriv,deltas,
                         stationaryParamsDict, maxSteps, changeBasis):

        curs = self.dbConnection.cursor()
        curs.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='%s'" % self.trackMetaTable)
        result=curs.fetchall()
        if not result:
            print "Track metadata table '%s' not found in db; creating now" % self.trackMetaTable
            curs.execute("CREATE TABLE %s  %s" %(self.trackMetaTable,metadataColumns) )
        else:
            print "Track metadata table already exists, returning without recording metadata!"
            return 1

        entry=[str(independentVars).replace(" ",""),
               funcName, str(fixedNames).replace(" ",""),
               firstDeriv, str(tuple(deltas)).replace(" ",""),
               str(stationaryParamsDict).replace(" ",""),
               maxSteps,str(changeBasis)]
        print entry
        print tuple(entry)
        print str(tuple(entry))
        curs.execute("INSERT INTO "+self.trackMetaTable+" VALUES "+ str(tuple(entry)) )

        self.dbConnection.commit()
        return 0

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
    trackVars=()
    trackData=[]
    trackMetaTable="trackMetadata"

    def __init__(self,dbFilenames,trackTableName,trackVars):

        assert isinstance(trackVars,tuple)
        self.dbFilenames=dbFilenames
        #TODO: what if track tablenames differ between dbNames!
        self.trackTableName=trackTableName
        self.trackMetaTable=trackTableName+"Metadata"
        self.trackVars=trackVars


        for file in self.dbFilenames:
            thisFilesData={key:[] for key in trackVars}
            connection=sqlite3.connect(file)

            metadataDict=self.readTrackMetadata(connection)
            thisFilesData.update(metadataDict)
            c=connection.cursor()
            rawData=queryDBGivenParams(["pointNum","point","gradDict","projGrad","normProj"]+list(trackVars),
                                       {},c,self.trackTableName,(), " ORDER BY pointNum" )
            pointList=[]
            gradDictList=[]
            projGradList=[]
            normProjList=[]
            for entry in rawData:
                #print entry
                point = ast.literal_eval( entry[1] )
                gradDict = ast.literal_eval( entry[2])
                projGrad = ast.literal_eval( entry[3])
                normProj = entry[4]
                gradDictList.append(gradDict)
                projGradList.append(projGrad)
                normProjList.append(normProj)
                for i,key in enumerate(trackVars):
                    thisFilesData[key].append( entry[ i + 5]) #since there are 5 variables before the trackVars

                pointList.append(point)
            thisFilesData.update({'points':pointList,'gradDicts':gradDictList,
                                  'projGrads':projGradList, 'normProjs':normProjList})
            print thisFilesData
            self.trackData.append(thisFilesData)

    def readTrackMetadata(self,dbConnection):

        c = dbConnection.cursor()
        c.execute("SELECT * FROM " +self.trackMetaTable )
        rawMetadata=c.fetchall()
        assert len(rawMetadata) < 2, "Metadata table shouldn't have multiple entries!"
        rawMetadata=list(rawMetadata[0])
        #print rawMetadata
        keys = metadataColumns.strip('()').replace(" ","").replace('\n',"").split(',')
        metadataDict={}
        for i,key in enumerate(keys):
            if isinstance(rawMetadata[i],unicode):
                rawMetadata[i]=str(rawMetadata[i])
            value = None

            try:
                value = ast.literal_eval(rawMetadata[i])
            except ValueError:
                value = rawMetadata[i]
            #Weird syntax error in ast occurs if the literal is a string that begins with a number
            except SyntaxError:
                value = ast.literal_eval("'" + rawMetadata[i] + "'")

            metadataDict[key] = value

        dbConnection.commit()
        return metadataDict

    if not MAYAVI_OFF:
        def trackPlotter(self,plotVars):


            for i,track in enumerate(self.trackData):
                pointList=zip(*track['points'])
                xs_ys_zs=[]
                #Here we search through the available data and add the correct data to plot to xs_ys_zs
                for plotVar in plotVars:
                    gotItFlag=False
                    for pointIndex,pointVar in enumerate(track['independentVars']):
                        if pointVar==plotVar:
                            print 'got ind var %s' % plotVar
                            xs_ys_zs.append(pointList[pointIndex])
                            gotItFlag=True
                            break
                    if gotItFlag:
                        continue
                    for availData in track.keys():
                        if availData == plotVar:
                            print 'got other track var %s' % plotVar
                            gotItFlag=True
                            xs_ys_zs.append(track[plotVar])
                            break
                    assert gotItFlag, "uh oh didn't find our variable to plot '%s'" % plotVar


                print  'redmax:', track['RedMax']
                print track['baryMass']
                mlab.plot3d(*xs_ys_zs,
                            color=(1-(1./(i%3+1)),1,1./(i%2+1.)),
                            reset_zoom=False,
                            tube_radius=None)
            mlab.show()