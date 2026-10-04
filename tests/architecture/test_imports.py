import os
import ast

def test_core_does_not_import_vendor_sdk():
    """
    Verify that files in the 'core' directory do not directly import 
    provider-specific vendor SDKs (e.g., sarvam, openai, elevenlabs, etc.)
    or the 'providers' directory itself.
    """
    core_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../core'))
    forbidden_imports = ['sarvam', 'openai', 'elevenlabs', 'boto3', 'providers']
    
    violations = []
    
    for root, _, files in os.walk(core_dir):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    try:
                        tree = ast.parse(f.read(), filename=filepath)
                    except SyntaxError:
                        continue
                        
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            base_module = alias.name.split('.')[0]
                            if base_module in forbidden_imports:
                                violations.append(f"{filepath} imports {alias.name}")
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            base_module = node.module.split('.')[0]
                            if base_module in forbidden_imports:
                                violations.append(f"{filepath} imports from {node.module}")
                                
    assert len(violations) == 0, f"Architecture violation found: {violations}"
