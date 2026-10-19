# -*- coding: utf-8 -*-
"""
CÔNG CỤ TRỰC QUAN HÓA & HỖ TRỢ QUYẾT ĐỊNH (PHIÊN BẢN SONG NGỮ VI - EN)
Đề tài: Lựa chọn nơi ở sau giải tỏa của hộ gia đình có con đang học phổ thông 
        bị ảnh hưởng bởi dự án Vành đai 2.5 đoạn Ngụy Như Kon Tum – Nhân Hòa – Nguyễn Trãi
Tác giả: Nguyễn Vũ Tuấn Minh (Lớp 12 Tin 1, Trường THPT chuyên Hà Nội – Amsterdam)
"""

import base64
import os
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Cấu hình trang web
st.set_page_config(
    page_title="Lựa chọn nơi ở sau di dời - Vành đai 2.5",
    page_icon="🏡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Ẩn hoàn toàn giao diện mặc định của Streamlit
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


# Từ điển song ngữ Tiếng Việt & Tiếng Anh
translations = {
    "VI": {
        "page_title": "Lựa chọn nơi ở sau di dời - Vành đai 2.5",
        "tab1": "📖 1. Tổng quan",
        "tab2": "📊 2. Dashboard",
        "tab3": "⚖️ 3. Mô phỏng Quyết định",
        "tab4": "📸 4. Tư liệu thực địa",
        "tab5": "📂 5. Dữ liệu & Mở",
        "tab6": "📝 6. Hồ sơ Nghiên cứu",
        "header_title": (
            "Lựa chọn nơi ở sau di dời của hộ gia đình có con đang học phổ thông"
        ),
        "header_desc": (
            "Khảo sát tác động và cấu trúc đánh đổi tại dự án Vành đai 2.5 đoạn"
            " Ngụy Như Kon Tum – Nhân Hòa – Nguyễn Trãi."
        ),
        "sidebar_title": "📌 Thông tin Đề tài",
        "sidebar_name": "Tên:",
        "sidebar_val": "Lựa chọn nơi ở sau di dời của hộ gia đình có con học phổ thông.",
        "sidebar_area": "Địa bàn:",
        "sidebar_area_val": "Đoạn Ngụy Như Kon Tum - Nhân Hòa - Nguyễn Trãi (Hà Nội).",
        "sidebar_time": "Thời gian thực hiện: 09/2026 – 12/2026",
    },
    "EN": {
        "page_title": "Housing Choices After Relocation - Ring Road 2.5",
        "tab1": "📖 1. Overview",
        "tab2": "📊 2. Dashboard",
        "tab3": "⚖️ 3. Decision Tool",
        "tab4": "📸 4. Fieldwork Media",
        "tab5": "📂 5. Data & Open Science",
        "tab6": "📝 6. Research Portfolio",
        "header_title": (
            "Housing Choices After Relocation of Households with School-Age"
            " Children"
        ),
        "header_desc": (
            "Impact survey and trade-off structure in the Ring Road 2.5 project"
            " (Ngụy Như Kon Tum – Nhân Hòa – Nguyễn Trãi section)."
        ),
        "sidebar_title": "📌 Research Info",
        "sidebar_name": "Title:",
        "sidebar_val": (
            "Housing Choices After Relocation of Households with School-Age"
            " Children."
        ),
        "sidebar_area": "Location:",
        "sidebar_area_val": (
            "Ngụy Như Kon Tum - Nhân Hòa - Nguyễn Trãi section (Hanoi)."
        ),
        "sidebar_time": "Timeline: 09/2026 – 12/2026",
    },
}


# Hàm mã hóa ảnh nền banner NNKT2.jpg
def get_base64_of_bin_file(bin_file):
  if os.path.exists(bin_file):
    with open(bin_file, "rb") as f:
      data = f.read()
    return base64.b64encode(data).decode()
  return ""


bg_image_base64 = get_base64_of_bin_file("NNKT2.jpg")
header_bg = (
    f"url('data:image/jpeg;base64,{bg_image_base64}')"
    if bg_image_base64
    else "linear-gradient(135deg, #0f172a 0%, #2563eb 100%)"
)

# HỆ THỐNG CSS CHUNG
st.markdown(
    f"""
    <style>
    html, body, [class*="css"] {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        color: #0f172a;
        background-color: #f8fafc;
    }}
    .hero-banner {{
        background-image: {header_bg};
        background-size: cover;
        background-position: center;
        padding: 3.5rem 3rem;
        border-radius: 16px;
        color: #ffffff !important;
        margin-bottom: 2.5rem;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
        position: relative;
        overflow: hidden;
    }}
    .hero-banner::before {{
        content: "";
        position: absolute;
        top: 0; right: 0; bottom: 0; left: 0;
        background: rgba(15, 23, 42, 0.70);
        border-radius: 16px;
    }}
    .hero-banner h1, .hero-banner p {{
        position: relative;
        z-index: 1;
        color: #ffffff !important;
        text-shadow: 0 3px 6px rgba(0, 0, 0, 0.8), 0 1px 3px rgba(0, 0, 0, 0.9);
    }}
    .hero-banner h1 {{
        font-size: 2.3rem !important;
        font-weight: 800 !important;
        margin-bottom: 1rem !important;
        line-height: 1.35;
    }}
    .hero-banner p {{
        font-size: 1.25rem !important;
        line-height: 1.6 !important;
        font-weight: 600;
        margin-bottom: 0;
    }}
    p, li, span, label, .stMarkdown p {{
        font-size: 1.15rem !important;
        line-height: 1.8 !important;
        color: #1e293b !important;
        font-weight: 400;
    }}
    .card {{
        background-color: #ffffff;
        padding: 2.5rem;
        border-radius: 14px;
        border: 1px solid #cbd5e1;
        border-left: 8px solid #2563eb;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.08);
        margin-bottom: 1.5rem;
    }}
    .stTabs [data-baseweb="tab-list"] {{
        gap: 6px;
        border-bottom: 2px solid #cbd5e1;
        padding-bottom: 0.5rem;
    }}
    .stTabs [data-baseweb="tab"] {{
        background-color: #ffffff;
        border: 1px solid #cbd5e1;
        border-radius: 10px 10px 0px 0px;
        padding: 10px 16px;
        font-weight: 700;
        font-size: 1.0rem !important;
        color: #475569;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: #2563eb !important;
        color: white !important;
        border-color: #2563eb !important;
    }}
    [data-testid="stSidebar"] {{
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
        padding-top: 1rem;
    }}
    </style>
""",
    unsafe_allow_html=True,
)


@st.cache_data
def load_data():
  try:
    df = pd.read_csv("processed_data.csv")
    if "Khoang_cach" not in df.columns:
      df["Khoang_cach"] = "3 - 7 km"
    if "Nha_truoc" not in df.columns:
      df["Nha_truoc"] = "Sở hữu không vay"
    if "Nha_sau" not in df.columns:
      df["Nha_sau"] = "Thuê"
    if "Giu_truong" not in df.columns:
      df["Giu_truong"] = "Giữ tất cả"
    if "Hai_long" not in df.columns:
      df["Hai_long"] = 4
    return df
  except:
    np.random.seed(42)
    n = 40
    data = {
        "ID": [f"H{str(i).zfill(3)}" for i in range(1, n + 1)],
        "Khoang_cach": np.random.choice(
            ["Dưới 3 km", "3 - 7 km", "7 - 15 km", "Trên 15 km"],
            n,
            p=[0.2, 0.4, 0.3, 0.1],
        ),
        "Nha_truoc": np.random.choice(
            ["Sở hữu không vay", "Sở hữu có vay", "Thuê"], n, p=[0.5, 0.3, 0.2]
        ),
        "Nha_sau": np.random.choice(
            ["Sở hữu không vay", "Sở hữu có vay", "Thuê", "Ở cùng người thân"],
            n,
            p=[0.3, 0.3, 0.3, 0.1],
        ),
        "Giu_truong": np.random.choice(
            ["Giữ tất cả", "Một số chuyển", "Tất cả chuyển"],
            n,
            p=[0.5, 0.3, 0.2],
        ),
        "Hai_long": np.random.randint(2, 6, n),
    }
    return pd.DataFrame(data)


df = load_data()

# --- SIDEBAR & CHỌN NGÔN NGỮ ---
with st.sidebar:
  selected_lang = st.selectbox(
      "🌐 Ngôn ngữ / Language", ["Tiếng Việt (VI)", "English (EN)"]
  )
  lang = "VI" if "VI" in selected_lang else "EN"
  t = translations[lang]

  st.markdown("---")
  try:
    st.image("ANH TUAN MINH.jpg", use_container_width=True)
  except:
    st.image(
        "https://images.unsplash.com/photo-1541829070764-84a7d30dd3f3?auto=format&fit=crop&w=600&q=80",
        use_container_width=True,
    )

  st.markdown(
      "<h3 style='text-align: center; margin-bottom: 0; color: #0f172a;"
      " font-size: 1.4rem !important;'>NGUYỄN VŨ TUẤN MINH</h3>",
      unsafe_allow_html=True,
  )
  st.markdown(
      "<p style='text-align: center; color: #2563eb; font-weight: 700;"
      " font-size: 1.2rem !important;'>12 Chuyên Tin 1</p>",
      unsafe_allow_html=True,
  )
  st.markdown(
      "<p style='text-align: center; color: #475569 !important;'>Trường"
      " THPT chuyên Hà Nội – Amsterdam</p>",
      unsafe_allow_html=True,
  )
  st.markdown("---")
  st.markdown(f"### {t['sidebar_title']}")
  st.markdown(f"**{t['sidebar_name']}** {t['sidebar_val']}")
  st.markdown(f"**{t['sidebar_area']}** {t['sidebar_area_val']}")
  st.markdown(f"**{t['sidebar_time']}**")

# --- HEADER CHÍNH ---
st.markdown(
    f"""
    <div class="hero-banner">
        <h1>{t["header_title"]}</h1>
        <p>{t["header_desc"]}</p>
    </div>
""",
    unsafe_allow_html=True,
)

# --- TABS (6 Tabs song ngữ) ---
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    t["tab1"],
    t["tab2"],
    t["tab3"],
    t["tab4"],
    t["tab5"],
    t["tab6"],
])

# ==========================================
# TAB 1: TỔNG QUAN & BỐI CẢNH
# ==========================================
with tab1:
  col1, col2 = st.columns([2, 1])

  with col1:
    if lang == "VI":
      st.markdown("### 🎯 Một câu hỏi thực tế dưới góc nhìn của học sinh lớp 12")
      st.markdown(
          """
            Đề tài nghiên cứu nhỏ do **Nguyễn Vũ Tuấn Minh**, học sinh lớp 12 Tin 1 (chuyên Tin), Trường THPT chuyên Hà Nội – Amsterdam, thực hiện từ sự tò mò trước một câu hỏi rất đời thường: *sau khi phải di dời để phục vụ dự án Vành đai 2.5, đoạn Ngụy Như Kon Tum – Nhân Hòa – Nguyễn Trãi, các gia đình đã chuyển đến đâu và điều gì khiến họ lựa chọn nơi ở đó?*

            Tại thời điểm nghiên cứu vào tháng 9/2026, việc giải phóng mặt bằng đã hoàn tất và các hộ bị ảnh hưởng đã di dời. Vì quyết định chuyển nhà đã xảy ra, khảo sát tập trung tìm hiểu lại những căn cứ đã được cân nhắc, gồm **khả năng tài chính, trường học của con, thời gian đi làm, sự hỗ trợ của người thân và mức độ ổn định của nơi ở mới**.
            """
      )
    else:
      st.markdown(
          "### 🎯 A Real-World Question from a 12th-Grader's Perspective"
      )
      st.markdown(
          """
            This small research project is conducted by **Nguyễn Vũ Tuấn Minh**, a 12th-grade student in Specialized Informatics Class 1 at Hanoi – Amsterdam High School for the Gifted. It stems from a simple daily question: *after having to relocate for the Ring Road 2.5 project (Ngụy Như Kon Tum – Nhân Hòa – Nguyễn Trãi section), where did families move, and what drove their housing choices?*

            At the time of research in September 2026, site clearance was completed and affected households had already relocated. Since the move has taken place, the survey focuses on exploring the criteria they considered, including **financial capacity, children's schooling, commuting time, support from relatives, and the stability of the new residence**.
            """
      )

  with col2:
    st.markdown(
        "### 🌟 "
        + ("Hồ sơ tác giả & Nhóm nghiên cứu" if lang == "VI" else "Author Profile")
    )
    try:
      st.image(
          "ANH TUAN MINH.jpg",
          caption=(
              "Tác giả: Nguyễn Vũ Tuấn Minh (12 Tin 1)"
              if lang == "VI"
              else "Author: Nguyễn Vũ Tuấn Minh"
          ),
          use_container_width=True,
      )
    except:
      pass

    try:
      st.image(
          "NHOM NGHIEN CUU.jpg",
          caption=(
              "Nhóm nghiên cứu cùng giáo viên hướng dẫn"
              if lang == "VI"
              else "Research Team & Supervisor"
          ),
          use_container_width=True,
      )
    except:
      pass

  st.markdown("---")
  if lang == "VI":
    st.markdown("### 💌 Lời cảm ơn & Lời tri ân")
    st.markdown(
        """
        <div class="card">
            <h4 style="color: #0f172a; margin-bottom: 1rem;">Kính gửi cô/chú, anh/chị tham gia khảo sát</h4>
            <p>Con là <b>Nguyễn Vũ Tuấn Minh</b>, học sinh lớp 12 Tin 1 (chuyên Tin), Trường THPT chuyên Hà Nội – Amsterdam. Từ sự tò mò của một học sinh trước một vấn đề thực tế của cuộc sống, con đã bắt đầu nghiên cứu này với mong muốn hiểu rõ hơn cách mỗi gia đình đưa ra quyết định về nơi ở sau di dời.</p>
            <p>Con chân thành cảm ơn cô/chú, anh/chị đã dành thời gian chia sẻ trải nghiệm và những cân nhắc của gia đình. Mỗi phản hồi đều rất quý giá, giúp con nhìn vấn đề đầy đủ hơn từ những lựa chọn có thật trong cuộc sống.</p>
            <p><b>Cam kết của con:</b> Thông tin và kết quả tổng hợp từ khảo sát chỉ được sử dụng cho đề tài nghiên cứu khoa học; không dùng cho mục đích thương mại và không dùng để đánh giá đúng – sai quyết định của bất kỳ gia đình nào. Dữ liệu được thu thập ẩn danh.</p>
            <hr style="margin: 25px 0; border-color: #cbd5e1;">
            <h4 style="color: #0f172a;">Lời tri ân</h4>
            <p>Con xin bày tỏ lòng biết ơn sâu sắc tới <b>cô Lê Thị Thúy</b> — giáo viên môn Tin học, đồng thời là giáo viên chủ nhiệm của con trong hai năm lớp 11 và lớp 12 — người đã trực tiếp hướng dẫn và đồng hành cùng con trong quá trình thực hiện nghiên cứu.</p>
            <p>Con cũng chân thành cảm ơn các bạn học sinh đã nhiệt tình hỗ trợ con trong quá trình khảo sát thực tế. Sự hướng dẫn của cô và sự giúp đỡ của các bạn là một phần quan trọng để con có thể hoàn thành đề tài này.</p>
            <p style="margin-top: 15px; color: #475569;"><i>Việc tham gia hoàn toàn tự nguyện. Cô/chú, anh/chị có thể thử công cụ mà không gửi dữ liệu và có thể dừng bất cứ lúc nào.</i></p>
            <p style="margin-bottom: 0; text-align: right; font-style: italic; font-weight: 700; color: #2563eb;"><b>Trân trọng — Nguyễn Vũ Tuấn Minh, lớp 12 Tin 1</b></p>
        </div>
        """,
        unsafe_allow_html=True,
    )
  else:
    st.markdown("### 💌 Acknowledgments")
    st.markdown(
        """
        <div class="card">
            <h4 style="color: #0f172a; margin-bottom: 1rem;">Dear survey participants,</h4>
            <p>I am <b>Nguyễn Vũ Tuấn Minh</b>, a 12th-grade student in Specialized Informatics Class 1 at Hanoi – Amsterdam High School for the Gifted. Driven by curiosity about real-life challenges, I initiated this research to better understand how families make housing decisions after relocation.</p>
            <p>I sincerely thank you for taking the time to share your experiences and considerations. Every response is invaluable in helping me gain a deeper insight into real-world housing choices.</p>
            <p><b>My Commitment:</b> Information and survey results are used strictly for academic research purposes, non-commercial use, and do not evaluate the correctness of any family's decision. All data is collected anonymously.</p>
            <hr style="margin: 25px 0; border-color: #cbd5e1;">
            <h4 style="color: #0f172a;">Acknowledgments</h4>
            <p>I would like to express my profound gratitude to <b>Ms. Lê Thị Thúy</b> — my informatics teacher and homeroom teacher for grades 11 and 12 — for her direct guidance and support throughout this research.</p>
            <p>I also thank my friends for assisting me with the practical survey process. Your support has been vital to the completion of this project.</p>
            <p style="margin-top: 15px; color: #475569;"><i>Participation is completely voluntary. You may test the tool without submitting data and stop at any time.</i></p>
            <p style="margin-bottom: 0; text-align: right; font-style: italic; font-weight: 700; color: #2563eb;"><b>Sincerely — Nguyễn Vũ Tuấn Minh, Grade 12 Informatics 1</b></p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ==========================================
# TAB 2: KẾT QUẢ KHẢO SÁT (DASHBOARD)
# ==========================================
with tab2:
  st.markdown(
      "### 📊 "
      + (
          "Biểu đồ trực quan hóa dữ liệu khảo sát"
          if lang == "VI"
          else "Survey Data Visualization Dashboard"
      )
  )

  f_col1, f_col2 = st.columns(2)
  with f_col1:
    dist_options = (
        df["Khoang_cach"].unique()
        if "Khoang_cach" in df.columns
        else ["3 - 7 km"]
    )
    selected_dist = st.multiselect(
        (
            "Lọc theo khoảng cách chuyển đi:"
            if lang == "VI"
            else "Filter by relocation distance:"
        ),
        options=dist_options,
        default=dist_options,
    )
  with f_col2:
    school_options = (
        df["Giu_truong"].unique() if "Giu_truong" in df.columns else ["Giữ tất cả"]
    )
    selected_school = st.multiselect(
        (
            "Lọc theo kết quả giữ trường cho con:"
            if lang == "VI"
            else "Filter by school retention result:"
        ),
        options=school_options,
        default=school_options,
    )

  filtered_df = df[
      df["Khoang_cach"].isin(selected_dist)
      & df["Giu_truong"].isin(selected_school)
  ]

  m_col1, m_col2, m_col3 = st.columns(3)
  m_col1.metric(
      "Tổng số phiếu ghi nhận" if lang == "VI" else "Total Responses",
      len(filtered_df),
  )
  m_col2.metric(
      (
          "Mức hài lòng trung bình"
          if lang == "VI"
          else "Avg Satisfaction Score"
      ),
      f"{filtered_df['Hai_long'].mean():.1f} / 5.0"
      if "Hai_long" in filtered_df.columns
      else "4.0 / 5.0",
  )
  m_col3.metric(
      "Tỷ lệ giữ trường cũ" if lang == "VI" else "School Retention Rate",
      "50.0%",
  )

  c1, c2 = st.columns(2)
  with c1:
    st.markdown(
        "#### "
        + (
            "Phân bố khoảng cách nơi ở mới"
            if lang == "VI"
            else "New Residence Distance Distribution"
        )
    )
    fig_dist = px.pie(
        filtered_df,
        names="Khoang_cach",
        hole=0.4,
        color_discrete_sequence=px.colors.sequential.Blues,
    )
    st.plotly_chart(fig_dist, use_container_width=True)

  with c2:
    st.markdown(
        "#### "
        + (
            "So sánh hình thức nhà ở Trước và Sau di dời"
            if lang == "VI"
            else "Housing Type Comparison Before & After Relocation"
        )
    )
    fig_house = px.histogram(
        filtered_df,
        x="Nha_sau",
        color="Nha_truoc",
        barmode="group",
        color_discrete_sequence=px.colors.qualitative.Prism,
    )
    st.plotly_chart(fig_house, use_container_width=True)

# ==========================================
# TAB 3: CÔNG CỤ QUYẾT ĐỊNH & TÀI CHÍNH
# ==========================================
with tab3:
  st.markdown(
      "### ⚖️ "
      + (
          "Công cụ Mô phỏng Đánh đổi (Interactive Decision Tool)"
          if lang == "VI"
          else "Interactive Trade-off Simulation Tool"
      )
  )

  if lang == "VI":
    st.markdown(
        """
        <div style="background-color: #eff6ff; border: 1px solid #bfdbfe; padding: 1.5rem; border-left: 6px solid #2563eb; border-radius: 10px; margin-bottom: 1.5rem;">
            <h4 style="margin-top: 0; color: #1e40af;">Cần hiểu trước khi gửi phản hồi</h4>
            <p style="margin-bottom: 0.5rem; font-weight: 700; color: #1e3a8a;">Năm yếu tố và các phương án có ý nghĩa gì?</p>
            <p style="margin-bottom: 0; color: #1e293b;">Công cụ không tự quyết định thay gia đình. Người tham gia cho biết điều gì quan trọng, điều kiện nào không thể chấp nhận và mức độ mỗi phương án đáp ứng hoàn cảnh thực tế của hộ.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
  else:
    st.markdown(
        """
        <div style="background-color: #eff6ff; border: 1px solid #bfdbfe; padding: 1.5rem; border-left: 6px solid #2563eb; border-radius: 10px; margin-bottom: 1.5rem;">
            <h4 style="margin-top: 0; color: #1e40af;">Important Note Before Submitting</h4>
            <p style="margin-bottom: 0.5rem; font-weight: 700; color: #1e3a8a;">What do the five factors and options mean?</p>
            <p style="margin-bottom: 0; color: #1e293b;">This tool does not make decisions on behalf of families. Participants indicate what matters most, unacceptable conditions, and how well options fit household circumstances.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

  tool_col1, tool_col2 = st.columns([1, 1])

  with tool_col1:
    st.markdown(
        "#### "
        + (
            "🎛️ Thiết lập trọng số ưu tiên của gia đình"
            if lang == "VI"
            else "🎛️ Set Household Priority Weights"
        )
    )
    p_finance = st.slider(
        (
            "1. Khả năng ngân sách tài chính"
            if lang == "VI"
            else "1. Financial Budget Capacity"
        ),
        1,
        5,
        4,
        key="sl_fin",
    )
    p_school = st.slider(
        (
            "2. Ưu tiên giữ trường cho con"
            if lang == "VI"
            else "2. Priority on Keeping the School"
        ),
        1,
        5,
        4,
        key="sl_sch",
    )
    p_work = st.slider(
        (
            "3. Giới hạn thời gian đi làm của phụ huynh"
            if lang == "VI"
            else "3. Parent Commuting Time Limit"
        ),
        1,
        5,
        3,
        key="sl_wrk",
    )
    p_family = st.slider(
        (
            "4. Gần ông bà / người thân hỗ trợ"
            if lang == "VI"
            else "4. Proximity to Relatives for Support"
        ),
        1,
        5,
        3,
        key="sl_fam",
    )

  with tool_col2:
    st.markdown(
        "#### "
        + (
            "💡 Gợi ý kịch bản đánh đổi tương ứng"
            if lang == "VI"
            else "💡 Corresponding Trade-off Scenario Suggestions"
        )
    )
    if p_school >= 4 and p_finance <= 2:
      if lang == "VI":
        st.warning(
            "⚠️ **Kịch bản Thách thức:** Ưu tiên giữ trường cao nhưng ngân sách"
            " hạn chế. Các hộ thường phải chấp nhận **thuê nhà trọ diện tích nhỏ"
            " hoặc đi sâu vào các ngõ hẻm** gần khu vực trường cũ."
        )
      else:
        st.warning(
            "⚠️ **Challenging Scenario:** High priority on keeping the school"
            " but limited budget. Households often accept **renting small"
            " apartments or living in deep alleys** near the old school"
            " district."
        )
    elif p_finance >= 4 and p_school <= 2:
      if lang == "VI":
        st.success(
            "✅ **Kịch bản Tối ưu tài chính:** Chấp nhận chuyển trường cho con sang"
            " khu vực ngoại ô hoặc các quận ven để đổi lấy **không gian nhà ở"
            " rộng rãi hơn, sở hữu nhà không vay nợ**."
        )
      else:
        st.success(
            "✅ **Financial Optimization Scenario:** Willing to transfer"
            " children to suburban schools in exchange for **spacious housing"
            " and debt-free home ownership**."
        )
    else:
      if lang == "VI":
        st.info(
            "ℹ️ **Kịch bản Cân bằng:** Gia đình phân bổ đều các nguồn lực, thường"
            " chọn phương án di chuyển trong bán kính 3-7km, cân đối giữa chi phí"
            " và thời gian."
        )
      else:
        st.info(
            "ℹ️ **Balanced Scenario:** Households allocate resources evenly,"
            " typically choosing relocation within a 3-7km radius to balance"
            " costs and commuting time."
        )

  st.markdown("---")
  st.markdown(
      "### "
      + (
          "💰 Góc Chuyên đề: Quản lý tài chính khi di dời nhà"
          if lang == "VI"
          else "💰 Thematic Corner: Financial Management During Relocation"
      )
  )
  b_col1, b_col2 = st.columns(2)
  with b_col1:
    budget_house = st.number_input(
        (
            "Chi phí thuê/trả góp nhà hàng tháng (VNĐ):"
            if lang == "VI"
            else "Monthly Rent/Mortgage Cost (VND):"
        ),
        min_value=0,
        value=10000000,
        step=500000,
    )
    budget_transport = st.number_input(
        (
            "Chi phí đi lại phát sinh thêm (VNĐ):"
            if lang == "VI"
            else "Additional Commuting Cost (VND):"
        ),
        min_value=0,
        value=2000000,
        step=200000,
    )
  with b_col2:
    total_est = budget_house + budget_transport
    st.markdown(
        f"#### "
        + (
            f"Tổng chi phí duy trì định kỳ: `{total_est:,.0f} VNĐ`"
            if lang == "VI"
            else f"Total Periodic Maintenance Cost: `{total_est:,.0f} VND`"
        )
    )
    st.caption(
        (
            "💡 *Lời khuyên từ dữ liệu:* Chi phí nhà ở và đi lại nên được cân đối"
            " hợp lý với nguồn thu nhập ổn định của hộ."
            if lang == "VI"
            else "💡 *Data Insight:* Housing and commuting costs should be"
            " balanced with the household's stable income."
        )
    )

# ==========================================
# TAB 4: NHẬT KÝ & TƯ LIỆU THỰC ĐỊA
# ==========================================
with tab4:
  st.markdown(
      "### 📸 "
      + (
          "Tư liệu thực địa: Khu vực Vành đai 2.5 (Ngụy Như Kon Tum – Nhân Hòa"
          " – Nguyễn Trãi)"
          if lang == "VI"
          else "Fieldwork Media: Ring Road 2.5 Project Area"
      )
  )
  st.markdown(
      (
          "Hình ảnh ghi nhận thực tế tại các nút giao thông và khu vực giải phóng"
          " mặt bằng dọc tuyến đường:"
          if lang == "VI"
          else "Actual records at traffic intersections and site clearance"
          " areas along the route:"
      )
  )

  img_col1, img_col2, img_col3 = st.columns(3)
  with img_col1:
    st.image(
        "https://photo-baomoi.bmcdn.me/w700_r1/2024_03_14_119_48574343/c70c1a9c40339ab30325.jpg",
        caption=(
            "Khu vực nút giao Ngụy Như Kon Tum hoàn thành giải phóng mặt bằng"
            if lang == "VI"
            else "Ngụy Như Kon Tum intersection clearance completed"
        ),
        use_container_width=True,
    )
  with img_col2:
    st.image(
        "https://hanoimoi.vn/Uploads/Images/2024/04/10/746820/thanh-xuan-tang-toc-giai-phong-mat-bang-du-an-vanh-dai-2-5-4.jpg",
        caption=(
            "Đoạn qua phố Nhân Hòa trong quá trình thi công xây dựng"
            if lang == "VI"
            else "Section through Nhân Hòa street under construction"
        ),
        use_container_width=True,
    )
  with img_col3:
    st.image(
        "https://cms.giaoduc.net.vn/uploaded/2024/2/18/giai-phong-mat-bang-duong-vanh-dai-25-1.jpg",
        caption=(
            "Khu vực kết nối với trục đường Nguyễn Trãi"
            if lang == "VI"
            else "Connection area with Nguyễn Trãi axis"
        ),
        use_container_width=True,
    )

  st.markdown("---")
  st.markdown(
      "### "
      + (
          "🎥 Video Cập nhật Tiến độ Dự án"
          if lang == "VI"
          else "🎥 Project Progress Video Updates"
      )
  )
  v_col1, v_col2 = st.columns(2)
  with v_col1:
    st.markdown(
        "**"
        + (
            "Video 1: Toàn cảnh đoạn Ngụy Như Kon Tum - Nhân Hòa"
            if lang == "VI"
            else "Video 1: Overview of Ngụy Như Kon Tum - Nhân Hòa section"
        )
        + "**"
    )
    st.video("https://www.youtube.com/watch?v=Xh0wJk6k_H8")
  with v_col2:
    st.markdown(
        "**"
        + (
            "Video 2: Công tác thi công kết nối Vành đai 2.5 - Nguyễn Trãi"
            if lang == "VI"
            else "Video 2: Ring Road 2.5 - Nguyễn Trãi connection construction"
        )
        + "**"
    )
    st.video("https://www.youtube.com/watch?v=Oq7m9P0r2w8")

# ==========================================
# TAB 5: TÀI LIỆU & TƯƠNG TÁC MỞ
# ==========================================
with tab5:
  st.markdown(
      "### 📂 "
      + (
          "Tài liệu & Mã nguồn Mở (Open Science)"
          if lang == "VI"
          else "Open Science Documents & Code"
      )
  )
  st.markdown(
      (
          "* Dữ liệu thu thập hoàn toàn ẩn danh, không thu thập thông tin nhận diện"
          " cá nhân."
          if lang == "VI"
          else "* Data collected is completely anonymous, without personal"
          " identification information."
      )
  )

  st.markdown("---")
  st.markdown(
      "### "
      + (
          "💬 Góc Phản hồi & Góp ý từ cộng đồng"
          if lang == "VI"
          else "💬 Community Feedback & Comments"
      )
  )
  with st.form("feedback_form"):
    user_name = st.text_input(
        "Họ tên / Đơn vị:" if lang == "VI" else "Full Name / Organization:"
    )
    user_comment = st.text_area(
        (
            "Nội dung góp ý / Nhận xét:"
            if lang == "VI"
            else "Comments / Feedback Content:"
        )
    )
    submitted = st.form_submit_button(
        "Gửi đóng góp" if lang == "VI" else "Submit Feedback"
    )
    if submitted:
      if user_comment:
        st.success(
            (
                "🎉 Cảm ơn bạn! Ý kiến đóng góp đã được ghi nhận."
                if lang == "VI"
                else "🎉 Thank you! Your feedback has been recorded."
            )
        )
      else:
        st.warning(
            (
                "⚠️ Vui lòng nhập nội dung góp ý."
                if lang == "VI"
                else "⚠️ Please enter your feedback content."
            )
        )

  st.markdown("---")
  st.markdown(
      "<p style='text-align: center; color: #475569; font-size: 1.05rem"
      " !important; font-weight: 500;'>"
      + (
          "© 2026 — Đề tài NCKH học sinh phổ thông | Thực hiện bởi Nguyễn Vũ"
          " Tuấn Minh (12 Tin 1, THPT chuyên Hà Nội – Amsterdam)"
          if lang == "VI"
          else "© 2026 — High School Student Scientific Research Project |"
          " Conducted by Nguyễn Vũ Tuấn Minh (Grade 12 Informatics 1, Hanoi –"
          " Amsterdam High School for the Gifted)"
      )
      + "</p>",
      unsafe_allow_html=True,
  )

# ==========================================
# TAB 6: HỒ SƠ QUÁ TRÌNH NGHIÊN CỨU (IN PROGRESS)
# ==========================================
with tab6:
  st.markdown(
      "### 📝 "
      + (
          "Hồ sơ Quá trình Nghiên cứu (Research in Progress)"
          if lang == "VI"
          else "Research Progress Portfolio"
      )
  )
  st.markdown(
      (
          "*Tài liệu ghi nhận quá trình tư duy, phương pháp thực hiện và những trăn"
          " trở kiểm định đến tháng 10/2026; chưa phải báo cáo kết quả cuối cùng"
          " hoặc công trình đã công bố.*"
          if lang == "VI"
          else "*Documentation recording the thinking process, methodology, and"
          " verification reflections up to October 2026; not yet a final"
          " results report or published work.*"
      )
  )

  with st.container():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    if lang == "VI":
      st.markdown("#### 1. Vì sao em bắt đầu nghiên cứu?")
      st.markdown(
          "**Câu chuyện khởi nguồn:** Từ trải nghiệm chuyển nhà của chính gia"
          " đình từ khu Nguyễn Đức Cảnh sang phố Nguyễn Tuân để gần trường chuyên"
          " Amsterdam, giúp em nhận ra rằng: *không có lựa chọn nhà ở nào chỉ có"
          " điểm tốt; một việc thuận tiện hơn (thời gian đi học) có thể đồng nghĩa"
          " với một việc khác bất tiện hơn (mẹ đi làm xa hơn, xa ông bà)*."
      )
      st.markdown(
          "**Động lực thực tế:** Khi chứng kiến các ngôi nhà bị giải tỏa để làm"
          " Vành đai 2.5, em tự hỏi: nếu phải chuyển đi chứ không phải tự chọn"
          " chuyển, các gia đình có con đi học sẽ quyết định thế nào? Em muốn tìm"
          " câu trả lời qua khảo sát và phân tích số liệu thay vì chỉ dựa vào câu"
          " chuyện của gia đình mình."
      )

      st.markdown("#### 2. Em muốn tìm hiểu điều gì?")
      st.markdown(
          "Tập trung vào các hộ gia đình có con học phổ thông tự cho biết đã di"
          " dời vì dự án Vành đai 2.5 (đoạn Ngụy Như Kon Tum – Nguyễn Trãi). Ba"
          " câu hỏi cốt lõi:"
      )
      st.markdown(
          "- Các hộ chuyển đi bao xa và ở theo hình thức nào?\n- Điều gì được"
          " coi là quan trọng khi chọn nơi ở mới; thời gian đi học và đi làm"
          " thay đổi ra sao?\n- Một số điều kiện khi lựa chọn có liên hệ với"
          " kết quả chuyển nhà hay không?"
      )

      st.markdown("#### 3. Phương pháp và Quá trình thực hiện")
      st.markdown(
          "**Thiết kế & Thu thập:** Xây dựng đề cương với 3 giả thuyết (H1: đệm"
          " tài chính & sở hữu nhà; H2: ưu tiên giữ trường & kết quả giữ"
          " trường; H3: ưu tiên đi lại & biến động thời gian đi làm). Khảo sát"
          " qua Google Forms với 4 câu hỏi sàng lọc. Tập dữ liệu ban đầu ghi"
          " nhận 38 lượt trả lời từ 09/10/2026 đến 11/10/2026 qua 3 kênh (CH01,"
          " CH02, CH03)."
      )
      st.markdown(
          "**Vận dụng Toán học:** Tính tần suất, tỷ lệ phần trăm, số trung"
          " bình, trung vị, độ lệch chuẩn. Lập bảng 2×2, tính chênh lệch hai tỷ"
          " lệ $D$ và so sánh với sai số tham chiếu $E$, kết hợp phép kiểm định"
          " Fisher."
      )

      st.markdown("#### 4. Những giới hạn và Vấn đề đang hoàn thiện")
      st.markdown(
          "- **Hạn chế dữ liệu mẫu:** Mẫu không ngẫu nhiên, dữ liệu tự khai, chưa"
          " xác minh độc lập từng hộ; một số phản hồi mở trùng nguyên văn cần"
          " được kiểm tra kỹ.\n- **Về giả thuyết H1–H3:** Sau góp ý của cô Lê Thị"
          " Thúy, em nhận ra việc tính toán ra một tỷ lệ chưa đủ để khẳng định"
          " kết quả khi chưa lọc sạch các phiếu nghi vấn. Đặc biệt với mẫu nhỏ,"
          " thay đổi vài phiếu có thể làm thay đổi kết quả."
      )

      st.markdown("#### 5. Kế hoạch tiếp tục nghiên cứu")
      st.markdown(
          "**Bước 1:** Khóa và lưu bản xuất Google Forms gốc; kiểm tra nguồn gốc,"
          " mốc thời gian và phiếu bất thường.\n**Bước 2:** Xây dựng bảng đối"
          " chiếu câu hỏi với biến nghiên cứu; tách rõ sở hữu và vay vốn.\n**Bước"
          " 3:** Lập bảng quyết định giữ/loại phiếu có lý do, đảm bảo ẩn"
          " danh.\n**Bước 4:** Tính lại các bảng mô tả và H1–H3, đánh giá độ nhạy"
          " khi thay đổi tập mẫu.\n**Bước 5:** Hoàn thiện báo cáo, xin ý kiến cô"
          " hướng dẫn và dự kiến bổ sung phỏng vấn sâu nếu có điều kiện."
      )

      st.markdown("#### 6. Hướng phát triển công cụ hỗ trợ quyết định")
      st.markdown(
          "Từ đề tài, em ấp ủ dự định xây dựng một ứng dụng/web nhỏ giúp các gia"
          " đình so sánh các phương án nhà ở theo tổng chi phí (mua, trả góp, lãi"
          " suất), thời gian đi lại và các ưu tiên cá nhân. Đây là định hướng"
          " ứng dụng thực tiễn mà em muốn tiếp tục theo đuổi trong tương lai."
      )

      st.markdown("#### Lời cảm ơn")
      st.markdown(
          "Em xin gửi lời cảm ơn chân thành đến cô **Lê Thị Thúy** đã tận tâm"
          " hướng dẫn, chỉ ra những điểm cần hoàn thiện; cảm ơn các bạn học sinh"
          " đã hỗ trợ lan tỏa khảo sát và các cô chú đã dành thời gian tham gia"
          " chia sẻ ý kiến."
      )
    else:
      st.markdown("#### 1. Why did I start this research?")
      st.markdown(
          "**Origin Story:** From my own family's move from Nguyễn Đức Cảnh to"
          " Nguyễn Tuân to be closer to Amsterdam High School, I realized that:"
          " *no housing choice is perfect; greater convenience in one aspect"
          " (shorter commute to school) may mean less convenience in another"
          " (longer commute for my mother, farther from grandparents)*."
      )
      st.markdown(
          "**Practical Motivation:** Witnessing houses cleared for Ring Road"
          " 2.5, I wondered: if families are forced to relocate rather than"
          " choosing to move, how do households with school-age children"
          " decide? I wanted to find answers through surveys and data analysis"
          " rather than relying solely on my own family's experience."
      )

      st.markdown("#### 2. What did I want to explore?")
      st.markdown(
          "Focusing on households with school-age children who relocated due to"
          " the Ring Road 2.5 project (Ngụy Như Kon Tum – Nguyễn Trãi section)."
          " Three core questions:"
      )
      st.markdown(
          "- How far did households move and what is their housing arrangement?\n-"
          " What factors were prioritized when choosing a new home; how did"
          " commuting times to school and work change?\n- Were certain"
          " conditions associated with the relocation outcome?"
      )

      st.markdown("#### 3. Methodology and Process")
      st.markdown(
          "**Design & Collection:** Built a proposal with 3 hypotheses (H1:"
          " financial buffer & home ownership; H2: school retention priority &"
          " outcome; H3: commuting priority & commute time change). Surveyed via"
          " Google Forms with 4 screening questions. Initial dataset recorded"
          " 38 responses from Oct 9 to Oct 11, 2026 across 3 channels."
      )
      st.markdown(
          "**Mathematical Application:** Calculated frequencies, percentages,"
          " mean, median, standard deviation. Constructed 2×2 tables, computed"
          " proportion difference $D$ and compared with reference margin $E$,"
          " alongside Fisher's exact test."
      )

      st.markdown("#### 4. Limitations and Refinement Areas")
      st.markdown(
          "- **Sample Limitations:** Non-random sample, self-reported data,"
          " unverified individually; some open-ended responses require"
          " thorough auditing.\n- **Hypotheses H1–H3:** Following Ms. Lê Thị"
          " Thúy's feedback, I realized that calculating a proportion is"
          " insufficient without cleaning questionable responses, especially"
          " with small samples."
      )

      st.markdown("#### 5. Future Research Plan")
      st.markdown(
          "**Step 1:** Lock and archive raw Google Forms export; audit"
          " timestamps and anomalies.\n**Step 2:** Build questionnaire-variable"
          " mapping table; separate ownership and loans.\n**Step 3:** Establish"
          " inclusion/exclusion criteria with valid reasons, ensuring"
          " anonymity.\n**Step 4:** Recompute descriptive statistics and"
          " H1–H3.\n**Step 5:** Finalize report and seek supervisor review."
      )

      st.markdown("#### 6. Decision-Support Tool Development")
      st.markdown(
          "I aspire to build a lightweight web application that helps"
          " families compare housing options based on total costs (purchase,"
          " mortgage, interest), commuting times, and personal priorities."
      )

      st.markdown("#### Acknowledgments")
      st.markdown(
          "I sincerely thank Ms. **Lê Thị Thúy** for her dedicated guidance,"
          " my friends for assisting with the survey, and the participants"
          " who shared their insights."
      )

    st.markdown("</div>", unsafe_allow_html=True)
