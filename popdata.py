"""
Dati di gioco estratti dai bundle Addressables di Prince of Persia: The Lost Crown.

Sorgenti (installazione Steam, build con DLC1):
  StreamingAssets/aa/StandaloneWindows64/worlddata_mainworld_assets_all.bundle
      -> PortalData (m_portalType == 1 = viaggio rapido), LevelData (scena/nome)
  StreamingAssets/aa/StandaloneWindows64/scriptablesingleton__scenemetadatamanager_assets_all.bundle
      -> posizioni dei punti di viaggio rapido (FastTravelPositions)
  StreamingAssets/aa/StandaloneWindows64/mandatory_gamemanager_assets_all.bundle
      -> lezioni di Artaban (m_GUID + locId)
  StreamingAssets/aa/StandaloneWindows64/data_scriptableobjects_localization_assets_all.bundle
      -> nomi localizzati delle lezioni (italiano/inglese)

File generato da tmp/extract_gamedata.py: non modificare a mano.
"""

REGIONS = [('CIT_LOW', 'Città Bassa'), ('CIT_UPP', 'Città Alta'), ('CIT_OLD', 'Vecchia Strada Reale'), ('CIT_DEP', 'Profondità della Città'), ('HYR_AUT', 'Foresta Ircana (autunno)'), ('HYR_SOM', 'Foresta Ircana (Soma)'), ('SAC_SAC', 'Archivi Sacri'), ('NEC_TOW', 'Torre del Silenzio'), ('END_PIT', 'Fossa delle Sabbie Eterne'), ('VAL_RAG', 'Mare Infernale'), ('VAL_SUN', 'Baia del Sole'), ('RAD_', 'DLC — Mente di Radjen'), ('CU3', 'DLC'), ('KIN_', 'Monte Qaf'), ('CRO_', 'Crocevia dei Tempi')]

FAST_TRAVEL = [
    {'guid': 'e382cbb0dd2c709498e3224d9a9d4dda', 'level': 'SAC_SAC02_11_WakWak', 'level_guid': '58a5a086d65ee7d429e01fdc00d63001', 'code': 'SAC_SAC02_11_WakWak', 'region': 'Archivi Sacri', 'portal': '2985287e-a76a-4b4b-8bc5-ec55a2a0075b', 'pos': {'x': 24.0, 'y': 14.5, 'z': 0.0}},
    {'guid': '3ec38959037f155429336ed5ec4adb78', 'level': 'SAC_SAC_14_Homa_Room', 'level_guid': 'a1d6076da2155cc47b3d876f81b942ee', 'code': 'SAC_SAC_14_Homa_Room', 'region': 'Archivi Sacri', 'portal': 'e0402931-ce8a-4b94-a57c-42e31fbebeef', 'pos': {'x': -258.0, 'y': 158.5, 'z': 0.0}},
    {'guid': 'f3b6821137a76cf4f8e7080dd936122f', 'level': 'VAL_SUN_03_WAKWAK_CAVE', 'level_guid': '587f4dba0d8e37f4eba87aa604fdad76', 'code': 'VAL_SUN_03_WAKWAK_CAVE_0', 'region': 'Baia del Sole', 'portal': '8eed6588-b535-4ad5-b00e-49fca564eefd', 'pos': {'x': 43.283714294433594, 'y': 11.000000953674316, 'z': 0.0}},
    {'guid': '3d2a653fbf5425a468e8d24b432e6a31', 'level': 'VAL_SUN_08_PIRATE_AMBUSH_ARENA', 'level_guid': '6d040f64b1b0ab549a1ea41557cc6bbc', 'code': 'VAL_SUN_08_PIRATE_AMBUSH_ARENA', 'region': 'Baia del Sole', 'portal': '29cdfe3c-c3b9-4f71-affb-5c0e16ffd996', 'pos': {'x': 28.5, 'y': 32.5, 'z': 0.0}},
    {'guid': '67cce6a4a91143e4bbaa97b9e7efb0eb', 'level': 'CIT_UPP_03_Day_Temple', 'level_guid': '30c866617062c0245a918b836c253962', 'code': 'CIT_UPP_03_Day_Temple_0', 'region': 'Città Alta', 'portal': '6b8828bb-5aec-4477-83b2-a63ee639720f', 'pos': {'x': 91.5, 'y': 49.5, 'z': 0.0}},
    {'guid': '64a01ad13b21af64882da2c14c5af3bd', 'level': 'CIT_UPP_12_Night_Temple', 'level_guid': '71b504c074e7b73449003f3dc639c10a', 'code': 'CIT_UPP_12_Night_Temple_0', 'region': 'Città Alta', 'portal': '5a0bf105-bfe8-4c1d-b7b2-bc0869d701af', 'pos': {'x': 88.5, 'y': 57.5, 'z': 0.0}},
    {'guid': '319c48eb051141144b2d8c9fd0a9dd87', 'level': 'CIT_UPP_21bis_BirdCage', 'level_guid': 'f29cc214b155c5d46bff9a9b26995377', 'code': 'CIT_UPP_21bis_BirdCage', 'region': 'Città Alta', 'portal': '9f3f9c77-e492-4ef5-ad0d-8abc29814c20', 'pos': {'x': 47.0, 'y': 85.0, 'z': 0.0}},
    {'guid': 'ebe637b2e8239a24995e35111ad19eb0', 'level': 'CIT_UPP_24_Engine_Puzzle', 'level_guid': '8c32d1157b278c54da40e0ea76140a1b', 'code': 'CIT_UPP_24_Engine_Puzzle', 'region': 'Città Alta', 'portal': 'd9a01684-5e76-47fe-891a-0b78887ea76e', 'pos': {'x': 42.5, 'y': 60.04150390625, 'z': 0.0}},
    {'guid': '05343dbd8dcf6044fb8d011418f03313', 'level': 'CIT_UPP_25_Royal_Corridor', 'level_guid': 'e4403a2443a3b9547a6699dfb12c33fc', 'code': 'CIT_UPP_25_Royal_Corridor', 'region': 'Città Alta', 'portal': '27a5844b-0940-42c3-afd4-55de1cfc6edc', 'pos': {'x': 184.5, 'y': 90.0, 'z': 0.0}},
    {'guid': '116d826ed4ef37e478505f664f572c2e', 'level': 'CIT_LOW_07_Up', 'level_guid': '8877a2e83bd71c74dbbaf265c3836d20', 'code': 'CIT_LOW_07_Up', 'region': 'Città Bassa', 'portal': '240127b9-b8ab-454c-b3d4-ae3cc236d4c9', 'pos': {'x': -61.0, 'y': -11.0, 'z': 0.0}},
    {'guid': 'eeb98bd363721054bbbf57fa6773a624', 'level': 'CIT_LOW_10', 'level_guid': '061fa5b4e91673c459a3113ab921e270', 'code': 'CIT_LOW_10', 'region': 'Città Bassa', 'portal': '90807acb-a782-4ca2-a577-a1c2ae282cfd', 'pos': {'x': 128.5, 'y': 55.0, 'z': 0.0}},
    {'guid': '2eaa7c6d97cfa1649bcfc54498f0e790', 'level': 'HYR_SOM_04Bis_Uncursed_SomaTree', 'level_guid': '8421fa5b65774f14087435e8e9da1cb3', 'code': 'HYR_SOM_04Bis_Uncursed_SomaTree', 'region': 'Foresta Ircana (Soma)', 'portal': '26aa582b-1fe5-4f9b-892c-00101e620eb1', 'pos': {'x': 25.79998779296875, 'y': 5.0, 'z': 0.0}},
    {'guid': '8c2b08673aa4bfd489469909a60571db', 'level': 'HYR_SOM_04_SomaTree', 'level_guid': 'ccce05b4064877b41a9c73a82b443545', 'code': 'HYR_SOM_04_SomaTree_0', 'region': 'Foresta Ircana (Soma)', 'portal': '443c04d3-0766-4d2a-a013-010cccc3f750', 'pos': {'x': 26.59002685546875, 'y': 5.0, 'z': 0.0}},
    {'guid': '6746ddd1fd75ceb4fa07a1c6221fd818', 'level': 'HYR_SOM_11_Foliage_Crossroad', 'level_guid': '0e9eff3059ff22649a3ef5dd434bc139', 'code': 'HYR_SOM_11_Foliage_Crossroad', 'region': 'Foresta Ircana (Soma)', 'portal': 'eeddd0af-e8bd-4a6f-bcdf-4736a8168929', 'pos': {'x': 65.5, 'y': 31.0, 'z': 0.0}},
    {'guid': '02aeadad2ad4d3e419e6aea894e313dd', 'level': 'HYR_SOM_23_OldTower', 'level_guid': '6841825a62f8ffb40ab35b47ecd1d5d9', 'code': 'HYR_SOM_23_OldTower', 'region': 'Foresta Ircana (Soma)', 'portal': 'e7770602-4fda-420a-8747-09249329573a', 'pos': {'x': 3.0, 'y': 23.0, 'z': 0.0}},
    {'guid': 'a80073e0a44389c41aa5b78fb870fe53', 'level': 'END_PIT_10_HubDoubleJump', 'level_guid': '828c41abe4173bb45aee6f74760b996d', 'code': 'END_PIT_10_HubDoubleJump', 'region': 'Fossa delle Sabbie Eterne', 'portal': 'bfc3fa02-c2d4-4064-8806-1c9b1d51b147', 'pos': {'x': 63.5, 'y': 13.0, 'z': 0.0}},
    {'guid': '0458bc4f688943242948ac55ba9588b7', 'level': 'END_PIT_11_AzdahaArenaEntrance', 'level_guid': 'bbf2f9560a8b8b9409dadcec2bdb2e3c', 'code': 'END_PIT_11_AzdahaArenaEntrance', 'region': 'Fossa delle Sabbie Eterne', 'portal': '758a8e0d-60b5-402e-9b6f-aa052fb6a855', 'pos': {'x': 71.0, 'y': 49.0, 'z': 0.0}},
    {'guid': 'e8e46714d6c24734c9ad49d3fed99816', 'level': 'VAL_RAG_03_frozenboat2_inside', 'level_guid': 'ec8b9149ff89f8a4cb6291fa521592aa', 'code': 'VAL_RAG_03_frozenboat2_inside', 'region': 'Mare Infernale', 'portal': 'e6cfe9a8-33e5-45a1-80a8-3f6962b7ba44', 'pos': {'x': 58.5, 'y': 13.5, 'z': 0.0}},
    {'guid': '77e7f50029321894b9c13014b4296855', 'level': 'VAL_RAG_12_unfrozenoutside4_homa', 'level_guid': '5b4fe6572b7753d4b8d74076306270d6', 'code': 'VAL_RAG_12_unfrozenoutside4_homa', 'region': 'Mare Infernale', 'portal': 'e7c79f93-70c5-42c3-a46a-f426f9cf9550', 'pos': {'x': 5.5, 'y': 3.0, 'z': 0.0}},
    {'guid': '03247182b31d13e439daa2b0638f4718', 'level': 'CIT_DEP02_03_nolight2_sphincterhall', 'level_guid': '4bde7e4617438dc4fb596cb6cb1f95f8', 'code': 'CIT_DEP02_03_nolight2_sphincterhall', 'region': 'Profondità della Città', 'portal': 'd511e0e9-450e-4243-b71b-9984df7c5793', 'pos': {'x': 0.0, 'y': 5.5, 'z': 0.0}},
    {'guid': '5651ecdf361fe264dae697812b12f121', 'level': 'CIT_DEP_05_CollectorShopAccess', 'level_guid': 'c320bface06c5d04dac48f4522d2f576', 'code': 'CIT_DEP_05_CollectorShopAccess', 'region': 'Profondità della Città', 'portal': '7fafebda-9b0d-4404-a8a0-a8156a84e2a2', 'pos': {'x': 25.0, 'y': 8.0, 'z': 0.0}},
    {'guid': '308eb4e09298a4049bc3176bfaf40147', 'level': 'CIT_DEP_11_UndeadErlik', 'level_guid': 'cfe8f1fe056d1f7498917a3ff0f4509b', 'code': 'CIT_DEP_11_UndeadErlik', 'region': 'Profondità della Città', 'portal': 'f1038f50-7e1d-402a-a377-a1ff1b0e255c', 'pos': {'x': 60.0, 'y': 2.5, 'z': 0.0}},
    {'guid': 'ecb762b0dbe82eb44aea161ca454df92', 'level': 'NEC_TOW_12_WakWak_And_Hermit', 'level_guid': '6d5a1d46310b23d49baa660f935038fe', 'code': 'NEC_TOW_12_WakWak_And_Hermit', 'region': 'Torre del Silenzio', 'portal': 'eb8abb6c-7c16-4e1c-bbf7-f1443c822942', 'pos': {'x': 84.5, 'y': 75.0, 'z': 0.0}},
]

ARTABAN_LESSONS = [
    {'guid': '3f6a90b7d458227408eadf199539a7ec', 'code': 'ArtabanLesson_GroundedAttacks', 'name_it': 'Attacchi standard', 'name_en': 'Standard Attacks'},
    {'guid': '957628b4557e34e46b143aacd2dfb0c2', 'code': 'ArtabanLesson_Launchers', 'name_it': 'Lanci', 'name_en': 'Launchers'},
    {'guid': 'c5a92eba956a0cc4c9ddb57e366cace9', 'code': 'ArtabanLesson_Aerials', 'name_it': 'Attacchi in aria', 'name_en': 'Aerial Attacks'},
    {'guid': '23d05698c0ae5f848bb590ebe492395e', 'code': 'ArtabanLesson_Charged', 'name_it': 'Attacchi con carica', 'name_en': 'Charged Attacks'},
    {'guid': '4d83e5f7508f0464ca85d444699939c8', 'code': 'ArtabanLesson_NMEs', 'name_it': 'Reazioni nemiche', 'name_en': 'Enemies Reactions'},
    {'guid': '7de0a85384bed374ba7363c270fd4b68', 'code': 'ArtabanLesson_Defense', 'name_it': 'Opzioni di difesa', 'name_en': 'Defensive Options'},
    {'guid': 'cfd2434896046274194f29aefca3a268', 'code': 'ArtabanLesson_Movement', 'name_it': 'Mosse avanzate', 'name_en': 'Advanced Movements'},
    {'guid': 'b6d267ec16b83dd44800f47db6a9d0da', 'code': 'ArtabanLesson_Parry', 'name_it': 'Parata', 'name_en': 'Parry'},
    {'guid': '360d3c6811c4fc2438e0e3c1862e85b9', 'code': 'ArtabanLesson_Athra', 'name_it': 'Onda di Athra', 'name_en': 'Athra Surge'},
    {'guid': '6b76bae8344eef4499ac033fac1ebd9c', 'code': 'ArtabanLesson_Bow', 'name_it': 'Arco e chakram', 'name_en': 'Bow & Chakram'},
    {'guid': '1333a7f7b4c415745b3595684db1cd4d', 'code': 'ArtabanLesson_Teleport', 'name_it': 'Ombra di Simurgh', 'name_en': 'Shadow of the Simurgh'},
    {'guid': 'fb9e639051c6ed842a7945083924060a', 'code': 'ArtabanLesson_Scarf', 'name_it': 'Trama del mondo', 'name_en': 'Fabric of the World'},
    {'guid': 'c10b42a789bd2ca4288e35efb1069f3f', 'code': 'ArtabanLesson_Airdash', 'name_it': 'Scatto di Simurgh', 'name_en': 'Rush of the Simurgh'},
]
