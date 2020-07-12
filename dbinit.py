import pymongo
import csv

dbclient    = pymongo.MongoClient("mongodb://localhost:27017/")
dblist      = dbclient.list_database_names()

collection_arr = [
  { "name": "customers", "file": "./testdata/customers.csv"},
  { "name": "customer_companies", "file": "./testdata/customer_companies.csv"},
  { "name": "orders", "file": "./testdata/orders.csv"}
]

# Reset Data
def reset_data(dbselected):
    for coll_data_item in collection_arr:
        coll_name   = coll_data_item['name']
        coll        = dbselected[coll_name]
        coll.drop()

    import_data(dbselected)

# Import Data
def import_data(dbselected):
    for coll_data_item in collection_arr:
        coll_name   = coll_data_item['name']
        coll_file   = coll_data_item['file']
        csvfile     = open(coll_file, 'r')
        reader      = csv.DictReader(csvfile)

        import_data = []

        for row_data in reader:
            import_data.append(row_data)

        if len(import_data) > 0:
            coll = dbselected[coll_name]

            try:
              coll.insert_many(import_data)
            except:
              print("Error Inserting Data")

if "dbbackend" in dblist:
    print("DB Exist. Resetting Data")
    dbselected = dbclient["dbbackend"]

    reset_data(dbselected)
else:
    print("DB doesn't exist. Importing Data")
    dbselected = dbclient["dbbackend"]
    import_data(dbselected)
