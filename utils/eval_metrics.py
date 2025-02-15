import evaluate
from typing import Union, Callable, List


def format_label(label: Union[str, list[str]]) -> Union[list[str], list[list[str]]]:
    return [label]


class RogueScore:

    def __init__(self, rouge_type):
        self.rouge_type = rouge_type
        self.rouge = evaluate.load("rouge")

    def __call__(self, label, prediction):

        label = format_label(label)
        
        result = self.rouge.compute(
            predictions=[prediction], references=label, use_stemmer=True, 
            rouge_types = [self.rouge_type]
        )
        return round(float(list(result.values())[0]), 4)


chrf = evaluate.load("chrf")
def compute_chrf(label, prediction):
    label = format_label(label)
    result = chrf.compute(
        predictions=[prediction], references=label
    )
    result = {k: round(float(v), 4) for k, v in result.items()}
    return result['score']


meteor = evaluate.load('meteor')
def compute_meteor(label, prediction):
    label = format_label(label)
    result = meteor.compute(
        predictions=[prediction], references=label
    )
    return round(float(list(result.values())[0]), 4)

bertscore = evaluate.load("bertscore")
class BertScore:
    def __init__(self):
        self.bertscore = bertscore
        self.hash_map = {}

    def compute_result(self, label, prediction):
        if prediction not in self.hash_map:
            label = format_label(label)
            result = bertscore.compute(
                predictions=[prediction], references=label, lang="en", 
                model_type='microsoft/deberta-xlarge-mnli'
            )
            self.hash_map[prediction] = result
        return self.hash_map[prediction]

    def compute_bertscore_p(self, label, prediction):
        result = self.compute_result(label, prediction)
        return round(result['precision'][0], 4)
    
    def compute_bertscore_r(self, label, prediction):
        result = self.compute_result(label, prediction)
        return round(result['recall'][0], 4)
    
    def compute_bertscore_f(self, label, prediction):
        result = self.compute_result(label, prediction)
        return round(result['f1'][0], 4)   


def get_metrics() -> dict[str, Callable]:
    bscore = BertScore()

    metrics = {
        'rouge1': RogueScore('rouge1'),
        'rouge2': RogueScore('rouge2'),
        'rouge3': RogueScore('rouge3'),
        'rouge4': RogueScore('rouge4'),
        'rougeL': RogueScore('rougeL'),
        'chrf': compute_chrf,
        'meteor': compute_meteor,
        'bert_score_p': bscore.compute_bertscore_p,
        'bert_score_r': bscore.compute_bertscore_r,
        'bert_score_f': bscore.compute_bertscore_f
    }

    return metrics