from base.tenant import clear_current_brokerage, set_current_brokerage


class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, 'user', None)
        if user is not None and user.is_authenticated:
            request.brokerage = user.brokerage
        else:
            request.brokerage = None
        set_current_brokerage(request.brokerage)
        try:
            response = self.get_response(request)
        finally:
            clear_current_brokerage()
        return response
