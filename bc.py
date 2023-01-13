import json
import hashlib
import time as tm
from uuid import uuid4
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel


class Blockchain():

    def __init__(self):
        """initial blockchain"""
        self.chain = []
        self.current_trxs = []
        self.New_Block(previous_hash = 1, proof = 100)

    def New_Block(self, proof, previous_hash = None):
        """Create a new block in blockchain"""
        date_and_time = tm.time()
        current_time  = tm.ctime(date_and_time)
        
        block = {
                'index' : len(self.chain) + 1,
                'timestamp': current_time,
                'trxs' : self.current_trxs,
                'proof': proof,
                'previous_hash' : previous_hash or self.Hash(self.chain[-1]),
        }

        self.current_trxs = []

        self.chain.append(block)
        return block
        
    def New_Trx(self, sender, recipient, amount):
        """Add a new transaction to the memory pool"""
        self.current_trxs.append(
        {
            'sender': sender, 
            'recipient': recipient,
            'amount' : amount
        }
        )

        return self.Last_Block['index'] + 1 


    @staticmethod
    def Hash(block):
        """Calculate hash a block"""
        block_string = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(block_string).hexdigest()


    @property
    def Last_Block(self):
        return self.chain[-1]


    @staticmethod
    def Valid_Proof(last_proof, proof):
        """check if this proof is ok or not"""
        this_proof = f'{proof}{last_proof}'.encode()
        this_proof_hash = hashlib.sha256(this_proof).hexdigest()
        return this_proof_hash[:5] == '00000'


    def Proof_Of_Work(self, last_proof):
        proof = 0
        while self.Valid_Proof(last_proof, proof) is False:
            proof += 1

        return proof



Node_Id = str(uuid4())


blockchain = Blockchain()


class Data_Trx(BaseModel):
    sender:str
    recipient:str
    amount:int


app = FastAPI()


@app.get('/mine')
def Mine():
    last_block = blockchain.Last_Block
    last_proof = last_block['proof']
    proof      = blockchain.Proof_Of_Work(last_proof)

    blockchain.New_Trx(sender = "0", recipient = Node_Id, amount = 50)
    
    previous_hash = blockchain.Hash(last_block)
    block = blockchain.New_Block(proof, previous_hash)

    result = {
        'message'       : 'New block created',
        'index'         :  block['index'],
        'trxs'          :  block['trxs'],
        'proof'         :  block['proof'],
        'previous_hash' : block['previous_hash'],
    }
    
    return jsonable_encoder(result)


@app.post('/trxs_new')
def New_Trx(values_trx:Data_Trx):
    """will add a new transaction"""
    this_block = blockchain.New_Trx(values_trx.sender, values_trx.recipient, values_trx.amount)
    response = {'message' : f'will be added to block {this_block}'}
    return jsonable_encoder(response)


@app.get('/chain')
def Full_Chain():
    """returns the full chain"""
    response = {
        'Chain' : blockchain.chain,
        'Length': len(blockchain.chain)
    }
    return jsonable_encoder(response)

