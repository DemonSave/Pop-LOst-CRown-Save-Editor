import json, os, collections

p = os.path.join(os.path.dirname(__file__), '..', 'estratti', 'PopSaveGameSlot3Index0.AlkSave.json')
d = json.load(open(p, encoding='utf-8'))

print('root keys:', list(d.keys()))
lst = d['m_list']
print('m_list len', len(lst))
for i, frame in enumerate(lst):
    ents = frame.get('m_entities', [])
    names = []
    for e in ents:
        n = e.get('m_name') or e.get('m_entityName') or e.get('m_id') or list(e.keys())[:3]
        names.append(n)
    print(i, 'keys=', list(frame.keys())[:8], 'entities=', len(ents), names[:6])
