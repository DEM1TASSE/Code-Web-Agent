import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'output.md'

def test_fetch_creates_output(tmp_path):
    # Run the fetch script
    proc = subprocess.run(['python3', str(ROOT / 'fetch_standings.py')], capture_output=True, text=True)
    assert proc.returncode == 0, f"Script failed: {proc.stderr}"
    assert OUT.exists(), "output.md was not created"
    txt = OUT.read_text()
    assert 'MLS' in txt or 'Standings' in txt
    # check at least one known team name appears
    assert ('Philadelphia' in txt) or ('San Diego' in txt) or ('FC Cincinnati' in txt)
