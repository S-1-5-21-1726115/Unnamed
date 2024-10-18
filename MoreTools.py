from typing import Iterable,Union
from random import randint,choice

class CycleList:
    def __init__(self,List:Union[list,tuple,str,bytes]):
        self.List=List
        self.List_Length=len(self.List)
        self.Index=-1  #从-1开始以便下次调用时能从0开始
    
    def __iter__(self):
        self.Index=-1
        return self

    def __next__(self):
        self.Index+=1
        if self.List_Length==0:  # 处理空列表的情况
            raise StopIteration("空列表")
        return self.List[self.Index%self.List_Length]

    def __getitem__(self,Index:int):
        return self.List[Index%self.List_Length]

    def __str__(self):
        return "↻"+str(self.List)+"∞"

def Get_Random_Chinese():
    HighByte=randint(0xB0,0xD7)
    LowByte=randint(0xA1,0xFE)
    Bytes=(HighByte<<8)|LowByte
    Str_Hex="{:04x}".format(Bytes)
    return bytes.fromhex(Str_Hex).decode("gb2312",errors="replace")

def Get_Random_String():
    String=""
    Symbols=list("{}_-+=[]|\\:;\"\'<>,.?/~!@#$%^&*()`")
    Length=randint(1,20)
    for i in range(Length):
        Char_Type=randint(1,5)
        if Char_Type==5:
            String+=Get_Random_Chinese()
        elif Char_Type==4:
            String+=choice(Symbols)
        elif Char_Type==3:
            String+=chr(randint(65,90))
        elif Char_Type==2:
            String+=chr(randint(97,122))
        else:
            String+=str(randint(0,9))
    return String

if __name__=="__main__":
    Test=CycleList([1,2,3,4,5,6,7,8,9,10])
    print(Test)
    print(Test[5],Test[13])
    Index=1
    for i in Test:
        print(i)
        Index+=1
        if Index==20:
            break
    
    for i in range(10):
        print(Get_Random_Chinese())

    print(Get_Random_String())
