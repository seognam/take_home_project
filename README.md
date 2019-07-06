# Take Home Project

## Hosted online at <TBD>

## Instructions

Postman Echo is a service you can use to test your REST clients and make sample API calls. It provides endpoints for GET, POST, PUT, various auth mechanisms and other utility endpoints.
The documentation for the endpoints as well as example responses can be found at https://postman-echo.com

Your task is to build a Web Server that does the following.
1. Accept an API GET request to `/count`.
    - Increment a Counter (x) by one each time that the `/count` url is called.
    - Make an API Call out to postman-echo.com, (x) times
    - For example:
```
    if the counter (x) is 5, you'll need to make 5 API requests to postman-echo.com.

    GET https://postman-echo.com/get?x=0

    GET https://postman-echo.com/get?x=1

    GET https://postman-echo.com/get?x=2

    GET https://postman-echo.com/get?x=3

    GET https://postman-echo.com/get?x=4
```

2. Respond to the client with an application/json response that aggregates the responses from postman-echo.
    -> For example:
```
    [{
        "method": "GET",
        "url": "https://postman-echo.com/count?x=0",
        "headers": {
            "x-forwarded-proto": "https",
            "host": "postman-echo.com",
            "accept": "*/*",
            "accept-encoding": "gzip, deflate",
            "cache-control": "no-cache",
            "postman-token": "5c27cd7d-6b16-4e5a-a0ef-191c9a3a275f",
            "user-agent": "PostmanRuntime/7.6.1",
            "x-forwarded-port": "443"
        }
    }]
```
3. This Web Server should return a sub 5 second response when counter (x) is less than 100.
