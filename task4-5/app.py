# Task5  | Reviewed by Hassan Azam
# In inverse decorator, dictionary can be used instead of multiple if statements
# Usage of try catch block is good


from flask import Flask, request, jsonify
from functools import wraps
app = Flask(__name__)

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

@app.route('/calc', methods=['POST'])
@inverse
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
        return jsonify(response)

        

    except:
        response = { 'status': 500,
                     'message': 'Operator(op) or Operands(op1, op2) missing from the request' }
        return jsonify(response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
