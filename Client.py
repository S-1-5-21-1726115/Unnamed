# -*- coding: utf-8 -*-
#连客户端都是完全违反Python标准命名法的垃圾代码（
#甚至是面向结果编程

import hashlib
import base64
import socket
import os
from PackInt import *
from tkinter import *
from tkinter.filedialog import *

def Encode_Password(Password:str) -> str:
    return hashlib.sha256((hashlib.sha256(base64.b64encode(Password.encode("utf-8"))).hexdigest()).encode("utf-8")).hexdigest()

def Recv_Byte(Socket_Object:socket.socket) -> bytes:
    Length=Unpack_int(Socket_Object.recv(16))
    return Socket_Object.recv(Length)

def Send_String(Socket_Object:socket.socket,String:str) -> None:
    Byte=String.encode("utf-8")
    Length=Pack_int(len(Byte))
    Socket_Object.send(Length)
    Socket_Object.send(Byte)

def UpLoadFile(Socket_Object:socket.socket,UUID:str) -> None:
    """
    向服务端发送文件
    """
    Path="\\"+UUID+"\\"+Recv_Byte(Socket_Object).decode("utf-8")
    FullPath=os.path.abspath(Path)
    with open(FullPath,"rb") as Fp:
        Size=Pack_int(os.path.getsize(FullPath))
        Socket_Object.send(Pack_int(Size))
        State=0
        while True:
            Data=Fp.read(1024)
            if not Data:
                break
            TempSize=len(Data)
            Socket_Object.send(Pack_int(TempSize))
            Socket_Object.send(Data)
            State+=TempSize
            Display=State/Size*50
            print("\r"+"当前上传进度:"+"|"+"▬"*int(Display)+" "*(50-int(Display))+"|"+"%.1f" %(Display*2)+"%",end="")
        print("\r当前上传进度:|"+"▬"*100+"|100.0%",end="")
        print("\n上传完毕!")

def AcceptFile(Socket_Object:socket.socket) -> None:
    """
    接收服务端发送来的文件
    """
    MainWindow=Tk()
    MainWindow.withdraw()
    Path=asksaveasfilename(title="选择文件保存位置")
    State=0
    with open(Path,"wb") as Fp:
        Size=Recv_Byte(Socket_Object)
        while State<Size:
            TempSize=Unpack_int(Socket_Object.recv(16))
            Data=Socket_Object.recv(TempSize)
            Fp.write(Data)
            Size+=TempSize
            Display=State/Size*50
            print("\r"+"当前下载进度:"+"|"+"▬"*int(Display)+" "*(50-int(Display))+"|"+"%.1f" %(Display*2)+"%",end="")
        print("\r当前下载进度:|"+"▬"*50+"|100.0%",end="")
        print("\n下载完毕!")

def Accept(Socket_Obj:socket.socket) -> None:
    pass
