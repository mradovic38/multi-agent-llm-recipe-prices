from agents.orchestrator.orchestrator_agent import OrchestratorAgent
from models.decoder_model import LocalDecoderModel
from models.encoder_decoder_model import LocalEncoderDecoderModel
from recipes_rag.recipes_rag import RecipesRAG
from agents.ingridients.ingridients import IngredientsAgent
from agents.synthesis.synthesis_agent import SynthesisAgent

decoder_model = LocalDecoderModel()
try:
    
    # enc_dec_model = LocalEncoderDecoderModel()
    orchestrator_agent = OrchestratorAgent(
        decoder_model, 
        RecipesRAG(), 
        IngredientsAgent(decoder_model), 
        None,
        SynthesisAgent(decoder_model), 
        None)
    user_in = "How to make a pizza?"
    #user_in = "I really like to eat pizza with my family"
    #user_in += "\n Only write the python block\n '''"
    resp = orchestrator_agent.prompt(user_in)
    print(resp)
except Exception as e:
    print(e)
finally:
    decoder_model.free()
    # enc_dec_model.free()
