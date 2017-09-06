def collection_stats(db_client, databases):
    result = {}
    for database in databases:
        if database == "admin":
            continue
        db = db_client[database]

        result[database] = []

        collections = db.collection_names()
        for collection in collections:
            collstats = db.command("collstats", collection, scale=1024 * 1024)

            result[database].append({
                "name": collection,
                "ns": collstats["ns"],
                "count": collstats["count"],
                "avgObjSize": collstats.get("avgObjSize"),
                "storageSize": collstats["storageSize"]
            })

    return result
