import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from database.models import db_drop_and_create_all, setup_db, Drink
from auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

db_drop_and_create_all()
## ROUTES
@app.route('/drinks', methods=['GET'])
def get_drinks():
    try:
        drinks = Drink.query.all()
        shorted_drinks = [drk.short() for drk in drinks]
        print(shorted_drinks)
        return jsonify({ 
            "success": True,
            "drinks":  shorted_drinks
        })
    except Exception:
        abort(422)

@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_details(payload):
    try:
        drinks = Drink.query.all()
        long_drinks = [drk.long() for drk in drinks]
        return jsonify({ 
            "success": True,
            "drinks": [long_drinks]
        })
    except Exception:
        abort(422)

@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_new_drink(payload):
    try:   
        rqst = request.get_json()
        new_drink = Drink(title=rqst['title'], recipe=json.dumps(rqst['recipe']))
        new_drink.insert()
        return jsonify ({
            "success": True, 
            "drinks":  [new_drink.long()]
        })
    except Exception:
        abort(422)

@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drink(payload,id):
    id = request.view_args['id']
    drk = Drink.query.filter(Drink.id == id).one_or_none()
    if not drk:
        abort(404)
    try:
        rqst = request.get_json()
        drk.title = rqst['title']
        if 'recipe' in rqst:
            drk.recipe = json.dumps(req['recipe'])
        drk.update()
        return jsonify({
            'success': True,
            'drinks': [drk.long()]
        })
    except Exception:
        abort(422)

@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_requested_drink(payload,id):
    try:
        id = request.view_args['id']
        drk = Drink.query.filter(Drink.id == id).one_or_none()
        drk.delete()
        return jsonify({
            "success": True, 
            "delete": id
            })
    except Exception:
        abort(404)

## Error Handling
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

@app.errorhandler(404)
def unprocessable(error):
    return jsonify({
        "success": False, 
        "error": 404,
        "message": "resource not found"
    }), 404
  
@app.errorhandler(405)
def method_not_allowed(error):
     return jsonify({
         'error': 405,
         'success': False,
         'message': 'method not allowed'
     }), 405

@app.errorhandler(500)
def internal_server_error(error):
     return jsonify({
       'error': 500,
       'success': False,
       'message': 'server error'
     }), 500

@app.errorhandler(401)
def internal_server_error(error):
     return jsonify({
       'error': 401,
       'success': False,
       'message': 'unauthorized'
     }), 401

@app.errorhandler(AuthError)
def internal_auth_error(error):
    return jsonify({
       'error': error.error,
       'success': False,
       'message': error.status_code
     }), error.status_code