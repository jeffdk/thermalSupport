from copy import deepcopy
from matplotlib import pyplot as plt
from eosDriver import kentaDataTofLogRhoFit1, kentaDataTofLogRhoFit2, getTRollFunc
from matplotlib import rcParams, rc
import numpy
import eosDriver
import plot_defaults
#plt.rcParams['legend.fontsize'] = 18
print rcParams.keys()
#rcParams['ytick.major.pad'] = 5
#rcParams['xtick.major.pad'] = 10
#rcParams['figure.subplot.left'] = 0.13
##### change a few standard settings
rcParams['xtick.major.size'] = 13
rcParams['xtick.major.pad']  = 8
rcParams['xtick.minor.size'] = 7
rc('legend', fontsize=26) #16
rcParams['ytick.major.size'] = 13
rcParams['ytick.major.pad']  = 8
rcParams['ytick.minor.size'] = 7
fig = plt.figure(figsize=(10, 8))
fig.subplots_adjust(left=0.14)
fig.subplots_adjust(bottom=0.14)
fig.subplots_adjust(top=0.967)
fig.subplots_adjust(right=0.97)

##############################################################################
# Load Shen EOS for ye comparisons
##############################################################################
shen = eosDriver.eosDriver('/home/jeff/work/HShenEOS_rho220_temp180_ye65_version_1.1_20120817.h5')
ls220 = eosDriver.eosDriver('/home/jeff/work/LS220_234r_136t_50y_analmu_20091212_SVNr26.h5')
theEos = shen
plotBetaEq = True
parametrizedTempProfile = False
paramdTfunc = eosDriver.kentaDataTofLogRhoFit1()
nuFullBetaEq = True

colors = {'c30p0': 'g',
          'c20p0': 'b',
          'c40p0': 'r',
          'cold': 'k',
          'c30p5': 'c',
          'c30p10': 'm',
          'sim': plot_defaults.kotzbraun}
scripts = {key: [] for key in colors.keys()}
scriptsList = ['c40p0', 'c30p0', 'c20p0', 'c30p10', 'c30p5', 'cold']
cXXp0_params = [(40.0, 14.18, 0.5,), (30.0, 14.055, 0.375),  (20.0, 13.93, 0.25)]
tempFuncs = [getTRollFunc(params[0], 0.01, params[1], params[2]) for params in cXXp0_params]
tempFuncs.append(kentaDataTofLogRhoFit1())
tempFuncs.append(kentaDataTofLogRhoFit2())
tempFuncs.append(lambda x: 0.01)
tempFuncsDict = {scriptsList[i]: tempFuncs[i] for i in range(len(scriptsList))}


def readFile(filename):

    data = {'d': [], 'rho': [], 'p': [], 's': [], 'T': [], 'Omega': [], 'ye': [], 'yeBetaEq': [],
            'yeBetaParamdTemp': [], 'tableP': [], 'betaP': [], 'constP': [], 'yeNuFull': [],
            'constP.08': [], 'constP.1': [], 'constP.12': [],
            'yeBetaScripts': deepcopy(scripts), 'yeNuFullScripts': deepcopy(scripts),
            'yeSimTempLess': [], 'yeSimTempFull': []}
    labels = {'d': None, 'rho': None, 'p': None, 's': None, 'T': None, 'Omega': None, 'ye': None,
              'yeBetaEq': "Ye in BetaEq", 'tableP': 'Simulation', 'betaP': 'BetaEq',
              'yeNuFull': "Ye in NuFull BetaEq",
              'constP': 'Ye=.15', 'constP.08': 'Ye=.08', 'constP.1': 'Ye=.1', 'constP.12': 'Ye=.12'
              }
    answer = data.copy()

    infile = open(filename, 'r')
    headers = infile.readline().split()
    print headers
    labels['d'] = headers[1].replace('cm', 'km')
    labels['rho'] = r"log$_{10}( \rho_\mathrm{b} \,\, [\mathrm{g\, cm}^{-3}])"
    labels['p'] = headers[3]
    labels['s'] = headers[4].replace('entropu[/', 'entropy [')
    labels['T'] = headers[5]
    labels['Omega'] = headers[6].replace('Omega', r'$\Omega$')
    labels['ye'] = r"Y$_e$"
    print labels
    for row in infile.readlines():
        entries = row.split()
        if float(entries[0]) < 0.0:
            # this only grabs positive x axis
            continue
        #print entries
        answer['d'].append(float(entries[0]) / 1.e5)   # convert from cm to km
        answer['rho'].append(float(entries[1]))
        answer['p'].append(float(entries[2]))
        answer['s'].append(float(entries[3]))
        answer['T'].append(float(entries[4]))
        answer['Omega'].append(float(entries[5]))
        answer['ye'].append(float(entries[6]))
        rhob = float(entries[1])
        for script in scriptsList:
            temp = tempFuncsDict[script](numpy.log10(rhob))
            betaYe = theEos.setBetaEqState({'rho': rhob,
                                          'temp': temp})

            answer['yeBetaScripts'][script].append(betaYe)
            nuFullBetaYe = theEos.setNuFullBetaEqState({'rho': rhob,
                                                      'temp': temp})
            factor = numpy.exp(-numpy.power(10.0, 12.5)/float(entries[1]))
            nuFullBetaYe = nuFullBetaYe * factor + (1.0 - factor) * betaYe
            answer['yeNuFullScripts'][script].append(nuFullBetaYe)

        yeSimTempLess = theEos.setBetaEqState({'rho': rhob, 'temp': float(entries[4])})
        yeSimTempFull = theEos.setNuFullBetaEqState({'rho': rhob, 'temp': float(entries[4])})

        yeSimTempFull = yeSimTempFull * factor + (1.0 - factor) * yeSimTempLess
        answer['yeSimTempLess'].append(yeSimTempLess)
        answer['yeSimTempFull'].append(yeSimTempFull)
        # shen.setState({'rho': float(entries[1]),
        #                'temp': float(entries[4]),
        #                'ye': float(entries[6])})
        # answer['tableP'].append(shen.query('logpress', deLog10Result=True))
        # shen.setState({'rho': float(entries[1]),
        #                'temp': float(entries[4]),
        #                'ye': betaYe})
        # answer['betaP'].append(shen.query('logpress', deLog10Result=True))
        # shen.setState({'rho': float(entries[1]),
        #                'temp': float(entries[4]),
        #                'ye': 0.15})
        # answer['constP'].append(shen.query('logpress', deLog10Result=True))
        #
        # shen.setState({'rho': float(entries[1]),
        #                'temp': float(entries[4]),
        #                'ye': 0.08})
        # answer['constP.08'].append(shen.query('logpress', deLog10Result=True))
        #
        # shen.setState({'rho': float(entries[1]),
        #                'temp': float(entries[4]),
        #                'ye': 0.1})
        # answer['constP.1'].append(shen.query('logpress', deLog10Result=True))
        #
        # shen.setState({'rho': float(entries[1]),
        #                'temp': float(entries[4]),
        #                'ye': 0.12})
        # answer['constP.12'].append(shen.query('logpress', deLog10Result=True))
        #
    for key in data.keys():
        answer[key] = numpy.array(answer[key])
    return answer, labels

xaxisData, xlabels = readFile('/home/jeff/work/Shen135135_x_v2.dat')
#yaxisData, ylabels = readFile('/home/jeff/work/Shen135135_y_v2.dat')
#zaxisData, zlabels = readFile('/home/jeff/work/Shen135135_z_v2.dat')
#
# ##############################################################################
# #Paper temperature plot
# ##############################################################################
# fig = plt.figure(figsize=(10, 8))
# fig.subplots_adjust(left=0.124)
# fig.subplots_adjust(bottom=0.14)
# fig.subplots_adjust(top=0.967)
# fig.subplots_adjust(right=0.97)
#
# plateau10 = kentaDataTofLogRhoFit1()
# plateau5 = kentaDataTofLogRhoFit2()
# core20 = getTRollFunc(20.0, 0.01, 14.0 - .07, .25)
# core30 = getTRollFunc(30.0, 0.01, 14.125 - .07, .375)
# core40 = getTRollFunc(40.0, 0.01, 14.25 - 0.07, .5)
#
# lrs = numpy.log10([xaxisData['rho'][i] for i in range(len(xaxisData['rho'])) if xaxisData['d'][i] > 0.0])
# simTemps = [xaxisData['T'][i] for i in range(len(xaxisData['rho'])) if xaxisData['d'][i] > 0.0]
# lrsMore = numpy.array([15.1, 15.0, 14.9, 14.8] + lrs.tolist())
# fig.add_subplot(111).plot(lrs, simTemps, 'm',
#          lrsMore, core40(lrsMore), 'r',
#          lrsMore, core30(lrsMore), 'g',
#          lrsMore, core20(lrsMore), 'b',
#          lrsMore, plateau10(lrsMore), 'k',
#          lrsMore, plateau5(lrsMore), 'c')
# legends = ["Sekiguchi et al.", "c40p0", "c30p0", "c20p0", "c30p10", "c30p5"]
# plt.xlabel(r"$\mathrm{log_{10}}(\rho_b$ [g cm$^{-3}$])", labelpad=12)
# plt.ylabel(r"$T$ [MeV]", labelpad=12)
# plt.legend(legends, bbox_to_anchor=(0, 0, .65, .92))
# plt.xlim([10.9, 15.0])
# labels = plt.getp(plt.gca(), 'xticklabels')
# plt.setp(labels, size=28)
# xminorLocator = plt.MultipleLocator(0.2)
# xmajorLocator = plt.MultipleLocator(1)
#
# yminorLocator = plt.MultipleLocator(1)
# ymajorLocator = plt.MultipleLocator(5)
# ax = plt.gca()
# ax.xaxis.set_major_locator(xmajorLocator)
# ax.xaxis.set_minor_locator(xminorLocator)
# ax.yaxis.set_minor_locator(yminorLocator)
# ax.yaxis.set_major_locator(ymajorLocator)
# labels = plt.getp(plt.gca(), 'yticklabels')
# plt.setp(labels, size=28)
# plt.show()
# exit()
##############################################################################
#Pressure plots for different ye
##############################################################################
# fracDiff = lambda x: x/xaxisData['tableP'] - 1.0
# plt.plot(xaxisData['d'], fracDiff(xaxisData['p']),
#          xaxisData['d'], fracDiff(xaxisData['betaP']),
#          xaxisData['d'], fracDiff(xaxisData['constP']),
#          xaxisData['d'], fracDiff(xaxisData['constP.08']),
#          xaxisData['d'], fracDiff(xaxisData['constP.1']),
#          xaxisData['d'], fracDiff(xaxisData['constP.12']))
# plt.legend(['Simulation', xlabels['betaP'], xlabels['constP'],
#             xlabels['constP.08'], xlabels['constP.1'], xlabels['constP.12']], loc=0)
# plt.xlabel("Position on X-axis [km]")
# plt.ylabel(r"P/P(table$|_{SimulationData}) - 1$")
# plt.show()
#
# plt.plot(numpy.log10(xaxisData['rho']),  fracDiff(xaxisData['p']),
#          numpy.log10(xaxisData['rho']),  fracDiff(xaxisData['betaP']),
#          numpy.log10(xaxisData['rho']),  fracDiff(xaxisData['constP']),
#          numpy.log10(xaxisData['rho']),  fracDiff(xaxisData['constP.08']),
#          numpy.log10(xaxisData['rho']),  fracDiff(xaxisData['constP.1']),
#          numpy.log10(xaxisData['rho']),  fracDiff(xaxisData['constP.12']))
# plt.legend(['Simulation', xlabels['betaP'], xlabels['constP'],
#             xlabels['constP.08'], xlabels['constP.1'], xlabels['constP.12']], loc=0)
# plt.ylabel(r"P/P(table$|_{SimulationData}) - 1$")
# plt.xlabel(xlabels['rho'])
# plt.show()


##############################################################################
# Plots vs distance; func allows for transformations on y-axis data
##############################################################################
# for plotVar, func in [ #('Omega', None), ('rho', None), ('T', None), ('s', None), ('p', None),
#                       ('ye', None)]:
#     yaxisLabel = xlabels[plotVar]
#     logStr = ""
#     legends = ['X-axis', 'Y-axis']
#     if func is None:
#         func = lambda x: x
#     elif func(10.0) == 1.0:
#         yaxisLabel = 'log10 ' + yaxisLabel
#         logStr = 'log10'
#     else:
#         print "Warning unknown function type, not modifying label!"
#     plt.xlabel("Distance from origin [km]")
#     #assert xlabels[plotVar] == ylabels[plotVar], "Column header mismatch!"
#     plt.ylabel(yaxisLabel)#, labelPad=12)
#     plt.plot(xaxisData['d'], func(xaxisData[plotVar]), 'b')
#     if plotBetaEq and plotVar == 'ye':
#         print "wtf"
#         legends += ['X-ax BetaEq', 'Y-ax BetaEq']
#         plt.plot(xaxisData['d'], func(xaxisData['yeBetaEq']), 'b', ls='--')
#         if nuFullBetaEq:
#             plt.plot(xaxisData['d'], func(xaxisData['yeNuFull']), 'b', ls=':')
#             legends = ['Simulation', r'$\nu$Less-BetaEq($T_{simulation}$)', r'$\nu$Full BetaEq($T_{sim}$)']
#         if parametrizedTempProfile:
#             plt.plot(xaxisData['d'], func(xaxisData['yeBetaParamdTemp']), 'b', ls=':')
#             legends = ['Simulation', r'BetaEq($T_{simulation}$)', r'BetaEq($T_{parametrized}$)']
#     d1, d2, var1, var2 = plt.axis()
#     if numpy.log10(var2) > 2:
#         scalePower = int(numpy.log10(var2))
#         ylocs, ylabs = plt.yticks()
#         plt.ylabel(yaxisLabel + '/$10^{' + str(scalePower) + '}$')#, labelpad=12)
#         plt.yticks(ylocs, map(lambda x: "%.1f" % x, ylocs / numpy.power(10.0, scalePower)))
#     plt.legend(legends, loc=9)
#     fig = plt.gcf()
#     #fig.savefig("kentaPlots/shen135135_d_vs_" + logStr + plotVar + ".png")
#     plt.show()
#     #fig.clf()

#Log10(rho) plot
##############################################################################
# Plots vs density; func allows for transformations on X-AXIS data
##############################################################################
for plotVar, func in [#('Omega', None), ('T', None), ('s', None), ('p', None),
                      ('ye', lambda rho: numpy.log10(rho))]:
    yaxisLabel = xlabels[plotVar]
    xaxisLabel = xlabels['rho']
    legends = ['X-axis', 'Y-axis']
    logStr = ""
    if func is None:
        func = lambda x: x

    else:
        print "Warning unknown function type, not modifying label!"
    plt.xlabel(xaxisLabel)
    plt.ylabel(yaxisLabel)#, labelpad=12)
    plt.plot(func(xaxisData['rho']), xaxisData[plotVar], c=colors['sim'],
             dashes=plot_defaults.longDashes, lw=4, zorder=4)
    plt.plot(func(xaxisData['rho']), xaxisData['yeSimTempLess'], c=colors['sim'],
             dashes=plot_defaults.goodDashDot, zorder=4)
    plt.plot(func(xaxisData['rho']), xaxisData['yeSimTempFull'], c=colors['sim'], zorder=4)
    if plotBetaEq and plotVar == 'ye':
        legends += ['X-ax BetaEq', 'Y-ax BetaEq']
        theDict = deepcopy(xaxisData['yeBetaScripts'])
        nuFullDict = deepcopy(xaxisData['yeNuFullScripts'])
        for script in scriptsList:
            print theDict[script]
            plt.plot(func(xaxisData['rho']), theDict[script], dashes=plot_defaults.goodDashDot,
                     c=colors[script])
            if nuFullBetaEq:
                plt.plot(func(xaxisData['rho']), nuFullDict[script], ls='-',
                         c=colors[script], label=script)
                legends = ['Simulation', r'$\nu$Less-BetaEq($T_{simulation}$)', r'$\nu$Full BetaEq($T_{sim}$)']
    rho1, rho2, var1, var2 = plt.axis()
    if numpy.log10(var2) > 2:
        ylocs, ylabs = plt.yticks()
        scalePower = int(numpy.log10(var2))
        plt.ylabel(yaxisLabel + '/$10^{' + str(scalePower) + '}$')#, labelpad=12)
        plt.yticks(ylocs, map(lambda x: "%.1f" % x, ylocs / numpy.power(10.0, scalePower)))
    #if numpy.log10(rho2) > 2:
    xlocs, xlabs = plt.xticks()
    #scalePower = int(numpy.log10(rho2))
    #plt.xlabel(xaxisLabel + '/$10^{' + str(scalePower) + '}$')
    #plt.xticks(xlocs, map(lambda x: "%.0f" % x, xlocs / numpy.power(10.0, scalePower)))
    ax = plt.gca()
    xminorLocator = plt.MultipleLocator(0.2)
    xmajorLocator = plt.MultipleLocator(1)
    ax.xaxis.set_major_locator(xmajorLocator)
    ax.xaxis.set_minor_locator(xminorLocator)
    legend1 = plt.legend(loc=1, handletextpad=.1)
    fig = plt.gcf()
    #fig.savefig("kentaPlots/shen135135_" + logStr + "rho_vs_" + plotVar + ".png")
    #fig.clf()
    p1, = plt.plot([1], [1], c='k')
    p2, = plt.plot([1], [1], c='k', ls='--', dashes=plot_defaults.goodDashDot)
    p3, = plt.plot([1], [1], c=colors['sim'], lw=4, ls='--', dashes=plot_defaults.longDashes)
    legend2 = plt.legend((p1, p2, p3), ("$\\nu$-full $\\beta$-eq.",
                                        "$\\nu$-less $\\beta$-eq.",
                                        "Sekiguchi et al."),
                                        loc=9, handletextpad=.1)
    plt.gca().add_artist(legend1)
    plt.minorticks_on()
    plt.xlim([10.9, 15.0])
    plt.ylim([0.0, 0.36])
    plt.show()


#plt.plot(xaxisData['d'], abs(xaxisData[plotVar]*xaxisData['d']**(power)), yaxisData['d'], abs(yaxisData[plotVar]*yaxisData['d']**(power)))

#plt.plot(numpy.log(xaxisData['d']),    numpy.log(xaxisData[plotVar]),
#         numpy.log(yaxisData['d']), numpy.log(yaxisData[plotVar]))
