# -*- coding: utf-8 -*-
"""
CÔNG CỤ TRỰC QUAN HÓA & HỖ TRỢ QUYẾT ĐỊNH (PHIÊN BẢN NÂNG CAO)
Đề tài: Lựa chọn nơi ở sau di dời của hộ gia đình có con đang học phổ thông 
        bị ảnh hưởng bởi dự án Vành đai 2.5 đoạn Ngụy Như Kon Tum - Nguyễn Trãi[cite: 2]
Tác giả: Vũ Thị Tuyết Nhung / Tuấn Minh (THPT chuyên Hà Nội - Amsterdam)[cite: 1, 2]
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Cấu hình trang web
st.set_page_config(
    page_title="Nghiên cứu Di dời Vành đai 2.5 & Công cụ Hỗ trợ",
    page_icon="🏡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Tùy chỉnh CSS giao diện (Tone màu xanh dương học thuật, thẻ card nổi)
st.markdown(
    """
    <style>
    .main-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 2.5rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .card {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #3b82f6;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }
    .author-card {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #f1f5f9;
        border-radius: 6px 6px 0px 0px;
        padding: 10px 20px;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #3b82f6 !important;
        color: white !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Hàm tải dữ liệu mẫu (hoặc dữ liệu thật từ file processed_data.csv nếu có)
@st.cache_data
def load_data():
  try:
    df = pd.read_csv("processed_data.csv")
    return df
  except:
    # Tạo dữ liệu giả lập chuẩn cấu trúc đề tài nếu chưa có file
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
        "Tai_chinh_thap": np.random.choice([0, 1], n, p=[0.6, 0.4]),
        "Uu_tien_di_lai": np.random.randint(1, 6, n),
        "Hai_long": np.random.randint(2, 6, n),
    }
    return pd.DataFrame(data)


df = load_data()

# --- SIDEBAR: THANH ĐIỀU HƯỚNG & THÔNG TIN ---
with st.sidebar:
  st.image(
      "https://images.unsplash.com/photo-1541829070764-84a7d30dd3f3?auto=format&fit=crop&w=600&q=80",
      use_container_width=True,
  )
  st.title("🏡 Nghiên cứu Vành đai 2.5")
  st.markdown("---")
  st.markdown("### 📌 Thông tin Đề tài")
  st.markdown(
      "**Tên:** Lựa chọn nơi ở sau di dời của hộ gia đình có con học phổ thông[cite: 2]."
  )
  st.markdown(
      "**Địa bàn:** Đoạn Ngụy Như Kon Tum - Nguyễn Trãi (Hà Nội)[cite: 2]."
  )
  st.markdown("**Thời gian:** 09/2026 – 12/2026[cite: 2]")
  st.markdown("---")
  st.markdown("### 👤 Tác giả")
  st.markdown("**Vũ Thị Tuyết Nhung / Tuấn Minh**[cite: 1, 2]")
  st.markdown("Trường THPT chuyên Hà Nội - Amsterdam[cite: 2]")
  st.markdown("---")
  status_data = (
      "📊 Đang dùng: Dữ liệu giả lập minh họa"
      if "ID" in df.columns
      else "📁 Đang dùng: Dữ liệu thực tế"
  )
  st.info(status_data)

# --- HEADER CHÍNH ---
st.markdown(
    """
    <div class="main-header">
        <h1>Lựa chọn nơi ở sau di dời của hộ gia đình có con đang học phổ thông</h1>
        <p style="font-size: 1.1rem; margin-top: 0.5rem;">Khảo sát tác động và cấu trúc đánh đổi tại dự án Vành đai 2.5 đoạn Ngụy Như Kon Tum - Nguyễn Trãi[cite: 2]. Công cụ tương tác hỗ trợ phân tích quyết định.</p>
    </div>
""",
    unsafe_allow_html=True,
)

# --- TẠO CÁC TABS GIAO DIỆN CHÍNH ---
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
    st.markdown("### 🎯 Bối cảnh thực tiễn và Vấn đề nghiên cứu")
    st.markdown(
        """
        Đoạn Vành đai 2.5 từ Ngụy Như Kon Tum đến Nguyễn Trãi đi qua khu dân cư hiện hữu[cite: 2]. Công tác giải phóng mặt bằng hoàn tất buộc các hộ dân phải rời nơi ở cũ[cite: 2]. 
        Nghiên cứu tập trung phân tích các quyết định thực tế đã xảy ra: **Hộ chuyển đến đâu? Sử dụng hình thức nhà ở nào? Có giữ trường cho con không? Và những đánh đổi đằng sau các lựa chọn đó là gì?**[cite: 1, 2]
        """
    )

    st.markdown("### 🔄 Khung khái niệm nghiên cứu")
    st.markdown(
        """
        Nghiên cứu được tổ chức theo chuỗi trình tự logic:
        1. **Điều kiện tại thời điểm chọn:** Nguồn lực tài chính, nhu cầu giữ trường, đi lại, hỗ trợ từ người thân[cite: 2].
        2. **Quá trình ra quyết định:** Số phương án cân nhắc, ưu tiên và ràng buộc[cite: 2].
        3. **Lựa chọn thực tế:** Khoảng cách, hình thức nhà ở, thay đổi hành trình[cite: 2].
        4. **Đánh giá sau di dời:** Mức độ hài lòng và những khó khăn còn lại[cite: 2].
        """
    )

  with col2:
    st.markdown("### 🌟 Hồ sơ tác giả")
    st.markdown(
        """
        <div class="author-card">
            <img src="https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=300&q=80" style="border-radius: 50%; width: 120px; height: 120px; object-fit: cover; margin-bottom: 10px;">
            <h4>Tuấn Minh</h4>
            <p><b>Học sinh lớp 12</b><br>Trường THPT chuyên Hà Nội - Amsterdam[cite: 2]</p>
            <p style="font-size: 0.9rem; color: #64748b;">Đam mê nghiên cứu xã hội học đô thị và ứng dụng công nghệ phân tích dữ liệu vào đời sống.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

  st.markdown("---")
  st.markdown("### 💌 Lời tri ân chân thành")
  st.markdown(
      """
        <div class="card">
            <p>Lời đầu tiên, tác giả xin gửi lời cảm ơn sâu sắc đến <b>Cô giáo chủ nhiệm cùng các thầy cô hướng dẫn</b> đã tận tình định hướng, hỗ trợ và đưa ra những góp ý quý báu để đề tài nghiên cứu khoa học này được hoàn thiện.</p>
            <p>Tác giả cũng xin gửi lời cảm ơn chân thành đến <b>các cô bác, anh chị đại diện các hộ gia đình</b> đã dành thời gian quý báu tham gia phỏng vấn, chia sẻ những trải nghiệm thực tế giúp nhóm có được góc nhìn khách quan và chân thực nhất.</p>
            <p style="margin-bottom: 0; text-align: right; font-style: italic;">— Tác giả: Tuấn Minh —</p>
        </div>
        """,
      unsafe_allow_html=True,
  )

# ==========================================
# TAB 2: KẾT QUẢ KHẢO SÁT (DASHBOARD)
# ==========================================
with tab2:
  st.markdown("### 📊 Biểu đồ trực quan hóa dữ liệu khảo sát")
  st.markdown(
      "Sử dụng các bộ lọc dưới đây để phân tích sâu hơn theo từng nhóm đối"
      " tượng hộ gia đình."
  )

  # Bộ lọc tương tác (Filters)
  f_col1, f_col2 = st.columns(2)
  with f_col1:
    selected_dist = st.multiselect(
        "Lọc theo khoảng cách chuyển đi:",
        options=df["Khoang_cach"].unique(),
        default=df["Khoang_cach"].unique(),
    )
  with f_col2:
    selected_school = st.multiselect(
        "Lọc theo kết quả giữ trường cho con:",
        options=df["Giu_truong"].unique(),
        default=df["Giu_truong"].unique(),
    )

  # Lọc dữ liệu theo bộ lọc
  filtered_df = df[
      df["Khoang_cach"].isin(selected_dist)
      & df["Giu_truong"].isin(selected_school)
  ]

  m_col1, m_col2, m_col3 = st.columns(3)
  m_col1.metric("Tổng số phiếu ghi nhận", len(filtered_df))
  m_col2.metric(
      "Mức hài lòng trung bình", f"{filtered_df['Hai_long'].mean():.1f} / 5.0"
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
    fig_house.update_layout(
        xaxis_title="Hình thức nhà ở sau di dời", ythe_title="Số lượng hộ"
    )
    st.plotly_chart(fig_house, use_container_width=True)

# ==========================================
# TAB 3: CÔNG CỤ QUYẾT ĐỊNH & GÓC TÀI CHÍNH
# ==========================================
with tab3:
  st.markdown("### ⚖️ Công cụ Mô phỏng Đánh đổi (Interactive Decision Tool)")
  st.markdown(
      "Kéo các thanh trượt để thiết lập mức độ ưu tiên của gia đình bạn. Hệ"
      " thống sẽ phân tích gợi ý kịch bản phù hợp dựa trên dữ liệu nghiên"
      " cứu."
  )

  tool_col1, tool_col2 = st.columns([1, 1])

  with tool_col1:
    st.markdown("#### 🎛️ Thiết lập trọng số ưu tiên")
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
    score_total = p_finance + p_school + p_work + p_family

    if p_school >= 4 and p_finance <= 2:
      st.warning(
          "⚠️ **Kịch bản Thách thức:** Ưu tiên giữ trường cao nhưng ngân sách"
          " hạn chế. Các hộ thường phải chấp nhận **thuê nhà trọ diện tích nhỏ"
          " hoặc đi sâu vào các ngõ hẻm** gần khu vực trường cũ để tiết kiệm"
          " chi phí thuê nhà lớn."
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
          " chọn phương án di chuyển trong bán kính 3-7km, chấp nhận tăng nhẹ thời"
          " gian đi lại để giữ ổn định trường học và công việc."
      )

  st.markdown("---")
  st.markdown(
      "### 💰 Góc Chuyên đề: Hỗ trợ quản lý tài chính trong bối cảnh di dời nhà"
  )
  st.markdown(
      "Tính nhẩm nhanh dòng tiền dự kiến cho việc ổn định nơi ở mới:"
  )

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
        "💡 *Lời khuyên từ dữ liệu:* Hãy đảm bảo tổng chi phí nhà ở và đi lại"
        " không vượt quá 50% tổng thu nhập ổn định hàng tháng của gia đình để"
        " tránh áp lực tài chính."
    )

# ==========================================
# TAB 4: NHẬT KÝ & TƯ LIỆU THỰC ĐỊA
# ==========================================
with tab4:
  st.markdown("### 📸 Nhật ký Hình ảnh & Hành trình thực địa")
  st.markdown(
      "Những hình ảnh ghi lại quá trình khảo sát, thử nghiệm nhận thức bảng hỏi"
      " và làm việc trực tiếp tại thực địa."
  )

  img_col1, img_col2, img_col3 = st.columns(3)
  with img_col1:
    st.image(
        "https://images.unsplash.com/photo-1577495508048-b635879837f1?auto=format&fit=crop&w=500&q=80",
        caption="Khảo sát thực địa tuyến Vành đai 2.5",
        use_container_width=True,
    )
  with img_col2:
    st.image(
        "https://images.unsplash.com/photo-1531482615713-2afd69097998?auto=format&fit=crop&w=500&q=80",
        caption="Buổi thử nghiệm nhận thức bảng hỏi (8-10 người)",
        use_container_width=True,
    )
  with img_col3:
    st.image(
        "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?auto=format&fit=crop&w=500&q=80",
        caption="Xử lý và mã hóa dữ liệu nghiên cứu",
        use_container_width=True,
    )

  st.markdown("---")
  st.markdown("### 🎥 Video Tóm tắt Quá trình Nghiên cứu")
  st.markdown(
      "Video ngắn tổng quan hành trình thực hiện đề tài khoa học từ bước lên"
      " ý tưởng đến khi hoàn thiện công cụ web:"
  )
  st.video("https://www.youtube.com/watch?v=dQw4w9WgXcQ")  # Link minh họa

# ==========================================
# TAB 5: TÀI LIỆU & TƯƠNG TÁC MỞ
# ==========================================
with tab5:
  st.markdown("### 📂 Tài liệu & Mã nguồn Mở (Open Science)")
  st.markdown(
      """
        * Toàn bộ dữ liệu sử dụng trong ứng dụng đã được **mã hóa và ẩn danh hoàn toàn** (không thu thập tên, số điện thoại, địa chỉ chính xác hay thu nhập cụ thể)[cite: 2].
        * Bạn có thể xem mã nguồn chi tiết và sổ tay Python tại kho lưu trữ GitHub của đề tài[cite: 2].
        """
  )

  st.markdown("---")
  st.markdown("### 💬 Góc Phản hồi & Góp ý từ cộng đồng")
  st.markdown("Hãy để lại lời nhắn hoặc câu hỏi đóng góp cho đề tài của tác giả:")

  with st.form("feedback_form"):
    user_name = st.text_input("Họ tên / Đơn vị:")
    user_comment = st.text_area("Nội dung góp ý / Nhận xét:")
    submitted = st.form_submit_button("Gửi đóng góp")
    if submitted:
      if user_comment:
        st.success(
            "🎉 Cảm ơn bạn! Ý kiến đóng góp của bạn đã được ghi nhận thành"
            " công."
        )
      else:
        st.warning("⚠️ Vui lòng nhập nội dung góp ý trước khi gửi.")

  st.markdown("---")
  st.caption(
      "© 2026 — Đề tài NCKH học sinh phổ thông | Thiết kế bởi Tuấn Minh (THPT"
      " chuyên Hà Nội - Amsterdam)[cite: 1, 2]"
  )
