import logging
import json
import os
import requests
import azure.functions as func
from openai import OpenAI



# Environment variables

GOOGLE_MAPS_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-5.4")


client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("travel-time-test started")

    
    # 1. Читаем входной JSON
   
    try:
        req_body = req.get_json()
        logging.info(f"Request body: {req_body}")
    except ValueError:
        return func.HttpResponse(
            json.dumps({"error": "Invalid JSON"}),
            status_code=400,
            mimetype="application/json"
        )

   
    # 2. Достаем поля из Apps Script / формы
   
    from_address = (req_body.get("from_address") or "").strip()
    to_address = (req_body.get("to_address") or "").strip()

    apartment_size = (req_body.get("move_size") or "").strip()
    boxes = (req_body.get("boxes") or "").strip()
    stairs = req_body.get("stairs")
    elevator = req_body.get("elevator")

    if not from_address or not to_address:
        return func.HttpResponse(
            json.dumps({"error": "Both from_address and to_address are required"}),
            status_code=400,
            mimetype="application/json"
        )

    if not GOOGLE_MAPS_API_KEY:
        return func.HttpResponse(
            json.dumps({"error": "GOOGLE_MAPS_API_KEY is missing"}),
            status_code=500,
            mimetype="application/json"
        )

    
    # 3. Базовый адрес компании
   
    base_address = "Newton, MA"


    # 4. Считаем travel routes
    
    base_to_from = compute_route(base_address, from_address, GOOGLE_MAPS_API_KEY)
    to_to_base = compute_route(to_address, base_address, GOOGLE_MAPS_API_KEY)

    
    # 5. Считаем общий travel time
    
    total_travel_minutes = (
        (base_to_from.get("minutes", 0) or 0) +
        (to_to_base.get("minutes", 0) or 0)
    )

    
    # 6. Base recommendation в Python
    
    base_rec = get_base_recommendation(
        apartment_size=apartment_size,
        boxes=boxes,
        stairs=stairs,
        elevator=elevator
    )
    price_estimate = calculate_price_estimate(
    base_rec=base_rec,
    total_travel_minutes=total_travel_minutes
    )
    
    # 7. Вызываем OpenAI
    
    if OPENAI_API_KEY and client:
        try:
            ai_result = get_ai_estimate(
                client=client,
                apartment_size=apartment_size,
                boxes=boxes,
                stairs=stairs,
                elevator=elevator,
                from_address=from_address,
                to_address=to_address,
                base_to_from=base_to_from,
                to_to_base=to_to_base,
                total_travel_minutes=total_travel_minutes,
                base_rec=base_rec,
                price_estimate=price_estimate
            )
        except Exception as e:
            logging.exception("OpenAI request failed")
            ai_result = {
                "status": "FAILED",
                "recommended_crew": "",
                "recommended_truck": "",
                "labor_hours_range": "",
                "travel_time_minutes": "",
                "total_estimated_time_range": "",
                "short_reason": "",
                "estimate_text": "",
                "error_message": str(e)
            }
    else:
        ai_result = {
            "status": "SKIPPED",
            "recommended_crew": "",
            "recommended_truck": "",
            "labor_hours_range": "",
            "travel_time_minutes": "",
            "total_estimated_time_range": "",
            "short_reason": "",
            "estimate_text": "",
            "error_message": "OPENAI_API_KEY is missing"
        }

    
    # 8. Возвращаем всё Apps Script-у
    
    result = {
        "base_to_from": base_to_from,
        "to_to_base": to_to_base,
        "total_travel_minutes": total_travel_minutes,
        "base_recommendation": base_rec,
        "price_estimate": price_estimate,
        "ai_result": ai_result
    }

    return func.HttpResponse(
        json.dumps(result, ensure_ascii=False),
        status_code=200,
        mimetype="application/json"
    )



# Google Routes API

def compute_route(origin_address, destination_address, api_key):
    """
    Считает один маршрут через Google Routes API.
    Возвращает:
    {
      "status": "OK",
      "minutes": 10,
      "miles": 3.41,
      ...
    }
    или ошибку.
    """
    url = "https://routes.googleapis.com/directions/v2:computeRoutes"

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "routes.distanceMeters,routes.duration"
    }

    payload = {
        "origin": {
            "address": origin_address
        },
        "destination": {
            "address": destination_address
        },
        "travelMode": "DRIVE"
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)

        logging.info(f"Google status: {response.status_code}")
        logging.info(f"Google response: {response.text}")

        try:
            result = response.json()
        except Exception:
            return {
                "status": "INVALID_JSON",
                "error_message": response.text
            }

        if response.status_code != 200:
            return {
                "status": result.get("error", {}).get("status", f"HTTP_{response.status_code}"),
                "error_message": result.get("error", {}).get("message", "Google API error")
            }

        routes = result.get("routes", [])
        if not routes:
            return {
                "status": "NO_ROUTE",
                "error_message": "No routes found"
            }

        route = routes[0]
        distance_meters = route.get("distanceMeters", 0)
        duration_text = route.get("duration", "0s")

        # duration обычно приходит как строка вида "1234s"
        seconds = 0
        try:
            seconds = int(duration_text.replace("s", ""))
        except Exception:
            seconds = 0

        minutes = round(seconds / 60)
        miles = round(distance_meters * 0.000621371, 2)

        return {
            "status": "OK",
            "minutes": minutes,
            "miles": miles,
            "duration_raw": duration_text,
            "distance_meters": distance_meters
        }

    except Exception as e:
        logging.exception("Google Maps request failed")
        return {
            "status": "REQUEST_FAILED",
            "error_message": str(e)
        }



# Base recommendation logic (Python)

def get_base_recommendation(apartment_size, boxes, stairs, elevator):
    """
    - recommended crew base
    - truck base
    - labor hours base range
    """
    size = (apartment_size or "").lower()
    boxes_text = (boxes or "").lower()
    stairs_text = str(stairs).lower()
    elevator_text = str(elevator).lower()

    crew = "2 movers"
    truck = "18ft truck"
    labor_low = 3.0
    labor_high = 5.0

    # --- apartment size rules ---
    if "studio" in size:
        crew = "2 movers"
        truck = "18ft truck"
        labor_low = 2.0
        labor_high = 4.0

    elif "1 bedroom" in size:
        crew = "2 movers"
        truck = "18ft truck"
        labor_low = 2.5
        labor_high = 4.5

    elif "2 bedroom" in size:
        crew = "3 movers"
        truck = "20ft truck"
        labor_low = 4.0
        labor_high = 7.0

    # --- box adjustments ---
    if "21-40" in boxes_text or "41+" in boxes_text:
        labor_low += 0.5
        labor_high += 1.0

    # --- stairs add time ---
    if stairs_text == "true":
        labor_low += 0.5
        labor_high += 0.7

    # --- no elevator can add time ---
    if elevator_text == "false":
        labor_low += 0.5
        labor_high += 1.0

    return {
        "crew_base": crew,
        "truck_base": truck,
        "labor_low": round(labor_low, 1),
        "labor_high": round(labor_high, 1)
    }

def calculate_price_estimate(base_rec, total_travel_minutes):
    labor_low = float(base_rec.get("labor_low", 0))
    labor_high = float(base_rec.get("labor_high", 0))

    crew = base_rec.get("crew_base", "2 movers")

    if "3" in crew:
        rate = 159
    else:
        rate = 129

    travel_hours = total_travel_minutes / 60

    total_low = labor_low + travel_hours
    total_high = labor_high + travel_hours

    price_low = total_low * rate
    price_high = total_high * rate

    return {
        "hourly_rate": rate,
        "labor_hours_range": f"{labor_low:.1f}-{labor_high:.1f} hours",
        "travel_time_minutes": total_travel_minutes,
        "travel_time_hours": round(travel_hours, 2),
        "total_time_range": f"{total_low:.2f}-{total_high:.2f} hours",
        "estimated_price_range": f"${price_low:.0f}-${price_high:.0f}"
    }

# OpenAI estimate logic

def get_ai_estimate(
    client,
    apartment_size,
    boxes,
    stairs,
    elevator,
    from_address,
    to_address,
    base_to_from,
    to_to_base,
    total_travel_minutes,
    base_rec,
    price_estimate
):
    """
    Отправляет в OpenAI уже ГОТОВЫЕ факты:
    - apartment size
    - boxes
    - stairs/elevator
    - travel time
    - base Python recommendation

    Важно:
    AI не должен угадывать travel time.
    AI должен использовать уже посчитанный travel time и
    объяснять, что он добавляется отдельно к labor estimate.
    """
    prompt = f"""
You are an expert move estimator for a professional moving company.

Your task is to review the move and provide a practical estimate.

You must follow these rules:
1. Labor time and travel time are separate.
2. Labor time means loading, carrying, moving, unloading, and basic furniture handling.
3. Travel time means only driving-related time already calculated by the system.
4. Total estimated time must include both labor time and travel time.
5. Use the system-calculated travel time exactly as provided.
6. Use the base recommendation unless there is a strong reason to adjust it.
7. Keep the answer practical, concise, and business-friendly.

Move details:
- Apartment size: {apartment_size}
- Boxes: {boxes}
- Stairs: {stairs}
- Elevator: {elevator}
- From address: {from_address}
- To address: {to_address}

System-calculated travel data:
- Base to From: {base_to_from.get("minutes", 0)} minutes
- To to Base: {to_to_base.get("minutes", 0)} minutes
- Total travel time: {total_travel_minutes} minutes

Base system recommendation:
- Crew base: {base_rec["crew_base"]}
- Truck base: {base_rec["truck_base"]}
- Labor hours base range: {base_rec["labor_low"]}-{base_rec["labor_high"]} hours
Price calculation:
- Hourly rate: ${price_estimate["hourly_rate"]}/hr
- Estimated price range: {price_estimate["estimated_price_range"]}

Instructions for reasoning:
- Explain whether stairs increase labor time.
- Explain whether lack of elevator affects labor time.
- Explain that travel time is added separately to labor time.
- Keep the recommendation realistic for a moving company.

Return ONLY valid JSON in this exact format:
{{
  "recommended_crew": "...",
  "recommended_truck": "...",
  "labor_hours_range": "...",
  "travel_time_minutes": "...",
  "total_estimated_time_range": "...",
  "short_reason": "...",
  "estimate_text": "..."
}}

Requirements for estimate_text:
- Write it as a full email to the customer.
- Start with: Hi,
- Thank the customer for reaching out.
- Include recommended crew.
- Include truck recommendation.
- Include estimated labor time.
- Include travel time.
- Include estimated total time.
- Include estimated price range.
- Mention that this is a preliminary estimate and actual time may vary depending on inventory, building access, stairs, elevator, and parking.
- End with:
Best regards,
Ken
Seven Moving
617-401-1777
sevenmoving@gmail.com
"""

    response = client.responses.create(
        model=OPENAI_MODEL,
        input=prompt
    )

    
    ai_text = response.output[0].content[0].text
    logging.info(f"OpenAI raw output: {ai_text}")


    try:
        parsed = json.loads(ai_text)
        return {
            "status": "OK",
            "recommended_crew": parsed.get("recommended_crew", ""),
            "recommended_truck": parsed.get("recommended_truck", ""),
            "labor_hours_range": parsed.get("labor_hours_range", ""),
            "travel_time_minutes": parsed.get("travel_time_minutes", ""),
            "total_estimated_time_range": parsed.get("total_estimated_time_range", ""),
            "short_reason": parsed.get("short_reason", ""),
            "estimate_text": parsed.get("estimate_text", ""),
            "error_message": ""
        }

    except Exception:
        
        return {
            "status": "OK_TEXT_ONLY",
            "recommended_crew": "",
            "recommended_truck": "",
            "labor_hours_range": "",
            "travel_time_minutes": "",
            "total_estimated_time_range": "",
            "short_reason": "",
            "estimate_text": ai_text,
            "error_message": ""
        }
