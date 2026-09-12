import streamlit as st
import json
import re
import os
from openai import OpenAI

st.set_page_config(page_title="AI Roadmap Generator", page_icon="🗺️", layout="wide")

# Retrieve key safely from Streamlit secrets
api_key = st.secrets.get("XAI_API_KEY", "")

st.title("🗺️ AI Learning Roadmap Generator")

with st.sidebar:
    st.header("Input Parameters")
    domain = st.text_input("Target Domain / Skill", placeholder="e.g., Computer Systems")
    skill_level = st.selectbox("Current Skill Level", ["Absolute Beginner", "Intermediate", "Advanced"])
    duration = st.text_input("Time Available", value="1 Month")
    generate_btn = st.button("Generate Roadmap", type="primary")

def generate_roadmap(domain, skill_level, duration):
    if not api_key:
        return "❌ Error: API key not found in secrets."

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1"
    )

    system_prompt = (
        "You are an expert curriculum designer. Create a structured learning roadmap. "
        "Do NOT use raw control characters or literal multi-line breaks inside JSON string values. "
        "Return ONLY a single valid JSON object matching this structure:\n"
        "{\n"
        '  "title": "Roadmap Title",\n'
        '  "summary": "Overview strategy",\n'
        '  "prerequisites": ["Skill 1"],\n'
        '  "phases": [\n'
        '    {\n'
        '      "phase_name": "Phase 1",\n'
        '      "timeframe": "Week 1",\n'
        '      "topics": ["Topic A"],\n'
        '      "projects": ["Project A"],\n'
        '      "resources": ["Resource A"]\n'
        '    }\n'
        '  ]\n'
        "}"
    )

    user_prompt = f"Domain: {domain}\nSkill Level: {skill_level}\nTime Available: {duration}"

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2
        )

        raw_json = response.choices[0].message.content.strip()
        if raw_json.startswith("```"):
            raw_json = raw_json.split("\n", 1)[1].rsplit("\n", 1)[0]
        
        clean_json = re.sub(r'[\x00-\x09\x0B-\x1F\x7F]', '', raw_json)
        return json.loads(clean_json, strict=False)

    except Exception as e:
        return f"❌ Error: {str(e)}"

if generate_btn:
    if not domain.strip():
        st.warning("Please enter a domain or field.")
    else:
        with st.spinner("Generating roadmap..."):
            roadmap_data = generate_roadmap(domain, skill_level, duration)

        if isinstance(roadmap_data, str):
            st.error(roadmap_data)
        else:
            st.header(f"🚀 {roadmap_data.get('title', 'Learning Roadmap')}")
            st.write(f"**Overview:** {roadmap_data.get('summary', '')}")
            
            st.subheader("📋 Prerequisites")
            for req in roadmap_data.get('prerequisites', []):
                st.write(f"- {req}")

            st.divider()

            for idx, phase in enumerate(roadmap_data.get('phases', []), 1):
                st.subheader(f"Phase {idx}: {phase.get('phase_name', '')} ({phase.get('timeframe', '')})")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write("**Topics to Master:**")
                    for t in phase.get('topics', []):
                        st.write(f"- {t}")
                with col2:
                    st.write("**Projects:**")
                    for p in phase.get('projects', []):
                        st.write(f"- 🛠️ {p}")
                with col3:
                    st.write("**Resources:**")
                    for r in phase.get('resources', []):
                        st.write(f"- 📚 {r}")
                st.divider()