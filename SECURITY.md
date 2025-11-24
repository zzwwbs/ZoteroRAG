# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability, please email the maintainers directly rather than opening a public issue. This helps protect users while a fix is being developed.

**Please include:**
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | ✅ Active support  |
| 0.x.x   | ⚠️ Beta - limited  |

## API Key Security

**Best Practices:**
- ✅ The app uses OS keyring by default (macOS Keychain, Windows Credential Manager)
- ✅ API keys are stored in `~/.zotero_rag/settings.json` as fallback
- ✅ This directory is outside the git repository
- ⚠️ **Never commit files from `~/.zotero_rag/` to version control**
- ⚠️ **Exclude `~/.zotero_rag/` from cloud backups if it contains API keys**
- ⚠️ **Rotate keys immediately if accidentally exposed**

**Environment Variables:**
- `OPENAI_API_KEY` is used as fallback if no stored key exists
- Set this in your shell profile, not in committed files

**If Keys Are Compromised:**
1. Immediately revoke the key in your API provider dashboard
2. Generate a new key
3. Update the key in the app Settings tab
4. Check your API usage logs for suspicious activity

## Data Storage

All user data is stored locally in `~/.zotero_rag/`:
- `settings.json` - Configuration (may contain API keys if keyring unavailable)
- `zoterorag.db` - Metadata, chunks, token usage
- `zoterorag.faiss` - Vector index
- `debug.log` - Application logs

**Privacy:** This app does not send data anywhere except:
- To your configured embedding/chat API endpoints
- No telemetry, no tracking, no data collection

## Dependencies

We regularly update dependencies to patch security vulnerabilities. If you find a vulnerable dependency:
1. Open an issue with CVE details
2. We'll prioritize the update
3. A patched release will be published ASAP
