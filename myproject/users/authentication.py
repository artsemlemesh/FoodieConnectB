from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend




class EmailAuthBackend(BaseBackend):#after creating this backend and connecting it in settings we can not only log in by 'login and passw'(default ways) but also by 'email and password'
#it is necessary to redefine two methods: authenticate and get_user: the former is for authentication by email, the latter is to display currently logged in user on the website( right upper corner in my case)
    def authenticate(self, request, username=None, password=None, **kwargs):#copied his func from the settings and slightly modified
        user_model = get_user_model()


        try:
            user = user_model.objects.get(email=username)
            if user.check_password(password):
                return user
            return None
        except (user_model.DoesNotExist, user_model.MultipleObjectsReturned):
            return None
        
    def get_user(self, user_id):
        user_model = get_user_model()
        try:
            return user_model.objects.get(pk=user_id)
        except user_model.DoesNotExist:
            return None