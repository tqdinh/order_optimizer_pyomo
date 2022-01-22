import json
from json import JSONEncoder

from base_entity import BaseEntity

class Order(BaseEntity):
    def __init__(self,id,owner_name,dish_name,price) :
        self.id=id
        self.owner_name=owner_name
        self.dish_name=dish_name
        self.price=price
    def getJSONString(self):
        return super().getJSONString()

class OrderParser(Order):
    def __init__(self, json_string):
       
        if  isinstance(json_string,str):
            _dict_=json.loads(json_string)
            super().__init__(**_dict_)   
        elif isinstance(json_string,dict):
            super().__init__(**json_string)
    
    def getDish(self):
        return Order(self.id,self.owner_name,self.dish_name,self.price)



    

dis=Order("1231","dinh","com",100)

jsonstring=dis.getJSONString()
print(jsonstring)

json_loaded=json.loads(jsonstring)
t=type(json_loaded)
print(t)
newt=Order(*json_loaded)
# print(DishParser(jsonstring).getJSON())

