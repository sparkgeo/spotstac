import os
from datetime import datetime
from tempfile import NamedTemporaryFile

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

import tomic
from spotstac.geobase_ftp import GeobaseSpotFTP
from spotstac.stac_templates import build_catalog
from spotstac.utils import bbox, transform_geom

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


def build_collections(src, spot_sensor):
    with NamedTemporaryFile(suffix=".shp", delete=False) as f:
        with fiona.open(
            f, "w", driver=src.driver, crs=src.crs, schema=src.schema
        ) as subset:
            for i in src:
                if i["properties"].get("NAME").startswith(spot_sensor):
                    subset.write(i)
    return subset


def build_items(index_geom):
    """
    index_geom: fiona readable file (ex, shapefile)
    Build the STAC items
    """

    with fiona.open(index_geom) as src:
        src_crs = Proj(src.crs)
        dest_crs = Proj("WGS84")
        project = Transformer.from_proj(src_crs, dest_crs)

        # Get differnt SPOT data
        s4 = build_collections(src, "S4")
        s5 = build_collections(src, "S4")

        # build spatial extent for collections
        s4_extent = box(**s4.bounds)
        s4_bbox = shapely_transform(project.transform, s4_extent)
        SPOT4Collection = GeobaseSTAC.get_child("canada_spot4_orthoimages")
        SPOT4Collection.extent.spatial = SpatialExtent([list(s4_bbox.bounds)])

        s5_extent = box(**s5.bounds)
        s5_bbox = shapely_transform(project.transform, s5_extent)
        SPOT5Collection = GeobaseSTAC.get_child("canada_spot5_orthoimages")
        SPOT5Collection.extent.spatial = SpatialExtent([list(s5_bbox.bounds)])

        geobase = GeobaseSpotFTP()

        count = 0
        for f in src:
            feature_out = f.copy()

            new_coords = transform_geom(src_crs, dest_crs, f["geometry"]["coordinates"])
            feature_out["geometry"]["coordinates"] = new_coords

            name = feature_out["properties"]["NAME"]
            sensor = SPOT_SENSOR[name[:2]]

            if name[:2] == "S4":
                new_item = create_item(name, feature_out, SPOT4Collection)
            else:
                new_item = create_item(name, feature_out, SPOT5Collection)

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

            if name[:2] == "S4":
                SPOT4Collection.add_item(new_item)
                # TODO: Parse out each year and add them to a separete catalog
            else:
                SPOT5Collection.add_item(new_item)

            count += 1
            print(f"{count}... {new_item.id}")


build_items(
    "/Users/james/PycharmProjects/Prescient/PCI/NAPL/geobase_index/GeoBase_Orthoimage_Index/GeoBase_Orthoimage_Index.shp"
)
GeobaseSTAC.normalize_and_save(
    "https://geobase-spot-dev.s3.amazonaws.com", CatalogType.ABSOLUTE_PUBLISHED
)
print("Finished")
