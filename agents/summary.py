from models.encoder_decoder_model import ABCEncoderDecoderModel, APIEncoderDecoderModel, LocalEncoderDecoderModel

class ABCSummaryAgent(ABCEncoderDecoderModel):
    pass

class APISummaryAgent(APIEncoderDecoderModel):
    def prompt(self, input, parameters=None) -> str:
        return super().prompt("summarize: " + input, parameters)

class LocalSummaryAgent(LocalEncoderDecoderModel):
    def prompt(self, input, parameters=None) -> str:
        return super().prompt("summarize: " + input, parameters)