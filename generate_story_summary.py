from data.story_info import Story, story_info_list
import os
from tqdm import tqdm
from utils.constants import (
    chapter_summary_length, result_parent_folder, result__debug_folder, stories_folder, segment_summary_length
)
from summarization_process.model_logger import ModelArgs, ModelReplicateArgs, ModelOpenAIArgs
from summarization_process import direct_summarization, segmented_summarization
from summarization_process.segmented_summarization import (
    SegmentationObject, SceneSegmentation, ConstantSegmentation, TextTiling, NaiveSceneSegmentation, seg_obj_repr
)
import sys


model_args_list = [
    ModelReplicateArgs(
        name="Llama3_70B",
        replicate_name="meta/meta-llama-3-70b-instruct",
    ),
    ModelOpenAIArgs(
        name="Gpt4o",
        openai_name="gpt-4o"
    ),
    ModelOpenAIArgs(
        name="Gpt4",
        openai_name='gpt-4-turbo'
    ),
    ModelOpenAIArgs(
        name="Gpt3.5",
        openai_name='gpt-3.5-turbo'
    )
]

segmentation_objects = [
    None, #No segmentattion
    SceneSegmentation(),
    ConstantSegmentation(600),
    ConstantSegmentation(800),
    ConstantSegmentation(1000),
    TextTiling(),
    NaiveSceneSegmentation()
]


def get_story_summary(story: Story, model_args: ModelArgs, seg_obj: SegmentationObject = None):

    story_name = story.name
    story_dir = f"{stories_folder}/{story_name}"
    segmentation_type = seg_obj_repr(seg_obj)
    results_dir = f"{result_parent_folder}/results__{model_args.name}_{segmentation_type}/{story_name}"

    # Different for different stories so probably better to use this as a variable
    summary_pov_details = story.pov_info

    os.makedirs(results_dir, exist_ok=True)

    for chp_file in tqdm(os.listdir(story_dir)):

        if os.path.isfile(results_dir+ "/" + chp_file + "/" + chp_file + ".txt"):
            continue

        os.makedirs(results_dir + "/" + chp_file, exist_ok=True) 
        chp_text = []

        for chp_sub_file in os.listdir(story_dir + "/" + chp_file):

            with open(
                story_dir + "/" + chp_file + "/" + chp_sub_file, "r"
            ) as f:

                chp_text.append(f.read())

        chp_text = "\n".join(chp_text)

        
        if seg_obj:
            summary = segmented_summarization.get_summary(
                chapter_title=chp_file, chapter_text=chp_text,
                summary_pov_details=summary_pov_details,
                segment_summary_length=segment_summary_length,
                chapter_summary_length=chapter_summary_length,
                model_args=model_args, result_debug_folder=result__debug_folder,
                story_name=story_name, seg_obj=seg_obj
            )

        else:
            summary = direct_summarization.get_summary(
                chapter_text=chp_text, summary_pov_details=summary_pov_details,
                chapter_summary_length=chapter_summary_length, model_args=model_args
            )

        with open(results_dir+ "/" + chp_file + "/" + chp_file + ".txt", "w") as fw:
            fw.write(summary)

            


if __name__ == "__main__":

    story_start, story_end = 0 , -1

    if len(sys.argv) == 5:
        model_index = int(sys.argv[1])
        segmentation_index = int(sys.argv[2])
        model_args_list = [model_args_list[model_index]]
        segmentation_objects = [segmentation_objects[segmentation_index]]
        story_start = int(sys.argv[3])
        story_end = int(sys.argv[4])

    for model_args in model_args_list:
        for seg_obj in segmentation_objects:
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
            print(model_args, seg_obj_repr(seg_obj))
            for story in story_info_list[story_start:story_end]:
                get_story_summary(story, model_args, seg_obj)
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")