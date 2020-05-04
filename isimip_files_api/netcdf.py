import numpy as np
import numpy.ma as ma


def copy_data(ds_in, ds_out, mask):
    # create dimensions
    for dimension_name, dimension in ds_in.dimensions.items():
        ds_out.createDimension(dimension_name, len(dimension) if not dimension.isunlimited() else None)

    # create variables
    for variable_name, variable in ds_in.variables.items():
        # try to get the fill value from the input variable
        try:
            fill_value = variable._FillValue
        except AttributeError:
            fill_value = None

        var = ds_out.createVariable(variable_name, variable.datatype, variable.dimensions,
                                    zlib=True, fill_value=fill_value)
        var.setncatts({k: v for k, v in variable.__dict__.items() if not k.startswith('_')})

        if variable_name in ['lat', 'lon', 'time']:
            var[:] = variable[:]
        else:
            var_mask = np.broadcast_to(mask, var.shape)
            var[...] = ma.masked_array(variable[...], var_mask)

    # copy global attributes
    ds_in.setncatts(ds_out.__dict__)
