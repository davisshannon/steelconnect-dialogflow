from flask import Flask, request, make_response
import json
import logging

from actions.create_uplink import create_uplink
from actions.create_site import create_site
from actions.list_sites import list_sites
from actions.list_sites_followup import list_sites_followup
from actions.create_wan import create_wan
from actions.create_WAN_new import create_WAN
from actions.add_site_to_wan import add_site_to_WAN
from actions.clear_sites import clear_sites
from actions.create_zone import create_zone

from app import app

@app.route('/webhook/', methods=['POST'])
def webhook():
    """
    Extracts the intent, action and paramaters and passes them to the handling method.
    :return: Returns a json formatted response containing the text to be read back to the user
    :rtype: json
    """
    req = request.get_json(silent=True, force=True)

    logging.debug("Request\n" + json.dumps(req, indent=4))

    try:
        action_type = req["result"]["action"]
        intent_type = req["result"]["metadata"]["intentName"]
        parameters = req["result"]["parameters"]
        contexts = req["result"]["contexts"]
    except KeyError as e:
        logging.error("Error processing request {}".format(e))
        return format_response("There was an error processing your request")

    if action_type == "CreateSite":
        response = create_site(app.config["SC_API"], parameters)
    elif action_type == "CreateUplink":
        response = create_uplink(parameters)
    elif action_type == "ListSites":
        response = list_sites(app.config["SC_API"], parameters)
    elif action_type == "ListSites.ListSites-custom":
        response = list_sites_followup(app.config["SC_API"], req["result"]["contexts"][0]["parameters"])
    elif action_type == "ListSites.ListSites-yes":
        parameters["position"] = "all"
        response = list_sites_followup(app.config["SC_API"], None)
    elif action_type == "CreateWan":
        response = create_wan(parameters)
    elif action_type == "CreateWAN":
        response = create_WAN(app.config["SC_API"], parameters, contexts)
    elif action_type == "AddSiteToWAN":
        response = add_site_to_WAN(app.config["SC_API"], parameters, contexts)
    elif action_type == "ClearSites":
        response = clear_sites(parameters)
    elif action_type == "CreateZone":
        response = create_zone(app.config["SC_API"], parameters)


    # elif action_type == "SomeOtherAction"            # Use elif to add extra functionality
    else:
        response = "Error: This feature has not been implemented yet"
        logging.error("Not implemented error action: {} intent: {}".format(action_type, intent_type))

    return format_response(response)                        # Correctly format the text response into json for API.AI to read out to the user


def format_response(speech):
    """
    :param speech: A text string to be read out to the user
    :type speech: string
    :return: Returns a json formatted response
    :rtype: json
    """
    response = {
        "speech": speech,
        "displayText": speech,
        "source": "steelconnect"
    }

    response = json.dumps(response, indent=4)
    logging.debug(response)
    r = make_response(response)
    r.headers['Content-Type'] = 'application/json'
