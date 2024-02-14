import unittest
from unittest.mock import patch, MagicMock
from service import run_speed_test, insertIntoUsertest

class TestSpeedTest(unittest.TestCase):
    @patch('service.boto3.resource')
    @patch('service.requests.get')
    @patch('service.time.time')
    @patch('service.requests.post')
    def test_run_speed_test_and_insertIntoUsertest(self, mock_post, mock_time, mock_requests_get, mock_boto3_resource):
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
    def test_run_speed_test_integration(self):
        # Call the function to test
        download_speed, upload_speed = run_speed_test()

        # Assert that download and upload speeds are non-empty strings
        self.assertTrue(download_speed)
        self.assertTrue(upload_speed)
if __name__ == '__main__':
    unittest.main()
