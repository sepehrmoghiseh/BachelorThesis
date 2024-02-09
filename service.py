import socket
from datetime import datetime
import time
import requests
import boto3
result_data = ''

def run_speed_test():
    SPEEDTEST_URL = "http://speedtest.ftp.otenet.gr/files/test1Mb.db"
    s3_resource = boto3.resource(
        's3',
        endpoint_url='https://openwrtt.s3.ir-thr-at1.arvanstorage.ir',
        aws_access_key_id='65a0c54d-5ad8-429b-989d-ea431d6c92aa',
        aws_secret_access_key='b0733d9e84cd241c1dced64bb8ebda629146eaa14af94751618879e7eeb2c32a'
    )

    bucket = s3_resource.Bucket('openwrtt')
    response = requests.get(SPEEDTEST_URL)
    start_time = time.time()
    bucket.put_object(
        ACL='private',
        Body=response.content,
        Key="s.db"
    )
    end_time = time.time()
    upload = 8 / (end_time - start_time)

    # Run speed test
    start_time = time.time()
    response = requests.get(SPEEDTEST_URL)
    end_time = time.time()

    # Calculate download speed in bps with two decimal places
    download_speed = 8 / (end_time - start_time)
    float_value = float(download_speed)
    formatted_download = format(float_value, ".2f")
    float_value = float(upload)
    formatted_upload = format(float_value, ".2f")
    insertIntoUsertest(formatted_download,formatted_upload)
    return f"{download_speed:.2f} Mbps", f"{upload:.2f} Mbps"

def insertIntoUsertest(download,upload):
    rpc_url = "http://192.168.1.1/cgi-bin/luci/rpc/sys?auth=" + result_data

    mac = "\'" + download + "\'"
    name = "\'" + upload + "\'"
    insert = "INSERT INTO userSpeedtest (download_speed, upload_speed) VALUES (" + mac + "," + name + ");"
    command = "sqlite3 database.db \"" + insert + "\""
    rpc_request = {"method": "exec", "params": [command]}
    requests.post(rpc_url, json=rpc_request).json()



def searchMac(mac):
    rpc_url = "http://192.168.1.1/cgi-bin/luci/rpc/sys?auth=" + result_data

    mac = "\'" + mac + "\'"
    search = "select * FROM devices WHERE mac_address = " + mac + ";"
    command = "sqlite3 database.db \"" + search + "\""
    rpc_request = {"method": "exec", "params": [command]}
    result = requests.post(rpc_url, json=rpc_request).json()
    if result["result"] != '':
        string = result['result'].find("|")
        return result['result'][string + 1:]
    else:
        return None

def searchIp(ip_address):
    host = what_device_is_connected(result_data)
    for key in host:
        if 'ipv4' in host[key]:
            if ip_address in host[key]['ipv4']:
                return searchMac(key)


def login(username, password):
    rpc_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "login",
        "params": [username, password]
    }
    response = requests.post("http://192.168.1.1/cgi-bin/luci/rpc/auth", json=rpc_request)
    global result_data
    result_data = response.json()['result']
    ip_address = get_local_ip()
    current_datetime = datetime.now()
    formatted_date = current_datetime.strftime("%a %b %d %H:%M:%S %Y")
    named = ""
    named = searchIp(ip_address)
    if named is None:
        addLoginInfo(ip_address, formatted_date)
    else:
        addLoginInfo(named[:-1], formatted_date)
    return result_data


def get_local_ip():
    try:
        # Create a socket and connect to an external server (doesn't actually send data)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except socket.error:
        return "Unable to retrieve IP address"


def getUser():
    rpc_url = "http://192.168.1.1/cgi-bin/luci/rpc/sys?auth=" + result_data
    rpc_request = {
        "method": "user.getuser",
        "params": [
            "0"
        ]
    }
    response = requests.post(rpc_url, json=rpc_request)
    user = response.json()['result']

    return user


def what_device_is_connected(result_data):
    rpc_url = "http://192.168.1.1/cgi-bin/luci/rpc/sys?auth=" + result_data
    rpc_request = {
        "method": "net.host_hints"
    }
    response = requests.post(rpc_url, json=rpc_request)
    hosts = response.json()['result']
    devices = {}

    for key in hosts:
        if key.lower() in stations():
            devices[key]=hosts[key]
        else:
            continue
    return devices
    # return devices


def changePasswordService(password):
    rpc_url = "http://192.168.1.1/cgi-bin/luci/rpc/sys?auth=" + result_data
    rpc_request = {
        "method": "user.setpasswd",
        "params": [
            "root", password
        ]
    }
    response = requests.post(rpc_url, json=rpc_request)


def logread():
    rpc_url = "http://192.168.1.1/cgi-bin/luci/rpc/sys?auth=" + result_data
    rpc_request = {"method": "exec", "params": ["logread"]}
    response = requests.post(rpc_url, json=rpc_request)
    log = response.json()['result']
    return log


def addLoginInfo(ip_address, date_formatted):
    rpc_url = "http://192.168.1.1/cgi-bin/luci/rpc/sys?auth=" + result_data
    rpc_request = {"method": "exec", "params": ["sqlite3 database.db \"SELECT COUNT(*) FROM loginInfo\""]}
    response = requests.post(rpc_url, json=rpc_request).json()
    if int(response['result']) > 10:
        rpc_request = {"method": "exec", "params": [
            "sqlite3 database.db \"DELETE FROM loginInfo WHERE id = (SELECT MIN(id) FROM loginInfo)\""]}
        requests.post(rpc_url, json=rpc_request).json()
    ip = "\'" + ip_address + "\'"
    date = "\'" + date_formatted + "\'"
    insert = "INSERT INTO loginInfo (ip, date) VALUES (" + ip + "," + date + ");"
    command = "sqlite3 database.db \"" + insert + "\""
    rpc_request = {"method": "exec", "params": [command]}
    requests.post(rpc_url, json=rpc_request).json()


def reportLogin():
    rpc_url = "http://192.168.1.1/cgi-bin/luci/rpc/sys?auth=" + result_data
    rpc_request = {"method": "exec", "params": ["sqlite3 database.db \"SELECT * FROM loginInfo\""]}
    return requests.post(rpc_url, json=rpc_request).json()['result']


def editName(name, mac):
    rpc_url = "http://192.168.1.1/cgi-bin/luci/rpc/sys?auth=" + result_data

    mac = "\'" + mac + "\'"
    name = "\'" + name + "\'"
    search = "select * FROM devices WHERE mac_address = " + mac + ";"
    command = "sqlite3 database.db \"" + search + "\""
    rpc_request = {"method": "exec", "params": [command]}
    result = requests.post(rpc_url, json=rpc_request).json()
    if result["result"] == '':
        insert = "INSERT INTO devices (mac_address, name) VALUES (" + mac + "," + name + ");"
        command = "sqlite3 database.db \"" + insert + "\""
        rpc_request = {"method": "exec", "params": [command]}
        requests.post(rpc_url, json=rpc_request).json()
    else:
        insert = "UPDATE devices SET name = " + name + " WHERE mac_address = " + mac + ";"
        command = "sqlite3 database.db \"" + insert + "\""
        rpc_request = {"method": "exec", "params": [command]}
        requests.post(rpc_url, json=rpc_request).json()


def deleteName(mac):
    rpc_url = "http://192.168.1.1/cgi-bin/luci/rpc/sys?auth=" + result_data
    mac = "\'" + mac + "\'"

    delete = "DELETE FROM devices WHERE mac_address = " + mac + ";"

    command = "sqlite3 database.db \"" + delete + "\""
    rpc_request = {"method": "exec", "params": [command]}
    requests.post(rpc_url, json=rpc_request).json()
def disconnect(mac):
    rpc_url = "http://192.168.1.1/cgi-bin/luci/rpc/sys?auth=" + result_data
    print(mac.lower())
    print("iw dev phy0-ap0 station del "+mac.lower())
    rpc_request = {"method": "exec", "params": ["iw dev phy0-ap0 station del "+mac.lower()]}
    requests.post(rpc_url, json=rpc_request).json()

def findName(mac):
    rpc_url = "http://192.168.1.1/cgi-bin/luci/rpc/sys?auth=" + result_data

    mac = "\'" + mac + "\'"
    search = "select * FROM devices WHERE mac_address = " + mac + ";"
    command = "sqlite3 database.db \"" + search + "\""
    rpc_request = {"method": "exec", "params": [command]}
    result = requests.post(rpc_url, json=rpc_request).json()
    if result['result']!= '':
        string=result['result'].find("|")
        return result['result'][string+1:]
    else:
        return None

def speedtestGateWay():
    rpc_url = "http://192.168.1.1/cgi-bin/luci/rpc/sys?auth=" + result_data
    rpc_request = {"method": "exec", "params": ["sqlite3 database.db \"SELECT COUNT(*) FROM speedtest\""]}
    response = requests.post(rpc_url, json=rpc_request).json()
    if int(response['result']) > 10:
        result=int(response['result'])-10
        rpc_request = {"method": "exec", "params": [
            "sqlite3 database.db \"DELETE FROM speedtest WHERE id IN (SELECT id FROM speedtest LIMIT "+str(result)+");\""]}
        requests.post(rpc_url, json=rpc_request).json()
    rpc_url = "http://192.168.1.1/cgi-bin/luci/rpc/sys?auth=" + result_data
    rpc_request = {"method": "exec", "params": ["sqlite3 database.db \"SELECT * FROM speedtest\""]}
    result= requests.post(rpc_url, json=rpc_request).json()['result']
    lines = result.splitlines()
    times=[]
    speeds=[]
    for line in lines:
        first = line.find("|")
        second = line.find("|", first + 1)
        speeds.append(float(line[second + 1:-1]))
        times.append(datetime.strptime(line[first + 1:second], "%Y-%m-%d %H:%M:%S"))



    # Show the plot
    return times, speeds

def userSpeedMat():
    rpc_url = "http://192.168.1.1/cgi-bin/luci/rpc/sys?auth=" + result_data
    rpc_request = {"method": "exec", "params": ["sqlite3 database.db \"SELECT COUNT(*) FROM userSpeedtest\""]}
    response = requests.post(rpc_url, json=rpc_request).json()
    if int(response['result']) > 10:
        result=int(response['result'])-10
        rpc_request = {"method": "exec", "params": [
            "sqlite3 database.db \"DELETE FROM userSpeedtest WHERE id IN (SELECT id FROM userSpeedtest LIMIT "+str(result)+");\""]}
        requests.post(rpc_url, json=rpc_request).json()
    rpc_url = "http://192.168.1.1/cgi-bin/luci/rpc/sys?auth=" + result_data
    rpc_request = {"method": "exec", "params": ["sqlite3 database.db \"SELECT * FROM userSpeedtest\""]}
    result = requests.post(rpc_url, json=rpc_request).json()['result']
    lines = result.splitlines()
    times = []
    speeds = []
    uploads=[]
    for line in lines:
        first = line.find("|")
        second = line.find("|", first + 1)
        third = line.find("|", second + 1)
        speeds.append(float(line[second + 1:third]))
        times.append(datetime.strptime(line[first + 1:second], "%Y-%m-%d %H:%M:%S"))
        uploads.append(float(line[third+1:]))
    return times, speeds,uploads

def usage():
    rpc_url = "http://192.168.1.1/cgi-bin/luci/rpc/sys?auth=" + result_data
    rpc_request = {"method": "exec", "params": ["sqlite3 database.db \"SELECT * FROM connected_clients\""]}
    result = requests.post(rpc_url, json=rpc_request).json()['result']
    lines = result.splitlines()
    times = []
    speeds = []
    for line in lines:
        first = line.find("|")
        print(line[:first])
        print(line[first + 1:])
        speeds.append(line[:first])
        times.append(int(line[first + 1:]))
    return times, speeds
def data_usage():
    rpc_url = "http://192.168.1.1/cgi-bin/luci/rpc/sys?auth=" + result_data
    rpc_request = {"method": "exec", "params": ["vnstat -u -i phy0-ap0"]}

    result = requests.post(rpc_url, json=rpc_request).json()['result']
    rpc_request = {"method": "exec", "params": ["vnstat -d -i phy0-ap0"]}

    result = requests.post(rpc_url, json=rpc_request).json()['result']

    lines = result.splitlines()
    lines = lines[5:-2]
    date=[]
    data_usages=[]
    for index, line in enumerate(lines):
        date.append(datetime.strptime(line[6:14], "%m/%d/%y"))
        first=line.find("|")
        sec=line.find("|",first+1)
        third=line.find("|",sec+1)
        if "MiB" in line[sec+1:third]:
            stripped_string = line[sec+1:third].strip()
            space_index = stripped_string.find(' ')
            float_string = stripped_string[:space_index]
            float_value = float(float_string)
            float_value=float_value*(2**-10)
            data_usages.append(float_value)

        elif "KiB" in line[sec+1:third] :
            stripped_string = line[sec + 1:third].strip()
            space_index = stripped_string.find(' ')
            float_string = stripped_string[:space_index]
            float_value = float(float_string)
            float_value=float_value*(2**-20)
            data_usages.append(float_value)
        else:
            stripped_string = line[sec + 1:third].strip()
            space_index = stripped_string.find(' ')
            float_string = stripped_string[:space_index]
            float_value = float(float_string)
            data_usages.append(float_value)
    return date,data_usages
def stations():
    rpc_url = "http://192.168.1.1/cgi-bin/luci/rpc/sys?auth=" + result_data
    rpc_request = {"method": "exec", "params": ["iw dev phy0-ap0 station dump"]}
    return requests.post(rpc_url, json=rpc_request).json()['result']



if __name__ == "__main__":
    result_data = login('root', 'admin')
