from matplotlib import pyplot as plt
import matplotlib
import numpy


def latexField(field):
    """
    Takes a field label from sql database and translates it to a good form
    for displaying in the paper
    """
    assert isinstance(field, str), "Input field must be a string!"

    fieldsDict = {'gravMass': r"$M_g \, [M_\odot]$",
                  'edMax': r"$E_{\mathrm{max}}$ $[\mathrm{g/cm}^3]$",
                  'a': r"$\tilde{A}$",
                  'arealR': "Circumferential Radius (km)",
                  'omega_c': r"$\Omega_c$ (rad/s)",
                  'rpoe': r"$r_p/r_e$",
                  'shed': "Mass Shed Parameter",
                  'ToverW': r"$T/|W|$"}

    return fieldsDict[field]


def fixExponentialAxes(fixCbar=False):
    """
    Removes the x 10 ^ pow on axes tick labels and
    appends / 10 ^ pow to axes labels
    """  # TODO: IMPLEMENT FIXCBAR
    x1, x2, y1, y2 = plt.axis()
    xlabel = plt.axes().xaxis.get_label_text()
    ylabel = plt.axes().yaxis.get_label_text()
    if numpy.log10(y2) > 2:
        scalePower = int(numpy.log10(y2))
        ylocs, ylabs = plt.yticks()
        plt.ylabel(ylabel + '/$10^{' + str(scalePower) + '}$', labelpad=12)
        plt.yticks(ylocs, map(lambda y: "%.1f" % y, ylocs / numpy.power(10.0, scalePower)))
    if numpy.log10(x2) > 2:
        scalePower = int(numpy.log10(x2))
        xlocs, xlabs = plt.xticks()
        #plt.xlabel(xlabel + '/$10^{' + str(scalePower) + '}$', labelpad=12)
        plt.xticks(xlocs, map(lambda x: "%.1f" % x, xlocs / numpy.power(10.0, scalePower)))
    if fixCbar:  # DOESNT WORK YET
        cbar = plt.colorbar()
        ticks = cbar.ax.get_yticklabels()
        print ticks, max(ticks)


def removeExponentialNotationOnAxis(axis):
    """

    """
    assert axis == 'x' or axis == 'y'
    if axis == 'x':
        xlocs, xlabs = plt.xticks()
        plt.xticks(xlocs, map(lambda x: '%.1f' % x, xlocs))
    if axis == 'y':
        ylocs, ylabs = plt.yticks()
        plt.yticks(ylocs, map(lambda y: '%.0f' % y, ylocs))
        pass


def fixScientificNotation(num):
    """
    Given a number, returns a latex string leading digit \times 10^power
    e.g. in 1e+13, out "$1 \times 10^{13}$"
    """
    power = int(numpy.log10(num))

    leading = str(numpy.round(num/10**power*10))[0]
    second = str(numpy.round(num/10**power*10))[1]
    third = str(numpy.round(num/10**power*100))[2]

    return r"$%s.%s%s\times10^{%s}$" % (leading, second, third, power)