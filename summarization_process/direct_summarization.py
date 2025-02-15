from .model_logger.model_args import ModelArgs, call_model_for_summarization

def get_summary(chapter_text: str, summary_pov_details, chapter_summary_length, model_args: ModelArgs):

    prompt = "Story:\n\n" + chapter_text
    system_prompt = " ".join(
            (
                "The story is provided to following the Story: tag.",
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