from flask  import Flask,request,jsonify
from flask_restful import Resource, Api, reqparse
import pandas as pd
import ast
import json

from order import OrderParser
from requestrespone import *
from BillOptimizer import *

from flask import Flask, jsonify


from OpenSSL import SSL



app = Flask(__name__)
api = Api(app)

class Users(Resource):
    # methods go here
    def get(self):
        data = pd.read_csv('users.csv')  # read CSV
        data = data.to_dict()  # convert dataframe to dictionary
        return {'data': data}, 200  # return data and 200 OK code

    def post(self):
        #form=request.form
        data=request.get_json()

        print(data)
        return {'data': "abc"}, 200  # return data with 200 OK
    pass
    
class Locations(Resource):
    def post(self):
        #form=request.form
        data=request.get_json()

        print(data)
        return {'data': "abc"}, 200  # return data with 200 OK
    pass

class Dishes(Resource):
    def post(self):
        jsonstring=request.get_json()
        print("request json")
        print(jsonstring)
        billObject:BillRequestObject = BillRequest(jsonstring).getObject()
        
        opimizer=BillOptimizer(billObject.shipping_fee,billObject.orders,billObject.vouchers)
        result=opimizer.optimize()

        print(result)
        # json_data=json.dumps(result,default=lambda o: o.__dict__)
        jsonObject=json.loads(result)
        return jsonObject,200
   
    pass

api.add_resource(Dishes, '/dishes')  # '/users' is our entry point for Users
api.add_resource(Users, '/users')  # '/users' is our entry point for Users
api.add_resource(Locations, '/locations')  # and '/locations' is our entry point for Locations
if __name__ == '__main__':
    app.run(host='0.0.0.0')  # run our Flask app