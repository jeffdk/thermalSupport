

def latexField(field):
    """
    Takes a field label from sql database and translates it to a good form
    for displaying in the paper
    """
    assert isinstance(field, str), "Input field must be a string!"

    fieldsDict = {'gravMass': r"$M_g/M_\odot$",
                  'edMax': r"$E_{\mathrm{max}}$ $\mathrm{g/cm}^3$",
                  'a': r"$\tilde{A}$",
                  'arealR': "Circumferential Radius (km)",
                  'omega_c': r"$\Omega_c$ (rad/s)",
                  'rpoe': r"$r_p/r_e$"}

    return fieldsDict[field]