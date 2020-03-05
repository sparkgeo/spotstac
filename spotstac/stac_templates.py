from datetime import datetime

from pystac import (
    Band,
    STAC_IO,
    Catalog,
    Collection,
    Extent,
    Link,
    Provider,
    SpatialExtent,
    TemporalExtent,
)

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

SPOT_4_COMMON = {
    "bands": [
        Band(
            name="Panchromatic",
            description="Panchromatic: 610-680 nm",
            common_name="panchromatic",
        ),
        Band(name="Green", description="Green: 500-590 nm", common_name="green"),
        Band(name="Red", description="Red: 610-680 nm", common_name="red"),
        Band(
            name="Near Infrared",
            description="Near Infrared: 780-890 nm",
            common_name="nir",
        ),
        Band(
            name="ShortWave Infrared",
            description="ShortWave Infrared: 1580-1750 nm",
            common_name="swir",
        ),
    ],
    "platform": "SPOT 4",
    "gsd": 20,  # Nominal GSD, see STAC spec
    "instrument": "HRVIR",
}

SPOT_5_COMMON = {
    "bands": [
        Band(
            name="Panchromatic",
            description="Panchromatic: 480-710 nm",
            common_name="panchromatic",
        ),
        Band(name="Green", description="Green: 500-590 nm", common_name="green"),
        Band(name="Red", description="Red: 610-680 nm", common_name="red"),
        Band(
            name="Near Infrared",
            description="Near Infrared: 780-890 nm",
            common_name="nir",
        ),
        Band(
            name="ShortWave Infrared",
            description="ShortWave Infrared: 1580-1750 nm",
            common_name="swir",
        ),
    ],
    "platform": "SPOT 5",
    "gsd": 20,  # Nominal GSD, see STAC spec
    "instrument": "HVG",
}

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
        title="STAC for Geobase",
        stac_extensions=None,
    )

    OrthoCatalog = Catalog(
        id="canada_spot_orthoimages",
        description="Orthoimages of Canada 2005-2010",
        title="STAC SPOT Orthoimages",
        stac_extensions=None,
    )

    SPOT4Collection = Collection(
        id="canada_spot4_orthoimages",
        description="SPOT 4 Orthoimages of Canada 2005-2010",
        extent=SpotExtents,
        title="SPOT 4 Orthoimages of Canada 2005-2010",
        stac_extensions=["eo"],
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
        stac_extensions=["eo"],
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
