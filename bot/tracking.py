import os
import aiohttp


SHIP24_URL = "https://api.ship24.com/public/v1/tracking/search"


async def get_tracking_info(tracking_number):

    api_key = os.getenv("TRACKING_API_KEY")

    if not api_key:
        return {
            "success": False,
            "error": "Ship24 API key is missing."
        }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "trackingNumber": tracking_number
    }

    try:

        async with aiohttp.ClientSession() as session:

            async with session.post(
                SHIP24_URL,
                headers=headers,
                json=data
            ) as response:

                response_data = await response.json()

                # Accept every successful HTTP response
                if response.status < 200 or response.status >= 300:

                    print("Ship24 error:", response.status)
                    print(response_data)

                    return {
                        "success": False,
                        "error": "Tracking request failed."
                    }

                trackings = (
                    response_data
                    .get("data", {})
                    .get("trackings", [])
                )

                if not trackings:

                    return {
                        "success": False,
                        "error": "No tracking information found."
                    }

                tracking = trackings[0]

                shipment = tracking.get(
                    "shipment",
                    {}
                )

                events = tracking.get(
                    "events",
                    []
                )

                # -------------------------
                # STATUS
                # -------------------------

                status = shipment.get(
                    "statusMilestone",
                    "Unknown"
                )

                if status:
                    status = status.replace(
                        "_",
                        " "
                    ).title()

                # -------------------------
                # LATEST EVENT
                # -------------------------

                latest_event = None

                if events:
                    latest_event = events[-1]

                # -------------------------
                # CARRIER
                # -------------------------

                carrier = "Unknown"

                if latest_event:

                    courier_code = latest_event.get(
                        "courierCode"
                    )

                    if courier_code == "il-post":
                        carrier = "Israel Post"

                    elif courier_code:
                        carrier = courier_code

                # -------------------------
                # LOCATION
                # -------------------------

                location = "Unknown"

                if latest_event:

                    event_location = latest_event.get(
                        "location"
                    )

                    if event_location:
                        location = event_location

                # -------------------------
                # ESTIMATED DELIVERY
                # -------------------------

                delivery = shipment.get(
                    "delivery",
                    {}
                )

                estimated_delivery = (
                    delivery.get(
                        "estimatedDeliveryDate"
                    )
                    or delivery.get(
                        "courierEstimatedDeliveryDate"
                    )
                    or "Not available"
                )

                # -------------------------
                # RETURN RESULT
                # -------------------------

                return {
                    "success": True,

                    "tracking_number":
                        tracking_number,

                    "carrier":
                        carrier,

                    "status":
                        status,

                    "location":
                        location,

                    "estimated_delivery":
                        estimated_delivery,

                    "events":
                        events
                }

    except Exception as error:

        print(
            "Tracking error:",
            error
        )

        return {
            "success": False,
            "error": str(error)
        }