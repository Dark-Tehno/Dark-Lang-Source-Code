import httpclient
import tables
import json
import strutils
import httpcore

proc native_http_get(url: string): tuple[status_code: int, headers: Table[string, string], body: Response] =
  if not (url is string):
    raise newException(ValueError, "URL must be a string")
  
  let client = newHttpClient()
  let response = client.request(url, httpMethod = HttpGet)
  var headers = initTable[string, string]()
  for key, value in response.headers:
    headers[key] = value
  let status_code = parseInt(response.status.split()[0])
  return (status_code, headers, response)

proc native_http_post(url: string, data: string, headers: Table[string, string] = initTable[string, string]()): tuple[status_code: int, headers: Table[string, string], response: Response] =
  if not (url is string):
    raise newException(ValueError, "URL must be a string")
  
  let client = newHttpClient()
  for key, value in headers:
    client.headers[key] = value
  let response = client.request(url, httpMethod = HttpPost, body = data)
  var response_headers = initTable[string, string]()
  for key, value in response.headers:
    response_headers[key] = value
  let status_code = parseInt(response.status.split()[0])
  return (status_code, response_headers, response)

proc native_http_json(response: Response): JsonNode =
  return parseJson(response.body)

proc native_http_text(response: Response): string =
  return response.body