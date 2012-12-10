"""
Importing this file addresses the following issue:
'The problem is that multiprocessing must pickle things to sling them among processes,
 and bound methods are not picklable.
 The workaround (whether you consider it "easy" or not;-)
 is to add the infrastructure to your program to allow such methods to be pickled,
 registering it with the copy_reg standard library method.'
 See:
 http://stackoverflow.com/questions/1816958/cant-pickle-type-instancemethod-when-using-pythons-multiprocessing-pool-ma
"""
__author__ = 'jeff'

def _pickle_method(method):
    func_name = method.im_func.__name__
    obj = method.im_self
    cls = method.im_class
    return _unpickle_method, (func_name,obj,cls)

def _unpickle_method(func_name,obj,cls):
    for cls in cls.mro():
        try:
            func = cls.__dict__[func_name]
        except KeyError:
            pass
        else:
            break
    return func.__get__(obj,cls)

import copy_reg
import types

copy_reg.pickle(types.MethodType,_pickle_method,_unpickle_method)