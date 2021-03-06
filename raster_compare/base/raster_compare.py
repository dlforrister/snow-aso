import os
import sys

import gdal

from base.raster_file import RasterFile


class RasterCompare(object):
    def __init__(self, **kwargs):
        self.base_path = kwargs['base_path']
        self.output_path = kwargs['output_path']
        self.lidar_dem = kwargs['lidar_dem']
        self.sfm_dem = kwargs['sfm_dem']
        self.shape_file = kwargs['shape_file']

    @property
    def base_path(self):
        return self._base_path

    @base_path.setter
    def base_path(self, path):
        self._base_path = self.check_path(os.path.join(path, ''))

    @property
    def lidar_dem(self):
        return self._lidar_dem

    @lidar_dem.setter
    def lidar_dem(self, path):
        self._lidar_dem = self.check_path(path)

    @property
    def sfm_dem(self):
        return self._sfm_dem

    @sfm_dem.setter
    def sfm_dem(self, path):
        self._sfm_dem = self.check_path(path)

    @property
    def output_path(self):
        return self._output_path

    @output_path.setter
    def output_path(self, path):
        output_path = os.path.join(self.base_path, path, '')
        if not os.path.exists(output_path):
            os.mkdir(output_path)
        self._output_path = output_path

    @property
    def shape_file(self):
        return self._shape_file

    @shape_file.setter
    def shape_file(self, path):
        if path is not None:
            self._shape_file = self.check_path(path)
        else:
            self._shape_file = None

    def check_path(self, path):
        if hasattr(self, 'base_path'):
            _path = os.path.join(self.base_path, path)
        else:
            _path = path
        if not os.path.exists(_path):
            print('** ERROR **\n  Given file or path missing: ' + _path + '\n')
            sys.exit()
        return _path

    @staticmethod
    def crop_to_shape(raster_file, shape_file):
        output_file = raster_file.replace('.tif', '_cropped.tif')

        if not os.path.exists(output_file):
            print('Cropping raster:\n   ' + raster_file +
                  '\nto shape:\n   ' + shape_file + '\n')
            warped = gdal.Warp(
                '', raster_file,
                format='MEM', dstAlpha=True, cropToCutline=True,
                cutlineDSName=shape_file
            )
            gdal.Translate(
                output_file, warped,
                creationOptions=["COMPRESS=LZW", "TILED=YES",
                                 "BIGTIFF=IF_SAFER", "NUM_THREADS=ALL_CPUS"]
            )
            del warped

        return output_file

    def prepare(self):
        if self.shape_file:
            self.lidar_dem = self.crop_to_shape(self.lidar_dem, self.shape_file)
            self.sfm_dem = self.crop_to_shape(self.sfm_dem, self.shape_file)

    def file_args(self):
        return dict(
            lidar=RasterFile(self.lidar_dem),
            sfm=RasterFile(self.sfm_dem),
            output_path=self.output_path
        )
