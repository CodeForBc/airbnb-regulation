from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch
import logging


class HarvestListingsViewTest(TestCase):
    """
    Test suite for the 'harvest_listings' view. This suite tests the behavior of the
    view when the `run_harvest_task` is successful and when it fails.

    Methods:
        setUp: Prepares the test client and necessary components.
        test_harvest_listings_success: Tests successful execution of the harvest task.
        test_harvest_listings_failure: Tests failure in executing the harvest task.
    """

    def setUp(self):
        """
        Sets up the necessary components for each test, including the test client,
        the URL for the 'harvest_listings' view, and the logger.
        """
        self.client = Client()
        self.url = reverse('harvest_listings')
        self.logger = logging.getLogger('django')

    @patch('listings.tasks.run_harvest_task.delay')
    def test_harvest_listings_success(self, mock_run_harvest_task):
        """
        Tests that the 'harvest_listings' view returns a 202 status code when the
        harvest task is successfully initiated and the task is called once.

        Args:
            mock_run_harvest_task: Mocked version of the 'run_harvest_task.delay' method.
        """
        mock_run_harvest_task.return_value = None
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 202)
        mock_run_harvest_task.assert_called_once()

    @patch('listings.tasks.run_harvest_task.delay')
    def test_harvest_listings_failure(self, mock_run_harvest_task):
        """
        Tests that the 'harvest_listings' view returns a 500 status code when the
        harvest task fails, and logs the error appropriately.

        Args:
            mock_run_harvest_task: Mocked version of the 'run_harvest_task.delay' method.
        """
        mock_run_harvest_task.side_effect = Exception("Task failure")

        with self.assertLogs('django', level='ERROR') as log:
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, 500)
            mock_run_harvest_task.assert_called_once()
