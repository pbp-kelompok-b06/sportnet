from django.contrib.auth.decorators import login_required

def hybrid_login_required(view_func):
    return login_required(view_func)
