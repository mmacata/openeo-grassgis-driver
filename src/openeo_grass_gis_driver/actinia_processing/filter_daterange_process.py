# -*- coding: utf-8 -*-
from random import randint
import json
from openeo_grass_gis_driver.actinia_processing.base import process_node_to_actinia_process_chain, PROCESS_DICT, \
    PROCESS_DESCRIPTION_DICT, ProcessNode
from openeo_grass_gis_driver.process_schemas import Parameter, ProcessDescription, ReturnValue
from openeo_grass_gis_driver.actinia_processing.actinia_interface import ActiniaInterface

__license__ = "Apache License, Version 2.0"
__author__ = "Sören Gebbert"
__copyright__ = "Copyright 2018, Sören Gebbert, mundialis"
__maintainer__ = "Soeren Gebbert"
__email__ = "soerengebbert@googlemail.com"

PROCESS_NAME = "filter_daterange"


def create_process_description():
    p_data = Parameter(description="Any openEO process object that returns raster datasets "
                                   "or space-time raster dataset",
                       schema={"type": "object", "format": "eodata"},
                       required=True)

    p_from = Parameter(description="The start date of the filter in YYYY-MM-DD HH:mm:SS format",
                       schema={"type": "string", "examples": ["2018-01-01 00:30:00"]},
                       required=True)

    p_to = Parameter(description="The end date of the filter in YYYY-MM-DD HH:mm:SS format",
                     schema={"type": "string", "examples": ["2018-01-01 00:30:00"]},
                     required=True)

    rv = ReturnValue(description="Processed EO data.",
                     schema={"type": "object", "format": "eodata"})

    examples = dict(simple={
        "filter_daterange_1": {
            "process_id": PROCESS_NAME,
            "arguments": {
                "data": {"from_node": "get_strds_data"},
                "from": "2001-01-01",
                "to": "2005-01-01",
            }
        }
    })

    pd = ProcessDescription(id=PROCESS_NAME,
                            description="Drops observations from a collection that have been "
                                        "captured between start and end date.",
                            summary="Drops observations from a collection",
                            parameters={"data": p_data, "from": p_from, "to": p_to},
                            returns=rv,
                            examples=examples)

    return json.loads(pd.to_json())


PROCESS_DESCRIPTION_DICT[PROCESS_NAME] = create_process_description()


def create__process_chain_entry(input_name, start_time, end_time, output_name):
    """Create a Actinia command of the process chain that uses t.rast.extract to create a subset of a strds

    :param strds_name: The name of the strds
    :param start_time:
    :param end_time:
    :return: A Actinia process chain description
    """
    location, mapset, datatype, layer_name = ActiniaInterface.layer_def_to_components(input_name)
    input_name = layer_name
    if mapset is not None:
        input_name = layer_name + "@" + mapset
    base_name = "%s_extract" % layer_name

    # Get info about the time series to extract its resolution settings and bbox
    rn = randint(0, 1000000)

    pc = {"id": "t_rast_extract_%i" % rn,
          "module": "t.rast.extract",
          "inputs": [{"param": "input", "value": input_name},
                     {"param": "where", "value": "start_time >= '%(start)s' "
                                                 "AND end_time <= '%(end)s'" % {"start": start_time, "end": end_time}},
                     {"param": "output", "value": output_name},
                     {"param": "expression", "value": "1.0 * %s" % input_name},
                     {"param": "basename", "value": base_name},
                     {"param": "suffix", "value": "num"}]}

    return pc


def get_process_list(node: ProcessNode):
    """Analyse the process description and return the Actinia process chain and the name of the processing result
    strds that was filtered by start and end date

    :param node: The process node
    :return: (output_names, actinia_process_list)
    """

    # Get the input description and the process chain to attach this process
    input_names, process_list = process_node_to_actinia_process_chain(node)
    output_names = []

    for input_name in node.get_parent_by_name(parent_name="data").output_names:

        location, mapset, datatype, layer_name = ActiniaInterface.layer_def_to_components(input_name)

        # Skip if the datatype is not a strds and put the input into the output
        if datatype and datatype != "strds":
            output_names.append(input_name)
            continue

        output_name = "%s_%s" % (layer_name, PROCESS_NAME)
        output_names.append(output_name)
        node.add_output(output_name)

        start_time = None
        end_time = None

        if "from" in node.arguments:
            start_time = node.arguments["from"]
        if "to" in node.arguments:
            end_time = node.arguments["to"]

        pc = create__process_chain_entry(input_name=input_name,
                                         start_time=start_time,
                                         end_time=end_time,
                                         output_name=output_name)
        process_list.append(pc)

    return output_names, process_list


PROCESS_DICT[PROCESS_NAME] = get_process_list
