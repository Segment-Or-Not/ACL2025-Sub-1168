#  Can Large Language Models Summarize Long Narratives? A Study of Holistic versus Segmented Story Summarization

The booksum stories can be collected from https://www.gutenberg.org/

We collected the booksum summaries from 
- https://huggingface.co/datasets/kmfoda/booksum
- https://huggingface.co/datasets/ubaada/booksum-complete-cleaned

Following that we manually cleaned the summaries and did manual inspection to fix any misaligned summaries.

For scrapping wattpad stories, we used the following github repo
- https://github.com/Architrixs/Wattpad2Epub (Thank you Archit aka Architrixs)
- The wattpad scrapping URLs are,
    - "https://www.wattpad.com/apiv2/"
    - "https://www.wattpad.com/api/v3/"

We ran our Prolific experiment, to collect human written summaries for the wattpad stories. The summaries has been provided in the folder data/human_wattpad_summaries
