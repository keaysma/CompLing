import os, json, math
from typing import Dict, List, Tuple, Callable
from collections import defaultdict

Weights = List[Tuple[str, int]]

t = ['this', 'is', 'a', 'test', 'of', 'the', 'system!']

WINDOW_MAX_SIZE = 5

class BaysianWeights:
    weights: Dict[str, Dict[str, int]]

    def __init__(self) -> None:
        self.weights = defaultdict(dict)

    @staticmethod
    def __vectorize_inputs(inputs: List[str]) -> str:
        return ' '.join(inputs)

    def load_weights(self, path_to_weights: str = "./weights.json") -> None:
        self.weights = json.load(open(path_to_weights, 'r'))
    
    def save_weights(self, path_to_weights: str = "./weights.json") -> None:
        with open(path_to_weights, 'w') as f:
            f.write(json.dumps(self.weights))
        return
    
    def add_weight(self, inputs: List[str], output: str) -> None:
        v_inputs = self.__vectorize_inputs(inputs)
        if self.weights[v_inputs].get(output) is not None:
            self.weights[v_inputs][output] += 1
        else:
            self.weights[v_inputs][output] = 1

    def get_weights(self, inputs: List[str]) -> Weights:
        return list(self.weights[self.__vectorize_inputs(inputs)].items())
    
    def get_weights_spread(self, inputs: List[str]) -> Dict[str, Weights]:
        spread = {}
        for i in range(len(inputs)):
            v_inputs = self.__vectorize_inputs(inputs[i:])
            if self.weights.get(v_inputs):
                spread[v_inputs] = list(self.weights[v_inputs].items())
        return spread
    
    def next_word(self, inputs: List[str], calc_fn: Callable[[Dict[str, Weights]], str]) -> str:
        spread = self.get_weights_spread(inputs)
        return calc_fn(spread)
    
def next_word_v1(spread: Dict[str, Weights]) -> str:
    strength: Dict[str, int] = defaultdict(int)
    for key, weights in spread.items():
        for output, weight in weights:
            #print(f"{output=} -> {weight=} * {math.sqrt(len(key.split()))}")
            strength[output] += weight * math.sqrt(len(key.split()))
    #print(f"{strength=}")
    strength_tuples = list(strength.items())
    strength_tuples.sort(key=lambda v: v[1], reverse=True)

    if len(strength_tuples) == 0:
        return ''
    
    return strength_tuples[0][0]

def get_windows(tokens: List[str], window_size: int) -> List[Tuple[List[str], str]]:
    windows = []
    for i in range(1, len(tokens)):
        windows.append((tokens[max(0, i-window_size):i], tokens[i]))
    return windows

def train_on_tokens(tokens: List[str]):
    for window_size in range(1, WINDOW_MAX_SIZE):
        for (inputs, output) in get_windows(tokens, window_size):
            w.add_weight(inputs, output)

def train_on_data():
    for file_name in os.listdir('./data'):
        print(f"{file_name=}")
        data = json.load(open(f"./data/{file_name}", "r"))
        train_on_tokens(data["tokens"])

def ramble(w: BaysianWeights, prompt: str, length: int = 5):
    """
    Starting with a prompt, just talk for length amount of tokens
    """
    tokens = prompt.split()
    for i in range(length):
        tokens.append(w.next_word(tokens, next_word_v1))
    print(' '.join(tokens))

if __name__ == '__main__':
    w = BaysianWeights()