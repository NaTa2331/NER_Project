import streamlit as st
import spacy

# Load spaCy model
spacy_model_path = "IE Model"
nlp_spacy = spacy.load(spacy_model_path)

# Initialize session state for storing user inputs
if "total_inputs" not in st.session_state:
    st.session_state.total_inputs = []

def extract_information_spacy(sentence):
    doc = nlp_spacy(sentence)
    extracted_info = {}
    for ent in doc.ents:
        extracted_info.setdefault(ent.label_, []).append(ent.text)
    return extracted_info

def format_output(text, entities):
    output = f"Văn bản gốc: {text}\n\n"
    for entity_type, tokens in entities.items():
        unique_tokens = list(set(tokens))  # Loại bỏ trùng lặp
        output += f"{entity_type}: {', '.join(unique_tokens)}\n"
    return output

# Streamlit UI
st.title("Named Entity Recognition (NER) App")
user_input = st.text_area("Nhập văn bản:", "")

if st.button("Nhận diện thực thể"):
    if user_input:
        st.session_state.total_inputs.append(user_input)
        
        # Xử lý mô hình spaCy
        extracted_entities_spacy = extract_information_spacy(user_input)
        formatted_text_spacy = format_output(user_input, extracted_entities_spacy)

        # Hiển thị kết quả
        st.subheader("Kết quả từ mô hình spaCy:")
        st.text_area("spaCy Output:", formatted_text_spacy, height=200)
        
        # Lưu cả văn bản nhập và kết quả nhận dạng vào tệp
        all_inputs_with_entities = []
        for text in st.session_state.total_inputs:
            extracted_entities_spacy = extract_information_spacy(text)
            formatted_text_spacy = format_output(text, extracted_entities_spacy)
            all_inputs_with_entities.append(formatted_text_spacy)
        
        # Tạo tệp để tải xuống
        all_inputs_with_entities_text = "\n\n".join(all_inputs_with_entities)
        
        st.download_button(
            label="Tải xuống tất cả văn bản và kết quả nhận dạng",
            data=all_inputs_with_entities_text,
            file_name="all_inputs_with_entities.txt",
            mime="text/plain"
        )
    else:
        st.warning("Vui lòng nhập văn bản.")
