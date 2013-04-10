from matplotlib import pyplot as plt
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


def fixExponentialAxes():
    """
    Removes the x 10 ^ pow on axes tick labels and
    appends / 10 ^ pow to axes labels
    """
    x1, x2, y1, y2 = plt.axis()
    xlabel = plt.axes().xaxis.get_label_text()
    ylabel = plt.axes().yaxis.get_label_text()
    print xlabel, ylabel
    if numpy.log10(y2) > 2:
        scalePower = int(numpy.log10(y2))
        ylocs, ylabs = plt.yticks()
        plt.ylabel(ylabel + '/$10^{' + str(scalePower) + '}$', labelpad=12)
        plt.yticks(ylocs, map(lambda y: "%.1f" % y, ylocs / numpy.power(10.0, scalePower)))
    if numpy.log10(x2) > 2:
        scalePower = int(numpy.log10(x2))
        xlocs, xlabs = plt.xticks()
        plt.xlabel(xlabel + '/$10^{' + str(scalePower) + '}$', labelpad=12)
        plt.xticks(xlocs, map(lambda x: "%.1f" % x, xlocs / numpy.power(10.0, scalePower)))
