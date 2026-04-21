# 🔴 Fixing the "Invalid Endpoint for OpenAPI Spec" Error

## THE SOLUTION

The red error you see in the FAB Studio screenshot is because the **"Endpoint for OpenAPI Spec (Json / YAML)"** field is empty.

### ✅ FILL IT WITH THIS VALUE:

```
https://raw.githubusercontent.com/tushar270721/CodeGameRepo/main/apis/azdo-openapi-spec.yaml
```

---

## Step-by-Step Fix

### 1. Copy the URL above ⬆️

### 2. Go to FAB Studio

Navigate to: https://fab.wolterskluwer.ai/workspaces/learningworkspace_tushar/agents/agents/67854599-19ca-4f89-8b6e-60175748484d/f04d3834-096c-4f56-97f5-4d7c16ddeaeb

### 3. Click on the Design Tab

Look for the red highlighted field called:
```
Endpoint for OpenAPI Spec (Json / YAML)
```

### 4. Paste the URL

Replace the empty field with:
```
https://raw.githubusercontent.com/tushar270721/CodeGameRepo/main/apis/azdo-openapi-spec.yaml
```

### 5. The Error Should Disappear ✅

The red error will turn green when:
- URL is valid
- YAML file is accessible
- Spec is properly formatted

---

## Then Fill These Other Fields

### 📝 System Message
```
You are an Azure DevOps bug reader agent.

Your job:
1. Use Azure DevOps REST APIs
2. Read work item by ID
3. Validate content
4. Extract relevant information
5. Return structured JSON
```

### 🔑 Headers (Get PAT First)

1. Go to: https://dev.azure.com/{YOUR_ORG}/_usersSettings/tokens
2. Create a new token named "CodeGame FAB Agent"
3. Set scopes: ✅ Work Items (Read), ✅ Code (Read), ✅ Build (Read)
4. Copy the token

5. In PowerShell, encode it:
```powershell
$pat = "paste_your_token_here"
$base64 = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes(":$pat"))
Write-Host $base64
```

6. Paste the output in Headers:
```json
{
  "Authorization": "Basic PASTE_BASE64_OUTPUT_HERE",
  "Content-Type": "application/json"
}
```

### ✅ Enable External APIs
Check the box: "Allow this agent to use external APIs"

### 📋 Allowed Methods
```
GET, POST, PUT, PATCH, DELETE
```

---

## Verify It Works

### Test Input
```json
{
  "input": {
    "query": "Get work item 791842"
  }
}
```

### Expected Result
```json
{
  "statusCode": 200,
  "reason": "agent",
  "message": "Work item retrieved",
  "details": {
    "id": 791842,
    "title": "...",
    "state": "Active"
  }
}
```

---

## What Was Created in Your Repository

✅ **OpenAPI Spec File**
- Location: `apis/azdo-openapi-spec.yaml`
- Contains all Azure DevOps API endpoints
- Ready to use (publicly accessible from GitHub)

✅ **Documentation**
- `docs/FAB_AGENT_SETUP.md` - Full setup guide
- `docs/QUICK_CONFIG_REFERENCE.md` - Copy-paste configs
- `docs/IMPLEMENTATION_SUMMARY.md` - What's next
- `README.md` - Project overview

✅ **Agent Configurations**
- `agents/azdo-reader-config.json` - Reader agent config
- `agents/parent-agent-config.json` - Parent orchestrator config

---

## Quick Checklist

- [ ] Copy the OpenAPI endpoint URL
- [ ] Fill it in FAB Studio Design tab
- [ ] Generate and encode Azure DevOps PAT token
- [ ] Fill in Headers with Authorization
- [ ] Check "Allow external APIs" ✅
- [ ] Set Allowed Methods: GET, POST, PUT, PATCH, DELETE
- [ ] Test with sample input
- [ ] Verify green check mark (error disappears)

---

## Still Getting the Error?

### Check These:

1. **Is the GitHub URL accessible?**
   ```
   https://raw.githubusercontent.com/tushar270721/CodeGameRepo/main/apis/azdo-openapi-spec.yaml
   ```
   Open in browser - should show YAML content

2. **Is YAML valid?**
   - Visit: https://www.yamllint.com/
   - Paste the YAML file content
   - No syntax errors should appear

3. **Did you hit Save?**
   - After pasting URL, click somewhere else to trigger validation
   - Wait a few seconds for the endpoint to be verified

4. **Check your internet?**
   - Ensure FAB Studio can access GitHub URLs
   - Try a different network/VPN if needed

---

## Success! 🎉

When you see:
✅ Green check next to "Endpoint for OpenAPI Spec"
✅ Test returns 200 status code
✅ No red error messages

**Then you're ready to move to the next phase!**

---

## Repository GitHub URL

Your public repo is hosted at:
```
https://github.com/tushar270721/CodeGameRepo
```

---

**Need Help?**
- Check: `docs/FAB_AGENT_SETUP.md` - Troubleshooting section
- Check: `docs/QUICK_CONFIG_REFERENCE.md` - Common issues table
