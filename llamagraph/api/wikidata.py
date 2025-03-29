"""
Wikidata integration for LlamaGraph

This module allows LlamaGraph to fetch additional entity and relation data from Wikidata,
enriching the knowledge graph with external structured data.
"""
import logging
import time
from typing import Dict, Any, List, Optional, Union, Tuple
import json
import urllib.parse
import urllib.request
from urllib.error import HTTPError, URLError

from llamagraph.extractor.entity_extractor import Entity
from llamagraph.graph.knowledge_graph import KnowledgeGraph

logger = logging.getLogger(__name__)

# Wikidata endpoint URLs
WIKIDATA_API_URL = "https://www.wikidata.org/w/api.php"
WIKIDATA_SPARQL_URL = "https://query.wikidata.org/sparql"

class WikidataEnricher:
    """Class for enriching LlamaGraph knowledge graphs with data from Wikidata"""
    
    def __init__(self, user_agent: str = "LlamaGraph/1.0.0"):
        """
        Initialize the Wikidata enricher
        
        Args:
            user_agent: The User-Agent header to use in requests
        """
        self.user_agent = user_agent
        self.cache = {}  # Simple in-memory cache
    
    def enrich_entity(self, entity: Entity) -> Dict[str, Any]:
        """
        Enrich a single entity with data from Wikidata
        
        Args:
            entity: The entity to enrich
            
        Returns:
            Dictionary with additional entity attributes from Wikidata
        """
        # Try to get from cache first
        cache_key = f"entity_{entity.text}_{entity.entity_type}"
        if cache_key in self.cache:
            logger.info(f"Using cached Wikidata data for '{entity.text}'")
            return self.cache[cache_key]
        
        # Search for the entity in Wikidata
        search_results = self._search_entity(entity.text)
        
        # If no results, try with normalized text
        if not search_results and entity.text != entity.normalized_text:
            search_results = self._search_entity(entity.normalized_text)
        
        # If still no results, return empty dict
        if not search_results:
            logger.info(f"No Wikidata results found for '{entity.text}'")
            self.cache[cache_key] = {}
            return {}
        
        # Get the first (most relevant) result
        wikidata_id = search_results[0]["id"]
        
        # Get entity details from Wikidata
        entity_data = self._get_entity_details(wikidata_id)
        
        # Cache the result
        self.cache[cache_key] = entity_data
        
        return entity_data
    
    def enrich_knowledge_graph(self, kg: KnowledgeGraph) -> None:
        """
        Enrich an entire knowledge graph with data from Wikidata
        
        Args:
            kg: The knowledge graph to enrich
            
        Returns:
            None (modifies the knowledge graph in-place)
        """
        logger.info("Enriching knowledge graph with Wikidata data...")
        
        # Process each entity
        for entity_text, entity in kg.entities.items():
            try:
                # Get Wikidata data for this entity
                wikidata_data = self.enrich_entity(entity)
                
                if wikidata_data:
                    # Add Wikidata attributes to the entity in the graph
                    for key, value in wikidata_data.items():
                        # Avoid overwriting existing attributes
                        if key not in kg.graph.nodes[entity_text]:
                            kg.graph.nodes[entity_text][key] = value
                    
                    # Mark as enriched
                    kg.graph.nodes[entity_text]["wikidata_enriched"] = True
                
                # Be nice to the Wikidata API
                time.sleep(0.5)
                
            except Exception as e:
                logger.warning(f"Error enriching entity '{entity_text}': {e}")
        
        logger.info("Knowledge graph enrichment complete")
    
    def find_additional_relations(self, kg: KnowledgeGraph) -> List[Dict[str, Any]]:
        """
        Find additional relations between entities in the knowledge graph
        from Wikidata
        
        Args:
            kg: The knowledge graph to find relations for
            
        Returns:
            List of potential new relations
        """
        new_relations = []
        
        # Get all entity pairs where both have Wikidata IDs
        entity_pairs = []
        for source in kg.entities:
            for target in kg.entities:
                if source != target:
                    source_id = kg.graph.nodes[source].get("wikidata_id")
                    target_id = kg.graph.nodes[target].get("wikidata_id")
                    if source_id and target_id:
                        entity_pairs.append((source, target, source_id, target_id))
        
        # Query for relations between each pair
        for source, target, source_id, target_id in entity_pairs:
            try:
                relations = self._get_relations(source_id, target_id)
                
                if relations:
                    for relation in relations:
                        new_relations.append({
                            "source": source,
                            "target": target,
                            "relation_type": relation["predicate_label"],
                            "wikidata_predicate": relation["predicate"],
                            "sentence": f"According to Wikidata, {source} {relation['predicate_label']} {target}."
                        })
                
                # Be nice to the Wikidata API
                time.sleep(0.5)
                
            except Exception as e:
                logger.warning(f"Error finding relations between '{source}' and '{target}': {e}")
        
        return new_relations
    
    def _search_entity(self, entity_text: str) -> List[Dict[str, Any]]:
        """
        Search for an entity in Wikidata
        
        Args:
            entity_text: The text to search for
            
        Returns:
            List of search results
        """
        params = {
            "action": "wbsearchentities",
            "format": "json",
            "language": "en",
            "search": entity_text
        }
        
        try:
            response = self._make_request(WIKIDATA_API_URL, params)
            return response.get("search", [])
        except Exception as e:
            logger.warning(f"Error searching Wikidata for '{entity_text}': {e}")
            return []
    
    def _get_entity_details(self, entity_id: str) -> Dict[str, Any]:
        """
        Get detailed information about an entity from Wikidata
        
        Args:
            entity_id: The Wikidata entity ID
            
        Returns:
            Dictionary with entity details
        """
        params = {
            "action": "wbgetentities",
            "format": "json",
            "ids": entity_id,
            "languages": "en",
            "props": "labels|descriptions|claims"
        }
        
        try:
            response = self._make_request(WIKIDATA_API_URL, params)
            
            # Extract the entity data
            if entity_id in response.get("entities", {}):
                entity_data = response["entities"][entity_id]
                
                # Extract useful attributes
                result = {
                    "wikidata_id": entity_id,
                    "wikidata_label": self._extract_label(entity_data),
                    "wikidata_description": self._extract_description(entity_data),
                }
                
                # Extract important properties
                properties = self._extract_properties(entity_data)
                result.update(properties)
                
                return result
            
            return {}
            
        except Exception as e:
            logger.warning(f"Error getting Wikidata details for '{entity_id}': {e}")
            return {}
    
    def _get_relations(self, source_id: str, target_id: str) -> List[Dict[str, Any]]:
        """
        Get relations between two entities from Wikidata
        
        Args:
            source_id: The Wikidata ID of the source entity
            target_id: The Wikidata ID of the target entity
            
        Returns:
            List of relations between the entities
        """
        # SPARQL query to find relations between two entities
        sparql_query = f"""
        SELECT ?predicate ?predicateLabel WHERE {{
          wd:{source_id} ?predicate wd:{target_id} .
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}
        }}
        """
        
        params = {
            "query": sparql_query,
            "format": "json"
        }
        
        try:
            response = self._make_request(WIKIDATA_SPARQL_URL, params, is_sparql=True)
            
            results = []
            for binding in response.get("results", {}).get("bindings", []):
                if "predicate" in binding and "predicateLabel" in binding:
                    results.append({
                        "predicate": binding["predicate"]["value"].split("/")[-1],
                        "predicate_label": binding["predicateLabel"]["value"]
                    })
            
            return results
            
        except Exception as e:
            logger.warning(f"Error querying Wikidata for relations between '{source_id}' and '{target_id}': {e}")
            return []
    
    def _make_request(self, url: str, params: Dict[str, str], is_sparql: bool = False) -> Dict[str, Any]:
        """
        Make a request to the Wikidata API
        
        Args:
            url: The API URL
            params: Request parameters
            is_sparql: Whether this is a SPARQL endpoint request
            
        Returns:
            JSON response as a dictionary
        """
        # Encode parameters
        if is_sparql:
            data = urllib.parse.urlencode(params).encode()
            headers = {
                "User-Agent": self.user_agent,
                "Accept": "application/sparql-results+json",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            req = urllib.request.Request(url, data=data, headers=headers)
        else:
            query_string = urllib.parse.urlencode(params)
            full_url = f"{url}?{query_string}"
            headers = {"User-Agent": self.user_agent}
            req = urllib.request.Request(full_url, headers=headers)
        
        try:
            with urllib.request.urlopen(req) as response:
                return json.loads(response.read().decode())
        except (HTTPError, URLError) as e:
            logger.error(f"Error making request to Wikidata: {e}")
            raise
    
    def _extract_label(self, entity_data: Dict[str, Any]) -> str:
        """Extract the English label from entity data"""
        labels = entity_data.get("labels", {})
        if "en" in labels:
            return labels["en"].get("value", "")
        return ""
    
    def _extract_description(self, entity_data: Dict[str, Any]) -> str:
        """Extract the English description from entity data"""
        descriptions = entity_data.get("descriptions", {})
        if "en" in descriptions:
            return descriptions["en"].get("value", "")
        return ""
    
    def _extract_properties(self, entity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract important properties from entity data"""
        properties = {}
        claims = entity_data.get("claims", {})
        
        # Important property mappings
        # (Wikidata property ID -> user-friendly name)
        property_map = {
            "P31": "instance_of",      # instance of
            "P279": "subclass_of",     # subclass of
            "P19": "place_of_birth",   # place of birth
            "P569": "date_of_birth",   # date of birth
            "P570": "date_of_death",   # date of death
            "P106": "occupation",      # occupation
            "P27": "country",          # country of citizenship
            "P17": "country_located",  # country (for locations)
            "P159": "headquarters",    # headquarters location
            "P856": "website",         # official website
            "P112": "founded_by",      # founded by
            "P571": "inception_date",  # inception/founding date
            "P463": "member_of",       # member of
            "P361": "part_of",         # part of
            "P527": "has_part",        # has part
            "P1056": "product",        # product or material produced
        }
        
        # Extract values for each property
        for pid, friendly_name in property_map.items():
            if pid in claims:
                values = []
                for claim in claims[pid]:
                    mainsnak = claim.get("mainsnak", {})
                    if mainsnak.get("datatype") == "wikibase-item":
                        if "datavalue" in mainsnak:
                            value_id = mainsnak["datavalue"]["value"]["id"]
                            values.append(value_id)
                    elif mainsnak.get("datatype") == "time":
                        if "datavalue" in mainsnak:
                            time_value = mainsnak["datavalue"]["value"]["time"]
                            values.append(time_value)
                    elif mainsnak.get("datatype") == "url":
                        if "datavalue" in mainsnak:
                            url_value = mainsnak["datavalue"]["value"]
                            values.append(url_value)
                    elif mainsnak.get("datatype") == "string":
                        if "datavalue" in mainsnak:
                            string_value = mainsnak["datavalue"]["value"]
                            values.append(string_value)
                
                if values:
                    properties[f"wikidata_{friendly_name}"] = values
        
        return properties 