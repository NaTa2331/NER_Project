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
    "LOC": "Địa điểm",
    "ORG": "Tên tổ chức",
    "PER": "Tên người",
    "MISC": "Thực thể khác"
}

def extract_information_spacy(sentence):
    doc = nlp_spacy(sentence)
    extracted_info = {"LOC": [], "ORG": [], "PER": [], "MISC": []}
    
    prev_label = None
    entity_text = ""
    
    for ent in doc.ents:
        if ent.label_ in extracted_info:
            if prev_label == ent.label_:  # Tiếp tục cùng một thực thể
                entity_text += " " + ent.text
            else:  # Bắt đầu thực thể mới
                if entity_text:
                    extracted_info[prev_label].append(entity_text.strip())
                entity_text = ent.text
                prev_label = ent.label_
    
    # Thêm thực thể cuối cùng nếu có
    if entity_text and prev_label:
        extracted_info[prev_label].append(entity_text.strip())
    
    # Loại bỏ trùng lặp
    for key in extracted_info:
        extracted_info[key] = list(set(extracted_info[key]))
    
    return extracted_info

def format_output(text, entities):
    output = f"### Văn bản gốc:\n{text}\n\n"
    output += "### Kết quả nhận diện thực thể:\n"
    
    if any(entities.values()):
        for entity_type, tokens in entities.items():
            if tokens:
                description = ENTITY_DESCRIPTIONS.get(entity_type, "Thực thể khác")
                output += f"- **{description}**: {', '.join(tokens)}\n"
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
        extracted_entities_spacy = extract_information_spacy(user_input)
        formatted_text_spacy = format_output(user_input, extracted_entities_spacy)

        # Hiển thị kết quả
        st.subheader("📌 Kết quả từ mô hình AI:")
        st.markdown(formatted_text_spacy)
        
        # Lưu cả văn bản nhập và kết quả nhận dạng vào tệp
        all_inputs_with_entities = []
        for text in st.session_state.total_inputs:
            extracted_entities_spacy = extract_information_spacy(text)
            formatted_text_spacy = format_output(text, extracted_entities_spacy)
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