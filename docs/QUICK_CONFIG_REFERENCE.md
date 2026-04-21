# FAB Agent Configuration - Quick Reference

## For azdo-reader-v2 Agent in FAB Studio

### Step-by-Step Configuration

#### Tab: Design

**Field: Base agent name**
```
Generic Prompt Agent With Tools
```

**Field: Base agent version**
```
0.54.0
```

**Field: Endpoint for OpenAPI Spec (Json / YAML)** ⚠️ THIS IS YOUR RED ERROR FIELD

Choose ONE of the following based on your setup:

**Option 1: GitHub Raw URL (RECOMMENDED)**
```
https://raw.githubusercontent.com/tushar270721/CodeGameRepo/main/apis/azdo-openapi-spec.yaml
```
✅ Use this if your repo is public on GitHub

**Option 2: Local Development Server**
```
http://localhost:8000/azdo-openapi-spec.yaml
```
✅ Use this during local development
Run: `python -m http.server 8000` in the `apis/` folder

**Option 3: Azure DevOps Hosted**
```
https://dev.azure.com/YOUR_ORG/YOUR_PROJECT/_apis/git/repositories/YOUR_REPO/items?path=/apis/azdo-openapi-spec.yaml&api-version=7.1
```
✅ Use this if hosted in your Azure DevOps project

---

**Field: System Message**
```
You are an Azure DevOps bug reader agent.

Your job:
1. Use Azure DevOps REST APIs
2. Read work item by ID
3. Validate content
4. Extract relevant information
5. Return structured JSON

Use these steps:
1. Authenticate using PAT token
2. Read work item by ID
3. Extract fields: ID, Title, Description, State, Tags, Priority, Comments
4. Return structured JSON with all extracted data
```

**Field: User Prompt**
```
[query]
```

---

#### Section: Headers

**Field: Headers** (for API calls)
```json
{
  "Authorization": "Basic {{PAT_TOKEN}}",
  "Content-Type": "application/json"
}
```

Replace `{{PAT_TOKEN}}` with:
1. Get your PAT from: https://dev.azure.com/{org}/_usersSettings/tokens
2. Run this PowerShell command:
```powershell
$pat = "your_pat_here"
$base64 = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes(":$pat"))
$base64 | Set-Clipboard
# Paste in the header
```

**Field: Headers for fetching OpenAPI Spec** (if using GitHub or secured endpoint)
```json
{
  "Accept": "application/yaml"
}
```
(Only needed if endpoint is secured)

---

#### Section: External APIs

**Checkbox: Allow this agent to delegate requests to other agents**
☐ Leave UNCHECKED for now (check when adding child agents)

**Checkbox: Allow this agent to use external APIs**
☑ CHECK THIS ✅

**Field: Allowed Methods**
```
GET, POST, PUT, PATCH, DELETE
```

---

### Test Configuration

Once you fill in all fields, use this test input:

**In the Test section, Input field:**
```json
{
  "input": {
    "query": "Get work item 791842 from Azure DevOps"
  }
}
```

**Expected Output:**
```json
{
  "statusCode": 200,
  "reason": "agent",
  "message": "Work item retrieved successfully",
  "details": {
    "id": 791842,
    "title": "Sample bug title",
    "state": "Active",
    "tags": ["agent-ready"],
    ...
  }
}
```

---

## Fixing the Red Error

### If you see: "Invalid Endpoint for OpenAPI Spec (Json / YAML)"

**Check these:**

1. **Is the URL accessible?**
   ```powershell
   # Test the URL
   Invoke-WebRequest -Uri "https://raw.githubusercontent.com/tushar270721/CodeGameRepo/main/apis/azdo-openapi-spec.yaml"
   ```

2. **Is the YAML valid?**
   - Use: https://www.yamllint.com/
   - Paste the content of `apis/azdo-openapi-spec.yaml`

3. **Is CORS enabled?** (if using GitHub)
   - GitHub allows raw content access by default ✅

4. **Verify the file exists:**
   - Check: `c:\Users\TUSHAR.SONAWANE\CodeGame\CodeGameRepo\apis\azdo-openapi-spec.yaml`

---

## Credentials Setup

### Get Azure DevOps PAT Token

1. Navigate to: https://dev.azure.com/{your_organization}/_usersSettings/tokens
2. Click "New Token"
3. **Name:** CodeGame FAB Agent
4. **Organization:** Select your org
5. **Expiration:** Custom (180 days recommended)
6. **Scopes:**
   - ✅ Work Items (Read)
   - ✅ Code (Read)
   - ✅ Build (Read)
7. Click "Create"
8. Copy and encode (see Headers section above)

### Git Repository Access

For the agent to read your repository:
1. Repository URL: `https://github.com/tushar270721/CodeGameRepo`
2. Access: Public (no auth needed) or use PAT for private repos

---

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| 401 Unauthorized | Check PAT token, verify Base64 encoding |
| 404 Not Found | Verify org/project/work item IDs exist |
| YAML Parse Error | Use YAML linter to validate spec file |
| Timeout | Increase API timeout or check network |
| CORS Error | Ensure endpoint is publicly accessible |

---

## Next Steps After Configuration

1. ✅ Configure and save this agent
2. ✅ Test with sample work item IDs
3. ✅ Create child agents for other tasks
4. ✅ Create parent agent to orchestrate
5. ✅ Set up workflow automation

---

## Files in Your Repository

```
CodeGameRepo/
├── apis/
│   └── azdo-openapi-spec.yaml          ← OpenAPI specification
├── agents/
│   ├── azdo-reader-config.json         ← This agent config
│   └── parent-agent-config.json        ← Parent orchestrator
└── docs/
    └── FAB_AGENT_SETUP.md              ← Full setup guide
```

---

## Resources

- **OpenAPI Spec:** `apis/azdo-openapi-spec.yaml`
- **Setup Guide:** `docs/FAB_AGENT_SETUP.md`
- **Azure DevOps API Docs:** https://docs.microsoft.com/en-us/rest/api/azure/devops/
- **FAB Documentation:** Check your FAB Studio help menu
