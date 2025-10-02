# filename: create_requirements.py
import os

requirements_content = '''fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
python-multipart==0.0.6
'''

os.makedirs(os.path.dirname('../korean-text-corrector/backend/requirements.txt'), exist_ok=True)

with open('../korean-text-corrector/backend/requirements.txt', 'w', encoding='utf-8') as f:
    f.write(requirements_content)

print('Created: ../korean-text-corrector/backend/requirements.txt')