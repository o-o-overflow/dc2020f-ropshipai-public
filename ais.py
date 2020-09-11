
import random
import copy
from collections import OrderedDict

import math
import keras
from keras.models import Sequential
from keras.models import load_model
from keras.optimizers import SGD
from keras.layers import Dense, Activation
import numpy as np
import numpy

import stateconverter


class AI:
    
    def __init__(self):
        pass

    def get_moves(self, aistate):
        pass

    def state_to_aistate(self, state, defcon_id):
        return state

    def dump(self):
        return None


class NoMoveAI(AI):

    def __init__(self):
        pass

    def get_move(self, aistate):
        return b"n"

    def dump(self):
        return None



class RandomAI(AI):

    def __init__(self, moves = None):
        self.gmove = 0
        if moves == None:
            self.vmoves = [(b"n", 1/7.0), (b"u", 1/7.0), (b"l", 1/7.0), (b"r", 1/7.0), (b"d", 1/7.0), (b"s", 1/7.0), (b"a", 1/7.0)]
        else:
            if len(moves[0]) == 1:
                self.vmoves = [(move, 1/float(len(moves))) for move in moves]
            else:
                self.vmoves = moves


    def get_move(self, aistate):
        self.gmove+=1

        if len(self.vmoves) <= 1:
            return self.vmoves[0][0]

        scale_factor = sum([y for x,y in self.vmoves])
        rnd = random.random()
        cv1 = 0
        for move in self.vmoves:
            cv2 = cv1 + move[1]/scale_factor
            if rnd >= cv1 and rnd < cv2:
                return move[0]
            cv1 = cv2


    def dump(self):
        return None



import pygame
import sys
class ManulMovesAI(AI):

    def __init__(self):
        pass



    def get_move(self, aistate):
        for event in pygame.event.get():
            if event.type==pygame.QUIT or (event.type==pygame.KEYDOWN and event.key==ord('q')):
                print("Terminating...")
                pygame.quit()
                sys.exit(0)

        kp = pygame.key.get_pressed()
        if kp[pygame.K_a]:
            return b"a"
        if kp[pygame.K_s]:
            return b"s"
        if kp[pygame.K_LEFT]:
            return b"l"
        if kp[pygame.K_RIGHT]:
            return b"r"
        if kp[pygame.K_UP]:
            return b"u"
        if kp[pygame.K_DOWN]:
            return b"d"



    def state_to_aistate(self, state, defcon_id):
        aistate = stateconverter.state_to_nnstate(state, defcon_id)
        for k,v in aistate.items():
            print(k,v)
        print("===")
        return aistate

    def dump(self):
        pass


class NNAI1(AI):
    network = None
    input_layer_len = 40
    

    def __init__(self, weights=None):



        network = Sequential()


        #import IPython; IPython.embed();

        network.add(Dense(24, input_shape = (self.input_layer_len,) ) )
        network.add(Activation('relu'))
        network.add(Dense(12))
        network.add(Activation('relu'))
        network.add(Dense(7))
        network.add(Activation('softmax'))
        opt = keras.optimizers.SGD(nesterov=True,momentum=0.2)
        network.compile(loss='categorical_crossentropy',
                optimizer=opt,
                 metrics=['accuracy'])
        self.network = network

        if weights!=None:
            # some of these copies are unneccessary
            self.network.set_weights(copy.deepcopy(weights))


    def state_to_aistate(self, state, defcon_id):
        return stateconverter.state_to_nnstate(state, defcon_id)


    def get_move(self, aistate):
        vmoves = [b"n", b"u", b"l", b"r", b"d", b"s", b"a"]


        input_values = list(aistate.values()) + [1.0] * (self.input_layer_len - len(list(aistate)))
        #print(input_values)
        output_values = list(self.network.predict([input_values])[0])


        #import IPython; IPython.embed();

        return vmoves[output_values.index(max(output_values))]


    def dump(self):
        if self.network is not None:
            return copy.deepcopy(self.network.get_weights())
        else:
            return None

    def mutate(self, mutation_rate=0.1, mutation_strength=0.1):
        weights = self.network.get_weights()
        ttt = 0
        for i in range(0,len(weights),2):
            if weights[i] == numpy.float32: continue
            for j in range(len(weights[i])):
                if weights[i][j] == numpy.float32: continue
                for k in range(len(weights[i][j])):
                    ttt += 1
                    if random.random()>(1.0-mutation_rate):
                        weights[i][j][k] = max(min(weights[i][j][k] + (2*random.random()-1.0)*mutation_strength, 0.0), 1.0)
        self.network.set_weights(copy.deepcopy(weights))

    def __deepcopy__(self, memo):
        # it is impossible to copy keras stuff, and we don't want to
        return self


class NNAI2(AI):
    network = None
    input_layer_len = 40
    

    def __init__(self, weights_file=None, l1=24, l2=12, l3=7, weights=None):

        network = Sequential()
        #import IPython; IPython.embed();
        network.add(Dense(l1, input_shape = (self.input_layer_len,) ) )
        network.add(Activation('relu'))
        network.add(Dense(l2))
        network.add(Activation('relu'))
        network.add(Dense(5))
        network.add(Activation('softmax'))
        opt = keras.optimizers.SGD(nesterov=True,momentum=0.2)
        network.compile(loss='categorical_crossentropy', optimizer=opt, metrics=['accuracy'])
        #network.fit(x_np, y_np, epochs=32, batch_size=1024, validation_split=0.25, verbose=2)

        if weights != None:
            network.set_weights(weights)
        else:
            network.load_weights(weights_file)

        self.network = network

    def state_to_aistate(self, state, defcon_id):
        return stateconverter.state_to_nnstate(state, defcon_id)


    def get_move(self, aistate):
        vmoves = b"adrsu"

        input_values = list(aistate.values()) + [1.0] * (self.input_layer_len - len(list(aistate)))
        cc = self.network.predict_classes([input_values])[0]
        move = bytes((vmoves[cc],))

        return move


    def dump(self):
        if self.network is not None:
            return copy.deepcopy(self.network.get_weights())
        else:
            return None

    def mutate(self, mutation_rate=0.1, mutation_strength=0.1):
        weights = self.network.get_weights()
        ttt = 0
        for i in range(0,len(weights),2):
            if weights[i] == numpy.float32: continue
            for j in range(len(weights[i])):
                if weights[i][j] == numpy.float32: continue
                for k in range(len(weights[i][j])):
                    ttt += 1
                    if random.random()>(1.0-mutation_rate):
                        weights[i][j][k] = max(min(weights[i][j][k] + (2*random.random()-1.0)*mutation_strength, 0.0), 1.0)
        self.network.set_weights(copy.deepcopy(weights))

    def __deepcopy__(self, memo):
        # it is impossible to copy keras stuff, and we don't want to
        return self


class PythonAI(AI):
    network = None
    nsamples = 0
    samples = []
    

    def __init__(self, dumper = None):
        self.dumper = dumper

    def state_to_aistate(self, state, defcon_id):
        return stateconverter.state_to_nnstate(state, defcon_id)

    def get_move(self, aistate):
        ns = aistate
        out = self.get_move_int(ns)

        if self.dumper is not None:
            self.dumper.add_sample((list(ns.values()), out))

        return out

    def get_move_int(self, ns):
        vmoves = [b"n", b"u", b"l", b"r", b"d", b"s", b"a"]

        #print("===\n", len(ns), ns)

        # if there is a bullet near (regardless of the direction), we enable the shield (if available)
        if ns["bullets0d"] > 0.85 and ns["shield_available"] > 0.999:
            return b"s"

        if ns["attack_available"] < 0.999: # if we have already attacked and not attack available, we try to go outward
            # if we are alligned with the outside circle we go backward
            if ns["attack_available"] < 0.5 and abs(ns["ocirclel"]-ns["ocircler"]) < 0.2 and (ns["ocirclef"] < ns["ocircleb"]):
                return b"d"
            else:
                # otherwise we rotate left
                if ns["attack_available"] < 0.75:
                    return b"r"
                # but when the attack is almost available again we go forwards
                else: 
                    return b"u"

        # if a ship is near and it has not a shield
        if ns["ships0d"] > 0.8 and ns["ships0shield"] < 0.999:
            # if we are not alligned with rotate right
            if ns["ships0ca"] <=  0.995:
                return b"r"
            # if we are alligned we shoot
            else:
                #print("==============")
                return b"a"
        # if the nearest ship is too far
        else:
            # we aligned a bit
            if ns["ships0ca"] <=  0.8:
                return b"r"
            # and then we move forward
            else:
                # but we need to be careful not to get stuck on the outer circle
                if ns["ocirclef"] > 0.85 or ns["ships0d"] > 0.9: # we also do not want to get too close to someone
                    return b"r"
                else:
                    return b"u"

        return b"r"

        if self.dumper is not None:
            self.dumper.add_sample((list(ns.values()), out))

        return out

    def dump(self):
        return None

    def __deepcopy__(self, memo):
        # we do not want to copy things, because otherwise if we have the dumper enabled the memory consumption is huge
        if self.dumper is not None:
            return None
        else:
            return self

class PythonAI2(AI):
    network = None
    nsamples = 0
    samples = []
    

    def __init__(self, dumper = None):
        self.dumper = dumper

    def state_to_aistate(self, state, defcon_id):
        return stateconverter.state_to_nnstate(state, defcon_id)

    def get_move(self, aistate):
        ns = aistate
        out = self.get_move_int(ns)

        if self.dumper is not None:
            self.dumper.add_sample((list(ns.values()), out))

        return out

    def get_move_int(self, ns):
        vmoves = [b"n", b"u", b"l", b"r", b"d", b"s", b"a"]

        #print("===\n", len(ns), ns)
        if ns["ships0ca"] > 0.99:
            return b"a"

        if ns["attack_available"] < 0.99:
            return b"u"

        return b"r"

        if self.dumper is not None:
            self.dumper.add_sample((list(ns.values()), out))

        return out

    def dump(self):
        return None

    def __deepcopy__(self, memo):
        # we do not want to copy things, because otherwise if we have the dumper enabled the memory consumption is huge
        if self.dumper is not None:
            return None
        else:
            return self

