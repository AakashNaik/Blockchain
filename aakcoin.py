# -*- coding: utf-8 -*-
"""
Created on Sat Jun  4 14:42:36 2022

@author: Akash
"""

import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse



class BlockChain:
    
    def __init__(self):
        self.chain=[]
        self.createBlock(proof=1, previousHash='0')
        self.transactions = []
        self.nodes = set()
        
    def createBlock(self, proof, previousHash):
        block=  { 'index'         : len(self.chain)+1,
                  'timestamp'     : str(datetime.datetime.now()),
                  'proof'         : proof,
                  'previousHash'  : previousHash,
                  'transactions'  : self.transactions
                }
        self.transactions = []
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
    
    def addTransaction(self, sender, receiver, amount):
        self.transactions.append({'sender'   : sender,
                                  'receiver' : receiver,
                                  'amount'   : amount            
                                  })
        previousBlock = self.getPreviousBlock()
        return previousBlock['index'] + 1
    
    def addNode(self, address):
        parsedUrl = urlparse(address)
        self.nodes.add(parsedUrl.netloc)
    
    def replaceChain(self):
        network = self.nodes
        longestChain = None
        maxLength = len(self.chain)
        for node in network:
            response = requests.get(f'http://127.0.0.1:{node}/get_chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain  = response.json()['chain']
                if length > maxLength and self.isChainValid(chain):
                    maxLength    = length
                    longestChain = chain
        if longestChain:
            self.chain = longestChain
            return True
        return False 
app = Flask(__name__)

nodeAddress = str(uuid4()).replace('-','')
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
                      'previousHash'  : block['previousHash'],
                      'transaction'   : block['transactions']
                      }    
    
    return jsonify(response), 200

@app.route('/get_chain', methods=['GET'])
def getChain():
    response ={'chain'  : blockchain.chain,
               'length' : len(blockchain.chain) }
    return jsonify(response), 200

@app.route('/add_transaction', methods=['POST'])
def addTransaction():
    json = request.get_json()
    transaction_keys = ['sender','receiver','amount']
    if not all (key is json for key in transaction_keys):
        return 'Some elements of the transaction are missing', 400
    index = blockchain.addTransaction(sender = json['sender'], receiver = json['receiver'], amount = json['amount'])
    response = {'message': f'This transaction will be added to Block {index}'}
    
    return jsonify(response), 201

@app.route('/connect_node', methods=['POST'])
def connectNode():
    json  = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return "No Node", 400
    for node in nodes:
        blockchain.addNode(node)
    response = {'message':'All the nodes are now connected!',
                'total_nodes': list(blockchain.nodes)}
    return jsonify(response), 201

@app.route('/replace_chain', methods=['POST'])
def replaceChain():
    isChainReplaced = blockchain.replaceChain()
    if isChainReplaced:
        response = {'message': 'The nodes had different chains so the chains is replaced',
                    'new_chain': blockchain.chain
                    }
    else:
        response = {'message'   : 'All good, The chain is the longest one',
                    'new_chain' : blockchain.chain}
    return jsonify(response), 201
 
app.run(host = '0.0.0.0', port = 5000)