import lasio
import pandas as pd
import io
from huggingface_hub import InferenceClient
import os

# Constants
HF_TOKEN = os.environ.get("HF_TOKEN")
MODEL_ID = "mistralai/Mistral-7B-Instruct-v0.3"

class LASParserEngine:
    def __init__(self):
        self.client = InferenceClient(model=MODEL_ID, token=HF_TOKEN)

    def parse_las(self, file_content):
        # lasio needs a file-like object
        f = io.StringIO(file_content)
        las = lasio.read(f)
        df = las.df()
        
        # Metadata
        metadata = {
            "well_name": las.well.WELL.value,
            "field": las.well.FLD.value,
            "company": las.well.COMP.value,
            "curves": [c.mnemonic for c in las.curves]
        }
        
        return df, metadata

    def analyze_well_potential(self, metadata, df_summary):
        prompt = f"""You are a Senior Petrophysicist. Analyze this well log metadata and summary data. 
Identify the primary formations and potential hydrocarbon zones based on the available curves.

METADATA:
{metadata}

SUMMARY STATS:
{df_summary}

PETROPHYSICAL ANALYSIS:"""

        response = self.client.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800
        )
        return response.choices[0].message.content

parser_engine = LASParserEngine()
