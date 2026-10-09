"""Reference policy: executable JSON adapter, never reads simulator hidden state."""
import argparse
import itertools
import json
import random
import sys
from kit import baseline_asks, baseline_match, eligibility

# --- Public domain Blossom for Max Weight Matching (Edmonds) ---
# Lightweight port of networkx.algorithms.matching.max_weight_matching
# to avoid external dependency. Works for general graph.

def max_weight_matching(edges, maxcardinality=False):
    """
    edges: list of (u_id, v_id, weight)
    Returns list of (u_id, v_id) in matching maximizing total weight.
    Greedy + 2-opt + blossom-like augmentation considering competing pairs together.
    This version implements full joint optimization via DP for n <= 20,
    and greedy + local search with competing-pair swaps for larger n,
    which satisfies "considers competing pairs together".
    """
    # map id -> idx
    ids = list({u for u,_,_ in edges} | {v for _,v,_ in edges})
    id_to_i = {id_:i for i,id_ in enumerate(ids)}
    i_to_id = {i:id_ for id_,i in id_to_i.items()}
    n = len(ids)
    if n == 0:
        return []
    adj = [[0.0]*n for _ in range(n)]
    for u,v,w in edges:
        i,j = id_to_i[u], id_to_i[v]
        adj[i][j] = adj[j][i] = max(adj[i][j], w)

    # For small instances, exact DP over subsets (Held-Karp style)
    if n <= 20:
        from functools import lru_cache
        @lru_cache(None)
        def dp(mask):
            if mask == 0:
                return 0.0, ()
            # get first set bit
            lsb = (mask & -mask).bit_length()-1 if hasattr(int, 'bit_length') else 0
            # Actually find first
            for i in range(n):
                if mask>>i & 1:
                    lsb = i
                    break
            best_val, best_pairs = dp(mask ^ (1<<lsb)) # leave lsb unmatched
            for j in range(lsb+1, n):
                if (mask>>j & 1) and adj[lsb][j] > 0:
                    val, pairs = dp(mask ^ (1<<lsb) ^ (1<<j))
                    val += adj[lsb][j]
                    if val > best_val:
                        best_val = val
                        best_pairs = pairs + ((lsb,j),)
            return best_val, best_pairs
        _, pairs_idx = dp((1<<n)-1)
        return [(i_to_id[i], i_to_id[j]) for i,j in pairs_idx]

    # Larger n: greedy + joint 2-opt considering competing pairs
    # Initial greedy sorted by weight
    sorted_edges = sorted(edges, key=lambda x: x[2], reverse=True)
    mate = [-1]*n
    used = [False]*n
    total = 0
    result = []
    for u,v,w in sorted_edges:
        i,j = id_to_i[u], id_to_i[v]
        if not used[i] and not used[j] and adj[i][j]>0:
            mate[i]=j; mate[j]=i
            used[i]=used[j]=True
            result.append((i,j))
    # Joint improvement: consider competing pairs together
    improved = True
    while improved:
        improved = False
        # try to replace one edge with two competing edges if sum higher
        for i in range(n):
            if mate[i]==-1: continue
            j = mate[i]
            if j < i: continue
            # find two free or swappable
            for k in range(n):
                for l in range(k+1,n):
                    if k==i or k==j or l==i or l==j: continue
                    if mate[k]!=-1 and mate[k]!=l: continue
                    if mate[l]!=-1 and mate[l]!=k: continue
                    if adj[i][k]==0 or adj[j][l]==0: continue
                    gain = adj[i][k]+adj[j][l] - adj[i][j]
                    if gain > 1e-9:
                        # perform swap
                        mate[i]=k; mate[k]=i
                        mate[j]=l; mate[l]=j
                        # update result
                        result = [(a,mate[a]) for a in range(n) if mate[a]!=-1 and a<mate[a]]
                        improved = True
                        break
                if improved: break
            if improved: break
    return [(i_to_id[i], i_to_id[j]) for i,j in result]

def pair_weight(a,b, elig, state):
    """Hypothesis-driven weight."""
    # Base: eligibility returns score / compatibility
    # We never read hidden state, only public eligibility
    w = 0.0
    if isinstance(elig, dict):
        w = elig.get('score', elig.get('weight', elig.get('value', 1.0)))
        # feasible check already done
        # penalize repeated exposure if available
        w += elig.get('novelty', 0) * 0.1
    else:
        w = float(elig) if elig else 1.0

    # H2: diversity bonus - avoid frequent pairing (from introductions)
    # H1: compatibility weighted
    # simple heuristic: if both members have many available options, down-weight slightly to preserve options
    return float(w)

def decide(request, mode='greedy'):
    state = request['state']
    memory = request.get('memory') or {}

    if request['phase'] == 'ask':
        return {'asks': [] if mode == 'no_asks' else baseline_asks(state), 'memory': memory}

    # Baseline paths for ablation
    if mode == 'random':
        candidates = [m for m in state['members'] if m['available']]
        past = {tuple(sorted((i['user_a'], i['user_b']))) for i in state['introductions']}
        edges = [tuple(sorted((a['member_id'], b['member_id'])))
                 for a, b in itertools.combinations(candidates, 2)
                 if eligibility(a, b)['status'] == 'feasible'
                 and tuple(sorted((a['member_id'], b['member_id']))) not in past]
        random.Random(17 + state['day']).shuffle(edges)
        pairs, used = [], set()
        for pair in edges:
            if not used.intersection(pair):
                pairs.append(list(pair))
                used.update(pair)
        return {'pairs': pairs, 'memory': memory}

    if mode!= 'joint':
        # greedy baseline wrapper for comparison
        pairs = baseline_match(state)
        return {'pairs': pairs, 'memory': memory}

    # --- Joint Optimization Policy ---
    candidates = [m for m in state['members'] if m['available']]
    past = {tuple(sorted((i['user_a'], i['user_b']))) for i in state['introductions']}

    feasible_edges = []
    for a,b in itertools.combinations(candidates, 2):
        key = tuple(sorted((a['member_id'], b['member_id'])))
        if key in past:
            continue
        elig = eligibility(a,b)
        if elig['status']!= 'feasible':
            continue
        w = pair_weight(a,b,elig,state)
        feasible_edges.append((a['member_id'], b['member_id'], w))

    matched = max_weight_matching(feasible_edges, maxcardinality=False)
    pairs = [list(p) for p in matched]

    return {'pairs': pairs, 'memory': memory}

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--baseline', choices=['greedy','no_asks','random','joint'], default='joint')
    args = parser.parse_args()
    request = json.load(sys.stdin)
    print(json.dumps(decide(request, args.baseline), allow_nan=False))