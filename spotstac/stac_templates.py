from datetime import datetime

from pystac import (
    STAC_IO,
    Catalog,
    Collection,
    Extent,
    Link,
    Provider,
    SpatialExtent,
    TemporalExtent,
)

SPOT_SENSOR = {"S4": "SPOT 4", "S5": "SPOT 5"}

SpotProviders = [
    Provider(
        "Government of Canada",
        "Natural Resources; Strategic Policy and Results Sector",
        ["licensor", "processor"],
        "https://open.canada.ca/data/en/dataset/d799c202-603d-4e5c-b1eb-d058803f80f9",
    ),
    Provider(
        "Sparkgeo",
        "info@sparkegeo.com",
        ["processor", "host"],
        "https://www.sparkgeo.com",
    ),
    Provider(
        "PCI Geomatics",
        "info@pci.com",
        ["processor", "host"],
        "https://www.pcigeomatics.com",
    ),
]

SpotExtents = Extent(
    SpatialExtent([[0.0, 0.0, 0.0, 0.0]]),
    TemporalExtent(
        [
            [
                datetime.strptime("2005-05-01", "%Y-%m-%d"),
                datetime.strptime("2010-10-31", "%Y-%m-%d"),
            ]
        ]
    ),
)


GeobaseLicense = Link(
    "license",
    "https://open.canada.ca/en/open-government-licence-canada",
    "text",
    "Open Government Licence Canada",
)

### STAC ORGANIZATION ###


def build_catalog():
    GeobaseCatalog = Catalog(
        id="Geobase",
        description="STAC Catalog for Geobase",
        title="test",
        stac_extensions=None,
    )

    OrthoCatalog = Catalog(
        id="canada_spot_orthoimages",
        description="Orthoimages of Canada 2005-2010",
        title="TEST",
        stac_extensions=None,
    )

    SPOT4Collection = Collection(
        id="canada_spot4_orthoimages",
        description="SPOT 4 Orthoimages of Canada 2005-2010",
        extent=SpotExtents,
        title="SPOT 4 Orthoimages of Canada 2005-2010",
        stac_extensions=None,
        license="Proprietery",
        keywords="SPOT, Geobase, orthoimages",
        version="0.0.2",
        providers=SpotProviders,
    )

    SPOT5Collection = Collection(
        id="canada_spot5_orthoimages",
        description="SPOT 5 Orthoimages of Canada 2005-2010",
        extent=SpotExtents,
        title="SPOT 5 Orthoimages of Canada 2005-2010",
        stac_extensions=None,
        license="Proprietery",
        keywords="SPOT, Geobase, orthoimages",
        version="0.0.2",
        providers=SpotProviders,
    )

    GeobaseCatalog.add_child(OrthoCatalog)
    SPOT5Collection.add_link(GeobaseLicense)
    SPOT4Collection.add_link(GeobaseLicense)
    OrthoCatalog.add_child(SPOT4Collection)
    OrthoCatalog.add_child(SPOT5Collection)
    return GeobaseCatalog
