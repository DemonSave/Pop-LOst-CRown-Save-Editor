import json, os, zlib, hashlib, struct

base = os.path.join(os.path.dirname(__file__), '..', 'estratti')
d = json.load(open(os.path.join(base, 'PopSaveGameSlot3Index0.AlkSave.json'), encoding='utf-8'))

scenes = [(s.get('m_sceneName'), s.get('m_sceneGUID')) for s in d['m_list']]
print('sample scenes:', scenes[:8])

def u32(x): return x & 0xffffffff
def s32(x):
    x &= 0xffffffff
    return x - 0x100000000 if x >= 0x80000000 else x

def fnv1a(b):
    h = 0x811c9dc5
    for c in b:
        h ^= c; h = u32(h * 0x01000193)
    return h
def fnv1(b):
    h = 0x811c9dc5
    for c in b:
        h = u32(h * 0x01000193); h ^= c
    return h
def djb2(b):
    h = 5381
    for c in b: h = u32(h * 33 + c)
    return h
def djb2x(b):
    h = 5381
    for c in b: h = u32(h * 33) ^ c
    return h
def sdbm(b):
    h = 0
    for c in b: h = u32(c + (h << 6) + (h << 16) - h)
    return h
def crc(b): return zlib.crc32(b) & 0xffffffff
def md5le(b): return struct.unpack('<I', hashlib.md5(b).digest()[:4])[0]
def md5be(b): return struct.unpack('>I', hashlib.md5(b).digest()[:4])[0]
def md5le_l(b): return struct.unpack('<I', hashlib.md5(b).digest()[-4:])[0]
def md5be_l(b): return struct.unpack('>I', hashlib.md5(b).digest()[-4:])[0]
def sha1le(b): return struct.unpack('<I', hashlib.sha1(b).digest()[:4])[0]

def murmur3(data, seed=0):
    c1, c2 = 0xcc9e2d51, 0x1b873593
    h = seed; n = len(data); i = 0
    while i + 4 <= n:
        k = struct.unpack_from('<I', data, i)[0]; i += 4
        k = u32(k * c1); k = ((k << 15) | (k >> 17)) & 0xffffffff; k = u32(k * c2)
        h ^= k; h = ((h << 13) | (h >> 19)) & 0xffffffff; h = u32(h * 5 + 0xe6546b64)
    k = 0
    tail = data[i:]
    if len(tail) == 3: k ^= tail[2] << 16
    if len(tail) >= 2: k ^= tail[1] << 8
    if len(tail) >= 1:
        k ^= tail[0]; k = u32(k * c1); k = ((k << 15) | (k >> 17)) & 0xffffffff; k = u32(k * c2); h ^= k
    h ^= n; h ^= h >> 16; h = u32(h * 0x85ebca6b); h ^= h >> 13; h = u32(h * 0xc2b2ae35); h ^= h >> 16
    return h

funcs = {'fnv1a': fnv1a, 'fnv1': fnv1, 'djb2': djb2, 'djb2x': djb2x, 'sdbm': sdbm,
         'crc32': crc, 'md5le': md5le, 'md5be': md5be, 'md5le_l': md5le_l, 'md5be_l': md5be_l,
         'sha1le': sha1le, 'mm3': murmur3}

names = [n for n, g in scenes if n and isinstance(g, int)]
pairs = [(n, g) for n, g in scenes if n and isinstance(g, int)]
print('pairs', len(pairs))
for fname, f in funcs.items():
    for variant, enc in (('raw', 'utf-8'), ('lower', 'utf-8'), ('upper', 'utf-8')):
        ok = 0
        for n, g in pairs[:20]:
            s = n if variant == 'raw' else (n.lower() if variant == 'lower' else n.upper())
            try:
                hv = f(s.encode(enc))
            except Exception:
                continue
            if s32(hv) == g or hv == (g & 0xffffffff):
                ok += 1
        if ok:
            print('MATCH', fname, variant, ok, '/', len(pairs[:20]))
