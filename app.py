import streamlit as st
import spacy

# Load spaCy model
spacy_model_path = "IE Model"
nlp_spacy = spacy.load(spacy_model_path)

# Initialize session state for storing user inputs
if "total_inputs" not in st.session_state:
    st.session_state.total_inputs = []

# Chuyển đổi nhãn thực thể thành tên dễ hiểu
ENTITY_LABELS = {
    "LOC": "Địa điểm",
    "ORG": "Tên tổ chức",
    "PER": "Tên người",
    "MISC": "Thực thể khác",
}

def extract_entities(sentence):
    doc = nlp_spacy(sentence)
    entities = {}
    current_entity = ""
    current_label = ""

    for ent in doc.ents:
        label = ENTITY_LABELS.get(ent.label_, "Thực thể khác")
        
        if label == current_label:
            current_entity += " " + ent.text  # Ghép thực thể tiếp theo cùng loại
        else:
            if current_entity:  # Nếu có thực thể trước đó, thêm vào danh sách
                entities.setdefault(current_label, []).append(current_entity)
            current_entity = ent.text
            current_label = label

    # Thêm thực thể cuối cùng vào danh sách
    if current_entity:
        entities.setdefault(current_label, []).append(current_entity)

    return entities

def format_output(text, entities):
    output = f"### Văn bản gốc:\n{text}\n\n"
    output += "### Kết quả nhận diện thực thể:\n"

    if entities:
        for category, values in entities.items():
            unique_values = list(set(values))  # Loại bỏ trùng lặp
            output += f"- **{category}**: {', '.join(f'[{value}]' for value in unique_values)}\n"
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
        
        # Xử lý với spaCy
        extracted_entities = extract_entities(user_input)
        formatted_text = format_output(user_input, extracted_entities)

        # Hiển thị kết quả
        st.subheader("📌 Kết quả từ mô hình AI:")
        st.markdown(formatted_text)
        
        # Lưu toàn bộ dữ liệu
        all_inputs_with_entities = []
        for text in st.session_state.total_inputs:
            extracted_entities = extract_entities(text)
            formatted_text = format_output(text, extracted_entities)
            all_inputs_with_entities.append(formatted_text)
        
        # Tạo tệp để tải xuống
        all_inputs_text = "\n\n".join(all_inputs_with_entities)
        
        st.download_button(
            label="📥 Tải xuống kết quả nhận diện",
            data=all_inputs_text,
            file_name="ket_qua_ner.txt",
            mime="text/plain"
        )
    else:
        st.warning("⚠️ Vui lòng nhập văn bản trước khi phân tích.")
