# Security Migration Guide - Miles AI System

## 🚨 IMMEDIATE ACTIONS REQUIRED

This guide helps you migrate from the insecure hardcoded credentials to environment-based security.

### Step 1: Create Your .env File

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` and add your actual credentials:
```env
# X (Twitter) API Credentials
TWITTER_API_KEY=your_actual_api_key_here
TWITTER_API_SECRET=your_actual_api_secret_here
TWITTER_BEARER_TOKEN=your_actual_bearer_token_here
```

3. **IMPORTANT**: Never commit `.env` to Git! It's already in `.gitignore`.

### Step 2: Update Your Code

Replace all imports of the old credentials:

**OLD (INSECURE):**
```python
from config.credentials import TwitterCredentials

creds = TwitterCredentials(
    api_key="hardcoded_key",
    api_key_secret="hardcoded_secret",
    bearer_token="hardcoded_token"
)
```

**NEW (SECURE):**
```python
from config.secure_credentials import get_twitter_credentials

creds = get_twitter_credentials()
```

### Step 3: Use the Secure Server

Instead of running the old server:
```bash
python miles_ai_simple_server.py
```

Run the new secure server:
```bash
python miles_ai_secure_server.py
```

### Step 4: Update All Files Using Credentials

Files that need updating:
- `x_api_data_fetcher.py`
- `fetch_miles_tweets.py`
- `miles_1000_tweets_fetcher.py`
- Any other files importing from `config.credentials`

### Step 5: Test Security Features

1. Check if credentials are properly loaded:
```python
from config.secure_credentials import check_credential_security

security_check = check_credential_security()
if security_check['secure']:
    print("✓ All credentials properly configured")
else:
    print("Issues found:", security_check['issues'])
```

2. Test input validation:
```python
from src.core.input_validator import InputValidator

validator = InputValidator()
safe_text = validator.sanitize_text("<script>alert('xss')</script>Hello")
print(safe_text)  # Output: &lt;script&gt;alert('xss')&lt;/script&gt;Hello
```

### Step 6: Deploy with Security

When deploying to production:

1. Set environment variables on your server:
```bash
export TWITTER_API_KEY="your_key"
export TWITTER_API_SECRET="your_secret"
export TWITTER_BEARER_TOKEN="your_token"
export SECRET_KEY="generate_random_key_here"
export JWT_SECRET_KEY="generate_another_random_key"
```

2. Use a proper secret generator:
```python
import secrets
print(secrets.token_urlsafe(32))  # For SECRET_KEY
print(secrets.token_urlsafe(32))  # For JWT_SECRET_KEY
```

### Security Checklist

- [ ] Created `.env` file with real credentials
- [ ] Removed all hardcoded credentials from code
- [ ] Updated all imports to use `secure_credentials.py`
- [ ] Generated random SECRET_KEY and JWT_SECRET_KEY
- [ ] Tested the secure server
- [ ] Verified input validation is working
- [ ] Confirmed `.env` is in `.gitignore`
- [ ] Deleted or archived old `credentials.py` file

### Additional Security Features

The new secure system includes:

1. **Input Validation**: All user inputs are sanitized
2. **Rate Limiting**: Prevents API abuse (60/min, 1000/hour)
3. **XSS Protection**: HTML content is escaped
4. **Request Size Limits**: Max 10KB per request
5. **Security Headers**: X-Frame-Options, X-Content-Type-Options, etc.

### Troubleshooting

**Error: "Missing required Twitter credentials"**
- Make sure your `.env` file exists and contains all required keys
- Check that you're in the correct directory when running the script

**Error: "Twitter credentials not properly configured"**
- Verify your API keys are correct (not the example values)
- Ensure no extra spaces in your `.env` file

**Rate limiting issues**
- Default: 60 requests/minute, 1000/hour
- Adjust in `.env`: `RATE_LIMIT_PER_MINUTE=120`

### Next Steps

After completing the security migration:

1. Archive the old `config/credentials.py` file
2. Update your deployment scripts to use environment variables
3. Consider implementing additional security measures:
   - API key rotation
   - Monitoring and alerting
   - Web Application Firewall (WAF)

## Need Help?

If you encounter issues during migration:
1. Check the error messages carefully
2. Verify all environment variables are set
3. Review the `config/secure_credentials.py` file for usage examples

Remember: **Security is not optional** in production systems!