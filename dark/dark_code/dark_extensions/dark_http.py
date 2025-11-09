import requests

def native_http_get(args):
    if len(args) != 1:
        raise TypeError("http.get() принимает ровно 1 аргумент (url)")
    
    url = args[0]
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
    
def native_http_post(args):
    """Выполняет HTTP POST-запрос и возвращает словарь с status_code, headers, и body."""
    if len(args) not in [2, 3]:
        raise TypeError("http.post() принимает 2 или 3 аргумента (url, data, headers_dict_optional)")
    
    url = args[0]
    data = args[1]
    headers = {}
    if len(args) == 3:
        if not isinstance(args[2], dict):
            raise TypeError("Необязательный третий аргумент http.post() должен быть словарем заголовков")
        headers = args[2]

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

def native_http_json(args):
    """Выполняет HTTP json и возвращает словарь."""
    if len(args) != 1:
        raise TypeError("http.post() принимает 1 аргумент (response)")
    
    response = args[0]
    return response.json()

def native_http_text(args):
    """Выполняет HTTP text и возвращает текст."""
    if len(args) != 1:
        raise TypeError("http.post() принимает 1 аргумент (response)")
    
    response = args[0]
    return response.text