from utils import get_metrics
from data.story_info import Story, story_info_list
from summarization_process.model_logger import ModelArgs, ModelReplicateArgs, ModelOpenAIArgs
from summarization_process.segmented_summarization import SegmentationObject, SceneSegmentation, ConstantSegmentation, seg_obj_repr
from utils.constants import result_parent_folder, stories_folder
from tqdm import tqdm
import os, sys
from generate_story_summary import model_args_list, segmentation_objects
import pandas as pd
import itertools
from collections import defaultdict


BOOKSUM = "BOOKSUM"
WATTPAD = "WATTPAD"


def get_reference_labels_for_wattpad(story_name, chp_file, wattpad_summary_dir) -> list[str]:

    def get_chp_num_for_story(chp):
        n = chp.split("chp")[-1]
        if n.startswith("_"):
            n = n[1:]
        return int(n)

    def get_chp_num_for_summary(chp):
        n = chp.split("_")[1]
        return int(n)

    chp_num_story = get_chp_num_for_story(chp_file)

    references = []
    for chp in os.listdir(wattpad_summary_dir+"/"+story_name):
        if chp_num_story == get_chp_num_for_summary(chp):
            with open(wattpad_summary_dir+"/"+story_name+"/"+chp, "r", encoding='cp1252') as f:
                #print(chp_file, story_name+"/"+chp)
                references.append(f.read())

    return references


def get_reference_labels_for_booksum(story_name, chp_file, booksum_summary_dir) -> list[str]:
    references = []
    for chp in os.listdir(story_dir:=booksum_summary_dir+"/"+story_name):
        if chp_file == chp:
            for chp_sub_file in os.listdir(chp_folder:=story_dir+"/"+chp):
                with open(chp_folder+"/"+chp_sub_file, "r") as f:
                    references.append(f.read())
    return references


def evaluate_chapter_summary(
        story: Story, 
        chp_file: str,
        reference_labels: list[str], 
        model_args: ModelArgs, 
        seg_obj: SegmentationObject = None
    ) -> dict[str, float]:

    segmentation_type = seg_obj_repr(seg_obj)
    results_dir = f"{result_parent_folder}/results__{model_args.name}_{segmentation_type}/{story.name}"

    summary_file_name = results_dir+ "/" + chp_file + "/" + chp_file + ".txt"

    metrics = get_metrics()
    results = {}

    if not os.path.isfile(summary_file_name):
        for metric_name, metric_fn in metrics.items():
            results[metric_name] = None
        return results

    with open(summary_file_name, "r") as fw:
        summary = fw.read()

    if len(summary.strip()) == 0:
        for metric_name, metric_fn in metrics.items():
            results[metric_name] = None
        return results

    
    for metric_name, metric_fn in metrics.items():
        results[metric_name] = metric_fn(reference_labels, summary)
    return results


def main(data_source: str):
    metric_names = list(get_metrics().keys())
    result_sheets = {k: defaultdict(list) for k in metric_names}

    wattpad_summary_dir = "data/human_wattpad_summaries"
    booksum_summary_dir = "data/booksum_summaries"

    wattpad_stories = set(os.listdir(wattpad_summary_dir))
    booksum_stories = set(os.listdir(booksum_summary_dir))

    stories_set = booksum_stories if data_source == BOOKSUM else wattpad_stories

    for story in story_info_list:

        if (story.name not in stories_set):
            continue

        is_wattpad_story = story.name in wattpad_stories

        for chp_file in tqdm(os.listdir(f"{stories_folder}/{story.name}")):

            if is_wattpad_story:
                reference_labels = get_reference_labels_for_wattpad(story.name, chp_file, wattpad_summary_dir)
            else:
                reference_labels = get_reference_labels_for_booksum(story.name, chp_file, booksum_summary_dir)

            if len(reference_labels) == 0:
                continue

            for metric in result_sheets:
                result_sheets[metric]['stories'].append(f"{story.name}/{chp_file}")

            for model_args, seg_obj in itertools.product(model_args_list, segmentation_objects):
                method_name = model_args.name + "/" + seg_obj_repr(seg_obj) 
                scores = evaluate_chapter_summary(story, chp_file, reference_labels, model_args, seg_obj)
                for metric, score in scores.items():
                    result_sheets[metric][method_name].append(score)


    writer = pd.ExcelWriter('results5.xlsx', engine='xlsxwriter')
    for metric, sheet in result_sheets.items():
        df = pd.DataFrame(sheet)
        df.to_excel(writer, sheet_name=metric)
    writer.close()

if __name__ == '__main__':

    if len(sys.argv) == 2:
        data_source = sys.argv[1]
        if data_source in (BOOKSUM, WATTPAD):
            main(data_source)



    