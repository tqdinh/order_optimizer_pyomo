import json

from base_entity import BaseEntity


class Voucher(BaseEntity):
    
    def __init__(self,id,percent,range_from,range_to,max_applied):
        self.id=id
        self.percent=percent
        self.range_from=range_from
        self.range_to=range_to
        self.max_applied=max_applied

    def getJSONString(self):
        return super().getJSONString()


class VoucherParser(Voucher):
    def __init__(self, json_string):
            if  isinstance(json_string,str):
                _dict_=json.loads(json_string)
                super().__init__(**_dict_)   
            elif isinstance(json_string,dict):
                super().__init__(**json_string)

    def getVoucer(self):
        return Voucher(self.id,self.percent,self.range_from,self.range_to,self.max_applied)


json_string=Voucher("123",10,40,80,120).getJSONString()
print(json_string)