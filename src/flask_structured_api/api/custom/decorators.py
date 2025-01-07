from functools import wraps

from flask import abort

from flask_structured_api.extensions.models.countries import CountryCode


def validate_country_code(f):
    @wraps(f)
    def decorated_function(country_code, *args, **kwargs):
        if not CountryCode.is_valid(country_code):
            abort(400, description="Invalid country code: {}".format(country_code))
        return f(country_code, *args, **kwargs)

    return decorated_function
