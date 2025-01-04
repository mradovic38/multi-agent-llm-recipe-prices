import faiss
from sentence_transformers import SentenceTransformer
import json
from typing import Dict

class RecipesRAG():
    def __init__(self,
                 recipes_json_path: str = "recipes_rag/recipes.json", 
                 model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
                 recipes_index_path: str = "recipes_rag/recipes_index.faiss") -> None:
        
        with open(recipes_json_path, "r", encoding="utf8") as f:
            self.recipes = json.load(f)

        self.model = SentenceTransformer(model_name)

        # Generate embeddings for the recipes
        embeddings = self.model.encode(self.recipes)

        # Save embeddings to a FAISS index
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings)
        
        # Save the FAISS index
        faiss.write_index(index, recipes_index_path)

        self.index=index


    def retrieve_recipe(self, query: str, top_k: int = 1) -> Dict[str, str]:
        # Generate query embedding
        query_embedding = self.model.encode([query])
        
        # Perform similarity search
        distances, indices = self.index.search(query_embedding, top_k)
        
        # Retrieve matching recipes
        results = [self.recipes[i] for i in indices[0]]

        return results


    def answer_query(self, query: str, top_k: int = 1):
        # Retrieve matching recipes
        recipes = self.retrieve_recipe(query, top_k)
        
        # Format response
        if recipes:
            return recipes[0]
        else:
            return "No recipes found matching your query."
        



if __name__ == '__main__':

    rr = RecipesRAG()

    def show_result(query):
        
        print("---Query:---")
        print(query)
        print('\n')
        print("---Result:---")
        print(rr.answer_query(query))
        print('-'*50)
        print('\n')

        
    
    query1 = "Give me a vegan recipe"
    show_result(query1)
    query2 = "How to make a pizza"
    show_result(query2)

