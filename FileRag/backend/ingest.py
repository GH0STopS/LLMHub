import ast
import os
import shutil
import json
from pathlib import Path
import logging
from dotenv import load_dotenv
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import Language, RecursiveCharacterTextSplitter


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()


def extract_code_metadata(file_path : str):
    try:
        logger.info(f"extracting............")
        with open(file_path, 'r', encoding = 'utf-8') as f:
            content = f.read()
        tree = ast.parse(content)
        functions = []
        classes = []
        imports = []
        for node in ast.walk(tree):
            print(node)
            if isinstance(node, ast.FunctionDef):
                # functions.append({
                #     'name':node.name,
                #     'line':node.lineno,
                #     'args':[arg.arg for arg in node.args.args],
                #     'decorators':[d.id if isinstance(d, ast.Name) else 'decorator' for d in node.decorator_list]
                # })
                functions.append(node.name)

            elif isinstance(node, ast.ClassDef):
                # methods = [n.name for n in node if isinstance(n, ast.FunctionDef)]
                # classes.append({
                #     'name': node.name,
                #     'line':node.lineno,
                #     'methods':methods,
                #     'bases':[b.id if isinstance(b, ast.Name) else 'base' for b in node.bases]
                # })
                classes.append(node.name)
            elif isinstance(node, ast.Import):
                imports.extend([a.name for a in node.names])
            elif isinstance(node, ast.ImportFrom):
                imports.append(f"from {node.module}")
        # logger.info("got out..............")
            metadata = {
                'file_path':str(file_path),
                'file_name':os.path.basename(file_path),
                'functions':', '.join(functions),
                'classes':', '.join(classes),
                'imports':', '.join(imports),
                'line_count':len(content.split('\n'))
            }
            
        return metadata, content
    except Exception as e:
        logger.error(f"error : {file_path}: {e}")
        return None, None
    
def ingest_codebase(
        file_path: str,
        persist_db: str = './code_vectordb'
):
    documents = []
    all_metadata = []
    metadata, content = extract_code_metadata(file_path)

    print("----------here---------")

    if metadata and content:
        print("------got it------")
        all_metadata.append(metadata)
        e_content = f"""
File: {metadata['file_name']}
Path: {metadata['file_path']}
Lines: {metadata['line_count']}

Functions: {metadata['functions']}
Classes: {metadata['classes']}
Imports: {metadata['imports'][:10]}

CODE:
{content}
"""

        documents.append({
            'content':e_content,
            'metadata':metadata
        })

    python_splitter = RecursiveCharacterTextSplitter.from_language(
        language=Language.PYTHON,
        chunk_size = 2000,
        chunk_overlap = 400
    )

    texts = []
    metadatas = []
    print(f"---------{len(documents)}")
    for doc in documents:
        chunks = python_splitter.split_text(doc['content'])

        for chunk in chunks:
            texts.append(chunk)
            metadatas.append(doc['metadata'])
    
    logger.info(f"created {len(texts)}")

    embedding = OllamaEmbeddings(model="all-minilm:latest")

    if os.path.exists(persist_db):
        
        shutil.rmtree(persist_db)
    
    batch_size = 5
    vectordb = None

    for i in range(0, len(texts), batch_size):
        batch_text = texts[i:i+batch_size]
        batch_metas = metadatas[i:i+batch_size]

        print(f"-------------in for loop")

        if vectordb is None:
            logger.info(f"vector db is none")
            vectordb = Chroma.from_texts(
                texts=batch_text,
                embedding=embedding,
                metadatas=batch_metas,
                persist_directory=persist_db,
            )
        else:
            logger.info(f"vector db is not none")
            # logger.info(f"meta? {batch_metas}")
            vectordb.add_texts(texts=batch_text, metadatas=batch_metas)
    # logger.info(f"vector: {vectordb._collection.count()}")

    metadata_file = os.path.join(persist_db, 'code_metadata.json')
    with open(metadata_file, 'w') as f:
        json.dump(all_metadata, f, indent=2)
    
    logger.info(f"meta saved: {metadata_file}")