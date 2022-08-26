# -*- coding: utf-8 -*-
"""
Created on Fri Aug 26 09:39:37 2022

@author: renkert2
"""
import pickle
import io

class RenameUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        renamed_module = module
        if module == "Param":
            renamed_module = "GraphTools_Phil_V2.OpenMDAO.PARAMS.Param"

        return super(RenameUnpickler, self).find_class(renamed_module, name)

def renamed_load(file_obj):
    return RenameUnpickler(file_obj).load()

def renamed_loads(pickled_bytes):
    file_obj = io.BytesIO(pickled_bytes)
    return renamed_load(file_obj)