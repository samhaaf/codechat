import inspect
from functools import wraps


def fastapi_decorator(decor_func):
    """ A decorator factory which returns new decorators which
            . Integrate the new decorator into the fastapi dependency chain
    """

    def make_injectable_route(route_func):
        """ Creates a wrapped route that is injectable with the `injects` kwargs """

        async def injectable_route(*args, **kwargs):
            """ Conditionally drops `injects` params from route_func call if not requested """

            # Inspect route_func to determine if it expects any injects parameters
            params = inspect.signature(route_func).parameters

            # For each injectable, if not expected by route_func then drop it
            for key in kwargs:
                if key not in params:
                    del kwargs[key]

            # Call the original route_func with its parameters, injected if necessary
            return await route_func(*args, **kwargs)

        return injectable_route

    @wraps(decor_func)
    def wrapped_decorator(route_func):
        """ This function is what will be exposed to fastapi.

            Returns a new function with
                . modified arg signatures
                . ability to conditionally inject new values into the route
        """

        # Wrap route_func with route_wrapper to create injected_route_func
        injectable_route = make_injectable_route(route_func)

        # Get the original signatures
        route_sig = inspect.signature(route_func)
        decor_sig = inspect.signature(decor_func)

        # Create a new list of parameters for the decor_func signature
        new_params = list(decor_sig.parameters.values())

        # Identify the keyword-only parameters from route_func that are not in decor_func
        only_route_sigs = [
            param for param_name, param in route_sig.parameters.items()
            if param_name not in decor_sig.parameters and param.kind == inspect.Parameter.KEYWORD_ONLY
        ]

        # Extend the new_params with the only_route_params
        new_params.extend(only_route_sigs)

        # Apply the new signature to decor_func
        decor_func.__signature__ = decor_sig.replace(parameters=new_params)

        return decor_func(injectable_route)

    return wrapped_decorator
