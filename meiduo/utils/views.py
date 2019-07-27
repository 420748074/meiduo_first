from django import http
from django.contrib.auth.mixins import LoginRequiredMixin

class LoginRequiredJSONMixin(LoginRequiredMixin):

    def handle_no_permission(self):

        return http.JsonResponse({'code':'4101','errmsg':'用户未登陆'})