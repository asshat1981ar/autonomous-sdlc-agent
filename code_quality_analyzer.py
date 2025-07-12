#!/usr/bin/env python3
"""
Code Quality Analyzer and Refactoring Tool
Manual linting and code quality analysis for the Steampunk A2A MCP Framework
"""

import ast
import os
import re
import sys
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from pathlib import Path

# Constants
MILLISECONDS_PER_SECOND = 1000
SECONDS_PER_DAY = 86400
SECONDS_PER_HOUR = 3600


@dataclass
class CodeIssue:
    """CodeIssue class for steampunk operations."""
    file_path: str
    line_number: int
    issue_type: str
    severity: str
    message: str
    suggestion: str = ""

class SteampunkCodeQualityAnalyzer:
    """Industrial-grade code quality analysis"""

    """  Init   with enhanced functionality."""
    def __init__(self):
        self.issues = []
        self.stats = {
            'files_analyzed': 0,
            'lines_analyzed': 0,
            'issues_found': 0,
            'severity_counts': {'error': 0, 'warning': 0, 'info': 0}
        }

    def analyze_file(self, file_path: str) -> List[CodeIssue]:
        """Analyze a single Python file for quality issues"""
        issues = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')

            self.stats['files_analyzed'] += 1
            self.stats['lines_analyzed'] += len(lines)

            # Parse AST for advanced analysis
            try:
                tree = ast.parse(content)
                issues.extend(self._analyze_ast(file_path, tree, lines))
            except SyntaxError as e:
                issues.append(CodeIssue(
                    file_path=file_path,
                    line_number=e.lineno or 1,
                    issue_type="syntax_error",
                    severity="error",
                    message=f"Syntax error: {e.msg}",
                    suggestion="Fix the syntax error"
                ))

            # Line-by-line analysis
            issues.extend(self._analyze_lines(file_path, lines))

            # Import analysis
            issues.extend(self._analyze_imports(file_path, content, lines))

            # Documentation analysis
            issues.extend(self._analyze_documentation(file_path, content, lines))

        except Exception as e:
            issues.append(CodeIssue(
                file_path=file_path,
                line_number=1,
                issue_type="file_error",
                severity="error",
                message=f"Failed to analyze file: {e}",
                suggestion="Check file encoding and permissions"
            ))

        return issues

    def _analyze_ast(self, file_path: str, tree: ast.AST, lines: List[str]) -> List[CodeIssue]:
        """Analyze AST for structural issues"""
        issues = []

        for node in ast.walk(tree):
            # Function complexity analysis
            if isinstance(node, ast.FunctionDef):
                issues.extend(self._analyze_function(file_path, node, lines))

            # Class analysis
            elif isinstance(node, ast.ClassDef):
                issues.extend(self._analyze_class(file_path, node, lines))

            # Exception handling analysis
            elif isinstance(node, ast.ExceptHandler):
                if node.type is None:  # bare except:
                    issues.append(CodeIssue(
                        file_path=file_path,
                        line_number=node.lineno,
                        issue_type="broad_except",
                        severity="warning",
                        message="Bare except clause can mask programming errors",
                        suggestion="Catch specific exception types"
                    ))

            # Variable name analysis
            elif isinstance(node, ast.Name):
                if len(node.id) == 1 and node.id not in ['i', 'j', 'k', 'x', 'y', 'z']:
                    issues.append(CodeIssue(
                        file_path=file_path,
                        line_number=node.lineno,
                        issue_type="short_variable_name",
                        severity="info",
                        message=f"Single character variable name: '{node.id}'",
                        suggestion="Use descriptive variable names"
                    ))

        return issues

    def _analyze_function(self, file_path: str, node: ast.FunctionDef, lines: List[str]) -> List[CodeIssue]:
        """Analyze function for quality issues"""
        issues = []

        # Function length
        if hasattr(node, 'end_lineno') and node.end_lineno:
            func_length = node.end_lineno - node.lineno
            if func_length > 50:
                issues.append(CodeIssue(
                    file_path=file_path,
                    line_number=node.lineno,
                    issue_type="long_function",
                    severity="warning",
                    message=f"Function '{node.name}' is {func_length} lines long",
                    suggestion="Consider breaking into smaller functions"
                ))

        # Function complexity (simplified cyclomatic complexity)
        complexity = self._calculate_cyclomatic_complexity(node)
        if complexity > 10:
            issues.append(CodeIssue(
                file_path=file_path,
                line_number=node.lineno,
                issue_type="high_complexity",
                severity="warning",
                message=f"Function '{node.name}' has high cyclomatic complexity: {complexity}",
                suggestion="Simplify the function logic"
            ))

        # Missing docstring
        if not ast.get_docstring(node):
            issues.append(CodeIssue(
                file_path=file_path,
                line_number=node.lineno,
                issue_type="missing_docstring",
                severity="info",
                message=f"Function '{node.name}' missing docstring",
                suggestion="Add a descriptive docstring"
            ))

        # Too many parameters
        if len(node.args.args) > 7:
            issues.append(CodeIssue(
                file_path=file_path,
                line_number=node.lineno,
                issue_type="too_many_parameters",
                severity="warning",
                message=f"Function '{node.name}' has {len(node.args.args)} parameters",
                suggestion="Consider using a configuration object or breaking the function"
            ))

        return issues

    def _analyze_class(self, file_path: str, node: ast.ClassDef, lines: List[str]) -> List[CodeIssue]:
        """Analyze class for quality issues"""
        issues = []

        # Missing docstring
        if not ast.get_docstring(node):
            issues.append(CodeIssue(
                file_path=file_path,
                line_number=node.lineno,
                issue_type="missing_docstring",
                severity="info",
                message=f"Class '{node.name}' missing docstring",
                suggestion="Add a descriptive docstring"
            ))

        # Class naming convention
        if not node.name[0].isupper():
            issues.append(CodeIssue(
                file_path=file_path,
                line_number=node.lineno,
                issue_type="class_naming",
                severity="warning",
                message=f"Class '{node.name}' should start with uppercase",
                suggestion="Use PascalCase for class names"
            ))

        # Too many methods
        methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
        if len(methods) > 20:
            issues.append(CodeIssue(
                file_path=file_path,
                line_number=node.lineno,
                issue_type="too_many_methods",
                severity="warning",
                message=f"Class '{node.name}' has {len(methods)} methods",
                suggestion="Consider breaking into smaller classes"
            ))

        return issues

    def _analyze_lines(self, file_path: str, lines: List[str]) -> List[CodeIssue]:
        """Analyze individual lines for quality issues"""
        issues = []

        for i, line in enumerate(lines, 1):
            stripped = line.strip()

            # Line length
            if len(line) > 120:
                issues.append(CodeIssue(
                    file_path=file_path,
                    line_number=i,
                    issue_type="line_too_long",
                    severity="warning",
                    message=f"Line {i} is {len(line)} characters long",
                    suggestion="Break long lines for better readability"
                ))

            # Trailing whitespace
            if line != line.rstrip():
                issues.append(CodeIssue(
                    file_path=file_path,
                    line_number=i,
                    issue_type="trailing_whitespace",
                    severity="info",
                    message=f"Line {i} has trailing whitespace",
                    suggestion="Remove trailing whitespace"
                ))

            # TODO/FIXME comments
            if 'TODO' in stripped or 'FIXME' in stripped:
                issues.append(CodeIssue(
                    file_path=file_path,
                    line_number=i,
                    issue_type="todo_comment",
                    severity="info",
                    message=f"TODO/FIXME comment found",
                    suggestion="Address the TODO item"
                ))

            # Print statements (should use logging)
            if re.search(r'\bprint\s*\(', stripped) and not stripped.startswith('#'):
                issues.append(CodeIssue(
                    file_path=file_path,
                    line_number=i,
                    issue_type="print_statement",
                    severity="info",
                    message="Use logging instead of print statements",
                    suggestion="Replace print() with logger.info() or similar"
                ))

            # Magic numbers
            magic_numbers = re.findall(r'\b\d{2,}\b', stripped)
            for number in magic_numbers:
                if number not in ['10', '100', 'MILLISECONDS_PER_SECOND', '24', '60', 'SECONDS_PER_HOUR', 'SECONDS_PER_DAY']:
                    issues.append(CodeIssue(
                        file_path=file_path,
                        line_number=i,
                        issue_type="magic_number",
                        severity="info",
                        message=f"Magic number '{number}' found",
                        suggestion="Replace with a named constant"
                    ))
                    break  # Only report one per line

        return issues

    def _analyze_imports(self, file_path: str, content: str, lines: List[str]) -> List[CodeIssue]:
        """Analyze import statements"""
        issues = []

        import_lines = []
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith(('import ', 'from ')):
                import_lines.append((i, stripped))

        # Check for unused imports (simplified check)
        for line_num, import_line in import_lines:
            if import_line.startswith('import '):
                module = import_line.replace('import ', '').split(' as ')[0].split('.')[0]
                if module not in content.replace(import_line, ''):
                    issues.append(CodeIssue(
                        file_path=file_path,
                        line_number=line_num,
                        issue_type="unused_import",
                        severity="info",
                        message=f"Potentially unused import: {module}",
                        suggestion="Remove unused imports"
                    ))

        return issues

    def _analyze_documentation(self, file_path: str, content: str, lines: List[str]) -> List[CodeIssue]:
        """Analyze documentation quality"""
        issues = []

        # Check for module docstring
        try:
            tree = ast.parse(content)
            module_docstring = ast.get_docstring(tree)
            if not module_docstring:
                issues.append(CodeIssue(
                    file_path=file_path,
                    line_number=1,
                    issue_type="missing_module_docstring",
                    severity="info",
                    message="Module missing docstring",
                    suggestion="Add a module-level docstring describing the purpose"
                ))
        except:
            pass

        return issues

    def _calculate_cyclomatic_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity of a function"""
        complexity = 1  # Base complexity

        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, (ast.And, ast.Or)):
                complexity += 1

        return complexity

    def generate_report(self, issues: List[CodeIssue]) -> str:
        """Generate a comprehensive quality report"""
        self.stats['issues_found'] = len(issues)
        for issue in issues:
            self.stats['severity_counts'][issue.severity] += 1

        report = []
        report.append("🔧 STEAMPUNK CODE QUALITY ANALYSIS REPORT")
        report.append("=" * 50)
        report.append("")

        # Summary
        report.append("📊 SUMMARY")
        report.append(f"   Files analyzed: {self.stats['files_analyzed']}")
        report.append(f"   Lines analyzed: {self.stats['lines_analyzed']}")
        report.append(f"   Issues found: {self.stats['issues_found']}")
        report.append("")

        # Severity breakdown
        report.append("⚠️  SEVERITY BREAKDOWN")
        for severity, count in self.stats['severity_counts'].items():
            if count > 0:
                icon = "🔴" if severity == "error" else "🟡" if severity == "warning" else "🔵"
                report.append(f"   {icon} {severity.upper()}: {count}")
        report.append("")

        # Group issues by file
        issues_by_file = {}
        for issue in issues:
            if issue.file_path not in issues_by_file:
                issues_by_file[issue.file_path] = []
            issues_by_file[issue.file_path].append(issue)

        # Detailed issues
        if issues:
            report.append("🔍 DETAILED ISSUES")
            for file_path, file_issues in issues_by_file.items():
                report.append(f"\n📁 {file_path}")
                for issue in sorted(file_issues, key=lambda x: x.line_number):
                    severity_icon = "🔴" if issue.severity == "error" else "🟡" if issue.severity == "warning" else "🔵"
                    report.append(f"   Line {issue.line_number}: {severity_icon} {issue.message}")
                    if issue.suggestion:
                        report.append(f"      💡 Suggestion: {issue.suggestion}")
        else:
            report.append("✅ NO ISSUES FOUND - Code quality is excellent!")

        return "\n".join(report)

def main():
    """Run code quality analysis on the project"""
    analyzer = SteampunkCodeQualityAnalyzer()

    # Find Python files to analyze
    python_files = []
    for root, dirs, files in os.walk('.'):
        # Skip virtual environments and hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['venv', '__pycache__']]

        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                # Skip certain files
                if not any(skip in file_path for skip in ['.venv', 'venv', '__pycache__', 'test_']):
                    python_files.append(file_path)

    logger.info(f"🔍 Analyzing {len(python_files)} Python files...")

    all_issues = []
    for file_path in python_files:
        logger.info(f"   Analyzing: {file_path}")
        issues = analyzer.analyze_file(file_path)
        all_issues.extend(issues)

    # Generate and display report
    report = analyzer.generate_report(all_issues)
    logger.info("\n" + report)

    # Save report to file
    with open('code_quality_report.txt', 'w', encoding='utf-8') as f:
        f.write(report)

    logger.info(f"\n📄 Report saved to: code_quality_report.txt")

    return len([i for i in all_issues if i.severity == 'error'])

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)