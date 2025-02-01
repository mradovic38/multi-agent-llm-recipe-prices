from models import LocalDecoderModel

from agents import OrchestratorAgent, IngredientsAgent, SynthesisAgent, PricesAgent, MemoryAgent

from tools import RecipesRAG, PriceScaper, PriceExtractor, DatabaseManager

decoder_model = LocalDecoderModel()

try:
    scraper  = PriceScaper()
    extractor = PriceExtractor()
    manager = DatabaseManager()

    orchestrator_agent = OrchestratorAgent(
        decoder_model, 
        RecipesRAG(), 
        IngredientsAgent(decoder_model), 
        PricesAgent(decoder_model, scraper, extractor, manager),
        SynthesisAgent(decoder_model),
        MemoryAgent(decoder_model))
    
    user_in = "Recipe for cookies"
    resp = orchestrator_agent.prompt(user_in)
    print("-"*100)
    print("Synthesized response:")
    print(resp)
    print("-"*100)
    
except Exception as e:
    print(e)
finally:
    decoder_model.free()
