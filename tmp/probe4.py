import json, os, collections

base = os.path.join(os.path.dirname(__file__), '..', 'estratti')
d = json.load(open(os.path.join(base, 'PopSaveGameSlot3Index0.AlkSave.json'), encoding='utf-8'))
opt = json.load(open(os.path.join(base, 'GameOptionsSlot3Index0.AlkContent.json'), encoding='utf-8'))

# search for blackboard in all json
for fn in ('PopSaveGameSlot3Index0.AlkSave.json', 'GameOptionsSlot3Index0.AlkContent.json', 'ProgressionSlot3Index0.AlkContent.json'):
    txt = open(os.path.join(base, fn), encoding='utf-8').read()
    print(fn, 'blackboard count:', txt.lower().count('blackboard'), '| stats count:', txt.count('Stats'), '| hash count:', txt.count('hash'))

# gather ints that are 32-bit-ish hash magnitudes
vals = collections.Counter()
def walk(node, path, depth=0):
    if depth > 60: return
    if isinstance(node, dict):
        for k, v in node.items():
            np = path + '/' + str(k)
            if isinstance(v, int) and not isinstance(v, bool) and abs(v) > 1000000:
                vals[(k, v)] += 1
            walk(v, np, depth + 1)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            walk(v, path + '[%d]' % i, depth + 1)
walk(d, '')
print('\n--- int fields with big values (key, value): count ---')
for (k, v), c in vals.most_common(60):
    print(c, k, v)
