from .model_logger.model_args import ModelArgs, call_model_for_summarization
from .chapter_segmentation_util import (
    SegmentationUtil, SegmentationObject, SceneSegmentation, ConstantSegmentation, NaiveSceneSegmentation, TextTiling, seg_obj_repr
)
    

def get_summary_from_segments(
        segment_type: str,
        segment_summaries: list[str], 
        chapter_summary_length: int, 
        summary_pov_details: str, 
        model_args: ModelArgs
    ) -> str:

    prompt = "Story:\n\n" + "\n".join(segment_summaries)
    system_prompt = " ".join(
            (
                f"The {segment_type} wise summary of the story is provided to following the Story: tag."
                f"Generate a short summary of this story under {chapter_summary_length} words.",
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

    return summary


def get_summary(
        chapter_title: str, 
        chapter_text: str, 
        summary_pov_details: str,
        segment_summary_length: int,
        chapter_summary_length: int, 
        model_args: ModelArgs,
        result_debug_folder: str,
        story_name: str,
        seg_obj: SegmentationObject
    ) -> tuple[str, str]:

    segmentation_type = seg_obj_repr(seg_obj)
    results_for_debug = f"{result_debug_folder}/results_debug_{model_args.name}_{segmentation_type}/{story_name}" 

    segmentation_util = SegmentationUtil(
        chapter_title=chapter_title,
        chapter_text=chapter_text,
        segment_summary_length=segment_summary_length,
        summary_pov_details=summary_pov_details,
        model_args=model_args,
        results_for_debug=results_for_debug,
        segmentation_method=seg_obj
    )

    segment_summaries = segmentation_util.get_segment_summaries()

    summary_from_segments = get_summary_from_segments("segment", segment_summaries, chapter_summary_length, summary_pov_details, model_args)

    return summary_from_segments

    

