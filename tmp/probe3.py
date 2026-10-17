import json, os

p = os.path.join(os.path.dirname(__file__), '..', 'estratti', 'PopSaveGameSlot3Index0.AlkSave.json')
d = json.load(open(p, encoding='utf-8'))

want = ('m_gameStatsSaves', 'm_worldItemsStats', 'm_worldItemCounters', 'm_archstoneSaveData',
        'm_challengesCompletions', 'm_unlockedRiddles', 'm_solvedRiddles', 'm_unlockedGuids',
        'm_bossReplaySaveData', 'm_bossRushSaveData')

for si, scene in enumerate(d['m_list']):
    for ei, ent in enumerate(scene.get('m_entities', [])):
        for fi, fr in enumerate(ent.get('m_frames', [])):
            if any(w in fr for w in want):
                print('=== scene', si, scene.get('m_sceneName'), 'entity', ei, 'frame', fi, 'type=', fr.get('@type'))
                for w in want:
                    if w in fr:
                        v = fr[w]
                        print('---', w, type(v).__name__, (len(v) if isinstance(v, (list, dict)) else v))
                        print(json.dumps(v, ensure_ascii=False)[:3000])
                        print()
