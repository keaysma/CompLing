import os, json, math
from typing import Dict, List, Tuple, Callable
from collections import defaultdict

Weights = List[Tuple[str, int]]

t = ['this', 'is', 'a', 'test', 'of', 'the', 'system!']

WINDOW_MAX_SIZE = 20
MAX_TRAINING_FILES = 2_500

class BaysianWeights:
    weights: Dict[str, Dict[str, int]]

    def __init__(self) -> None:
        self.weights = defaultdict(dict)

    @staticmethod
    def __vectorize_inputs(inputs: List[str]) -> str:
        return ' '.join(inputs)

    def load_weights(self, path_to_weights: str = "./weights.json") -> None:
        print(f"loading weights from {path_to_weights}")
        self.weights = json.load(open(path_to_weights, 'r'))
    
    def save_weights(self, path_to_weights: str = "./weights.json") -> None:
        print(f"saving weights to {path_to_weights}")
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

def next_word_v2(spread: Dict[str, Weights]) -> str:
    strength: Dict[str, int] = defaultdict(int)
    for key, weights in spread.items():
        for output, weight in weights:
            strength[output] += weight * math.pow(len(key.split()), 2)
    strength_tuples = list(strength.items())
    strength_tuples.sort(key=lambda v: v[1], reverse=True)
    if len(strength_tuples) == 0:
        return ''
    return strength_tuples[0][0]

def next_word_v3(spread: Dict[str, Weights]) -> str:
    strength: Dict[str, int] = defaultdict(int)
    for key, weights in spread.items():
        for output, weight in weights:
            strength[output] += weight * math.pow(len(key.split()), 4)
    strength_tuples = list(strength.items())
    strength_tuples.sort(key=lambda v: v[1], reverse=True)
    if len(strength_tuples) == 0:
        return ''
    return strength_tuples[0][0]

def next_word_v4(spread: Dict[str, Weights]) -> str:
    strength: Dict[str, int] = defaultdict(int)
    for key, weights in spread.items():
        for output, weight in weights:
            strength[output] += math.pow(weight, len(key.split()))
    strength_tuples = list(strength.items())
    strength_tuples.sort(key=lambda v: v[1], reverse=True)
    if len(strength_tuples) == 0:
        return ''
    return strength_tuples[0][0]

import random
def next_word_v5(spread: Dict[str, Weights]) -> str:
    strength: Dict[str, int] = defaultdict(int)
    for key, weights in spread.items():
        for output, weight in weights:
            strength[output] += math.pow(len(key.split()), math.sqrt(weight))
    strength_tuples = list(strength.items())
    strength_tuples.sort(key=lambda v: v[1], reverse=True)
    if len(strength_tuples) == 0:
        return ''
    return strength_tuples[random.randint(0, min(5, len(strength_tuples)))][0]

def next_word_v6(spread: Dict[str, Weights]) -> str:
    strength: Dict[str, int] = defaultdict(int)
    for key, weights in spread.items():
        for output, weight in weights:
            strength[output] += math.pow(weight, (len(key.split()) - 7)/3)
    strength_tuples = list(strength.items())
    strength_tuples.sort(key=lambda v: v[1], reverse=True)
    if len(strength_tuples) == 0:
        return ''
    return strength_tuples[0][0]

def next_word_v7(spread: Dict[str, Weights]) -> str:
    strength: Dict[str, int] = defaultdict(int)
    for key, weights in spread.items():
        for output, weight in weights:
            x = len(key.split())
            y = (-math.pow((1.05 * x) - 7, 2) + 20)/8
            strength[output] += math.pow(weight, y)
    strength_tuples = list(strength.items())
    strength_tuples.sort(key=lambda v: v[1], reverse=True)
    if len(strength_tuples) == 0:
        return ''
    return strength_tuples[0][0]

def next_word_v8(spread: Dict[str, Weights]) -> str:
    strength: Dict[str, int] = defaultdict(int)
    for key, weights in spread.items():
        for output, weight in weights:
            x = len(key.split())
            y = (-math.pow((1.05 * x) - 9, 2) + (20.5 * x))/15
            strength[output] += math.pow(weight, y)
    strength_tuples = list(strength.items())
    strength_tuples.sort(key=lambda v: v[1], reverse=True)
    if len(strength_tuples) == 0:
        return ''
    return strength_tuples[0][0]

import random
#KEY_LEN_FACTOR = [-1, -9, -1, -3, 5, 6, 5,4,3,3,-20,-2,-3,-4,-10, -8,-6,-4,-2,-1]
KEY_LEN_FACTOR = [0,-3,-2,1,1,1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1]
def next_word_v9(spread: Dict[str, Weights]) -> str:
    strength: Dict[str, int] = defaultdict(int)
    strength_sentinel: Dict[str, Tuple[int, int]] = {}
    for key, weights in spread.items():
        for output, weight in weights:
            a = len(key.split())
            x = KEY_LEN_FACTOR[a]
            y = math.pow(weight, x)
            strength[output] += y
            if existing_sentinel_value:= strength_sentinel.get(output):
                if existing_sentinel_value[-2] < y:
                    strength_sentinel[output] = (weight, a, x, y, strength_sentinel[output][4] + 1, strength[output])
                else:
                    strength_sentinel[output] = (
                        strength_sentinel[output][0],
                        strength_sentinel[output][1],
                        strength_sentinel[output][2],
                        strength_sentinel[output][3],
                        strength_sentinel[output][4] + 1,
                        strength[output]
                    )
            else:
                strength_sentinel[output] = (weight, a, x, y, 1, strength[output])
    strength_tuples = list(strength.items())
    strength_tuples.sort(key=lambda v: v[1], reverse=True)
    if len(strength_tuples) == 0:
        return ''
    highest_val, highest_val_count = 0, 0
    for s in strength_tuples:
        if highest_val < s[1]:
            highest_val_count = 0
            highest_val = s[1]
        if highest_val == s[1]:
            highest_val_count += 1
    top_sentinets = list(strength_sentinel.items())
    top_sentinets.sort(key=lambda v: v[1][-1], reverse=True)
    print(f"{highest_val} ({highest_val_count})")
    [print(t) for t in top_sentinets[:highest_val_count+5]]
    #pick = random.randint(0, max(min(3, len(strength_tuples)), highest_val_count-1))
    pick = random.randint(0, highest_val_count-1)
    print(f"{pick=}")
    print()
    print()
    return strength_tuples[pick][0]

def get_windows(tokens: List[str], window_size: int) -> List[Tuple[List[str], str]]:
    windows = []
    for i in range(1, len(tokens)):
        windows.append((tokens[max(0, i-window_size):i], tokens[i]))
    return windows

def train_on_tokens(w: BaysianWeights, tokens: List[str]):
    for window_size in range(1, WINDOW_MAX_SIZE):
        for (inputs, output) in get_windows(tokens, window_size):
            w.add_weight(inputs, output)

def train_on_data(w: BaysianWeights):
    files = os.listdir('./data')
    for i, file_name in enumerate(files[:MAX_TRAINING_FILES]):
        print(f"[{i}/{len(files)}] {file_name=}")
        try:
            data = json.load(open(f"./data/{file_name}", "r"))
            train_on_tokens(w, data["tokens"])
        except:
            pass

def ramble(w: BaysianWeights, prompt: str, length: int = 5, fn: Callable = next_word_v1):
    """
    Starting with a prompt, just talk for length amount of tokens
    """
    tokens = prompt.split()
    for i in range(length):
        tokens.append(w.next_word(tokens, fn))
    print(' '.join(tokens))

def brute_force_ramble(w: BaysianWeights, prompt: str, length: int = 5, fn: Callable = next_word_v1):
    """
    Ramble breaks because next word fn has issues sometimes
    For lazy testing, just brute force past 'em
    """
    while True:
        try: return ramble(w, prompt, length, fn)
        except: pass

if __name__ == '__main__':
    mod = BaysianWeights()
    train_on_data(mod)
    mod.save_weights()