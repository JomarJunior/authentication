from enum import Enum


class AuthenticationMethodEnum(str, Enum):
    PASSWORD = "password"
    MFA = "mfa"
    GOOGLE = "social:google"
    FACEBOOK = "social:facebook"
    GITHUB = "social:github"
    TWITTER = "social:twitter"
