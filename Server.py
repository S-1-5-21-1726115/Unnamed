# -*- coding: utf-8 -*-
#完全违反Python标准命名法的垃圾代码（

import socket
import json
import os
from random import *
from logging import *
import time
import threading
from PackInt import *
from typing import *


# 在写主程序之前给你们看个笑话:

# I don't like QQ and WeChat also skype, because they are so Laggy.
# also they bother, such as Login.
# Telegram also bother.
# This is my make the this application(TPMessage)'s reason.

#以上是qq群里面的某个人发的图片里的代码里的注释,以下是我的锐评

# 我寻思着你登个录会死啊?
# 对了,他甚至用的Ursina的联机模块而不是Socket
# 真是笑死我了
# 甚至他是在qq群里面发的
#----------------------------
# 我的乐子老爸
# 不仅控制欲极强
# 还最爱混淆概念+打人
# 孔子不提倡的事情他最爱做
# 还说要打我妈
# 我一辩解就说我是在狡辩,还说我养成了什么怪习惯
# 语气还很凶
# 你无敌了
#----------------------------


os.makedirs("Logs\\",exist_ok=True)
Handler=FileHandler(filename="Logs\\Log_"+time.strftime("%Y-%m-%d-%H_%M_%S",time.localtime())+".log",encoding="utf-8")
basicConfig(handlers=[Handler],format="\"%(filename)s\",Line %(lineno)s [%(asctime)s][%(levelname)s]:%(message)s",datefmt="%Y/%m/%d %H:%M:%S",level=DEBUG)

UUIDList=[]
UserInfoDataBase=[]

def Recv_Byte(Socket_Object:socket.socket) -> bytes:
    Length=Unpack_int(Socket_Object.recv(16))
    return Socket_Object.recv(Length)

def Send_String(Socket_Object:socket.socket,String:str) -> None:
    Byte=String.encode("utf-8")
    Length=Pack_int(len(Byte))
    Socket_Object.send(Length)
    Socket_Object.send(Byte)

def Init() -> str:
    debug("正在初始化...")
    info("正在加载用户信息...")
    global UUIDList,UserInfoDataBase
    if os.path.exists(os.path.abspath("422ae1e3-5e62-828a-d278-5ecffa860978.dat")):
        with open("422ae1e3-5e62-828a-d278-5ecffa860978.dat","w+") as fp:
            UserInfoDataBase=json.load(fp)
    else:
        with open("422ae1e3-5e62-828a-d278-5ecffa860978.dat","w+") as fp:
            json.dump(UserInfoDataBase,fp,ensure_ascii=False)

    if os.path.exists(os.path.abspath("66097383-4ac5-18c3-eac6-79d1a9a1cba2.dat")):
        with open("66097383-4ac5-18c3-eac6-79d1a9a1cba2.dat","w+") as fp:
            UserInfoDataBase=json.load(fp)
    else:
        with open("66097383-4ac5-18c3-eac6-79d1a9a1cba2.dat","w+") as fp:
            json.dump(UserInfoDataBase,fp,ensure_ascii=False)
    
    info("加载完毕!")
    return "操作成功完成"

def CreateUUID() -> str:
    NewUUID=str(hex(randint(0x10000000,0xFFFFFFFF))).lstrip("0x")+"-"+str(hex(randint(0x1000,0xFFFF))).lstrip("0x")+"-"+str(hex(randint(0x1000,0xFFFF))).lstrip("0x")+"-"+str(hex(randint(0x1000,0xFFFF))).lstrip("0x")+"-"+str(hex(randint(0x100000000000,0xFFFFFFFFFFFF))).lstrip("0x")
    info("本次生成的UUID为:{}".format(NewUUID))
    return NewUUID

def RegistNewUser(Username:str,Password_Hash:str) -> int:
    info("注册新用户,用户名:{},加密后的密码:{}".format(Username,Password_Hash))
    global UserInfoDataBase
    UUID=CreateUUID()
    while UUID in UUIDList:
        UUID=CreateUUID()
    UUIDList.append(UUID)
    UserInfoDataBase.append({"Username":Username,"Password":Password_Hash,"UUID":UUID})
    with open("422ae1e3-5e62-828a-d278-5ecffa860978.dat","w+") as fp:
        json.dump(UserInfoDataBase,fp,ensure_ascii=False)
    
    with open("66097383-4ac5-18c3-eac6-79d1a9a1cba2.dat","w+") as fp:
        json.dump(UUIDList,fp,ensure_ascii=False)
    info("注册成功!")
    return 0

def LoginUser(Username:str,Password_Hash:str) -> str|int:
    for UserInfo in UserInfoDataBase:
        if UserInfo["Username"]==Username:
            info("用户名匹配,正在校验密码...")
            if UserInfo["Password"]==Password_Hash:
                info("密码校验成功!登录成功!欢迎{}登录!".format(Username))
                return UserInfo["UUID"]
            else:
                warning("用户{}登录失败:密码错误".format(Username))
                return -1

    else:
        error("错误:无法找到用户{},放弃本次登录操作".format(Username))
        return -2

def CreateUserFilePath(UUID:str) -> str:
    os.makedirs("UserData\\{}".format(UUID),exist_ok=True)
    debug("创建了目录{}".format(os.path.abspath("UserData\\{}".format(UUID))))

def Login(Socket_Object:socket.socket) -> None:
    Username=Recv_Byte(Socket_Object).decode("utf-8")
    Password_Hash=Recv_Byte(Socket_Object).decode("utf-8")
    UUID=LoginUser(Username,Password_Hash)
    if UUID==-1:
        Send_String(Socket_Object,"PasswdEr")
    elif UUID==-2:
        Send_String(Socket_Object,"NotFndUsr")
    else:
        CreateUserFilePath(UUID)
        Send_String(Socket_Object,"OK")
        return UUID

def Regist(Socket_Object:socket.socket) -> int:
    Username=Recv_Byte(Socket_Object).decode("utf-8")
    Password_Hash=Recv_Byte(Socket_Object).decode("utf-8")
    return RegistNewUser(Username,Password_Hash)

def Server(Socket_Object:socket.socket,Addr:tuple) -> None:
    try:
        while True:
            Command=Recv_Byte(Socket_Object)
            UserUUID=''
            if Command==b'Exit':
                Send_String(Socket_Object,"Closed")
                Socket_Object.close()
                info("已关闭该来自{}:{}的客户端的连接".format(Addr[0],Addr[1]))
                info("由{}:{}客户端启动的线程已退出".format(Addr[0],Addr[1]))
                return
            elif Command==b'Login':
                UserUUID=Login(Socket_Object)
            elif Command==b'Regist':
                Regist(Socket_Object)
            elif Command==b'Download':
                DownloadFile(Socket_Object,UserUUID)
            
    except Exception as E:
        exception(E)

def DownloadFile(Socket_Object:socket.socket,UUID:str) -> None:
    """
    向客户端传送文件
    """
    Path="\\"+UUID+"\\"+Recv_Byte(Socket_Object).decode("utf-8")
    FullPath=os.path.abspath(Path)
    info("正在向客户端传送以下文件:{}...".format(FullPath))
    with open(FullPath,"rb") as Fp:
        Socket_Object.send(Pack_int(os.path.getsize(FullPath)))
        while True:
            Data=Fp.read(1024)
            if not Data:
                break
            Socket_Object.send(Pack_int(len(Data)))
            Socket_Object.send(Data)

def AcceptFile(Socket_Object:socket.socket,UUID:str) -> None:
    """
    接收客户端发送来的文件
    """
    FileName=Recv_Byte(Socket_Object).decode("utf-8")
    Path="\\"+UUID+"\\"+FileName
    info("正在接收客户端发来的文件...文件名:{}".format(Path))
    State=0
    with open(Path,"wb") as Fp:
        Size=Unpack_int(Recv_Byte(Socket_Object))
        while State<Size:
            TempSize=Unpack_int(Socket_Object.recv(16))
            Data=Socket_Object.recv(TempSize)
            Fp.write(Data)
            Size+=TempSize

if __name__=="__main__":
    """
    主函数
    严格意义上来说,其实不能叫函数
    应该叫程序入口点()
    """
    Init()
    Server_Socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    Server_Socket.bind(("127.0.0.1",11451))
    info("成功绑定了端口11451")
    Server_Socket.listen(2147483647)
    while True:
        Client_Socket,Client_Addr=Server_Socket.accept()
        Mutil_Thread=threading.Thread(target=Server,args=(Client_Socket,Client_Addr))
        Mutil_Thread.start()
        info("为来自{}:{}的客户端启动了一个线程".format(Client_Addr[0],Client_Addr[1]))
