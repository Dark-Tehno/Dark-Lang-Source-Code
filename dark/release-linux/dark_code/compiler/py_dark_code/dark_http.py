# Copyright 2026 Dark.Tehno
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import requests

def get(url):    
    if not isinstance(url, str):
        raise TypeError("Аргумент http.get() должен быть строкой")

    try:
        response = requests.get(url)
        headers = {key: value for key, value in response.headers.items()}
        return {
            "status_code": response.status_code,
            "headers": headers,
            "body": response
        }
    except requests.HTTPError as e:
        headers = {key: value for key, value in e.headers.items()}
        return {
            "status_code": e.status_code,
            "headers": headers,
            "body": e
        }
    
def post(url, data, headers_dict_optional={}):
    """Выполняет HTTP POST-запрос и возвращает словарь с status_code, headers, и body."""

    headers = {}
    if headers_dict_optional:
        if not isinstance(headers_dict_optional, dict):
            raise TypeError("Необязательный третий аргумент http.post() должен быть словарем заголовков")
        headers = headers_dict_optional

    if not isinstance(url, str):
        raise TypeError("Первый аргумент http.post() (url) должен быть строкой")

    try:
        response = requests.post(url, data=data, headers=headers)
        response_headers = {key: value for key, value in response.headers.items()}

        return {
            "status_code": response.status_code,
            "headers": response_headers,
            "response": response
        }

    except requests.HTTPError as e:
        headers = {key: value for key, value in e.headers.items()}
        return {
            "status_code": e.status_code,
            "headers": headers,
            "response": e
        }

def json(response):
    """Выполняет HTTP json и возвращает словарь."""
    return response.json()

def text(response):
    """Выполняет HTTP text и возвращает текст."""
    return response.text