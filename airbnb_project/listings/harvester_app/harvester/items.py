import scrapy


class AirBnBListingItem(scrapy.Item):
    """
    Item class representing a basic Airbnb listing.

    This class defines the core attributes of an Airbnb listing that are commonly
    available in search results or listing previews.

    Attributes:
        airbnb_listing_id (scrapy.Field): The unique Airbnb listing ID.
        title (scrapy.Field): The title of the listing.
        name (scrapy.Field): The name of the listing.
        registration_number (scrapy.Field): The registration number of the listing.
        latitude (scrapy.Field): The latitude coordinate of the listing.
        longitude (scrapy.Field): The longitude coordinate of the listing.
    """
    airbnb_listing_id = scrapy.Field()
    title = scrapy.Field()
    name = scrapy.Field()
    registration_number = scrapy.Field()
    latitude = scrapy.Field()
    longitude = scrapy.Field()


class ExpandedAirBnBListingItem(AirBnBListingItem):
    """
    Item class representing an expanded Airbnb listing with additional details.

    This class inherits from AirBnBListingItem and includes extra fields that
    provide more detailed information about the listing. These additional fields
    are typically available on individual listing pages or in detailed search results.

    Attributes:
        location (scrapy.Field): The specific location or neighborhood of the listing.
        room_type (scrapy.Field): The type of room (e.g., entire home, private room).
        person_capacity (scrapy.Field): The maximum number of guests the listing can accommodate.
        baths (scrapy.Field): The number of bathrooms in the listing.
        beds (scrapy.Field): The number of beds in the listing.
        baths_text (scrapy.Field): Textual description of the bathroom facilities.
        bath_is_shared (scrapy.Field): Boolean indicating if the bathroom is shared.

    Inherited Attributes:
        All attributes from AirBnBListingItem are also available in this class.
    """
    location = scrapy.Field()
    room_type = scrapy.Field()
    person_capacity = scrapy.Field()
    baths = scrapy.Field()
    beds = scrapy.Field()
    baths_text = scrapy.Field()
    bath_is_shared = scrapy.Field()
