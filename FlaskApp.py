import requests
from flask import Flask

app = Flask(__name__)


@app.route('/login', methods=["POST"])
def loginFlask(rpc_request):
    response = requests.post("http://192.168.1.1/cgi-bin/luci/rpc/auth", json=rpc_request)
    return response


@app.route('/show-network', methods=["POST"])
def showNetwork(url, rpc_request):
    response = requests.post(url, json=rpc_request)

    return response


@app.route('/show-connected-device', methods=["POST"])
def connectedDevice(url, rpc_request):
    response = requests.post(url, json=rpc_request)

    return response


@app.route('/user', methods=['POST'])
def getUsers(rpc_url, rpc_request):
    response = requests.post(rpc_url, json=rpc_request)

    return response


@app.route('/password', methods=['POST'])
def changePasswordFlask(rpc_url, rpc_request):
    response = requests.post(rpc_url, json=rpc_request)

    return response


if __name__ == '__main__':
    app.run(debug=True)
