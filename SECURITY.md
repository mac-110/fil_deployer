# Security

## Token Encryption

### Overview

Sensitive data (GitLab and Artifactory tokens) in `config/app_config.json` are automatically encrypted at rest using **Fernet symmetric encryption** from the `cryptography` library.

### How It Works

1. **Encryption Algorithm**: Fernet (AES-128-CBC with HMAC authentication)
2. **Key Derivation**: PBKDF2-HMAC-SHA256 with 100,000 iterations
3. **Automatic Encryption**: Tokens are encrypted when saved, decrypted when loaded
4. **Backward Compatible**: Existing plaintext tokens are automatically encrypted on first save

### Architecture

```
┌─────────────────────┐
│  User enters token  │
│   via Settings UI   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   API receives      │
│   plaintext token   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────┐
│  app_config.py              │
│  ├─ Encrypts with Fernet    │
│  └─ Saves to JSON           │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  config/app_config.json     │
│  {                          │
│    "gitlab_group_token":    │
│      "gAAAAABl..."          │  ← Encrypted!
│  }                          │
└──────────┬──────────────────┘
           │
           ▼ (on read)
┌─────────────────────────────┐
│  app_config.py              │
│  ├─ Loads from JSON         │
│  ├─ Detects encrypted token │
│  └─ Decrypts with Fernet    │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────┐
│  Application uses   │
│  decrypted token    │
└─────────────────────┘
```

### Files Involved

- `backend/app/crypto_utils.py` - Encryption/decryption logic
- `backend/app/app_config.py` - Config manager with automatic encryption
- `config/app_config.json` - Storage file (tokens encrypted)

### Encryption Key

The encryption key is derived from a secret using PBKDF2:

```python
Secret → PBKDF2-HMAC-SHA256 (100k iterations) → Fernet Key
```

#### Configuration via Environment Variable

The encryption secret can be configured via the `ENCRYPTION_SECRET` environment variable:

**Method 1: Environment Variable (Recommended for Production)**
```bash
# Set in your environment
export ENCRYPTION_SECRET="your-super-secret-encryption-key"

# Or in .env file
echo "ENCRYPTION_SECRET=your-super-secret-encryption-key" >> .env
```

**Method 2: Docker Compose**
```yaml
environment:
  - ENCRYPTION_SECRET=${ENCRYPTION_SECRET}
```

**Generate a Strong Secret:**
```bash
# Generate a random 32-byte secret
openssl rand -base64 32
```

#### Fallback Behavior

If `ENCRYPTION_SECRET` is not set, the application will:
1. ⚠️  Display a warning in logs
2. Use a default secret (not recommended for production)

**Always set a custom `ENCRYPTION_SECRET` in production!**

#### Key Rotation

To rotate encryption keys:

1. **Export existing tokens** (they're encrypted with old key)
2. **Set new `ENCRYPTION_SECRET`**
3. **Re-enter tokens** via Settings UI (will encrypt with new key)
4. **Restart application**

⚠️ **Warning:** Changing `ENCRYPTION_SECRET` will make existing encrypted tokens unreadable!

### Example

**Before Encryption** (`app_config.json`):
```json
{
  "gitlab_url": "https://code.swisscom.com",
  "gitlab_group_token": "glpat-xxxxxxxxxxxxxxxxxxxx",
  "artifactory_url": "https://bin.swisscom.com",
  "artifactory_token": "AKCp8xxxxxxxxxxxxxxxxx"
}
```

**After Encryption** (`app_config.json`):
```json
{
  "gitlab_url": "https://code.swisscom.com",
  "gitlab_group_token": "gAAAAABl2Kx8vQ9Z...",
  "artifactory_url": "https://bin.swisscom.com",
  "artifactory_token": "gAAAAABl2Kx9pR3A..."
}
```

### Migration

Existing plaintext tokens are automatically migrated:

1. On first read, tokens are loaded as-is (plaintext)
2. On next save, tokens are automatically encrypted
3. All subsequent reads decrypt the tokens transparently

No manual migration needed!

### Security Benefits

✅ **At-Rest Protection**: Tokens are encrypted in the file system
✅ **Automatic**: No manual encryption needed
✅ **Transparent**: Application code doesn't change
✅ **HMAC Authentication**: Prevents tampering
✅ **Standard Algorithm**: Uses industry-standard Fernet

### Limitations

⚠️ **Not End-to-End**: Tokens are decrypted in application memory
⚠️ **Single Key**: All tokens use the same encryption key
⚠️ **Key Rotation**: Changing encryption key requires re-entering all tokens

### Best Practices

For production deployment:

1. **✅ Set `ENCRYPTION_SECRET`**: Always use a custom encryption secret via environment variable
   ```bash
   export ENCRYPTION_SECRET=$(openssl rand -base64 32)
   ```

2. **🔒 Keep Secret Secure**: Never commit `.env` file to git
   ```bash
   echo ".env" >> .gitignore
   ```

3. **🔄 Rotate Keys Periodically**: Implement key rotation strategy
   - Backup existing tokens before rotation
   - Set new `ENCRYPTION_SECRET`
   - Re-enter all tokens via UI

4. **📁 Access Control**: Restrict file system access to `config/` directory
   ```bash
   chmod 600 config/app_config.json
   ```

5. **🔐 Secrets Management**: For enterprise deployments, consider:
   - HashiCorp Vault
   - AWS Secrets Manager
   - Azure Key Vault
   - Google Cloud Secret Manager

6. **📊 Audit Logging**: Log all token access/modifications (future enhancement)

### Testing Encryption

You can verify encryption is working by:

1. Set a token via Settings UI
2. Check `config/app_config.json` - should see `gAAAAAB...` format
3. Restart application - token should still work (decryption successful)

### Troubleshooting

**"Failed to decrypt token"** error:
- Token was encrypted with different key
- File corruption
- Solution: Delete `app_config.json` and re-enter tokens

**Tokens not encrypting**:
- Check `cryptography` library is installed
- Verify `backend/requirements.txt` includes `cryptography==41.0.7`
- Run `pip install -r backend/requirements.txt`

## Additional Security Measures

### Authentication

- Session-based authentication with secure cookies
- Password hashing with secure algorithms
- Admin-only access to sensitive operations

### CORS

- Restricted to configured frontend URL
- Credentials support enabled
- Prevents unauthorized cross-origin requests

### Input Validation

- Pydantic models validate all API inputs
- CSV parsing with error handling
- GitLab/Artifactory API validation

### Future Improvements

- [ ] Move encryption key to environment variable
- [ ] Implement key rotation
- [ ] Add audit logging for token access
- [ ] Consider HSM for key storage
- [ ] Implement token expiration/refresh
- [ ] Add rate limiting for API endpoints
