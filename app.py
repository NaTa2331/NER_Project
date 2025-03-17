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
    "B-ORG": "Tên tổ chức",
    "I-ORG": "Tên tổ chức",
    "B-LOC": "Địa điểm",
    "I-LOC": "Địa điểm",
    "B-PER": "Tên người",
    "I-PER": "Tên người",
    "B-MISC": "Thực thể khác",
    "I-MISC": "Thực thể khác",
}

def extract_entities(sentence):
    doc = nlp_spacy(sentence)
    entities = []
    current_entity = ""
    current_label = ""
    
    for token in doc:
        if token.ent_iob_ == "B":
            if current_entity:
                entities.append((current_label, current_entity.strip()))
            current_entity = token.text
            current_label = token.ent_type_
        elif token.ent_iob_ == "I" and token.ent_type_ == current_label:
            current_entity += " " + token.text
        else:
            if current_entity:
                entities.append((current_label, current_entity.strip()))
                current_entity = ""
                current_label = ""
    
    if current_entity:
        entities.append((current_label, current_entity.strip()))
    
    return entities

def format_output(text, entities):
    output = f"### Văn bản gốc:\n{text}\n\n"
    output += "### Danh sách thực thể nhận diện:\n"
    
    if entities:
        entity_list = [f"- {ENTITY_DESCRIPTIONS.get(label, 'Thực thể khác')}: {entity}" for label, entity in entities]
        output += "\n".join(entity_list) + "\n\n"
        
        output += "### Kết quả phân tích chi tiết:\n"
        grouped_entities = {}
        for label, entity in entities:
            grouped_entities.setdefault(label, []).append(entity)
        
        for entity_type, tokens in grouped_entities.items():
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
        extracted_entities = extract_entities(user_input)
        formatted_text = format_output(user_input, extracted_entities)

        # Hiển thị kết quả
        st.subheader("📌 Kết quả từ mô hình AI:")
        st.markdown(formatted_text)
        
        # Lưu cả văn bản nhập và kết quả nhận dạng vào tệp
        all_inputs_with_entities = []
        for text in st.session_state.total_inputs:
            extracted_entities = extract_entities(text)
            formatted_text = format_output(text, extracted_entities)
            all_inputs_with_entities.append(formatted_text)
        
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