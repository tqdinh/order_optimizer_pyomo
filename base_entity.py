import json
from json import JSONEncoder


class TmpEncoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

class BaseEntity(JSONEncoder):
    def default(self, o):
        return o.__dict__
    
    def getJSONString(self):
        return json.dumps(self, indent=4, cls=BaseEntity)
        

    def getJSONObject(self):
        
        return TmpEncoder().encode(self)

        