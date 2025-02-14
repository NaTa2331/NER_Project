import streamlit as st
from transformers import AutoModelForTokenClassification, AutoTokenizer
import torch
import spacy

# Load Transformer-based model
model_path_transformer = "./saved_model_transformer_T2"
model_transformer = AutoModelForTokenClassification.from_pretrained(model_path_transformer)
tokenizer_transformer = AutoTokenizer.from_pretrained(model_path_transformer)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model_transformer.to(device)

# Load spaCy model
spacy_model_path = "IE Model"
nlp_spacy = spacy.load(spacy_model_path)

# Define label mapping for Transformer model
label_list = ['O', 'B-MISC', 'I-MISC', 'B-PER', 'I-PER', 'B-LOC', 'I-LOC', 'B-ORG', 'I-ORG']
id_to_label = {i: label for i, label in enumerate(label_list)}

# Initialize session state for storing user inputs
if "total_inputs" not in st.session_state:
    st.session_state.total_inputs = []

def extract_information_transformer(sentence):
    tokenized_inputs = tokenizer_transformer(
        [sentence], return_tensors="pt", padding=True, truncation=True, max_length=128
    )
    tokenized_inputs = {key: value.to(device) for key, value in tokenized_inputs.items()}

    with torch.no_grad():
        outputs = model_transformer(**tokenized_inputs)
    predictions = outputs.logits.argmax(axis=2)

    tokens = tokenizer_transformer.convert_ids_to_tokens(tokenized_inputs['input_ids'][0])
    pred_labels = [id_to_label[p.item()] for p in predictions[0]]

    extracted_info = {}
    for token, label in zip(tokens, pred_labels):
        if label != "O":
            entity_type = label.split("-")[-1]
            extracted_info.setdefault(entity_type, []).append(token)
    return extracted_info

def extract_information_spacy(sentence):
    doc = nlp_spacy(sentence)
    extracted_info = {}
    for ent in doc.ents:
        extracted_info.setdefault(ent.label_, []).append(ent.text)
    return extracted_info

def format_output(text, entities):
    output = text + "\n"
    for entity_type, tokens in entities.items():
        output += f"<{entity_type}> {' '.join(tokens)}\n"
    return output

# Streamlit UI
st.title("Named Entity Recognition (NER) App")
user_input = st.text_area("Nhập văn bản:", "")

if st.button("Nhận diện thực thể"):
    if user_input:
        st.session_state.total_inputs.append(user_input)
        
        # Xử lý mô hình Transformer
        extracted_entities_transformer = extract_information_transformer(user_input)
        formatted_text_transformer = format_output(user_input, extracted_entities_transformer)

        # Xử lý mô hình spaCy
        extracted_entities_spacy = extract_information_spacy(user_input)
        formatted_text_spacy = format_output(user_input, extracted_entities_spacy)

        # Hiển thị kết quả
        st.subheader("Kết quả từ mô hình Transformer:")
        st.text_area("Transformer Output:", formatted_text_transformer, height=200)
        
        st.subheader("Kết quả từ mô hình spaCy:")
        st.text_area("spaCy Output:", formatted_text_spacy, height=200)
        
        # Lưu cả văn bản nhập và kết quả nhận dạng vào tệp
        all_inputs_with_entities = []
        for text in st.session_state.total_inputs:
            all_inputs_with_entities.append(f"Văn bản: {text}\n")
            extracted_entities_transformer = extract_information_transformer(text)
            formatted_text_transformer = format_output(text, extracted_entities_transformer)
            all_inputs_with_entities.append(f"Kết quả Transformer: {formatted_text_transformer}\n")
            
            extracted_entities_spacy = extract_information_spacy(text)
            formatted_text_spacy = format_output(text, extracted_entities_spacy)
            all_inputs_with_entities.append(f"Kết quả spaCy: {formatted_text_spacy}\n")
        
        # Tạo tệp để tải xuống
        all_inputs_with_entities_text = "\n".join(all_inputs_with_entities)
        
        st.download_button(
            label="Tải xuống tất cả văn bản và kết quả nhận dạng",
            data=all_inputs_with_entities_text,
            file_name="all_inputs_with_entities.txt",
            mime="text/plain"
        )
    else:
        st.warning("Vui lòng nhập văn bản.")

