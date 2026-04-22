from azure_devops import get_bug
from github_repo import GitHubRepoHandler
import os
import sys

def prepare_code_fix(bug_id, repo_url):
    """
    Workflow Step 3: Prepare repository for code changes
    
    - Clone/update repository
    - Understand project structure
    - Identify relevant files
    - Create a new branch
    """
    
    print(f"\n{'='*70}")
    print(f"🔧 Step 3: Preparing Repository for Bug #{bug_id}")
    print(f"{'='*70}\n")
    
    try:
        # Step 1: Fetch bug details from Azure DevOps
        print("📋 Fetching bug details from Azure DevOps...")
        bug = get_bug(bug_id)
        
        title = bug["fields"]["System.Title"]
        tags = bug["fields"].get("System.Tags", "")
        
        print(f"✅ Bug Title: {title}")
        print(f"   Tags: {tags if tags else 'None'}")
        
        # Step 2: Extract keywords from bug title and description
        keywords = [word for word in title.lower().split() if len(word) > 3]
        keywords.extend(['validation', 'error', 'fix', 'api', 'tenant', 'payload'])
        
        print(f"\n🔍 Search keywords: {', '.join(keywords[:5])}...")
        
        # Step 3: Initialize GitHub repo handler
        repo_name = repo_url.split('/')[-1].replace('.git', '')
        local_path = f"./repos/{repo_name}"
        
        print(f"\n📥 Repository: {repo_url}")
        print(f"   Local path: {local_path}")
        
        handler = GitHubRepoHandler(repo_url, local_path)
        
        # Step 4: Clone repository
        if not handler.clone_repo():
            print("❌ Failed to clone repository")
            return None
        
        # Step 5: Analyze project structure
        print(f"\n📁 Analyzing project structure...")
        structure = handler.get_project_structure(max_depth=2)
        
        # Count files by type
        file_types = {}
        def count_files(node):
            for key, value in node.items():
                if isinstance(value, dict):
                    if value.get('type') == 'file':
                        ext = key.split('.')[-1] if '.' in key else 'no_ext'
                        file_types[ext] = file_types.get(ext, 0) + 1
                    elif value.get('type') == 'directory':
                        count_files(value.get('children', {}))
        
        count_files(structure)
        print(f"   File types found:")
        for ext, count in sorted(file_types.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"     - .{ext}: {count} files")
        
        # Step 6: Identify relevant files
        print(f"\n🎯 Identifying relevant files...")
        relevant_files = handler.identify_relevant_files(keywords)
        
        if relevant_files:
            print(f"   Found {len(relevant_files)} relevant files:")
            for f in relevant_files[:10]:
                print(f"     ✓ {f}")
            if len(relevant_files) > 10:
                print(f"     ... and {len(relevant_files) - 10} more")
        else:
            print(f"   No relevant files found with current keywords")
        
        # Step 7: Create new branch
        print(f"\n🔀 Creating feature branch...")
        branch_name = handler.create_branch(bug_id, branch_type="fix")
        
        if not branch_name:
            print("❌ Failed to create branch")
            return None
        
        current_branch = handler.get_current_branch()
        
        # Step 8: Summary
        print(f"\n{'='*70}")
        print(f"✅ Repository Preparation Complete")
        print(f"{'='*70}")
        print(f"📌 Bug ID: {bug_id}")
        print(f"📄 Bug Title: {title}")
        print(f"📦 Repository: {repo_name}")
        print(f"🔀 Current Branch: {current_branch}")
        print(f"📂 Relevant Files: {len(relevant_files)}")
        
        return {
            "bug_id": bug_id,
            "title": title,
            "repo_url": repo_url,
            "local_path": local_path,
            "branch_name": branch_name,
            "relevant_files": relevant_files,
            "handler": handler
        }
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


# Example usage
if __name__ == "__main__":
    # For testing, use the bug we've been working with
    bug_id = 791842
    repo_url = "https://github.com/example/my-repo.git"  # Replace with actual repo
    
    # Or pass via command line:
    if len(sys.argv) > 2:
        bug_id = int(sys.argv[1])
        repo_url = sys.argv[2]
    
    result = prepare_code_fix(bug_id, repo_url)
    
    if result:
        print(f"\n✨ Ready for code changes!")
        print(f"   Next: Make code fixes in {result['branch_name']}")
