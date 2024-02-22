import math
from typing import Dict, Union, List

from ..database import MongoConnection
import importlib.metadata

version = importlib.metadata.version("sorting-hat-step")


def oid_query(db: MongoConnection, oid: str) -> Union[str, None]:
    """
    Query the database and check if any of the OIDs is already in database

    :param db: Database connection
    :param oid: oid of any survey

    :return: existing aid if exists else is None
    """
    found = db.database["object"].find_one({"_id": oid}, {"aid": 1}) #creo que hay que hacer esto
    if found:
        return found["aid"]
    return None


def conesearch_query(
    db: MongoConnection, ra: float, dec: float, radius: float
) -> Union[str, None]:
    """
    Query the database and check if there is an alerce_id
    for the specified coordinates and search radius

    :param db: Database connection
    :param ra: first coordinate argument (RA)
    :param dec: first coordinate argument (Dec)
    :param radius: search radius (arcsec)

    :return: existing aid if exists else is None
    """
    found = db.database["object"].find_one(
        {
            "loc": {
                "$nearSphere": {
                    "$geometry": {
                        "type": "Point",
                        "coordinates": [ra - 180, dec],
                    },
                    "$maxDistance": math.radians(radius / 3600) * 6.3781e6,
                },
            },
        },
        {"aid": 1},
    )
    if found:
        return found["aid"]
    return None


def update_query(db: MongoConnection, records: List[dict]):
    """
    Insert or update the records in a dictionary. Pushes the oid array to
    oid column.

    :param db: Database connection
    :param records: Records containing _id and oid fields to insert or update
    """
    for record in records:
        query = {"_id": record["_id"]}
        new_value = {
            "$set": {"aid": record["aid"]},
        }
        db.database["object"].find_one_and_update(
            query, new_value, upsert=True, return_document=True
        )
