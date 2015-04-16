from pyramid.view import forbidden_view_config


@forbidden_view_config(renderer='views/forbidden.html')
def forbidden(request):
    request.response.status = 403
    return {}
