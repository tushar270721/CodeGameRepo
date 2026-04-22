import os
import subprocess
import json
from datetime import datetime
from azure_devops import add_comment

class PRHandler:
    """
    Workflow Step 6: Push changes and raise a PR
    
    - Commit code changes
    - Push to feature branch
    - Create pull request
    - Link PR to Azure DevOps ticket
    """
    
    def __init__(self, repo_path):
        self.repo_path = repo_path
        self.pr_info = {}
    
    def git_add_files(self, file_paths=None):
        """Stage files for commit"""
        try:
            os.chdir(self.repo_path)
            
            if file_paths:
                for file_path in file_paths:
                    subprocess.run(['git', 'add', file_path], capture_output=True, check=True)
                print(f"✅ Staged {len(file_paths)} file(s)")
            else:
                subprocess.run(['git', 'add', '.'], capture_output=True, check=True)
                print(f"✅ Staged all changes")
            
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Error staging files: {e.stderr.decode()}")
            return False
    
    def git_commit(self, bug_id, title, description=None):
        """Commit changes with structured message"""
        try:
            os.chdir(self.repo_path)
            
            # Create commit message
            commit_msg = f"fix(#{bug_id}): {title}"
            
            if description:
                commit_msg += f"\n\n{description}"
            
            result = subprocess.run(
                ['git', 'commit', '-m', commit_msg],
                capture_output=True,
                text=True,
                check=True
            )
            
            print(f"✅ Committed changes")
            print(f"   Message: {title}")
            return True
            
        except subprocess.CalledProcessError as e:
            if 'nothing to commit' in e.stderr.lower():
                print(f"ℹ️  Nothing to commit")
                return True
            print(f"❌ Error committing: {e.stderr}")
            return False
    
    def git_push(self, branch_name):
        """Push branch to remote"""
        try:
            os.chdir(self.repo_path)
            
            result = subprocess.run(
                ['git', 'push', '-u', 'origin', branch_name],
                capture_output=True,
                text=True,
                check=True
            )
            
            print(f"✅ Pushed branch: {branch_name}")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Error pushing: {e.stderr}")
            return False
    
    def get_commit_details(self):
        """Get details of current commit"""
        try:
            os.chdir(self.repo_path)
            
            # Get commit hash
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                capture_output=True,
                text=True,
                check=True
            )
            commit_hash = result.stdout.strip()
            
            # Get commit message
            result = subprocess.run(
                ['git', 'log', '-1', '--pretty=%B'],
                capture_output=True,
                text=True,
                check=True
            )
            commit_msg = result.stdout.strip()
            
            # Get current branch
            result = subprocess.run(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                capture_output=True,
                text=True,
                check=True
            )
            branch = result.stdout.strip()
            
            # Get files changed
            result = subprocess.run(
                ['git', 'diff', '--name-only', 'HEAD~1'],
                capture_output=True,
                text=True
            )
            files = result.stdout.strip().split('\n') if result.stdout.strip() else []
            
            return {
                'hash': commit_hash[:8],
                'message': commit_msg,
                'branch': branch,
                'files': files
            }
        
        except Exception as e:
            print(f"❌ Error getting commit details: {str(e)}")
            return None
    
    def generate_pr_description(self, bug_id, bug_title, changes_summary, relevant_files):
        """Generate comprehensive PR description"""
        pr_desc = f"""## Fix for Bug #{bug_id}

### Bug Title
{bug_title}

### Changes Made
{changes_summary}

### Affected Files
"""
        
        for file_path in relevant_files[:10]:
            pr_desc += f"- `{file_path}`\n"
        
        if len(relevant_files) > 10:
            pr_desc += f"- ... and {len(relevant_files) - 10} more files\n"
        
        pr_desc += f"""

### Testing
- [ ] Unit tests passed
- [ ] Integration tests passed
- [ ] Manual testing completed
- [ ] Code review completed

### Linked Issue
Closes #{bug_id}

### PR Type
- [x] Bug Fix
- [ ] Feature
- [ ] Enhancement
- [ ] Breaking Change
"""
        
        return pr_desc
    
    def create_pr_locally(self, branch_name, title, description, bug_id):
        """Prepare PR information locally"""
        try:
            commit_details = self.get_commit_details()
            if not commit_details:
                return False
            
            self.pr_info = {
                'branch': branch_name,
                'title': title,
                'description': description,
                'commit': commit_details['hash'],
                'message': commit_details['message'],
                'files': commit_details['files'],
                'bug_id': bug_id,
                'created_at': datetime.now().isoformat()
            }
            
            print(f"✅ PR information prepared")
            return True
        
        except Exception as e:
            print(f"❌ Error preparing PR: {str(e)}")
            return False
    
    def link_pr_to_azdo(self, bug_id, pr_title, pr_url, branch_name):
        """Link PR to Azure DevOps work item"""
        try:
            comment_text = f"""🤖 Fab Agent: Pull Request Created

**PR Information:**
- Title: {pr_title}
- Branch: {branch_name}
- URL: {pr_url}

**Status:** Awaiting Review

The code changes have been committed and pushed. Please review and merge when ready.

### Review Checklist
- [ ] Code follows project standards
- [ ] All tests pass
- [ ] No breaking changes
- [ ] Documentation updated
"""
            
            # Post comment to Azure DevOps
            add_comment(bug_id, comment_text)
            print(f"✅ Linked PR to Azure DevOps work item #{bug_id}")
            return True
        
        except Exception as e:
            print(f"❌ Error linking PR: {str(e)}")
            return False
    
    def generate_pr_report(self, bug_id, bug_title, repo_url, branch_name):
        """Generate comprehensive PR report"""
        print(f"\n{'='*70}")
        print(f"📤 Step 6: Pull Request Report")
        print(f"{'='*70}\n")
        
        print(f"🐛 Bug #: {bug_id}")
        print(f"📝 Bug Title: {bug_title}\n")
        
        if self.pr_info:
            print(f"📋 PR Information:")
            print(f"   Branch: {self.pr_info['branch']}")
            print(f"   Commit: {self.pr_info['commit']}")
            print(f"   Title: {self.pr_info['title']}")
            print(f"   Files Changed: {len(self.pr_info['files'])}\n")
            
            print(f"📄 Files Modified:")
            for file_path in self.pr_info['files'][:5]:
                print(f"   ✓ {file_path}")
            if len(self.pr_info['files']) > 5:
                print(f"   ... and {len(self.pr_info['files']) - 5} more\n")
        
        # Generate PR URL
        repo_name = repo_url.split('/')[-1].replace('.git', '')
        pr_url = f"{repo_url.replace('.git', '')}/pull/new/{branch_name}"
        
        print(f"🔗 Next Steps:")
        print(f"   1. Navigate to repository: {repo_url}")
        print(f"   2. Create PR from branch: {branch_name}")
        print(f"   3. Use generated description below")
        print(f"   4. Assign reviewers")
        print(f"   5. Request merge\n")
        
        print(f"{'='*70}")
        print(f"📝 Suggested PR Description:")
        print(f"{'='*70}\n")
        
        if self.pr_info:
            print(self.pr_info.get('description', 'N/A'))
        
        print(f"\n{'='*70}")
        print(f"✨ PR Ready for Manual Creation & Review")
        print(f"{'='*70}")
        
        return self.pr_info
    
    def get_github_cli_command(self, branch_name, title, body=None):
        """Generate GitHub CLI command to create PR (for reference)"""
        cmd = f"gh pr create --base main --head {branch_name} --title '{title}'"
        
        if body:
            # Escape quotes in body
            body_escaped = body.replace("'", "'\\''")
            cmd += f" --body '{body_escaped}'"
        
        return cmd


def push_and_create_pr(repo_path, repo_url, bug_id, bug_title, branch_name, 
                       files_changed, relevant_files, commit_description=None):
    """
    Complete Step 6: Push changes and create PR
    """
    
    print(f"\n{'='*70}")
    print(f"📤 Step 6: Push Changes & Create PR")
    print(f"{'='*70}\n")
    
    handler = PRHandler(repo_path)
    
    # Step 1: Stage files
    print("1️⃣  Staging files...")
    if not handler.git_add_files(files_changed):
        return None
    
    # Step 2: Commit changes
    print("\n2️⃣  Committing changes...")
    if not handler.git_commit(bug_id, bug_title, commit_description):
        return None
    
    # Step 3: Push to branch
    print("\n3️⃣  Pushing to remote...")
    if not handler.git_push(branch_name):
        return None
    
    # Step 4: Generate PR description
    print("\n4️⃣  Generating PR description...")
    changes_summary = f"Fixed validation issues in {len(files_changed)} file(s)."
    pr_description = handler.generate_pr_description(
        bug_id, 
        bug_title, 
        changes_summary,
        relevant_files
    )
    
    # Step 5: Create PR locally
    print("\n5️⃣  Preparing PR information...")
    pr_title = f"fix: {bug_title} (#{bug_id})"
    if not handler.create_pr_locally(branch_name, pr_title, pr_description, bug_id):
        return None
    
    # Step 6: Link to Azure DevOps
    print("\n6️⃣  Linking to Azure DevOps...")
    repo_name = repo_url.split('/')[-1].replace('.git', '')
    pr_url = f"https://github.com/{repo_url.split('/')[-2]}/{repo_name}/pull/new/{branch_name}"
    
    try:
        handler.link_pr_to_azdo(bug_id, pr_title, pr_url, branch_name)
    except Exception as e:
        print(f"⚠️  Could not link to Azure DevOps: {str(e)}")
    
    # Step 7: Generate report
    print("\n7️⃣  Generating report...")
    handler.generate_pr_report(bug_id, bug_title, repo_url, branch_name)
    
    return handler.pr_info


# Example usage
if __name__ == "__main__":
    import sys
    
    # Example parameters
    repo_path = "./repos/sample-repo"
    repo_url = "https://github.com/tushar270721/CodeGameRepo.git"
    bug_id = 791842
    bug_title = "Tenant Events API accepts invalid payload and does not validate input properly"
    branch_name = "fix/bug-791842"
    files_changed = ["src/EventProcessor.java", "src/validators/InputValidator.java"]
    relevant_files = ["src/EventProcessor.java", "src/validators/InputValidator.java", "test/EventProcessorTest.java"]
    
    commit_description = """Implemented comprehensive input validation for Tenant Events API:

- Added required field validation for enablonTenantId
- Added URL format validation for rootUrl
- Added type checking for navigationAssistantStatus
- Added helper methods for validation
- Updated error responses with detailed messages"""
    
    # Check if repo path exists, if not, show example output
    if not os.path.exists(repo_path):
        print(f"\n{'='*70}")
        print(f"📤 Step 6: Push Changes & Create PR (EXAMPLE)")
        print(f"{'='*70}\n")
        print(f"ℹ️  Repository path does not exist: {repo_path}")
        print(f"    When using with real repository, the workflow will:\n")
        
        handler = PRHandler(repo_path)
        
        # Create mock PR info
        handler.pr_info = {
            'branch': branch_name,
            'title': f"fix: {bug_title} (#{bug_id})",
            'commit': 'a1b2c3d',
            'message': f"fix(#{bug_id}): {bug_title}",
            'files': files_changed,
            'bug_id': bug_id,
            'created_at': datetime.now().isoformat()
        }
        
        # Show example output
        changes_summary = f"Fixed validation issues in {len(files_changed)} file(s)."
        pr_description = handler.generate_pr_description(
            bug_id, 
            bug_title, 
            changes_summary,
            relevant_files
        )
        
        handler.pr_info['description'] = pr_description
        
        # Generate report
        handler.generate_pr_report(bug_id, bug_title, repo_url, branch_name)
        
        print(f"\n✅ Example workflow complete!")
    else:
        # Execute PR workflow with real repository
        pr_info = push_and_create_pr(
            repo_path,
            repo_url,
            bug_id,
            bug_title,
            branch_name,
            files_changed,
            relevant_files,
            commit_description
        )
        
        if pr_info:
            print(f"\n✅ Workflow complete!")
