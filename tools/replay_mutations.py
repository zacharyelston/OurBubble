"""Prove mounted replay guards refuse plausible display/wiring defects. No scientific runs."""
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
source = (ROOT / 'demos/replay.mjs').read_text()
attacks = [
    ('swapped arms', '[row.vertex,row.baseline,row.experiment]', '[row.vertex,row.experiment,row.baseline]'),
    ('invented cells', 'String(value)', '"314159"'),
    ('wrong arm bound', 'replay.answer.experiment.checks.oscillatory_mode_stability', 'replay.answer.baseline.checks.oscillatory_mode_stability'),
    ('swapped headings', '["dot","baseline","changed weights"]', '["dot","changed weights","baseline"]'),
    ('stale refused form', 'catch(error){sync();message.textContent=', 'catch(error){message.textContent='),
    ('wrong export', 'new Blob([replay.save()]', 'new Blob(["{}"]'),
]
with tempfile.TemporaryDirectory(prefix='replay-guards-') as directory:
    root = Path(directory)
    shutil.copytree(ROOT / 'engine', root / 'engine')
    (root / 'demos').mkdir()
    for name in ['engine.mjs', 'replay-dom.test.mjs']:
        shutil.copyfile(ROOT / 'demos' / name, root / 'demos' / name)
    def run():
        return subprocess.run(['node', 'demos/replay-dom.test.mjs'], cwd=root,
                              capture_output=True, text=True)
    path = root / 'demos/replay.mjs'
    path.write_text(source)
    baseline = run()
    assert baseline.returncode == 0, baseline.stdout + baseline.stderr
    for name, before, after in attacks:
        assert source.count(before) == 1, name + ': mutation anchor drifted'
        path.write_text(source.replace(before, after))
        result = run()
        assert result.returncode != 0 and 'AssertionError' in result.stderr, name + ': mutation escaped or failed for unrelated reason'
        print('replay guard refused: ' + name)
