from agents.orchestrator.orchestrator_agent import OrchestratorAgent
from models.decoder_model import LocalDecoderModel
from models.encoder_decoder_model import LocalEncoderDecoderModel
from recipes_rag.recipes_rag import RecipesRAG
from agents.ingredients.ingredients_agent import IngredientsAgent
from agents.synthesis.synthesis_agent import SynthesisAgent
from agents.prices.prices_agent import PricesAgent
from agents.memory.memory_agent import MemoryAgent

from scraping.prices_scraper import PriceScaper
from scraping.prices_extraction import PriceExtractor
from scraping.database_manager import DatabaseManager

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
    # enc_dec_model.free()
