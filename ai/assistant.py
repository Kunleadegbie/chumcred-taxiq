import os
import openai
import streamlit as st
from ai.prompts import vat_analysis_prompt

openai.api_key = os.getenv("OPENAI_API_KEY")

def analyze(df):
    prompt = vat_analysis_prompt(df.to_string())

    res = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return res.choices[0].message.content