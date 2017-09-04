from mongo_stats.utils import json_format


@json_format()
def collection_stats(db_client, databases):
    result = {}
    for database in databases:
        if database == "admin":
            continue
        db = db_client[database]

        result[database] = []

        collections = db.collection_names()
        for collection in collections:
            if collection == "users_raw":
                collstats = db.command("collstats", collection, scale=1024 * 1024)

                result[database].append({
                    "name": collection,
                    "ns": collstats["ns"],
                    "count": collstats["count"],
                    "avgObjSize": collstats["avgObjSize"],
                    "storageSize": collstats["storageSize"]
                })

    return result
