from urllib import request, error


def native_http_get(args):
    """Performs an HTTP GET request and returns a dictionary with status_code, headers, and body."""
    if len(args) != 1:
        raise TypeError("http.get() takes exactly 1 argument (url)")
    
    url = args[0]
    if not isinstance(url, str):
        raise TypeError("Argument to http.get() must be a string")

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
    """Performs an HTTP POST request and returns a dictionary with status_code, headers, and body."""
    if len(args) not in [2, 3]:
        raise TypeError("http.post() takes 2 or 3 arguments (url, data, headers_dict_optional)")
    
    url = args[0]
    data = args[1]
    headers = {}
    if len(args) == 3:
        if not isinstance(args[2], dict):
            raise TypeError("Optional third argument to http.post() must be a dictionary of headers")
        headers = args[2]

    if not isinstance(url, str):
        raise TypeError("First argument to http.post() (url) must be a string")
    if not isinstance(data, str):
        raise TypeError("Second argument to http.post() (data) must be a string")

    try:
        req = request.Request(url, data=data.encode('utf-8'), headers=headers, method='POST')
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