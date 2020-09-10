#!/usr/bin/env python

from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import sys
import time
from datetime import datetime
from ctypes import cdll
import copy
import gzip
import json
import codecs
import os
import shutil
import pickle
import random
import subprocess
from multiprocessing import Process, Queue

import game
import stateconverter


BASEPATH = "/dev/shm/ropship"
NROUNDS = 1000
AITIME = 0.1


def dump_states(states):
    def serialize(obj):
        if type(obj) == bytes:
            return codecs.decode(obj)
        return obj.__dict__

    print("="*3, datetime.now(), "dumping states")
    gzip.compress(json.dumps(states, default=serialize,separators=(',', ':')).encode("utf-8"))
    with open(os.path.join(BASEPATH, "states_tmp"), "wb") as fp:
        fp.write(gzip.compress(json.dumps(states, default=serialize,separators=(',', ':')).encode("utf-8")))
    shutil.move(os.path.join(BASEPATH, "states_tmp"), os.path.join(BASEPATH, "states"))


def run(teams_with_ais, gamentick, generation=0, visualize=False, defcon_ids_list=None, save_states=True):
    def parallel_aistate(defcon_id):
        cdll['libc.so.6'].prctl(1, 9)

        if state.teams_by_defcon_id[defcon_id].ship == None:
            res = (defcon_id, None)
        else:
            res = (defcon_id, stateconverter.state_to_nnstate(state, defcon_id))
        queue.put(res)

    def parallel_getmove(defcon_id, aistate):
        cdll['libc.so.6'].prctl(1, 9)
        if aistate == None:
            move = b"n"
            queue.put((defcon_id, move))
            return
        else:
            input_path = os.path.join(BASEPATH,"inputs/")
            input_fname = os.path.join(input_path, "team%d"%defcon_id)
            state_fname = os.path.join(BASEPATH,"round_state_"+str(defcon_id))
            if not os.path.exists(input_fname):
                move = b"n"
                queue.put((defcon_id, move))
                return
            if os.stat(input_fname).st_size==0:
                move = b"n"
                queue.put((defcon_id, move))
                return

            stateconverter.serialize(aistate, state_fname)
            aslr = 0x3e000000 + (random.randrange(0, 256) * 0x10000)
            p = subprocess.Popen(["./stub", input_fname, state_fname, hex(aslr)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            time.sleep(AITIME)
            res = p.poll()
            if res==None:
                move = b"n"
            else:
                if res > 0 and res < 127:
                    if bytes([res]) in b"asrldun":
                        move = bytes([res])
                    else:
                        move = b"n"
                else:
                    move = b"n"
            p.kill()
            p.wait()


            queue.put((defcon_id, move))

    if visualize:
        import visualizer
        visualizer.init()

    defconround = generation

    states = []
    state = game.init(teams_with_ais, defconround, 1, gamentick, defcon_ids_list=defcon_ids_list)

    states.append(copy.deepcopy(state))
    while True:
        if state.tick%100 == 0: print("=", state.tick)

        if visualize:
            visualizer.show(state, None, gamentick)

        t1 = time.time()
        moves = {}

        processes = []
        queue = Queue()
        for defcon_id in state.teams_by_defcon_id.keys():
            p = Process(target=parallel_aistate, args=(defcon_id,))
            p.start()
            processes.append(p)
        aistates = {}
        for _ in range(len(state.teams_by_defcon_id)):
            defcon_id, aistate = queue.get()
            aistates[defcon_id] = aistate
        for p in processes:
            p.join()


        processes = []
        queue = Queue()
        for defcon_id in state.teams_by_defcon_id.keys():
            p = Process(target=parallel_getmove, args=(defcon_id, aistates[defcon_id]))
            p.start()
            processes.append(p)
        moves = {}
        for _ in range(len(state.teams_by_defcon_id)):
            defcon_id, move = queue.get()
            moves[state.teams_by_defcon_id[defcon_id].tid] = move
        for p in processes:
            p.join()

        state = game.next_state(state, moves)

        if save_states:
            states.append(copy.deepcopy(state))

        if state.tick >= gamentick-1:
            return states



def decode_dict(tstr):
    d = {}
    for kv in tstr.split(b"_"):
        k, v = kv.split(b"-")
        d[int(k)] = codecs.decode(codecs.decode(v, "hex"))
    return d


def encode_dict(d):
    assert all((type(k)==int and type(v)==str for k, v in d.items()))
    return b"_".join((codecs.encode(str(k))+b"-"+codecs.encode(codecs.encode(v), "hex") for k, v in d.items()))



def main(defconround, teams, nrounds):
    teams_with_ais = {}
    for i, t in teams.items():
        teams_with_ais[i] = (t, None)

    states = run(teams_with_ais, nrounds, generation=defconround)
    
    dump_states(states)


if __name__ == "__main__":
    cdll['libc.so.6'].prctl(1, 9)

    defconround = int(sys.argv[1])
    teams = decode_dict(sys.argv[2].encode(sys.getfilesystemencoding(), 'surrogateescape'))
    if len(sys.argv)>=4:
        nrounds = int(sys.argv[3])
    else:
        nrounds = NROUNDS


    print("="*10, "START", defconround, datetime.now())
    print(nrounds)
    print(repr(teams))
    main(defconround, teams, nrounds)
    print("="*10, "END", defconround, datetime.now())






