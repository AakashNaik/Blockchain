# -*- coding: utf-8 -*-
"""
Created on Tue May 31 19:43:47 2022

@author: Akash
"""

import datetime
import hashlib
import json
from flask import Flask, jsonify


class BlockChain:
    
    def __init__(self):
        self.chain=[]
        self.createBlock(proof=1, previousHash='0')
        
    def createBlock(self, proof, previousHash):
        block=  { 'index'         : len(self.chain)+1,
                  'timestamp'     : str(datetime.datetime.now()),
                  'proof'         : proof,
                  'previousHash' : previousHash
                }
        
        self.chain.append(block)
        return block
    
    def getPreviousBlock(self):
        return self.chain[-1]
    
    def proofOfWork(self, previousProof):
        newProof   = 1
        checkProof = False
        
        while not checkProof:
            hashOperation = hashlib.sha256(str(newProof**3- previousProof**3).encode()).hexdigest()
            if hashOperation[:4] == '0000':
                checkProof= True
            else:
                newProof +=1
        return newProof
    
    def hash(self, block):
        encodedBlock = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(encodedBlock).hexdigest()
    
    def isChainValid( self , chain):
        previousBlock = chain[0]
        blockIndex = 1
        while blockIndex < len(chain):
            block = chain(blockIndex)
            
            if block['previousHash'] !=self.hash(previousBlock):
                return False
            
            previousProof = previousBlock['proof']
            proof = block['proof']
            hashOperation = hashlib.sha256(str(proof**3- previousProof**3).encode()).hexdigest()
            if hashOperation !='0000':
                return False
            previousBlock = block
            
            blockIndex +=1
            
        return True
    

app = Flask(__name__)

blockchain = BlockChain()

@app.route('/mine_block', methods=['GET'])
def mineBlock():
    previousBlock = blockchain.getPreviousBlock()
    previousProof = previousBlock['proof']
    proof         = blockchain.proofOfWork(previousProof)
    previousHash  = blockchain.hash(previousBlock)
    block         = blockchain.createBlock(proof, previousHash)
    response      = { 'message'       : 'You have mined a block!',
                      'index'         : block['index'],
                      'timestamp'     : block['timestamp'],
                      'proof'         : block['proof'],
                      'previousHash' : block['previousHash']
                      }    
    
    return jsonify(response), 200

@app.route('/get_chain', methods=['GET'])
def getChain():
    response ={'chain'  : blockchain.chain,
               'length' : len(blockchain.chain) }
    return jsonify(response), 200

app.run(host = '0.0.0.0', port = 5000)