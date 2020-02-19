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

from geobase_ftp import GeobaseSpotFTP
from stac_templates import build_catalog
from utils import bbox, transform_geom, read_remote_stacs, write_remote_stacs


# STAC_IO.read_text_method = read_remote_stacs
# STAC_IO.write_text_method = write_remote_stacs


class Geobase(object):

    SPOT_SENSOR = {"S4": "SPOT 4", "S5": "SPOT 5"}

    def __init__(self, index_geom):
        self.index_geom = index_geom
        self.geobase_stac = build_catalog()

    def create_item(self, name, feature, collection):
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

    def get_extents(self, src, spot_sensor):
        with NamedTemporaryFile(suffix=".shp", delete=False) as f:
            with fiona.open(
                f, "w", driver=src.driver, crs=src.crs, schema=src.schema
            ) as subset:
                for i in src:
                    if i["properties"].get("NAME").startswith(spot_sensor):
                        subset.write(i)
                subset_extent = box(*subset.bounds)

        return subset_extent

    def build_items(self):
        """
        index_geom: fiona readable file (ex, shapefile)
        Build the STAC items
        """

        with fiona.open(self.index_geom) as src:
            src_crs = Proj(src.crs)
            dest_crs = Proj("WGS84")
            project = Transformer.from_proj(src_crs, dest_crs)

            # Get differnt SPOT data extents
            s4 = self.get_extents(src, "S4")
            s5 = self.get_extents(src, "S5")

            # build spatial extent for collections
            s4_bbox = shapely_transform(project.transform, s4)
            SPOT4Collection = self.geobase_stac.get_child(
                "canada_spot4_orthoimages", True
            )
            SPOT4Collection.extent.spatial = SpatialExtent([list(s4_bbox.bounds)])

            s5_bbox = shapely_transform(project.transform, s5)
            SPOT5Collection = self.geobase_stac.get_child(
                "canada_spot5_orthoimages", True
            )
            SPOT5Collection.extent.spatial = SpatialExtent([list(s5_bbox.bounds)])

            geobase = GeobaseSpotFTP()

            count = 0
            for f in src:
                feature_out = f.copy()

                new_coords = transform_geom(
                    src_crs, dest_crs, f["geometry"]["coordinates"]
                )
                feature_out["geometry"]["coordinates"] = new_coords

                name = feature_out["properties"]["NAME"]
                sensor = self.SPOT_SENSOR[name[:2]]

                """
                Create a new item under the appropriate catalog sorted by year-month
                """

                # Build item with appropriate references
                if name[:2] == "S4":
                    new_item = self.create_item(name, feature_out, SPOT4Collection)
                else:
                    new_item = self.create_item(name, feature_out, SPOT5Collection)

                for f in geobase.list_contents(name):
                    # Add data to the asset
                    spot_file = Asset(
                        href=f"http://{f}", title=None, media_type="application/zip"
                    )

                    file_key = f[-13:-4]  # image type
                    new_item.add_asset(file_key, spot_file)

                # Add the thumbnail asset
                new_item.add_asset(
                    key="thumbnail",
                    asset=Asset(
                        href=f"http://{geobase.get_thumbnail(name)}",
                        title=None,
                        media_type=MediaType.JPEG,
                    ),
                )

                if name[:2] == "S4":
                    if (
                        SPOT4Collection.get_child(f"{name[:2]}_{name[14:-4]}", True)
                        is None
                    ):
                        year_cat = Catalog(
                            id=f"{name[:2]}_{name[14:-4]}",
                            description=f"{sensor} images for {name[14:-4:]}",
                            title=f"{name[:2]}_{name[14:-4:]}",
                            stac_extensions=None,
                        )
                    else:
                        year_cat = SPOT4Collection.get_child(
                            f"{name[:2]}_{name[14:-4]}", True
                        )
                    year_cat.add_item(new_item)
                    SPOT4Collection.add_child(year_cat)
                else:
                    if (
                        SPOT5Collection.get_child(f"{name[:2]}_{name[14:-4]}", True)
                        is None
                    ):
                        year_cat = Catalog(
                            id=f"{name[:2]}_{name[14:-4:]}",
                            description=f"{sensor} images for {name[14:-4:]}",
                            title=f"{name[:2]}_{name[14:-4]}",
                            stac_extensions=None,
                        )
                    else:
                        year_cat = SPOT5Collection.get_child(
                            f"{name[:2]}_{name[14:-4]}", True
                        )
                    year_cat.add_item(new_item)
                    SPOT5Collection.add_child(year_cat)

                count += 1
                print(f"{count}... {new_item.id}")
        return self.geobase_stac


# build_items(
#     "/Users/james/PycharmProjects/Prescient/PCI/NAPL/geobase_index/GeoBase_Orthoimage_Index/GeoBase_Orthoimage_Index.shp"
# )
a = Geobase(
    "/Users/james/PycharmProjects/Prescient/PCI/NAPL/geobase_index/GeoBase_Orthoimage_Index/test.shp"
)
a.build_items()
print(a)
a.geobase_stac.normalize_and_save(
    "https://geobase-spot-dev.s3.amazonaws.com", CatalogType.ABSOLUTE_PUBLISHED
)
# GeobaseSTAC = build_items(
#     "/Users/james/PycharmProjects/Prescient/PCI/NAPL/geobase_index/GeoBase_Orthoimage_Index/test.shp",
#     GeobaseSTAC,
# )
# GeobaseSTAC.normalize_and_save(
#     "https://geobase-spot-dev.s3.amazonaws.com", CatalogType.ABSOLUTE_PUBLISHED
# )
print("Finished")
