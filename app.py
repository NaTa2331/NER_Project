import streamlit as st
import spacy

# Load spaCy model
spacy_model_path = "IE Model"
nlp_spacy = spacy.load(spacy_model_path)

# Initialize session state for storing user inputs
if "total_inputs" not in st.session_state:
    st.session_state.total_inputs = []

# Dictionary chuyển đổi mã thực thể sang tên đầy đủ
ENTITY_DESCRIPTIONS = {
    "ORG": "Tên tổ chức",
    "LOC": "Địa điểm",
    "PER": "Tên người",
    "MISC": "Thực thể khác",
}

def extract_entities(sentence):
    """Nhóm các thực thể liên tiếp lại thành cụm hoàn chỉnh."""
    doc = nlp_spacy(sentence)
    entities = []
    current_entity = None

    for ent in doc.ents:
        entity_label = ent.label_.replace("B-", "").replace("I-", "")

        if current_entity and current_entity["type"] == entity_label:
            current_entity["text"] += " " + ent.text  # Ghép nối thực thể tiếp theo
        else:
            if current_entity:
                entities.append(current_entity)  # Lưu thực thể trước đó
            current_entity = {"type": entity_label, "text": ent.text}  # Khởi tạo thực thể mới

    if current_entity:
        entities.append(current_entity)  # Thêm thực thể cuối cùng

    return entities

def format_entity_list(entities):
    """Tạo danh sách thực thể tóm tắt."""
    entity_summary = "### 📋 Danh sách thực thể nhận diện được:\n"
    grouped_entities = {}

    for entity in entities:
        entity_name = ENTITY_DESCRIPTIONS.get(entity["type"], "Thực thể khác")
        grouped_entities.setdefault(entity_name, []).append(entity["text"])

    for entity_name, tokens in grouped_entities.items():
        unique_tokens = list(set(tokens))  # Loại bỏ trùng lặp
        entity_summary += f"- **{entity_name}**: {', '.join(unique_tokens)}\n"

    if not grouped_entities:
        entity_summary += "*Không tìm thấy thực thể nào.*\n"

    return entity_summary

def format_detailed_output(text, entities):
    """Tạo phân tích chi tiết về từng thực thể trong văn bản."""
    output = f"### 📜 Văn bản gốc:\n{text}\n\n"
    output += "### 🔍 Phân tích chi tiết:\n"

    if entities:
        for entity in entities:
            entity_name = ENTITY_DESCRIPTIONS.get(entity["type"], "Thực thể khác")
            output += f"- **{entity_name}**: {entity['text']}\n"
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

        # Hiển thị danh sách thực thể trước
        entity_list_output = format_entity_list(extracted_entities)
        st.subheader("📌 Kết quả nhận diện:")
        st.markdown(entity_list_output)

        # Hiển thị phân tích chi tiết sau
        detailed_output = format_detailed_output(user_input, extracted_entities)
        st.subheader("📊 Phân tích chi tiết:")
        st.markdown(detailed_output)
        
        # Lưu kết quả vào tệp
        all_inputs_with_entities = []
        for text in st.session_state.total_inputs:
            extracted_entities = extract_entities(text)
            entity_list_output = format_entity_list(extracted_entities)
            detailed_output = format_detailed_output(text, extracted_entities)
            all_inputs_with_entities.append(entity_list_output + "\n" + detailed_output)
        
        all_inputs_with_entities_text = "\n\n".join(all_inputs_with_entities)
        
        st.download_button(
            label="📥 Tải xuống kết quả nhận diện",
            data=all_inputs_with_entities_text,
            file_name="ket_qua_ner.txt",
            mime="text/plain"
        )
    else:
        st.warning("⚠️ Vui lòng nhập văn bản trước khi phân tích.")