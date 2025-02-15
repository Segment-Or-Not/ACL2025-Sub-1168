from dataclasses import dataclass
from . import openai_logger
from . import replicate_logger
import re

@dataclass
class ModelArgs:
    name: str
    hf_name: str

    def __init__(self, name:str, hf_name:str = None):
        self.name = name
        self.hf_name = hf_name

@dataclass
class ModelReplicateArgs(ModelArgs):
    replicate_name: str

    def __init__(self, name:str, replicate_name: str, hf_name:str = None):
        super().__init__(name, hf_name)
        self.replicate_name = replicate_name

@dataclass
class ModelOpenAIArgs(ModelArgs):
    openai_name: str

    def __init__(self, name:str, openai_name: str, hf_name:str = None):
        super().__init__(name, hf_name)
        self.openai_name = openai_name
        


def call_model_for_summarization(model_args: ModelArgs, prompt: str, system_prompt: str, temperature: int):

    if type(model_args) == ModelReplicateArgs:

        input_for_model = {
            "prompt": prompt,
            "system_prompt": system_prompt,
            "temperature": temperature
        }

        response = replicate_logger.run(model_args.replicate_name, input=input_for_model)
        result = "".join(response)
        result = result.split("\n\n")[-1]

    elif type(model_args) == ModelOpenAIArgs:

        completion = openai_logger.chat_completions(
            model=model_args.openai_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature= temperature
        )

        result = completion.choices[0].message.content

    return result


def call_model_for_naive_scene_boundary_identification(
        model_args: ModelArgs, previous_context: list[str], following_context: list[str], temperature: int
    ) -> tuple[str, str, str]:
    
    prompt = "\n".join((
        "Previous Context:",
        " ".join(previous_context) + "\n",
        "Following Context:",
        " ".join(following_context) + "\n",
    ))

    system_prompt = "\n".join((
        "Scene Boundaries separate SCENE-TO-SCENE, SCENE-TO-NONSCENE or NONSCENE-TO-SCENE.",

        " ".join((
            "\nI will pass you the previous context after the 'Previous Context:' tag",
            "and it's following context after the 'Following Context:' tag.",
            "Answer whether there is a scene boundary between the previous context and following context.",
            "Remember, if there is a scene boundary between the previous context and the following context,"
            "that indicates, the previous SCENE/NON-SCENE ended at previous context and",
            "a new SCENE/NON-SCENE started at the following context.\n" #Intetionally left out comma here
            "Provide your reasoning after the 'Reasoning:' tag, followed by a single word answer",
            "'Yes' or 'No' following the 'Boundary:' tag."
        ))
    ))

    if type(model_args) == ModelReplicateArgs:

        input_for_model = {
            "prompt": prompt,
            "system_prompt": system_prompt,
            "temperature": temperature
        }

        response = replicate_logger.run(model_args.replicate_name, input=input_for_model)
        result = "".join(response)

    elif type(model_args) == ModelOpenAIArgs:

        completion = openai_logger.chat_completions(
            model=model_args.openai_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature= temperature
        )

        result = completion.choices[0].message.content

    try:
        result1 = result.split("Reasoning:", maxsplit=1)[-1]
        reasoning, answer = result1.split("Boundary:", maxsplit=1)
    except:
        reasoning, answer = "Failed_Case>>>"+result, "No"
    return reasoning, answer

def call_model_for_scene_boundary_identification(
        model_args: ModelArgs, previous_context: list[str], following_context: list[str], temperature: int
    ) -> tuple[str, str, str]:
    
    prompt = "\n".join((
        "Previous Context:",
        " ".join(previous_context) + "\n",
        "Following Context:",
        " ".join(following_context) + "\n",
    ))

    system_prompt = "\n".join((
        "A scene a segment of the discourse in a narrative such that",
        "\ta) time is more or less similar",
        "\tb) place stays relatively the same",
        "\tc) it centers around a particular set of actions",
        "\td) character configuration does not change",

        "\nNon-scenes are text passages that are not spatially and temporally concreted or do not contain any acting characters, for example",
        "\ta) Passages with accelerated speed of narration",
        "\tb) Passages with long descriptions",
        "\tc) Scenic passage whose text indicates iterativity",

        " ".join((
            "\nScene Boundary are sentences that separate SCENE-TO-SCENE, SCENE-TO-NONSCENE or NONSCENE-TO-SCENE.", 
            "A sentence that starts a new scene after a segment that is classified as a non-scene would be labelled as NONSCENE-TO-SCENE."
        )),

        "\nIf the changes trigger changes in the plot of the narrative.",
        "\tyes: scene change is likely.",
        "\tno: No scene change",

        "\nHere are some additional features of scene change based on importance:", 
        "\t1. Scene change if a large amount of text is spent describing the flashforward and flashback",
        "\t2. Scene change if there is a major change in narrative pace",
        "\t3. Scene change if a new set of actions start and do not belong to the previous set of actions",
        "\t4. Scene change if the previous characters are not the focus anymore",
        "\t5. No scene change if the previous characters remain important and the course of actions essentially remains the same",
        "\t6. No scene change if the new character does not shape the course of actions",
        "\t7. No scene change if one or more characters exit but the course of actions stays the same.",
        "\t8. Scene change if the course of actions changes because of the exiting characters",
        "\t9. No scene change if several rooms can be combined to one larger room like a hotel",

        " ".join((
            "\nIn many cases, an intuitive test is helpful to detect a scene.", 
            "Imagine the passage in question as a movie and ask yourself,", 
            "whether it could be transposed to one movie scene (or a movie scene at all).",
            "The boundaries of the scene are the points where a fade out (or fade in) could be inserted."
        )),

        " ".join((
            "\nI will pass you the previous context after the 'Previous Context:' tag",
            "and it's following context after the 'Following Context:' tag.",
            "Answer whether there is a scene boundary between the previous context and following context.",
            "Remember, if there is a scene boundary between the previous context and the following context,"
            "that indicates, the previous SCENE/NON-SCENE ended at previous context and",
            "a new SCENE/NON-SCENE started at the following context.\n" #Intetionally left out comma here
            "Provide your reasoning after the 'Reasoning:' tag, followed by a single word answer",
            "'Yes' or 'No' following the 'Boundary:' tag."
        ))
    ))

    if type(model_args) == ModelReplicateArgs:

        input_for_model = {
            "prompt": prompt,
            "system_prompt": system_prompt,
            "temperature": temperature
        }

        response = replicate_logger.run(model_args.replicate_name, input=input_for_model)
        result = "".join(response)

    elif type(model_args) == ModelOpenAIArgs:

        completion = openai_logger.chat_completions(
            model=model_args.openai_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature= temperature
        )

        result = completion.choices[0].message.content

    result1 = result.split("Reasoning:", maxsplit=1)[-1]
    reasoning, answer = result1.split("Boundary:", maxsplit=1)
    return reasoning, answer