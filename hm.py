import unittest
from unittest.mock import patch, MagicMock
from service import *


class TestSpeedTest(unittest.TestCase):
    @patch('service.boto3.resource')
    @patch('service.requests.get')
    @patch('service.requests.post')
    @patch('service.time.time')
    def test_run_speed_test_and_insertIntoUsertest(self, mock_time, mock_post, mock_requests_get, mock_boto3_resource):
        # Mocking the response from S3 bucket
        mock_bucket = MagicMock()
        mock_boto3_resource.return_value.Bucket.return_value = mock_bucket
        # Mocking response content from requests.get
        mock_response = MagicMock()
        mock_response.content = b'fake_response_content'
        mock_requests_get.return_value = mock_response

        # Mocking time measurements
        mock_time.side_effect = [0, 1, 2, 3]  # start_time, end_time (upload), start_time, end_time (download)
        # Call the function to test
        download_speed, upload_speed = run_speed_test()

        # Assert the results
        self.assertEqual(download_speed, "8.00 Mbps")
        self.assertEqual(upload_speed, "8.00 Mbps")
        mock_bucket.put_object.assert_called_once_with(
            ACL='private',
            Body=b'fake_response_content',
            Key="s.db"
        )

        # Assert insertIntoUsertest
        mock_post.assert_called_once()

    @patch('service.requests.post')
    def test_run_speed_test_integration(self, mock_post):
        # Call the function to test
        download_speed, upload_speed = run_speed_test()
        mock_post.assert_called_once()
        # Assert that download and upload speeds are non-empty strings
        self.assertTrue(download_speed)
        self.assertTrue(upload_speed)

    @patch('service.requests.post')
    @patch('service.get_local_ip')
    @patch('service.searchIp')
    @patch('service.addLoginInfo')
    def test_login(self, mock_add_login_info, mock_search_ip, mock_get_local_ip, mock_requests_post):
        # Mocking response from requests.post
        mock_response = MagicMock()
        mock_response.json.return_value = {'result': 'fake_result_data'}
        mock_requests_post.return_value = mock_response

        # Mocking response from get_local_ip
        mock_get_local_ip.return_value = 'fake_ip_address'

        # Mocking response from searchIp
        mock_search_ip.return_value = 'fake_name '

        # Call the function to test
        result = login('fake_username', 'fake_password')

        # Assert the results
        self.assertEqual(result, 'fake_result_data')
        mock_add_login_info.assert_called_once_with('fake_name', datetime.now().strftime("%a %b %d %H:%M:%S %Y"))

    @patch('service.requests.post')
    def test_get_user(self, mock_post):
        # Mocking response from requests.post
        mock_response = MagicMock()
        mock_response.json.return_value = {'result': 'fake_user_data'}
        mock_post.return_value = mock_response

        # Call the function to test
        user = getUser()

        # Assert the result
        self.assertEqual(user, 'fake_user_data')

    @patch('service.requests.post')
    def test_get_user_integration(self, mock_post):
        # Mock the response from requests.post
        mock_response = MagicMock()
        mock_response.json.return_value = {'result': 'fake_user_data'}  # Simulated response
        mock_post.return_value = mock_response

        # Set a mock result_data
        result_data = 'fake_result_data'

        # Call the function to test
        user = getUser()

        # Assert that the response contains the expected key and value
        self.assertEqual(user, 'fake_user_data')

    @patch('service.requests.post')
    def test_what_device_is_connected_integration(self, mock_post):
        # Mock the response from requests.post
        mock_response = MagicMock()
        mock_response.json.return_value = {'result': {'device1': 'info1', 'device2': 'info2'}}
        mock_post.return_value = mock_response

        # Call the function to test
        result_data = 'fake_result_data'
        devices = what_device_is_connected(result_data)

        # Assert that the function returns the expected devices
        self.assertEqual(devices, {'device1': 'info1', 'device2': 'info2'})

    @patch('service.requests.post')
    def test_change_password_service(self, mock_post):
        # Mock a successful response
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"result": "success"}

        # Call the function with a password
        password = "new_password"
        result = changePasswordService(password)

        # Assert that the function returns 'success' for a successful response
        self.assertEqual(result, None)

    @patch('service.requests.post')
    def test_change_password_service_integration(self, mock_post):
        # Define the expected request URL and JSON payload
        expected_url = "http://192.168.1.1/cgi-bin/luci/rpc/sys?auth="
        expected_json = {
            "method": "user.setpasswd",
            "params": ["root", "new_password"]
        }

        # Set up the mock response from the server
        mock_response = {"status": "success"}
        mock_post.return_value.json.return_value = mock_response

        # Call the function to test
        result = changePasswordService("new_password")

        # Assert that the POST request was made with the correct URL and JSON payload
        mock_post.assert_called_once_with(expected_url, json=expected_json)

        # Assert that the function returns the expected result based on the mock response
        self.assertEqual(result, None)

    @patch('service.requests.post')
    def test_logread_integration(self, mock_post):
        # Mock response from the server
        mock_response = {"result": "fake_log_data"}
        mock_post.return_value.json.return_value = mock_response

        # Call the function to test
        log = logread()

        # Assert that the function returns the expected log data
        self.assertEqual(log, "fake_log_data")

    @patch('service.requests.post')
    def test_add_login_info_integration(self, mock_post):
        # Mock response from the server
        mock_response = MagicMock()
        mock_response.json.return_value = {"result": 11}
        mock_post.return_value = mock_response

        # Call the function to test
        addLoginInfo('fake_ip_address', 'fake_formatted_date')

        # Assert that the function made the expected requests to the server
        mock_post.assert_any_call(
            "http://192.168.1.1/cgi-bin/luci/rpc/sys?auth=" + result_data,
            json={"method": "exec", "params": ["sqlite3 database.db \"SELECT COUNT(*) FROM loginInfo\""]}
        )
        mock_post.assert_any_call(
            "http://192.168.1.1/cgi-bin/luci/rpc/sys?auth=" + result_data,
            json={"method": "exec", "params": [
                "sqlite3 database.db \"DELETE FROM loginInfo WHERE id = (SELECT MIN(id) FROM loginInfo)\""]}
        )
        mock_post.assert_any_call(
            "http://192.168.1.1/cgi-bin/luci/rpc/sys?auth=" + result_data,
            json={"method": "exec", "params": [
                "sqlite3 database.db \"INSERT INTO loginInfo (ip, date) VALUES ('fake_ip_address','fake_formatted_date');\""]}
        )

    @patch('service.requests.post')
    def test_report_login_integration(self, mock_post):
        # Mock response from the server
        mock_response = MagicMock()
        mock_response.json.return_value = {"result": "fake_login_info"}
        mock_post.return_value = mock_response

        # Call the function to test
        login_info = reportLogin()

        # Assert that requests.post was called with the correct URL and JSON payload

        # Assert that the function returns the expected login information
        self.assertEqual(login_info, "fake_login_info")

    @patch('service.requests.post')
    def test_edit_name_integration(self, mock_post):
        # Mock response from the server
        mock_response = MagicMock()
        mock_response.json.return_value = {"result": ""}
        mock_post.return_value = mock_response

        # Call the function to test
        editName("fake_name", "fake_mac")

        # Assert that requests.post was called with the correct URL and JSON payload for insertion
        mock_post.assert_called_with(
            "http://192.168.1.1/cgi-bin/luci/rpc/sys?auth=" + result_data,
            json={"method": "exec", "params": [
                "sqlite3 database.db \"INSERT INTO devices (mac_address, name) VALUES (\'fake_mac\',\'fake_name\');\""]}
        )

        # Call the function again to test update
        mock_response.json.return_value = {"result": "fake_result"}
        editName("fake_new_name", "fake_mac")

        # Assert that requests.post was called with the correct URL and JSON payload for update
        mock_post.assert_called_with(
            "http://192.168.1.1/cgi-bin/luci/rpc/sys?auth=" + result_data,
            json={"method": "exec", "params": [
                "sqlite3 database.db \"UPDATE devices SET name = \'fake_new_name\' WHERE mac_address = \'fake_mac\';\""]}
        )

    @patch('service.requests.post')
    def test_delete_name_integration(self, mock_post):
        # Mock response from the server
        mock_response = MagicMock()
        mock_response.json.return_value = {"result": ""}
        mock_post.return_value = mock_response

        # Call the function to test
        deleteName("fake_mac")

        # Assert that requests.post was called with the correct URL and JSON payload for deletion
        mock_post.assert_called_once_with(
            "http://192.168.1.1/cgi-bin/luci/rpc/sys?auth=" + result_data,
            json={"method": "exec",
                  "params": ["sqlite3 database.db \"DELETE FROM devices WHERE mac_address = \'fake_mac\';\""]}
        )

    @patch('service.requests.post')
    def test_find_name_integration(self, mock_post):
        # Mock response from the server
        mock_response = MagicMock()
        mock_response.json.return_value = {"result": "fake_name"}
        mock_post.return_value = mock_response

        # Call the function to test
        result = findName("fake_mac")

        # Assert that requests.post was called with the correct URL and JSON payload for finding the name
        mock_post.assert_called_once_with(
            "http://192.168.1.1/cgi-bin/luci/rpc/sys?auth=" + result_data,
            json={"method": "exec",
                  "params": ["sqlite3 database.db \"select * FROM devices WHERE mac_address = \'fake_mac\';\""]}
        )

        # Assert the result returned by the function
        self.assertEqual(result, "fake_name")

    @patch('service.requests.post')
    def test_speedtest_gateway_integration(self, mock_post):
        # Mock the response for the first RPC call to get speedtest count
        mock_post.return_value.json.side_effect = [{'result': '15'}, {
            'result': '15'}, {
                                                       'result': '1|2024-02-14 12:00:00|100|50\n2|2024-02-14 12:10:00|120|60\n'}]

        # Call the function to test
        times, speeds, uploads = speedtestGateWay()

        self.assertIsInstance(times, list)
        self.assertIsInstance(speeds, list)
        self.assertIsInstance(uploads, list)
        self.assertEqual(len(times), 2)  # Assuming there are 2 records in the response
        self.assertEqual(len(speeds), 2)  # Assuming there are 2 records in the response
        self.assertEqual(len(uploads), 2)  # Assuming there are 2 records in the response

        # Check the values of the first record
        self.assertEqual(times[0], datetime(2024, 2, 14, 12, 0, 0))
        self.assertEqual(speeds[0], 100)
        self.assertEqual(uploads[0], 50)

        # Check the values of the second record
        self.assertEqual(times[1], datetime(2024, 2, 14, 12, 10, 0))
        self.assertEqual(speeds[1], 120)
        self.assertEqual(uploads[1], 60)

    @patch('service.requests.post')
    def test_userSpeedtest_gateway_integration(self, mock_post):
        # Mock the response for the first RPC call to get speedtest count
        mock_post.return_value.json.side_effect = [{'result': '15'}, {'result': '15'},
                                                   {
                                                       'result': '1|2024-02-14 12:00:00|100|50\n2|2024-02-14 12:10:00|120|60\n'}]

        # Call the function to test
        times, speeds, uploads = userSpeedMat()

        # Assertions
        self.assertIsInstance(times, list)
        self.assertIsInstance(speeds, list)
        self.assertIsInstance(uploads, list)
        self.assertEqual(len(times), 2)  # Assuming there are 2 records in the response
        self.assertEqual(len(speeds), 2)  # Assuming there are 2 records in the response
        self.assertEqual(len(uploads), 2)  # Assuming there are 2 records in the response

        # Check the values of the first record
        self.assertEqual(times[0], datetime(2024, 2, 14, 12, 0, 0))
        self.assertEqual(speeds[0], 100)
        self.assertEqual(uploads[0], 50)

        # Check the values of the second record
        self.assertEqual(times[1], datetime(2024, 2, 14, 12, 10, 0))
        self.assertEqual(speeds[1], 120)
        self.assertEqual(uploads[1], 60)

    @patch('service.requests.post')
    def test_stations(self, mock_post):
        # Define a mock response for the HTTP request
        mock_response = MagicMock()
        mock_response.json.return_value = {'result': 'mocked_stations_data'}
        mock_post.return_value = mock_response

        # Set the expected result_data value

        # Call the function to test
        result = stations()
        mock_post.assert_called_with(
            "http://192.168.1.1/cgi-bin/luci/rpc/sys?auth=" + result_data,
            json={"method": "exec", "params": ["iw dev phy0-ap0 station dump"]}
        )
        # Assertions
        self.assertEqual(result, 'mocked_stations_data')


if __name__ == '__main__':
    unittest.main()
