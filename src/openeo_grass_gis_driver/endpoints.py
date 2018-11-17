# -*- coding: utf-8 -*-
from .app import flask_api
from .capabilities import Capabilities, OutputFormats, ServiceTypes
from .data import Data
from .data_product_id import DataProductId
from .processes_process_id import ProcessesProcessId
from .processes import Processes
from .jobs import Jobs
from .jobs_job_id import JobsJobId
from .udf import Udf
from .udf_lang_udf_type import UdfType

__license__ = "Apache License, Version 2.0"
__author__ = "Sören Gebbert"
__copyright__ = "Copyright 2018, Sören Gebbert, mundialis"
__maintainer__ = "Soeren Gebbert"
__email__ = "soerengebbert@googlemail.com"


def create_endpoints():
    """Create all endpoints for the openEO Core API  wrapper

    :return:
    """
    flask_api.add_resource(Capabilities, '/')
    flask_api.add_resource(OutputFormats, '/output_formats')
    flask_api.add_resource(ServiceTypes, '/service_types')

    flask_api.add_resource(Data, '/data')
    flask_api.add_resource(DataProductId, '/data/<string:data_id>')

    flask_api.add_resource(Processes, '/processes')
    flask_api.add_resource(ProcessesProcessId, '/processes/<string:process_id>')

    flask_api.add_resource(Jobs, '/jobs')
    flask_api.add_resource(JobsJobId, '/jobs/<string:job_id>')

    flask_api.add_resource(Udf, '/udf')
    flask_api.add_resource(UdfType, '/udf/<string:lang>/<string:udf_type>')