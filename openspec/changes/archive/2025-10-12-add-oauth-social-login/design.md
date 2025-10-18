# OAuth Support and Social Login - Technical Design

## Context

The application currently uses Emmett's built-in Auth module for traditional username/password authentication. We need to add OAuth2 social login support while maintaining backward compatibility with existing authentication.

### Background
- Emmett framework provides Auth extension with session-based authentication
- Current auth stores username/password in database with hashed passwords
- No existing OAuth infrastructure
- Need to support multiple OAuth providers (Google, GitHub, Microsoft, Facebook)
- Must maintain existing user accounts and authentication

### Constraints
- Emmett framework patterns and conventions must be followed
- Must use pyDAL ORM for database operations
- Must maintain backward compatibility with existing auth
- Security is paramount (OAuth tokens, PKCE, state validation)
- Should follow OAuth2 and OpenID Connect best practices

### Stakeholders
- **End Users**: Want easy, secure login without creating new accounts
- **Developers**: Need clear patterns for adding new OAuth providers
- **Admins**: Need visibility into OAuth connections and ability to manage them
- **Security Team**: Need assurance that OAuth implementation follows best practices

## Goals / Non-Goals

### Goals
- ✅ Implement OAuth2 authorization code flow with PKCE
- ✅ Support at least 4 major providers (Google, GitHub, Microsoft, Facebook)
- ✅ Allow new user registration via OAuth
- ✅ Allow existing users to link OAuth accounts
- ✅ Securely store and refresh OAuth tokens
- ✅ Provide seamless UX with one-click social login
- ✅ Maintain backward compatibility with username/password auth
- ✅ Follow security best practices (PKCE, state validation, encrypted tokens)
- ✅ Enable future API integrations via stored OAuth tokens

### Non-Goals
- ❌ OAuth1.0a support (deprecated, rarely used)
- ❌ SAML/SSO enterprise authentication (separate feature)
- ❌ Custom OAuth provider UI (use provider-hosted consent screens)
- ❌ OAuth token usage for third-party API calls (future feature)
- ❌ Social sharing features (separate from authentication)
- ❌ Migration of existing password accounts to OAuth-only (users keep both options)

## Technical Decisions

### Decision 1: OAuth Library

**Choice**: Use **Authlib** for OAuth2/OIDC implementation

**Rationale**:
- Industry-standard Python OAuth library
- Supports OAuth2 and OpenID Connect
- Built-in PKCE support
- Well-documented with good examples
- Active maintenance and security updates
- Works well with any WSGI/ASGI framework (Emmett compatible)

**Alternatives Considered**:
- **requests-oauthlib**: Lower-level, requires more manual implementation
- **python-social-auth**: Django-focused, harder to adapt to Emmett
- **Roll our own**: Too risky for security-critical code

**Implementation**:
```python
from authlib.integrations.base_client import OAuthError
from authlib.jose import jwt
from authlib.common.security import generate_token

# Will be used for:
# - Authorization URL generation with PKCE
# - Token exchange
# - Token validation
# - JWKS key fetching for OpenID Connect
```

### Decision 2: Database Schema

**Choice**: Separate `OAuthProvider` and `OAuthToken` models

**Schema**:
```python
class OAuthProvider(Model):
    tablename = "oauth_providers"
    
    user_id = Field.reference('auth_user')  # Links to Emmett Auth user
    provider = Field.string()  # 'google', 'github', 'microsoft', 'facebook'
    provider_user_id = Field.string()  # User ID from provider
    email = Field.string()
    name = Field.string()
    avatar_url = Field.string()
    created_at = Field.datetime()
    last_login_at = Field.datetime()
    
    # Unique constraint on (provider, provider_user_id)
    # Index on (user_id, provider)

class OAuthToken(Model):
    tablename = "oauth_tokens"
    
    provider_id = Field.reference('oauth_providers')
    access_token = Field.text()  # Encrypted
    refresh_token = Field.text()  # Encrypted
    token_type = Field.string()
    expires_at = Field.datetime()
    scope = Field.string()
    created_at = Field.datetime()
    updated_at = Field.datetime()
    
    # Index on (provider_id, expires_at)
```

**Rationale**:
- Separates provider identity from token storage
- Allows multiple OAuth providers per user
- Tokens can be rotated without touching provider data
- Enables token refresh background jobs
- Clear separation of concerns

**Alternatives Considered**:
- **Single table**: Would mix identity and token data, harder to manage
- **Embed tokens in user table**: Doesn't scale to multiple providers
- **External token store (Redis)**: Overkill for current scale, harder to manage

### Decision 3: OAuth Provider Abstraction

**Choice**: Abstract base class with provider-specific implementations

**Structure**:
```python
# runtime/oauth/base.py
class BaseOAuthProvider:
    provider_name: str
    authorize_url: str
    token_url: str
    user_info_url: str
    scopes: List[str]
    
    def get_authorization_url(self, redirect_uri: str, state: str) -> Tuple[str, str]:
        """Returns (url, code_verifier)"""
        pass
    
    def exchange_code(self, code: str, redirect_uri: str, code_verifier: str) -> Dict:
        """Exchange auth code for tokens"""
        pass
    
    def get_user_info(self, access_token: str) -> Dict:
        """Fetch user profile from provider"""
        pass
    
    def refresh_token(self, refresh_token: str) -> Dict:
        """Refresh access token"""
        pass

# runtime/oauth/google.py
class GoogleOAuthProvider(BaseOAuthProvider):
    provider_name = 'google'
    authorize_url = 'https://accounts.google.com/o/oauth2/v2/auth'
    token_url = 'https://oauth2.googleapis.com/token'
    user_info_url = 'https://www.googleapis.com/oauth2/v2/userinfo'
    scopes = ['openid', 'email', 'profile']
    
    # Provider-specific implementations...
```

**Rationale**:
- Easy to add new providers (extend base class)
- Consistent interface across all providers
- Provider-specific logic encapsulated
- Testable with mocks
- Clear contract for what each provider must implement

**Alternatives Considered**:
- **Configuration-driven**: Too rigid, doesn't handle provider quirks
- **Monolithic class**: Hard to maintain, violates single responsibility
- **Separate modules without base class**: Inconsistent, harder to test

### Decision 4: Security - PKCE Implementation

**Choice**: Use PKCE (Proof Key for Code Exchange) for all OAuth flows

**Implementation**:
```python
import secrets
import hashlib
import base64

def generate_pkce_pair():
    # Generate code_verifier (43-128 characters)
    code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
    
    # Generate code_challenge (SHA256 hash of verifier)
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode('utf-8')).digest()
    ).decode('utf-8').rstrip('=')
    
    return code_verifier, code_challenge

# Store code_verifier in session
# Send code_challenge in authorization request
# Send code_verifier in token exchange request
```

**Rationale**:
- Protects against authorization code interception attacks
- Required for public clients (mobile apps, SPAs) but good practice for all
- Recommended by OAuth 2.1 spec
- No server-side secret needed (works with client-side code)

**Security Benefits**:
- Prevents authorization code replay attacks
- Protects against man-in-the-middle attacks
- No need to store client secrets in client-side code

### Decision 5: Token Storage - Encryption at Rest

**Choice**: Encrypt OAuth tokens before storing in database

**Implementation**:
```python
from cryptography.fernet import Fernet

# Generate and store encryption key securely
OAUTH_TOKEN_ENCRYPTION_KEY = os.environ.get('OAUTH_TOKEN_ENCRYPTION_KEY')
cipher = Fernet(OAUTH_TOKEN_ENCRYPTION_KEY)

def encrypt_token(token: str) -> str:
    return cipher.encrypt(token.encode()).decode()

def decrypt_token(encrypted: str) -> str:
    return cipher.decrypt(encrypted.encode()).decode()

# Use in model methods
class OAuthToken(Model):
    def set_access_token(self, token: str):
        self.access_token = encrypt_token(token)
    
    def get_access_token(self) -> str:
        return decrypt_token(self.access_token)
```

**Rationale**:
- Protects tokens if database is compromised
- Industry best practice for sensitive credentials
- Relatively small performance overhead
- Easy to implement with Fernet (symmetric encryption)

**Alternatives Considered**:
- **Plain text storage**: Unacceptable security risk
- **External secrets manager (Vault)**: Overkill for current scale
- **OS keyring**: Doesn't work in containerized environments

### Decision 6: Account Linking Strategy

**Choice**: Automatic linking for matching verified emails, manual linking otherwise

**Flow**:
```python
def handle_oauth_callback(provider, code):
    # Exchange code for token
    # Get user info from provider
    
    oauth_account = OAuthProvider.where(
        lambda p: (p.provider == provider) & (p.provider_user_id == user_info['id'])
    ).first()
    
    if oauth_account:
        # Existing OAuth account - log in
        user = oauth_account.user
        login_user(user)
    else:
        # Check if email matches existing user
        user = User.where(lambda u: u.email == user_info['email']).first()
        
        if user and user_info.get('email_verified'):
            # Email verified by provider - auto-link
            create_oauth_provider(user, provider, user_info)
            login_user(user)
        elif user:
            # Email not verified - require manual linking
            session['pending_oauth_link'] = user_info
            redirect(url('link_accounts'))
        else:
            # New user - create account
            user = create_user_from_oauth(user_info)
            create_oauth_provider(user, provider, user_info)
            login_user(user)
```

**Rationale**:
- Auto-linking for verified emails improves UX
- Manual linking for unverified emails prevents account takeover
- Clear security boundary (email verification)
- Handles all scenarios (new user, existing user, existing OAuth)

**Security Considerations**:
- Only auto-link if provider confirms email is verified
- Show clear UI when manual linking is required
- Require current password for manual linking
- Log all account linking events for audit

### Decision 7: Token Refresh Strategy

**Choice**: Lazy refresh on use + background job for proactive refresh

**Implementation**:
```python
def get_valid_access_token(oauth_provider):
    token = oauth_provider.token
    
    # Check if token is expired or expiring soon (5 min buffer)
    if token.expires_at < now() + timedelta(minutes=5):
        # Refresh token
        provider = get_provider_instance(oauth_provider.provider)
        new_tokens = provider.refresh_token(token.refresh_token)
        
        # Update stored tokens
        token.update_record(
            access_token=encrypt_token(new_tokens['access_token']),
            refresh_token=encrypt_token(new_tokens.get('refresh_token', token.refresh_token)),
            expires_at=now() + timedelta(seconds=new_tokens['expires_in'])
        )
    
    return decrypt_token(token.access_token)

# Background job (run every hour)
@app.command('refresh_oauth_tokens')
async def refresh_expiring_tokens():
    expiring_soon = OAuthToken.where(
        lambda t: (t.expires_at < now() + timedelta(hours=2)) & (t.refresh_token != None)
    ).select()
    
    for token in expiring_soon:
        try:
            get_valid_access_token(token.provider)
        except Exception as e:
            logger.error(f"Failed to refresh token for {token.provider_id}: {e}")
```

**Rationale**:
- Lazy refresh ensures tokens are fresh when needed
- Background job reduces user-facing refresh latency
- 5-minute buffer prevents race conditions
- Graceful degradation if refresh fails

**Alternatives Considered**:
- **Only lazy refresh**: Higher latency on first use after expiry
- **Only background jobs**: More complex scheduling, harder to guarantee freshness
- **Never refresh**: Unacceptable UX (users forced to re-authenticate)

### Decision 8: Route Structure

**Choice**: RESTful routes under `/auth/oauth/` prefix

**Routes**:
```python
# Initiate OAuth flow
GET /auth/oauth/<provider>/login
    -> Generate state, PKCE challenge
    -> Store in session
    -> Redirect to provider authorization URL

# OAuth callback
GET /auth/oauth/<provider>/callback?code=xxx&state=xxx
    -> Validate state
    -> Exchange code for token (with PKCE verifier)
    -> Create/link account
    -> Log in user

# Link OAuth account to existing user
GET /auth/oauth/<provider>/link
    -> Requires authenticated user
    -> Initiate OAuth flow with link intent

# Unlink OAuth account
POST /auth/oauth/<provider>/unlink
    -> Requires authenticated user
    -> Validate user has another auth method
    -> Remove OAuth provider

# OAuth error page
GET /auth/oauth/error?message=xxx&provider=xxx
    -> Display user-friendly error
```

**Rationale**:
- Clear, predictable URL structure
- RESTful conventions
- Easy to extend for new providers
- Separates concerns (login vs link vs unlink)

## Risks / Trade-offs

### Risk 1: Provider API Changes
**Risk**: OAuth providers change their APIs, breaking our integration
**Likelihood**: Medium
**Impact**: High (login fails for all users of that provider)
**Mitigation**:
- Use versioned API endpoints when available
- Monitor provider developer blogs/changelogs
- Implement graceful degradation (fallback to password auth)
- Add comprehensive error logging
- Set up automated testing against provider APIs (within rate limits)

### Risk 2: Token Security
**Risk**: OAuth tokens are high-value targets for attackers
**Likelihood**: Low (if properly implemented)
**Impact**: Critical (account takeover, data access)
**Mitigation**:
- Encrypt tokens at rest
- Use HTTPS only (enforce in production)
- Implement token revocation on suspicious activity
- Short token lifetimes with refresh
- Audit logging for all token operations
- Rate limiting on OAuth endpoints

### Risk 3: Email Conflicts
**Risk**: User tries to link OAuth with email that matches existing account
**Likelihood**: Medium
**Impact**: Low-Medium (UX friction, support tickets)
**Mitigation**:
- Clear UI explaining email conflict
- Require email verification or password for linking
- Provide clear steps to resolve conflict
- Allow users to change email if needed

### Risk 4: Provider Outages
**Risk**: OAuth provider is down, users can't log in
**Likelihood**: Low (providers are highly available)
**Impact**: Medium (users with OAuth-only can't log in)
**Mitigation**:
- Always allow password-based auth as fallback
- Show clear error message when provider is down
- Implement retry logic with exponential backoff
- Cache provider metadata (OIDC discovery)
- Consider setting up fallback providers

### Risk 5: Scope Creep
**Risk**: Users grant too many permissions, privacy concerns
**Likelihood**: Low (if we're careful)
**Impact**: Medium (user trust, privacy violations)
**Mitigation**:
- Request minimal scopes (email, profile only)
- Clear explanation of why each scope is needed
- Never request write access unless explicitly needed
- Follow provider guidelines for scope requests
- Regular privacy audits

### Trade-off 1: Security vs UX
**Tension**: PKCE and state validation add complexity and potential failure points
**Decision**: Prioritize security, optimize UX within security constraints
**Justification**: Account security is non-negotiable, but we can make secure flows seamless with good UX design

### Trade-off 2: Auto-linking vs Manual Linking
**Tension**: Auto-linking is convenient but has account takeover risks if email not verified
**Decision**: Auto-link only for verified emails, require manual linking otherwise
**Justification**: Security takes precedence, but verified emails are safe to auto-link

### Trade-off 3: Token Storage Location
**Tension**: Database vs external secrets manager vs in-memory cache
**Decision**: Encrypted database storage with in-memory caching
**Justification**: Simpler deployment, acceptable security with encryption, good performance with caching

## Migration Plan

### Phase 1: Setup (Week 1)
- Add authlib dependency
- Create OAuth models and migrations
- Set up provider configurations
- Create base OAuth provider class

### Phase 2: Google Implementation (Week 2)
- Implement Google OAuth provider
- Create OAuth routes and handlers
- Add basic UI (login buttons)
- Test Google OAuth flow end-to-end

### Phase 3: Additional Providers (Week 3)
- Implement GitHub OAuth provider
- Implement Microsoft OAuth provider
- Implement Facebook OAuth provider
- Test all provider flows

### Phase 4: Account Management (Week 4)
- Implement account linking
- Implement account unlinking
- Create account settings UI
- Test all linking scenarios

### Phase 5: Security & Testing (Week 5)
- Security audit (PKCE, state, tokens)
- Comprehensive testing
- Rate limiting
- Error handling
- Performance testing

### Phase 6: Production (Week 6)
- Documentation
- Monitoring setup
- Production OAuth app registration
- Deployment
- User communication

### Rollback Strategy
- Database migrations are reversible
- Feature can be disabled via config without code rollback
- OAuth routes can be disabled without affecting password auth
- If critical issue found, remove OAuth buttons from UI (password auth still works)

## Open Questions

1. **Q**: Should we support OAuth for API authentication (bearer tokens)?
   **A**: Not in this phase. Focus on web authentication first. API auth can be future enhancement.

2. **Q**: Should we allow OAuth-only accounts (no password)?
   **A**: Yes, but strongly encourage setting a password as backup. Show warning if no password set.

3. **Q**: How long should we keep unused OAuth tokens?
   **A**: 90 days of inactivity. Background job to clean up expired/unused tokens.

4. **Q**: Should we support custom OAuth providers (enterprise SSO)?
   **A**: Not in this phase. Start with public providers. Custom providers can be Phase 2.

5. **Q**: Should we display which OAuth providers are connected on user profile?
   **A**: Yes, in account settings. Show connection status and last login time.

6. **Q**: What happens if user deletes their account with OAuth provider?
   **A**: Token refresh will fail. Show error and suggest account unlinking or setting password.

7. **Q**: Should we support linking multiple accounts from same provider?
   **A**: No. One account per provider per user. Reduces complexity and confusion.

8. **Q**: How do we handle username conflicts?
   **A**: Generate username from email (part before @) with number suffix if needed. Allow user to change later.

## Success Metrics

### Launch Metrics (First 30 Days)
- % of new users signing up via OAuth (target: >40%)
- % of existing users linking OAuth accounts (target: >20%)
- OAuth flow completion rate (target: >85%)
- OAuth error rate (target: <5%)
- Support tickets related to OAuth (target: <10)

### Long-term Metrics (90 Days)
- % of logins via OAuth vs password (track trend)
- Token refresh success rate (target: >95%)
- Average login time (should decrease with OAuth)
- Password reset requests (should decrease)
- User satisfaction with login experience (survey)

### Technical Metrics
- OAuth endpoint response time (target: <500ms p95)
- Token refresh latency (target: <1s p95)
- OAuth callback success rate (target: >95%)
- Security incidents related to OAuth (target: 0)

