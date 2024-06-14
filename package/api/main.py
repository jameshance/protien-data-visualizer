import os
import json
from dotenv import load_dotenv
from typing import List
from models import protein_data
from fastapi import FastAPI, HTTPException
from protein import ProteinBase
from database import database, engine
import logging
from sqlalchemy import select, text
from contextlib import asynccontextmanager
from queryModel import QueryRequest, CHAT_GPT_SYSTEM_PROMPT, CHAT_GPT_FOLLOWUP_PROMPT
from util_functions import remove_control_characters, process_protein_data
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from lang_folder.agents import classify_input_string, get_ai_response_for_conversation, query_database
from fastapi.middleware.cors import CORSMiddleware



logging.basicConfig(level=logging.INFO)

# Load environment variables from .env file
load_dotenv()

# Retrieve OpenAI API key from environment variables
# openai.api_key = os.getenv('OPENAI_API_KEY')


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    yield
    await database.disconnect()

app = FastAPI(lifespan=lifespan)


# Define allowed origins
origins = ["*"]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Handle OPTIONS requests
@app.options("/{rest_of_path:path}")
async def options_handler(rest_of_path: str):
    return JSONResponse(status_code=200, headers={
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization"
    })

# Simple endpoint for testing
@app.get("/")
async def read_root():
    return {"message": "Hello World"}

@app.get("/proteins/{entry}", response_model=ProteinBase)
async def read_protein(entry: str):
    query = protein_data.select().where(protein_data.c.entry == entry)
    result = await database.fetch_one(query)
    if result is None:
        raise HTTPException(status_code=404, detail="Protein not found")

    result = dict(result)
    if isinstance(result['amino_acid_composition'], str):
        result['amino_acid_composition'] = json.loads(result['amino_acid_composition'])
    if isinstance(result['secondary_structure'], str):
        result['secondary_structure'] = json.loads(result['secondary_structure'])

    return result

@app.get("/get_protein_data/{entry}")
async def get_protein_data(entry: str):

    query = protein_data.select().where(protein_data.c.entry == entry)
    protein = await database.fetch_one(query)
    if not protein:
        raise HTTPException(status_code=404, detail="Protein not found")
    processed_data = process_protein_data(protein)
    return processed_data    

@app.post("/proteins/", response_model=ProteinBase)
async def create_protein(protein: ProteinBase):
    try:
        query = protein_data.insert().values(
            entry=protein.entry,
            length=protein.length,
            first_seen=str(protein.first_seen),
            last_seen=str(protein.last_seen),
            organism_id=protein.organism_id,
            protein_names=protein.protein_names,
            sequence=protein.sequence,
            pfam=protein.pfam,
            smart=protein.smart,
            amino_acid_composition=jsonable_encoder(protein.amino_acid_composition),
            avg_hydrophobicity=protein.avg_hydrophobicity,
            secondary_structure=jsonable_encoder(protein.secondary_structure)
        )
        last_record_id = await database.execute(query)
        return {**protein.dict(), "id": last_record_id}
    except Exception as e:
        logging.error(f"Error creating protein: {e}")
        raise HTTPException(status_code=400, detail="Error creating protein")

@app.get("/proteins/", response_model=List[ProteinBase])
async def list_proteins(skip: int = 0, limit: int = 10):
    query = select(
        protein_data.c.entry,
        protein_data.c.length,
        protein_data.c.first_seen,
        protein_data.c.last_seen,
        protein_data.c.sequence,
        protein_data.c.pfam,
        protein_data.c.smart,
        protein_data.c.avg_hydrophobicity,
    ).offset(skip).limit(limit)
    results = await database.fetch_all(query)
    response = []
    
    for result in results:
        result_dict = dict(result)
        response.append(result_dict)
    return response

@app.put("/proteins/{entry}")
async def update_protein(entry: str, protein: ProteinBase):
    # Step 1: Perform the update
    query = (
        protein_data.update()
        .where(protein_data.c.entry == entry)
        .values(
            length=protein.length,
            first_seen=str(protein.first_seen),
            last_seen=str(protein.last_seen),
            sequence=protein.sequence,
            pfam=protein.pfam,
            smart=protein.smart,
            amino_acid_composition=protein.amino_acid_composition,
            avg_hydrophobicity=protein.avg_hydrophobicity,
            secondary_structure=protein.secondary_structure
        )
    )
    result = await database.execute(query)
    
    # Check if any rows were affected
    if result == 0:
        raise HTTPException(status_code=404, detail="Protein not found")
    
    # Step 2: Retrieve the updated record
    select_query = protein_data.select().where(protein_data.c.entry == entry)
    updated_protein = await database.fetch_one(select_query)
    
    if not updated_protein:
        raise HTTPException(status_code=404, detail="Protein not found")
    
    return updated_protein

@app.delete("/proteins/{entry}", response_model=dict)
async def delete_protein(entry: str):
    query = protein_data.delete().where(protein_data.c.entry == entry)
    await database.execute(query)
    return {"message": "Protein deleted successfully"}


async def format_data_as_markdown2(data: list) -> str:
    """
    Format the query result data into markdown using OpenAI's API.
    
    :param data: The data to format.
    :return: A markdown-formatted string.
    """

    # def split_data(data, chunk_size=100):
    #     """ Split data into smaller chunks to avoid exceeding token limit. """
    #     for i in range(0, len(data), chunk_size):
    #         yield data[i:i + chunk_size]
    
    # for chunk in split_data(data):
    prompt = f"Given the following data '{data}', format it into a well-structured markdown format:\n\nReturn the response in markdown format."
    
    return ""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an assistant that formats data into markdown. You only return the final output, no fillers. You suggest a couple of queries that the user can ask next to the chatbot."},
                {"role": "user", "content": prompt}
            ]
        )
        content = response.choices[0].message['content']

        return content
        
    except Exception as e:
        raise Exception(f"Error in formatting data as markdown: {e}")
    
    

async def format_data_as_markdown(data: list, query: str) -> str:
    """
    Format the query result data into markdown using OpenAI's API.
    
    :param data: The data to format.
    :param query: The query that was used to generate the data.
    :return: A markdown-formatted string.
    """

    def split_data(data, chunk_size=100):
        """ Split data into smaller chunks to avoid exceeding token limit. """
        for i in range(0, len(data), chunk_size):
            yield data[i:i + chunk_size]
    
    markdown_parts = []
    return ""

    for chunk in split_data(data):
        prompt = f"Given the following data retrieved using the query '{query}', format it into a well-structured markdown format:\n\n{chunk}\n\nReturn the response in markdown format. Include the query below the result. Do not use ` backticks in the output"
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-16k-0613",
                messages=[
                    {"role": "system", "content": "You are an assistant that formats data into markdown. You only return the final output, no fillers."},
                    {"role": "user", "content": prompt}
                ]
            )
            content = response.choices[0].message['content']
            markdown_parts.append(content)
        except Exception as e:
            raise Exception(f"Error in formatting data as markdown: {e}")
    
    return "\n".join(markdown_parts)


@app.post("/query_followup/")
async def query_followup(query_request: QueryRequest):
    messages = [CHAT_GPT_FOLLOWUP_PROMPT] + query_request.context + [{"role": "user", "content": query_request.query}]
    
    return ""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages
        )
        content = response.choices[0].message['content']

        print("Initial response ", content)

        content = remove_control_characters(content)

        print("Removed control chars  ", content)

        # Parse the JSON response from the model
        response_json = json.loads(content)              

        follow_up_questions = response_json.get("follow_up_questions", [])

        print("Follow up questions: ", follow_up_questions)

        if not follow_up_questions:
            return {"follow_up_questions": [""]}

        return {"follow_up_questions": follow_up_questions} 

    except Exception as e:
        print(e)
        return {"follow_up_questions": [""]}


@app.post("/query/")
async def query_model(query_request: QueryRequest):
    print(f"Data coming in to query : {query_request}")

    # Pick the last conversation from the user
    length = len(query_request.context)
    lastEntry = query_request.context[length-1]
    userQuery = lastEntry['content']

    updatedContext =  query_request.context + [{"role": "user", "content": userQuery}]

    messages = [CHAT_GPT_SYSTEM_PROMPT] + updatedContext
    
    # Check if given input is query or a conversation
    classification = classify_input_string(userQuery)
    print(f"the user input is classified as {classification}")

    # If it is a normal question, then just pass it along to the conversation chain
    if classification == "conversation":
        print(f"updated context {updatedContext}")
        # Invoke the LLMChain to get the response
        result = get_ai_response_for_conversation(updatedContext)
        return {"response": result}
    else :
        result = query_database(userQuery)
        # Else pass it to the query generation chain
        return {"response": result}
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages
        )
        content = response.choices[0].message['content']

        print("Initial response ", content)

        content = remove_control_characters(content)

        print("Removed control chars  ", content)

        # Parse the JSON response from the model
        response_json = json.loads(content)              

        response_type = response_json.get("type")
        response_content = response_json.get("content")

        print("printing both ", response_json, response_content)

        if response_type == "query":
            # Execute the SQL query using raw SQL
            with engine.connect() as conn:
                result = conn.execute(text(response_content)).fetchall()
                print("query result ", result)
                print("get markdown result of query content")
                markdown_result = await format_data_as_markdown(result, response_content)
                return { "response": markdown_result}   
        else:
            print("get markdown result of response ")
            # markdown_result = await format_data_as_markdown2(response_content)
            return { "response": response_content}   


    except Exception as e:
        print(e)
        # raise HTTPException(status_code=500, detail=str(e))
        return {"response": "Error in forming output"}
    
