"""Offline temporary-install tests. Never touches real global skills."""
import importlib.util
import json
import shutil
import sys
import tempfile
from pathlib import Path
sys.dont_write_bytecode = True
here = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('fagi_sync', here / 'scripts/sync_skills.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
source = here.parent
name = 'fagi-xhs-competitor-analyzer'


def duplicate(root, alias, version='1.3.0'):
    p = root / alias
    shutil.copytree(root / name, p)
    meta = json.loads((p / 'package.json').read_text())
    meta['version'] = version
    (p / 'package.json').write_text(json.dumps(meta))
    return p


with tempfile.TemporaryDirectory() as d:
    base = Path(d)
    a = base / 'codex/skills'; b = base / 'workbuddy/skills'
    a.mkdir(parents=True); b.mkdir(parents=True)
    (a / 'unrelated').mkdir(); (a / 'unrelated/SKILL.md').write_text('unrelated')
    plan = module.sync(source, [a, b]); assert not plan['applied'] and not (a / 'fagi').exists()
    initial = module.sync(source, [a, b], True); assert initial['applied']
    assert all(len([p for p in r.iterdir() if module.skill_name(p)]) == 10 for r in [a, b])
    assert all(p['files_changed'] == 0 for p in module.sync(source, [a, b])['installations'])
    old = duplicate(a, name + '-v1.3')
    (old / 'data').mkdir(); (old / 'data/personal.txt').write_text('keep me')
    nested = a / 'fagi' / name
    shutil.copytree(old, nested)
    result = module.sync(source, [a, b], True)
    assert result['applied'] and len(result['installations'][0]['duplicates']) == 2
    assert not old.exists() and not nested.exists()
    assert (a / name / 'data/personal.txt').read_text() == 'keep me'
    assert (a / 'unrelated/SKILL.md').read_text() == 'unrelated'
    assert (b / name / 'SKILL.md').exists()
    assert len(list(Path(result['installations'][0]['archive']).glob('duplicates/**/SKILL.md'))) == 2
    assert all(not r['duplicates'] and r['files_changed'] == 0 for r in module.sync(source, [a, b])['installations'])
    bad = duplicate(a, name + '-conflict')
    (bad / 'data/personal.txt').write_text('different')
    assert module.sync(source, [a], True)['blocked'] and bad.exists()
    shutil.rmtree(bad)
    custom = duplicate(a, name + '-custom', '1.4.0')
    (custom / 'SKILL.md').write_text((custom / 'SKILL.md').read_text() + '\ncustom')
    assert module.sync(source, [a], True)['blocked'] and custom.exists()
    shutil.rmtree(custom)
    newer = duplicate(a, name + '-newer', '99.0.0')
    assert module.sync(source, [a], True)['blocked'] and newer.exists()
    shutil.rmtree(newer)
    unknown = duplicate(a, name + '-unknown')
    (unknown / 'package.json').unlink()
    assert module.sync(source, [a], True)['blocked'] and unknown.exists()
    shutil.rmtree(unknown)
    canonical_file = a / name / 'SKILL.md'
    original = canonical_file.read_bytes()
    canonical_file.write_bytes(original + b'\ncustom canonical')
    assert module.sync(source, [a], True)['blocked']
    assert canonical_file.read_bytes() == original + b'\ncustom canonical'
    canonical_file.write_bytes(original)
    real = base / 'canonical-target'; shutil.move(str(a / name), real)
    (a / name).symlink_to(real, target_is_directory=True)
    assert module.sync(source, [a], True)['applied'] and (a / name).is_symlink()
    alias = a / (name + '-link'); alias.symlink_to(real, target_is_directory=True)
    assert module.sync(source, [a], True)['blocked'] and alias.is_symlink() and real.exists()
print('PASS: plan-only, two-host installs, idempotence, alias/nested dedup, data merge/conflict, custom/unknown/newer versions, unrelated skills and links')
