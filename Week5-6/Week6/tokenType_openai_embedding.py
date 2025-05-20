# -*- coding: utf-8 -*-
"""
Created on Tue May 20 09:32:34 2025

@author: alice
"""

# Built-in and external modules

import os             # For accessing environment variables and file paths
import csv            # To write and read CSV files
from openai import OpenAI          # To connect to OpenAI's embedding API
from neo4j import GraphDatabase    # To connect and query the Neo4j graph database
from dotenv import load_dotenv     #To load sensitive config values from a .env file

#Load environment variables from a specific .env file
load_dotenv(dotenv_path="C:/Users/alice/OneDrive/Masaüstü/LangChainIntrudiction/neo4j.env")


# Get the OpenAI API key from environment
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

def get_tokentype_exampleUsecase(limit=None):
    """
   Connects to Neo4j and retrieves token types and their example use cases.
   Returns a list of tokenType dictionaries.
   """
   
   #Connect to Neo4j using URI, username and password from .env
    driver = GraphDatabase.driver(
        os.getenv('NEO4J_URI'),
        auth=(os.getenv('NEO4J_USERNAME'), os.getenv('NEO4J_PASSWORD'))
    )
    # Confirm connectivity to Neo4j

    driver.verify_connectivity()
    
    
    # Cypher query to get token types with example use cases
    query = """MATCH (tt:TokenType) WHERE tt.exampleUsecase IS NOT NULL
    RETURN tt.tokenTypeId AS tokenTypeId, tt.tokenType AS tokenType, tt.exampleUsecase AS exampleUsecase"""

    if limit is not None:
        query += f' LIMIT {limit}'
    
    
    #Run the query
    tokentypes, summary, keys = driver.execute_query(query)
    
    #Close the connection after query
    driver.close()

    return tokentypes

def generate_embeddings(file_name, limit=None):
    """
  Generates OpenAI embeddings for token use cases from Neo4j,
  and saves the result to a CSV file.
  """
    # 📁 Open the output CSV file
    csvfile_out = open(file_name, 'w', encoding='utf8', newline='')
    fieldnames = ['tokenTypeId','embedding']
    output = csv.DictWriter(csvfile_out, fieldnames=fieldnames)
    output.writeheader()
    
    # Retrieve data from Neo4j
    tokentypes = get_tokentype_exampleUsecase(limit=limit)

    print(len(tokentypes))
    
    # Initialize the OpenAI client
    llm = OpenAI()

    for tokentype in tokentypes:
        print(tokentype['tokenType'])
        
        # Combine token type and example use case for embedding input
        exampleUsecase = f"{tokentype['tokenType']}: {tokentype['exampleUsecase']}"
        
        # Send request to OpenAI Embeddings API
        response = llm.embeddings.create(
            input=exampleUsecase,
            model='text-embedding-ada-002'
        )
        
        # Write the result to CSV
        output.writerow({
            'tokenTypeId': tokentype['tokenTypeId'],
            'embedding': response.data[0].embedding
        })
    #Close the file
    csvfile_out.close()
    
# Run the function to generate embeddings and save to CSV
generate_embeddings(r'.\data\tokenType-exampleUsecase-embeddings.csv')