# -*- coding: utf-8 -*-
"""
CÔNG CỤ TRỰC QUAN HÓA & HỖ TRỢ QUYẾT ĐỊNH
Đề tài: Lựa chọn nơi ở sau di dời của hộ gia đình có con đang học phổ thông
        bị ảnh hưởng bởi dự án Vành đai 2.5 đoạn Ngụy Như Kon Tum - Nguyễn Trãi

Chạy:  streamlit run app.py
Thư viện: streamlit, pandas, numpy, plotly

LƯU Ý: toàn bộ số liệu trong ứng dụng là DỮ LIỆU GIẢ LẬP để minh họa cấu trúc
phân tích. Khi có dữ liệu khảo sát thật (đã mã hóa, ẩn danh), chỉ cần thay hàm
`tao_du_lieu_gia_lap()` bằng lệnh đọc file CSV (xem chú thích tại hàm).
"""

import os

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# =============================================================================
# PHẦN 0. CẤU HÌNH CHUNG
# =============================================================================
st.set_page_config(
    page_title="Nơi ở sau di dời - Vành đai 2.5",
    page_icon="🏘️",
    layout="wide",
)

# Đường dẫn tới sổ tay Python (Jupyter/Colab/GitHub). Thay bằng đường dẫn thật.
NOTEBOOK_URL = ""

# Bảng màu thống nhất toàn ứng dụng (xanh navy - xanh ngọc - vàng đồng - xám)
NAVY = "#12355B"      # màu chủ đạo, dùng cho "Sau di dời"
SLATE = "#A9B8CC"     # màu nhạt, dùng cho "Trước di dời"
TEAL = "#2A7F8E"      # nhấn: giảm / tích cực
GOLD = "#C8963E"      # nhấn: điểm nổi bật
RED = "#B5483A"       # nhấn: tăng / cảnh báo
GREY = "#8A94A6"      # trung tính: không đổi

# Thứ tự các nhóm (cố định để biểu đồ luôn xếp đúng thứ tự logic)
KHOANG_CACH = ["Dưới 3 km", "3–7 km", "Trên 7–15 km",
               "Trên 15 km (trong Hà Nội)", "Ngoài Hà Nội"]
NHA_O = ["Sở hữu, không vay", "Sở hữu, có vay", "Thuê",
         "Ở cùng người thân", "Tạm thời/khác"]
TG_DI_HOC = ["Dưới 15 phút", "15–30 phút", "31–45 phút",
             "46–60 phút", "Trên 60 phút"]
TG_DI_LAM = ["Không thường xuyên", "Dưới 30 phút", "30–45 phút",
             "46–60 phút", "Trên 60 phút"]
GIU_TRUONG = ["Giữ tất cả", "Một số chuyển", "Tất cả chuyển"]
YEU_TO = ["Khả năng tài chính", "Ưu tiên giữ trường",
          "Giới hạn thời gian đi làm", "Hỗ trợ từ người thân"]
# Tên cột trong file CSV tương ứng với 4 yếu tố (viết không dấu để tránh lỗi mã hóa)
COT_QT = {"Khả năng tài chính": "qt_tai_chinh",
          "Ưu tiên giữ trường": "qt_giu_truong",
          "Giới hạn thời gian đi làm": "qt_di_lam",
          "Hỗ trợ từ người thân": "qt_nguoi_than"}
# File dữ liệu đã mã hóa, đặt cùng thư mục với app.py
FILE_DU_LIEU = "processed_data.csv"


def hien_thi_bieu_do(fig, chieu_cao=380):
    """Định dạng chung cho mọi biểu đồ Plotly rồi hiển thị.
    Tự nhận biết phiên bản Streamlit để dùng đúng tham số chiều rộng."""
    fig.update_layout(
        template="plotly_white",
        height=chieu_cao,
        margin=dict(l=10, r=10, t=50, b=10),
        font=dict(family="Segoe UI, Roboto, Arial, sans-serif", size=13,
                  color="#1F2A37"),
        title=dict(font=dict(size=16, color=NAVY)),
        legend=dict(orientation="h", yanchor="bottom", y=-0.28, x=0),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    phien_ban = tuple(int(x) for x in st.__version__.split(".")[:2])
    if phien_ban >= (1, 50):
        st.plotly_chart(fig, width="stretch")
    else:
        st.plotly_chart(fig, use_container_width=True)


# Giao diện: CSS nhẹ để tạo cảm giác trang trọng, sạch sẽ
st.markdown(
    f"""
    <style>
      .block-container {{ padding-top: 1.6rem; max-width: 1200px; }}
      .banner {{
          background: linear-gradient(120deg, {NAVY} 0%, #1E4E82 100%);
          color: #fff; padding: 1.4rem 1.6rem; border-radius: 12px;
          margin-bottom: 1rem;
      }}
      .banner h1 {{ font-size: 1.45rem; margin: 0 0 .35rem 0; color: #fff; line-height: 1.35; }}
      .banner p  {{ margin: 0; opacity: .9; font-size: .95rem; }}
      .card {{
          border: 1px solid #DCE3EC; border-left: 5px solid {GOLD};
          border-radius: 8px; padding: .9rem 1.1rem; background: #FAFBFD;
          margin-bottom: .6rem;
      }}
      .flow {{ display: flex; gap: .5rem; align-items: stretch; flex-wrap: wrap; }}
      .flow .step {{
          flex: 1 1 180px; background: #F1F5FA; border: 1px solid #C9D6E6;
          border-top: 4px solid {NAVY}; border-radius: 8px; padding: .8rem;
      }}
      .flow .step b {{ color: {NAVY}; }}
      .flow .arrow {{ align-self: center; font-size: 1.6rem; color: {GOLD}; }}
      .warn {{
          background: #FFF7E6; border: 1px solid #F0D9A8; border-radius: 8px;
          padding: .7rem 1rem; font-size: .92rem;
      }}
      .disclaimer {{
          background: #FDECEA; border: 1px solid #E8B4AC; border-radius: 8px;
          padding: .8rem 1rem; color: #7A2B20; font-weight: 600;
      }}
      button[data-baseweb="tab"] {{ font-weight: 600; }}
    </style>
    """,
    unsafe_allow_html=True,
)

# =============================================================================
# PHẦN 1. DỮ LIỆU GIẢ LẬP (cấu trúc khớp bảng hỏi 30 câu, 30–45 phiếu)
# =============================================================================
@st.cache_data
def tao_du_lieu_gia_lap(n: int, seed: int = 2026) -> pd.DataFrame:
    """Sinh bộ dữ liệu giả lập, mỗi dòng = 1 hộ (1 người đại diện trả lời).

    Để dùng dữ liệu thật đã mã hóa, thay toàn bộ hàm này bằng:
        return pd.read_csv("04_public/du_lieu_ma_hoa.csv")
    với các cột trùng tên như bên dưới (xem từ điển biến ở Tab 4).

    Nguyên tắc sinh: có quy luật hợp lý (hộ chuyển càng xa thì càng dễ đổi
    trường, thời gian đi lại càng dễ tăng) nhưng chỉ mang tính minh họa.
    """
    rng = np.random.default_rng(seed)  # seed cố định -> kết quả lặp lại được
    df = pd.DataFrame({"ma_phieu": [f"H{i:03d}" for i in range(1, n + 1)]})

    # --- (a) Khoảng cách nơi ở mới (RQ1)
    df["khoang_cach"] = rng.choice(KHOANG_CACH, size=n,
                                   p=[0.22, 0.33, 0.25, 0.12, 0.08])
    idx_kc = df["khoang_cach"].map(KHOANG_CACH.index).to_numpy()

    # --- (b) Hình thức nhà ở trước di dời
    df["nha_o_truoc"] = rng.choice(NHA_O, size=n,
                                   p=[0.50, 0.10, 0.25, 0.10, 0.05])

    # --- (c) Hình thức nhà ở sau di dời: chọn theo "ma trận chuyển đổi"
    #     (hàng = hình thức trước, cột = hình thức sau). Mỗi hàng cộng = 1.
    ma_tran = {
        "Sở hữu, không vay": [0.45, 0.30, 0.10, 0.10, 0.05],
        "Sở hữu, có vay":    [0.15, 0.55, 0.15, 0.10, 0.05],
        "Thuê":              [0.02, 0.08, 0.75, 0.10, 0.05],
        "Ở cùng người thân": [0.05, 0.10, 0.20, 0.60, 0.05],
        "Tạm thời/khác":     [0.05, 0.10, 0.35, 0.20, 0.30],
    }
    df["nha_o_sau"] = [rng.choice(NHA_O, p=ma_tran[t]) for t in df["nha_o_truoc"]]

    # --- (d) Kết quả giữ trường: xác suất giữ giảm dần theo khoảng cách
    p_giu = np.array([0.90, 0.70, 0.40, 0.20, 0.10])[idx_kc]
    u = rng.random(n)
    giu = []
    for xac_suat, x in zip(p_giu, u):
        if x < xac_suat:
            giu.append("Giữ tất cả")
        elif x < xac_suat + (1 - xac_suat) * 0.4:
            giu.append("Một số chuyển")
        else:
            giu.append("Tất cả chuyển")
    df["giu_truong"] = giu

    # --- (e) Thời gian đi học & đi làm: "trước" chọn ngẫu nhiên, "sau" = trước
    #     + độ dịch chuyển (-1, 0, +1, +2 nhóm), độ dịch phụ thuộc khoảng cách.
    dich = [-1, 0, 1, 2]
    p_dich = {0: [.10, .55, .30, .05], 1: [.10, .35, .40, .15],
              2: [.10, .20, .40, .30], 3: [.10, .10, .40, .40],
              4: [.10, .10, .30, .50]}

    def dich_nhom(idx_truoc, idx_kc_i, nho_nhat):
        """Trả về chỉ số nhóm sau di dời, giới hạn trong [nho_nhat, 4]."""
        d = rng.choice(dich, p=p_dich[idx_kc_i])
        return int(np.clip(idx_truoc + d, nho_nhat, 4))

    hoc_truoc = rng.choice(len(TG_DI_HOC), size=n, p=[.25, .35, .22, .13, .05])
    lam_truoc = rng.choice(len(TG_DI_LAM), size=n, p=[.08, .30, .30, .22, .10])
    hoc_sau = [dich_nhom(a, k, 0) for a, k in zip(hoc_truoc, idx_kc)]
    # Nhóm 0 của đi làm = "Không thường xuyên" -> giữ nguyên, không tính thay đổi
    lam_sau = [0 if a == 0 else dich_nhom(a, k, 1)
               for a, k in zip(lam_truoc, idx_kc)]

    df["tg_hoc_truoc"] = [TG_DI_HOC[i] for i in hoc_truoc]
    df["tg_hoc_sau"] = [TG_DI_HOC[i] for i in hoc_sau]
    df["tg_lam_truoc"] = [TG_DI_LAM[i] for i in lam_truoc]
    df["tg_lam_sau"] = [TG_DI_LAM[i] for i in lam_sau]

    # --- (f) Biến "thay đổi" so sánh thứ bậc nhóm sau với trước
    def nhan_thay_doi(truoc, sau, khong_xac_dinh=False):
        if khong_xac_dinh:
            return "Không xác định"
        return "Tăng" if sau > truoc else ("Giảm" if sau < truoc else "Không đổi")

    df["doi_tg_hoc"] = [nhan_thay_doi(a, b) for a, b in zip(hoc_truoc, hoc_sau)]
    df["doi_tg_lam"] = [nhan_thay_doi(a, b, a == 0)
                        for a, b in zip(lam_truoc, lam_sau)]

    # --- (g) Mức quan trọng 4 yếu tố tại thời điểm chọn nơi ở (thang 1–5)
    trung_binh = {"Khả năng tài chính": 4.2, "Ưu tiên giữ trường": 3.8,
                  "Giới hạn thời gian đi làm": 3.6, "Hỗ trợ từ người thân": 3.2}
    for ten, tb in trung_binh.items():
        df[COT_QT[ten]] = np.clip(np.round(rng.normal(tb, 1.0, n)), 1, 5).astype(int)

    # Mức nguồn lực tài chính hộ huy động được tại thời điểm chốt nơi ở (1–5).
    # Thấp = 1–2 (dùng cho giả thuyết H1)
    df["kha_nang_tai_chinh"] = np.clip(np.round(rng.normal(3.0, 1.1, n)), 1, 5).astype(int)

    # --- (h) Số phương án đã cân nhắc và mức hài lòng sau di dời (thang 1–5)
    df["so_phuong_an"] = rng.integers(1, 7, size=n)
    df["hai_long"] = np.clip(np.round(rng.normal(3.6 - 0.25 * idx_kc, 0.9)),
                             1, 5).astype(int)
    return df


# =============================================================================
# PHẦN 2. THANH BÊN (sidebar): thông tin & bộ lọc mẫu
# =============================================================================
with st.sidebar:
    st.markdown("### ⚙️ Thiết lập dữ liệu mẫu")
    if os.path.exists(FILE_DU_LIEU):
        # Có file CSV -> dùng dữ liệu trong file, không cần thanh trượt
        st.success(f"Đang dùng file {FILE_DU_LIEU}")
        n_phieu = None
    else:
        # Không có file -> tự sinh dữ liệu giả lập, cho chọn cỡ mẫu
        n_phieu = st.slider("Số phiếu giả lập", min_value=30, max_value=45,
                            value=36, step=1,
                            help="Khớp mục tiêu 30–45 phiếu hợp lệ trong đề cương.")
        st.caption("Không tìm thấy processed_data.csv nên ứng dụng tự sinh dữ liệu giả lập.")
    st.markdown("---")
    st.markdown("**Người thực hiện:** Tuấn Minh  \n"
                "**Đơn vị:** THPT chuyên Hà Nội – Amsterdam  \n"
                "**Thời gian:** 09/2026 – 12/2026")

if n_phieu is None:
    df = pd.read_csv(FILE_DU_LIEU, encoding="utf-8-sig")
else:
    df = tao_du_lieu_gia_lap(n_phieu)

# Banner đầu trang
st.markdown(
    """
    <div class="banner">
      <h1>Lựa chọn nơi ở sau di dời của hộ gia đình có con đang học phổ thông
      bị ảnh hưởng bởi dự án Vành đai 2.5 đoạn Ngụy Như Kon Tum – Nguyễn Trãi</h1>
      <p>Công cụ trực quan hóa kết quả nghiên cứu và minh họa các đánh đổi trong lựa chọn nơi ở</p>
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown(
    "<div class='warn'>⚠️ <b>Số liệu trong ứng dụng là dữ liệu giả lập</b> "
    "để minh họa cấu trúc phân tích, <b>không phải kết quả khảo sát thực tế</b>.</div>",
    unsafe_allow_html=True,
)
st.write("")

tab1, tab2, tab3, tab4 = st.tabs([
    "📘 Tổng quan & Bối cảnh",
    "📊 Kết quả khảo sát (Dashboard)",
    "🧭 Công cụ hỗ trợ quyết định",
    "🔓 Tài liệu & Mã nguồn mở",
])

# =============================================================================
# TAB 1. TỔNG QUAN & BỐI CẢNH NGHIÊN CỨU
# =============================================================================
with tab1:
    st.subheader("Tên đề tài")
    st.markdown(
        "<div class='card'><b>Lựa chọn nơi ở sau di dời của hộ gia đình có con đang "
        "học phổ thông bị ảnh hưởng bởi dự án Vành đai 2.5 đoạn Ngụy Như Kon Tum – "
        "Nguyễn Trãi</b><br>Nghiên cứu quan sát cắt ngang hồi cứu, mang tính khám phá.</div>",
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns([3, 2], gap="large")
    with c1:
        st.subheader("Bối cảnh thực tiễn")
        st.markdown(
            """
- Đoạn Vành đai 2.5 từ Ngụy Như Kon Tum đến Nguyễn Trãi đi qua **khu dân cư hiện hữu**.
- Các nguồn chính thức tháng 3/2026 cho biết dự án vào giai đoạn **giải phóng mặt bằng và thi công**.
- Theo thông tin thực địa tháng 9/2026, các hộ chịu ảnh hưởng **đã rời nơi ở cũ**.
- Vì vậy nghiên cứu quan sát **quyết định đã xảy ra**: chuyển đến đâu, ở hình thức nào,
  giữ hay đổi trường cho con, thời gian đi học – đi làm thay đổi ra sao, đã chấp nhận đánh đổi gì.
            """
        )
        st.markdown(
            "<div class='warn'>📌 Thông tin hoàn tất giải phóng mặt bằng cần được bổ sung "
            "nguồn chính thức hoặc xác nhận kiểm chứng được trước khi nộp đề tài.</div>",
            unsafe_allow_html=True,
        )
    with c2:
        st.subheader("Câu hỏi nghiên cứu")
        st.markdown(
            """
- **RQ1.** Hộ chuyển đến đâu, dùng hình thức nhà ở nào, xem xét bao nhiêu phương án?
- **RQ2.** Trường học, thời gian đi học – đi làm, hỗ trợ từ người thân thay đổi thế nào?
- **RQ3.** Hộ ưu tiên, bị giới hạn và đánh đổi những gì?
- **RQ4.** Tài chính, ưu tiên giữ trường, ưu tiên thời gian đi làm liên hệ ra sao với 3 kết quả tương ứng?
            """
        )

    st.subheader("Khung khái niệm")
    # Sơ đồ 4 bước dựng bằng HTML/CSS
    st.markdown(
        """
        <div class="flow">
          <div class="step"><b>1. Điều kiện</b><br>Tài chính, quy mô hộ, con đang học,
          nơi làm việc, hỗ trợ từ người thân <i>tại thời điểm chốt nơi ở</i></div>
          <div class="arrow">➜</div>
          <div class="step"><b>2. Quá trình</b><br>Số phương án cân nhắc, thời gian tìm,
          yếu tố ưu tiên, ràng buộc loại phương án</div>
          <div class="arrow">➜</div>
          <div class="step"><b>3. Lựa chọn</b><br>Khoảng cách nơi ở mới,
          hình thức nhà ở, giữ/đổi trường</div>
          <div class="arrow">➜</div>
          <div class="step"><b>4. Đánh giá sau di dời</b><br>Thay đổi thời gian đi học – đi làm,
          hỗ trợ gia đình, mức hài lòng</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("Nghiên cứu đo các mối liên hệ giữa các nhóm thông tin; "
               "**không** xác nhận quan hệ nhân quả và **không** suy rộng cho toàn bộ hộ bị ảnh hưởng.")

    with st.expander("Phạm vi kết luận & giới hạn của nghiên cứu"):
        st.markdown(
            """
- Không ước lượng tác động nhân quả của dự án đối với lựa chọn nơi ở.
- Mẫu phi xác suất (có chủ đích + giới thiệu tự nguyện), có thể thiếu hộ chuyển xa.
- Không đánh giá mức bồi thường; không thu số tiền bồi thường hay địa chỉ chính xác.
- Sai lệch hồi tưởng: người trả lời có thể hợp lý hóa quyết định sau khi biết kết quả.
- Hài lòng hiện tại không phải bằng chứng rằng lựa chọn ban đầu là tối ưu.
            """
        )

# =============================================================================
# TAB 2. DASHBOARD KẾT QUẢ KHẢO SÁT (dữ liệu giả lập)
# =============================================================================
with tab2:
    st.subheader("Kết quả khảo sát trực quan")

    # --- Hàng chỉ số tổng hợp
    ty_le_giu = (df["giu_truong"] == "Giữ tất cả").mean() * 100
    co_lam = df[df["doi_tg_lam"] != "Không xác định"]
    ty_le_tang_lam = (co_lam["doi_tg_lam"] == "Tăng").mean() * 100
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Số phiếu hợp lệ (giả lập)", f"{len(df)}")
    m2.metric("Giữ trường cho tất cả con", f"{ty_le_giu:.0f}%")
    m3.metric("Thời gian đi làm tăng", f"{ty_le_tang_lam:.0f}%",
              help=f"Tính trên {len(co_lam)} hộ có hành trình đi làm thường xuyên.")
    m4.metric("Hài lòng trung vị (1–5)", f"{df['hai_long'].median():.1f}")
    st.write("")

    # --- Biểu đồ 1: phân bố khoảng cách nơi ở mới (RQ1)
    dem = (df["khoang_cach"].value_counts().reindex(KHOANG_CACH).fillna(0)
           .astype(int).rename_axis("Khoảng cách").reset_index(name="Số hộ"))
    dem["Tỷ lệ"] = dem["Số hộ"] / dem["Số hộ"].sum() * 100
    dem["Nhãn"] = dem.apply(lambda r: f"{r['Số hộ']} hộ ({r['Tỷ lệ']:.0f}%)", axis=1)
    fig1 = px.bar(dem, x="Khoảng cách", y="Số hộ", text="Nhãn",
                  title="1. Phân bố khoảng cách từ nơi ở mới đến nơi ở cũ",
                  color_discrete_sequence=[NAVY])
    fig1.update_traces(textposition="outside", cliponaxis=False)
    fig1.update_layout(xaxis_title=None, yaxis_title="Số hộ",
                       yaxis_range=[0, dem["Số hộ"].max() * 1.25])
    hien_thi_bieu_do(fig1)
    st.caption("Khoảng cách do người trả lời ước tính, không phải tọa độ đo chính xác.")

    # --- Biểu đồ 2: hình thức nhà ở trước và sau (RQ1)
    st.markdown("---")
    cot_a, cot_b = st.columns([3, 2], gap="large")
    with cot_a:
        truoc = df["nha_o_truoc"].value_counts().reindex(NHA_O).fillna(0)
        sau = df["nha_o_sau"].value_counts().reindex(NHA_O).fillna(0)
        fig2 = go.Figure()
        fig2.add_bar(x=NHA_O, y=truoc.values, name="Trước di dời",
                     marker_color=SLATE, text=truoc.values.astype(int),
                     textposition="outside")
        fig2.add_bar(x=NHA_O, y=sau.values, name="Sau di dời",
                     marker_color=NAVY, text=sau.values.astype(int),
                     textposition="outside")
        fig2.update_layout(barmode="group",
                           title="2. Hình thức nhà ở trước và sau di dời",
                           yaxis_title="Số hộ",
                           yaxis_range=[0, max(truoc.max(), sau.max()) * 1.25])
        hien_thi_bieu_do(fig2)
    with cot_b:
        # Bảng chuyển đổi (hàng = trước, cột = sau) dạng bản đồ nhiệt
        chuyen = pd.crosstab(df["nha_o_truoc"], df["nha_o_sau"]).reindex(
            index=NHA_O, columns=NHA_O, fill_value=0)
        fig2b = px.imshow(chuyen.values, x=NHA_O, y=NHA_O, text_auto=True,
                          color_continuous_scale=["#FFFFFF", NAVY],
                          aspect="auto",
                          title="Bảng chuyển đổi (dòng: trước → cột: sau)")
        fig2b.update_layout(coloraxis_showscale=False, xaxis_title=None,
                            yaxis_title=None)
        fig2b.update_xaxes(tickangle=-35)
        hien_thi_bieu_do(fig2b)

    # --- Biểu đồ 3: thay đổi thời gian đi học và đi làm (RQ2)
    st.markdown("---")
    st.markdown("##### 3. Thay đổi thời gian đi học và đi làm")
    lua_chon = st.radio("Xem theo", ["Đi học của con", "Đi làm của phụ huynh"],
                        horizontal=True)
    if lua_chon == "Đi học của con":
        cot_truoc, cot_sau, cot_doi = "tg_hoc_truoc", "tg_hoc_sau", "doi_tg_hoc"
        thu_tu, du_lieu = TG_DI_HOC, df
    else:
        cot_truoc, cot_sau, cot_doi = "tg_lam_truoc", "tg_lam_sau", "doi_tg_lam"
        thu_tu, du_lieu = TG_DI_LAM, df

    g1, g2 = st.columns([3, 2], gap="large")
    with g1:
        a = du_lieu[cot_truoc].value_counts().reindex(thu_tu).fillna(0)
        b = du_lieu[cot_sau].value_counts().reindex(thu_tu).fillna(0)
        fig3 = go.Figure()
        fig3.add_bar(x=thu_tu, y=a.values, name="Trước di dời", marker_color=SLATE)
        fig3.add_bar(x=thu_tu, y=b.values, name="Sau di dời", marker_color=NAVY)
        fig3.update_layout(barmode="group", yaxis_title="Số hộ",
                           title=f"Phân bố thời gian một chiều – {lua_chon.lower()}")
        hien_thi_bieu_do(fig3)
    with g2:
        thu_tu_doi = ["Giảm", "Không đổi", "Tăng"]
        cnt = du_lieu[cot_doi].value_counts().reindex(thu_tu_doi).fillna(0)
        fig3b = px.pie(names=cnt.index, values=cnt.values, hole=0.55,
                       color=cnt.index,
                       color_discrete_map={"Giảm": TEAL, "Không đổi": GREY,
                                           "Tăng": RED},
                       title="Tỷ lệ hộ thay đổi thời gian đi lại")
        fig3b.update_traces(textinfo="label+percent", sort=False)
        fig3b.update_layout(showlegend=False)
        hien_thi_bieu_do(fig3b)
    if lua_chon == "Đi làm của phụ huynh":
        st.caption("Chỉ tính hộ có hành trình đi làm thường xuyên khi xác định "
                   "tăng/giảm (nhóm 'Không thường xuyên' bị loại khỏi biểu đồ tròn).")

    # --- Biểu đồ 4 (bổ trợ): mức quan trọng của 4 yếu tố (RQ3)
    st.markdown("---")
    tb = pd.DataFrame({
        "Yếu tố": YEU_TO,
        "Điểm trung bình": [df[COT_QT[t]].mean() for t in YEU_TO],
    }).sort_values("Điểm trung bình")
    fig4 = px.bar(tb, x="Điểm trung bình", y="Yếu tố", orientation="h",
                  text=tb["Điểm trung bình"].round(2),
                  title="4. Mức quan trọng của các yếu tố tại thời điểm chọn nơi ở (thang 1–5)",
                  color_discrete_sequence=[TEAL])
    fig4.update_layout(xaxis_range=[0, 5], yaxis_title=None)
    fig4.update_traces(textposition="outside", cliponaxis=False)
    hien_thi_bieu_do(fig4, chieu_cao=300)

    with st.expander("Xem bảng dữ liệu giả lập (đã ẩn danh)"):
        st.dataframe(df, hide_index=True)

# =============================================================================
# TAB 3. CÔNG CỤ TƯƠNG TÁC HỖ TRỢ QUYẾT ĐỊNH
# =============================================================================
# 5 phương án giả lập. Điểm 1–5 cho từng yếu tố theo thứ tự YEU_TO:
# [tài chính, giữ trường, thời gian đi làm, hỗ trợ người thân]
# Điểm càng cao = phương án càng "dễ đáp ứng" yếu tố đó. Đây là GIẢ ĐỊNH MINH HỌA
# do nhóm nghiên cứu đặt ra, sẽ được hiệu chỉnh theo xu hướng khảo sát thật.
PHUONG_AN = [
    {"ten": "A. Thuê nhà gần khu cũ (dưới 3 km)", "diem": [2, 5, 4, 3],
     "duoc": "Giữ trường cũ, đi làm thuận tiện",
     "doi": "Tiền thuê cao, không gian nhỏ, chưa có tài sản sở hữu"},
    {"ten": "B. Mua nhà có vay (3–7 km)", "diem": [2, 4, 3, 3],
     "duoc": "Có nhà sở hữu, vẫn tương đối gần trường",
     "doi": "Gánh nặng trả nợ dài hạn, thời gian di chuyển tăng nhẹ"},
    {"ten": "C. Nhà sở hữu giá mềm (7–15 km)", "diem": [4, 2, 2, 3],
     "duoc": "Chi phí nhà ở thấp hơn, diện tích lớn hơn",
     "doi": "Nhiều khả năng phải đổi trường, đi làm xa hơn"},
    {"ten": "D. Ở cùng/gần người thân", "diem": [5, 3, 3, 5],
     "duoc": "Tiết kiệm chi phí, có người đưa đón, trông nom con",
     "doi": "Ít riêng tư, sinh hoạt chung, phụ thuộc điều kiện người thân"},
    {"ten": "E. Ngoài Hà Nội / vùng xa", "diem": [5, 1, 1, 2],
     "duoc": "Chi phí nhà ở thấp nhất, quỹ đất rộng",
     "doi": "Gần như chắc chắn đổi trường, đi làm rất xa, xa mạng lưới hỗ trợ"},
]


def tinh_diem(trong_so):
    """Điểm khớp (0–100) = tổng(trọng số × điểm phương án) / (5 × tổng trọng số).
    Trọng số chính là mức quan trọng 1–5 do người dùng chọn."""
    tong = sum(trong_so)
    ket_qua = []
    for pa in PHUONG_AN:
        tu = sum(w * s for w, s in zip(trong_so, pa["diem"]))
        diem = tu / (5 * tong) * 100
        # Xung đột: yếu tố người dùng đặt quan trọng (>=4) nhưng phương án đáp ứng kém (<=2)
        xung_dot = [YEU_TO[i] for i in range(4)
                    if trong_so[i] >= 4 and pa["diem"][i] <= 2]
        ket_qua.append({
            "Phương án": pa["ten"],
            "Mức khớp ưu tiên (%)": round(diem, 1),
            "Điều đạt được": pa["duoc"],
            "Điều phải đánh đổi": pa["doi"],
            "Xung đột với ưu tiên cao": ", ".join(xung_dot) if xung_dot else "—",
        })
    return pd.DataFrame(ket_qua).sort_values("Mức khớp ưu tiên (%)",
                                             ascending=False).reset_index(drop=True)


def goi_y_danh_doi(w):
    """Bộ quy tắc 'nếu – thì' mô tả đánh đổi thường gặp theo tổ hợp ưu tiên.
    w = [tài chính, giữ trường, đi làm, người thân]; >=4 là cao, <=2 là thấp."""
    tc, tr, dl, ht = w
    ds = []
    if tr >= 4 and tc >= 4:
        ds.append("**Giữ trường + ngân sách hạn chế** → xu hướng thuê nhà trọ/nhà nhỏ gần trường, "
                   "hoặc chấp nhận tăng thời gian di chuyển của người lớn.")
    if tr >= 4 and tc <= 2:
        ds.append("**Giữ trường + tài chính thoải mái** → có thể chọn nhà gần trường (thuê hoặc vay), "
                   "đánh đổi là chi phí nhà ở/nợ cao hơn.")
    if dl >= 4 and tr >= 4:
        ds.append("**Vừa gần trường vừa gần nơi làm** → vùng lựa chọn rất hẹp, giá thuê/mua cao, ít phương án.")
    if dl >= 4 and tc >= 4:
        ds.append("**Đi làm gần + ngân sách hạn chế** → thường phải chấp nhận diện tích nhỏ hơn hoặc thuê thay vì sở hữu.")
    if ht >= 4 and tc >= 4:
        ds.append("**Cần người thân hỗ trợ + ngân sách hạn chế** → ở cùng/gần người thân là phương án cân bằng, "
                   "đánh đổi là quyền riêng tư và không gian sinh hoạt.")
    if ht >= 4 and tr >= 4:
        ds.append("**Cần người thân + giữ trường** → chỉ khả thi nếu người thân ở gần trường cũ; nếu không phải ưu tiên một trong hai.")
    if tr <= 2 and tc >= 4:
        ds.append("**Ít gắn với trường cũ + ngân sách hạn chế** → có thể đổi trường để đổi lấy nhà rẻ/rộng hơn; "
                   "đánh đổi là con phải thích nghi môi trường mới.")
    if not ds:
        ds.append("Các ưu tiên tương đối cân bằng, chưa xuất hiện đánh đổi nổi trội; "
                  "hãy xem cột 'Xung đột với ưu tiên cao' của từng phương án.")
    return ds


with tab3:
    st.subheader("Công cụ so sánh phương án theo mức ưu tiên")
    st.markdown(
        "Chấm mức quan trọng từ **1 (ít quan trọng)** đến **5 (rất quan trọng)** cho từng yếu tố, "
        "rồi bấm nút để xem các đánh đổi thường gặp. Công cụ **không dự báo một hộ cụ thể** "
        "và **không xác định phương án đúng**."
    )

    cs, ck = st.columns([2, 3], gap="large")
    with cs:
        st.markdown("##### Mức quan trọng (1–5)")
        w_tc = st.slider("1. Khả năng tài chính (cần tiết kiệm chi phí nhà ở)", 1, 5, 3)
        w_tr = st.slider("2. Ưu tiên giữ trường cho con", 1, 5, 3)
        w_dl = st.slider("3. Giới hạn thời gian đi làm (muốn đi làm gần)", 1, 5, 3)
        w_ht = st.slider("4. Hỗ trợ từ ông bà/người thân", 1, 5, 3)
        bam_nut = st.button("Phân tích kịch bản đánh đổi", type="primary")

    # Ghi nhớ đã bấm nút để kết quả không biến mất khi kéo thanh trượt
    if bam_nut:
        st.session_state["da_phan_tich"] = True

    with ck:
        if not st.session_state.get("da_phan_tich"):
            st.info("Chọn mức quan trọng ở bên trái rồi bấm **Phân tích kịch bản đánh đổi**.")
        else:
            trong_so = [w_tc, w_tr, w_dl, w_ht]
            bang = tinh_diem(trong_so)

            # Biểu đồ cột ngang: mức khớp của từng phương án
            fig5 = px.bar(bang.sort_values("Mức khớp ưu tiên (%)"),
                          x="Mức khớp ưu tiên (%)", y="Phương án", orientation="h",
                          text="Mức khớp ưu tiên (%)",
                          title="Mức khớp giữa phương án giả lập và ưu tiên của bạn",
                          color_discrete_sequence=[NAVY])
            fig5.update_layout(xaxis_range=[0, 100], yaxis_title=None)
            fig5.update_traces(textposition="outside", cliponaxis=False)
            hien_thi_bieu_do(fig5, chieu_cao=330)

    if st.session_state.get("da_phan_tich"):
        st.markdown("##### Bảng phân tích đánh đổi")
        st.dataframe(bang, hide_index=True)

        st.markdown("##### Đánh đổi thường gặp với tổ hợp ưu tiên bạn chọn")
        for dong in goi_y_danh_doi([w_tc, w_tr, w_dl, w_ht]):
            st.markdown(f"- {dong}")

        with st.expander("Cách tính (để giải thích trước hội đồng)"):
            st.markdown(
                "- Mỗi phương án có điểm 1–5 cho 4 yếu tố (giả định minh họa).\n"
                "- **Mức khớp (%) = Σ(mức quan trọng × điểm phương án) ÷ (5 × Σ mức quan trọng) × 100.**\n"
                "- 'Xung đột' xuất hiện khi yếu tố được chấm ≥ 4 nhưng phương án chỉ đạt ≤ 2 điểm.\n"
                "- Mức khớp cao **không có nghĩa** đó là lựa chọn đúng; chỉ phản ánh sự phù hợp với ưu tiên đã nhập."
            )

    # Tuyên bố từ chối trách nhiệm (BẮT BUỘC) - luôn hiển thị dưới công cụ
    st.write("")
    st.markdown(
        "<div class='disclaimer'>⚠️ Công cụ này chỉ mang tính chất minh họa dựa trên dữ liệu "
        "khảo sát nghiên cứu khoa học, không phải lời khuyên tài chính hay pháp lý tuyệt đối.</div>",
        unsafe_allow_html=True,
    )

# =============================================================================
# TAB 4. TÀI LIỆU & MÃ NGUỒN MỞ (OPEN SCIENCE)
# =============================================================================
with tab4:
    st.subheader("Bộ dữ liệu đã mã hóa và ẩn danh")
    d1, d2 = st.columns(2, gap="large")
    with d1:
        st.markdown("##### ✅ Dữ liệu có trong bộ công khai")
        st.markdown(
            """
- Mã phiếu ngẫu nhiên (H001, H002…), không liên hệ được với người trả lời.
- Khoảng cách theo **nhóm** (không phải số chính xác).
- Hình thức nhà ở trước – sau, giữ/đổi trường, nhóm thời gian đi lại.
- Mức quan trọng các yếu tố (thang 1–5), mức hài lòng (thang 1–5).
            """
        )
    with d2:
        st.markdown("##### 🚫 Không thu thập")
        st.markdown(
            """
- Họ tên, số điện thoại, email.
- Địa chỉ cũ/mới, vị trí GPS.
- Tên trường, tên nơi làm việc.
- Thu nhập, dư nợ, số tiền bồi thường chính xác.
            """
        )
    st.markdown(
        "<div class='card'>Nghiên cứu tuân thủ nguyên tắc: tự nguyện, người tham gia từ 18 tuổi, "
        "mỗi hộ một phiếu, phiếu gốc lưu riêng và chỉ công khai kết quả tổng hợp.</div>",
        unsafe_allow_html=True,
    )

    st.subheader("Từ điển biến (rút gọn)")
    tu_dien = pd.DataFrame([
        ["ma_phieu", "Mã phiếu ẩn danh", "Văn bản"],
        ["khoang_cach", "Khoảng cách nơi ở mới – cũ (nhóm)", "5 nhóm"],
        ["nha_o_truoc / nha_o_sau", "Hình thức nhà ở trước/sau di dời", "5 nhóm"],
        ["giu_truong", "Kết quả giữ trường cho các con", "3 nhóm"],
        ["tg_hoc_truoc / tg_hoc_sau", "Thời gian đi học một chiều", "5 nhóm"],
        ["tg_lam_truoc / tg_lam_sau", "Thời gian đi làm một chiều", "5 nhóm"],
        ["doi_tg_hoc / doi_tg_lam", "Thay đổi: Giảm / Không đổi / Tăng / Không xác định", "Phân loại"],
        ["qt_tai_chinh, qt_giu_truong, qt_di_lam, qt_nguoi_than", "Mức quan trọng của 4 yếu tố khi chọn nơi ở", "Thang 1–5"],
        ["kha_nang_tai_chinh", "Mức nguồn lực tài chính huy động được tại thời điểm chốt nơi ở (thấp = 1–2)", "Thang 1–5"],
        ["so_phuong_an", "Số phương án đã cân nhắc", "Số nguyên"],
        ["hai_long", "Mức hài lòng sau di dời", "Thang 1–5"],
    ], columns=["Tên biến", "Ý nghĩa", "Kiểu dữ liệu"])
    st.dataframe(tu_dien, hide_index=True)

    # Cho tải bộ dữ liệu giả lập dạng CSV (utf-8-sig để Excel đọc đúng tiếng Việt)
    st.download_button(
        "⬇️ Tải dữ liệu giả lập (CSV)",
        data=df.to_csv(index=False).encode("utf-8-sig"),
        file_name="du_lieu_gia_lap_vanh_dai_2_5.csv",
        mime="text/csv",
    )

    st.subheader("Sổ tay Python phân tích dữ liệu")
    st.markdown(
        """
Sổ tay thực hiện toàn bộ quy trình và **tái tạo được mọi bảng, biểu đồ** từ dữ liệu đã xử lý:

1. Nhập dữ liệu → 2. Kiểm tra điều kiện tham gia → 3. Mã hóa biến →
4. Tạo biến thay đổi trước–sau → 5. Xuất bảng mô tả → 6. Ba kiểm tra đã định trước (H1–H3) → 7. Vẽ biểu đồ.
        """
    )
    if NOTEBOOK_URL:
        st.markdown(f"🔗 [Mở hướng dẫn đọc sổ tay Python]({NOTEBOOK_URL})")
    else:
        st.info("Đường dẫn sổ tay sẽ được cập nhật (gán vào biến `NOTEBOOK_URL` ở đầu file app.py).")

    with st.expander("Quy tắc kiểm tra giả thuyết (H1–H3)"):
        st.markdown(
            "- Chỉ kiểm tra khi tổng mẫu ≥ 30 và mỗi nhóm so sánh có ≥ 5 quan sát; "
            "nếu không, chỉ báo cáo số lượng và tỷ lệ.\n"
            "- Dùng bảng 2×2 và kiểm định Fisher; kết quả chỉ mang tính khám phá.\n"
            "- Kết quả không ủng hộ giả thuyết thì giữ nguyên, không đổi giả thuyết sau khi xem dữ liệu."
        )

st.markdown("---")
st.caption("Đề tài NCKH học sinh phổ thông • Dữ liệu minh họa giả lập • Mã nguồn mở phục vụ tái lập kết quả")
