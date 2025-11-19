import gradio as gr
import google.generativeai as genai

# Configure Gemini API
genai.configure(api_key="API_KEY")

model = genai.GenerativeModel("gemini-2.5-flash")

def evaluate_answer(question, reference, student):
    prompt = f"""
You are an automatic short-answer feedback generator.  

Given a question, a student answer, and a reference answer. Evaluate student answers against a reference answer for correctness, providing labels (correct/partially correct/incorrect) and constructive feedback in about 3-4 lines.

Ensure feedback guides the learner without invoking negative emotions and does not reference the provided reference answer.

Format output as a json object with level_of_correctness as one key and feedback as another.

Question : {question}

Reference Answer : {reference}

Student Answer : {student}

Output :    
"""

    response = model.generate_content(prompt)
    text = response.text

    # Very simple extraction (assuming Gemini returns proper JSON)
    try:
        import json
        data = json.loads(text.replace('json','').replace('```','').replace('\n',''))
        return data.get("level_of_correctness", ""), data.get("feedback", "")
    except:
        # fallback: return raw text
        return "Could not parse JSON", text

# Gradio UI
with gr.Blocks() as app:
    gr.Markdown("### BharatGen Acharya - AI Answer Evaluator")

    q = gr.Textbox(label="Question")
    ref = gr.Textbox(label="Reference Answer")
    stu = gr.Textbox(label="Student Answer")

    level = gr.Textbox(label="Level of Correctness")
    fb = gr.Textbox(label="Feedback")

    btn = gr.Button("Evaluate")

    btn.click(evaluate_answer, inputs=[q, ref, stu], outputs=[level, fb])

app.launch()
