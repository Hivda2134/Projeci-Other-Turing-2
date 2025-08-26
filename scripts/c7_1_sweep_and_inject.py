
#!/usr/bin/env python3
import os, json, difflib, itertools, pathlib, subprocess, sys, time, hashlib

def run_mask(target, out_path, a, b, seed):
    cmd = [
        'python3', 'scripts/mask_engine.py',
        '--in', str(target),
        '--out', str(out_path),
        '--alpha', str(a),
        '--beta', str(b),
        '--clover-density', '0.0',
        '--seed', str(seed),
    ]
    subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def calculate_drift(path_a, path_b):
    with open(path_a, 'r', encoding='utf-8') as f1:
        A = f1.read().splitlines(keepends=True)
    with open(path_b, 'r', encoding='utf-8') as f2:
        B = f2.read().splitlines(keepends=True)
    sm = difflib.SequenceMatcher(a=A, b=B)
    return 1.0 - sm.ratio()

def write_sig(path, context):
    ctx = dict(context)
    ctx['ts'] = int(time.time())
    payload = json.dumps(ctx, sort_keys=True).encode('utf-8')
    sig = hashlib.sha256(payload).hexdigest()
    with open(str(path)+'.sig', 'w', encoding='utf-8') as f:
        json.dump({'sig': sig, 'context': ctx}, f, sort_keys=True)

def inject_single_zwsp(in_path, out_path):
    with open(in_path, 'r', encoding='utf-8') as f:
        data = f.read()
    idx = data.find('\n')
    if idx == -1:
        masked = data + '\u200b'
    else:
        masked = data[:idx+1] + '\u200b' + data[idx+1:]
    pathlib.Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(masked)

def main():
    target_file = os.environ['C71_TARGET']
    reports_dir = pathlib.Path('ci_artifacts_private/c7_1/reports')
    tmp_dir = pathlib.Path('ci_artifacts_private/c7_1/tmp')
    ledger = pathlib.Path('ci_artifacts_private/c7_1/ledger/intervention_log.jsonl')
    reports_dir.mkdir(parents=True, exist_ok=True)
    tmp_dir.mkdir(parents=True, exist_ok=True)
    ledger.parent.mkdir(parents=True, exist_ok=True)

    alphas = [0.001, 0.0005, 0.0002, 0.0001]
    betas  = [0.001, 0.0005, 0.0002, 0.0001]
    base_seed = 4243

    grid = []
    for i, (a, b) in enumerate(itertools.product(alphas, betas)):
        out_file = tmp_dir / f'target.a{a}_b{b}.masked'
        run_mask(target_file, out_file, a, b, seed=base_seed + i)
        drift = calculate_drift(target_file, out_file)
        grid.append({'alpha': a, 'beta': b, 'drift': drift, 'artifact': str(out_file)})

    if not grid:
        print('Error: Sweep produced no results.', file=sys.stderr)
        sys.exit(1)

    best = min(grid, key=lambda r: r['drift'])
    best_a, best_b = best['alpha'], best['beta']

    # Ghost: tek ZWSP, deterministik yerleştirme
    ghost_input  = tmp_dir / f'target.a{best_a}_b{best_b}.masked'
    ghost_output = tmp_dir / f'target.a{best_a}_b{best_b}.ghosted.masked'
    inject_single_zwsp(ghost_input, ghost_output)
    ghost_drift = calculate_drift(target_file, ghost_output)

    final_report = {
        'sweep_summary': grid,
        'best_params_no_ghost': best,
        'ghost_injection_result': {
            'alpha': best_a,
            'beta': best_b,
            'zwsp_count': 1,
            'drift': ghost_drift,
            'has_ghost': True,
            'artifact': str(ghost_output)
        }
    }

    with open(reports_dir / 'sweep_integrity.json', 'w', encoding='utf-8') as f:
        json.dump(final_report, f, indent=2)

    # Sign and ledger
    write_sig(reports_dir / 'sweep_integrity.json', {'kind':'c7.1-report'})
    with open(ledger, 'a', encoding='utf-8') as f:
        f.write(json.dumps({
            'event':'c7.1_sweep_and_inject',
            'target': target_file,
            'best_alpha': best_a,
            'best_beta': best_b,
            'ghost_drift': ghost_drift,
            'ts': int(time.time())
        }, sort_keys=True) + '\n')

    print('Sweep and injection complete. Report generated.')
    print(json.dumps(final_report, indent=2))

if __name__ == '__main__':
    main()


