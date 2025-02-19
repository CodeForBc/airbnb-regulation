from django.test import TestCase
from listings.listing_models import Listing
from listings.harvester_app.harvester.pipelines import DjangoORMPipeline
from unittest.mock import Mock
import logging

class DjangoORMPipelineTest(TestCase):

    def setUp(self):
        # Mock spider to test logging and other interactions
        self.spider = Mock()
        self.spider.logger = logging.getLogger('test_logger')  # Add a valid logger here
        self.pipeline = DjangoORMPipeline()

    def test_process_item_creates_new_listing(self):
        # Simulate the item scraped by the spider
        item = {
            'airbnb_listing_id': '12345',
            'name': 'Test Listing',
            'title': 'Beautiful Apartment',
            'baths': '2',  # Converted to string
            'beds': '3',  # Converted to string
            'latitude': '49.2827',  # Converted to string
            'longitude': '-123.1207',  # Converted to string
            'person_capacity': '5',  # Converted to string
            'registration_number': 'ABC123',
            'room_type': 'Entire home/apt',
            'location': 'Downtown Vancouver',
            'bath_is_shared': False,  # Keep this as boolean
            'baths_text': '2 baths'
        }

        # Process the item through the pipeline
        self.pipeline.process_item(item, self.spider)

        # Assert that a new listing was created in the database
        self.assertEqual(Listing.objects.count(), 1)
        listing = Listing.objects.get(airbnb_listing_id='12345')
        self.assertEqual(listing.name, 'Test Listing')
        self.assertEqual(listing.beds, 3)  # Update assertion to compare strings
        self.assertEqual(listing.person_capacity, 5)  # Update assertion to compare strings

    # def test_process_item_skips_existing_listing(self):
    #     # Create a listing in the database
    #     Listing.objects.create(
    #         airbnb_listing_id='12345',
    #         name='Existing Listing',
    #         title='Old Apartment',
    #         baths=2,
    #         beds=3,
    #         latitude='49.2827',
    #         longitude='-123.1207',
    #         person_capacity=5,
    #         registration_number='DEF456',
    #         room_type='Entire home/apt',
    #         location='Downtown Vancouver',
    #         is_bath_shared=False,
    #         baths_text='2 baths'
    #     )
    #
    #     # Simulate the same item scraped by the spider
    #     item = {
    #         'airbnb_listing_id': '12345',
    #         'name': 'Test Listing',
    #         'title': 'Beautiful Apartment',
    #         'baths': 2,
    #         'beds': 3,
    #         'latitude': '49.2827',
    #         'longitude': '-123.1207',
    #         'person_capacity': 5,
    #         'registration_number': 'ABC123',
    #         'room_type': 'Entire home/apt',
    #         'location': 'Downtown Vancouver',
    #         'bath_is_shared': False,
    #         'baths_text': '2 baths'
    #     }
    #
    #     # Process the item through the pipeline
    #     self.pipeline.process_item(item, self.spider)
    #
    #     # Assert that the existing listing was not duplicated
    #     self.assertEqual(Listing.objects.count(), 1)
    #     listing = Listing.objects.get(airbnb_listing_id='12345')
    #     self.assertEqual(listing.name, 'Existing Listing')  # Name remains unchanged

    def test_process_item_handles_integrity_error(self):
        # Simulate an item with a missing required field
        item = {
            'airbnb_listing_id': '', # Missing ID, which will cause an IntegrityError/ValidationError
            'name': 'Test Listing',
            'title': 'Beautiful Apartment',
            'baths': 2,
            'beds': 3,
            'latitude': '49.2827',
            'longitude': '-123.1207',
            'person_capacity': 5,
            'registration_number': 'ABC123',
            'room_type': 'Entire home/apt',
            'location': 'Downtown Vancouver',
            'bath_is_shared': False,
            'baths_text': '2 baths'
        }

        # Get the initial count of listings in the database
        initial_count = Listing.objects.count()

        # Process the item through the pipeline
        self.pipeline.process_item(item, self.spider)
        listings = Listing.objects.all()  # Retrieve all listings
        for listing in listings:
            print(f"Listing ID: {listing.airbnb_listing_id}, Name: {listing.name}, Title: {listing.title}")

        # Assert that no new listing was created
        self.assertEqual(Listing.objects.count(), initial_count,
                         "Expected no new listing to be created in the database.")
