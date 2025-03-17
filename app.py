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
    "B-ORG": "Tên tổ chức (Bắt đầu thực thể)",
    "I-ORG": "Tên tổ chức (Tiếp tục thực thể)",
    "B-LOC": "Địa điểm (Bắt đầu thực thể)",
    "I-LOC": "Địa điểm (Tiếp tục thực thể)",
    "B-PER": "Tên người (Bắt đầu thực thể)",
    "I-PER": "Tên người (Tiếp tục thực thể)",
    "B-MISC": "Thực thể khác (Bắt đầu thực thể)",
    "I-MISC": "Thực thể khác (Tiếp tục thực thể)",
    "O": "Không thuộc thực thể nào",
}

def extract_information_spacy(sentence):
    """Trích xuất thực thể từ văn bản bằng spaCy."""
    doc = nlp_spacy(sentence)
    extracted_info = {}
    for ent in doc.ents:
        extracted_info.setdefault(ent.label_, []).append(ent.text)
    return extracted_info

def format_entity_list(entities):
    """Tạo danh sách thực thể tóm tắt."""
    entity_summary = "### 📋 Danh sách thực thể nhận diện được:\n"
    unique_entities = set()  # Sử dụng set để loại bỏ trùng lặp
    for entity_type, tokens in entities.items():
        unique_tokens = list(set(tokens))
        entity_summary += f"- **{ENTITY_DESCRIPTIONS.get(entity_type, 'Thực thể khác')}**: {', '.join(unique_tokens)}\n"
        unique_entities.update(unique_tokens)

    if not unique_entities:
        entity_summary += "*Không tìm thấy thực thể nào.*\n"

    return entity_summary

def format_detailed_output(text, entities):
    """Tạo phân tích chi tiết về từng thực thể trong văn bản."""
    output = f"### 📜 Văn bản gốc:\n{text}\n\n"
    output += "### 🔍 Phân tích chi tiết:\n"
    
    if entities:
        for entity_type, tokens in entities.items():
            unique_tokens = list(set(tokens))
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
        extracted_entities_spacy = extract_information_spacy(user_input)

        # Hiển thị danh sách thực thể trước
        entity_list_output = format_entity_list(extracted_entities_spacy)
        st.subheader("📌 Kết quả nhận diện:")
        st.markdown(entity_list_output)

        # Hiển thị phân tích chi tiết sau
        detailed_output = format_detailed_output(user_input, extracted_entities_spacy)
        st.subheader("📊 Phân tích chi tiết:")
        st.markdown(detailed_output)
        
        # Lưu cả văn bản nhập và kết quả nhận dạng vào tệp
        all_inputs_with_entities = []
        for text in st.session_state.total_inputs:
            extracted_entities_spacy = extract_information_spacy(text)
            entity_list_output = format_entity_list(extracted_entities_spacy)
            detailed_output = format_detailed_output(text, extracted_entities_spacy)
            all_inputs_with_entities.append(entity_list_output + "\n" + detailed_output)
        
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
