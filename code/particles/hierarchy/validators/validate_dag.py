#!/usr/bin/env python3
import json, sys, pathlib
from collections import defaultdict, deque

def reachable(graph, src):
    seen=set()
    q=deque([src])
    while q:
        u=q.popleft()
        for v in graph[u]:
            if v not in seen:
                seen.add(v); q.append(v)
    return seen

def main(path):
    data=json.loads(pathlib.Path(path).read_text())
    graph=defaultdict(list)
    for e in data["edges"]:
        graph[e["from"]].append(e["to"])
    failures=[]
    for f in data["forbidden_sources"]:
        r=reachable(graph,f)
        for target in data["protected_targets"]:
            if target in r:
                failures.append((f,target))
    print(json.dumps({"pass": not failures, "forbidden_paths": failures}, indent=2))
    return 0 if not failures else 1

if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv)>1 else "certificates/DAG_U.json"))
