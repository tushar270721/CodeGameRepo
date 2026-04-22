import os
import re
import json
from pathlib import Path
from collections import defaultdict

class LogAnalyzer:
    """
    Workflow Step 4: Analyze logs and infer error patterns
    
    - Read Application Insights / logs
    - Infer exception, failure path, or error pattern
    """
    
    # Common exception patterns
    EXCEPTION_PATTERNS = {
        'null_pointer': r'(NullPointerException|null reference|cannot read property|undefined)',
        'validation_error': r'(validation|invalid|constraint|required field)',
        'type_error': r'(TypeError|type mismatch|cannot convert|incompatible type)',
        'argument_error': r'(ArgumentError|invalid argument|wrong number of arguments)',
        'auth_error': r'(Unauthorized|Forbidden|401|403|authentication|permission denied)',
        'not_found': r'(NotFound|404|not found|does not exist|no such)',
        'timeout': r'(TimeoutException|timeout|timed out|deadline exceeded)',
        'connection_error': r'(ConnectionError|connection refused|socket error|network error)',
        'io_error': r'(IOException|I/O error|file not found|disk space)',
        'server_error': r'(500|500 Internal Server Error|ServerError|internal error)',
        'parsing_error': r'(ParseException|json parse|xml parse|parsing error|malformed)',
    }
    
    def __init__(self):
        self.logs = []
        self.exceptions = defaultdict(list)
        self.error_patterns = defaultdict(int)
    
    def read_log_file(self, file_path):
        """Read and parse log file"""
        try:
            if not os.path.exists(file_path):
                print(f"⚠️  Log file not found: {file_path}")
                return False
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            print(f"✅ Read {len(lines)} lines from log file")
            self.logs = lines
            return True
            
        except Exception as e:
            print(f"❌ Error reading log file: {str(e)}")
            return False
    
    def read_log_text(self, log_text):
        """Parse log text directly"""
        try:
            self.logs = log_text.split('\n')
            print(f"✅ Parsed {len(self.logs)} lines of log text")
            return True
        except Exception as e:
            print(f"❌ Error parsing log text: {str(e)}")
            return False
    
    def extract_exceptions(self):
        """Extract exception details from logs"""
        current_exception = None
        exception_stack = []
        
        for line in self.logs:
            line = line.strip()
            
            if not line:
                continue
            
            # Detect exception start
            if any(keyword in line for keyword in ['Exception', 'Error:', 'ERROR', 'FATAL', 'Traceback']):
                if current_exception:
                    self.exceptions[current_exception['type']].append(current_exception)
                
                # Extract exception type
                match = re.search(r'([\w]+(?:Exception|Error))', line)
                if match:
                    exc_type = match.group(1)
                else:
                    exc_type = 'Unknown Error'
                
                current_exception = {
                    'type': exc_type,
                    'message': line,
                    'stack_trace': [],
                    'line_number': 0
                }
                exception_stack.append(current_exception)
            
            # Add to stack trace
            elif current_exception and (line.startswith('at ') or line.startswith('File ') or '/' in line or '\\' in line):
                if current_exception:
                    current_exception['stack_trace'].append(line)
        
        # Add last exception
        if current_exception:
            self.exceptions[current_exception['type']].append(current_exception)
        
        return len(self.exceptions)
    
    def identify_error_patterns(self):
        """Identify common error patterns in logs"""
        for line in self.logs:
            line_lower = line.lower()
            
            for pattern_name, pattern_regex in self.EXCEPTION_PATTERNS.items():
                if re.search(pattern_regex, line, re.IGNORECASE):
                    self.error_patterns[pattern_name] += 1
        
        return self.error_patterns
    
    def extract_stack_traces(self):
        """Extract and format stack traces"""
        stack_traces = []
        
        for exc_type, exceptions in self.exceptions.items():
            for exc in exceptions:
                if exc['stack_trace']:
                    stack_traces.append({
                        'type': exc_type,
                        'message': exc['message'],
                        'trace': '\n'.join(exc['stack_trace'][:5])  # First 5 lines
                    })
        
        return stack_traces
    
    def correlate_with_bug(self, bug_title):
        """Correlate log errors with bug description"""
        correlations = []
        bug_keywords = bug_title.lower().split()
        
        # Check if error patterns match bug keywords
        for pattern_name, count in self.error_patterns.items():
            if count > 0:
                # Check relevance
                if any(keyword in pattern_name for keyword in bug_keywords):
                    correlations.append({
                        'pattern': pattern_name,
                        'occurrences': count,
                        'relevance': 'high',
                        'description': f"Found {count} instances of {pattern_name} errors"
                    })
                elif count > 3:  # Frequent errors are relevant
                    correlations.append({
                        'pattern': pattern_name,
                        'occurrences': count,
                        'relevance': 'medium',
                        'description': f"Found {count} instances of {pattern_name} errors (frequent)"
                    })
        
        return correlations
    
    def infer_failure_path(self):
        """Infer the failure path from logs"""
        failure_path = {
            'entry_point': None,
            'affected_components': set(),
            'failure_point': None,
            'root_cause': None
        }
        
        # Find earliest error in logs
        for i, line in enumerate(self.logs):
            if any(keyword in line for keyword in ['Exception', 'Error', 'ERROR']):
                # Look backwards for entry point
                for j in range(max(0, i-10), i):
                    if 'called' in self.logs[j].lower() or 'method' in self.logs[j].lower():
                        failure_path['entry_point'] = self.logs[j].strip()
                
                # Current line is the failure
                failure_path['failure_point'] = line.strip()
                
                # Extract exception type as root cause
                match = re.search(r'([\w]+(?:Exception|Error))', line)
                if match:
                    failure_path['root_cause'] = match.group(1)
                
                break
        
        # Find affected components
        for line in self.logs:
            if 'in ' in line or 'at ' in line:
                # Extract class/module names
                matches = re.findall(r'([\w\.]+)\(', line)
                for match in matches:
                    failure_path['affected_components'].add(match)
        
        failure_path['affected_components'] = list(failure_path['affected_components'])
        return failure_path
    
    def generate_report(self, bug_title, bug_id):
        """Generate comprehensive analysis report"""
        print(f"\n{'='*70}")
        print(f"📊 Step 4: Log Analysis Report")
        print(f"{'='*70}\n")
        
        print(f"🐛 Bug #: {bug_id}")
        print(f"📝 Title: {bug_title}\n")
        
        # Exception Summary
        print(f"🔴 Exceptions Found:")
        for exc_type, exceptions in sorted(self.exceptions.items(), key=lambda x: len(x[1]), reverse=True):
            print(f"   {exc_type}: {len(exceptions)} occurrence(s)")
        
        if not self.exceptions:
            print(f"   ℹ️  No exceptions detected in logs")
        
        # Error Patterns
        print(f"\n⚠️  Error Patterns Identified:")
        for pattern_name, count in sorted(self.error_patterns.items(), key=lambda x: x[1], reverse=True):
            if count > 0:
                print(f"   {pattern_name}: {count} instance(s)")
        
        if not self.error_patterns or all(v == 0 for v in self.error_patterns.values()):
            print(f"   ℹ️  No specific error patterns detected")
        
        # Bug Correlation
        print(f"\n🔗 Correlation with Bug:")
        correlations = self.correlate_with_bug(bug_title)
        if correlations:
            for corr in correlations:
                print(f"   [{corr['relevance'].upper()}] {corr['description']}")
        else:
            print(f"   ℹ️  No direct correlation found between bug and logs")
        
        # Failure Path
        print(f"\n📍 Failure Path Analysis:")
        failure_path = self.infer_failure_path()
        if failure_path['entry_point']:
            print(f"   Entry Point: {failure_path['entry_point']}")
        if failure_path['failure_point']:
            print(f"   Failure Point: {failure_path['failure_point']}")
        if failure_path['root_cause']:
            print(f"   Root Cause: {failure_path['root_cause']}")
        if failure_path['affected_components']:
            print(f"   Affected Components: {', '.join(failure_path['affected_components'][:3])}")
        
        # Stack Traces
        stack_traces = self.extract_stack_traces()
        if stack_traces:
            print(f"\n📋 Stack Traces ({len(stack_traces)} found):")
            for idx, trace in enumerate(stack_traces[:3], 1):
                print(f"\n   [{idx}] {trace['type']}")
                print(f"   Message: {trace['message']}")
                print(f"   Trace:\n{trace['trace']}")
        
        return {
            'exceptions': dict(self.exceptions),
            'error_patterns': dict(self.error_patterns),
            'correlations': correlations,
            'failure_path': failure_path,
            'stack_traces': stack_traces
        }


# Example usage
if __name__ == "__main__":
    import sys
    
    # Sample error log for testing
    sample_log = """
2024-04-22 10:15:30 INFO: Starting Tenant Events API service
2024-04-22 10:15:31 INFO: Initializing database connection
2024-04-22 10:15:32 DEBUG: Loading configuration
2024-04-22 10:15:35 INFO: Service started on port 8080
2024-04-22 10:16:00 INFO: Received event from client
2024-04-22 10:16:01 ERROR: Validation error - invalid payload structure
2024-04-22 10:16:01 ERROR: com.example.ValidationException: The EnablonTenantId field is required.
2024-04-22 10:16:01 ERROR: at com.example.api.EventValidator.validate(EventValidator.java:45)
2024-04-22 10:16:01 ERROR: at com.example.api.TenantEventsController.processEvent(TenantEventsController.java:128)
2024-04-22 10:16:02 ERROR: Invalid URL format in rootUrl field
2024-04-22 10:16:02 ERROR: java.net.MalformedURLException: For input string: "invalid-url"
2024-04-22 10:16:03 ERROR: Type mismatch for navigationAssistantStatus - expected boolean, got string
2024-04-22 10:16:03 ERROR: com.fasterxml.jackson.databind.exc.InvalidTypeIdException: Could not resolve type id 'INVALID'
2024-04-22 10:16:04 WARN: Request failed with HTTP 400 - Bad Request
2024-04-22 10:16:05 ERROR: Request processing failed: Invalid request payload.
    """
    
    # Initialize analyzer
    analyzer = LogAnalyzer()
    
    # Read logs
    analyzer.read_log_text(sample_log)
    
    # Analyze
    analyzer.extract_exceptions()
    analyzer.identify_error_patterns()
    
    # Generate report
    analyzer.generate_report(
        bug_title="Tenant Events API accepts invalid payload and does not validate input properly",
        bug_id=791842
    )
