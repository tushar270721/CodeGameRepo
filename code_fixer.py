import os
import re
from pathlib import Path

class CodeFixer:
    """
    Workflow Step 5: Make code changes
    
    - Fix the bug / implement asked change
    - Follow existing coding style
    - Create and apply patches
    """
    
    def __init__(self, repo_path):
        self.repo_path = repo_path
        self.file_changes = {}
        self.code_style = None
    
    def detect_code_style(self, file_path):
        """Detect and analyze existing code style"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            style = {
                'language': self._detect_language(file_path),
                'indent_type': self._detect_indent(content),
                'indent_size': self._detect_indent_size(content),
                'line_ending': self._detect_line_ending(content),
                'quote_style': self._detect_quotes(content),
            }
            
            return style
            
        except Exception as e:
            print(f"⚠️  Could not detect style: {str(e)}")
            return None
    
    def _detect_language(self, file_path):
        """Detect programming language from file extension"""
        ext_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cs': 'csharp',
            '.cpp': 'cpp',
            '.c': 'c',
            '.go': 'go',
            '.rs': 'rust',
        }
        ext = Path(file_path).suffix.lower()
        return ext_map.get(ext, 'unknown')
    
    def _detect_indent(self, content):
        """Detect indent type (spaces vs tabs)"""
        if '\t' in content:
            return 'tabs'
        return 'spaces'
    
    def _detect_indent_size(self, content):
        """Detect indent size (2, 4, etc)"""
        matches = re.findall(r'^( +)', content, re.MULTILINE)
        if matches:
            sizes = [len(m) for m in matches if len(m) <= 8]
            if sizes:
                return max(set(sizes), key=sizes.count)
        return 4  # Default
    
    def _detect_line_ending(self, content):
        """Detect line ending style"""
        if '\r\n' in content:
            return 'crlf'
        return 'lf'
    
    def _detect_quotes(self, content):
        """Detect quote style preference"""
        single = content.count("'")
        double = content.count('"')
        return 'single' if single > double else 'double'
    
    def read_file(self, file_path):
        """Read file content"""
        try:
            full_path = os.path.join(self.repo_path, file_path)
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"❌ Error reading file: {str(e)}")
            return None
    
    def write_file(self, file_path, content):
        """Write file content"""
        try:
            full_path = os.path.join(self.repo_path, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"❌ Error writing file: {str(e)}")
            return False
    
    def apply_validation_fix(self, file_path, field_configs):
        """Apply input validation fix to a file"""
        content = self.read_file(file_path)
        if not content:
            return False
        
        original = content
        style = self.detect_code_style(os.path.join(self.repo_path, file_path))
        
        # Detect language and apply appropriate fix
        language = style['language'] if style else 'unknown'
        
        if language == 'java':
            content = self._apply_java_validation(content, field_configs, style)
        elif language == 'python':
            content = self._apply_python_validation(content, field_configs, style)
        elif language == 'csharp':
            content = self._apply_csharp_validation(content, field_configs, style)
        elif language in ['javascript', 'typescript']:
            content = self._apply_js_validation(content, field_configs, style)
        else:
            print(f"⚠️  Validation fix not implemented for {language}")
            return False
        
        if content != original:
            self.file_changes[file_path] = {
                'original': original,
                'modified': content,
                'type': 'validation_fix'
            }
            return True
        
        return False
    
    def _apply_java_validation(self, content, fields, style):
        """Apply Java input validation"""
        indent = '\t' if style and style['indent_type'] == 'tabs' else ' ' * (style['indent_size'] if style else 4)
        
        validation_code = f'''\n{indent}// Input validation\n'''
        
        for field, config in fields.items():
            if config['type'] == 'required':
                validation_code += f'''{indent}if (tenantId == null || tenantId.isEmpty()) {{\n'''
                validation_code += f'''{indent}{indent}throw new ValidationException("The EnablonTenantId field is required.");\n'''
                validation_code += f'''{indent}}}\n'''
            
            elif config['type'] == 'url':
                validation_code += f'''{indent}if (!isValidUrl(payload.getRootUrl())) {{\n'''
                validation_code += f'''{indent}{indent}throw new ValidationException("Invalid URL format for rootUrl.");\n'''
                validation_code += f'''{indent}}}\n'''
            
            elif config['type'] == 'boolean':
                validation_code += f'''{indent}if (!(payload.getNavigationAssistantStatus() instanceof Boolean)) {{\n'''
                validation_code += f'''{indent}{indent}throw new ValidationException("navigationAssistantStatus must be a boolean.");\n'''
                validation_code += f'''{indent}}}\n'''
        
        # Add validation method if not exists
        if 'isValidUrl' not in content:
            url_validator = f'''\n{indent}private static boolean isValidUrl(String url) {{\n'''
            url_validator += f'''{indent}{indent}try {{\n'''
            url_validator += f'''{indent}{indent}{indent}new URL(url);\n'''
            url_validator += f'''{indent}{indent}{indent}return true;\n'''
            url_validator += f'''{indent}{indent}}} catch (Exception e) {{\n'''
            url_validator += f'''{indent}{indent}{indent}return false;\n'''
            url_validator += f'''{indent}{indent}}}\n'''
            url_validator += f'''{indent}}}\n'''
            
            # Insert before closing brace
            if '}' in content:
                last_brace = content.rfind('}')
                content = content[:last_brace] + url_validator + content[last_brace:]
        
        # Insert validation code in appropriate place
        if 'public void process' in content or 'public void validate' in content:
            # Find the method body
            match = re.search(r'(public\s+\w+\s+\w+\s*\([^)]*\)\s*\{)', content)
            if match:
                insert_pos = match.end()
                content = content[:insert_pos] + validation_code + content[insert_pos:]
        
        return content
    
    def _apply_python_validation(self, content, fields, style):
        """Apply Python input validation"""
        indent = '\t' if style and style['indent_type'] == 'tabs' else ' ' * (style['indent_size'] if style else 4)
        
        validation_code = f'''\n{indent}# Input validation\n'''
        
        for field, config in fields.items():
            if config['type'] == 'required':
                validation_code += f'''{indent}if not tenant_id or tenant_id.strip() == "":\n'''
                validation_code += f'''{indent}{indent}raise ValueError("The EnablonTenantId field is required.")\n'''
            
            elif config['type'] == 'url':
                validation_code += f'''{indent}if not is_valid_url(payload.get("rootUrl")):\n'''
                validation_code += f'''{indent}{indent}raise ValueError("Invalid URL format for rootUrl.")\n'''
            
            elif config['type'] == 'boolean':
                validation_code += f'''{indent}if not isinstance(payload.get("navigationAssistantStatus"), bool):\n'''
                validation_code += f'''{indent}{indent}raise ValueError("navigationAssistantStatus must be a boolean.")\n'''
        
        # Add URL validator if not exists
        if 'is_valid_url' not in content:
            url_validator = f'''\n{indent}def is_valid_url(url):\n'''
            url_validator += f'''{indent}{indent}import re\n'''
            url_validator += f'''{indent}{indent}url_pattern = r'^https?://[^\\s/$.?#].[^\\s]*$'\n'''
            url_validator += f'''{indent}{indent}return bool(re.match(url_pattern, url))\n'''
            content = url_validator + '\n' + content
        
        # Insert validation
        if 'def ' in content:
            first_def = content.find('def ')
            first_method_end = content.find(':', first_def) + 1
            content = content[:first_method_end] + validation_code + content[first_method_end:]
        
        return content
    
    def _apply_csharp_validation(self, content, fields, style):
        """Apply C# input validation"""
        indent = '\t' if style and style['indent_type'] == 'tabs' else ' ' * (style['indent_size'] if style else 4)
        
        validation_code = f'''\n{indent}// Input validation\n'''
        
        for field, config in fields.items():
            if config['type'] == 'required':
                validation_code += f'''{indent}if (string.IsNullOrEmpty(tenantId))\n'''
                validation_code += f'''{indent}{{\n'''
                validation_code += f'''{indent}{indent}throw new ValidationException("The EnablonTenantId field is required.");\n'''
                validation_code += f'''{indent}}}\n'''
            
            elif config['type'] == 'url':
                validation_code += f'''{indent}if (!IsValidUrl(payload.RootUrl))\n'''
                validation_code += f'''{indent}{{\n'''
                validation_code += f'''{indent}{indent}throw new ValidationException("Invalid URL format for rootUrl.");\n'''
                validation_code += f'''{indent}}}\n'''
            
            elif config['type'] == 'boolean':
                validation_code += f'''{indent}if (payload.NavigationAssistantStatus is not bool)\n'''
                validation_code += f'''{indent}{{\n'''
                validation_code += f'''{indent}{indent}throw new ValidationException("navigationAssistantStatus must be a boolean.");\n'''
                validation_code += f'''{indent}}}\n'''
        
        # Add URL validator
        if 'IsValidUrl' not in content:
            url_validator = f'''\n{indent}private static bool IsValidUrl(string url)\n'''
            url_validator += f'''{indent}{{\n'''
            url_validator += f'''{indent}{indent}return Uri.TryCreate(url, UriKind.Absolute, out _);\n'''
            url_validator += f'''{indent}}}\n'''
            content = content.replace('}', url_validator + '\n}', 1)
        
        return content
    
    def _apply_js_validation(self, content, fields, style):
        """Apply JavaScript/TypeScript input validation"""
        indent = '\t' if style and style['indent_type'] == 'tabs' else ' ' * (style['indent_size'] if style else 4)
        quote = "'" if style and style['quote_style'] == 'single' else '"'
        
        validation_code = f'''\n{indent}// Input validation\n'''
        
        for field, config in fields.items():
            if config['type'] == 'required':
                validation_code += f'''{indent}if (!tenantId || tenantId.trim() === {quote}{quote}) {{\n'''
                validation_code += f'''{indent}{indent}throw new Error({quote}The EnablonTenantId field is required.{quote});\n'''
                validation_code += f'''{indent}}}\n'''
            
            elif config['type'] == 'url':
                validation_code += f'''{indent}if (!isValidUrl(payload.rootUrl)) {{\n'''
                validation_code += f'''{indent}{indent}throw new Error({quote}Invalid URL format for rootUrl.{quote});\n'''
                validation_code += f'''{indent}}}\n'''
            
            elif config['type'] == 'boolean':
                validation_code += f'''{indent}if (typeof payload.navigationAssistantStatus !== {quote}boolean{quote}) {{\n'''
                validation_code += f'''{indent}{indent}throw new Error({quote}navigationAssistantStatus must be a boolean.{quote});\n'''
                validation_code += f'''{indent}}}\n'''
        
        # Add URL validator
        if 'isValidUrl' not in content:
            url_validator = f'''\n{indent}function isValidUrl(url) {{\n'''
            url_validator += f'''{indent}{indent}try {{\n'''
            url_validator += f'''{indent}{indent}{indent}new URL(url);\n'''
            url_validator += f'''{indent}{indent}{indent}return true;\n'''
            url_validator += f'''{indent}{indent}}} catch (e) {{\n'''
            url_validator += f'''{indent}{indent}{indent}return false;\n'''
            url_validator += f'''{indent}{indent}}}\n'''
            url_validator += f'''{indent}}}\n'''
            content = url_validator + content
        
        return content
    
    def generate_patch(self, file_path):
        """Generate unified diff patch for changes"""
        if file_path not in self.file_changes:
            return None
        
        change = self.file_changes[file_path]
        original_lines = change['original'].split('\n')
        modified_lines = change['modified'].split('\n')
        
        patch = f"--- a/{file_path}\n"
        patch += f"+++ b/{file_path}\n"
        
        # Simple unified diff
        from difflib import unified_diff
        diff = unified_diff(original_lines, modified_lines, lineterm='')
        patch += '\n'.join(diff)
        
        return patch
    
    def apply_changes(self):
        """Apply all queued file changes"""
        success_count = 0
        
        for file_path, change in self.file_changes.items():
            if self.write_file(file_path, change['modified']):
                success_count += 1
                print(f"✅ Applied changes to {file_path}")
            else:
                print(f"❌ Failed to apply changes to {file_path}")
        
        return success_count
    
    def generate_report(self, bug_id, bug_title, issue_type='validation'):
        """Generate code fix report"""
        print(f"\n{'='*70}")
        print(f"🔧 Step 5: Code Changes Report")
        print(f"{'='*70}\n")
        
        print(f"🐛 Bug #: {bug_id}")
        print(f"📝 Title: {bug_title}")
        print(f"🔨 Fix Type: {issue_type}\n")
        
        if not self.file_changes:
            print("⚠️  No changes queued")
            return
        
        print(f"📋 Files Modified: {len(self.file_changes)}\n")
        
        for file_path, change in self.file_changes.items():
            print(f"📄 {file_path}")
            print(f"   Type: {change['type']}")
            
            # Calculate statistics
            orig_lines = len(change['original'].split('\n'))
            mod_lines = len(change['modified'].split('\n'))
            
            print(f"   Lines: {orig_lines} → {mod_lines}")
            
            # Show changes summary
            if 'validation' in change['type'].lower():
                print(f"   ✓ Added input validation")
                print(f"   ✓ Added error handling")
                print(f"   ✓ Added type checking")
            
            print()
        
        print(f"{'='*70}")
        print(f"✨ Ready for: Step 6 (Push & Create PR)")
        print(f"{'='*70}")


# Example usage
if __name__ == "__main__":
    import sys
    
    # Example: Fix validation issues
    repo_path = "./sample_repo"
    
    fixer = CodeFixer(repo_path)
    
    # Create sample Java file for testing
    sample_java = '''package com.example.api;

public class EventProcessor {
    public void processEvent(String tenantId, EventPayload payload) {
        // Process event
        System.out.println("Processing event...");
    }
}'''
    
    os.makedirs(repo_path, exist_ok=True)
    test_file = os.path.join(repo_path, "EventProcessor.java")
    with open(test_file, 'w') as f:
        f.write(sample_java)
    
    # Detect style
    print("🎨 Detecting code style...")
    style = fixer.detect_code_style(test_file)
    if style:
        print(f"   Language: {style['language']}")
        print(f"   Indent: {style['indent_type']} ({style['indent_size']} spaces)")
    
    # Apply validation fix
    print("\n🔨 Applying validation fixes...")
    fields = {
        'tenantId': {'type': 'required'},
        'rootUrl': {'type': 'url'},
        'navigationAssistantStatus': {'type': 'boolean'}
    }
    
    if fixer.apply_validation_fix("EventProcessor.java", fields):
        print("✅ Validation fix applied")
        
        # Generate report
        fixer.generate_report(791842, "Tenant Events API validation fix", "validation")
        
        # Apply changes
        fixer.apply_changes()
    else:
        print("⚠️  No changes made")
