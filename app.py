import gradio as gr
import plotly.express as px
import pandas as pd
from src.parser_engine import parser_engine

def process_las(file):
    if file is None:
        return None, "Please upload a .las file.", ""
    
    try:
        content = open(file.name, "r").read()
        df, meta = parser_engine.parse_las(content)
        
        # Create plot (first 3 curves)
        curves_to_plot = meta["curves"][:3]
        fig = px.line(df.reset_index(), x="DEPTH" if "DEPTH" in df.index.names else df.columns[0], 
                     y=curves_to_plot, title=f"Well Log: {meta['well_name']}")
        
        # Analyze
        analysis = parser_engine.analyze_well_potential(meta, df.describe().to_string())
        
        meta_str = f"**Well**: {meta['well_name']}\n**Company**: {meta['company']}\n**Curves**: {', '.join(meta['curves'])}"
        
        return fig, meta_str, analysis
    except Exception as e:
        return None, f"### Error Processing LAS\n{str(e)}", ""

# ============================================
# GRADIO UI
# ============================================

with gr.Blocks(title="LAS Parser", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # LAS Parser
    ### Well Log Data Parser
    
    Automated Log ASCII Standard (LAS) parsing with AI-driven formation analysis.
    """)
    
    with gr.Row():
        with gr.Column():
            file_input = gr.File(label="Upload .las File", file_types=[".las"])
            parse_btn = gr.Button("Parse & Analyze", variant="primary")
            meta_output = gr.Markdown(label="Well Metadata")
            
        with gr.Column():
            plot_output = gr.Plot(label="Log Visualization")
            
    analysis_output = gr.Markdown(label="Petrophysical Analysis")
    
    parse_btn.click(
        fn=process_las,
        inputs=[file_input],
        outputs=[plot_output, meta_output, analysis_output]
    )
    
    gr.Markdown("""
    ---
    **Tech Stack:** lasio • Mistral-7B • Plotly • Gradio
    
    **Author:** [David Fernandez](https://davidfernandez.dev) | AI Engineer
    """)

if __name__ == "__main__":
    demo.launch()
