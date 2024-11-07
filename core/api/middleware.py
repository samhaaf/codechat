import time

async def log_requests(request: Request, call_next):
    start_time = time.time()

    # Log the request details
    print(f"Request: {request.method} {request.url.path}")

    # Process the request
    response = await call_next(request)

    # Calculate the request processing time
    process_time = time.time() - start_time

    # Log the response status and processing time
    print(f"Response: {response.status_code} Process time: {process_time}")

    return response


async def maintain_db_connection(request: Request, call_next) :

    # Global variable to store the last connection check time
    last_db_check_time = None

    # Process the request
    response = await call_next(request)

    return response
