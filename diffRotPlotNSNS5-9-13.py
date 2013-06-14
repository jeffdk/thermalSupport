from eosDriver import eosDriver, getTRollFunc, kentaDataTofLogRhoFit2
import matplotlib
import matplotlib.pyplot as plt
import numpy
from datasetManager import cstDataset, cstSequence
import plot_defaults
from plotUtilsForPaper import fixExponentialAxes, removeExponentialNotationOnAxis
matplotlib.rcParams['figure.subplot.left'] = 0.15
myfig = plt.figure(figsize=(10, 8))
myfig.subplots_adjust(left=0.15)
myfig.subplots_adjust(bottom=0.14)
myfig.subplots_adjust(top=0.967)
myfig.subplots_adjust(right=0.96)
sourceDb = '/home/jeff/work/rotNSruns/vdenseBetaEqOnlyMoreC.db'
tovSourceDb = '/home/jeff/work/rotNSruns/allRuns3-25-13.db'
shenEosTableFilename = '/home/jeff/work/HShenEOS_rho220_temp180_ye65_version_1.1_20120817.h5'
ls220EosTableFilename = '/home/jeff/work/LS220_234r_136t_50y_analmu_20091212_SVNr26.h5'

eosName = 'HShenEOS'
theEos = eosDriver(shenEosTableFilename)

tovSlice = {'a': 0.0, 'rpoe': 1.0}
uniformMaxRotSlice = {'a': 0.0, 'rpoe': 'min'}
diffMaxRotSlice = {'a': 1.0, 'rpoe': 'min'}
a8 = {'a': 0.8, 'rpoe': 'min'}
a7 = {'a': 0.7, 'rpoe': 'min'}
a6 = {'a': 0.6, 'rpoe': 'min'}
a5 = {'a': 0.5, 'rpoe': 'min'}
a4 = {'a': 0.4, 'rpoe': 'min'}

colors = {'c30p0': 'g',
          'c20p0': 'b',
          'c40p0': 'r',
          'cold': 'k',
          'c30p5': 'c',
          'c30p10': 'm'}

scripts = ['c40p0', 'cold']
params40 = (40.0, 14.18, 0.5,)
params20 = (20.0, 13.93, 0.25,)
tFuncs = [#getTRollFunc(params20[0], 0.01, params20[1], params20[2]),
          getTRollFunc(params40[0], 0.01, params40[1], params40[2]),
          #kentaDataTofLogRhoFit2(),
          lambda x: 0.01]
ye = 'BetaEq'
colorLegs = []
pltsForLeg = []
#############################################################
# First lay down RotNS results
#############################################################
for i, script in enumerate(scripts):
    #break
    tempFunc = tFuncs[i]
    theEos.resetCachedBetaEqYeVsRhobs(tempFunc, 13.5, 16.0)

    xFunc = lambda x: theEos.rhobFromEnergyDensityWithTofRho(x, ye, tempFunc)
    #xFunc = lambda x: x
    filters = ('ToverW<0.25',)

    thisSet = cstDataset(script, eosName, ye, sourceDb)
    dashList = [(None, None), (25, 4), (13, 5), (20, 4, 10, 6), (10, 3, 5, 5)]
    # (20, 5, 10, 5, 5, 10)]
    pltsForLeg = []
    dashList = dashList[::-1]
    for j, slicer in enumerate([uniformMaxRotSlice, a5, diffMaxRotSlice]):
        thisSeq = cstSequence(thisSet, slicer, filters)

        thisPlot = thisSeq.getSeqPlot(['edMax'], ['gravMass', 'baryMass'], filters, xcolFunc=xFunc,
                                      ycolFunc=lambda x, y: y)

        plert, = plt.plot(*thisPlot, c=colors[script], dashes=dashList[j], lw=(3+j//2)/2.0)
        pltsForLeg.append(plert)
    colorLegs.append(plert)
    del thisSet
legend1 = plt.legend(pltsForLeg + colorLegs, [r"$\tilde{A}=0.0$", r"$\tilde{A}=0.5$",
                                              r"$\tilde{A}=1.0$"] + scripts,
                     loc=4, handlelength=4, labelspacing=0.5, handletextpad=0.5)
#############################################################
# Second plot points from Sekiguchi et al
#############################################################
endDensity = 1.2e15
sekiguchiData = [{"label": 'L',
                  "TOV_Mg": 1.35,
                  "TOV_Mb": 1.45,
                  "HMNS_Mb": 2.90,
                  "TOV_rhob": 4.87e14,
                  "HMNS_9ms_rhob": 5.7e14,
                  "HMNS_25ms_rhob": 6.8e14},
                 {"label": 'M',
                  "TOV_Mg": 1.5,
                  "TOV_Mb": 1.64,
                  "HMNS_Mb": 3.28,
                  "TOV_rhob": 5.39e14,
                  "HMNS_9ms_rhob": 7.6e14,
                  "HMNS_25ms_rhob": 9.1e14},
                 {"label": 'H',
                  "TOV_Mg": 1.6,
                  "TOV_Mb": 1.77,
                  "HMNS_Mb": 3.54,
                  "TOV_rhob": 5.79e14,
                  "HMNS_9ms_rhob": endDensity,
                  "HMNS_25ms_rhob": None},
                 ]
colors = [plot_defaults.darkmagenta, plot_defaults.green2, 'b']
symbolSize = 200
lineWidth = 5
legendPlts = []
firstTime = True
for i, model in enumerate(sekiguchiData):
    mb = [model['HMNS_Mb']]
    plt.scatter([model['TOV_rhob']], mb, marker='o', c=colors[i], s=symbolSize*.6,
                zorder=4)

    plert, = plt.plot([model['TOV_rhob'], model['HMNS_9ms_rhob']], [mb, mb], c=colors[i], ls='-',
                      lw=lineWidth)
    legendPlts.append(plert)
    dynamicAnnoteString = ""
    secularAnnoteString = ""
    dynamiceAnnoteRad = 0.3
    secularAnnoteRad = -0.3
    if model["HMNS_25ms_rhob"] is not None:
        plt.scatter([model['HMNS_9ms_rhob']], mb, marker='d', c=colors[i], s=symbolSize*.7,
                    zorder=4)
        plt.plot([model['HMNS_9ms_rhob'], model['HMNS_25ms_rhob']], [mb, mb],
                 c=colors[i], dashes=(3, 1.5), lw=lineWidth)
        plt.scatter([model['HMNS_25ms_rhob']], mb, marker='s', c=colors[i], s=symbolSize*.8,
                    zorder=4)
        secularAnnotateRho = (model['HMNS_25ms_rhob'] - model['HMNS_9ms_rhob']) / 2.0 + model['HMNS_9ms_rhob']
        if not firstTime:
            secularAnnoteString = "Secular evolution (dotted lines)"
            secularAnnoteRad = 0.0
        plt.annotate(secularAnnoteString, (secularAnnotateRho, model['HMNS_Mb'] - 0.015),
                 xytext=(0.2, 0.07),  va="center",
                 xycoords='data', textcoords='axes fraction',
                 arrowprops={'arrowstyle': '->', 'connectionstyle': "arc3,rad=%s" % secularAnnoteRad,
                             'fc': "0.6", 'ec': "k", 'relpos': (-0.001, 1.)},
                 #{'width': 1, 'frac': 0.2},
                 fontsize=18,
                 zorder=5)
        plt.annotate("9 ms", (model['HMNS_9ms_rhob'] - .3e14, model['HMNS_Mb'] + 0.07),
                 xytext=(model['HMNS_9ms_rhob'] - .3e14, model['HMNS_Mb'] + 0.07),
                 xycoords='data', textcoords='data',
                 bbox={'ec': "none", 'fc': 'w'},
                 fontsize=16,
                 zorder=5)
        plt.annotate("25 ms", (model['HMNS_25ms_rhob'] - .2e14, model['HMNS_Mb'] + 0.07),
                 xytext=(model['HMNS_25ms_rhob'] - .2e14, model['HMNS_Mb'] + 0.07),
                 xycoords='data', textcoords='data',
                 bbox={'ec': "none", 'fc': 'w'},
                 fontsize=16,
                 zorder=5)
    else:
        dynamiceAnnoteRad = -0.0
        dynamicAnnoteString = "Dynamical evolution (solid lines)"
        plt.scatter([endDensity*1.0], mb, marker='>', c=colors[i], s=symbolSize,
                    zorder=4, edgecolors=None)
        plt.annotate("Collapse (9 ms)", (endDensity*0.8, mb[0]+.06),
                 xytext=(endDensity*0.8, mb[0]+.06),
                 xycoords='data', textcoords='data',
                 bbox={'ec': "none", 'fc': 'w'},
                 fontsize=18)
        #plt.arrow(endDensity, mb[0], endDensity*.1, 0.0, fc=colors[i], ec=colors[i],
        #          head_width=0.01, head_length=1e14)
    dynamicAnnotateRho = (model['HMNS_9ms_rhob'] - model['TOV_rhob']) / 4.0 + model['TOV_rhob']
    plt.annotate(dynamicAnnoteString, (dynamicAnnotateRho, model['HMNS_Mb'] + 0.015),
                 xytext=(0.05, 0.93),
                 xycoords='data', textcoords='axes fraction',
                 arrowprops={'arrowstyle': '->',
                             'connectionstyle': "arc3,rad=%s" % dynamiceAnnoteRad,
                             'fc': "0.6", 'ec': "k", 'relpos': (-.005, 0.)},
                 #{'width': 1, 'frac': 0.2},
                 fontsize=18,
                 zorder=5)
    firstTime = False

legend2 = plt.legend(legendPlts, [model['label'] for model in sekiguchiData],
                     loc=1, labelspacing=0.2, handletextpad=0.5)
plt.gca().add_artist(legend1)


textPos = 1.2
if eosName == "HShenEOS":
    eosName = "HShen"
    textPos = 4.0
plt.text(1.0e15, textPos, eosName, fontsize=26)  #  Mg LS220
plt.minorticks_on()
plt.xlabel(r"$\rho_{\mathrm{b, max}}$ [$10^{15}$ g cm$^{-3}$]", labelpad=10)
plt.ylabel("$M_\mathrm{b} \,\, [M_\odot]$", labelpad=6)
plt.xlim([4.1e14, 1.3e15])
plt.ylim([2.05, 4.3])
fixExponentialAxes()
#removeExponentialNotationOnAxis('x')
plt.show()