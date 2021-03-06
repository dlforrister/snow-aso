import json

import pdal


class PdalPipeline(object):
    def __init__(self):
        self._workflow = {"pipeline": []}

    @property
    def workflow(self):
        return self._workflow

    def add(self, step):
        if isinstance(step, list):
            self.workflow["pipeline"].extend(step)
        else:
            self.workflow["pipeline"].append(step)

    def to_json(self):
        return json.dumps(self.workflow)

    def execute(self):
        pdal_process = pdal.Pipeline(self.to_json())
        pdal_process.validate()
        pdal_process.execute()

    @staticmethod
    def filter_smrf():
        return [
            {
                "type": "filters.smrf",
            },
            {
                "type": "filters.range",
                "limits": "Classification[2:2]"
            },
        ]

    @staticmethod
    def mask_casi(casi_file, surfaces='snow'):
        upper_limit = 1 if surfaces == 'snow' else 2
        return [
            {
                "type": "filters.colorization",
                "raster": casi_file,
                "dimensions": "Red:1"
            },
            {
                "type": "filters.range",
                "limits": "Red[0:{0}]".format(upper_limit)
            },
        ]

    @staticmethod
    def mask_envi(envi_file):
        return [
            {
                "type": "filters.colorization",
                "raster": envi_file,
                "dimensions": "Red:1"
            },
            {
                "type": "filters.range",
                "limits": "Red(2:255]"
            },
        ]

    @staticmethod
    def create_las(outfile):
        return [
            {
                "filename": outfile,
                "type": "writers.las",
                "compression": "laszip",
                "forward": "all",
                "dataformat_id": 0,
            }
        ]

    @staticmethod
    def create_dem(**kwargs):
        return [
            {
                "filename": kwargs['outfile'],
                "type": "writers.gdal",
                "bounds": kwargs['bounds'],
                "gdalopts": "t_srs=" + kwargs['epsg'],
                "gdaldriver": "GTiff",
                "resolution": "1.0",
                "output_type": "all",
            }
        ]
