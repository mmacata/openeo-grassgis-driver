# -*- coding: utf-8 -*-
from random import randint
from .base import analyse_process_graph, PROCESS_DICT, PROCESS_DESCRIPTION_DICT
from .actinia_interface import ActiniaInterface

__license__ = "Apache License, Version 2.0"
__author__ = "Sören Gebbert"
__copyright__ = "Copyright 2018, Sören Gebbert, mundialis"
__maintainer__ = "Soeren Gebbert"
__email__ = "soerengebbert@googlemail.com"

PROCESS_NAME = "get_data"

DOC = {
    "name": PROCESS_NAME,
    "summary": "Returns a single dataset that is available in the /data endpoint for processing",
    "description": "This process returns a raster-, a vector- or a space-time raster datasets "
                   "that is available in the /data endpoint.",
    "parameters":
        {
            "data_id":
                {
                    "description": "The identifier of a single raster-, vector- or space-time raster dataset",
                    "schema":
                        {
                            "type": "string",
                            "examples": ["nc_spm_08.landsat.raster.lsat5_1987_10",
                                         "nc_spm_08.PERMANENT.vector.lakes",
                                         "ECAD.PERMANENT.strds.temperature_1950_2017_yearly"]
                        }
                }
        },
    "returns":
        {
            "description": "Processed EO data.",
            "schema":
                {
                    "type": "object",
                    "format": "eodata"
                }
        },
    "examples": [
        {
            "process_id": PROCESS_NAME,
            "data_id": "nc_spm_08.landsat.raster.lsat5_1987_10"
        },
        {
            "process_id": PROCESS_NAME,
            "data_id": "nc_spm_08.PERMANENT.vector.lakes",
        },
        {
            "process_id": PROCESS_NAME,
            "data_id": "ECAD.PERMANENT.strds.temperature_1950_2017_yearly"
        }
    ]
}

PROCESS_DESCRIPTION_DICT[PROCESS_NAME] = DOC


def create_process_chain_entry(input_name):
    """Create a Actinia process description that uses t.rast.series to create the minimum
    value of the time series.

    :param input_time_series: The input time series name
    :param output_map: The name of the output map
    :return: A Actinia process chain description
    """

    location, mapset, datatype, layer_name = ActiniaInterface.layer_def_to_components(input_name)
    input_name = layer_name
    if mapset is not None:
        input_name = layer_name + "@" + mapset

    rn = randint(0, 1000000)

    pc = {}

    if datatype == "raster":
        pc = {"id": "r_info_%i"%rn,
              "module": "r.info",
              "inputs": [{"param": "map", "value": input_name},],
              "flags": "g"}
    elif datatype == "vector":
        pc = {"id": "v_info_%i"%rn,
              "module": "v.info",
              "inputs": [{"param": "map", "value": input_name},],
              "flags": "g"}
    elif datatype == "strds":
        pc = {"id": "t_info_%i"%rn,
              "module": "t.info",
              "inputs": [{"param": "input", "value": input_name},],
              "flags": "g"}
    else:
        raise Exception("Unsupported datatype")

    return pc


def get_process_list(process):
    """Analyse the process description and return the Actinia process chain and the name of the processing result

    :param process: The process description
    :return: (output_names, actinia_process_list)
    """

    input_names, process_list = analyse_process_graph(process)
    output_names = []

    # First analyse the data entrie
    if "data_id" not in process:
        raise Exception("Process %s requires parameter <data_id>" % PROCESS_NAME)

    output_names.append(process["data_id"])

    pc = create_process_chain_entry(input_name=process["data_id"])
    process_list.append(pc)

    # Then add the input to the output
    for input_name in input_names:

        # Create the output name based on the input name and method
        output_name = input_name
        output_names.append(output_name)

    return output_names, process_list


PROCESS_DICT[PROCESS_NAME] = get_process_list
