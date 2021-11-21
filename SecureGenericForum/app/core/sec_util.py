import json
import re

class Util:
    
    # Constructor
    def __init__(self, data, min_value=None, max_value=None):
        self.data = data
        if min_value:
            self.min_value = min_value
        
        if max_value:
            self.max_value = max_value
    
    # Check if string (keep)
    def is_string(self) -> bool:
        
        if isinstance(self.data, str):
            return self.data
        
        return False

    def is_string_alpha(self) -> bool: # (keep)
        
        if isinstance(self.data, str) and self.data.isalpha():
            return self.data
        
        return False

    def is_string_only_num(self) -> bool: # keep
        
        if isinstance(self.data, str) and self.data.isnumeric():
            return self.data
        
        return False

    def is_alnum(self) -> "bool or str": # keep
        
        if self.data.isalnum():
            return str(self.data)
        
        return False

    # Check if dict
    def is_dict(self) -> bool:
        
        if isinstance(self.data, dict):
            return self.data
        
        return False
    
    def is_dict_and_alphanumeric(self) -> "bool or json": # keep
    
        if Util(self.data).is_dict():
            for x in self.data:
                if not Util(x).is_string() or not Util(self.data[x]).is_email():
                    return False 

        return self.data

    # Check if correct email
    def is_email(self) -> bool:
        regex = r'\b[A-Za-z0-9.!#$%&’*+/=?^_`{|}~-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        ptn = re.compile(regex)
        
        if bool(ptn.fullmatch(self.data)):
            return self.data
        
        return False

    # Check if within bound
    def check_bound(self) -> bool:
        if len(self.data) > self.max_value or len(self.data) < self.min_value:
            return False
        
        return True

    # Check input content
    def check_content(self) -> list:
        regex = r'''^[A-Za-z0-9,.!#$%&+\/=?^_`{|}~()"\- ]+$'''
        regex2 = r'''(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]))'''

        temp_data = str(self.data).strip()

        ptn = re.compile(regex)
        ptn2 = re.compile(regex2)
        
        if len(temp_data) > 500:
            print("fail 0")
            return False

        if not bool(ptn.search(temp_data)):
            print("fail 1")
            return False

        elif bool(ptn2.search(temp_data)):
            print("fail 2")
            return False

        else:
            return temp_data
        
    def check_token(self) -> bool:
        regex = r'''^[a-zA-Z\d_~-]+\.[a-zA-Z\d_~-]+\.[a-zA-Z\d_~-]+'''
        ptn = re.compile(regex)

        if bool(ptn.fullmatch(self.data)):
            return self.data
        
        return False
        