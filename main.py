from agents.orchestrator.orchestrator_agent import OrchestratorAgent
from models.decoder_model import LocalDecoderModel
from models.encoder_decoder_model import LocalEncoderDecoderModel
from recipes_rag.recipes_rag import RecipesRAG
from agents.ingridients.ingridients import IngredientsAgent

try:
    decoder_model = LocalDecoderModel()
    # enc_dec_model = LocalEncoderDecoderModel()
    orchestrator_agent = OrchestratorAgent(decoder_model, RecipesRAG(), IngredientsAgent(decoder_model), None, None)
    user_in = "How to make a pizza, use the systems code generation to help me"
    user_in = "I really like to eat pizza with my family"
    user_in += "\n Only write the python block\n '''"
    resp = orchestrator_agent.prompt(user_in)
    print(resp)
except Exception as e:
    print(e)
finally:
    decoder_model.free()
    # enc_dec_model.free()
