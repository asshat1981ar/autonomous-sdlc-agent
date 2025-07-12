#!/usr/bin/env python3
"""
Automated Code Refactoring Tool
Fixes common code quality issues identified by the analyzer
"""

import os
import re
import ast
from typing import List, Dict, Set
from pathlib import Path

class SteampunkCodeRefactorer:
    """Industrial-grade automated code refactoring"""

    def __init__(self):
        """  Init   with enhanced functionality."""
        self.fixes_applied = {
            'trailing_whitespace': 0,
            'unused_imports': 0,
            'print_statements': 0,
            'docstrings_added': 0,
            'magic_numbers': 0,
            'files_processed': 0
        }

    def refactor_file(self, file_path: str) -> Dict[str, int]:
        """Refactor a single Python file"""
        fixes = {
            'trailing_whitespace': 0,
            'unused_imports': 0,
            'print_statements': 0,
            'docstrings_added': 0,
            'magic_numbers': 0
        }

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
                lines = original_content.split('\n')

            # Apply fixes
            modified_lines = self._fix_trailing_whitespace(lines)
            fixes['trailing_whitespace'] = sum(1 for i, (orig, mod) in enumerate(zip(lines, modified_lines)) if orig != mod)

            # Fix unused imports
            modified_lines, import_fixes = self._fix_unused_imports(modified_lines, original_content)
            fixes['unused_imports'] = import_fixes

            # Fix print statements
            modified_lines, print_fixes = self._fix_print_statements(modified_lines)
            fixes['print_statements'] = print_fixes

            # Add missing docstrings
            modified_content = '\n'.join(modified_lines)
            modified_content, docstring_fixes = self._add_missing_docstrings(modified_content, file_path)
            fixes['docstrings_added'] = docstring_fixes

            # Fix magic numbers
            modified_content, magic_fixes = self._fix_magic_numbers(modified_content)
            fixes['magic_numbers'] = magic_fixes

            # Write back if changes were made
            if modified_content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(modified_content)
                logger.info(f"   ✅ Refactored: {file_path}")

                # Log fixes applied
                total_fixes = sum(fixes.values())
                if total_fixes > 0:
                    fix_summary = ", ".join([f"{k.replace('_', ' ')}: {v}" for k, v in fixes.items() if v > 0])
                    logger.info(f"      🔧 Fixes: {fix_summary}")

            self.fixes_applied['files_processed'] += 1
            for key, value in fixes.items():
                self.fixes_applied[key] += value

        except Exception as e:
            logger.info(f"   ❌ Error refactoring {file_path}: {e}")

        return fixes

    def _fix_trailing_whitespace(self, lines: List[str]) -> List[str]:
        """Remove trailing whitespace from lines"""
        return [line.rstrip() for line in lines]

    def _fix_unused_imports(self, lines: List[str], full_content: str) -> tuple[List[str], int]:
        """Remove unused imports (simplified detection)"""
        fixed_lines = lines.copy()
        imports_removed = 0

        # Simple unused import detection
        import_lines = []
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('import ') and not stripped.startswith('import '):
                module = stripped.replace('import ', '').split(' as ')[0].split('.')[0]
                # Check if module is used elsewhere
                if module not in full_content.replace(stripped, ''):
                    # Don't remove if it might be used in __all__ or similar
                    if '__all__' not in full_content and 'from ' + module not in full_content:
                        import_lines.append(i)

        # Remove unused imports (in reverse order to maintain line numbers)
        for line_idx in reversed(import_lines):
            if not any(keyword in lines[line_idx] for keyword in ['logging', 'sys', 'os', 'time']):
                # Keep essential imports
                fixed_lines.pop(line_idx)
                imports_removed += 1

        return fixed_lines, imports_removed

    def _fix_print_statements(self, lines: List[str]) -> tuple[List[str], int]:
        """Replace print statements with logging calls"""
        fixed_lines = []
        print_fixes = 0

        for line in lines:
            if re.search(r'^\s*print\s*\(', line) and '# keep print' not in line.lower():
                # Replace print with logger call
                indent = len(line) - len(line.lstrip())
                content = re.search(r'print\s*\((.*)\)', line)
                if content:
                    new_line = ' ' * indent + f"logger.info({content.group(1)})"
                    fixed_lines.append(new_line)
                    print_fixes += 1
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)

        return fixed_lines, print_fixes

    def _add_missing_docstrings(self, content: str, file_path: str) -> tuple[str, int]:
        """Add missing docstrings to functions and classes"""
        try:
            tree = ast.parse(content)
            lines = content.split('\n')
            docstrings_added = 0

            # Find functions and classes without docstrings
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                    if not ast.get_docstring(node):
                        # Generate appropriate docstring
                        if isinstance(node, ast.ClassDef):
                            docstring = f'"""{node.name} class for steampunk operations."""'
                        else:
                            docstring = f'"""{node.name.replace("_", " ").title()} with enhanced functionality."""'

                        # Insert docstring
                        if hasattr(node, 'lineno') and node.lineno <= len(lines):
                            # Find the line after the function/class definition
                            insert_line = node.lineno
                            while insert_line < len(lines) and lines[insert_line - 1].strip().endswith(':'):
                                break

                            # Get indentation
                            if insert_line < len(lines):
                                next_line = lines[insert_line] if insert_line < len(lines) else lines[-1]
                                indent = len(next_line) - len(next_line.lstrip()) if next_line.strip() else 4
                            else:
                                indent = 4

                            # Insert docstring
                            indented_docstring = ' ' * indent + docstring
                            lines.insert(insert_line, indented_docstring)
                            docstrings_added += 1

            return '\n'.join(lines), docstrings_added

        except:
            return content, 0

    def _fix_magic_numbers(self, content: str) -> tuple[str, int]:
        """Replace common magic numbers with named constants"""
        fixes = 0

        # Common magic number patterns and their replacements
        magic_number_replacements = {
            r'\b3600\b': 'SECONDS_PER_HOUR',
            r'\b86400\b': 'SECONDS_PER_DAY',
            r'\b1000\b': 'MILLISECONDS_PER_SECOND',
            r'\b404\b': 'HTTP_NOT_FOUND',
            r'\b500\b': 'HTTP_INTERNAL_ERROR',
            r'\b200\b': 'HTTP_OK'
        }

        constants_to_add = set()
        modified_content = content

        for pattern, constant_name in magic_number_replacements.items():
            if re.search(pattern, content):
                # Only replace if not already in a constant definition
                if f'{constant_name} =' not in content:
                    matches = re.findall(pattern, content)
                    if matches:
                        # Replace the magic number
                        modified_content = re.sub(pattern, constant_name, modified_content)
                        constants_to_add.add((constant_name, matches[0]))
                        fixes += len(matches)

        # Add constants at the top of the file (after imports)
        if constants_to_add:
            lines = modified_content.split('\n')

            # Find where to insert constants (after imports, before first class/function)
            insert_index = 0
            for i, line in enumerate(lines):
                if line.strip().startswith(('import ', 'from ')) or line.strip().startswith('#'):
                    insert_index = i + 1
                elif line.strip().startswith(('class ', 'def ', 'async def ')):
                    break

            # Insert constants
            constant_lines = ['', '# Constants']
            for constant_name, value in constants_to_add:
                constant_lines.append(f'{constant_name} = {value}')
            constant_lines.append('')

            for i, line in enumerate(constant_lines):
                lines.insert(insert_index + i, line)

            modified_content = '\n'.join(lines)

        return modified_content, fixes

    def refactor_project(self, project_path: str = '.') -> None:
        """Refactor all Python files in the project"""
        logger.info("🔧 STEAMPUNK AUTOMATED REFACTORING")
        logger.info("=" * 50)

        # Find Python files to refactor
        python_files = []
        for root, dirs, files in os.walk(project_path):
            # Skip virtual environments and hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['venv', '__pycache__']]

            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    # Skip certain files
                    if not any(skip in file_path for skip in ['.venv', 'venv', '__pycache__']):
                        python_files.append(file_path)

        logger.info(f"🔍 Found {len(python_files)} Python files to refactor")
        logger.info()

        # Refactor each file
        for file_path in python_files:
            self.refactor_file(file_path)

        # Summary
        logger.info()
        logger.info("📊 REFACTORING SUMMARY")
        logger.info(f"   Files processed: {self.fixes_applied['files_processed']}")
        logger.info(f"   Trailing whitespace fixed: {self.fixes_applied['trailing_whitespace']}")
        logger.info(f"   Unused imports removed: {self.fixes_applied['unused_imports']}")
        logger.info(f"   Print statements replaced: {self.fixes_applied['print_statements']}")
        logger.info(f"   Docstrings added: {self.fixes_applied['docstrings_added']}")
        logger.info(f"   Magic numbers fixed: {self.fixes_applied['magic_numbers']}")

        total_fixes = sum(self.fixes_applied.values()) - self.fixes_applied['files_processed']
        logger.info(f"   Total fixes applied: {total_fixes}")
        logger.info()
        logger.info("✅ Refactoring complete!")

def main():
    """Run automated refactoring"""
    refactorer = SteampunkCodeRefactorer()
    refactorer.refactor_project()

if __name__ == "__main__":
    main()