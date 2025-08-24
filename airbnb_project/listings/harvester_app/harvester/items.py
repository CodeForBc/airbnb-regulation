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

    This class defines attributes related to both the listing and the host, which are typically
    available on individual listing pages or in detailed search results.

    Attributes:
        location (scrapy.Field): The specific location or neighborhood of the listing (string).
        room_type (scrapy.Field): The type of room (e.g., entire home, private room) (string).
        person_capacity (scrapy.Field): The maximum number of guests the listing can accommodate (int).
        baths (scrapy.Field): The number of bathrooms in the listing (int).
        beds (scrapy.Field): The number of beds in the listing (int).
        baths_text (scrapy.Field): Textual description of the bathroom facilities (string).
        bath_is_shared (scrapy.Field): Boolean indicating if the bathroom is shared (bool).
        user_id (scrapy.Field): User ID from PassportData (big integer).
        name (scrapy.Field): The name of the user (string).
        title_text (scrapy.Field): The title text associated with the listing (string).
        profile_picture_url (scrapy.Field): The profile picture URL of the user (string).
        thumbnail_url (scrapy.Field): The thumbnail URL of the listing (string).
        is_verified (scrapy.Field): Boolean indicating if the listing is verified (bool).
        is_superhost (scrapy.Field): Boolean indicating if the host is a superhost (bool).
        rating_count (scrapy.Field): The number of ratings for the listing (int).
        rating_average (scrapy.Field): The average rating for the listing (float).
        time_as_host_years (scrapy.Field): The years part of the host's time as a host (int).
        time_as_host_months (scrapy.Field): The months part of the host's time as a host (int).
    """
    location = scrapy.Field()
    room_type = scrapy.Field()
    person_capacity = scrapy.Field()
    baths = scrapy.Field()
    beds = scrapy.Field()
    baths_text = scrapy.Field()
    bath_is_shared = scrapy.Field()
    user_id = scrapy.Field()  # userId from PassportData
    host_name = scrapy.Field()  # The name of the user
    title_text = scrapy.Field()  # titleText from PassportData
    profile_picture_url = scrapy.Field()  # profilePictureUrl
    thumbnail_url = scrapy.Field()  # thumbnailUrl
    is_verified = scrapy.Field()  # isVerified
    is_superhost = scrapy.Field()  # isSuperhost
    rating_count = scrapy.Field()  # ratingCount
    rating_average = scrapy.Field()  # ratingAverage
    time_as_host_years = scrapy.Field()  # years part of timeAsHost
    time_as_host_months = scrapy.Field()  # months part of timeAsHost

