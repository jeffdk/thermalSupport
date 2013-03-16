from matplotlib import pyplot as plt
import numpy
import plot_defaults


def readFile(filename):

    data = {'d': [], 'rho': [], 'p': [], 's': [], 'T': [], 'Omega': []}
    labels = {'d': None, 'rho': None, 'p': None, 's': None, 'T': None, 'Omega': None}
    answer = data.copy()

    infile = open(filename, 'r')
    headers = infile.readline().split()
    print headers
    labels['d'] = headers[1].replace('cm', 'km')
    labels['rho'] = headers[2].replace('rho', r'$\rho$')
    labels['p'] = headers[3]
    labels['s'] = headers[4].replace('entropu[/', 'entropy [')
    labels['T'] = headers[5]
    labels['Omega'] = headers[6].replace('Omega', r'$\Omega$')
    print labels
    for row in infile.readlines():
        entries = row.split()
        #print entries
        answer['d'].append(float(entries[0]) / 1.e5)   # convert from cm to km
        answer['rho'].append(float(entries[1]))
        answer['p'].append(float(entries[2]))
        answer['s'].append(float(entries[3]))
        answer['T'].append(float(entries[4]))
        answer['Omega'].append(float(entries[5]))
    for key in data.keys():
        answer[key] = numpy.array(answer[key])
    return answer, labels

xaxisData, xlabels = readFile('/home/jeff/work/Shen135135_x.dat')
yaxisData, ylabels = readFile('/home/jeff/work/Shen135135_y.dat')
zaxisData, zlabels = readFile('/home/jeff/work/Shen135135_z.dat')
#print xaxisData

##############################################################################
# Plots vs distance; func allows for transformations on y-axis data
##############################################################################
for plotVar, func in [('Omega', None), ('rho', None), ('T', None), ('s', None), ('p', None),
                      ('rho', lambda rho: numpy.log10(rho))]:
    yaxisLabel = ylabels[plotVar]
    logStr = ""
    if func is None:
        func = lambda x: x
    elif func(10.0) == 1.0:
        yaxisLabel = 'log10 ' + yaxisLabel
        logStr = 'log10'
    else:
        print "Warning unknown function type, not modifying label!"
    plt.xlabel("Distance from origin [km]")
    assert xlabels[plotVar] == ylabels[plotVar], "Column header mismatch!"
    plt.ylabel(yaxisLabel, labelpad=12)
    plt.plot(xaxisData['d'], func(xaxisData[plotVar]), yaxisData['d'], func(yaxisData[plotVar]))
    d1, d2, var1, var2 = plt.axis()
    if numpy.log10(var2) > 2:
        scalePower = int(numpy.log10(var2))
        ylocs, ylabs = plt.yticks()
        plt.ylabel(yaxisLabel + '/$10^{' + str(scalePower) + '}$', labelpad=12)
        plt.yticks(ylocs, map(lambda x: "%.1f" % x, ylocs / numpy.power(10.0, scalePower)))
    plt.legend(['X-axis', 'Y-axis'], loc=4)
    #plt.legend([xlabels['d'], ylabels['d']])
    fig = plt.gcf()
    fig.savefig("kentaPlots/shen135135_d_vs_" + logStr + plotVar + ".png")
    plt.show()
    #fig.clf()

#Log10(rho) plot
##############################################################################
# Plots vs density; func allows for transformations on X-AXIS data
##############################################################################
for plotVar, func in [('Omega', None), ('T', None), ('s', None), ('p', None),
                      ('T', lambda rho: numpy.log10(rho)), ('s', lambda rho: numpy.log10(rho))]:
    yaxisLabel = ylabels[plotVar]
    xaxisLabel = xlabels['rho']
    logStr = ""
    if func is None:
        func = lambda x: x
    elif func(10.0) == 1.0:
        xaxisLabel = 'log10 ' + xaxisLabel
        logStr = 'log10'
    else:
        print "Warning unknown function type, not modifying label!"
    plt.xlabel(xaxisLabel)
    plt.ylabel(yaxisLabel, labelpad=12)
    plt.plot(func(xaxisData['rho']), xaxisData[plotVar], func(yaxisData['rho']), yaxisData[plotVar])
    rho1, rho2, var1, var2 = plt.axis()
    if numpy.log10(var2) > 2:
        ylocs, ylabs = plt.yticks()
        scalePower = int(numpy.log10(var2))
        plt.ylabel(yaxisLabel + '/$10^{' + str(scalePower) + '}$', labelpad=12)
        plt.yticks(ylocs, map(lambda x: "%.1f" % x, ylocs / numpy.power(10.0, scalePower)))
    if numpy.log10(rho2) > 2:
        xlocs, xlabs = plt.xticks()
        scalePower = int(numpy.log10(rho2))
        plt.xlabel(xaxisLabel + '/$10^{' + str(scalePower) + '}$')
        plt.xticks(xlocs, map(lambda x: "%.1f" % x, xlocs / numpy.power(10.0, scalePower)))
    plt.legend(['X-axis', 'Y-axis'], loc=2)
    fig = plt.gcf()
    fig.savefig("kentaPlots/shen135135_" + logStr + "rho_vs_" + plotVar + ".png")
    #fig.clf()
    plt.show()


#plt.plot(xaxisData['d'], abs(xaxisData[plotVar]*xaxisData['d']**(power)), yaxisData['d'], abs(yaxisData[plotVar]*yaxisData['d']**(power)))

#plt.plot(numpy.log(xaxisData['d']),    numpy.log(xaxisData[plotVar]),
#         numpy.log(yaxisData['d']), numpy.log(yaxisData[plotVar]))
