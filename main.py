from flask import Flask, Response, request, redirect
from twilio.jwt.client import ClientCapabilityToken
from twilio.twiml.voice_response import VoiceResponse
from twilio.twiml.messaging_response import MessagingResponse


import googlemaps
import json
from datetime import datetime
import sys
import math
import re
import geocoder


def get_directions(start, destination):
    def parse(json):
        result = []
        try:
            steps = json[0]["legs"][0]["steps"]
        except:
            print("there were no directions received from the server", file=sys.stderr)
            exit(1)
        for step in steps:
            result.append(step["html_instructions"])
        return result

    def remove_angle_brackets(string):
        idx = 0
        while idx < len(string):
            if string[idx] == "<":
                while string[idx] != ">":
                    string = string[:idx] + string[idx + 1:]
                string = string[:idx] + string[idx + 1:]
            else:
                idx += 1
        return string

    api_key = "AIzaSyDparrNFJI2nGLVWYZIBVNwxNRlGsSrcyo"
    gmaps = googlemaps.Client(key=api_key)
    transport = "driving"
    directions_result = gmaps.directions(start, destination, mode=transport, departure_time=datetime.now())
    waypoints = parse(directions_result)
    return ('. '.join([remove_angle_brackets(w) for w in waypoints]))


app = Flask(__name__)


@app.route('/token', methods=['GET'])
def get_capability_token():
    """Respond to incoming requests."""

    # Find these values at twilio.com/console
    account_sid = 'ACf2d4b74b4b25771e647846fd049d58fa'
    auth_token = 'c0e421d575b7c12c28434af8b9c02d79'

    capability = ClientCapabilityToken(account_sid, auth_token)

    # Twilio Application Sid
    application_sid = 'APXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
    capability.allow_client_outgoing(application_sid)
    capability.allow_client_incoming('joey')
    token = capability.to_jwt()

    return Response(token, mimetype='application/jwt')

@app.route("/sms", methods=['GET', 'POST'])
def sms_reply():
    """Respond to incoming calls with a simple text message."""
    # Start our TwiML Response
    dest = str(request.values.get('Body', None))

    resp = MessagingResponse()

    source = str(geocoder.ip('me').address)

    # Add a message
    resp.message(get_directions(source,dest ))


    return str(resp)


if __name__ == "__main__":
    app.run(debug=True)



