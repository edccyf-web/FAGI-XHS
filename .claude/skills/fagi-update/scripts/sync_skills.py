#!/usr/bin/env python3
"""Sync an unpacked FAGI release; plan by default, archive confirmed duplicates on --apply."""
import argparse
import hashlib
import json
import re
import shutil
import time
import uuid
from pathlib import Path


def ignored(path):
    return any(p.startswith('._') or p in ('.DS_Store', '__pycache__') for p in path.parts)


def files(base):
    return {p.relative_to(base): p for p in base.rglob('*') if p.is_file() and not ignored(p.relative_to(base))}


def skill_name(base):
    p = base / 'SKILL.md'
    if not p.is_file():
        return None
    text = p.read_text(encoding='utf-8')
    if not text.startswith('---\n'):
        return None
    match = re.search(r'^name:\s*[\'"]?([a-z0-9-]+)[\'"]?\s*$', text.split('---', 2)[1], re.M)
    return match.group(1) if match else None


def version(base):
    try:
        value = json.loads((base / 'package.json').read_text())['version']
    except (OSError, ValueError, KeyError):
        return None
    return tuple(map(int, value.split('.'))) if re.fullmatch(r'\d+\.\d+\.\d+', str(value)) else None


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fingerprint(base, nested_skills=()):
    return {str(rel): sha(p) for rel, p in files(base).items() if rel.parts[0] != 'data' and skill_name(base / rel.parts[0]) not in nested_skills}


def sync(source, roots, apply=False):
    names = ['fagi'] + json.loads((source / 'package.json').read_text())['fagi']['agents']
    if len(names) != len(set(names)) or any(not re.fullmatch(r'fagi(?:-[a-z0-9]+)*', n) for n in names):
        raise ValueError('Invalid FAGI manifest')
    sources = {n: source if n == 'fagi' else source / n for n in names}
    payload = {}
    for name, base in sources.items():
        if skill_name(base) != name or version(base) is None:
            raise ValueError('Missing identity/version: ' + name)
        payload[name] = {r: p for r, p in files(base).items() if not (name == 'fagi' and r.parts[0] in names[1:])}
        if any(p.is_symlink() for p in base.rglob('*')):
            raise ValueError('Release must not contain symlinks')
    roots = [Path(p).expanduser().resolve() for p in roots]
    if len({p.resolve() for p in roots}) != len(roots):
        raise ValueError('Installation roots must be distinct')
    # A root is one host installation; copies in different hosts are not duplicates.
    plans = []
    for root in roots:
        if not root.is_dir() or root == source or source.is_relative_to(root) or root.is_relative_to(source):
            raise ValueError('Invalid installation root: ' + str(root))
        candidates = [p for p in root.iterdir() if p.is_dir()]
        if (root / 'fagi').is_dir():
            candidates += [p for p in (root / 'fagi').iterdir() if p.is_dir()]
        links = [p for p in candidates if p.is_symlink()]
        changes, duplicates, issues, merges = [], [], [], {}
        protected = {str(p): sha(p) for n in names for rel, p in files(root / n).items() if rel.parts[0] == 'data'}
        for name, base in sources.items():
            canonical = root / name
            found = [p for p in candidates if skill_name(p) == name]
            if canonical.exists() and skill_name(canonical) != name:
                issues.append(str(canonical) + ': canonical identity mismatch')
            if canonical.is_symlink() and not canonical.exists():
                issues.append(str(canonical) + ': broken canonical link')
            source_fp = {str(r): sha(q) for r, q in payload[name].items() if r.parts[0] != 'data'}
            for p in found:
                v = version(p)
                if v is not None and v > version(base):
                    issues.append(str(p) + ': newer local version; no downgrade')
                if p == canonical:
                    if (v is None or v == version(base)) and fingerprint(p, names[1:] if name == 'fagi' else ()) != source_fp:
                        issues.append(str(p) + ': canonical unknown/equal version with distinct content')
                    continue
                if p.is_symlink() or any(q.is_symlink() for q in p.rglob('*')) or any(q.resolve().is_relative_to(p.resolve()) for q in links):
                    issues.append(str(p) + ': linked duplicate retained')
                    continue
                # Unknown/equal versions with differing content may be a custom fork.
                if (v is None or v == version(base)) and fingerprint(p, names[1:] if name == 'fagi' else ()) != source_fp:
                    issues.append(str(p) + ': unknown/equal version with distinct content')
                    continue
                if v is not None and v > version(base):
                    continue
                for rel, q in files(p).items():
                    if rel.parts[0] != 'data':
                        continue
                    target = canonical / rel
                    if target.exists() and sha(target) != sha(q) or target in merges and sha(merges[target]) != sha(q):
                        issues.append(str(target) + ': conflicting personal data')
                    elif not target.exists():
                        merges[target] = q
                duplicates.append(p)
            for rel, q in payload[name].items():
                target = canonical / rel
                if target.is_symlink() and not target.exists():
                    issues.append(str(target) + ': broken file link')
                    continue
                if rel.parts[0] == 'data':
                    if target.exists() or target.is_symlink() or target in merges:
                        continue
                    if rel != Path('data/README.md') and 'templates' not in rel.parts:
                        continue
                if not target.exists() or sha(target) != sha(q):
                    changes.append((q, target))
        plans.append((root, changes, duplicates, issues, merges, protected, {str(p): str(p.readlink()) for p in links}))
    result = {'applied': False, 'blocked': any(p[3] for p in plans), 'installations': []}
    for root, changes, duplicates, issues, merges, protected, links in plans:
        result['installations'].append({'root': str(root), 'files_changed': len(changes), 'duplicates': [str(p) for p in duplicates], 'issues': issues, 'personal_files': len(protected)})
    if not apply or result['blocked']:
        return result
    for index, (root, changes, duplicates, issues, merges, protected, links) in enumerate(plans):
        if not changes and not duplicates and not merges:
            result['installations'][index].update({'skills_verified': len(names), 'data_preserved': True, 'links_preserved': True, 'archive': None})
            continue
        archive = root.parent / 'fagi-skill-backups' / (time.strftime('%Y%m%d-%H%M%S') + '-' + uuid.uuid4().hex[:8])
        for path in protected:
            backup = archive / 'personal-data' / Path(path).relative_to(root)
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, backup)
        for q, target in changes + [(q, target) for target, q in merges.items()]:
            if target.exists():
                backup = archive / 'replaced' / target.relative_to(root)
                backup.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(target, backup)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(q, target)
        for name in names:
            for rel, q in payload[name].items():
                if rel.parts[0] != 'data' and sha(root / name / rel) != sha(q):
                    raise RuntimeError('Installed content verification failed')
        if any(sha(Path(p)) != value for p, value in protected.items()):
            raise RuntimeError('Personal data changed')
        if any(sha(target) != sha(q) for target, q in merges.items()):
            raise RuntimeError('Merged data verification failed')
        for p in duplicates:
            dest = archive / 'duplicates' / p.relative_to(root)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(p), str(dest))
        if any(not Path(p).is_symlink() or str(Path(p).readlink()) != target for p, target in links.items()):
            raise RuntimeError('Existing link changed')
        result['installations'][index].update({'skills_verified': len(names), 'data_preserved': True, 'links_preserved': True, 'archive': str(archive) if archive.exists() else None})
    result['applied'] = True
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True, help='Unpacked release fagi directory')
    parser.add_argument('--root', type=Path, action='append', required=True, help='One host skills directory; repeat for other hosts')
    parser.add_argument('--apply', action='store_true', help='Apply plan; otherwise read-only')
    args = parser.parse_args()
    result = sync(args.source.resolve(), args.root, args.apply)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(2 if result['blocked'] else 0)
