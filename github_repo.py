import os
import subprocess
import json
from pathlib import Path

class GitHubRepoHandler:
    """Handle GitHub repository operations locally without third-party tools"""
    
    def __init__(self, repo_url, local_path):
        self.repo_url = repo_url
        self.local_path = local_path
        self.repo_name = repo_url.split('/')[-1].replace('.git', '')
    
    def clone_repo(self):
        """Clone repository locally"""
        try:
            if os.path.exists(self.local_path):
                print(f"ℹ️  Repository already exists at {self.local_path}")
                return True
            
            print(f"📥 Cloning repository from {self.repo_url}...")
            result = subprocess.run(
                ['git', 'clone', self.repo_url, self.local_path],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"✅ Repository cloned successfully")
                return True
            else:
                print(f"❌ Error cloning repository: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return False
    
    def get_project_structure(self, max_depth=3, ignore_dirs={'.git', '__pycache__', 'node_modules', '.env', 'venv'}):
        """Analyze project structure and return file tree"""
        structure = {}
        
        def scan_directory(path, depth=0):
            if depth > max_depth:
                return {}
            
            items = {}
            try:
                for item in sorted(os.listdir(path)):
                    if item.startswith('.') and item not in {'.github', '.gitignore'}:
                        continue
                    
                    item_path = os.path.join(path, item)
                    
                    if os.path.isdir(item_path):
                        if item in ignore_dirs:
                            continue
                        items[item] = {
                            'type': 'directory',
                            'children': scan_directory(item_path, depth + 1)
                        }
                    else:
                        items[item] = {
                            'type': 'file',
                            'size': os.path.getsize(item_path)
                        }
            except PermissionError:
                pass
            
            return items
        
        structure = scan_directory(self.local_path)
        return structure
    
    def identify_relevant_files(self, keywords):
        """Find files relevant to bug based on keywords"""
        relevant_files = []
        
        try:
            for root, dirs, files in os.walk(self.local_path):
                # Skip ignored directories
                dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', 'node_modules', '.env', 'venv'}]
                
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, self.local_path)
                    
                    # Check file name for keywords
                    if any(keyword.lower() in file.lower() for keyword in keywords):
                        relevant_files.append(rel_path)
                        continue
                    
                    # Check file content for keywords (for text files)
                    if file.endswith(('.py', '.js', '.java', '.cs', '.cpp', '.c', '.go', '.rs', '.ts')):
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read(5000)  # Read first 5KB
                                if any(keyword.lower() in content.lower() for keyword in keywords):
                                    relevant_files.append(rel_path)
                        except:
                            pass
        
        except Exception as e:
            print(f"⚠️  Error scanning files: {str(e)}")
        
        return list(set(relevant_files))
    
    def create_branch(self, bug_id, branch_type="fix"):
        """Create a new branch with naming pattern"""
        try:
            os.chdir(self.local_path)
            
            # Branch naming pattern: fix/bug-791842 or feature/enhancement-xxx
            branch_name = f"{branch_type}/bug-{bug_id}"
            
            # Fetch latest from origin
            print(f"📡 Fetching latest changes...")
            subprocess.run(['git', 'fetch', 'origin'], capture_output=True)
            
            # Checkout main/master branch first
            main_branch = self.get_main_branch()
            subprocess.run(['git', 'checkout', main_branch], capture_output=True)
            
            # Create new branch
            print(f"🔀 Creating branch: {branch_name}...")
            result = subprocess.run(
                ['git', 'checkout', '-b', branch_name],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"✅ Branch created: {branch_name}")
                return branch_name
            else:
                print(f"❌ Error creating branch: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return None
    
    def get_main_branch(self):
        """Detect main branch (main or master)"""
        try:
            os.chdir(self.local_path)
            
            # Try to get default branch
            result = subprocess.run(
                ['git', 'symbolic-ref', 'refs/remotes/origin/HEAD'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return result.stdout.strip().split('/')[-1]
            
            # Fallback to common names
            for branch in ['main', 'master', 'develop']:
                result = subprocess.run(
                    ['git', 'show-ref', '--verify', f'refs/heads/{branch}'],
                    capture_output=True
                )
                if result.returncode == 0:
                    return branch
            
            return 'main'  # Default
            
        except:
            return 'main'
    
    def get_file_content(self, file_path):
        """Read file content"""
        try:
            full_path = os.path.join(self.local_path, file_path)
            if os.path.exists(full_path):
                with open(full_path, 'r', encoding='utf-8') as f:
                    return f.read()
            return None
        except Exception as e:
            print(f"❌ Error reading file: {str(e)}")
            return None
    
    def get_current_branch(self):
        """Get current branch name"""
        try:
            os.chdir(self.local_path)
            result = subprocess.run(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return result.stdout.strip()
            return None
        except:
            return None


# Example usage
if __name__ == "__main__":
    # Initialize repo handler
    repo_url = "https://github.com/example/repo.git"  # Replace with actual repo
    local_path = "./repo_clone"
    
    handler = GitHubRepoHandler(repo_url, local_path)
    
    # Clone repository
    if handler.clone_repo():
        print("\n📁 Project Structure:")
        structure = handler.get_project_structure()
        print(json.dumps(structure, indent=2)[:500] + "...")
        
        # Find relevant files for a bug
        print("\n🔍 Identifying relevant files for 'validation' bug...")
        relevant = handler.identify_relevant_files(['validation', 'validator', 'validate'])
        print(f"Found {len(relevant)} relevant files:")
        for f in relevant[:5]:
            print(f"  - {f}")
        
        # Create a branch for the bug fix
        print("\n🔀 Creating branch for bug #791842...")
        branch = handler.create_branch(791842, branch_type="fix")
        if branch:
            current = handler.get_current_branch()
            print(f"Current branch: {current}")
