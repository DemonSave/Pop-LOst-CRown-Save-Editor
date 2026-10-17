import json, os, collections

p = os.path.join(os.path.dirname(__file__), '..', 'estratti', 'PopSaveGameSlot3Index0.AlkSave.json')
d = json.load(open(p, encoding='utf-8'))

# 1) all component/frame keys with counts
frame_keys = collections.Counter()
for frame in d['m_list']:
    for e in frame.get('m_entities', []):
        for fr in e.get('m_frames', []):
            for k in fr:
                frame_keys[k] += 1
print('--- frame keys (components?) ---')
for k, c in frame_keys.most_common():
    print(c, k)
