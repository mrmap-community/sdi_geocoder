from django.shortcuts import redirect
from django.urls import reverse, resolve
import requests
from django.contrib.auth.models import User, UserManager, AnonymousUser
from django.contrib.auth import authenticate
import uuid

class MapbenderAuthMiddleware:
    def __init__(self, get_response):
       self.get_response = get_response

    def __call__(self, request):
        print('MapbenderAuthMiddelware called')
        # List of paths that don't require authentication
        #open_paths = [
        #    '/login/',  # Assuming '/login/' is the path for your login view
            #'/social-auth/login/google-oauth2/',  # The path for social auth, avoid redirecting requests for authentication
            # Add any other paths that should be publicly accessible
        #]
        # check variable mb_user_id from session wrapper
        print(request.COOKIES)
        session_wrapper_url = "http://127.0.0.1/mapbender/php/mod_sessionWrapper.php"
        if 'MAPBENDER' in request.COOKIES:
            print("Mapbender cookie found")

            # try to replicate mapbender user and authenticate them automatically
            param_dict = {'sessionId': request.COOKIES['MAPBENDER'],
                      'operation': 'get',
                      'key': 'mb_user_id',
                      }
            resp = requests.get(url=session_wrapper_url, params=param_dict)
            data = resp.json()
            if data['success'] == True:
                if data['result']['value'] == 2:
                    print("set user to be anonymous!")
                    user = AnonymousUser
                    request.user = user
                else:
                    #if data['result']['value'] == 1:
                    #    print("set user to be superuser!")
                    #    user = AnonymousUser
                    #    request.user = user
                    # try to find special mapbender user in database - if not create one and set random password
                    password = uuid.uuid4()
                    user_list = User.objects.filter(username="mapbender_user_" + data['result']['value'])
                    if user_list:
                        user = user_list[0]
                        user.set_password('test')
                        user = authenticate(username="mapbender_user_" + data['result']['value'], password=password)
                        request.user = user
                    else:
                        user = User.objects.create_user("mapbender_user_" + data['result']['value'], "testuser@example.com", password)
                        request.user = user
                        user = authenticate(username="mapbender_user_" + data['result']['value'], password=password)
        else:
            print("Mapbender cookie not found - use normal django database authentication!")
        """
        if request.user.is_authenticated:
            print('user is authenticated!')
        else:
            print('user is not authenticated!')
        """
        # Check if the request path is not in the open paths
        #if request.path not in open_paths:
            #print(request.path)
            # Check if the user is authenticated
            #if not request.user.is_authenticated:
                #pass
                # Redirect to login page if not authenticated
                #return redirect(reverse('social:begin', args=('google-oauth2',)))

        # Continue processing the request
        response = self.get_response(request)
        return response