import os
from datetime import datetime

import fiona
from pyproj import Proj, Transformer, transform
from pystac import (
    STAC_IO,
    Asset,
    Catalog,
    CatalogType,
    Collection,
    Item,
    MediaType,
    SpatialExtent,
    utils,
)
from shapely.geometry import box
from shapely.ops import transform as shapely_transform
from spotstac.geobase_ftp import GeobaseSpotFTP
from spotstac.stac_templates import build_catalog
from spotstac.utils import bbox, read_remote_stacs, transform_geom, write_remote_stacs

STAC_IO.read_text_method = read_remote_stacs
STAC_IO.write_text_method = write_remote_stacs

GeobaseSTAC = build_catalog()

SPOT_SENSOR = {"S4": "SPOT 4", "S5": "SPOT 5"}


def create_item(name, feature, collection):
    """
    name: SPOT ID
    feature: geojson feature
    collection: pySTAC collection object
    Create a STAC item for SPOT
    """

    item = Item(
        id=name,
        geometry=feature["geometry"],
        bbox=list(bbox(feature)),
        properties={},
        datetime=datetime.strptime(name[14:22], "%Y%m%d"),
        collection=collection,
    )
    return item


def build_items(index_geom):
    """
    index_geom: fioan readable file (ex, shapefile)
    Build the STAC items
    """
    with fiona.open(index_geom) as src:
        src_crs = Proj(src.crs)
        dest_crs = Proj("WGS84")

        extent = box(*src.bounds)

        project = Transformer.from_proj(src_crs, dest_crs)
        catalog_bbox = shapely_transform(project.transform, extent)

        # build spatial extent for collection
        ortho_collection = GeobaseSTAC.get_child("canada_spot_orthoimages")
        ortho_collection.extent.spatial = SpatialExtent([list(catalog_bbox.bounds)])

        geobase = GeobaseSpotFTP()

        count = 0
        for f in src:
            feature_out = f.copy()

            new_coords = transform_geom(src_crs, dest_crs, f["geometry"]["coordinates"])
            feature_out["geometry"]["coordinates"] = new_coords

            name = feature_out["properties"]["NAME"]
            sensor = SPOT_SENSOR[name[:2]]

            new_item = create_item(name, feature_out, ortho_collection)

            for f in geobase.list_contents(name):
                # Add data to the asset
                spot_file = Asset(href=f, title=None, media_type="application/zip")

                file_key = f[-13:-4]  # image type
                new_item.add_asset(file_key, spot_file)

            # Add the thumbnail asset
            new_item.add_asset(
                key="thumbnail",
                asset=Asset(
                    href=geobase.get_thumbnail(name),
                    title=None,
                    media_type=MediaType.JPEG,
                ),
            )

            ortho_collection.add_item(new_item)

            count += 1
            print(f"{count}... {new_item.id}")


GeobaseSTAC.normalize_and_save("s3://geobase-spot", CatalogType.RELATIVE_PUBLISHED)
print("Finished")
