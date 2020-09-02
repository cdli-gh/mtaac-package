import os
import codecs
import json
from pprint import pprint
from mtaac_package.CoNLL_collection import conll_collection
from mtaac_package.CoNLL_file_parser import conll_file
from mtaac_package.ATF_transliteration_parser import transliteration
from mtaac_package.syllabary import syllabary

syl = syllabary()
##
'''Open and load numerals'''
##num_path = r'''C:/Users/Eli/Desktop/hlam_do_datathona/mtaac-package/''' \
##           '''mtaac_package/data/old_commented_data/numerals_ATF_unicode.txt'''
##
##with codecs.open(num_path, 'r', 'utf-8') as f:
##  lines = [l.strip('\n\r').split('\t') for l in f.readlines()]
'''Print numerals as JSON to update NOT_IN_SYLLABARY'''
##for val, code in lines:
##  sign_dict = syl.find_entry_by_code(code)
##  name = sign_dict['name']
##  s = [val, name, code]
##  s = json.dumps(s).replace('[', '  [\n    ').replace(', ', ',\n    ').replace(']', '\n  ],')
##  print(s)


lss = '''no objc: 5(dic)-am3
NO OBJC 1(ban2) X
no objc: 1(dic)
no objc: 1(barig)
NO OBJC 3(ban2) X
NO OBJC 4(ban2) X
NO OBJC 2(ban2) X
no objc: 5(dic)
no objc: 8(dic)
no objc: 4(dic)
no objc: 2(dic)
NO OBJC n X
no objc: 7(dic)-kam
no objc: 3(dic)-kam
no objc: 2(dic)-kam
no objc: 7(dic)
no objc: 4(barig)
NO OBJC 5/6(dic) X
NO OBJC 1/2(dic) X
no objc: 6(dic)-kam
no objc: 9(gec2)
no objc: 1/2(dic)-ta
no objc: 1(gec'u)
no objc: e2-iti-6(dic)
no objc: 9(dic)
no objc: 1(dic)-kam
no objc: 1(dic)-ce3
no objc: 6(dic)
no objc: 3(dic)
NO OBJC 2/3(dic) X
no objc: igi-4(dic)-gal2
no objc: 1(dic@t)-kam
NO OBJC 1/3(dic) X
no objc: 3(dic@t)-kam
no objc: 3(barig)
no objc: 2(barig)
NO OBJC 5(ban2) X
NO OBJC 1(bur3) X
NO OBJC 6(bur3) X
no objc: 8(dic)-kam
no objc: 5(dic)-kam
no objc: 4(dic)-kam
no objc: 3(dic)-kam-ac
no objc: 3(gec'u)
no objc: 2(gec'u)
no objc: 3(dic)-ce3
no objc: 9(ac)
no objc: 2(barig)-ta
no objc: 3(ban2)-ta
no objc: igi-6(dic)-gal2
no objc: 7(dic)-ta
NO OBJC 9(bur3) X
NO OBJC 2(bur3) X
no objc: 3(bur'u)
NO OBJC 8(bur3) X
NO OBJC 4(bur3) X
no objc: 1(bur'u)
no objc: 4(bur'u)
NO OBJC 3(bur3) X
NO OBJC n(bur3) X
no objc: n(ece3)
no objc: n(iku)
NO OBJC n(ban2) X
NO OBJC n(barig) X
no objc: 6(dic)-ce3
no objc: 5(dic)-ce3
no objc: 7(dic)-ce3
no objc: 2/3(dic)-kam
no objc: 5/6(dic)-kam
no objc: 5(gec'u)
NO OBJC 5(bur3) X
no objc: 1/3(dic)-kam
no objc: n-kam
no objc: 2(dic)-am3
no objc: 4(dic)-ce3
no objc: 2(gec'u)-kam
no objc: 4(gec'u)
no objc: 2(dic)-ta
no objc: 1(dic)-ta
no objc: 1(dic@t)-ta
no objc: 5/6(dic)-bi
NO OBJC 7(dic)? X
no objc: 1/3(dic)-ta
no objc: 1(barig)-ta
no objc: 1/3(dic){ca}
no objc: 2(dic@t)
no objc: e2-u4-7(dic)
no objc: 2(dic)-ce3
no objc: n-ce3
no objc: 2/3(dic){ca}
no objc: e2-iti-6(dic)-ce3
no objc: 1/3(dic)-am3
no objc: 5/6(dic)-am3
no objc: 8(dic@v)
no objc: 4(dic)-am3
no objc: 3(dic)-am3
no objc: 4(dic@v)
no objc: 2(dic@t)-kam
no objc: 1(dic@t)
NO OBJC sullimₓ X
no objc: sullimx
no objc: 1/2(dic)-ce3
no objc: 3-am3
no objc: 1-am3
no objc: 1-a-ni
no objc: 2-am3
no objc: 2-a-ni
no objc: 3-a-ni
no objc: 4-am3
no objc: 4-a-ni
no objc: 5-am3
no objc: 5-a-ni
no objc: 6-am3
no objc: 6-a-ni
no objc: 7-am3
no objc: 7-a-ni
no objc: 8-am3
no objc: 8-a-ni
no objc: 9-am3
no objc: 9-a-ni
no objc: 1-a
no objc: 2-kam-ma
no objc: 2-kam-ma-am3
no objc: 1-bi
no objc: 2-bi
no objc: 2-/bi
no objc: 3-bi
no objc: 3-/bi
no objc: 4-bi
no objc: 5-bi
no objc: 5-/bi
no objc: 6-bi
no objc: 6-/bi
no objc: 7-/bi
no objc: 7-bi
no objc: 8-bi
no objc: 9-bi
no objc: 2
no objc: 1
no objc: 2-kam-ma-ce3
no objc: 2\-kam-ma
no objc: 50-bi
no objc: gi-1-nindan
no objc: 7-e
no objc: 50
no objc: 50-ne-ne
no objc: 7-na-ne-ne
no objc: nij2-ur2-4-e
no objc: 2-na-ne-ne
no objc: 3-kam-ma-ac
no objc: 4-kam-ma-ac
no objc: 5-kam-ma-ac
no objc: 6-kam-ma-ac
no objc: 7-kam-ma-ac
no objc: 6
no objc: 4
no objc: 2-a-bi
no objc: 5
NO OBJC 10 X
no objc: 7
NO OBJC 300 X
NO OBJC 600 X
no objc: 1-kam-ma
no objc: 3-kam-ma
no objc: 4-kam-ma
no objc: 5-kam-ma
no objc: 6-kam-ma
no objc: 7-kam-ma
no objc: 3
no objc: 1-gin7
no objc: 10-am3
no objc: 600-am3
no objc: 600\-am3
no objc: /ceg9\-saj-6
no objc: muc-saj-7
no objc: ceg9-saj-6
no objc: /muc-saj\-7
no objc: 50-ju10
no objc: 7\-e
no objc: 2-kam
no objc: 3-kam
NO OBJC ugu)ugu4 X
no objc: /ugu)ugu4-bi
no objc: nij2-ur2-4
no objc: 70-am3
NO OBJC isin2/si) X
no objc: {d}nin-isin2/si)-na
no objc: nu-5-am3
no objc: nu-10-am3
NO OBJC 5/6 X
no objc: 50(source:5/6)
no objc: 30
no objc: 1-a-kam
no objc: 50-am3
no objc: 2-a
no objc: 1-ta-am3
no objc: 2-a-ne-ne-ne
no objc: 9-kam
no objc: 7-/na\-ce3
no objc: 2-/am3
no objc: 5-/am3
no objc: 6-/am3
no objc: 7-me-ec
no objc: 2-kam-/ma
no objc: 7-/kam\-ma
no objc: 7-/bi-e\-ne
no objc: 7-be2-e-ne
no objc: 4-kam
no objc: 5-kam
no objc: 6-kam
no objc: 2-e
no objc: 60
no objc: 3\-kam-ma-ce3
no objc: 3\-kam-ma
no objc: 4-kam-ma-ce3
no objc: 6-kam-ma-ce3
no objc: 2-na-ne-ne-bi
no objc: 7-kam\-ma
no objc: 1-e
no objc: 4-/kam-ma
no objc: 5-/kam-ma
no objc: 6-kam-ma-ka
no objc: 7-be2-ne
no objc: 300-ta-a-me-ec
no objc: 600-ta-a-me-ec
no objc: 3600-3600-3600-3600-3600-3600-3600
no objc: 7-ta-me-ec
no objc: 8-kam-ma-ne-ne
no objc: 3-kam-ma-bi
no objc: 7-ta
NO OBJC 14 X
no objc: 14-me-ec
no objc: 50-gin7
no objc: 50-uc
NO OBJC ub2/lu X
no objc: {kuc}lu-ub2/lu-ub2-cir
no objc: 3-kam-ma-ce3
NO OBJC source:unug X
no objc: aratta{ki}(source:unug{ki}-ga)-ka
NO OBJC 15 X
no objc: 15-/am3
no objc: 2-kam-ma-ac
NO OBJC 100 X
NO OBJC 2760 X
no objc: 1200
NO OBJC 1320 X
no objc: 1800
NO OBJC 900 X
NO OBJC 660 X
NO OBJC 2220 X
NO OBJC 1080 X
NO OBJC 690 X
NO OBJC 360 X
NO OBJC 990 X
NO OBJC 960 X
NO OBJC 1110 X
NO OBJC 160 X
NO OBJC 120 X
NO OBJC 280 X
NO OBJC 140 X
NO OBJC 144 X
no objc: 20
no objc: 2-a-kam
no objc: 3-a-kam
no objc: 4-a-kam
no objc: 5-a-kam
no objc: 2-na-bi-da
NO OBJC 1/2 X
no objc: 7-ce3
no objc: 2-a-ba
no objc: 50-a
no objc: 2-nam
no objc: 1-ta
no objc: 7-kam-ma-ka
no objc: muc(source:ur)-saj-7-am3
no objc: 2-kam-ni
no objc: 10-/am3
no objc: 4-ba
no objc: 4-ba-me-en
no objc: 7-bi-ta
no objc: 10-ni
no objc: 1-ra
no objc: 2-ce3
no objc: 7-na
NO OBJC )dusu X
no objc: )dusu-ka
no objc: 7-na-ni
no objc: 3-gin7
no objc: 4-kam-/ma
no objc: 8-kam-ma
no objc: 9-kam-ma-ta
no objc: {d}i-bi2-30-ju10
no objc: 7-a
no objc: 15-bi
no objc: 10-ba
NO OBJC gur21/ur3) X
no objc: {kuc}gur21/ur3)-ra2
no objc: 15-kam-/ma-ta
no objc: 40
NO OBJC 25 X
NO OBJC 45 X
NO OBJC 7200 X
no objc: 70
no objc: 1-kam
no objc: 1-ka
NO OBJC 26 X
NO OBJC 72 X
no objc: 15-ta-am3
no objc: 7-kam-ma-/ta
no objc: 5-/kam\-ma-ta
NO OBJC ece3/ece3 X
no objc: ece3/ece3{iku}
no objc: 15-kam
NO OBJC 1/3 X
NO OBJC 2/3 X
no objc: 2-kam-ma-bi
no objc: 2-ta-am3
no objc: 9-kam-ma
no objc: 7-ba
no objc: 4-za
no objc: 50-me-ec
NO OBJC lu? X
no objc: he2-em-mi-gu7(source:lu?)
no objc: 36000
no objc: 3600-am3
no objc: 36000-am3
no objc: 3600
no objc: 5-ta
no objc: 4-me-ec
NO OBJC im? X
no objc: im-di-ri(source:/im?)
no objc: 7-gin7
no objc: 50-e
NO OBJC 24 X
NO OBJC 23 X
NO OBJC 13 X
no objc: 8
NO OBJC 12 X
no objc: 9
NO OBJC 17 X
NO OBJC 11 X
NO OBJC 22 X
NO OBJC 16 X
no objc: 4-e
no objc: 11-kam-ma-bi-me-en
no objc: 12-am3
no objc: 30-am3
no objc: 40-am3
no objc: 3-kam-ma-ne-ne-/a
no objc: 2-na-/ne\-ne
no objc: 2-na-/ne-ne
no objc: 4-/am3
NO OBJC 180 X
NO OBJC 18 X
no objc: 3-/am3
no objc: nij2-/ur2\-4
no objc: 50-/am3
NO OBJC 55 X
no objc: 55-am3
NO OBJC 1(cargal) X
no objc: 1(cargal){gal}
NO OBJC 2(bur'u@c) X
NO OBJC 5(bur3@c) X
NO OBJC 1(bur'u@c) X
NO OBJC 1(bur3@c) X
NO OBJC 2(u@c) X
NO OBJC 3(u@c) X
NO OBJC 1/2(ac@c) X
NO OBJC 1(ac@c) X
NO OBJC 4(car'u@c) X
NO OBJC 3(ac@c) X
no objc: 2(u@c)-am6
no objc: 1(ac@c)-am6
NO OBJC 6(ac@c) X
no objc: 6(ac@c)-am6
NO OBJC 4(u@c) X
NO OBJC 1(u@c) X
NO OBJC 5(ac@c) X
no objc: 5(ac@c)-am6
NO OBJC 7(ac@c) X
NO OBJC 2(barig@c) X
NO OBJC 1(barig@c) X
NO OBJC 1(car'u@c) X
no objc: 1(car'u@c)-ta
NO OBJC 3(ban2@c) X
NO OBJC 4(ac@c) X
NO OBJC 2(ac@c) X
NO OBJC u@c X
NO OBJC 1(gec'u@c) X
NO OBJC 2(gec'u@c) X
NO OBJC 2(iku@c) X
'''

lss_main_lst = [l.replace('NO OBJC ', '').strip('X \r\n')
                for l in lss.split('\n') if 'NO OBJC ' in l]

name_lst = [el for el in sorted(lss_main_lst) if syl.find_entry_by_name(el)]
val_lst = [el for el in sorted(lss_main_lst) if syl.find_entry_by_value(el)]

print(len(lss_main_lst))
print(len(name_lst), name_lst)
print(len(val_lst), val_lst)

  
##
##for s_dict in syl.signs_lst:
##  print(s_dict)

'''Open a CoNLL collection from pre-saved JSON, don't lemmatize'''
##data_path = os.path.join('conll_data') #path/to/dir/ (containing conll_collection.json)
##cc = conll_collection(source_root=data_path,
##                      json_filename='conll_collection.json',
##                      lemmatize=False,)
##
##no_unicode = ['_']
##for c in cc.conll_lst:
##  c_obj = conll_file(data_dict=c)
##  for t in c_obj.tokens_lst:
##    atf_obj = transliteration(t['FORM_ATF'])    
##    if not hasattr(atf_obj, 'sign_list'):
##      if t['FORM_ATF'] not in no_unicode:
##        print('\tNO SIGN:', t['FORM_ATF'])
##        no_unicode.append(t['FORM_ATF'])
##    else:
##      for s, sd in zip(atf_obj.sign_list, atf_obj.syl_dict_lst):
##        if sd:
##          if 'unicode' in sd.keys():
##            pass
##            #print(s['value']+s['index'], sd['unicode'])
##          elif s['value']+s['index'] not in no_unicode:
##            print('NO UTF8', s['value']+s['index'], 'X')
##            no_unicode.append(s['value']+s['index'])
##        elif s['value']+s['index'] not in no_unicode \
##             and not syl.find_entry_by_value(s['value']+s['index']):
##          print('NO OBJC', s['value']+s['index'], 'X')
##          no_unicode.append(s['value']+s['index'])
##
##    for sd in atf_obj.syl_dict_lst:
##      if sd:
##        if 'unicode' not in sd.keys() and t['FORM_ATF'] not in no_unicode:
##          print('no utf8:', t['FORM_ATF'])
##          no_unicode.append(t['FORM_ATF'])
##        else:
##          pass
##          #print(sd['unicode'])
##      elif t['FORM_ATF'] not in no_unicode:
##        print('no objc:', t['FORM_ATF'])
##        no_unicode.append(t['FORM_ATF'])
    

''' Split & export '''
#cc.split_and_export()

##''' Export as Unicode '''
##cc.export_unicode()

##''' Dump collection to JSON '''
##cc.dump_collection_to_json()
