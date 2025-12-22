import os
import shutil
import glob

# Essential files to keep in root
KEEP = {
    '.github',
    '.gitignore',
    'data',
    'fetch_youtube_data.py',
    'requirements.txt',
    'config.yaml',
    'README.md',
    '.git',
    'archive'
}

# Source directory
root = r'c:\Users\tragh\Downloads\DA\focus pbi\red swtich\data collection'
archive = os.path.join(root, 'archive')

if not os.path.exists(archive):
    os.makedirs(archive)

for item in os.listdir(root):
    if item in KEEP:
        continue
    
    src = os.path.join(root, item)
    dst = os.path.join(archive, item)
    
    try:
        if os.path.exists(dst):
            if os.path.isdir(src):
                shutil.rmtree(dst)
            else:
                os.remove(dst)
        
        shutil.move(src, dst)
        print(f"Moved: {item}")
    except Exception as e:
        print(f"Error moving {item}: {e}")
