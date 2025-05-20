# -*- coding: utf-8 -*-
"""
Created on Tue May 20 09:32:34 2025

@author: alice
"""

import os
import csv

from openai import OpenAI
from neo4j import GraphDatabase

from dotenv import load_dotenv

load_dotenv(dotenv_path="C:/Users/alice/OneDrive/Masaüstü/LangChainIntrudiction/neo4j.env")




# Test için yazdıralım
print("URI:", os.getenv("NEO4J_URI"))
print("USERNAME:", os.getenv("NEO4J_USERNAME"))
print("PASSWORD:", os.getenv("NEO4J_PASSWORD"))


OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

def get_tokentype_exampleUsecase(limit=None):
    driver = GraphDatabase.driver(
        os.getenv('NEO4J_URI'),
        auth=(os.getenv('NEO4J_USERNAME'), os.getenv('NEO4J_PASSWORD'))
    )

    driver.verify_connectivity()

    query = """MATCH (tt:TokenType) WHERE tt.exampleUsecase IS NOT NULL
    RETURN tt.tokenTypeId AS tokenTypeId, tt.tokenType AS tokenType, tt.exampleUsecase AS exampleUsecase"""

    if limit is not None:
        query += f' LIMIT {limit}'

    tokentypes, summary, keys = driver.execute_query(
        query
    )

    driver.close()

    return tokentypes

def generate_embeddings(file_name, limit=None):

    csvfile_out = open(file_name, 'w', encoding='utf8', newline='')
    fieldnames = ['tokenTypeId','embedding']
    output = csv.DictWriter(csvfile_out, fieldnames=fieldnames)
    output.writeheader()

    tokentypes = get_tokentype_exampleUsecase(limit=limit)

    print(len(tokentypes))
    
    llm = OpenAI()

    for tokentype in tokentypes:
        print(tokentype['tokenType'])

        exampleUsecase = f"{tokentype['tokenType']}: {tokentype['exampleUsecase']}"
        response = llm.embeddings.create(
            input=exampleUsecase,
            model='text-embedding-ada-002'
        )

        output.writerow({
            'tokenTypeId': tokentype['tokenTypeId'],
            'embedding': response.data[0].embedding
        })

    csvfile_out.close()
    
generate_embeddings(r'.\data\tokenType-exampleUsecase-embeddings.csv')