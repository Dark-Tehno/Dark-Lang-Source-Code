from urllib import request, error


def native_http_get(args):
    if len(args) != 1:
        raise TypeError("http.get() принимает ровно 1 аргумент (url)")
    
    url = args[0]
    if not isinstance(url, str):
        raise TypeError("Аргумент http.get() должен быть строкой")

    try:
        with request.urlopen(url, timeout=10) as response:
            headers = {key: value for key, value in response.getheaders()}
            return {
                "status_code": response.status,
                "headers": headers,
                "body": response.read().decode('utf-8', errors='ignore')
            }
    except error.HTTPError as e:
        headers = {key: value for key, value in e.headers.items()}
        return {
            "status_code": e.code,
            "headers": headers,
            "body": e.read().decode('utf-8', errors='ignore')
        }
    except error.URLError as e:
        return {
            "status_code": -1, 
            "headers": {},
            "body": str(e.reason)
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
        req = request.Request(url, data=data, headers=headers, method='POST')
        with request.urlopen(req, timeout=10) as response:
            response_headers = {key: value for key, value in response.getheaders()}
            return {
                "status_code": response.status,
                "headers": response_headers,
                "body": response.read().decode('utf-8', errors='ignore')
            }
    except error.HTTPError as e:
        headers = {key: value for key, value in e.headers.items()}
        return {
            "status_code": e.code,
            "headers": headers,
            "body": e.read().decode('utf-8', errors='ignore')
        }
    except error.URLError as e:
        return {
            "status_code": -1, 
            "headers": {},
            "body": str(e.reason)
        }