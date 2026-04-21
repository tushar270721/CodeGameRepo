# CodeGame - Azure DevOps Bug Reader with FAB Agents

An automated workflow system for processing Azure DevOps tickets using FAB (Flexible AI Bot) agents. This project enables intelligent reading, analysis, and fixing of bugs through a coordinated multi-agent system.

## 🎯 Overview

CodeGame automates the entire bug handling workflow in Azure DevOps:

1. **Read** - Automatically read work items tagged `agent-ready`
2. **Analyze** - Analyze code impact and repository structure
3. **Validate** - Request clarification if needed
4. **Generate** - Generate code fixes
5. **Create** - Create branches and pull requests
6. **Link** - Link PRs back to tickets
7. **Review** - Enable human review and merge

## 🏗️ Architecture

### Multi-Agent System

```
Parent Agent (Orchestrator)
├── azdo-reader-v2 (Read & Validate)
├── code-analyzer (Analyze Impact)
├── fix-generator (Generate Fixes)
└── pr-creator (Create Pull Requests)
```

### Key Components

- **OpenAPI Specification**: Defines Azure DevOps API endpoints (`apis/azdo-openapi-spec.yaml`)
- **Agent Configurations**: JSON configs for each agent
- **Documentation**: Setup guides and quick references
- **Workflow Definition**: 11-step automated workflow

## 📋 Requirements

- Azure DevOps organization with access
- Azure DevOps Personal Access Token (PAT)
- FAB Studio account and agent access
- Git repository (this repo)

## 🚀 Quick Start

### 1. Configure the OpenAPI Endpoint

In FAB Studio for `azdo-reader-v2` agent, set:

```
Endpoint for OpenAPI Spec:
https://raw.githubusercontent.com/tushar270721/CodeGameRepo/main/apis/azdo-openapi-spec.yaml
```

### 2. Set Up Authentication

Get your Azure DevOps PAT token from:
```
https://dev.azure.com/{org}/_usersSettings/tokens
```

Encode it in PowerShell:
```powershell
$pat = "your_token"
$base64 = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes(":$pat"))
```

Add to FAB Studio Headers:
```json
{
  "Authorization": "Basic {base64_token_here}",
  "Content-Type": "application/json"
}
```

### 3. Test the Agent

Input:
```json
{
  "query": "Get work item 791842"
}
```

Expected output:
```json
{
  "statusCode": 200,
  "message": "Work item retrieved",
  "details": {...}
}
```

## 📁 Project Structure

```
CodeGameRepo/
├── apis/
│   └── azdo-openapi-spec.yaml          OpenAPI 3.0 specification
├── agents/
│   ├── azdo-reader-config.json         Child agent configuration
│   └── parent-agent-config.json        Parent/orchestrator agent
├── docs/
│   ├── FAB_AGENT_SETUP.md              Complete setup guide
│   ├── QUICK_CONFIG_REFERENCE.md       Copy-paste configurations
│   └── IMPLEMENTATION_SUMMARY.md       What was created and next steps
└── README.md                           This file
```

## 📚 Documentation

- **[FAB Agent Setup Guide](docs/FAB_AGENT_SETUP.md)** - Complete step-by-step setup
- **[Quick Configuration Reference](docs/QUICK_CONFIG_REFERENCE.md)** - Quick reference for FAB Studio
- **[Implementation Summary](docs/IMPLEMENTATION_SUMMARY.md)** - What was created and next steps

## 🔄 Workflow Steps

When a work item is tagged `agent-ready`:

| Step | Agent | Action |
|------|-------|--------|
| 1 | Parent | Listen for agent-ready tags |
| 2 | azdo-reader-v2 | Read work item details |
| 3 | azdo-reader-v2 | Validate content & ask clarifications |
| 4 | code-analyzer | Analyze code impact (coming soon) |
| 5 | fix-generator | Generate fixes (coming soon) |
| 6 | fix-generator | Create branch & commit (coming soon) |
| 7 | pr-creator | Create pull request (coming soon) |
| 8 | pr-creator | Request review (coming soon) |
| 9 | azdo-reader-v2 | Update ticket with PR link |
| 10 | Parent | Wait for human approval |
| 11 | azdo-reader-v2 | Mark ticket as complete |

## 🔐 Security

- Uses Azure DevOps PAT tokens for authentication
- Supports Basic Auth with token encoding
- No credentials stored in repository
- Use environment variables for sensitive data

## 📦 Available APIs

The OpenAPI specification includes endpoints for:

- **Work Items** - Read, search, and update work items
- **Git Repositories** - List repos and read structure
- **Commits** - Access commit history
- **Pull Requests** - Create and manage PRs
- **Builds** - Access build logs and information

## 🧪 Testing

Test the agent configuration with sample inputs:

```bash
# Read a specific bug
Query: "Get bug 791842 from Azure DevOps"

# Search for bugs
Query: "Find all work items tagged 'agent-ready'"

# List repositories
Query: "List all repositories in the project"
```

## 🛠️ Configuration Checklist

- [ ] Get Azure DevOps PAT token
- [ ] Encode PAT token to Base64
- [ ] Fill OpenAPI endpoint in FAB Studio
- [ ] Set authentication headers
- [ ] Set allowed HTTP methods (GET, POST, PUT, PATCH, DELETE)
- [ ] Enable external APIs
- [ ] Test agent with sample work item
- [ ] Fix red error indicator ✅

## 🚨 Troubleshooting

### "Invalid Endpoint for OpenAPI Spec" Error

1. Verify URL is accessible:
   ```powershell
   Invoke-WebRequest "https://raw.githubusercontent.com/..."
   ```

2. Validate YAML file at: https://www.yamllint.com/

3. Check GitHub repo is public or use authenticated URL

### "401 Unauthorized" Errors

1. Verify PAT token is correct
2. Check Base64 encoding (use above PowerShell command)
3. Ensure token has required scopes:
   - Work Items (Read)
   - Code (Read)
   - Build (Read)

### Timeout Issues

- Increase agent timeout in configuration
- Check network connectivity
- Verify API endpoints are accessible

## 📈 Roadmap

### Phase 1: Foundation ✅
- [x] OpenAPI specification
- [x] Agent configurations
- [x] Documentation

### Phase 2: Setup (Current)
- [ ] Configure azdo-reader-v2 agent
- [ ] Test agent functionality

### Phase 3: Child Agents
- [ ] code-analyzer agent
- [ ] fix-generator agent
- [ ] pr-creator agent

### Phase 4: Orchestration
- [ ] Parent agent configuration
- [ ] Workflow automation
- [ ] Error handling

### Phase 5: Optimization
- [ ] Performance tuning
- [ ] Advanced logging
- [ ] Monitoring and alerts

## 🤝 Contributing

This project is managed by the CodeGame Development Team.

## 📞 Support

- FAB Studio: https://fab.wolterskluwer.ai/
- Azure DevOps API: https://docs.microsoft.com/en-us/rest/api/azure/devops/
- OpenAPI Spec: https://spec.openapis.org/

## 📝 License

Internal project - Wolters Kluwer

---

**Last Updated:** April 21, 2026  
**Status:** Ready for Configuration  
**Next Action:** Set OpenAPI Endpoint in FAB Studio
