# OAuth2 and Social Login

## Why

Currently, the application only supports traditional email/password authentication. This creates several pain points:
- **User friction**: Users must create yet another account with password
- **Security burden**: Users reuse passwords across sites, creating vulnerabilities
- **No social features**: Cannot leverage social connections and profiles
- **Limited reach**: Some users prefer or expect social login options
- **Recovery complexity**: Password reset flows are cumbersome
- **Trust barrier**: Users hesitate to trust new sites with passwords

Implementing OAuth2 and social login will:
- **Reduce friction**: One-click signup using existing accounts
- **Improve security**: Leverage battle-tested OAuth providers, eliminate password storage
- **Increase conversions**: Users more likely to sign up with familiar social accounts
- **Enable social features**: Access to profile data, connections (with permission)
- **Build trust**: Users trust established providers (Google, GitHub, etc.)
- **Simplify management**: No password resets, account recovery handled by provider
- **Modern expectations**: OAuth is now standard in modern applications

## What Changes

- Implement OAuth2 authorization code flow with PKCE (Proof Key for Code Exchange)
- Support multiple OAuth providers: Google, GitHub, Microsoft, Facebook
- Create OAuth provider configuration system
- Add account linking (connect OAuth to existing email/password accounts)
- Implement secure token storage with encryption at rest
- Add automatic token refresh mechanism
- Create OAuth callback handlers with state validation
- Add provider-specific account management UI
- Implement email conflict resolution (when OAuth email matches existing account)
- Add rate limiting on OAuth endpoints
- Support simultaneous password and OAuth authentication (hybrid accounts)
- Create admin interface for OAuth provider management
- Add comprehensive logging and monitoring for OAuth flows
- Implement graceful fallback when OAuth providers unavailable

### OAuth Providers

#### Google OAuth
- Use Google Identity Platform
- Scopes: `openid email profile`
- PKCE required for security
- Support Google One Tap

#### GitHub OAuth
- Use GitHub OAuth Apps
- Scopes: `user:email` (read-only)
- Additional scopes available for future features
- Leverage GitHub's developer community

#### Microsoft OAuth
- Use Microsoft Identity Platform (Azure AD)
- Scopes: `openid email profile`
- Support personal, work, and school accounts
- Integration with Microsoft ecosystem

#### Facebook Login
- Use Facebook Login for Web
- Scopes: `email public_profile`
- Handle edge cases (users without email)
- Support Facebook Platform policies

### Key Features

1. **Multi-Provider Support**:
   - Unified interface for all OAuth providers
   - Provider-specific customizations
   - Easy to add new providers
   - Per-provider enable/disable configuration

2. **Account Linking**:
   - Connect OAuth accounts to existing accounts
   - Multiple OAuth providers per user
   - Disconnect providers (with at least one auth method remaining)
   - Prevent account hijacking via email verification

3. **Security Best Practices**:
   - PKCE for authorization code flow
   - State parameter validation (CSRF protection)
   - Nonce validation for OpenID Connect
   - Token encryption at rest
   - Secure callback URL validation
   - Rate limiting to prevent abuse

4. **User Experience**:
   - Social login buttons on signup/login pages
   - Account connection page in settings
   - Visual indicators of connected accounts
   - Clear error messages for OAuth failures
   - Seamless fallback to password auth

5. **Token Management**:
   - Automatic refresh token rotation
   - Secure storage with encryption
   - Token expiration handling
   - Cleanup of expired tokens
   - Optional: Revoke tokens on logout

## Impact

### Affected Specs
- `auth` - **MODIFIED** to include OAuth2 flows and social login
- `auto-ui-generation` - **MODIFIED** to generate OAuth account management UI
- `error-tracking` - **MODIFIED** to handle OAuth-specific errors
- `permissions` - (Optional) **MODIFIED** to add OAuth scope-based permissions

### Affected Code
- `runtime/app.py`:
  - Add OAuth configuration and initialization
  - Add OAuth callback routes
  - Update auth pipeline for OAuth support
- `runtime/auth/` (new directory):
  - `oauth.py` - Core OAuth2 implementation
  - `providers/` - Provider-specific implementations
    - `google.py` - Google OAuth provider
    - `github.py` - GitHub OAuth provider
    - `microsoft.py` - Microsoft OAuth provider
    - `facebook.py` - Facebook OAuth provider
    - `base.py` - Base provider class
  - `tokens.py` - Token storage and encryption
  - `linking.py` - Account linking logic
- `runtime/models.py`:
  - Add `OAuthAccount` model for linked accounts
  - Add `OAuthToken` model for token storage
  - Update `User` model with OAuth methods
- `runtime/templates/`:
  - Update `auth/login.html` with social login buttons
  - Update `auth/signup.html` with social signup buttons
  - Add `auth/oauth_callback.html` for OAuth processing
  - Add `auth/account_settings.html` for managing connections
  - Add `auth/link_accounts.html` for account linking flow
- `runtime/static/`:
  - Add OAuth provider logos and icons
  - Add CSS for social login buttons
- Configuration:
  - Add OAuth provider credentials (client ID, secret)
  - Add redirect URL configuration
  - Add feature flags per provider
- Documentation:
  - OAuth setup guide for developers
  - User guide for account linking
  - Security documentation
  - Provider-specific setup instructions

### Compatibility
- **Non-breaking**: Existing password authentication continues to work
- **Backward compatible**: Users can continue using password-only accounts
- **Hybrid accounts**: Users can have both password and OAuth
- **Migration path**: Existing users can link OAuth accounts
- **Graceful degradation**: If OAuth unavailable, password login still works

### Benefits
- **Better conversion**: 20-40% higher signup rates with social login
- **Improved security**: No password storage vulnerabilities, provider-level security
- **Lower support burden**: Fewer password reset requests
- **Faster onboarding**: One-click signup reduces friction
- **Enhanced trust**: Users trust established providers
- **Future features**: Foundation for social features (connections, sharing)
- **Modern UX**: Meets user expectations for authentication options
- **Analytics opportunity**: Better user attribution and understanding
- **Competitive advantage**: Feature parity with modern applications
- **Reduced liability**: Less responsibility for password security

### Example User Flows

#### Flow 1: New User Signup with Google
1. User clicks "Sign up with Google" button
2. Redirected to Google consent screen
3. User approves access to email and profile
4. Google redirects back with authorization code
5. Backend exchanges code for tokens
6. User profile created with Google account linked
7. User logged in automatically

#### Flow 2: Existing User Links GitHub
1. Logged-in user goes to account settings
2. Clicks "Connect GitHub" button
3. Redirected to GitHub authorization
4. GitHub redirects back after approval
5. GitHub account linked to existing user
6. User can now login with either password or GitHub

#### Flow 3: Email Conflict Resolution
1. User tries to signup with Google (email: user@example.com)
2. Email already exists for password account
3. User shown option to link accounts
4. User logs in with password to verify ownership
5. Google account linked to existing user
6. User can now use either method

### Security Considerations

#### PKCE (Proof Key for Code Exchange)
- Generate code_verifier (random string)
- Create code_challenge from verifier
- Send challenge with authorization request
- Send verifier with token exchange
- Provider validates match
- Prevents authorization code interception

#### State Parameter
- Generate random state value
- Store in session
- Include in authorization request
- Validate on callback
- Prevents CSRF attacks

#### Token Security
- Encrypt access tokens at rest using Fernet
- Store refresh tokens separately
- Use secure random for token generation
- Implement token rotation on refresh
- Revoke tokens on suspicious activity

#### Redirect URL Validation
- Whitelist exact callback URLs
- Reject mismatched redirects
- Use HTTPS in production
- Validate URL structure

## Migration Plan

### Phase 1: Foundation (Week 1-2)
- Set up OAuth provider applications (Google, GitHub, Microsoft, Facebook)
- Create base OAuth provider class and interface
- Implement OAuth2 authorization code flow with PKCE
- Add OAuthAccount and OAuthToken models
- Create token encryption system
- Write unit tests for core OAuth logic

### Phase 2: Provider Integration (Week 2-3)
- Implement Google OAuth provider
- Implement GitHub OAuth provider
- Implement Microsoft OAuth provider
- Implement Facebook OAuth provider
- Test each provider's authorization and token flow
- Handle provider-specific edge cases

### Phase 3: Account Linking (Week 3-4)
- Implement account linking logic
- Add email conflict detection and resolution
- Create account linking UI
- Add ability to disconnect providers (with safety checks)
- Test linking scenarios and edge cases

### Phase 4: UI Integration (Week 4-5)
- Add social login buttons to login page
- Add social signup buttons to signup page
- Create OAuth callback processing page
- Create account settings page for OAuth management
- Add provider icons and styling
- Implement error handling and user feedback

### Phase 5: Security Hardening (Week 5-6)
- Implement state validation (CSRF protection)
- Add rate limiting on OAuth endpoints
- Implement secure token storage and encryption
- Add token refresh automation
- Perform security audit of OAuth flows
- Add comprehensive logging

### Phase 6: Testing & Documentation (Week 6-7)
- Write integration tests for all OAuth flows
- Test each provider thoroughly
- Test account linking scenarios
- Test security measures (PKCE, state validation)
- Test error handling and edge cases
- Write user documentation
- Write developer setup guide
- Document security considerations

### Phase 7: Monitoring & Deployment (Week 7-8)
- Add OAuth metrics to monitoring
- Add error tracking for OAuth failures
- Configure alerts for OAuth issues
- Perform load testing
- Deploy to staging environment
- User acceptance testing
- Deploy to production with feature flag
- Monitor for issues

## Risks & Mitigation

### Risk: OAuth provider downtime
- **Mitigation**: Always support password authentication as fallback, show clear error messages

### Risk: Provider policy changes
- **Mitigation**: Monitor provider announcements, maintain abstraction layer for easy swapping

### Risk: Token theft/compromise
- **Mitigation**: Encrypt tokens at rest, implement token rotation, use short-lived access tokens

### Risk: Account hijacking via OAuth
- **Mitigation**: Require email verification for linking, implement secondary authentication for sensitive actions

### Risk: User confusion about multiple auth methods
- **Mitigation**: Clear UI indicators, help documentation, account settings showing all methods

### Risk: GDPR/privacy compliance
- **Mitigation**: Clear consent flows, data minimization, allow users to disconnect providers

### Risk: Development complexity
- **Mitigation**: Use well-tested OAuth libraries, comprehensive testing, clear documentation

### Risk: Increased attack surface
- **Mitigation**: Security audit, rate limiting, monitoring, follow OAuth best practices

## OAuth Provider Setup Requirements

### Google OAuth
- Create project in Google Cloud Console
- Enable Google+ API
- Create OAuth 2.0 credentials
- Configure authorized redirect URIs
- Requires: Client ID, Client Secret

### GitHub OAuth
- Create OAuth App in GitHub Developer Settings
- Configure callback URL
- Requires: Client ID, Client Secret

### Microsoft OAuth
- Register app in Azure AD
- Configure redirect URIs
- Add required permissions
- Requires: Client ID, Client Secret, Tenant ID (optional)

### Facebook Login
- Create app in Facebook Developers
- Add Facebook Login product
- Configure OAuth redirect URIs
- Requires: App ID, App Secret

## Configuration Example

```python
# OAuth provider configuration
OAUTH_PROVIDERS = {
    'google': {
        'enabled': True,
        'client_id': os.environ.get('GOOGLE_CLIENT_ID'),
        'client_secret': os.environ.get('GOOGLE_CLIENT_SECRET'),
        'authorize_url': 'https://accounts.google.com/o/oauth2/v2/auth',
        'token_url': 'https://oauth2.googleapis.com/token',
        'userinfo_url': 'https://www.googleapis.com/oauth2/v2/userinfo',
        'scopes': ['openid', 'email', 'profile'],
        'button_text': 'Continue with Google',
        'icon': 'google-icon.svg'
    },
    'github': {
        'enabled': True,
        'client_id': os.environ.get('GITHUB_CLIENT_ID'),
        'client_secret': os.environ.get('GITHUB_CLIENT_SECRET'),
        'authorize_url': 'https://github.com/login/oauth/authorize',
        'token_url': 'https://github.com/login/oauth/access_token',
        'userinfo_url': 'https://api.github.com/user',
        'scopes': ['user:email'],
        'button_text': 'Continue with GitHub',
        'icon': 'github-icon.svg'
    },
    # ... Microsoft and Facebook configurations
}
```

## Success Metrics
- Signup conversion rate increase
- Percentage of users using OAuth vs password
- Number of linked accounts per user
- OAuth authentication failure rate
- Time to complete signup (should decrease)
- Support tickets related to authentication (should decrease)
- User satisfaction scores for authentication

## Open Questions
1. Should we support multiple OAuth accounts of the same provider (e.g., 2 Google accounts)?
2. Should we allow OAuth-only accounts (no password)?
3. How long should we store refresh tokens?
4. Should we implement "Login with X" on every page or just auth pages?
5. Should we support deferred account creation (OAuth without immediate signup)?
6. Do we need to support custom OAuth providers (enterprise)?
