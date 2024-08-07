import subprocess

# Download and install the en_core_web_trf model
subprocess.run(["python", "-m", "spacy", "download", "en_core_web_trf"])