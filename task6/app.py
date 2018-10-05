from flask import Flask, request, jsonify
from functools import wraps
from pymongo import MongoClient

app = Flask(__name__)

myclient = MongoClient("mongodb://localhost:27017/")

mydb = myclient["mydatabase"]
mycol = mydb["calculations"]

@app.route('/')
def hello():
    return "Hello World"

def inverse(func):
    @wraps(func)

    def decorated_function(*args, **kwargs):

        try:
            op = request.get_json()["op"]

            if op == "+":
                op = "-"
            elif op == "-":
                op = "+"
            elif op == "/":
                op = "*"
            elif op == "*":
                op = "/"


            request.get_json()["op"] = op

            return func(*args, **kwargs)

        except:
            response = {"message": "Operation not supported"}
            return jsonify(response)

    return decorated_function


def arithmaticOperation(op1, op2, op):
    if op == "+":
        return op1 + op2
    if op == "-":
        return op1 - op2
    if op == "*":
        return op1 * op2
    if op == "/":
        return op1/op2

def allowedOperation(op):
    allowedOps = ["+", "-", "*", "/"]
    if op in allowedOps:
        return True
    return False

def getDB():
    for x in mycol.find():
        print(x)


@app.route('/calc', methods=['POST'])
def calc():

    data = request.get_json()

    try:
        op1 = data["op1"]
        op2 = data["op2"]
        op = data["op"]
        

        if not allowedOperation(op):
            response = { 'status': 501,
                         'message': 'This operation ({}) is not supported by the API' .format(op)}
            return jsonify(response)

        result = arithmaticOperation(op1, op2, op)
        response = { 'status': 200,
                     'result': result }

        mydict = { "op": op, "op1": op1, "op2": op2, "result": result }
        x = mycol.insert_one(mydict)
        print ("{} inserted successfully\n" .format(x))
        getDB()

        return jsonify(response)

        

    except:
        response = { 'status': 500,
                     'message': 'Operator(op) or Operands(op1, op2) missing from the request' }
        return jsonify(response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
