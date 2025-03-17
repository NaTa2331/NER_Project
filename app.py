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
    "B-MISC": "Thực thể khác (Bắt đầu thực thể)n",
    "I-MISC": "Thực thể khác (Tiếp tục thực thể)",
    "O": "Không thuộc thực thể nào",
}

def extract_information_spacy(sentence):
    doc = nlp_spacy(sentence)
    extracted_info = {}
    current_entity = None

    for ent in doc.ents:
        if ent.label_.startswith("B-"):
            if current_entity:
                extracted_info.setdefault(current_entity[0], []).append(" ".join(current_entity[1]))
            current_entity = [ent.label_, [ent.text]]  # Start a new entity
        elif ent.label_.startswith("I-") and current_entity and current_entity[0] == ent.label_[2:]:
            current_entity[1].append(ent.text)  # Continue the entity
        else:
            if current_entity:
                extracted_info.setdefault(current_entity[0], []).append(" ".join(current_entity[1]))
                current_entity = None

    if current_entity:
        extracted_info.setdefault(current_entity[0], []).append(" ".join(current_entity[1]))

    for ent in doc.ents:
        if not ent.label_.startswith("B-") and not ent.label_.startswith("I-"):
            extracted_info.setdefault(ent.label_, []).append(ent.text)

    return extracted_info

def format_output(text, entities):
    output = f"### Văn bản gốc:\n{text}\n\n"
    output += "### Kết quả nhận diện thực thể:\n"
    
    total_entities = sum(len(tokens) for tokens in entities.values())
    output += f"**Tổng số thực thể nhận diện được: {total_entities}**\n\n"

    if entities:
        output += "| Loại thực thể | Giá trị |\n"
        output += "|---------------|---------|\n"
        for entity_type, tokens in entities.items():
            unique_tokens = list(set(tokens))  # Loại bỏ trùng lặp
            description = ENTITY_DESCRIPTIONS.get(entity_type, "Thực thể khác")
            output += f"| **{description}** | {', '.join(unique_tokens)} |\n"
        
        # Add a section for complete phrases for all entity types
        output += "\n### Các cụm từ hoàn chỉnh:\n"
        for entity_type in entities.keys():
            if entity_type.startswith("B-"):
                complete_phrases = entities[entity_type] + entities.get("I-" + entity_type[2:], [])
                output += f"- **Cụm từ {ENTITY_DESCRIPTIONS.get(entity_type, 'khác')}**: {', '.join(set(complete_phrases))}\n"
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
