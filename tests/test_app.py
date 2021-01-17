import requests
import json
import unittest


url = "http://127.0.0.1:8000"

def consume_api(endpoint, data):
    request = requests.post(url+"/v1/"+endpoint, json=data)

    return request.json()


def test_login_returns_error_for_invalid_parameters():
   post_data = {
       "UserName":"Admin",
       "Password":"01234Admin"
   }

   assert consume_api("login", post_data)["Message"] == "Wrong Password or Username"

def test_login_works_for_valid_parameters():
    post_data = {
        "UserName":"admin",
        "Password":"01234Admin"
    }

    assert consume_api("login", post_data)["Message"] == "Login Successful"


