from flask import Flask, jsonify, request
import sys
import re

from pymongo.mongo_client import MongoClient

sys.path.insert(0, "..")
import conf


app = Flask(__name__)
db = MongoClient(conf.DATABASE_SERVER, conf.DATABASE_PORT)


@app.route('/', methods=['GET'])
def index():
    return app.send_static_file('index.html')


@app.route('/seeds', methods=['GET'])
def seeds():
    page = int(request.args.get('page', default=0))
    filter = re.escape(request.args.get('filter', default=''))
    results_start_idx = page * conf.WEB_RESULTS_LIMIT
    results_end_idx = (page + 1) * conf.WEB_RESULTS_LIMIT
    seeds = list(db.dionysus.seeds.find({'domain': {'$regex': filter}}, {'_id': 0})[results_start_idx:results_end_idx])
    result = {
        'success': True,
        'code': 200,
        'status': 'Operation succeeded',
        'data': seeds,
    }
    return jsonify(result)


@app.route('/dnskey', methods=['GET'])
def dnskey():
    page = int(request.args.get('page', default=0))
    results_start_idx = page * conf.WEB_RESULTS_LIMIT
    results_end_idx = (page + 1) * conf.WEB_RESULTS_LIMIT
    dnskeys = list(db.dionysus.dnskey.find({}, {'_id': 0})[results_start_idx:results_end_idx])
    result = {
        'success': True,
        'code': 200,
        'status': 'Operation succeeded',
        'data': dnskeys,
    }
    return jsonify(result), 200


@app.errorhandler(404)
def not_found(e):
    result = {
        'success': False,
        'code': 404,
        'status': 'Path not found.'
    }
    return jsonify(result), 404


@app.errorhandler(500)
def server_error(e):
    result = {
        'success': False,
        'code': 500,
        'status': 'Error: %s' % e,
    }
    return jsonify(result), 500


if __name__ == '__main__':
    app.run(debug=False)
