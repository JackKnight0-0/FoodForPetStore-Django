from django.contrib.auth.mixins import UserPassesTestMixin


class IsAdmin(UserPassesTestMixin):
    def test_func(self):
        """
        Check if user is admin for creating folder
        TODO May add group of user which can creating folder, items.
        """
        return self.request.user.is_staff

