from flask import Flask
from flask import jsonify
from flask import request
from flask_cors import CORS
from flask_pymongo import PyMongo

app = Flask(__name__)
CORS(app)

#DB CONNECTION
app.config['MONGO_DBNAME']  = 'dbbackend'
app.config['MONGO_URI']     = 'mongodb://localhost:27017/dbbackend'

mongo = PyMongo(app)

@app.route('/', methods=['GET'])
def get_orders():
    # URL PARAMS
    search          = request.args.get('search')
    page            = int(request.args.get('page'))
    itemsPerPage    = int(request.args.get('itemsPerPage'))
    sortBy          = request.args.get('sortBy')
    sortDesc        = int(request.args.get('sortDesc'))
    skip            = (itemsPerPage * page) if page > 1 else 0

    # SORT
    sort = dict()
    sort[sortBy] = sortDesc


    # QUERY
    query = mongo.db.orders.aggregate([
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
            '$group': {
                '_id': '$_id',
                'order_name': {
                    '$first': '$order_name'
                },
                'companydata': {
                    '$first': '$companydata'
                },
                'customersdata': {
                    '$first': '$customersdata'
                },
                'created_at': {
                    '$first': '$created_at'
                }
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
            '$sort': sort
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

    total_records_count = orders_data[0]['metadata'][0]['total']

    # ORGANIZE OUTPUT
    output = []
    for orders_data_item in orders_data[0]['data']:
        output.append({
            'order_name'        : orders_data_item['order_name'],
            'cutomer_company'   : orders_data_item['companydata']['company_name'],
            'cutomer_name'      : orders_data_item['customersdata']['name'],
            'created_at'        : orders_data_item['created_at'],
            'delivered_amount'  : '-',
            'total_amount'      : '-'
        })

    return jsonify({
        'search' : search,
        'pagination' : {
            'page'          : page,
            'itemsPerPage'  : itemsPerPage,
            'sortBy'        : sortBy,
            'sortDesc'      : sortDesc,
            'total_records' : total_records_count
        },
        'data' : {
            'items' : output
        }
    })


if __name__ == '__main__':
    app.run(debug=True)
