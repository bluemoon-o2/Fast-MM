from typing import List
import numpy as np
try:
    import torch
    import torch.nn.functional as F
    from transformers import AutoModel, AutoTokenizer
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False

class EmbeddingScorer:
    """
    A class for performing semantic search using embeddings.
    Uses the gte-multilingual-base model from Alibaba-NLP.
    """
    
    def __init__(self, model_name='Alibaba-NLP/gte-multilingual-base'):
        """
        Initialize the EmbeddingScorer with the specified model.
        
        Args:
            model_name (str): Name of the model to use.
        """
        if not HAS_TORCH:
            print("Warning: torch or transformers not found. EmbeddingScorer will not work.")
            return

        # Load the tokenizer and model
        # Using trust_remote_code=True as in original code
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name, trust_remote_code=True)
        self.dimension = 768  # The output dimension of the embedding
    
    def score_method(self, query: str, methods: List[dict]) -> List[dict]:
        """
        Calculate similarity between a query and a list of methods.
        
        Args:
            query (str): The query sentence.
            methods (list): List of method dictionaries to compare against the query.
            
        Returns:
            list: List of similarity scores between the query and each method.
        """
        if not HAS_TORCH:
            return [{"method_index": i+1, "score": 0.0} for i in range(len(methods))]

        # Prepare sentences
        sentences = [f"{method['method']}: {method.get('description', '')}" for method in methods]
        texts = [query] + sentences
        
        # Tokenize the input texts
        batch_dict = self.tokenizer(texts, max_length=8192, padding=True, truncation=True, return_tensors='pt')
        
        # Get embeddings
        with torch.no_grad():
            outputs = self.model(**batch_dict)
            
        # Get embeddings from the last hidden state
        embeddings = outputs.last_hidden_state[:, 0][:self.dimension]
        
        # Normalize embeddings
        embeddings = F.normalize(embeddings, p=2, dim=1)
        
        # Calculate similarities
        query_embedding = embeddings[0].unsqueeze(0)  # Shape: [1, dimension]
        method_embeddings = embeddings[1:]  # Shape: [num_methods, dimension]
        
        # Calculate cosine similarities (scaled by 100 as in the example)
        similarities = (query_embedding @ method_embeddings.T) * 100
        similarities = similarities.squeeze().tolist()
        
        # If only one method, similarities will be a scalar
        if not isinstance(similarities, list):
            similarities = [similarities]
        
        # Format results
        result = []
        for i, similarity in enumerate(similarities, start=1):
            result.append({
                "method_index": i,
                "score": float(similarity)
            })
        
        return result
