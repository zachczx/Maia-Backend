from core.utils.customer_utils import check_customer_exists, update_customer, get_customer_by_phone_number, get_customer_by_email
from core.utils.customer_engagement_utils import get_customer_engagements_by_customer
from ..utils.data_models import ProfilingResponse, ProfilingRequest
from .openai_service import get_llm_response
from ..utils.data_models import Customer, Analytics
from collections import Counter
from typing import Optional, List, Dict, Any
import logging
import Levenshtein

logger = logging.getLogger("django")

def update_analytics(customer: Customer) -> Optional[Customer]:
    try:
        updated_customer_data = update_customer(customer.id, customer.to_json_db())
        return updated_customer_data
    except Exception as e:
        return None

def generate_profile_analytics(customer: Customer, engagements: List[Dict[str, Any]]) -> Optional[Customer]:
    engagement_num = len(engagements)
    channel_counter = Counter()
    resolution_true_count = 0
    summaries = []
    notes = []

    for engagement in engagements:
        channel = engagement["channel"]
        status = engagement["resolution"]
        summary = engagement["conversation"]
        note = engagement["notes"] if engagement["notes"] is not None else ""
        
        channel_counter[channel] += 1
        if status:
            resolution_true_count += 1
        summaries.append(summary)
        notes.append(note)
    
    preferred_channels = [channel for channel, count in channel_counter.items() if count == max(channel_counter.values())]
    preferred_channel = "/".join(map(str, preferred_channels))
    resolution_status = (resolution_true_count / engagement_num) * 100    
    llm_response = get_llm_response(summaries, notes)
    
    analytics = Analytics(engagement_num, preferred_channel, resolution_status, summary=llm_response.summary, past_aggression=llm_response.past_aggression)
    customer.analytics = analytics
    
    update_record = update_analytics(customer)
    
    if update_record is not None:
        return update_record
    
    return None

def calculate_levenshtein_ratio(str1: str, str2: str) -> float:
    ratio = Levenshtein.ratio(str1, str2)
    return ratio

def search_similar_customer(customer: Customer) -> Dict[str, Any]:
    try:
        customer_record = get_customer_by_phone_number(customer.phone_number)
    except Exception:
        try:
            customer_record = get_customer_by_email(customer.email)
        except Exception:
            return {"exists": False, 'message': 'Customer not found with the given details'}

    customer_record_name = f"{customer_record['first_name']} {customer_record['last_name']}"
    inputted_customer_name = f"{customer.first_name} {customer.last_name}"
    
    levenshtein_ratio = calculate_levenshtein_ratio(customer_record_name, inputted_customer_name)
    
    if levenshtein_ratio > 0.85:
        return {
            'exists': True,
            'customer': customer_record,
            'message': 'Customer exists'
        }
    else:
        return {"exists": False, 'message': 'Customer not found with the given details'}

def search_customer(request: ProfilingRequest) -> ProfilingResponse:
    
    def update_and_return_customer(customer_obj: Customer, engagements: List[Dict[str, Any]]):
        updated_customer = generate_profile_analytics(customer_obj, engagements)
        if updated_customer is None:
            return ProfilingResponse(status=0)
        else:
            return ProfilingResponse(status=1, customer=updated_customer["customer"])

    customer_record = check_customer_exists(
        request.first_name,
        request.last_name, 
        request.country_code,
        request.phone_number, 
        request.email
    )
    
    if not customer_record["exists"]:
        customer_record = search_similar_customer(request)
    
        if not customer_record["exists"]:
            return ProfilingResponse(status=0)

    customer_obj = Customer(**customer_record["customer"])
    customer_id = customer_obj.id

    engagements = get_customer_engagements_by_customer(customer_id)
    engagement_num = len(engagements)

    if customer_obj.analytics is None:
        return update_and_return_customer(customer_obj, engagements)
    else:
        if engagement_num != customer_obj.analytics["engagement_num"]:
            return update_and_return_customer(customer_obj, engagements)
        else:
            return ProfilingResponse(status=1, customer=customer_record["customer"])
