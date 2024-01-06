from FlaskApp import *
import speedtest

result_data = ''

def run_speed_test():
    # Create a Speedtest object
    st = speedtest.Speedtest()

    # Get download speed in bits per second
    download_speed = st.download()

    # Get upload speed in bits per second
    upload_speed = st.upload()

    # Convert speeds to more human-readable units
    download_speed_mbps = download_speed / 10**6
    upload_speed_mbps = upload_speed / 10**6

    # Print the results
    return f"{download_speed_mbps:.2f} Mbps",f"{upload_speed_mbps:.2f} Mbps"
def login(username, password):
    rpc_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "login",
        "params": [username, password]
    }
    response = loginFlask(rpc_request)
    global result_data
    result_data = response.json()['result']

    return result_data


def getUser():
    rpc_url = "http://192.168.1.1/cgi-bin/luci/rpc/sys?auth=" + result_data
    rpc_request = {
        "method": "user.getuser",
        "params": [
            "0"
        ]
    }
    response = getUsers(rpc_url, rpc_request)
    user = response.json()['result']

    return user


def what_device_is_connected(result_data):
    rpc_url = "http://192.168.1.1/cgi-bin/luci/rpc/sys?auth=" + result_data
    rpc_request = {
        "method": "net.host_hints"
    }
    response = connectedDevice(rpc_url, rpc_request)
    hosts = response.json()['result']
    print(hosts)
    devices = {}

    for key in hosts:

        if 'name' in hosts[key]:
            if 'ipv4' in hosts[key]:
                if "OpenWrt" in hosts[key]['name']:
                    continue

                else:
                    devices[hosts[key]['name']] = {'ip': hosts[key]['ipv4'], 'mac': key}
        else:
            continue
    return hosts
    # return devices


def changePasswordService(password):
    rpc_url = "http://192.168.1.1/cgi-bin/luci/rpc/sys?auth=" + result_data
    rpc_request = {
        "method": "user.setpasswd",
        "params": [
            "root", password
        ]
    }
    response = changePasswordFlask(rpc_url, rpc_request)


if __name__ == "__main__":
    result_data = login('root', 'admin')
    run_speed_test()
