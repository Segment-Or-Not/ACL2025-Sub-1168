from io import TextIOWrapper
from typing import List
from transformers import AutoTokenizer
import os
from tqdm import tqdm
import copy
from nltk.tokenize import sent_tokenize, word_tokenize, TextTilingTokenizer


from .model_logger.model_args import (
    ModelArgs,
    call_model_for_summarization,
    call_model_for_scene_boundary_identification,
    call_model_for_naive_scene_boundary_identification
)


constant_splitting_length = 800
para_size_threshold = 100

from dataclasses import dataclass

@dataclass
class SegmentationObject:
    name: str
    size: int

@dataclass
class SceneSegmentation(SegmentationObject):
    def __init__(self):
        super().__init__("Scene", size=0)

@dataclass
class NaiveSceneSegmentation(SegmentationObject):
    def __init__(self):
        super().__init__("NaiveScene", size=0)

@dataclass
class ConstantSegmentation(SegmentationObject):
    def __init__(self, size:int = constant_splitting_length):
        super().__init__("Constant", size)

@dataclass
class TextTiling(SegmentationObject):
    def __init__(self):
        super().__init__("TextTiling", size=0)


def seg_obj_repr(seg_obj: SegmentationObject) -> str:

    if seg_obj:
        return seg_obj.name + str(seg_obj.size)
    else:
        return "NoSegmentation"


def split_chapter_into_constant_segments(
        story: str, split_length: int = constant_splitting_length
    ) -> List[str]:
    
    sents = sent_tokenize(story)
    segments = []

    prev_diff = split_length
    seg = ""
    for sent in sents:
        if prev_diff < abs(prev_diff - len(sent)):
            segments.append(seg)
            seg = sent
            prev_diff = abs(split_length - len(sent))
        else:
            seg += sent
            prev_diff = abs(prev_diff - len(sent))

    segments.append(seg)
    return segments


def is_scene_bounary(
        model_args: ModelArgs, 
        previous_context: list[str], 
        following_context: list[str],
        debug_writer: TextIOWrapper,
        naive_seg=False
    ) -> bool:
    
    if naive_seg:
        reasoning, answer = call_model_for_naive_scene_boundary_identification(
            model_args=model_args,
            previous_context=previous_context,
            following_context=following_context,
            temperature=0
        )
    else:
        reasoning, answer = call_model_for_scene_boundary_identification(
            model_args=model_args,
            previous_context=previous_context,
            following_context=following_context,
            temperature=0
        )

    prompt = "\n".join((
        "Previous Context:",
        "".join(previous_context) + "\n",
        "Following Context:",
        "".join(following_context) + "\n",
    ))

    result = " ".join((
        "Rasoning:\n",
        reasoning.strip(),
        "\nBoundary:",
        answer.strip()
    ))

    # Log for debugging
    debug_writer.write(prompt + "\n" + result +"\n\n")

    if answer.strip().lower() not in ['yes', 'no']:
        debug_writer.write(">>>>> BIG BIG PROBLEM HERE <<<<<<")

    return answer.strip().lower().startswith("yes")


def split_chapter_into_scenes(
        story: str, model_args: ModelArgs,
        chapter_title: str, results_for_debug: str,
        context_window_size = 5, naive_seg=False
    ) -> List[str]:
    """
    Split the story into scenes
    """
    sentences = sent_tokenize(story)
    min_scene_size = context_window_size

    ## Classify sentences as boundary and not boundary
    is_boundary: list[bool] = [False]*(min_scene_size - 1)
    last_scene_boundary = min_scene_size
    debug_writer = open(results_for_debug + "/" + chapter_title + ".txt", "w")
    for i in tqdm(range(min_scene_size, len(sentences)-min_scene_size+1)):

        if last_scene_boundary == min_scene_size:
            previous_context = sentences[max(0, i-context_window_size):i]
            following_context = sentences[i:min(len(sentences), i+context_window_size)]
            is_boundary_sentence = is_scene_bounary(model_args, previous_context, following_context, debug_writer, naive_seg)
            if is_boundary_sentence:
                last_scene_boundary = 0
        else:
            is_boundary_sentence = False
            last_scene_boundary += 1

        is_boundary.append(is_boundary_sentence)

    is_boundary.extend([False]*(min_scene_size - 1)) #Last sentence is never a bounary

    ## Group sentences in scenes
    segments = []
    seg = sentences[0] #0th sentence is always a boundary
    for sentence, is_boundary_sentence in zip(sentences[1:], is_boundary):
        if is_boundary_sentence:
            segments.append(seg)
            seg = sentence
        else:
            seg += sentence

    segments.append(seg)

    seg_sizes = [len(seg) for seg in segments]
    for i, seg in enumerate(segments):
        if len(seg) == 0:
            print("here")
            print(segments[i-1])
            print(segments[i+1])   
    debug_writer.write(
        f"Size details (Avg, Min, Max): {(sum(seg_sizes)/len(seg_sizes), min(seg_sizes), max(seg_sizes))}"
    )
    debug_writer.close()

    return segments


def segment_by_text_tiling(story: str) -> list[str]:

    sentences = sent_tokenize(story)
    mean_words_per_sentence = sum(len(word_tokenize(s)) for s in sentences)//len(sentences)

    # # Because conversation dialogues are written in their own lines we remove those.
    # paragraphs = [para.strip() for para in story.split("\n\n") if '"' not in para]
    # mean_paragraph_length = sum(len(p) for p in paragraphs)//len(paragraphs)

    return TextTilingTokenizer(w=mean_words_per_sentence).tokenize(story)


def get_segment_summaries(segments: list[str], model_args: ModelArgs, summary_pov_details: str, segment_summary_length: int):
    """
    Extract summary for each segment
    """

    summaries = []

    for seg in tqdm(segments):

        prompt = "Segment:\n\n" + seg
        system_prompt = " ".join(
                (
                    "A story segment is provided to following the Segment: tag.",
                    f"Generate short summary of this segment under {segment_summary_length} words.",
                    summary_pov_details,
                    "Obey the following instructions.\n",
                    "\nSummary should be in third person perspective.",
                    "\nGenerate simple sentences.",
                    "\nThe sentences shouldn't have any appositives or dependent clauses.",
                    "\nMinimize descriptive elaborations.",
                    "\n\n"
                 )
            )
        temperature = 0
        summary = call_model_for_summarization(model_args, prompt, system_prompt, temperature)

        summaries.append(summary)

    return summaries


class SegmentationUtil:

    def __init__(
            self, chapter_title, chapter_text: str, segment_summary_length: int,
            summary_pov_details, model_args, results_for_debug, 
            segmentation_method: SegmentationObject
        ):
        #segment_size is ignored if the constant_segment flag is False
        
        os.makedirs(results_for_debug, exist_ok=True)
        segments = []
        
        match segmentation_method:
            case ConstantSegmentation():
                segments += split_chapter_into_constant_segments(chapter_text, split_length=segmentation_method.size)
            case SceneSegmentation():
                segments += split_chapter_into_scenes(chapter_text, model_args, chapter_title, results_for_debug)
            case NaiveSceneSegmentation():
                segments += split_chapter_into_scenes(chapter_text, model_args, chapter_title, results_for_debug, naive_seg=True)
            case TextTiling():
                segments += segment_by_text_tiling(chapter_text)

        segment_summaries = get_segment_summaries(segments, model_args, summary_pov_details, segment_summary_length)

        self.segments = segments
        self.segment_summaries = segment_summaries

        with open(results_for_debug + "/" + chapter_title + "_segments_and_summaries.txt", "w") as dw:
            for seg, summ in zip(segments, segment_summaries):
                dw.write("\n".join((
                    "Segment:",
                    seg,
                    "Summary:",
                    summ,"\n"
                )))

    def get_segment_summaries(self) -> list[str]:
        return copy.deepcopy(self.segment_summaries)