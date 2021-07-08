from google_auth_oauthlib import flow as Flow
from googleapiclient.discovery import build

class GoogleAuthService():
    """Implementation for Google OAuth 2.0"""

    def __init__(self):
        # Initializes the installed app flow.
        # Use the client_secret.json file to identify the application requesting
        # authorization. The client ID (from that file) and access scopes are required.
        self.flow = Flow.InstalledAppFlow.from_client_secrets_file(
            'client_secret.json',
            scopes=['https://www.googleapis.com/auth/userinfo.email', 'openid'])

    def auth_url(self):
        """Provides URL for authentication.

        Returns:
            string. URL for user authentication with google account.
        """

        self.flow.redirect_uri = self.flow._OOB_REDIRECT_URI
        return self.flow.authorization_url(prompt = 'consent')

    def get_credentials(self, authorization_code):
        """"Returns user credentials

        Credentials can be used to get access to all google services (APIs)

        Args:
            authorization_code (str): Once the authorization is complete the
                authorization server will give the user a code. The user then must
                copy & paste this code into the application. The code is then
                exchanged for a token.

        Returns:
            google.oauth2.credentials.Credentials: The OAuth 2.0 credentials
                for the user.
        """

        if not authorization_code:
            return

        # Fetch token in exchange for authorization code.
        self.flow.fetch_token(code = authorization_code)
        return self.flow.credentials

    def validate_and_get_user_email(self, authorization_code):
        """"Validates user and returns their email address.

        Args:
            authorization_code (str): Once the authorization is complete the
                authorization server will give the user a code. The user then must
                copy & paste this code into the application. The code is then
                exchanged for a token.

        Returns:
            string: Authorized user's email address.
        """

        # Building oauth 2.0 service.
        oauth2 = build('oauth2', 'v2', credentials = self.get_credentials(
            authorization_code))

        # Executing api request.
        user_info = oauth2.userinfo().get().execute()

        if user_info['verified_email'] == False:
            raise UserNotValidatedException

        return user_info['email']


class UserNotValidatedException(Exception):
    """Raised when user tries to validate using a non-validated google account.

    Attributes:
        expression -- input expression in which the error occurred.
        message -- explanation why exception is raised.
    """

    def __init__(self, expression, message):
        self.expression = expression
        self.message = 'The users google account is not verified yet.'
