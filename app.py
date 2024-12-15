from PIL import Image
import gradio as gr

from minerva import Minerva
from formatter import AutoGenFormatter


title = "Minerva: AI Guardian for Scam Protection"
description = """
              Built with AutoGen 0.4.0 and OpenAI. </br> 
              Analysis might take up to 30s. </br>
              https://github.com/dcarpintero/minerva
              """
inputs = gr.components.Image()
outputs = [
    gr.components.Textbox(label="Analysis Result"),
    gr.HTML(label="Agentic Workflow (Streaming)")
]
examples = "samples"

model = Minerva()
formatter = AutoGenFormatter()

def to_html(texts):
    formatted_html = ''
    for text in texts:
        formatted_html += text.replace('\n', '<br>') + '<br>'
    return f'<pre>{formatted_html}</pre>'

async def predict(img):
    try:
        img = Image.fromarray(img)

        stream = await model.analyze(img)

        streams = []
        messages = []
        async for s in stream:
            msg = await formatter.to_output(s)
            streams.append(s)
            messages.append(msg)
            yield ["", to_html(messages)]
        
        if streams[-1]:
            prediction = streams[-1].messages[-1].content
        else:
            prediction = "No analysis available. Try again later."

        await model.reset()
        yield [prediction, to_html(messages)]

    except Exception as e:
        print(e)
        yield ["Error during analysis. Try again later.", ""]


with gr.Blocks() as demo:
    with gr.Tab("Minerva: AI Guardian for Scam Protection"):
        gr.Interface(
            fn=predict,
            inputs=inputs,
            outputs=outputs,
            examples=examples,
            description=description,
        ).queue(default_concurrency_limit=5)

demo.launch()