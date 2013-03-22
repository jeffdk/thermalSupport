from matplotlib import pyplot as plt
from matplotlib import rcParams
import numpy
import eosDriver
import plot_defaults
plt.rcParams['legend.fontsize'] = 18
##############################################################################
# Load Shen EOS for ye comparisons
##############################################################################
shen = eosDriver.eosDriver('/home/jeff/work/HShenEOS_rho220_temp180_ye65_version_1.1_20120817.h5')
plotBetaEq = True
parametrizedTempProfile = True
paramdTfunc = eosDriver.kentaDataTofLogRhoFit1()

def readFile(filename):

    data = {'d': [], 'rho': [], 'p': [], 's': [], 'T': [], 'Omega': [], 'ye': [], 'yeBetaEq': [],
            'yeBetaParamdTemp': [], 'tableP': [], 'betaP': [], 'constP': [],
            'constP.08': [], 'constP.1': [], 'constP.12': []  }
    labels = {'d': None, 'rho': None, 'p': None, 's': None, 'T': None, 'Omega': None, 'ye': None,
              'yeBetaEq': "Ye in BetaEq", 'tableP': 'Simulation', 'betaP': 'BetaEq',
              'constP': 'Ye=.15', 'constP.08': 'Ye=.08', 'constP.1': 'Ye=.1', 'constP.12': 'Ye=.12'
              }
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
    labels['ye'] = headers[7]
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
        answer['ye'].append(float(entries[6]))
        betaYe = shen.setBetaEqState({'rho': float(entries[1]),
                                      'temp': float(entries[4])})
        paramdT = paramdTfunc(numpy.log10(float(entries[1])))
        paramdBetaYe = shen.setBetaEqState({'rho': float(entries[1]),
                                            'temp': paramdT})
        shen.setState({'rho': float(entries[1]),
                       'temp': float(entries[4]),
                       'ye': float(entries[6])})
        answer['tableP'].append(shen.query('logpress', deLog10Result=True))
        shen.setState({'rho': float(entries[1]),
                       'temp': float(entries[4]),
                       'ye': betaYe})
        answer['betaP'].append(shen.query('logpress', deLog10Result=True))
        shen.setState({'rho': float(entries[1]),
                       'temp': float(entries[4]),
                       'ye': 0.15})
        answer['constP'].append(shen.query('logpress', deLog10Result=True))

        shen.setState({'rho': float(entries[1]),
                       'temp': float(entries[4]),
                       'ye': 0.08})
        answer['constP.08'].append(shen.query('logpress', deLog10Result=True))

        shen.setState({'rho': float(entries[1]),
                       'temp': float(entries[4]),
                       'ye': 0.1})
        answer['constP.1'].append(shen.query('logpress', deLog10Result=True))

        shen.setState({'rho': float(entries[1]),
                       'temp': float(entries[4]),
                       'ye': 0.12})
        answer['constP.12'].append(shen.query('logpress', deLog10Result=True))

        answer['yeBetaParamdTemp'].append(paramdBetaYe)
        answer['yeBetaEq'].append(betaYe)
    for key in data.keys():
        answer[key] = numpy.array(answer[key])
    return answer, labels

xaxisData, xlabels = readFile('/home/jeff/work/Shen135135_x_v2.dat')
yaxisData, ylabels = readFile('/home/jeff/work/Shen135135_y_v2.dat')
#zaxisData, zlabels = readFile('/home/jeff/work/Shen135135_z_v2.dat')

##############################################################################
#Pressure plots for different ye
##############################################################################
fracDiff = lambda x: x/xaxisData['tableP'] - 1.0
plt.plot(xaxisData['d'], fracDiff(xaxisData['p']),
         xaxisData['d'], fracDiff(xaxisData['betaP']),
         xaxisData['d'], fracDiff(xaxisData['constP']),
         xaxisData['d'], fracDiff(xaxisData['constP.08']),
         xaxisData['d'], fracDiff(xaxisData['constP.1']),
         xaxisData['d'], fracDiff(xaxisData['constP.12']))
plt.legend(['Simulation', xlabels['betaP'], xlabels['constP'],
            xlabels['constP.08'], xlabels['constP.1'], xlabels['constP.12']], loc=0)
plt.xlabel("Position on X-axis [km]")
plt.ylabel(r"P/P(table$|_{SimulationData}) - 1$")
plt.show()

plt.plot(numpy.log10(xaxisData['rho']),  fracDiff(xaxisData['p']),
         numpy.log10(xaxisData['rho']),  fracDiff(xaxisData['betaP']),
         numpy.log10(xaxisData['rho']),  fracDiff(xaxisData['constP']),
         numpy.log10(xaxisData['rho']),  fracDiff(xaxisData['constP.08']),
         numpy.log10(xaxisData['rho']),  fracDiff(xaxisData['constP.1']),
         numpy.log10(xaxisData['rho']),  fracDiff(xaxisData['constP.12']))
plt.legend(['Simulation', xlabels['betaP'], xlabels['constP'],
            xlabels['constP.08'], xlabels['constP.1'], xlabels['constP.12']], loc=0)
plt.ylabel(r"P/P(table$|_{SimulationData}) - 1$")
plt.xlabel(xlabels['rho'])
plt.show()
exit()

##############################################################################
# Plots vs distance; func allows for transformations on y-axis data
##############################################################################
for plotVar, func in [ #('Omega', None), ('rho', None), ('T', None), ('s', None), ('p', None),
                      ('ye', None), ('tableP', None), ('betaP', None), ('constP', None),
                      ('rho', lambda rho: numpy.log10(rho))]:
    yaxisLabel = ylabels[plotVar]
    logStr = ""
    legends = ['X-axis', 'Y-axis']
    if func is None:
        func = lambda x: x
    elif func(10.0) == 1.0:
        yaxisLabel = 'log10 ' + yaxisLabel
        logStr = 'log10'
    else:
        print "Warning unknown function type, not modifying label!"
    plt.xlabel("Distance from origin [km]")
    assert xlabels[plotVar] == ylabels[plotVar], "Column header mismatch!"
    plt.ylabel(yaxisLabel, labelPad=12)
    plt.plot(xaxisData['d'], func(xaxisData[plotVar]), 'b')
    if plotBetaEq and plotVar == 'ye':
        print "wtf"
        legends += ['X-ax BetaEq', 'Y-ax BetaEq']
        plt.plot(xaxisData['d'], func(xaxisData['yeBetaEq']), 'b', ls='--')
        if parametrizedTempProfile:
            plt.plot(xaxisData['d'], func(xaxisData['yeBetaParamdTemp']), 'b', ls=':')
            legends = ['Simulation', r'BetaEq($T_{simulation}$)', r'BetaEq($T_{parametrized}$)']
    d1, d2, var1, var2 = plt.axis()
    if numpy.log10(var2) > 2:
        scalePower = int(numpy.log10(var2))
        ylocs, ylabs = plt.yticks()
        plt.ylabel(yaxisLabel + '/$10^{' + str(scalePower) + '}$', labelpad=12)
        plt.yticks(ylocs, map(lambda x: "%.1f" % x, ylocs / numpy.power(10.0, scalePower)))
    plt.legend(legends, loc=9)
    fig = plt.gcf()
    fig.savefig("kentaPlots/shen135135_d_vs_" + logStr + plotVar + ".png")
    plt.show()
    #fig.clf()

#Log10(rho) plot
##############################################################################
# Plots vs density; func allows for transformations on X-AXIS data
##############################################################################
for plotVar, func in [#('Omega', None), ('T', None), ('s', None), ('p', None),
                      ('ye', None), ('ye', lambda rho: numpy.log10(rho)),
                      ('T', lambda rho: numpy.log10(rho)), ('s', lambda rho: numpy.log10(rho))]:
    yaxisLabel = ylabels[plotVar]
    xaxisLabel = xlabels['rho']
    legends = ['X-axis', 'Y-axis']
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
    plt.plot(func(xaxisData['rho']), xaxisData[plotVar])
    if plotBetaEq and plotVar == 'ye':
        print "wtf"
        legends += ['X-ax BetaEq', 'Y-ax BetaEq']
        plt.plot(func(xaxisData['rho']), xaxisData['yeBetaEq'], 'b', ls='--')
        if parametrizedTempProfile:
            plt.plot(func(xaxisData['rho']), xaxisData['yeBetaParamdTemp'], 'b', ls=':')
            legends = ['Simulation', r'BetaEq($T_{simulation}$)', r'BetaEq($T_{parametrized}$)']
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
    plt.legend(legends, loc=1)
    fig = plt.gcf()
    fig.savefig("kentaPlots/shen135135_" + logStr + "rho_vs_" + plotVar + ".png")
    #fig.clf()
    plt.show()


#plt.plot(xaxisData['d'], abs(xaxisData[plotVar]*xaxisData['d']**(power)), yaxisData['d'], abs(yaxisData[plotVar]*yaxisData['d']**(power)))

#plt.plot(numpy.log(xaxisData['d']),    numpy.log(xaxisData[plotVar]),
#         numpy.log(yaxisData['d']), numpy.log(yaxisData[plotVar]))
