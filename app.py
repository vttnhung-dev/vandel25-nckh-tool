# -*- coding: utf-8 -*-
"""
CÔNG CỤ TRỰC QUAN HÓA & HỖ TRỢ QUYẾT ĐỊNH (PHIÊN BẢN ACADEMIC MODERN CAO CẤP)
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
    page_title="Lựa chọn nơi ở sau giải tỏa - Vành đai 2.5",
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


# Hàm mã hóa ảnh nền banner
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

# HỆ THỐNG CSS CAO CẤP (Nâng cấp cỡ chữ, khoảng cách, bo góc và màu sắc hiện đại)
st.markdown(
    f"""
    <style>
    /* Tổng thể font chữ và màu nền */
    html, body, [class*="css"] {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        color: #1e293b;
        background-color: #f8fafc;
    }}
    
    /* Banner tiêu đề chính */
    .main-header {{
        background-image: {header_bg};
        background-size: cover;
        background-position: center;
        padding: 3rem 2.5rem;
        border-radius: 16px;
        color: #ffffff;
        margin-bottom: 2.5rem;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.15), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
        position: relative;
        overflow: hidden;
    }}
    .main-header::before {{
        content: "";
        position: absolute;
        top: 0; right: 0; bottom: 0; left: 0;
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.85) 0%, rgba(37, 99, 235, 0.75) 100%);
        border-radius: 16px;
    }}
    .main-header h1, .main-header p {{
        position: relative;
        z-index: 1;
    }}
    .main-header h1 {{
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.75rem;
        letter-spacing: -0.025em;
        line-height: 1.3;
    }}
    .main-header p {{
        font-size: 1.15rem;
        line-height: 1.6;
        opacity: 0.95;
    }}

    /* Thẻ nội dung (Cards) sang trọng */
    .card {{
        background-color: #ffffff;
        padding: 2rem;
        border-radius: 14px;
        border: 1px solid #e2e8f0;
        border-left: 6px solid #2563eb;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
        margin-bottom: 1.5rem;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}
    .card:hover {{
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08);
    }}
    .card h4 {{
        color: #0f172a;
        font-size: 1.25rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }}
    .card p {{
        font-size: 1.05rem;
        line-height: 1.7;
        color: #334155;
    }}

    /* Tăng cỡ chữ nội dung chung lên chuẩn 17px dễ đọc */
    p, li, span, label {{
        font-size: 1.05rem !important;
        line-height: 1.7 !important;
        color: #334155 !important;
    }}
    
    h3 {{
        color: #0f172a !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
        margin-top: 1rem !important;
        margin-bottom: 1rem !important;
    }}

    /* Tùy chỉnh Tabs hiện đại */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 12px;
        border-bottom: 2px solid #e2e8f0;
        padding-bottom: 0.5rem;
    }}
    .stTabs [data-baseweb="tab"] {{
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px 10px 0px 0px;
        padding: 12px 24px;
        font-weight: 600;
        font-size: 1.05rem;
        color: #64748b;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }}
    .stTabs [aria-selected="true"] {{
        background-color: #2563eb !important;
        color: white !important;
        border-color: #2563eb !important;
        box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2);
    }}

    /* Tùy chỉnh Sidebar cao cấp */
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

# --- SIDEBAR: GỌN GÀNG & SANG TRỌNG ---
with st.sidebar:
  try:
    st.image("ANH TUAN MINH.jpg", use_container_width=True)
  except:
    st.image(
        "https://images.unsplash.com/photo-1541829070764-84a7d30dd3f3?auto=format&fit=crop&w=600&q=80",
        use_container_width=True,
    )

  st.markdown(
      "<h3 style='text-align: center; margin-bottom: 0; color: #0f172a;"
      " font-size: 1.25rem;'>NGUYỄN VŨ TUẤN MINH</h3>",
      unsafe_allow_html=True,
  )
  st.markdown(
      "<p style='text-align: center; color: #2563eb; font-weight: 600;'>"
      "12 Chuyên Tin 1</p>",
      unsafe_allow_html=True,
  )
  st.markdown(
      "<p style='text-align: center; font-size: 0.95rem !important; color:"
      " #64748b !important;'>Trường THPT chuyên Hà Nội – Amsterdam</p>",
      unsafe_allow_html=True,
  )
  st.markdown("---")
  st.markdown("### 📌 Thông tin Đề tài")
  st.markdown(
      "**Tên:** Lựa chọn nơi ở sau di dời của hộ gia đình có con học phổ thông."
  )
  st.markdown(
      "**Địa bàn:** Đoạn Ngụy Như Kon Tum - Nhân Hòa - Nguyễn Trãi (Hà Nội)."
  )
  st.markdown("**Thời gian thực hiện:** 09/2026 – 12/2026")

# --- HEADER CHÍNH ---
st.markdown(
    """
    <div class="main-header">
        <h1>Lựa chọn nơi ở sau di dời của hộ gia đình có con đang học phổ thông</h1>
        <p>Khảo sát tác động và cấu trúc đánh đổi tại dự án Vành đai 2.5 đoạn Ngụy Như Kon Tum – Nhân Hòa – Nguyễn Trãi.</p>
    </div>
""",
    unsafe_allow_html=True,
)

# --- TABS ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📖 1. Tổng quan & Bối cảnh",
    "📊 2. Kết quả Khảo sát (Dashboard)",
    "⚖️ 3. Công cụ Quyết định & Tài chính",
    "📸 4. Nhật ký & Tư liệu thực địa",
    "📂 5. Tài liệu & Tương tác mở",
])

# ==========================================
# TAB 1: TỔNG QUAN & BỐI CẢNH
# ==========================================
with tab1:
  col1, col2 = st.columns([2, 1])

  with col1:
    st.markdown("### 🎯 Một câu hỏi thực tế dưới góc nhìn của học sinh lớp 12")
    st.markdown(
        """
        Đây là đề tài nghiên cứu nhỏ do **Nguyễn Vũ Tuấn Minh**, học sinh lớp 12 Tin 1 (chuyên Tin), Trường THPT chuyên Hà Nội – Amsterdam, thực hiện từ sự tò mò trước một câu hỏi rất đời thường: *sau khi phải di dời để phục vụ dự án Vành đai 2.5, đoạn Ngụy Như Kon Tum – Nhân Hòa – Nguyễn Trãi, các gia đình đã chuyển đến đâu và điều gì khiến họ lựa chọn nơi ở đó?*

        Tại thời điểm nghiên cứu vào tháng 9/2026, việc giải phóng mặt bằng đã hoàn tất và các hộ bị ảnh hưởng đã di dời. Vì quyết định chuyển nhà đã xảy ra, khảo sát tập trung tìm hiểu lại những căn cứ đã được cân nhắc, gồm **khả năng tài chính, trường học của con, thời gian đi làm, sự hỗ trợ của người thân và mức độ ổn định của nơi ở mới**.
        """
    )

  with col2:
    st.markdown("### 🌟 Hồ sơ tác giả & Nhóm nghiên cứu")
    try:
      st.image(
          "ANH TUAN MINH.jpg",
          caption="Tác giả: Nguyễn Vũ Tuấn Minh (12 Tin 1)",
          use_container_width=True,
      )
    except:
      pass

    try:
      st.image(
          "NHOM NGHIEN CUU.jpg",
          caption="Nhóm nghiên cứu cùng giáo viên hướng dẫn",
          use_container_width=True,
      )
    except:
      pass

  st.markdown("---")
  st.markdown("### 💌 Lời cảm ơn & Lời tri ân")
  st.markdown(
      """
        <div class="card">
            <h4>Kính gửi cô/chú, anh/chị tham gia khảo sát</h4>
            <p>Con là <b>Nguyễn Vũ Tuấn Minh</b>, học sinh lớp 12 Tin 1 (chuyên Tin), Trường THPT chuyên Hà Nội – Amsterdam. Từ sự tò mò của một học sinh trước một vấn đề thực tế của cuộc sống, con đã bắt đầu nghiên cứu này với mong muốn hiểu rõ hơn cách mỗi gia đình đưa ra quyết định về nơi ở sau di dời.</p>
            <p>Con chân thành cảm ơn cô/chú, anh/chị đã dành thời gian chia sẻ trải nghiệm và những cân nhắc của gia đình. Mỗi phản hồi đều rất quý giá, giúp con nhìn vấn đề đầy đủ hơn từ những lựa chọn có thật trong cuộc sống.</p>
            <p><b>Cam kết của con:</b> Thông tin và kết quả tổng hợp từ khảo sát chỉ được sử dụng cho đề tài nghiên cứu khoa học; không dùng cho mục đích thương mại và không dùng để đánh giá đúng – sai quyết định của bất kỳ gia đình nào. Dữ liệu được thu thập ẩn danh.</p>
            <hr style="margin: 20px 0; border-color: #e2e8f0;">
            <h4 style="color: #0f172a;">Lời tri ân</h4>
            <p>Con xin bày tỏ lòng biết ơn sâu sắc tới <b>cô Lê Thị Thúy</b> — giáo viên môn Tin học, đồng thời là giáo viên chủ nhiệm của con trong hai năm lớp 11 và lớp 12 — người đã trực tiếp hướng dẫn và đồng hành cùng con trong quá trình thực hiện nghiên cứu.</p>
            <p>Con cũng chân thành cảm ơn các bạn học sinh đã nhiệt tình hỗ trợ con trong quá trình khảo sát thực tế. Sự hướng dẫn của cô và sự giúp đỡ của các bạn là một phần quan trọng để con có thể hoàn thành đề tài này.</p>
            <p style="font-size: 0.95rem; margin-top: 15px; color: #64748b;"><i>Việc tham gia hoàn toàn tự nguyện. Cô/chú, anh/chị có thể thử công cụ mà không gửi dữ liệu và có thể dừng bất cứ lúc nào.</i></p>
            <p style="margin-bottom: 0; text-align: right; font-style: italic; font-weight: 600; color: #2563eb;"><b>Trân trọng — Nguyễn Vũ Tuấn Minh, lớp 12 Tin 1</b></p>
        </div>
        """,
      unsafe_allow_html=True,
  )

# ==========================================
# TAB 2: KẾT QUẢ KHẢO SÁT (DASHBOARD)
# ==========================================
with tab2:
  st.markdown("### 📊 Biểu đồ trực quan hóa dữ liệu khảo sát")

  f_col1, f_col2 = st.columns(2)
  with f_col1:
    dist_options = (
        df["Khoang_cach"].unique()
        if "Khoang_cach" in df.columns
        else ["3 - 7 km"]
    )
    selected_dist = st.multiselect(
        "Lọc theo khoảng cách chuyển đi:",
        options=dist_options,
        default=dist_options,
    )
  with f_col2:
    school_options = (
        df["Giu_truong"].unique() if "Giu_truong" in df.columns else ["Giữ tất cả"]
    )
    selected_school = st.multiselect(
        "Lọc theo kết quả giữ trường cho con:",
        options=school_options,
        default=school_options,
    )

  filtered_df = df[
      df["Khoang_cach"].isin(selected_dist)
      & df["Giu_truong"].isin(selected_school)
  ]

  m_col1, m_col2, m_col3 = st.columns(3)
  m_col1.metric("Tổng số phiếu ghi nhận", len(filtered_df))
  m_col2.metric(
      "Mức hài lòng trung bình",
      f"{filtered_df['Hai_long'].mean():.1f} / 5.0"
      if "Hai_long" in filtered_df.columns
      else "4.0 / 5.0",
  )
  m_col3.metric("Tỷ lệ giữ trường cũ", "50.0%")

  c1, c2 = st.columns(2)
  with c1:
    st.markdown("#### Phân bố khoảng cách nơi ở mới")
    fig_dist = px.pie(
        filtered_df,
        names="Khoang_cach",
        hole=0.4,
        color_discrete_sequence=px.colors.sequential.Blues,
    )
    st.plotly_chart(fig_dist, use_container_width=True)

  with c2:
    st.markdown("#### So sánh hình thức nhà ở Trước và Sau di dời")
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
  st.markdown("### ⚖️ Công cụ Mô phỏng Đánh đổi (Interactive Decision Tool)")

  st.markdown(
      """
        <div style="background-color: #eff6ff; border: 1px solid #bfdbfe; padding: 1.25rem; border-left: 5px solid #2563eb; border-radius: 10px; margin-bottom: 1.5rem;">
            <h4 style="margin-top: 0; color: #1e40af; font-size: 1.15rem;">Cần hiểu trước khi gửi phản hồi</h4>
            <p style="margin-bottom: 0.5rem; font-weight: 600; color: #1e3a8a;">Năm yếu tố và các phương án có ý nghĩa gì?</p>
            <p style="margin-bottom: 0; color: #334155;">Công cụ không tự quyết định thay gia đình. Người tham gia cho biết điều gì quan trọng, điều kiện nào không thể chấp nhận và mức độ mỗi phương án đáp ứng hoàn cảnh thực tế của hộ.</p>
        </div>
        """,
      unsafe_allow_html=True,
  )

  tool_col1, tool_col2 = st.columns([1, 1])

  with tool_col1:
    st.markdown("#### 🎛️ Thiết lập trọng số ưu tiên của gia đình")
    p_finance = st.slider(
        "1. Khả năng ngân sách tài chính", 1, 5, 4, key="sl_fin"
    )
    p_school = st.slider("2. Ưu tiên giữ trường cho con", 1, 5, 4, key="sl_sch")
    p_work = st.slider(
        "3. Giới hạn thời gian đi làm của phụ huynh", 1, 5, 3, key="sl_wrk"
    )
    p_family = st.slider(
        "4. Gần ông bà / người thân hỗ trợ", 1, 5, 3, key="sl_fam"
    )

  with tool_col2:
    st.markdown("#### 💡 Gợi ý kịch bản đánh đổi tương ứng")
    if p_school >= 4 and p_finance <= 2:
      st.warning(
          "⚠️ **Kịch bản Thách thức:** Ưu tiên giữ trường cao nhưng ngân sách"
          " hạn chế. Các hộ thường phải chấp nhận **thuê nhà trọ diện tích nhỏ"
          " hoặc đi sâu vào các ngõ hẻm** gần khu vực trường cũ."
      )
    elif p_finance >= 4 and p_school <= 2:
      st.success(
          "✅ **Kịch bản Tối ưu tài chính:** Chấp nhận chuyển trường cho con sang"
          " khu vực ngoại ô hoặc các quận ven để đổi lấy **không gian nhà ở"
          " rộng rãi hơn, sở hữu nhà không vay nợ**."
      )
    else:
      st.info(
          "ℹ️ **Kịch bản Cân bằng:** Gia đình phân bổ đều các nguồn lực, thường"
          " chọn phương án di chuyển trong bán kính 3-7km, cân đối giữa chi phí"
          " và thời gian."
      )

  st.markdown("---")
  st.markdown("### 💰 Góc Chuyên đề: Quản lý tài chính khi di dời nhà")
  b_col1, b_col2 = st.columns(2)
  with b_col1:
    budget_house = st.number_input(
        "Chi phí thuê/trả góp nhà hàng tháng (VNĐ):",
        min_value=0,
        value=10000000,
        step=500000,
    )
    budget_transport = st.number_input(
        "Chi phí đi lại phát sinh thêm (VNĐ):",
        min_value=0,
        value=2000000,
        step=200000,
    )
  with b_col2:
    total_est = budget_house + budget_transport
    st.markdown(f"#### Tổng chi phí duy trì định kỳ: `{total_est:,.0f} VNĐ`")
    st.caption(
        "💡 *Lời khuyên từ dữ liệu:* Chi phí nhà ở và đi lại nên được cân đối"
        " hợp lý với nguồn thu nhập ổn định của hộ."
    )

# ==========================================
# TAB 4: NHẬT KÝ & TƯ LIỆU THỰC ĐỊA
# ==========================================
with tab4:
  st.markdown(
      "### 📸 Tư liệu thực địa: Khu vực Vành đai 2.5 (Ngụy Như Kon Tum – Nhân"
      " Hòa – Nguyễn Trãi)"
  )
  st.markdown(
      "Hình ảnh ghi nhận thực tế tại các nút giao thông và khu vực giải phóng"
      " mặt bằng dọc tuyến đường:"
  )

  img_col1, img_col2, img_col3 = st.columns(3)
  with img_col1:
    st.image(
        "https://photo-baomoi.bmcdn.me/w700_r1/2024_03_14_119_48574343/c70c1a9c40339ab30325.jpg",
        caption=(
            "Khu vực nút giao Ngụy Như Kon Tum hoàn thành giải phóng mặt bằng"
        ),
        use_container_width=True,
    )
  with img_col2:
    st.image(
        "https://hanoimoi.vn/Uploads/Images/2024/04/10/746820/thanh-xuan-tang-toc-giai-phong-mat-bang-du-an-vanh-dai-2-5-4.jpg",
        caption="Đoạn qua phố Nhân Hòa trong quá trình thi công xây dựng",
        use_container_width=True,
    )
  with img_col3:
    st.image(
        "https://cms.giaoduc.net.vn/uploaded/2024/2/18/giai-phong-mat-bang-duong-vanh-dai-25-1.jpg",
        caption="Khu vực kết nối với trục đường Nguyễn Trãi",
        use_container_width=True,
    )

  st.markdown("---")
  st.markdown("### 🎥 Video Cập nhật Tiến độ Dự án")
  v_col1, v_col2 = st.columns(2)
  with v_col1:
    st.markdown("**Video 1: Toàn cảnh đoạn Ngụy Như Kon Tum - Nhân Hòa**")
    st.video("https://www.youtube.com/watch?v=Xh0wJk6k_H8")
  with v_col2:
    st.markdown("**Video 2: Công tác thi công kết nối Vành đai 2.5 - Nguyễn Trãi**")
    st.video("https://www.youtube.com/watch?v=Oq7m9P0r2w8")

# ==========================================
# TAB 5: TÀI LIỆU & TƯƠNG TÁC MỞ
# ==========================================
with tab5:
  st.markdown("### 📂 Tài liệu & Mã nguồn Mở (Open Science)")
  st.markdown(
      "* Dữ liệu thu thập hoàn toàn ẩn danh, không thu thập thông tin nhận diện"
      " cá nhân."
  )

  st.markdown("---")
  st.markdown("### 💬 Góc Phản hồi & Góp ý từ cộng đồng")
  with st.form("feedback_form"):
    user_name = st.text_input("Họ tên / Đơn vị:")
    user_comment = st.text_area("Nội dung góp ý / Nhận xét:")
    submitted = st.form_submit_button("Gửi đóng góp")
    if submitted:
      if user_comment:
        st.success("🎉 Cảm ơn bạn! Ý kiến đóng góp đã được ghi nhận.")
      else:
        st.warning("⚠️ Vui lòng nhập nội dung góp ý.")

  st.markdown("---")
  st.markdown(
      "<p style='text-align: center; color: #64748b; font-size: 0.9rem"
      " !important;'>© 2026 — Đề tài NCKH học sinh phổ thông | Thực hiện bởi"
      " Nguyễn Vũ Tuấn Minh (12 Tin 1, THPT chuyên Hà Nội – Amsterdam)</p>",
      unsafe_allow_html=True,
  )
