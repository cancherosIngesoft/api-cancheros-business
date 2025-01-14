from flask import Flask, jsonify, request, current_app
import requests
import string
import random


def get_auth0_token():
    auth_domain = current_app.config["AUTH0_DOMAIN"]
    url = f"https://{auth_domain}/oauth/token"
    headers = {"content-type": "application/json"}
    payload = {
        "client_id": current_app.config["AUTH0_CLIENT_ID"],
        "client_secret": current_app.config["AUTH0_CLIENT_SECRET"],
        "audience": current_app.config["AUTH0_AUDIENCE"],
        "grant_type": "client_credentials",
    }
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json().get("access_token")


def generate_password(length=12):

    characters = string.ascii_letters + string.digits + "!@#$%^&*()"
    return ''.join(random.choice(characters) for _ in range(length))

def create_auth_user(email):
    token = get_auth0_token()
    password = generate_password()
    auth_domain = current_app.config["AUTH0_DOMAIN"]
    url = f"https://{auth_domain}/api/v2/users"
    headers = {
        "Authorization": f"Bearer {token}",
        "content-type": "application/json"
    }
    payload = {
        "email": email,
        "password": password,
        "connection": "Username-Password-Authentication"
    }


    response = requests.post(url, json=payload, headers=headers)
    if response.status_code != 201:
        raise Exception(f"Error al crear usuario: {response.json().get('message', 'Unknown error')}")

    return email, password
     