import numpy as np
import numpy.ma as ma


def copy_data(ds, co, mask):
    # create dimensions
    for dimension_name, dimension in ds.dimensions.items():
        co.createDimension(dimension_name, len(dimension) if not dimension.isunlimited() else None)

    # create variables
    for variable_name, variable in ds.variables.items():
        var = co.createVariable(variable_name, variable.datatype, variable.dimensions, zlib=True)
        var.setncatts(variable.__dict__)

        if variable_name in ['lat', 'lon', 'time']:
            var[:] = variable[:]
        else:
            var_mask = np.broadcast_to(mask, var.shape)
            var[...] = ma.masked_array(variable[...], var_mask)

    # copy global attributes
    co.setncatts(ds.__dict__)
