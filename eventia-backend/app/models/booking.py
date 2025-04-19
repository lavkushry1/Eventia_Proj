# -*- coding: utf-8 -*-
# @Author: Roni Laukkarinen
# @Date:   2025-04-18 17:01:14
# @Last Modified by:   Roni Laukkarinen
# @Last Modified time: 2025-04-19 09:26:39
from datetime import datetime

from bson import ObjectId
from odmantic import Document, Field


class Booking(Document):
    """Booking model.
    
    Extends:
        Document
    """
    user_id: ObjectId = Field(...)
    event_id: ObjectId = Field(...)
    quantity: int = Field(...)
    created_at: datetime = Field(default_factory=datetime.now)