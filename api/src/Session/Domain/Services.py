from uuid import UUID
from typing import List
from src.Session.Domain.Models import Session


class SessionValidationService:
    @staticmethod
    def ValidateSession(
        session: Session,
        userId: UUID,
        requiredScopes: List[str],
        clientId: UUID,
        codeChallenge: str,
        authenticationMethod: str,
    ) -> None:
        # Check if the session belongs to the user
        if session.userId != userId:
            raise ValueError("Session does not belong to the user")

        # Check if the session has all required scopes
        if not session.HasAllScopes(requiredScopes):
            raise ValueError("Session does not have all required scopes")

        # Check if the session is revoked
        if not session.IsActive():
            raise ValueError("Session is revoked")

        # Check if the clientId matches
        if session.clientId != clientId:
            raise ValueError("Client ID does not match")

        # Check if the codeChallenge matches
        if session.codeChallenge != codeChallenge:
            raise ValueError("Code challenge does not match")

        # Check if the authentication method matches
        if session.authenticationMethod.value != authenticationMethod:
            raise ValueError("Authentication method does not match")
