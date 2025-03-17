import streamlit as st
import spacy

# Load spaCy model
spacy_model_path = "IE Model"
nlp_spacy = spacy.load(spacy_model_path)

# Initialize session state for storing user inputs
if "total_inputs" not in st.session_state:
    st.session_state.total_inputs = []

# Dictionary chuyển đổi mã thực thể sang tên đầy đủ và mô tả
ENTITY_DESCRIPTIONS = {
    "ORG": "Tên tổ chức",
    "LOC": "Địa điểm",
    "PER": "Tên người",
    "MISC": "Thực thể khác",
}

def extract_entity_groups(sentence):
    doc = nlp_spacy(sentence)
    entity_groups = []
    current_group = []
    current_label = None
    
    for ent in doc.ents:
        label = ent.label_
        
        if label.startswith("B-"):
            if current_group:
                entity_groups.append((current_label, " ".join(current_group)))
            current_group = [ent.text]
            current_label = label[2:]
        elif label.startswith("I-") and current_group:
            current_group.append(ent.text)
        else:
            if current_group:
                entity_groups.append((current_label, " ".join(current_group)))
                current_group = []
                current_label = None
    
    if current_group:
        entity_groups.append((current_label, " ".join(current_group)))
    
    return entity_groups

def extract_information_spacy(sentence):
    doc = nlp_spacy(sentence)
    extracted_info = {}
    for ent in doc.ents:
        extracted_info.setdefault(ent.label_, []).append(ent.text)
    return extracted_info

def format_output(text, entities, entity_groups):
    output = f"### Văn bản gốc:\n{text}\n\n"
    output += "### Danh sách cụm thực thể:\n"
    
    if entity_groups:
        for label, group in entity_groups:
            description = ENTITY_DESCRIPTIONS.get(label, "Thực thể khác")
            output += f"- **{description}**: {group}\n"
    else:
        output += "*Không có cụm thực thể nào được nhận diện.*\n"
    
    output += "\n### Kết quả nhận diện thực thể:\n"
    if entities:
        for entity_type, tokens in entities.items():
            unique_tokens = list(set(tokens))  # Loại bỏ trùng lặp
            description = ENTITY_DESCRIPTIONS.get(entity_type, "Thực thể khác")
            output += f"- **{description}**: {', '.join(unique_tokens)}\n"
    else:
        output += "*Không tìm thấy thực thể nào trong văn bản.*"
    
    return output

# Streamlit UI
st.title("🔎 Ứng dụng Nhận diện Thực thể (NER)")
st.write("Ứng dụng giúp trích xuất thông tin quan trọng từ văn bản bằng mô hình AI.")

user_input = st.text_area("Nhập văn bản cần phân tích:", "")

if st.button("Nhận diện thực thể"):
    if user_input:
        st.session_state.total_inputs.append(user_input)
        
        # Xử lý mô hình spaCy
        entity_groups = extract_entity_groups(user_input)
        extracted_entities_spacy = extract_information_spacy(user_input)
        formatted_text_spacy = format_output(user_input, extracted_entities_spacy, entity_groups)

        # Hiển thị kết quả
        st.subheader("📌 Kết quả từ mô hình AI:")
        st.markdown(formatted_text_spacy)
        
        # Lưu cả văn bản nhập và kết quả nhận dạng vào tệp
        all_inputs_with_entities = []
        for text in st.session_state.total_inputs:
            entity_groups = extract_entity_groups(text)
            extracted_entities_spacy = extract_information_spacy(text)
            formatted_text_spacy = format_output(text, extracted_entities_spacy, entity_groups)
            all_inputs_with_entities.append(formatted_text_spacy)
        
        # Tạo tệp để tải xuống
        all_inputs_with_entities_text = "\n\n".join(all_inputs_with_entities)
        
        st.download_button(
            label="📥 Tải xuống kết quả nhận diện",
            data=all_inputs_with_entities_text,
            file_name="ket_qua_ner.txt",
            mime="text/plain"
        )
    else:
        st.warning("⚠️ Vui lòng nhập văn bản trước khi phân tích.")