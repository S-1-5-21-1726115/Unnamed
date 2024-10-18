import platform
import requests
import json
import subprocess
import sys
import socket
import webbrowser
import random
import re
import hashlib

#ChatGPT说注释要专业，但是...呵呵，我这个注释可不是给你们用来方便看代码的
#↓以下为我的现状
#我焯！我爸硬是要我说出我在干什么，我真的想阐述它的梦
#并且结合它之前的逆天行为
#我只想说:你离网上所说的“逆天家长”不远了
#我爸又说"不打不成材"了，笑死我了
#我为我有这样的浮木感到耻辱
#为什么包括我妈呢?因为我妈更nb
#↑以上为我的现状

class NetworkError(Exception):
    """
    网络异常:)
    """
    errno:str

class FileOperationsException(Exception):
    """
    文件读取/写入错误（（
    """
    errno:str

def get_system():
    """
    判断当前系统
    只对Windows进行详细判断
    因为Windows不同版本之间的变化太大了(除了Windows 10和Windows 11)
    给Minecraft填的参数((
    不是Windows那Libriries之间的分割就用";"否则就用":"
    """
    system=platform.system()
    if system=="Windows":
        version=int(platform.win32_ver()[1].split(".")[2])
        if version>20348:
            return ("Windows 11 Build {}".format(platform.win32_ver()[1].lstrip("10.0")),10.0)
        elif version>9600:
            return ("Windows 10 Build {}".format(platform.win32_ver()[1].lstrip("10.0")),10.0)
        elif version>9200:
            return ("Windows 8.1 Build {}".format(platform.win32_ver()[1].lstrip("6.3")),6.3)
        elif version>7601:
            return ("Windows 8 Build {}".format(platform.win32_ver()[1].lstrip("6.2")),6.2)
        elif version>6002:
            return ("Windows 7 Build {}".format(platform.win32_ver()[1].lstrip("6.1")),6.1)
        elif version>2600:
            return ("Windows Vista Build {}".format(platform.win32_ver()[1].lstrip("6.1")),6.0)
        elif version>2195:
            return ("Windows XP/Whither",5.1)
        else:
            return ("Windows 2000-",5.0)
    elif system=="Linux":
        return ("Linux")

    elif system=="Darwin":
        return ("MacOS")
    
    else:
        return ("Unknown System")

def get_UserInfo():
    """
    获取玩家的UUID和账户名(获取AccessToken在另一个函数里)
    将返回一个元组
    第一项是UUID
    第二项是账户名
    第三项是AccessToken
    """
    Token=Get_Minecraft_AccessToken()
    RawData=json.loads(HttpGet("https://api.minecraftservices.com/minecraft/profile",{"Authorization":"Bearer {}".format(Token)}))
    Username=RawData["name"]
    UUID=RawData["id"]
    return (UUID,Username,Token)

def OAuth():
    """
    OAuth流程
    将返回获取的授权码
    (艹什么Tcp=Http)
    """
    UrI=CreateUrI("78914bdb-de6d-4d65-9d88-5f4f9d357db4","http://127.0.0.1:1145","XboxLive.signin"+"%20"+"offline_access")
    webbrowser.open(UrI)
    sk=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sk.bind(("127.0.0.1",1145))
    sk.listen()
    while True:
        Connect,Addres=sk.accept()
        while True:
            RawData=Connect.recv(2147483647).decode("utf-8")
            if RawData:
                break
        if RawData:
            break
    
    Code=re.findall(".*?/?code=(.*?).*?",RawData,re.S)[0]
    Linebreak="\r\n"
    Headers="HTTP/1.1 200 OK"+Linebreak+\
            "Content-Type: text/html; charset=utf-8"+Linebreak*2
    Html="""
    <html>
        <head>
            <title>已成功授权 - Simple Minecraft Launcher</title>
        </head>
        <body>
            <p>Fuck!这个页面丑死了!还tm不能显示巨硬特有的操作成功完成页面!tmd!到底新版验证怎么搞啊!!!</p>
        </body>
    </html>
    """
    Response=Headers+Html
    Connect.sendall(Response.encode("utf-8"))
    Connect.close()
    sk.close()
    return Code

def AccessCodeToAccessToken_Oauth():
    """
    通过在QAuth流程获取的授权获取授权令牌
    将返回一个元组
    第一个值是用于Xbox_live身份验证的令牌
    另一个是用于刷新Xbox_live身份验证的令牌的令牌
    """
    Code=OAuth()
    Data={"client_id":"78914bdb-de6d-4d65-9d88-5f4f9d357db4","code":Code,"grant_type":"authorization_code","redirect_uri":"http://127.0.0.1:1145","scope":"XboxLive.signin offline_access"}
    RawData=json.loads(HttpPost("https://login.microsoftonline.com/consumers/oauth2/v2.0/token",Data,{"Content-Type":"application/x-www-form-urlencoded"}))
    Token=(RawData["access_token"],RawData["refresh_token"])
    return Token

def Xbox_Live_Access():
    """
    Xbox_Live身份验证
    将返回一个元组
    第一个元组是Xbox_Live令牌
    第二个是Uhs
    """
    Login_Xbox_Token=AccessCodeToAccessToken_Oauth()[0]
    Data=json.dumps({"Properties":{"AuthMethod":"RPS","SiteName":"user.auth.xboxlive.com","RpsTicket":"d={}".format(Login_Xbox_Token)},"RelyingParty": "http://auth.xboxlive.com","TokenType": "JWT"})
    RawData=json.loads(HttpPost("https://user.auth.xboxlive.com/user/authenticate",Data,{"Content-Type":"application/json","Accept":"application/json"}))
    Token=RawData["Token"]
    Uhs=RawData["DisplayClaims"]["xui"][0]["uhs"]
    return (Token,Uhs)

def Xsts_Access():
    """
    Xsts身份验证
    将返回一个元组
    第一个是Uhs
    第二个是Xsts令牌
    """
    XboxToken_and_Uhs=Xbox_Live_Access()
    Data=json.dumps({"Properties": {"SandboxId": "RETAIL","UserTokens": [XboxToken_and_Uhs[0]]},"RelyingParty": "rp://api.minecraftservices.com/","TokenType": "JWT"})
    RawData=json.loads(HttpPost("https://xsts.auth.xboxlive.com/xsts/authorize",Data,{"Content-Type":"application/json","Accept":"application/json"}))
    Xsts_Token=RawData["Token"]
    return (XboxToken_and_Uhs[1],Xsts_Token)

def Get_Minecraft_AccessToken():
    """
    获取Minecraft访问令牌
    对了,我觉得我还要在启动之前检查玩家是否购买了Minecraft
    """
    Xststoken_and_Uhs=Xsts_Access()
    Data=json.dumps({"identityToken": "XBL3.0 x={};{}".format(Xststoken_and_Uhs[0],Xststoken_and_Uhs[1])})
    RawData=json.loads(HttpPost("https://api.minecraftservices.com/authentication/login_with_xbox",Data,{}))
    Access_Token=RawData["access_token"]
    return Access_Token


def launch(System,RAM,AccessToken,Username,UUID,LaunchVersion,Usertype,AssetsIndex,Gamedir,AssetsDir,WindowWidth,WindowHeight,PathSplit,VersionType):
    """
    "Minecraft,启动!"
    Minecraft的启动函数
    要传10个参数
    分别是:
    1.系统类型(例如Windows 10)
    2.要分配的内存,整数,最好不超过物理内存的一半
    3.Minecraft账户的AccessToken,此值应定时更新
    4.Minecraft账户的档案名
    5.Minecraft账户的UUID
    6.要启动的版本,为版本文件夹名称,且.jar和.json都是版本文件夹的名称
    7.账户类型,可以是mojang,msa或legacy
    8.资源文件索引,比如17
    9.游戏目录,即".minecraft"文件夹
    10.资源文件目录,即".minecraft\\assets"文件夹
    11.游戏窗口宽度
    12.游戏窗口高度
    13.路径分隔符(BYD就你Windows搞特殊是吧)
    14.版本类型,会显示在游戏主界面的左下角(会显示成Minecraft 24w35a/snapshot这样)
    """
    VersionInfo:dict=json.loads(open(Gamedir+PathSplit[1]+"versions"+PathSplit[1]+LaunchVersion+PathSplit[1]+LaunchVersion+".json","r").read())
    Libraries=VersionInfo["libraries"]
    Client_Download_Link=VersionInfo["downloads"]["client"]
    Need_Java_Version=Libraries["javaVersion"]["majorVersion"]
    AssetIndex=VersionInfo["assetIndex"]
    MainClass=VersionInfo["mainClass"]
    DownloadFile(Client_Download_Link,Gamedir+PathSplit[1]+"versions"+PathSplit[1]+LaunchVersion+PathSplit[1]+LaunchVersion+".jar")
    ClassPath=[]
    for Library in Libraries:
        LibraryPath=Gamedir+PathSplit[1]+"libraries"+PathSplit[1]+Library["artifact"]["path"].replace("/",PathSplit[1])
        DownloadFile(Library["artifact"],LibraryPath)
        if not Library.get("rules"):
            ClassPath.append(LibraryPath)
        else:
            OS:str=Library["rules"][0]["os"]["name"]
            OS.title()
            if OS in System:
                ClassPath.append(LibraryPath)
    
    ClassPath.append(Gamedir+PathSplit[1]+"versions"+PathSplit[1]+LaunchVersion+PathSplit[1]+LaunchVersion+".jar")
    ClassPath.append(MainClass)
    Java="javaw.exe"
    MainClass=VersionInfo["mainClass"]
    Game_Args=" ".join(["--username",Username,"--version",LaunchVersion,"--gameDir",Gamedir,"--assetsDir",AssetsDir,"--assetIndex",AssetsIndex,"--uuid",UUID,"--accessToken",AccessToken,"--clientid","${clientid}","--xuid","${xuid}","--userType",Usertype,"--versionType",VersionType,"--width",WindowWidth,"--height",WindowHeight,"-Xmx{}m".format(RAM),"-Xmn{}m".format(RAM/2),"-cp"])
    cp=PathSplit[0].join(ClassPath)
    Command=Java+" "+Game_Args+" "+cp
    Process=subprocess.Popen(Command,stdout=subprocess.PIPE,stderr=subprocess.PIPE)



def HttpPost(UrI,Post,Headers):
    """
    核心模块之一
    封装了requests.post类
    Post请求
    """
    Object=requests.post(UrI,data=Post,headers=Headers)
    if Object.status_code==200:
        return Object.content
    else:
        raise NetworkError("网络异常")

def HttpGet(UrI,Headers):
    """
    同样是核心模块之一
    封装了requests.get类
    Get请求
    """
    Object=requests.get(UrI,headers=Headers)
    if Object.status_code==200:
        return Object.content
    else:
        raise NetworkError("网络异常")

def DownloadFile(Data,FilePath):
    """
    还 是 核 心 模 块
    下载Minecraft用的
    还是封装的requests.get
    只不过是二进制文本
    ......吗?不止oh~
    """
    Url=Data["url"]
    Size=Data["size"]
    Object=requests.get(Url)
    FileData=Object.content
    Sha1=Data["sha1"]
    if Object.status_code==200:
        if len(FileData)==Size:
            if hashlib.sha1(FileData).hexdigest()==Sha1:
                try:
                    File=open(FilePath,"wb+")
                    File.write(FileData)
                    File.close()
                except WindowsError:
                    raise FileOperationsException("无法访问/读取文件")
            else:
                raise NetworkError("文件校验错误...")
        else:
            raise NetworkError("文件下载错误...大小错误,本应为大小为{}bytes的文件下载下来后的大小却是{}bytes".format(Size,len(FileData)))
        return "OK"
    else:
        raise NetworkError("网络异常")

def CreateUrI(client_id,redirect_uri,scope):
    """
    也是核心模块之一
    用于创建OAuth在浏览器内完成的链接
    """
    UrI="https://login.microsoftonline.com/consumers/oauth2/v2.0/authorize?client_id={}&response_type=code&redirect_uri={}&scope={}".format(client_id,redirect_uri,scope)
    return UrI

def offline_login(UserName):
    """
    如果你没有正版时可使用离线登录
    至少能启动对吧((
    """
    AccessToken=random.randint(0x100000000000,0xFFFFFFFFFFFF)
    UUID=random.randint(0x1000000000000000000000000000,0xFFFFFFFFFFFFFFFFFFFFFFFFFFFF)
    UserName=UserName
    return (UUID,UserName,AccessToken)

def main():
    """
    但是主函数还是要写的
    还没写完，正在写((
    """
    system=get_system()
    if system[0]=="Unknown System":
        print("不支持的系统!别告诉我你还在用Unix")
        sys.exit(2147549183)
    elif system[1]==5.0:
        print("我超!你居然还在用这么老的系统!升级一下吧...")
        sys.exit(2147549183)
    else:
        pass
    
    UserInfo=("","","")

    SignInThemod=input("请选择你的登录方式:\n1.离线登录请输入OF\n2.正版登录请输入GE\n")
    if SignInThemod=="OF":
        UserName=input("请输入用户名:\n")
        UserInfo=offline_login(UserName)
    elif SignInThemod=="GE":
        print("请在浏览器操作,将会在操作成功以后输出用户名和UUID")
        UserInfo=get_UserInfo()
        print("用户名:{}\nUUID:{}".format(UserInfo[1],UserInfo[0]))
        print("欢迎!")
    
    
    Path_split=(";","\\") if "Windows" in system[0] else (":","/")
    Versions=json.loads(HttpGet("https://piston-meta.mojang.com/mc/game/version_manifest.json",{}))
    print("最新正式版:{}".format(Versions["latest"]["release"]))
    print("最新快照/预发布/发布候选版:".format(Versions["latest"]["snapshot"] if Versions["latest"]["snapshot"]==Versions["latest"]["release"] else "也是"+Versions["latest"]["release"]))
    ReleaseVersions=[]
    SnapshotVersions=[]
    OldVersions=[]
    for Version in Versions["versions"]:
        if Version["type"]=="snapshot":
            SnapshotVersions.append({Version["id"]:Version["url"]})
        elif Version["type"]=="release":
            ReleaseVersions.append({Version["id"]:Version["url"]})
        else:
            OldVersions.append({Version["id"]:Version["url"]})
    while True:
        VersionType=input("你想要下载的版本的类型是什么?低于1.0的都是远古版本,所有非正式版都是快照版/n")
        if VersionType=="远古版本":
            print("目前可用的远古版本:")
            for OldVersion in OldVersions:
                VersionName=list(OldVersion.keys())[0]
                print(VersionName)
        elif VersionType=="正式版":
            print("目前可用的正式版:")
            for ReleaseVersion in ReleaseVersions:
                VersionName=list(ReleaseVersion.keys())[0]
                print(VersionName)
