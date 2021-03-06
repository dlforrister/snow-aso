import argparse
import os

import gdal

from basin_data import BASINS_BOUNDARIES, BASIN_EPSG
from pdal_pipeline import PdalPipeline

LAZ_MASKED_OUTFILE = '{0}_masked.laz'
LAZ_TO_DEM_OUTFILE = '{0}_1m.tif'
DEM_COMPRESSED_OUTFILE = '{0}_1m_c.tif'

SAVE_MESSAGE = 'Saved output to:\n  {0}\n'

parser = argparse.ArgumentParser()
parser.add_argument(
    '--lidar-laz',
    type=argparse.FileType('r'),
    help='Path to lidar point cloud',
    required=True
)
parser.add_argument(
    '--casi-mask',
    type=argparse.FileType('r'),
    help='Path to CASI mask',
    required=True
)
parser.add_argument(
    '--envi-mask',
    type=argparse.FileType('r'),
    help='Path to ENVI mask',
    required=True
)
parser.add_argument(
    '--basin',
    type=str,
    help='Basin boundaries',
    required=True,
    choices=BASINS_BOUNDARIES.keys()
)

if __name__ == '__main__':
    arguments = parser.parse_args()

    output_file = os.path.splitext(arguments.lidar_laz.name)[0]
    output_file = os.path.join(
        os.path.dirname(arguments.lidar_laz.name), output_file
    )

    mask_pipeline = PdalPipeline()

    print('Masking out vegetation')
    mask_pipeline.add(arguments.lidar_laz.name)
    mask_pipeline.add(PdalPipeline.mask_casi(
        arguments.casi_mask.name, surfaces='snow_rock'
    ))
    mask_pipeline.add(PdalPipeline.mask_envi(arguments.envi_mask.name))

    print('Filter to ground return only')
    mask_pipeline.add(PdalPipeline.filter_smrf())

    mask_pipeline.add(
        PdalPipeline.create_las(LAZ_MASKED_OUTFILE.format(output_file))
    )

    mask_pipeline.execute()
    print(SAVE_MESSAGE.format(LAZ_MASKED_OUTFILE.format(output_file)))
    del mask_pipeline

    print('Creating DEM')

    dem_pipeline = PdalPipeline()

    dem_pipeline.add(LAZ_MASKED_OUTFILE.format(output_file))
    dem_pipeline.add(PdalPipeline.mask_casi(arguments.casi_mask.name))
    dem_pipeline.add(PdalPipeline.create_dem(
        outfile=LAZ_TO_DEM_OUTFILE.format(output_file),
        bounds=BASINS_BOUNDARIES[arguments.basin],
        epsg=BASIN_EPSG[arguments.basin]
    ))

    print(SAVE_MESSAGE.format(LAZ_TO_DEM_OUTFILE.format(output_file)))

    dem_pipeline.execute()
    del dem_pipeline

    print('\nCompressing tif')

    gdal.Translate(
        DEM_COMPRESSED_OUTFILE.format(output_file),
        gdal.Open(LAZ_TO_DEM_OUTFILE.format(output_file), gdal.GA_ReadOnly),
        creationOptions=["COMPRESS=LZW", "TILED=YES",
                         "BIGTIFF=IF_SAFER", "NUM_THREADS=ALL_CPUS"]
    )

    print(SAVE_MESSAGE.format(DEM_COMPRESSED_OUTFILE.format(output_file)))
