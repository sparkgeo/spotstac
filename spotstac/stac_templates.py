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
        "PCI Geomatics", "info@pci.com", ["processor"], "https://www.pcigeomatics.com"
    ),
    Provider(
        "Sparkgeo",
        "info@sparkegeo.com",
        ["processor", "host"],
        "https://www.sparkgeo.com",
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
    "platform": "SPOT 4",
    "instruments": ["HRVIR"],
    "constellation": "SPOT",
    "eo:gsd": 20,  # Nominal GSD, see STAC spec
    "eo:bands": [
        Band(
            name="Panchromatic", description="Panchromatic: 610-680 nm", common_name="pan"
        ).to_dict(),
        Band(
            name="Green", description="Green: 500-590 nm", common_name="green"
        ).to_dict(),
        Band(name="Red", description="Red: 610-680 nm", common_name="red").to_dict(),
        Band(
            name="Near Infrared",
            description="Near Infrared: 780-890 nm",
            common_name="nir",
        ).to_dict(),
        Band(
            name="ShortWave Infrared",
            description="ShortWave Infrared: 1580-1750 nm",
            common_name="swir",
        ).to_dict(),
    ],
}

SPOT_5_COMMON = {
    "platform": "SPOT 5",
    "instruments": ["HVG"],
    "constellation": "SPOT",
    "eo:gsd": 20,  # Nominal GSD, see STAC spec
    "eo:bands": [
        Band(
            name="Panchromatic",
            description="Panchromatic: 480-710 nm",
            common_name="panchromatic",
        ).to_dict(),
        Band(
            name="Green", description="Green: 500-590 nm", common_name="green"
        ).to_dict(),
        Band(name="Red", description="Red: 610-680 nm", common_name="red").to_dict(),
        Band(
            name="Near Infrared",
            description="Near Infrared: 780-890 nm",
            common_name="nir",
        ).to_dict(),
        Band(
            name="ShortWave Infrared",
            description="ShortWave Infrared: 1580-1750 nm",
            common_name="swir",
        ).to_dict(),
    ],
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
        stac_extensions=["commons"],
        license="Proprietery",
        keywords="SPOT, Geobase, orthoimages",
        version="0.0.3",
        providers=SpotProviders,
        properties=SPOT_4_COMMON,
    )

    SPOT5Collection = Collection(
        id="canada_spot5_orthoimages",
        description="SPOT 5 Orthoimages of Canada 2005-2010",
        extent=SpotExtents,
        title="SPOT 5 Orthoimages of Canada 2005-2010",
        stac_extensions=["commons"],
        license="Proprietery",
        keywords="SPOT, Geobase, orthoimages",
        version="0.0.3",
        providers=SpotProviders,
        properties=SPOT_5_COMMON,
    )

    GeobaseCatalog.add_child(OrthoCatalog)
    SPOT5Collection.add_link(GeobaseLicense)
    SPOT4Collection.add_link(GeobaseLicense)
    OrthoCatalog.add_child(SPOT4Collection)
    OrthoCatalog.add_child(SPOT5Collection)
    return GeobaseCatalog
