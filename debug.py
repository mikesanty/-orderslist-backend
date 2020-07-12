import pymongo

dbclient    = pymongo.MongoClient("mongodb://localhost:27017/")

# URL PARAMS
search          = ''
page            = 1
itemsPerPage    = 10
sortBy          = 'created_at'
sortDesc        = -1
skip            = 10

# SORT
sort = dict()
sort[sortBy] = sortDesc

# QUERY
query = dbclient['dbbackend']['orders'].aggregate([
        {
        '$lookup': {
            'from': 'customers',
            'localField': 'customer_id',
            'foreignField': 'login',
            'as': 'customersdata'
        }
    }, {
        '$unwind': {
            'path': '$customersdata',
            'preserveNullAndEmptyArrays': True
        }
    }, {
        '$lookup': {
            'from': 'customer_companies',
            'localField': 'customer_companies.company_id',
            'foreignField': 'customers.company_id',
            'as': 'companydata'
        }
    }, {
        '$unwind': {
            'path': '$companydata',
            'preserveNullAndEmptyArrays': True
        }
    }, {
        '$project': {
            '_id': '$_id',
            'order_name'        : 1,
            'name'              : 1,
            'created_at'        : 1,
            'companydata'       : 1,
            'customersdata'     : 1,
        }
    }, {
        '$sort': {
            'created_at': -1
        }
    }, {
        '$facet': {
            'metadata': [
                {
                    '$count': 'total'
                }
            ],
            'data': [
                {
                    '$skip': skip
                }, {
                    '$limit': itemsPerPage
                }
            ]
        }
    }
])

orders_data = [doc for doc in query]

total_records = orders_data[0]['metadata'][0]['total']

# ORGANIZE OUTPUT
output = []
for orders_data_item in orders_data[0]['data']:
    output.append({
        'order_name'        : orders_data_item['order_name'],
        'cutomer_company'   : orders_data_item['companydata']['company_name'],
        'cutomer_name'      : orders_data_item['customersdata']['name'],
        'created_at'        : orders_data_item['created_at'],
        'delivered_amount'  : float(0.00),
        'total_amount'      : float(0.00)
    })

    print(output)
