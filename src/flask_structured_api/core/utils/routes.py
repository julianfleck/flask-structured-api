from flask import current_app, g
import inspect
from typing import List, Dict, Any
from flask_structured_api.core.auth import has_required_roles


def get_filtered_routes(include_methods: bool = False, check_auth: bool = True) -> Dict[str, Any]:
    """Get filtered application routes, excluding system endpoints and checking permissions."""
    routes = {}

    # Define public endpoints that should always be visible
    public_endpoints = {
        'root.welcome',                # Root welcome page
        'api_v1.auth.login',          # Login endpoint
        'api_v1.auth.register',       # Registration endpoint
        'api_v1.auth.refresh_token',  # Token refresh endpoint
    }

    # Define endpoints accessible to authenticated users
    authenticated_endpoints = {
        'api_v1.auth.get_current_user',  # /me endpoint
        'api_v1.health.health_check',    # Health check endpoint
        *public_endpoints
    }

    for rule in current_app.url_map.iter_rules():
        # Skip system routes
        if any(x in rule.rule for x in ['/openapi', '/static', '/swagger', '/redoc']) \
           or 'static' in rule.endpoint:
            continue

        view_func = current_app.view_functions[rule.endpoint]

        # For unauthenticated users, only show public endpoints
        if not check_auth:
            if rule.endpoint not in public_endpoints:
                continue
        # For authenticated users, show all accessible endpoints
        elif rule.endpoint not in authenticated_endpoints and hasattr(view_func, '_roles'):
            if not hasattr(g, 'user') or not has_required_roles(g.user, view_func._roles):
                continue

        doc = inspect.getdoc(view_func) or "No documentation available"
        first_line = doc.split('\n')[0].strip()

        if include_methods:
            methods = [m for m in rule.methods if m not in ['HEAD', 'OPTIONS']]
            routes[rule.rule] = {
                'description': first_line,
                'methods': methods,
                'name': rule.endpoint,
                'protected': hasattr(view_func, '_roles')
            }
        else:
            routes[rule.rule] = first_line

    return routes


def get_endpoints_list(check_auth: bool = True) -> List[Dict[str, Any]]:
    """Get list of endpoints with methods for welcome page"""
    routes = get_filtered_routes(include_methods=True, check_auth=check_auth)
    return sorted(
        [
            {
                'path': path,
                'methods': data['methods'],
                'name': data['name'],
                'protected': data.get('protected', False)
            }
            for path, data in routes.items()
        ],
        key=lambda x: x['path']
    )
