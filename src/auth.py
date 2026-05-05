import asyncio
import logging

import httpx
import jwt
from mcp.server.auth.provider import AccessToken, TokenVerifier

logger = logging.getLogger("mealie-mcp.auth")


class WorkOSTokenVerifier(TokenVerifier):
    def __init__(self, issuer: str, resource: str):
        self._issuer = issuer.rstrip("/")
        self._resource = resource.rstrip("/")
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(f"{self._issuer}/.well-known/openid-configuration")
            resp.raise_for_status()
            jwks_uri = resp.json()["jwks_uri"]
        self._jwks_client = jwt.PyJWKClient(jwks_uri)

    async def verify_token(self, token: str) -> AccessToken | None:
        try:
            signing_key = await asyncio.to_thread(
                lambda: self._jwks_client.get_signing_key_from_jwt(token).key
            )
            claims = jwt.decode(
                token,
                signing_key,
                algorithms=["RS256"],
                issuer=self._issuer,
                options={"verify_aud": False},
            )
        except jwt.PyJWTError as e:
            logger.warning({"message": "Token verification failed", "error": str(e)})
            return None

        aud = claims.get("aud")
        if aud is not None:
            aud_list = aud if isinstance(aud, list) else [aud]
            if self._resource not in aud_list:
                logger.warning({"message": "Token audience mismatch", "aud": aud})
                return None

        scope_claim = claims.get("scope") or claims.get("scp") or ""
        if isinstance(scope_claim, list):
            scopes = scope_claim
        else:
            scopes = scope_claim.split() if scope_claim else []

        client_id = (
            claims.get("client_id") or claims.get("azp") or claims.get("sub", "")
        )
        exp = claims.get("exp")
        return AccessToken(
            token=token,
            client_id=str(client_id),
            scopes=scopes,
            expires_at=int(exp) if exp is not None else None,
            resource=self._resource,
        )
