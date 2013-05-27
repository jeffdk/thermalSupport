from eosDriver import eosDriver, getTRollFunc, kentaDataTofLogRhoFit1, kentaDataTofLogRhoFit2
import matplotlib
import matplotlib.pyplot as plt
import numpy
from datasetManager import cstDataset, cstSequence
import plot_defaults
from plotUtilsForPaper import fixExponentialAxes, removeExponentialNotationOnAxis

matplotlib.rcParams['figure.subplot.left'] = 0.15

sourceDb = '/home/jeff/work/rotNSruns/vdenseBetaEqD5-26.db'
c30p10Db = '/home/jeff/work/rotNSruns/svdense30p10A.db'
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

symbols = {'c30p0': 's',
           'c20p0': 'v',
           'c40p0': '^',
           'c30p5': 'p',
           'c30p10': 'H',
           'cold': '*'}

slicesToPlot = [a7, diffMaxRotSlice]
plateauPlots = True

tFuncs = []
scripts = []
if plateauPlots:
    scripts = ['c30p10', 'c30p5', 'cold']
    tFuncs = [kentaDataTofLogRhoFit1(),
              kentaDataTofLogRhoFit2(),
              lambda x: 0.01]
else:
    params40 = (40.0, 14.18, 0.5,)
    params20 = (20.0, 13.93, 0.25,)
    scripts = ['c40p0', 'c20p0', 'cold']
    tFuncs = [getTRollFunc(params40[0], 0.01, params40[1], params40[2]),
              getTRollFunc(params20[0], 0.01, params20[1], params20[2]),
              lambda x: 0.01]



ye = 'BetaEq'
colorLegs = []
for i, script in enumerate(scripts):

    tempFunc = tFuncs[i]
    theEos.resetCachedBetaEqYeVsRhobs(tempFunc, 13.5, 16.0)

    xFunc = lambda x: theEos.rhobFromEnergyDensityWithTofRho(x, ye, tempFunc) / 1.0e15
    #xFunc = lambda x: x
    filters = ('ToverW<0.25',)

    thisSet = cstDataset(script, eosName, ye, sourceDb)
    if script == 'c30p10':
        thisSet.addEntriesFromDb(c30p10Db)
    dashList = [(None, None), (25, 4), (13, 5), (20, 4, 10, 6), (10, 3, 5, 5), (3, 1)]
    # (20, 5, 10, 5, 5, 10)]
    pltsForLeg = []
    dashList = dashList[::-1]
    for j, slicer in enumerate(slicesToPlot):
        thisSeq = cstSequence(thisSet, slicer, filters)
        filters = ('ToverW<0.25',)
        thisPlot = thisSeq.getSeqPlot(['edMax'], ['gravMass', 'baryMass', 'arealR'], filters, xcolFunc=xFunc,
                                      ycolFunc=lambda x, y, z: y)

        plert, = plt.semilogx(*thisPlot, c=colors[script], dashes=dashList[j], lw=(3+j)/2.0)
        pltsForLeg.append(plert)
    colorLegs.append(plert)
    del thisSet
legend1 = plt.legend(pltsForLeg, ("TOV", r"$\tilde{A}=0.0$", r"$\tilde{A}=0.4$", r"$\tilde{A}=0.5$",
                                  r"$\tilde{A}=0.7$", r"$\tilde{A}=1.0$"),
                     loc=1, handlelength=4)
legend2 = plt.legend(colorLegs, scripts,
                     loc=9, labelspacing=0.3, handletextpad=0.4)
plt.gca().add_artist(legend1)
plt.xlim([.50, 2.5])
locator = matplotlib.ticker.FixedLocator([0.5, 1.0, 2.5])
#plt.ylim([1.1, 3.75])
if eosName == "HShenEOS":
    eosName = "HShen"
    plt.xlim([.4, 2.])
    #plt.ylim([1.1, 4.15])
    plt.text(1.5, 3.8, eosName, fontsize=26) # Mb shen
    locator = matplotlib.ticker.FixedLocator([0.4, 1.0, 2.0])
else:
    plt.text(1.9, 3.4, eosName, fontsize=26) # Mg LS220
plt.gca().xaxis.set_major_locator(locator)
plt.minorticks_on()
plt.xlabel(r"$\rho_{\mathrm{{b, max}}$ [$10^{15}$ g cm$^{-3}$]", labelpad=10)
plt.ylabel("$M_\mathrm{b} \,\, [M_\odot]$", labelpad=6)
plt.ylabel("$R_E [km]$", labelpad=6)
#plt.ylabel(r"$rpoe")

#fixExponentialAxes()
removeExponentialNotationOnAxis('x')
plt.show()
