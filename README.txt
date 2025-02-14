Toàn bộ mã nguồn để demo được lưu trong notebook Main_Source.ipynb

Giải nén 2 model đã được huấn luyện để thực nghiệm

Các bước khởi tạo app demo (sử dụng streamlit)
Bước 1: tạo môi trường ảo: dùng cmd
	python -m venv ragenv

Bước 2: truy cập vào môi trường ảo
	ragenv\Scripts\activate

Bước 3: Cài đặt các thư viện cần thiết
pip install (streamlit, transformers, torch, spacy,...)

Bước 4: khởi động app.py
	streamlit run app.py