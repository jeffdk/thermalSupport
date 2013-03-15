from matplotlib import pyplot as plt
import numpy

def readFile(filename):

    data = {'d': [], 'rho': [], 'p': [], 's': [], 'T': [], 'Omega': []}

    answer = data.copy()

    infile = open(filename, 'r')
    print infile.readline()   # dump header
    for row in infile.readlines():
        print row[:-1]
        entries = row.split()
        answer['d'].append(float(entries[0]) / 100.0)   # convert from cm to m
        answer['rho'].append(float(entries[1]))
        answer['p'].append(float(entries[2]))
        answer['s'].append(float(entries[3]))
        answer['T'].append(float(entries[4]))
        answer['Omega'].append(float(entries[5]))
    for key in data.keys():
        answer[key] = numpy.array(answer[key])
    return answer

xaxisData = readFile('/home/jeff/work/Shen135135_x.dat')
yaxisData = readFile('/home/jeff/work/Shen135135_y.dat')
zaxisData = readFile('/home/jeff/work/Shen135135_z.dat')
print xaxisData

plotVar = 'Omega'

power = 2./2.

#plt.plot(xaxisData['d'], abs(xaxisData[plotVar]*xaxisData['d']**(power)), yaxisData['d'], abs(yaxisData[plotVar]*yaxisData['d']**(power)))
plt.plot(xaxisData['d'], xaxisData[plotVar], yaxisData['d'], yaxisData[plotVar])
#plt.plot(numpy.log(xaxisData['d']),    numpy.log(xaxisData[plotVar]),
#         numpy.log(yaxisData['d']), numpy.log(yaxisData[plotVar]))

plt.show()
