int128unsigned=16
int64unsigned=8
int32unsigned=4

def Pack_int(Int:int,Length:int=int128unsigned) -> bytes:
    # 将整数转换为二进制字符串并去掉'0b'前缀
    Bits=bin(Int).lstrip("0b")
    # 将长度不足的部分填充0，确保总长度为 Length * 8 位
    Bits=Bits.zfill(Length*8)
    # 每8位为一组，转换为十进制整数
    Packed_Int=[int(Bits[i:i+8],2) for i in range(0,Length*8,8)]
    # 返回字节串
    return bytes(Packed_Int)

def Unpack_int(Packed_Int:bytes) -> int:
    if not Packed_Int:
        return 0
    # 将每个字节转换为两位的十六进制字符串
    Bytes_List=[f'{byte:02x}' for byte in Packed_Int]
    # 将所有16进制字符串拼接，转换回整数
    Unpack_int = int("".join(Bytes_List),16)
    return Unpack_int
