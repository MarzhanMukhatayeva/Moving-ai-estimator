import logging
import json
import os
import requests
import azure.functions as func
from openai import OpenAI


# Azure entry point 

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="travel_time_estimator", methods=["POST"])
def travel_time_estimator(req: func.HttpRequest) -> func.HttpResponse:
    return main(req)



# Environment variables

GOOGLE_MAPS_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-5.4")

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None



# MAIN FUNCTION (твой код)

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("travel-time-test started")

    # 1. Read JSON
    try:
        req_body = req.get_json()
        logging.info(f"Request body: {req_body}")
    except ValueError:
        return func.HttpResponse(
            json.dumps({"error": "Invalid JSON"}),
            status_code=400,
            mimetype="application/json"
        )

    # 2. Extract fields
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

    # 3. Base address
    base_address = "Newton, MA"

    # 4. Compute routes
    base_to_from = compute_route(base_address, from_address, GOOGLE_MAPS_API_KEY)
    to_to_base = compute_route(to_address, base_address, GOOGLE_MAPS_API_KEY)

    # 5. Total travel time
    total_travel_minutes = (
        (base_to_from.get("minutes", 0) or 0) +
        (to_to_base.get("minutes", 0) or 0)
    )

    # 6. Base recommendation
    base_rec = get_base_recommendation(
        apartment_size=apartment_size,
        boxes=boxes,
        stairs=stairs,
        elevator=elevator
    )

    # 7. OpenAI call
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
                base_rec=base_rec
            )
        except Exception as e:
            logging.exception("OpenAI request failed")
            ai_result = {
                "status": "FAILED",
                "estimate_text": "",
                "error_message": str(e)
            }
    else:
        ai_result = {
            "status": "SKIPPED",
            "estimate_text": "",
            "error_message": "OPENAI_API_KEY is missing"
        }

    # 8. Response
    result = {
        "base_to_from": base_to_from,
        "to_to_base": to_to_base,
        "total_travel_minutes": total_travel_minutes,
        "base_recommendation": base_rec,
        "ai_result": ai_result
    }

    return func.HttpResponse(
        json.dumps(result, ensure_ascii=False),
        status_code=200,
        mimetype="application/json"
    )



# Google Routes API

def compute_route(origin_address, destination_address, api_key):
    url = "https://routes.googleapis.com/directions/v2:computeRoutes"

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "routes.distanceMeters,routes.duration"
    }

    payload = {
        "origin": {"address": origin_address},
        "destination": {"address": destination_address},
        "travelMode": "DRIVE"
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)

        try:
            result = response.json()
        except Exception:
            return {"status": "INVALID_JSON"}

        if response.status_code != 200:
            return {"status": "ERROR"}

        routes = result.get("routes", [])
        if not routes:
            return {"status": "NO_ROUTE"}

        route = routes[0]
        distance_meters = route.get("distanceMeters", 0)
        duration_text = route.get("duration", "0s")

        seconds = int(duration_text.replace("s", "")) if "s" in duration_text else 0

        minutes = round(seconds / 60)
        miles = round(distance_meters * 0.000621371, 2)

        return {
            "status": "OK",
            "minutes": minutes,
            "miles": miles
        }

    except Exception as e:
        return {"status": "REQUEST_FAILED", "error": str(e)}



# Base recommendation logic

def get_base_recommendation(apartment_size, boxes, stairs, elevator):
    size = (apartment_size or "").lower()

    crew = "2 movers"
    truck = "18ft truck"
    labor_low = 3.0
    labor_high = 5.0

    if "studio" in size:
        labor_low = 2.0
        labor_high = 4.0

    elif "2 bedroom" in size:
        crew = "3 movers"
        truck = "20ft truck"
        labor_low = 4.0
        labor_high = 7.0

    if str(stairs).lower() == "true":
        labor_low += 0.5
        labor_high += 1.0

    if str(elevator).lower() == "false":
        labor_low += 0.5
        labor_high += 1.0

    return {
        "crew_base": crew,
        "truck_base": truck,
        "labor_low": round(labor_low, 1),
        "labor_high": round(labor_high, 1)
    }



# OpenAI logic

def get_ai_estimate(client, apartment_size, boxes, stairs, elevator,
                    from_address, to_address, base_to_from,
                    to_to_base, total_travel_minutes, base_rec):

    prompt = f"""
Provide a moving estimate.

Apartment: {apartment_size}
Boxes: {boxes}
Stairs: {stairs}
Elevator: {elevator}

Travel time: {total_travel_minutes} minutes

Base recommendation:
Crew: {base_rec["crew_base"]}
Truck: {base_rec["truck_base"]}
Labor: {base_rec["labor_low"]}-{base_rec["labor_high"]} hours

Write a short customer-friendly email.
"""

    response = client.responses.create(
        model=OPENAI_MODEL,
        input=prompt
    )

    ai_text = response.output[0].content[0].text

    return {
        "status": "OK",
        "estimate_text": ai_text,
        "error_message": ""
    }
