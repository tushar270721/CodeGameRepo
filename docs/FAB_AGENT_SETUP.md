# Azure DevOps Bug Reader Agent - Setup Guide

## Overview
This guide explains how to configure the `azdo-reader-v2` FAB Agent to access Azure DevOps and read bugs/work items.

## Prerequisites
1. Azure DevOps organization access (PAT token)
2. Git repository access
3. Postman APIs documented and ready
4. FAB Agent configured with OpenAPI endpoint

## Step 1: Host the OpenAPI Specification

The OpenAPI spec file (`apis/azdo-openapi-spec.yaml`) needs to be accessible to the FAB Agent. You have several options:

### Option A: Host on GitHub (Recommended for public repos)
```
https://raw.githubusercontent.com/tushar270721/CodeGameRepo/main/apis/azdo-openapi-spec.yaml
```

### Option B: Host on Azure DevOps Artifacts
1. Upload the YAML file to your Azure DevOps project
2. Get the raw URL

### Option C: Host locally with a simple HTTP server
```powershell
# In the apis folder
python -m http.server 8000
# Access at: http://localhost:8000/azdo-openapi-spec.yaml
```

## Step 2: FAB Agent Configuration

In the FAB Studio, fill in the following fields:

### Design Tab Configuration

#### 1. **Base agent name**
```
Generic Prompt Agent With Tools
```

#### 2. **Base agent version**
```
0.54.0
```

#### 3. **Endpoint for OpenAPI Spec (Json / YAML)**

Choose based on your hosting option:
- **GitHub (Public Repo):**
  ```
  https://raw.githubusercontent.com/tushar270721/CodeGameRepo/main/apis/azdo-openapi-spec.yaml
  ```

- **Local Development:**
  ```
  http://localhost:8000/azdo-openapi-spec.yaml
  ```

- **Azure DevOps Artifacts:**
  ```
  https://dev.azure.com/{organization}/{project}/_apis/build/builds/{buildId}/artifacts
  ```

#### 4. **System Message**
Update with your specific instructions (replace enableon/ART - New SaaS with your org/project):

```
You are an Azure DevOps bug reader agent for the 'enableon' organization and 'ART - New SaaS' project.

Your job:
1. Use Azure DevOps REST APIs
2. Read work item by ID from the enableon organization
3. Validate content and extract information
4. Return structured JSON

Important details:
- Organization: enableon
- Project: ART - New SaaS
- API Base URL: https://dev.azure.com/enableon/ART%20-%20New%20SaaS/_apis

Use these steps:
1. Authenticate using PAT token
2. Extract work item ID from the query
3. Call Azure DevOps API to fetch work item details
4. Extract fields: ID, Title, Description, State, Tags, Priority, Comments, Assignee
5. Return structured JSON with all extracted data
```

#### 5. **User Prompt**
Template for input:
```
[query]
```

### Headers Configuration

The "Headers" section should include:

```json
{
  "Authorization": "Basic {{BASE64_ENCODED_PAT}}"
}
```

**To generate BASE64 encoded PAT:**
```powershell
# On Windows PowerShell
$pat = "your_pat_token_here"
$base64 = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes(":$pat"))
Write-Host $base64
```

### Headers for Fetching OpenAPI Spec

```json
{
  "Authorization": "Basic {{BASE64_ENCODED_PAT}}",
  "Accept": "application/yaml"
}
```

### Allowed Methods
```
GET, POST, PUT, PATCH, DELETE
```

### External APIs

Enable "Allow this agent to use external APIs" if calling outside services.

## Step 3: Test Inputs

Use these test inputs to verify the agent works:

```json
{
  "input": {
    "query": "Get bug 791842 details from Azure DevOps"
  }
}
```

Expected response structure:
```json
{
  "statusCode": 200,
  "reason": "agent",
  "message": "Work item details retrieved",
  "error": null,
  "details": {
    "id": 791842,
    "title": "Bug title here",
    "description": "Bug description",
    "state": "Active",
    "tags": ["agent-ready"],
    "priority": 1
  }
}
```

## Step 4: Azure DevOps Access

### Get Your PAT Token

1. Go to: https://dev.azure.com/{organization}/_usersSettings/tokens
2. Click "New Token"
3. Set scope: `Work Items (Read)`, `Code (Read)`, `Build (Read)`
4. Generate and save securely

### Organization and Project Details

In the agent configuration, ensure you have:
- Organization: `{your_organization}`
- Project: `{your_project_name}`

## Step 5: Testing with Postman

Before using the FAB Agent, test with Postman:

1. Import the OpenAPI spec into Postman
2. Set Authorization: Basic Auth with PAT
3. Test these endpoints:
   - GET `/workitems/{id}` - Get a specific bug
   - GET `/workitems?wiql=...` - Search bugs with tag "agent-ready"
   - GET `/repositories` - List git repos

## Troubleshooting

### "Invalid Endpoint for OpenAPI Spec" Error
- Verify the YAML file is valid
- Check that the URL is publicly accessible or includes proper authentication
- Use an online YAML validator: https://www.yamllint.com/

### "401 Unauthorized" in responses
- Verify PAT token is correct and not expired
- Check Base64 encoding is done properly
- Ensure headers are configured correctly

### "404 Not Found" when reading work items
- Verify organization and project names
- Check work item ID exists in Azure DevOps
- Ensure API version is compatible (7.1 recommended)

## Next Steps

After successful agent testing:
1. Create parent agent to orchestrate multiple child agents
2. Set up workflows for the complete ticket workflow
3. Link PR to work items
4. Set up approval workflow

## References

- Azure DevOps REST API: https://docs.microsoft.com/en-us/rest/api/azure/devops/
- OpenAPI 3.0 Spec: https://spec.openapis.org/oas/v3.0.3
- FAB Agents Documentation: Check your FAB Studio help section
