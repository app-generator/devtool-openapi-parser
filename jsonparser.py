

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
import requests
import json
import operator
import re
import sys
import warnings
from urllib import parse as urlparse
from urllib.parse import unquote
from urllib.request import urlopen
from glom import glom
from collections import OrderedDict
from pprint import pprint

iteritems = operator.methodcaller("items")
unicode = str
basestring = str
input_filename= sys.argv[1] 
ouput_filename= sys.argv[2] 

print(sys.argv[1] , sys.argv[2] )
#%%----------------------------------------------------------------
def refHandler(content):
    return content.split('/')[-1]


def getKeysofanObj(object, prev_key = None, keys = []):
    if type(object) != type({}):
        keys.append(prev_key)
        return keys
    new_keys = []
    for k, v in object.items():
        if prev_key != None:
            if k.find('ref')==1 :
                print(k , v )
            new_key = "{}.{}".format(prev_key, k)
        else:
            new_key = k
        new_keys.extend(getKeys(v, new_key, []))
    return new_keys



def get_keys(d, curr_key=[]):
    for k, v in d.items():
        
        if isinstance(v, dict):
            yield from get_keys(v, curr_key + [k])
        elif isinstance(v, list):
            for i in v:
                yield from get_keys(i, curr_key + [k])
        else:
            yield '.'.join(curr_key + [k])
            


def dict_replace_value(d, old, new):
    x = {}
    for k, v in d.items():
        if isinstance(v, dict):
            v = dict_replace_value(v, old, new)
        elif isinstance(v, list):
            v = list_replace_value(v, old, new)
        elif isinstance(v, str):
            v = v.replace(old, new)
        x[k] = v
    return x




def replace_keys(data_dict, key_dict):
    new_dict = { }
    if isinstance(data_dict, list):
        dict_value_list = list()
        for inner_dict in data_dict:
            dict_value_list.append(replace_keys(inner_dict, key_dict))
        return dict_value_list
    else:
        for key in data_dict.keys():
            value = data_dict[key]
            new_key = key_dict.get(key, key)
            if isinstance(value, dict) or isinstance(value, list):
                new_dict[new_key] = replace_keys(value, key_dict)
            else:
                new_dict[new_key] = value
        return new_dict
    return new_dict



def walk_json(obj, key_transform):

    assert isinstance(obj, dict)

    def _walk_json(obj, new):

        if isinstance(obj, dict):

            if isinstance(new, dict):
                for key, value in obj.items():

                    new_key = key_transform(key)

                    if isinstance(value, dict):
                        new[new_key] = {}
                        _walk_json(value, new=new[new_key])

                    elif isinstance(value, list):
                        new[new_key] = []
                        for item in value:
                            _walk_json(item, new=new[new_key])

                    else: 
                        new[new_key] = value

            elif isinstance(new, list):
                new.append(_walk_json(obj, new={}))

        else: 
            new.append(obj)
            

#%%----------------------------------------------------------------
class DesiredClass(object):
    def __init__(self, jsonfromsource):

        self.description = replacedRefDict['info']['description']
        self.models = replacedRefDict['components']['schemas']
        self.openapi = replacedRefDict['openapi']
        self.title = replacedRefDict['info']['title']
        self.version = replacedRefDict['info']['version']
        
        pprint(self.__dict__)
        with open(f'{ouput_filename}', 'w') as outfile:
            json.dump(self.__dict__, outfile)
        
    def return_json(self):
        return replacedRefDict

if __name__ == "__main__":
    
    source = open(f'{input_filename}')
    source= json.load(source)
    allthekeys = [*get_keys(source)]
    alltheValues= [ glom(source, item) for item in allthekeys]
    listofRefitem = [item for item in alltheValues if item.find('#')!=-1]

    for item in listofRefitem:
        source= dict_replace_value(source, item , item.split('/')[-1])
    template_ = { '$ref' : 'type'}
    replacedRefDict = replace_keys(source, template_)
    u = DesiredClass(replacedRefDict).return_json()






