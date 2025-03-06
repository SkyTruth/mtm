# Imports necessary Python libraries
import rasterio as rio
import fiona as fio
import copy
import affine
import click

# Allows for numerically small pixels (i.e. small georeferenced units)
affine.set_epsilon(1e-10)


def _cb_bidx(ctx, param, value):

    """
    Validates --bidx (band index) parameter
    """
    if value < 1:
        raise click.BadParameter("Band index must be >= 1")
    return value

# These decorators construct the command line interface
@click.command()
@click.argument("input_vector", required=True)
@click.argument("raster", required=True)
@click.argument("output_vector", required=True)
@click.option(
    "--bidx", type=click.INT, default=1, callback=_cb_bidx, show_default=True,
    help="Sample from this raster band."
)
@click.option(
    "--layer", help="Name of layer to process. If not specified, defaults to first."
)
@click.option(
    "--field", required=True, help="Place sampled values in this field."
)


def cli(input_vector, raster, output_vector, layer, bidx, field):

    """
    Samples vector points against a raster.
    """

    # Opens the input vector and the raster to sample against
    with fio.drivers(), rio.drivers(), fio.open(input_vector, layer=layer) as src, rio.open(raster) as rast:
        # Validate the input data to make sure sampling won't fail
        if src.schema['geometry'].lower() != "point":
            raise click.ClickException("Input vector must be a point layer.")
        if src.crs != rast.crs:
            raise click.ClickException("Input vector CRS and raster CRS must be the same.")
        if field in src.schema['properties']:
            raise click.ClickException("This field name already exits.")
        if bidx > rast.count:
            raise click.ClickException("This band doesn't exist.")

        # Constructs the output schema: layer type, CRS, field names, field types
        meta = copy.deepcopy(src.meta)
        if 'float' in rast.dtypes[bidx - 1].lower():
            field_type = 'float:10.4'
        else:
            field_type = 'int:10'
        meta['schema']['properties'][field] = field_type

        # Allows for operation on large rasters by sampling smaller windows (for smaller memory footprint)
        """
        x_min, y_min, x_max, y_max = src.bounds
        c_min, r_max = (x_min, y_min) * ~raster.affine
        c_max, r_min = (x_max, y_max) * ~raster.affine
        window = ((r_min, r_max),(c_min, c_max))

        ndvi = raster.read(1, window=window)
        aff = raster.window_transform(window)
        height, width = ndvi.shape
        """

        # Reads raster into numpy array
        data = rast.read(bidx)
        # Caches height and width to avoid sampling out of bounds
        height, width = data.shape

        # Opens output file, samples a feature and writes input metadata plus new feature into output file
        with fio.open(output_vector, 'w', **meta) as dst:
            for feature in src:
                feature['properties'][field] = None
                x, y = feature['geometry']['coordinates'][:2]
                col, row = (x,y) * ~rast.affine
                if 0 <= col < width and 0 <= row < height:
                    feature['properties'][field] = data[row][col].item()
                dst.write(feature)


if __name__ == "__main__":
    cli()
