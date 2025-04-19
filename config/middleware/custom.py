import uuid
from apps.user.auth import user_is_authenticated

class PreviousPageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Here is run only once when the server starts

    def __call__(self, request):

        # Here is run before a view is run
        if not "client_id" in request.session:
            request.session["client_id"] = str(uuid.uuid4())
        if request.session.get_expiry_age() != 10368000:
            request.session.set_expiry(60*60*24*120)
        if not request.user.is_authenticated and request.path not in ['/login/', '/logout/']:
            request.session['previous_page'] = request.META.get("PATH_INFO")
        response = self.get_response(request)

        # Here is run after a view is run
        # source = request.META.get("HTTP_REFERER")
        # destination = request.META.get("PATH_INFO")
        # if response.status_code >= 300 or response.status_code < 400:
        #     if  destination == "/checkout/":      
        #         request.session["CHECKOUT_LOGIN_REDIRECT"] = source
        return response
    

# middleware.py
class SimpleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = user_is_authenticated(request)
        if not user and request.path not in ['/login/', '/logout/']:
            request.session['previous_page'] = request.get_full_path()
        return self.get_response(request)