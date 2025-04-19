from odmantic import Document


class Stadium(Document):
    """
    Stadium model representing a sports venue.
    """

    name: str
    location: str
    capacity: int
    image_url: str