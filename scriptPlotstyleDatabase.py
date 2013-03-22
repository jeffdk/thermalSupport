
class eosPrescription(object):

    def __init__(self, paramsDict):
        """
        Params dict are the values corresponding to this eosPrescription
        """
        self.name = "Unnamed"


def symbolFromDBentry(paramsDict):
    prescriptionParameters = ('T', 'rollMid', 'rollScale', 'eosTmin',
                              'fixedTarget', 'fixedQuantity')
    assert all([key in paramsDict for key in prescriptionParameters]), \
        "Must specify all eosPrescription related parameters!"
