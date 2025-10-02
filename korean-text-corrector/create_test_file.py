# filename: create_test_file.py
import os

try:
    filepath = '../korean-text-corrector/test.txt'
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    with open(filepath, 'w') as f:
        f.write('Hello World')
    
    # Verify the file was created and contains correct content
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            content = f.read()
        print(f'✓ Successfully created: {filepath}')
        print(f'✓ Content verified: "{content}"')
    else:
        print(f'✗ File creation failed: {filepath}')
        
except Exception as e:
    print(f'✗ Error: {e}')