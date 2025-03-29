"""
FastAPI implementation for the LlamaGraph REST API
"""
import os
import logging
import tempfile
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import json

# Check if FastAPI is available
try:
    from fastapi import FastAPI, HTTPException, Query, Body, File, UploadFile, BackgroundTasks
    from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel, Field
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False
    logging.warning("FastAPI not available. REST API server will not work.")
    # Create dummy classes for type checking
    class BaseModel: pass
    class FastAPI: pass
    class Field: pass

from llamagraph.config import LlamaGraphConfig
from llamagraph.utils.cache import Cache
from llamagraph.extractor.entity_extractor import EntityExtractor
from llamagraph.extractor.relation_extractor import RelationExtractor
from llamagraph.graph.knowledge_graph import KnowledgeGraph
from llamagraph.graph.query_engine import QueryEngine
from llamagraph.utils.visualization import (
    create_interactive_graph,
    create_3d_graph,
    create_knowledge_map
)

# Define Pydantic models for API requests/responses
class ProcessTextRequest(BaseModel):
    """Request model for processing text"""
    text: str = Field(..., description="Text to process")
    use_mlx: bool = Field(True, description="Whether to use MLX acceleration")
    num_threads: int = Field(4, description="Number of threads to use")

class QueryRequest(BaseModel):
    """Request model for querying a knowledge graph"""
    query: str = Field(..., description="Query to execute on the knowledge graph")

class Entity(BaseModel):
    """Entity model for API responses"""
    text: str
    entity_type: str
    occurrences: int
    mentions: List[str]

class Relation(BaseModel):
    """Relation model for API responses"""
    source: str
    relation_type: str
    target: str
    sentence: str

class KnowledgeGraphModel(BaseModel):
    """Knowledge graph model for API responses"""
    entities: List[Entity]
    relations: List[Relation]

class ProcessResponse(BaseModel):
    """Response model for processing text"""
    success: bool
    message: str
    knowledge_graph: Optional[KnowledgeGraphModel] = None
    graph_id: Optional[str] = None

class QueryResponse(BaseModel):
    """Response model for querying a knowledge graph"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

# Create the FastAPI app
app = FastAPI(
    title="LlamaGraph API",
    description="REST API for LlamaGraph knowledge graph processing",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for knowledge graphs
# In a production environment, this should be replaced with a proper database
knowledge_graphs = {}

@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with API documentation"""
    return """
    <html>
        <head>
            <title>LlamaGraph API</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; line-height: 1.6; }
                h1 { color: #2c3e50; }
                h2 { color: #3498db; margin-top: 30px; }
                code { background: #f8f8f8; padding: 2px 4px; border-radius: 4px; }
                pre { background: #f8f8f8; padding: 10px; border-radius: 4px; overflow-x: auto; }
                .endpoint { margin-bottom: 40px; border-bottom: 1px solid #eee; padding-bottom: 20px; }
                .method { display: inline-block; padding: 4px 8px; border-radius: 4px; color: white; font-weight: bold; }
                .get { background-color: #61affe; }
                .post { background-color: #49cc90; }
            </style>
        </head>
        <body>
            <h1>🦙 LlamaGraph API</h1>
            <p>Welcome to the LlamaGraph API. This API allows you to create and query knowledge graphs from text.</p>
            <p>For full API documentation, visit <a href="/docs">/docs</a>.</p>
            
            <h2>Key Endpoints</h2>
            
            <div class="endpoint">
                <h3><span class="method post">POST</span> /process</h3>
                <p>Process text to create a knowledge graph.</p>
                <pre>
{
  "text": "Apple was founded by Steve Jobs. Tim Cook is the current CEO of Apple.",
  "use_mlx": true,
  "num_threads": 4
}
                </pre>
            </div>
            
            <div class="endpoint">
                <h3><span class="method post">POST</span> /query/{graph_id}</h3>
                <p>Query an existing knowledge graph.</p>
                <pre>
{
  "query": "find Apple"
}
                </pre>
            </div>
            
            <div class="endpoint">
                <h3><span class="method get">GET</span> /graph/{graph_id}</h3>
                <p>Get a knowledge graph by ID.</p>
            </div>
            
            <div class="endpoint">
                <h3><span class="method get">GET</span> /visualize/{graph_id}</h3>
                <p>Get an interactive visualization of a knowledge graph.</p>
            </div>
            
            <h2>Example Usage</h2>
            <p>Using curl to process text:</p>
            <pre>
curl -X POST "http://localhost:8000/process" \\
     -H "Content-Type: application/json" \\
     -d '{"text": "Apple was founded by Steve Jobs. Tim Cook is the current CEO of Apple."}'
            </pre>
            
            <p>Using curl to query a graph:</p>
            <pre>
curl -X POST "http://localhost:8000/query/graph_1234" \\
     -H "Content-Type: application/json" \\
     -d '{"query": "find Apple"}'
            </pre>
        </body>
    </html>
    """

@app.post("/process", response_model=ProcessResponse)
async def process_text(request: ProcessTextRequest, background_tasks: BackgroundTasks):
    """
    Process text to extract entities and relations, and build a knowledge graph
    """
    try:
        # Initialize components
        config = LlamaGraphConfig()
        config.use_mlx = request.use_mlx
        config.num_threads = request.num_threads
        
        cache = Cache(config.cache_dir, config.max_size)
        entity_extractor = EntityExtractor(config, cache)
        relation_extractor = RelationExtractor(config, cache)
        kg = KnowledgeGraph()
        
        # Extract entities
        entities = entity_extractor.extract(request.text)
        
        # Extract relations
        relations = relation_extractor.extract(request.text, entities)
        
        # Build knowledge graph
        for entity in entities:
            kg.add_entity(entity)
        
        for relation in relations:
            kg.add_relation(relation)
        
        # Generate a unique ID for this graph
        import uuid
        graph_id = str(uuid.uuid4())
        
        # Store the knowledge graph
        knowledge_graphs[graph_id] = kg
        
        # Schedule a cleanup task to remove the graph after 1 hour
        background_tasks.add_task(cleanup_graph, graph_id, 3600)
        
        # Convert to API model
        kg_data = kg.to_dict()
        kg_model = KnowledgeGraphModel(
            entities=[Entity(**e) for e in kg_data["entities"]],
            relations=[Relation(**r) for r in kg_data["relations"]]
        )
        
        return ProcessResponse(
            success=True,
            message=f"Successfully processed text with {len(entities)} entities and {len(relations)} relations",
            knowledge_graph=kg_model,
            graph_id=graph_id
        )
    
    except Exception as e:
        logging.exception("Error processing text")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query/{graph_id}", response_model=QueryResponse)
async def query_graph(graph_id: str, request: QueryRequest):
    """
    Execute a query on a knowledge graph
    """
    # Check if the graph exists
    if graph_id not in knowledge_graphs:
        raise HTTPException(status_code=404, detail=f"Knowledge graph with ID {graph_id} not found")
    
    try:
        # Get the knowledge graph
        kg = knowledge_graphs[graph_id]
        
        # Create a query engine
        query_engine = QueryEngine(kg)
        
        # Execute the query
        result = query_engine.execute_query(request.query)
        
        # Return the result
        return QueryResponse(
            success=result["success"],
            message=result["message"],
            data=result["data"]
        )
    
    except Exception as e:
        logging.exception("Error querying graph")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/graph/{graph_id}")
async def get_graph(graph_id: str):
    """
    Get a knowledge graph by ID
    """
    # Check if the graph exists
    if graph_id not in knowledge_graphs:
        raise HTTPException(status_code=404, detail=f"Knowledge graph with ID {graph_id} not found")
    
    try:
        # Get the knowledge graph
        kg = knowledge_graphs[graph_id]
        
        # Convert to dict and return
        return kg.to_dict()
    
    except Exception as e:
        logging.exception("Error getting graph")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/visualize/{graph_id}")
async def visualize_graph(
    graph_id: str, 
    visualization_type: str = Query("interactive", description="Type of visualization: interactive, 3d, or map")
):
    """
    Get an interactive visualization of a knowledge graph
    """
    # Check if the graph exists
    if graph_id not in knowledge_graphs:
        raise HTTPException(status_code=404, detail=f"Knowledge graph with ID {graph_id} not found")
    
    try:
        # Get the knowledge graph
        kg = knowledge_graphs[graph_id]
        
        # Create a temporary file for the visualization
        fd, temp_path = tempfile.mkstemp(suffix=".html")
        os.close(fd)
        temp_file = Path(temp_path)
        
        # Create the visualization
        if visualization_type == "interactive":
            create_interactive_graph(
                kg.graph,
                title=f"Knowledge Graph {graph_id}",
                save_path=temp_file
            )
        elif visualization_type == "3d":
            create_3d_graph(
                kg.graph,
                title=f"3D Knowledge Graph {graph_id}",
                save_path=temp_file
            )
        elif visualization_type == "map":
            create_knowledge_map(
                kg.graph,
                title=f"Knowledge Map {graph_id}",
                save_path=temp_file
            )
        else:
            raise HTTPException(status_code=400, detail=f"Invalid visualization type: {visualization_type}")
        
        # Return the visualization file
        return FileResponse(
            temp_file,
            media_type="text/html",
            filename=f"llamagraph_{graph_id}_{visualization_type}.html"
        )
    
    except Exception as e:
        logging.exception("Error visualizing graph")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/export/{graph_id}")
async def export_graph(
    graph_id: str,
    format: str = Query("json", description="Export format: json, gexf, graphml, or cytoscape")
):
    """
    Export a knowledge graph in the specified format
    """
    # Check if the graph exists
    if graph_id not in knowledge_graphs:
        raise HTTPException(status_code=404, detail=f"Knowledge graph with ID {graph_id} not found")
    
    try:
        # Get the knowledge graph
        kg = knowledge_graphs[graph_id]
        
        # Create a temporary file for the export
        temp_dir = tempfile.mkdtemp()
        temp_base = Path(temp_dir) / "graph"
        
        # Import the export function
        from llamagraph.utils.visualization import export_graph_to_formats
        
        # Export the graph
        exports = export_graph_to_formats(
            kg.graph,
            temp_base,
            formats=[format]
        )
        
        # Check if the export was successful
        if format not in exports:
            raise HTTPException(status_code=400, detail=f"Failed to export graph in format: {format}")
        
        # Get the exported file
        export_file = exports[format]
        
        # Set the appropriate media type
        media_types = {
            "json": "application/json",
            "gexf": "application/xml",
            "graphml": "application/xml",
            "cytoscape": "application/json"
        }
        
        media_type = media_types.get(format, "application/octet-stream")
        
        # Return the exported file
        return FileResponse(
            export_file,
            media_type=media_type,
            filename=f"llamagraph_{graph_id}.{export_file.suffix}"
        )
    
    except Exception as e:
        logging.exception("Error exporting graph")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload", response_model=ProcessResponse)
async def upload_file(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    """
    Upload a file and process its contents
    """
    try:
        # Check if the file is text
        content_type = file.content_type
        if not content_type or not content_type.startswith("text/"):
            raise HTTPException(status_code=400, detail="Only text files are supported")
        
        # Read the file contents
        contents = await file.read()
        text = contents.decode("utf-8")
        
        # Process the text
        config = LlamaGraphConfig()
        cache = Cache(config.cache_dir, config.max_size)
        entity_extractor = EntityExtractor(config, cache)
        relation_extractor = RelationExtractor(config, cache)
        kg = KnowledgeGraph()
        
        # Extract entities
        entities = entity_extractor.extract(text)
        
        # Extract relations
        relations = relation_extractor.extract(text, entities)
        
        # Build knowledge graph
        for entity in entities:
            kg.add_entity(entity)
        
        for relation in relations:
            kg.add_relation(relation)
        
        # Generate a unique ID for this graph
        import uuid
        graph_id = str(uuid.uuid4())
        
        # Store the knowledge graph
        knowledge_graphs[graph_id] = kg
        
        # Schedule a cleanup task if background_tasks is provided
        if background_tasks:
            background_tasks.add_task(cleanup_graph, graph_id, 3600)
        
        # Convert to API model
        kg_data = kg.to_dict()
        kg_model = KnowledgeGraphModel(
            entities=[Entity(**e) for e in kg_data["entities"]],
            relations=[Relation(**r) for r in kg_data["relations"]]
        )
        
        return ProcessResponse(
            success=True,
            message=f"Successfully processed file with {len(entities)} entities and {len(relations)} relations",
            knowledge_graph=kg_model,
            graph_id=graph_id
        )
    
    except Exception as e:
        logging.exception("Error processing uploaded file")
        raise HTTPException(status_code=500, detail=str(e))

async def cleanup_graph(graph_id: str, delay_seconds: int = 3600):
    """
    Remove a knowledge graph after a delay
    """
    import asyncio
    
    # Wait for the specified delay
    await asyncio.sleep(delay_seconds)
    
    # Remove the graph if it still exists
    if graph_id in knowledge_graphs:
        del knowledge_graphs[graph_id]
        logging.info(f"Cleaned up graph {graph_id}")

def start_api_server(host: str = "0.0.0.0", port: int = 8000):
    """
    Start the FastAPI server
    """
    if not HAS_FASTAPI:
        logging.error("FastAPI is required for the API server. Install with pip install fastapi uvicorn")
        return
    
    import uvicorn
    uvicorn.run("llamagraph.server.api:app", host=host, port=port, reload=False) 