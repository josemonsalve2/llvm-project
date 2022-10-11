from EfaUtil import *
#====== Activation Class is the basic unit of each stage ======                
class Activation:
    def __init__(self, state, property):
        self.state= state
        self.property = property

    def printOut(self, level):
        printd("activation:", level)
        self.state.printOut(level)
        self.property.printOut(level)
        
#====== State's Property Class ======   
# [[p_type]] can be one of the following (see AsmMachConvt.GetVector() for detail): 
#   "NULL"
#   "flag_majority"
#   "flag_default"
#   "flag"
#   "common"
#   "default"
#   "majority"                                        
class Property:
    def __init__(self, p_type, p_value):
        self.p_type = p_type
        self.p_val = p_value

    def printOut(self, level):
        printd("p_type:"+str(self.p_type)+"     p_val:"+str(self.p_val), level)
