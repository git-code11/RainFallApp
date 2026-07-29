import numpy as np
from ai_edge_litert.compiled_model import CompiledModel


class TFLiteRuntime:
    def __init__(self, model: CompiledModel):
        self.model = model
        self.signature_index = 0
        self.input_buffers = model.create_input_buffers(self.signature_index)
        self.output_buffers = model.create_output_buffers(self.signature_index)

    def __call__(self, X):
        self.input_buffers[0].write(X)
        self.model.run_by_index(self.signature_index,
                                self.input_buffers, self.output_buffers)
        output_array = self.output_buffers[0].read(1, np.float32)
        return output_array

    @classmethod
    def load(cls, model_path):
        assert model_path.lower().endswith("tflite"), "Require .tflite suffix"
        model = CompiledModel.from_file(model_path=model_path)
        return cls(model)
