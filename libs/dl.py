import numpy as np

from ai_edge_litert.interpreter import Interpreter
# Import the LiteRT interpreter module


class TFLiteRuntime:
    def __init__(self, interpreter: Interpreter):
        self.interpreter = interpreter
        self.input_index = interpreter.get_input_details()[0]['index']
        self.output_index = interpreter.get_output_details()[0]['index']

    def __call__(self, X):
        X = np.array(X, dtype=np.float32)
        X = X[np.newaxis, ...]
        self.interpreter.set_tensor(self.input_index, X)
        self.interpreter.invoke()
        y_pred = self.interpreter.get_tensor(self.output_index)
        return y_pred[0]

    @classmethod
    def load(cls, model_path):
        assert model_path.lower().endswith("tflite"), "Require .tflite suffix"
        interpreter = Interpreter(model_path=model_path)
        interpreter.allocate_tensors()
        return cls(interpreter)
