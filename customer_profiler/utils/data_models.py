from dataclasses import dataclass
from typing import Optional

@dataclass
class ProfilingRequest:
    first_name: str
    last_name: str
    country_code: str
    phone_number: str
    email: str 

@dataclass
class Analytics:
    engagement_num: int
    preferred_channel: str
    resolution_status: float
    summary: str
    past_aggression: bool
    
    def to_json(self):
        return {
            "engagement_num": self.engagement_num,
            "preferred_channel": self.preferred_channel,
            "resolution_status": self.resolution_status,
            "summary": self.summary,
            "past_aggression": self.past_aggression,
        }
    
@dataclass
class Customer:
    id: int
    updated_at: str
    first_name: str
    last_name: str
    country_code: str
    phone_number: str
    email: str 
    analytics: Optional[Analytics] = None
    
    def to_json_db(self):
        return {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "country_code": self.country_code,
            "phone_number": self.phone_number,
            "email": self.email,
            "analytics": self.analytics.to_json(),
        }
        
    def to_json(self):
        return {
            "id": self.id,
            "updated_at": self.updated_at,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "country_code": self.country_code,
            "phone_number": self.phone_number,
            "email": self.email,
            "analytics": self.analytics.to_json(),
        }

@dataclass
class ProfilingResponse():
    status: int # 0 - false, true - 1
    customer: Optional[dict] = None
    
    def to_json(self):
        return {
            "status": self.status,
            "customer": self.customer,
        }

@dataclass
class LLMResponse():
    summary: str
    past_aggression: bool
