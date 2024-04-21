from flask import Blueprint, jsonify

bp = Blueprint("tests", __name__)

@bp.route('/test/data', methods=['GET'])
def get_data():
    data = {'message': 'Hello from Flask!'}
    return jsonify(data)

