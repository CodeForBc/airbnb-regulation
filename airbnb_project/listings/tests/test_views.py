from django.test import TestCase
from unittest.mock import patch, MagicMock
from django.urls import reverse


class HarvestListingsTest(TestCase):

    @patch('listings.views.reactor')  # Mock the reactor
    @patch('listings.views.Thread')  # Mock the Thread
    @patch('listings.views.CrawlerRunner')  # Mock the Scrapy runner
    def test_harvest_listings_success(self, mock_runner, mock_thread, mock_reactor):
        """
        Test the harvest_listings view for a successful start.
        """
        # Ensure reactor is not running and scraping is not in progress
        mock_reactor.running = False
        mock_thread_instance = MagicMock()  # Create a mock thread instance
        mock_thread.return_value = mock_thread_instance

        # Make a GET request to the harvest_listings view
        response = self.client.get(reverse('harvest_listings'))

        # Check that a new thread was started
        mock_thread.assert_called_once()

        # Ensure the Scrapy runner has been called
        mock_runner.assert_called_once()

        # Validate response status code and content
        self.assertEqual(response.status_code, 202)
        self.assertEqual(response.content.decode(), "Harvesting process started")

    @patch('listings.views.is_scraping', new=True)  # Simulate is_scraping being True
    def test_harvest_listings_already_running(self):
        """
        Test the harvest_listings view when the spider is already running.
        """
        # Make a GET request to the harvest_listings view
        response = self.client.get(reverse('harvest_listings'))

        # Validate response status code and content
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.content.decode(), "A harvesting process is already running")

    @patch('listings.views.reactor')  # Mock the reactor
    @patch('listings.views.is_scraping', new=False)  # Simulate is_scraping being False
    def test_harvest_listings_failure(self, mock_reactor):
        """
        Test the harvest_listings view when an exception occurs.
        """
        mock_reactor.running = False
        # Force an exception to simulate failure during Scrapy runner start
        with patch('listings.views.CrawlerRunner', side_effect=Exception("Crawler error")):
            response = self.client.get(reverse('harvest_listings'))

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.content.decode(), "Failed to start harvesting process")
