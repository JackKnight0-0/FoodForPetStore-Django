from django.urls import path, re_path
from allauth.account import views as account_views
import accounts.views as views

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='account_login'),
    path('signup/', views.CustomSignupView.as_view(), name='account_signup'),
    path('logout/', account_views.LogoutView.as_view(), name='account_logout'),
    path('password/change/', views.CustomChangePasswordView.as_view(), name='account_change_password'),
    path("password/reset/", views.CustomResetPasswordView.as_view(), name="account_reset_password"),
    path("password/reset/done/",
         account_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'),
         name="account_reset_password_done", ),
    re_path(r"^password/reset/key/(?P<uidb36>[0-9A-Za-z]+)-(?P<key>.+)/$",
            views.CustomResetPasswordFromKeyView.as_view(),
            name="account_reset_password_from_key", ),
    path("password/reset/key/done/",
         account_views.PasswordResetFromKeyDoneView.as_view(template_name='accounts/password_reset_from_key_done.html'),
         name="account_reset_password_from_key_done", ),
    re_path(
        r"^confirm-email/(?P<key>[-:\w]+)/$",
        account_views.confirm_email,
        name="account_confirm_email",
    ),
]
