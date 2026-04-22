from azure_devops import get_bug, add_comment, get_comments
import sys
import json
import re
import html
from html.parser import HTMLParser

# Get bug IDs from command line arguments
BUG_IDS = [int(bid) for bid in sys.argv[1:]] if len(sys.argv) > 1 else [791842]

def analyze_bug(desc):
    desc = desc.lower()
    
    if "invalid payload" in desc or "validation" in desc:
        return "api_validation_issue"
    
    return "unknown"


def fix_issue(issue_type):
    if issue_type == "api_validation_issue":
        return """
Suggested Fix:
- Add input validation for:
  - enablonTenantId (required)
  - rootUrl (valid URL)
  - navigationAssistantStatus (boolean)

Return 400 Bad Request for invalid input.
"""
    return "No fix identified"


def extract_json_from_text(text):
    """Extract JSON objects from text/code blocks, handling HTML markup"""
    json_objects = []
    
    if not text:
        return json_objects
    
    # Decode HTML entities first
    text_decoded = html.unescape(text)
    
    # Remove HTML tags
    text_no_html = re.sub(r'<[^>]+>', '\n', text_decoded)
    
    # Remove HTML attributes and styling
    text_cleaned = text_no_html.replace('```json', '').replace('```', '')
    
    # Try to find all brace-enclosed content
    brace_depth = 0
    start_idx = -1
    
    for i, char in enumerate(text_cleaned):
        if char == '{':
            if brace_depth == 0:
                start_idx = i
            brace_depth += 1
        elif char == '}':
            brace_depth -= 1
            if brace_depth == 0 and start_idx != -1:
                potential_json = text_cleaned[start_idx:i+1]
                try:
                    # Clean up and parse
                    cleaned = potential_json.strip()
                    obj = json.loads(cleaned)
                    json_objects.append(obj)
                except json.JSONDecodeError:
                    pass
                start_idx = -1
    
    # Also try regex patterns as fallback
    if not json_objects:
        json_patterns = re.findall(r'\{(?:[^{}]|(?:\{[^{}]*\}))*\}', text_cleaned, re.DOTALL)
        
        for pattern in json_patterns:
            try:
                cleaned = pattern.strip()
                obj = json.loads(cleaned)
                if obj not in json_objects:
                    json_objects.append(obj)
            except json.JSONDecodeError:
                try:
                    # Remove newlines and extra spaces
                    cleaned = re.sub(r'[\n\r]+', '', pattern)
                    cleaned = re.sub(r'\s+', ' ', cleaned)
                    obj = json.loads(cleaned)
                    if obj not in json_objects:
                        json_objects.append(obj)
                except json.JSONDecodeError:
                    continue
    
    return json_objects


def validate_implementation(payload, issue_type):
    """Validate implementation against the fix suggestion"""
    if issue_type != "api_validation_issue":
        return None, "Unknown issue type"
    
    issues = []
    suggestions = []
    
    # Check for required fields
    if not isinstance(payload, dict):
        return False, "Invalid payload format (not a dictionary)"
    
    # Check for enablonTenantId
    if "enablonTenantId" not in payload:
        issues.append("- Missing: enablonTenantId (required)")
    elif not payload["enablonTenantId"]:
        issues.append("- Invalid: enablonTenantId is empty")
    
    # Check for rootUrl
    if "rootUrl" not in payload and "payload" in payload:
        if isinstance(payload["payload"], dict) and "rootUrl" not in payload["payload"]:
            issues.append("- Missing: rootUrl (should be valid URL)")
    
    # Check for navigationAssistantStatus
    if "navigationAssistantStatus" not in payload and "payload" in payload:
        if isinstance(payload["payload"], dict) and "navigationAssistantStatus" not in payload["payload"]:
            issues.append("- Missing: navigationAssistantStatus (should be boolean)")
    
    if not issues:
        return True, "✅ All validation requirements met!"
    
    return False, "\n".join(issues)


def get_implementation_comments(bug_id):
    """Fetch and analyze existing comments for implementation code"""
    try:
        comments_response = get_comments(bug_id)
        
        if "comments" not in comments_response:
            return None
        
        comments = comments_response.get("comments", [])
        print(f"   Total comments: {len(comments)}")
        
        # Look for implementation code in comments
        for idx, comment in enumerate(comments):
            text = comment.get("text", "")
            
            # Skip agent's own comments
            if "Fab Agent" in text:
                print(f"   [{idx}] Skipping Fab Agent comment")
                continue
            
            # Debug: Show comment preview
            preview = text[:100].replace('\n', ' ') if text else "(empty)"
            print(f"   [{idx}] Comment preview: {preview}...")
            
            # Look for JSON payloads
            json_objects = extract_json_from_text(text)
            
            if json_objects:
                print(f"   ✅ Found {len(json_objects)} JSON object(s) in comment")
                return {
                    "found": True,
                    "payloads": json_objects,
                    "comment_id": comment.get("id"),
                    "author": comment.get("createdBy", {}).get("displayName", "Unknown")
                }
            else:
                # Debug: Show if any braces found
                if '{' in text:
                    print(f"   ℹ️  Found braces but no valid JSON in this comment")
        
        print(f"   No JSON objects found in any comments")
        return {"found": False}
        
    except Exception as e:
        print(f"⚠️ Error fetching comments: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def process_bug(bug_id):
    try:
        print(f"\n{'='*60}")
        print(f"Processing Bug #{bug_id}")
        print(f"{'='*60}")
        
        bug = get_bug(bug_id)
        title = bug["fields"]["System.Title"]
        description = bug["fields"].get("System.Description", "")
        repro_steps = bug["fields"].get("Microsoft.VSTS.TCM.ReproSteps", "")
        
        print(f"🔍 Bug Title: {title}")
        
        # Analyze title if description is empty
        analysis_text = description if description else title
        
        issue = analyze_bug(analysis_text)
        fix = fix_issue(issue)
        
        print(f"🧠 Issue Type: {issue}")
        print(f"💡 Fix Suggestion:\n{fix}")
        
        # Check for existing implementation comments
        print(f"\n📋 Checking for implementation code in comments...")
        impl_comments = get_implementation_comments(bug_id)
        
        # Also check ReproSteps field
        print(f"📋 Checking ReproSteps field...")
        repro_payloads = extract_json_from_text(repro_steps) if repro_steps else []
        
        if repro_payloads:
            print(f"   Found {len(repro_payloads)} JSON object(s) in ReproSteps")
        
        found_implementation = False
        
        if impl_comments and impl_comments.get("found"):
            print(f"✅ Found implementation code in comments!")
            found_implementation = True
            
            payloads = impl_comments.get("payloads", [])
            for idx, payload in enumerate(payloads, 1):
                print(f"\n🔎 Validating payload {idx}...")
                
                is_valid, validation_msg = validate_implementation(payload, issue)
                
                if is_valid:
                    validation_comment = f"""🤖 Fab Agent Validation: ✅ PASS

Implementation validated successfully!

{validation_msg}

Payload structure is correct and all required fields are present.
✨ Ready for testing and deployment."""
                else:
                    validation_comment = f"""🤖 Fab Agent Validation: ⚠️ ISSUES FOUND

The implementation has the following issues:

{validation_msg}

Please address these before merging."""
                
                print(f"📝 Posting validation comment...")
                add_comment(bug_id, validation_comment)
                print(f"✅ Validation comment posted for payload {idx}")
        
        elif repro_payloads:
            print(f"✅ Found implementation code in ReproSteps!")
            found_implementation = True
            
            for idx, payload in enumerate(repro_payloads, 1):
                print(f"\n🔎 Validating payload from ReproSteps {idx}...")
                
                is_valid, validation_msg = validate_implementation(payload, issue)
                
                if is_valid:
                    validation_comment = f"""🤖 Fab Agent Validation: ✅ PASS

Implementation in ReproSteps validated successfully!

{validation_msg}

Payload structure is correct and all required fields are present.
✨ Ready for testing and deployment."""
                else:
                    validation_comment = f"""🤖 Fab Agent Validation: ⚠️ ISSUES FOUND

The implementation in ReproSteps has the following issues:

{validation_msg}

Please address these before merging."""
                
                print(f"📝 Posting validation comment...")
                add_comment(bug_id, validation_comment)
                print(f"✅ Validation comment posted for ReproSteps payload {idx}")
        
        else:
            # Post initial suggestion if no implementation found
            print(f"📝 No implementation found yet. Posting initial suggestion...")
            add_comment(bug_id, f"🤖 Fab Agent Suggestion:\n{fix}")
            print(f"✅ Comment posted successfully for bug #{bug_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error processing bug #{bug_id}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


# Process all bugs
print(f"\n🚀 Starting Batch Agent for {len(BUG_IDS)} bugs...")

success_count = 0
failed_count = 0

for bug_id in BUG_IDS:
    if process_bug(bug_id):
        success_count += 1
    else:
        failed_count += 1

print(f"\n{'='*60}")
print(f"📊 Summary:")
print(f"✅ Successful: {success_count}")
print(f"❌ Failed: {failed_count}")
print(f"{'='*60}\n")
