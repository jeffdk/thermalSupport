#!/usr/bin/python

import os
import sys
sys.path.append('../')
sys.path.append('/home/jeff/work/thermalSupport/evolveDownToverW')
import sqlite3
from numpy import *
from matplotlib import pyplot as mpl
from mpl_toolkits.mplot3d import Axes3D 
import math
##
# user created libraries
from sqlPlotRoutines import *
from parseFiles import *
from sqlUtils import *

dataDirName="newData/"

#TODO: replace older 'tprofile' string entry of database with newer rollMid  rollScale entries
#TODO: may require renaming of original data files to new format


connection=sqlite3.connect(':memory:')

c=connection.cursor()

#WARNING NO Z_b or Z_f ENTRY
c.execute("CREATE TABLE models" + columnsString)


connection.commit()

tovData={'T':[],'mmax':[]}
tovFilename="HShen_0.1.dat"
tovFile=open(tovFilename,'r')
for line in tovFile:
    tovData['T'].append(float(line.split()[0]))
    tovData['mmax'].append(float(line.split()[1]))


###############################################################################
#
#  PARSE ALL THE DATA FILES!
#-----------------------------------------------------------------------------
#
parseCstDataDirectoryIntoDB(dataDirName,c,tableName="models")
#
###############################################################################


c.execute('''SELECT DISTINCT eos,tprofile,a,T
                             FROM models''')

sequenceList= c.fetchall()

#for i in sequenceList:
#    if i[1]=='roll13.5' and i[2]>0.5:
#        partitionPlot('ToverW',0.25,c,i,'b')

c.execute("CREATE TABLE mMaxseqs " + columnsString)
c.execute("CREATE TABLE spheroidMMaxseqs " + columnsString)
c.execute("CREATE TABLE toroidMMaxseqs " + columnsString)


cuts=" arealR < 30 AND ToverW < 0.27 "

for sequence in sequenceList:
    #find maximum mass for each sequence
    c.execute("SELECT MAX(gravMass) FROM models WHERE "+cuts+" AND eos=?  AND tprofile=? AND a=? AND T=? ORDER BY edMax", sequence)
    mMax = c.fetchone()[0]
    
    newSeq = sequence + tuple([mMax])
    #print newSeq

    #select maximum mass model from each sequence
    c.execute("SELECT * FROM models WHERE "+cuts+"AND eos=?  AND tprofile=? AND a=? AND T=? AND gravMass=?", newSeq)
    vals = c.fetchone()

    if vals:
        c.execute("INSERT INTO mMaxseqs VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",vals)
    else:
        print "No spheroidal OR toroidal models WHERE "+cuts+"for sequence: ", sequence


    #----------------------------------------------------------------------

    #find maximum mass model from spheroidal configurations
    c.execute("SELECT MAX(gravMass) FROM models WHERE "+cuts+"AND eos=?  AND tprofile=? AND a=? AND T=? AND RedMax=0 ORDER BY edMax", sequence)
    mMax = c.fetchone()[0]
    
    newSeq = sequence + tuple([mMax])
    #print mMax
    #select maximum mass model from sphreoidal configurations
    c.execute("SELECT * FROM models WHERE "+cuts+"AND eos=?  AND tprofile=? AND a=? AND T=? AND gravMass=?  AND RedMax=0", newSeq)
    vals = c.fetchone()
#    if (vals==None):
    # c.execute("SELECT * FROM models WHERE  eos=?  AND tprofile=? AND a=? AND T=? ", sequence)
    # print "-------------------------------------------------------_"
    # for i in c.fetchall():
    #     print i

    
        
    #print vals
    if vals:
        c.execute("INSERT INTO spheroidMMaxseqs VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",vals)
    else:
        print "No spheriodal models WHERE "+cuts+"for sequence: ", sequence

    #----------------------------------------------------------------------

    #find maximum mass model from toroidal configurations
    c.execute("SELECT MAX(gravMass) FROM models WHERE "+cuts+"AND eos=?  AND tprofile=? AND a=? AND T=? AND RedMax>0 ORDER BY edMax", sequence)
    mMax = c.fetchone()[0]
    
    newSeq = sequence + tuple([mMax])
    #select maximum mass model from toroidal configurations
    c.execute("SELECT * FROM models WHERE "+cuts+"AND eos=?  AND tprofile=? AND a=? AND T=? AND gravMass=?  AND RedMax>0", newSeq)
    vals = c.fetchone()
    
    if vals:
        c.execute("INSERT INTO toroidMMaxseqs VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",vals)
    else:
        print "No toroidal models WHERE "+cuts+"for sequence: ", sequence
        


c.execute("SELECT * FROM mMaxseqs")
print "Num sequences from mMaxseqs table: ", len(c.fetchall())
c.execute("SELECT * FROM spheroidMMaxseqs")
print "Num sequences from spheroidMMaxseqs table: ", len(c.fetchall())
c.execute("SELECT * FROM toroidMMaxseqs")
print "Num sequences from toroidMMaxseqs table: ", len(c.fetchall())


SEQ = "mMaxseqs"

colorList={'roll12.5':'b','roll13.5':'g','roll14':'k','roll14fat':'y','roll14thin':'c'}

profileList=['roll12.5','roll13.5','roll14','roll14fat','roll14thin']
colorList={'roll14':'k','roll14fat':'y','roll14thin':'c'}

profileList=['roll13.5','roll14fat']
colorList={'roll13.5':'k','roll14fat':'y'}

profileList=['roll13.5','roll14fat']
fig = mpl.figure()
ax = fig.add_subplot(111, projection='3d')

for profile in profileList:

    xs=[]
    ys=[]
    zs=[]   
    count=0
    for row in c.execute("SELECT edMax,gravMass,T,a FROM " + SEQ +
                         " WHERE tprofile='"+profile+"' AND T>0 " +
                         " ORDER BY T,a"):
        #print row[2], row[3], row[1]
        xs.append(row[3])
        ys.append(row[2])
        zs.append(row[1])
        count+=1

    print "count: ", count

    avals=[0.0,0.2,0.4,0.6,0.8,1.0]
    tvals=[0.5,10,20,30,40,50]
    X,Y=meshgrid(avals,tvals)
    tovM =[]
    for t in tvals:
        for i in range(len(tovData['T'])):
            if tovData['T'][i] == t:
                tovM.append(tovData['mmax'][i])

    print tovM
    tovX,tovY=meshgrid(avals,tvals)
    tovX,tovM=meshgrid(avals,tovM)
    
    print tovM

    zvals=(2.*ones( (6,6) )).tolist()
    # print zvals
    # print X
    # print Y
    for i in range(6):
        for j in range(6):
            for k in range(len(zs)):
                #print xs[k], ys[k], zs[k]
                if xs[k] == avals[i] and ys[k] == tvals[j]:
                    zvals[j][i] = zs[k]


    # for i in range(6):
    #     flag = 0
    #     for j in range(len(zvals[i])):
    #         if zvals[j][i] == 2:
    #             del zvals[j][i]
    #             del X[j][i]
    #             del Y[j][i]
    #             print X
    #             print
    #             flag = 1
    #             break
    #     if flag:
    #         break


    #print zvals
    #print X
    #print Y

    #ax.set_markersize(20)
    ax.scatter(xs,ys,zs,color=colorList[profile])
    ax.plot_wireframe(X,Y,zvals,color=colorList[profile])


ax.plot_surface(tovX,tovY,tovM,color='r')
#mpl.colorbar()
mpl.xlabel("Differential rotation parameter A^-1")
mpl.ylabel("Temperature [MeV]")
mpl.title("Gravitational Mass [Msun]")
mpl.suptitle("Sequence - " + SEQ)
mpl.legend(profileList)
mpl.show()

mpl.pcolor(X,Y,zvals)
mpl.colorbar()
mpl.show()

count=0

linestyles = [ '-', '--', ':','-.','']

for i in range(len(avals)/2):
    a=avals[i+3]


    xs=[]
    ys=[]

    Tmax=50.0

    plotList=[]


    for row in c.execute("SELECT edMax,gravMass,T FROM " + SEQ +
                       '''  WHERE '''+cuts+''' 
                            AND tprofile='roll13.5' AND a='''+str(a)+
                            " ORDER BY T"):
        color=(row[2]/Tmax,.2,1.-row[2]/Tmax)
        count = count +1
        xs.append(row[2])
        ys.append(row[1])
        #plotList.append(row[0])
        #plotList.append(row[1])

        #plotList.append('color='+color

        #mpl.plot(row[2],row[1],color=color,marker='x')

        #print list(row)


    print count


    mpl.plot(xs,ys, color='k',marker='x',linestyle=linestyles[i])

    xs=[]
    ys=[]

    for row in c.execute("SELECT edMax,gravMass,T FROM  " + SEQ +
                        ''' WHERE '''+cuts+''' 
                            AND tprofile='roll14' AND a='''+str(a)+
                            ''' ORDER BY T'''):
        color=(row[2]/Tmax,.2,1.-row[2]/Tmax)
        count = count +1
        xs.append(row[2])
        ys.append(row[1])
        #plotList.append(row[0])
        #plotList.append(row[1])

        #plotList.append('color='+color

        #mpl.plot(row[2],row[1],color='r',marker='+')

        #print list(row)

    mpl.plot(xs,ys, color='r',marker='+',linestyle=linestyles[i])

    xs=[]
    ys=[]

    for row in c.execute("SELECT edMax,gravMass,T FROM  " + SEQ +
                        ''' WHERE '''+cuts+''' 
                            AND tprofile='roll12.5' AND a='''+str(a)+
                            ''' ORDER BY T'''):
        color=(row[2]/Tmax,.2,1.-row[2]/Tmax)
        count = count +1
        xs.append(row[2])
        ys.append(row[1])
        #plotList.append(row[0])
        #plotList.append(row[1])

        #plotList.append('color='+color

        #mpl.plot(row[2],row[1],color='b',marker='+')

        #print list(row)

    mpl.plot(xs,ys, color='b',marker='o',linestyle=linestyles[i])

mpl.xlabel("Temperature [MeV]")
mpl.ylabel("Gravitational Mass [Msun]")
#mpl.title("Gravitational Mass [Msun]")
mpl.legend(['roll13.5','roll14','roll12.5'])
mpl.suptitle("Sequence - " + SEQ)

mpl.show()



connection.close()
