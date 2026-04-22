# CodeGame POC - Security Setup Guide

## 🔐 Secure Configuration with Environment Variables

This project uses **environment variables** to manage sensitive credentials instead of hardcoding them in the repository.

### Setup Options

#### **Option 1: Using .env File (Local Development)**

1. Create a `.env` file in the project root:
```bash
cp .env.example .env
```

2. Edit `.env` and add your actual credentials:
```env
AZURE_DEVOPS_PAT=your_actual_pat_token
ENABLON_CLIENT_ID=your_client_id
ENABLON_CLIENT_SECRET=your_client_secret
```

**Note:** `.env` is in `.gitignore` and will NOT be committed to the repository.

#### **Option 2: Using Environment Variables (Recommended for CI/CD)**

**Windows PowerShell:**
```powershell
$env:AZURE_DEVOPS_PAT = "your_pat_token"
$env:ENABLON_CLIENT_ID = "your_client_id"
$env:ENABLON_CLIENT_SECRET = "your_client_secret"
```

**Windows Command Prompt:**
```cmd
set AZURE_DEVOPS_PAT=your_pat_token
set ENABLON_CLIENT_ID=your_client_id
set ENABLON_CLIENT_SECRET=your_client_secret
```

**Linux/Mac:**
```bash
export AZURE_DEVOPS_PAT="your_pat_token"
export ENABLON_CLIENT_ID="your_client_id"
export ENABLON_CLIENT_SECRET="your_client_secret"
```

#### **Option 3: Using Windows Credential Manager**

Store credentials securely in Windows Credential Manager and create a helper script.

### How It Works

The code automatically looks for credentials in this order:

1. **Environment Variables** (highest priority)
   ```python
   PAT = os.getenv('AZURE_DEVOPS_PAT')
   ```

2. **.env File** (if present)
   ```python
   from dotenv import load_dotenv
   load_dotenv()
   ```

3. **Placeholder** (development fallback)
   ```python
   PAT = "YOUR_PAT_TOKEN"
   ```

### Getting Your Credentials

#### Azure DevOps PAT

1. Go to https://dev.azure.com
2. Click your profile icon → Personal access tokens
3. Create new token with:
   - Name: CodeGame
   - Scopes: Work Items (Read & Write)
   - Expiration: 1 year
4. Copy the token to your `.env` file

#### Enablon API Credentials

1. Obtain credentials from Enablon API portal
2. Add to `.env`:
   ```env
   ENABLON_CLIENT_ID=your_id
   ENABLON_CLIENT_SECRET=your_secret
   ```

### Running the Application

```bash
# If using .env file
python batch_agent.py 791842

# If using environment variables
python batch_agent.py 791842
```

### Security Best Practices

✅ **DO:**
- Use `.env` for local development
- Use environment variables in production
- Store credentials in secure vaults (GitHub Secrets, Azure Key Vault, etc.)
- Rotate credentials regularly
- Use .gitignore to prevent accidental commits

❌ **DON'T:**
- Hardcode secrets in source code
- Commit `.env` file to repository
- Share credentials via email or chat
- Use old/expired tokens

### GitHub Actions Integration (Optional)

For CI/CD pipelines, add secrets to GitHub:

```yaml
env:
  AZURE_DEVOPS_PAT: ${{ secrets.AZURE_DEVOPS_PAT }}
  ENABLON_CLIENT_ID: ${{ secrets.ENABLON_CLIENT_ID }}
  ENABLON_CLIENT_SECRET: ${{ secrets.ENABLON_CLIENT_SECRET }}
```

---

**More Questions?** Check the individual Python files for inline documentation.
