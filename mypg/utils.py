# This file will contain class that generates the unique token for account activation and very each token when user go on the link


from django.contrib.auth.tokens import PasswordResetTokenGenerator
from six import text_type
class AppTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (text_type(user.is_active)+text_type(user.pk)+text_type(timestamp))

token_generator = AppTokenGenerator()