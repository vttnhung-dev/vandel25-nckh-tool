# -*- coding: utf-8 -*-
"""
CÔNG CỤ TRỰC QUAN HÓA & HỖ TRỢ QUYẾT ĐỊNH  (phiên bản 2)
Đề tài: Lựa chọn nơi ở sau di dời của hộ gia đình có con đang học phổ thông
        bị ảnh hưởng bởi dự án Vành đai 2.5 đoạn Ngụy Như Kon Tum - Nguyễn Trãi

Chạy:  streamlit run app.py
Thư viện: streamlit (>=1.40), pandas, numpy, plotly

Điểm mới của phiên bản 2:
  1. Giao diện tông xanh dương, các khối nội dung dạng thẻ (card) nổi.
  2. Tab 3: mô phỏng đánh đổi CẬP NHẬT THỜI GIAN THỰC khi kéo thanh trượt.
  3. Tab 2: bộ lọc tương tác theo nhóm đối tượng.

LƯU Ý: số liệu trong ứng dụng là DỮ LIỆU GIẢ LẬP để minh họa cấu trúc phân tích.
Khi có dữ liệu khảo sát thật (đã mã hóa, ẩn danh), chỉ cần thay file
processed_data.csv (cùng tên cột) - không cần sửa mã nguồn.
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

# File dữ liệu đã mã hóa, đặt cùng thư mục với app.py
FILE_DU_LIEU = "processed_data.csv"

# ---- Bảng màu: xanh dương chủ đạo + vài màu nhấn tiết chế
B900 = "#0A2F5C"   # xanh rất đậm: tiêu đề, chữ nhấn
B700 = "#1257A8"   # xanh chủ đạo: cột "Sau di dời", phương án nổi bật
B500 = "#2F80D0"   # xanh vừa
B200 = "#BBD4F0"   # xanh nhạt: cột "Trước di dời"
B50 = "#EEF4FB"    # xanh rất nhạt: nền khối phụ
TEAL = "#1F9E9A"   # nhấn: giảm / tích cực
AMBER = "#E0A030"  # nhấn: điểm nổi bật
RED = "#C0503F"    # nhấn: tăng / cảnh báo
GREY = "#8A94A6"   # trung tính: không đổi

# ---- Thứ tự các nhóm (cố định để biểu đồ luôn xếp đúng thứ tự logic)
KHOANG_CACH = ["Dưới 3 km", "3–7 km", "Trên 7–15 km",
               "Trên 15 km (trong Hà Nội)", "Ngoài Hà Nội"]
NHA_O = ["Sở hữu, không vay", "Sở hữu, có vay", "Thuê",
         "Ở cùng người thân", "Tạm thời/khác"]
TG_DI_HOC = ["Dưới 15 phút", "15–30 phút", "31–45 phút",
             "46–60 phút", "Trên 60 phút"]
TG_DI_LAM = ["Không thường xuyên", "Dưới 30 phút", "30–45 phút",
             "46–60 phút", "Trên 60 phút"]
GIU_TRUONG = ["Giữ tất cả", "Một số chuyển", "Tất cả chuyển"]
NHOM_TAI_CHINH = ["Thấp (1–2)", "Trung bình (3)", "Cao (4–5)"]
NHOM_DI_LAM = ["Đi làm thường xuyên", "Không thường xuyên"]

YEU_TO = ["Khả năng tài chính", "Ưu tiên giữ trường",
          "Giới hạn thời gian đi làm", "Hỗ trợ từ người thân"]
# Tên cột CSV tương ứng với 4 yếu tố (viết không dấu để tránh lỗi mã hóa)
COT_QT = {"Khả năng tài chính": "qt_tai_chinh",
          "Ưu tiên giữ trường": "qt_giu_truong",
          "Giới hạn thời gian đi làm": "qt_di_lam",
          "Hỗ trợ từ người thân": "qt_nguoi_than"}


# =============================================================================
# PHẦN 1. GIAO DIỆN: CSS, HÀM DỰNG THẺ, HÀM VẼ BIỂU ĐỒ
# =============================================================================
st.markdown(
    f"""
    <style>
      /* Nền trang xanh rất nhạt để các thẻ trắng "nổi" lên */
      .stApp {{ background: #F3F7FC; }}
      [data-testid="stSidebar"] {{ background: #E6EEF9; }}
      .block-container {{ padding-top: 1.4rem; max-width: 1240px; }}

      /* Thẻ nổi: mọi st.container(key="card_...") đều có khung này */
      div[class*="st-key-card"] {{
          background: #FFFFFF; border: 1px solid #DCE7F5; border-radius: 14px;
          box-shadow: 0 6px 20px rgba(18, 87, 168, .10);
          padding: 1.1rem 1.3rem; margin-bottom: .6rem;
      }}
      /* Thẻ bộ lọc: nền xanh nhạt để phân biệt với thẻ biểu đồ */
      div[class*="st-key-card_loc"] {{ background: {B50}; border-color: #C9DBF2; }}

      h1, h2, h3, h4 {{ color: {B900}; }}
      .card-title {{ font-size: 1.05rem; font-weight: 700; color: {B900};
                     margin: 0 0 .5rem 0; }}
      .card-title small {{ font-weight: 400; color: #5B6B82; margin-left: .4rem; }}

      /* Banner đầu trang */
      .banner {{
          background: linear-gradient(120deg, {B900} 0%, {B700} 100%);
          color: #fff; padding: 1.5rem 1.7rem; border-radius: 16px;
          box-shadow: 0 8px 24px rgba(10, 47, 92, .25); margin-bottom: .9rem;
      }}
      .banner h1 {{ font-size: 1.4rem; margin: 0 0 .4rem 0; color: #fff; line-height: 1.4; }}
      .banner p  {{ margin: 0; opacity: .9; font-size: .95rem; }}
      .pill {{ display: inline-block; background: rgba(255,255,255,.18);
               border: 1px solid rgba(255,255,255,.35); border-radius: 999px;
               padding: .1rem .7rem; font-size: .78rem; margin-bottom: .5rem; }}

      /* Ô chỉ số (st.metric) */
      [data-testid="stMetric"] {{
          background: #FFFFFF; border: 1px solid #DCE7F5; border-radius: 12px;
          padding: .8rem 1rem; box-shadow: 0 4px 14px rgba(18, 87, 168, .08);
      }}
      [data-testid="stMetricValue"] {{ color: {B700}; }}

      /* Ô chỉ số tự xuống dòng (dùng trong Tab 3) */
      .kpi {{ background: {B50}; border: 1px solid #C9DBF2; border-radius: 12px;
              padding: .6rem .9rem; height: 100%; }}
      .kpi .nhan {{ font-size: .8rem; color: #5B6B82; }}
      .kpi .tri {{ font-size: 1.15rem; font-weight: 700; color: {B700}; line-height: 1.3; }}

      /* Sơ đồ khung khái niệm */
      .flow {{ display: flex; gap: .5rem; align-items: stretch; flex-wrap: wrap; }}
      .flow .step {{ flex: 1 1 180px; background: {B50}; border: 1px solid #C9DBF2;
                     border-top: 4px solid {B700}; border-radius: 10px; padding: .8rem; }}
      .flow .step b {{ color: {B900}; }}
      .flow .arrow {{ align-self: center; font-size: 1.5rem; color: {B500}; }}

      /* Khối lưu ý và tuyên bố từ chối trách nhiệm */
      .warn {{ background: #FFF7E6; border: 1px solid #F0D9A8; border-radius: 10px;
               padding: .7rem 1rem; font-size: .92rem; }}
      .disclaimer {{ background: #FDECEA; border: 1px solid #E8B4AC; border-radius: 10px;
                     padding: .8rem 1rem; color: #7A2B20; font-weight: 600; }}
      .insight {{ background: {B50}; border-left: 5px solid {B700}; border-radius: 8px;
                  padding: .7rem 1rem; margin-bottom: .6rem; }}

      /* Thanh tab dạng viên thuốc */
      button[data-baseweb="tab"] {{ font-weight: 600; }}
    </style>
    """,
    unsafe_allow_html=True,
)


def tieu_de_the(tieu_de, phu=""):
    """Tiêu đề nhỏ đặt ở đầu mỗi thẻ."""
    phu_html = f"<small>{phu}</small>" if phu else ""
    st.markdown(f"<div class='card-title'>{tieu_de}{phu_html}</div>",
                unsafe_allow_html=True)


def o_chi_so(nhan, gia_tri):
    """Ô chỉ số dạng HTML: chữ dài tự xuống dòng thay vì bị cắt bằng dấu ba chấm."""
    st.markdown(f"<div class='kpi'><div class='nhan'>{nhan}</div>"
                f"<div class='tri'>{gia_tri}</div></div>", unsafe_allow_html=True)


def hien_thi_bieu_do(fig, chieu_cao=360, le=None, chu_giai_tren=False):
    """Định dạng chung cho mọi biểu đồ Plotly rồi hiển thị.
    Tự nhận biết phiên bản Streamlit để dùng đúng tham số chiều rộng."""
    fig.update_layout(
        template="plotly_white",
        height=chieu_cao,
        margin=le or dict(l=10, r=10, t=30, b=10),
        font=dict(family="Segoe UI, Roboto, Arial, sans-serif", size=13,
                  color="#1F2A37"),
        legend=(dict(orientation="h", yanchor="bottom", y=1.02, x=0) if chu_giai_tren
                else dict(orientation="h", yanchor="bottom", y=-0.3, x=0)),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    phien_ban = tuple(int(x) for x in st.__version__.split(".")[:2])
    if phien_ban >= (1, 50):
        st.plotly_chart(fig, width="stretch")
    else:
        st.plotly_chart(fig, use_container_width=True)


# =============================================================================
# PHẦN 2. DỮ LIỆU (đọc CSV, nếu không có thì sinh giả lập)
# =============================================================================
@st.cache_data
def tao_du_lieu_gia_lap(n: int, seed: int = 2026) -> pd.DataFrame:
    """Sinh bộ dữ liệu giả lập, mỗi dòng = 1 hộ (1 người đại diện trả lời).

    Nguyên tắc sinh: có quy luật hợp lý (hộ chuyển càng xa thì càng dễ đổi
    trường, thời gian đi lại càng dễ tăng) nhưng chỉ mang tính minh họa.
    """
    rng = np.random.default_rng(seed)  # seed cố định -> kết quả lặp lại được
    df = pd.DataFrame({"ma_phieu": [f"H{i:03d}" for i in range(1, n + 1)]})

    # (a) Khoảng cách nơi ở mới (RQ1)
    df["khoang_cach"] = rng.choice(KHOANG_CACH, size=n,
                                   p=[0.22, 0.33, 0.25, 0.12, 0.08])
    idx_kc = df["khoang_cach"].map(KHOANG_CACH.index).to_numpy()

    # (b) Hình thức nhà ở trước di dời
    df["nha_o_truoc"] = rng.choice(NHA_O, size=n,
                                   p=[0.50, 0.10, 0.25, 0.10, 0.05])

    # (c) Hình thức nhà ở sau di dời: chọn theo "ma trận chuyển đổi"
    #     (hàng = hình thức trước, cột = hình thức sau). Mỗi hàng cộng = 1.
    ma_tran = {
        "Sở hữu, không vay": [0.45, 0.30, 0.10, 0.10, 0.05],
        "Sở hữu, có vay":    [0.15, 0.55, 0.15, 0.10, 0.05],
        "Thuê":              [0.02, 0.08, 0.75, 0.10, 0.05],
        "Ở cùng người thân": [0.05, 0.10, 0.20, 0.60, 0.05],
        "Tạm thời/khác":     [0.05, 0.10, 0.35, 0.20, 0.30],
    }
    df["nha_o_sau"] = [rng.choice(NHA_O, p=ma_tran[t]) for t in df["nha_o_truoc"]]

    # (d) Kết quả giữ trường: xác suất giữ giảm dần theo khoảng cách
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

    # (e) Thời gian đi học & đi làm: "sau" = "trước" + độ dịch chuyển nhóm
    dich = [-1, 0, 1, 2]
    p_dich = {0: [.10, .55, .30, .05], 1: [.10, .35, .40, .15],
              2: [.10, .20, .40, .30], 3: [.10, .10, .40, .40],
              4: [.10, .10, .30, .50]}

    def dich_nhom(idx_truoc, idx_kc_i, nho_nhat):
        """Chỉ số nhóm sau di dời, giới hạn trong [nho_nhat, 4]."""
        d = rng.choice(dich, p=p_dich[idx_kc_i])
        return int(np.clip(idx_truoc + d, nho_nhat, 4))

    hoc_truoc = rng.choice(len(TG_DI_HOC), size=n, p=[.25, .35, .22, .13, .05])
    lam_truoc = rng.choice(len(TG_DI_LAM), size=n, p=[.08, .30, .30, .22, .10])
    hoc_sau = [dich_nhom(a, k, 0) for a, k in zip(hoc_truoc, idx_kc)]
    # Nhóm 0 của đi làm = "Không thường xuyên" -> giữ nguyên
    lam_sau = [0 if a == 0 else dich_nhom(a, k, 1)
               for a, k in zip(lam_truoc, idx_kc)]

    df["tg_hoc_truoc"] = [TG_DI_HOC[i] for i in hoc_truoc]
    df["tg_hoc_sau"] = [TG_DI_HOC[i] for i in hoc_sau]
    df["tg_lam_truoc"] = [TG_DI_LAM[i] for i in lam_truoc]
    df["tg_lam_sau"] = [TG_DI_LAM[i] for i in lam_sau]

    # (f) Biến "thay đổi": so sánh thứ bậc nhóm sau với trước
    def nhan_thay_doi(truoc, sau, khong_xac_dinh=False):
        if khong_xac_dinh:
            return "Không xác định"
        return "Tăng" if sau > truoc else ("Giảm" if sau < truoc else "Không đổi")

    df["doi_tg_hoc"] = [nhan_thay_doi(a, b) for a, b in zip(hoc_truoc, hoc_sau)]
    df["doi_tg_lam"] = [nhan_thay_doi(a, b, a == 0)
                        for a, b in zip(lam_truoc, lam_sau)]

    # (g) Mức quan trọng 4 yếu tố tại thời điểm chọn nơi ở (thang 1–5)
    trung_binh = {"Khả năng tài chính": 4.2, "Ưu tiên giữ trường": 3.8,
                  "Giới hạn thời gian đi làm": 3.6, "Hỗ trợ từ người thân": 3.2}
    for ten, tb in trung_binh.items():
        df[COT_QT[ten]] = np.clip(np.round(rng.normal(tb, 1.0, n)), 1, 5).astype(int)

    # Mức nguồn lực tài chính hộ huy động được tại thời điểm chốt nơi ở (1–5);
    # thấp = 1–2 (dùng cho giả thuyết H1)
    df["kha_nang_tai_chinh"] = np.clip(np.round(rng.normal(3.0, 1.1, n)), 1, 5).astype(int)

    # (h) Số phương án đã cân nhắc và mức hài lòng sau di dời (thang 1–5)
    df["so_phuong_an"] = rng.integers(1, 7, size=n)
    df["hai_long"] = np.clip(np.round(rng.normal(3.6 - 0.25 * idx_kc, 0.9)),
                             1, 5).astype(int)
    return df


def them_cot_phan_nhom(d: pd.DataFrame) -> pd.DataFrame:
    """Tạo các cột PHÂN NHÓM dùng cho bộ lọc (không sửa dữ liệu gốc)."""
    d = d.copy()
    # Nhóm nguồn lực tài chính: thấp 1–2, trung bình 3, cao 4–5 (quy ước của đề cương)
    d["nhom_tai_chinh"] = pd.cut(d["kha_nang_tai_chinh"], bins=[0, 2, 3, 5],
                                 labels=NHOM_TAI_CHINH).astype(str)
    # Nhóm hành trình đi làm: có đi làm thường xuyên hay không
    d["nhom_di_lam"] = np.where(d["tg_lam_truoc"] == "Không thường xuyên",
                                NHOM_DI_LAM[1], NHOM_DI_LAM[0])
    # Nhóm ưu tiên giữ trường: cao = 4–5 (quy ước của đề cương)
    d["nhom_uu_tien_truong"] = np.where(d[COT_QT["Ưu tiên giữ trường"]] >= 4,
                                        "Ưu tiên giữ trường cao (4–5)",
                                        "Thấp/trung bình (1–3)")
    return d


# ---- Nạp dữ liệu: ưu tiên file CSV, không có thì sinh giả lập
with st.sidebar:
    st.markdown("### ⚙️ Dữ liệu")
    if os.path.exists(FILE_DU_LIEU):
        st.success(f"Đang dùng file {FILE_DU_LIEU}")
        df_goc = pd.read_csv(FILE_DU_LIEU, encoding="utf-8-sig")
    else:
        n_phieu = st.slider("Số phiếu giả lập", 30, 45, 36, 1,
                            help="Khớp mục tiêu 30–45 phiếu hợp lệ trong đề cương.")
        st.caption("Không tìm thấy processed_data.csv nên ứng dụng tự sinh dữ liệu giả lập.")
        df_goc = tao_du_lieu_gia_lap(n_phieu)
    st.markdown("---")
    st.markdown("**Người thực hiện:** Tuấn Minh  \n"
                "**Đơn vị:** THPT chuyên Hà Nội – Amsterdam  \n"
                "**Thời gian:** 09/2026 – 12/2026")

CAC_COT_GOC = list(df_goc.columns)      # để tải về đúng các cột gốc, không kèm cột phân nhóm
df = them_cot_phan_nhom(df_goc)

# ---- Banner đầu trang
st.markdown(
    """
    <div class="banner">
      <span class="pill">DỮ LIỆU GIẢ LẬP – MINH HỌA</span>
      <h1>Lựa chọn nơi ở sau di dời của hộ gia đình có con đang học phổ thông
      bị ảnh hưởng bởi dự án Vành đai 2.5 đoạn Ngụy Như Kon Tum – Nguyễn Trãi</h1>
      <p>Công cụ trực quan hóa kết quả nghiên cứu và minh họa các đánh đổi trong lựa chọn nơi ở</p>
    </div>
    """,
    unsafe_allow_html=True,
)

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
    with st.container(key="card_ten_de_tai"):
        tieu_de_the("Tên đề tài")
        st.markdown(
            "**Lựa chọn nơi ở sau di dời của hộ gia đình có con đang học phổ thông bị ảnh hưởng "
            "bởi dự án Vành đai 2.5 đoạn Ngụy Như Kon Tum – Nguyễn Trãi**  \n"
            "Nghiên cứu quan sát cắt ngang hồi cứu, mang tính khám phá; "
            "mẫu mục tiêu 30–45 phiếu hợp lệ."
        )

    c1, c2 = st.columns([3, 2], gap="medium")
    with c1:
        with st.container(key="card_boi_canh"):
            tieu_de_the("Bối cảnh thực tiễn")
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
        with st.container(key="card_cau_hoi"):
            tieu_de_the("Câu hỏi nghiên cứu")
            st.markdown(
                """
- **RQ1.** Hộ chuyển đến đâu, dùng hình thức nhà ở nào, xem xét bao nhiêu phương án?
- **RQ2.** Trường học, thời gian đi học – đi làm, hỗ trợ từ người thân thay đổi thế nào?
- **RQ3.** Hộ ưu tiên, bị giới hạn và đánh đổi những gì?
- **RQ4.** Tài chính, ưu tiên giữ trường, ưu tiên thời gian đi làm liên hệ ra sao với 3 kết quả tương ứng?
                """
            )

    with st.container(key="card_khung_khai_niem"):
        tieu_de_the("Khung khái niệm", "Điều kiện → Quá trình → Lựa chọn → Đánh giá sau di dời")
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
        st.caption("Nghiên cứu đo các mối liên hệ giữa các nhóm thông tin; **không** xác nhận "
                   "quan hệ nhân quả và **không** suy rộng cho toàn bộ hộ bị ảnh hưởng.")

    with st.container(key="card_gioi_han"):
        tieu_de_the("Phạm vi kết luận & giới hạn")
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
# TAB 2. DASHBOARD KẾT QUẢ KHẢO SÁT + BỘ LỌC TƯƠNG TÁC
# =============================================================================
# Khai báo các bộ lọc: (khóa trạng thái, nhãn, cột dữ liệu, danh sách lựa chọn)
BO_LOC = [
    ("loc_kc", "Khoảng cách nơi ở mới", "khoang_cach", KHOANG_CACH),
    ("loc_giu", "Kết quả giữ trường", "giu_truong", GIU_TRUONG),
    ("loc_nha", "Hình thức nhà ở trước di dời", "nha_o_truoc", NHA_O),
    ("loc_tc", "Nguồn lực tài chính khi chọn nơi ở", "nhom_tai_chinh", NHOM_TAI_CHINH),
    ("loc_lam", "Hành trình đi làm", "nhom_di_lam", NHOM_DI_LAM),
]


def dat_lai_bo_loc():
    """Hàm gọi khi bấm nút 'Đặt lại': xóa lựa chọn = xem toàn bộ mẫu."""
    for khoa, *_ in BO_LOC:
        st.session_state[khoa] = []


def chi_so_tong_hop(d: pd.DataFrame):
    """Tính 4 chỉ số tóm tắt: %giữ trường, %tăng thời gian đi làm, hài lòng trung vị."""
    giu = (d["giu_truong"] == "Giữ tất cả").mean() * 100
    co_lam = d[d["doi_tg_lam"] != "Không xác định"]
    tang = (co_lam["doi_tg_lam"] == "Tăng").mean() * 100 if len(co_lam) else np.nan
    return giu, tang, d["hai_long"].median(), len(co_lam)


@st.fragment   # chỉ chạy lại phần này khi đổi bộ lọc -> mượt hơn
def khung_dashboard(du_lieu: pd.DataFrame):
    # ---------- Thẻ bộ lọc
    with st.container(key="card_loc"):
        tieu_de_the("🔎 Bộ lọc theo nhóm đối tượng",
                    "để trống = xem tất cả; chọn nhiều nhóm để gộp")
        hang1 = st.columns(3)
        hang2 = st.columns([1, 1, 1])
        vi_tri = hang1 + hang2[:2]
        for (khoa, nhan, _cot, lua_chon), o in zip(BO_LOC, vi_tri):
            with o:
                st.multiselect(nhan, lua_chon, key=khoa, placeholder="Tất cả")
        with hang2[2]:
            st.write("")
            st.button("↺ Đặt lại bộ lọc", on_click=dat_lai_bo_loc)

    # ---------- Áp dụng bộ lọc (các bộ lọc kết hợp bằng "và")
    mat_na = pd.Series(True, index=du_lieu.index)
    for khoa, _nhan, cot, _lc in BO_LOC:
        chon = st.session_state.get(khoa, [])
        if chon:
            mat_na &= du_lieu[cot].isin(chon)
    d = du_lieu[mat_na]
    dang_loc = len(d) < len(du_lieu)

    if len(d) == 0:
        st.warning("Không có hộ nào thỏa mãn tổ hợp bộ lọc này. Hãy bỏ bớt điều kiện lọc.")
        return
    st.caption(f"Đang xem **{len(d)}/{len(du_lieu)}** phiếu.")
    if len(d) < 5:
        st.error("Nhóm dưới 5 phiếu: theo quy tắc của đề cương chỉ mô tả số lượng, "
                 "không diễn giải tỷ lệ hay so sánh.")
    elif len(d) < 10:
        st.info("Nhóm nhỏ (dưới 10 phiếu): tỷ lệ dao động mạnh, chỉ nên xem như mô tả.")

    # ---------- Ô chỉ số (kèm chênh lệch so với toàn mẫu khi đang lọc)
    giu, tang, hl, n_lam = chi_so_tong_hop(d)
    giu0, tang0, hl0, _ = chi_so_tong_hop(du_lieu)

    def chenh(x, x0, don_vi=" điểm %"):
        if not dang_loc or np.isnan(x) or np.isnan(x0):
            return None
        return f"{x - x0:+.0f}{don_vi} so với toàn mẫu"

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Số phiếu đang xem", f"{len(d)}")
    m2.metric("Giữ trường cho tất cả con", f"{giu:.0f}%",
              chenh(giu, giu0), delta_color="off")
    m3.metric("Thời gian đi làm tăng",
              "—" if np.isnan(tang) else f"{tang:.0f}%",
              chenh(tang, tang0), delta_color="off",
              help=f"Tính trên {n_lam} hộ có hành trình đi làm thường xuyên.")
    m4.metric("Hài lòng trung vị (1–5)", f"{hl:.1f}",
              None if not dang_loc else f"{hl - hl0:+.1f} so với toàn mẫu",
              delta_color="off")
    st.write("")

    # ---------- Biểu đồ 1: khoảng cách nơi ở mới (RQ1)
    with st.container(key="card_bd1"):
        tieu_de_the("1. Phân bố khoảng cách từ nơi ở mới đến nơi ở cũ", "RQ1")
        dem = (d["khoang_cach"].value_counts().reindex(KHOANG_CACH).fillna(0)
               .astype(int).rename_axis("Khoảng cách").reset_index(name="Số hộ"))
        dem["Tỷ lệ"] = dem["Số hộ"] / dem["Số hộ"].sum() * 100
        dem["Nhãn"] = dem.apply(lambda r: f"{r['Số hộ']} hộ ({r['Tỷ lệ']:.0f}%)", axis=1)
        fig1 = px.bar(dem, x="Khoảng cách", y="Số hộ", text="Nhãn",
                      color_discrete_sequence=[B700])
        fig1.update_traces(textposition="outside", cliponaxis=False)
        fig1.update_layout(xaxis_title=None, yaxis_title="Số hộ",
                           yaxis_range=[0, max(dem["Số hộ"].max(), 1) * 1.3])
        hien_thi_bieu_do(fig1, 330)
        st.caption("Khoảng cách do người trả lời ước tính, không phải tọa độ đo chính xác.")

    # ---------- Biểu đồ 2: hình thức nhà ở trước - sau (RQ1)
    with st.container(key="card_bd2"):
        tieu_de_the("2. Hình thức nhà ở trước và sau di dời", "RQ1")
        ca, cb = st.columns([3, 2], gap="medium")
        with ca:
            truoc = d["nha_o_truoc"].value_counts().reindex(NHA_O).fillna(0)
            sau = d["nha_o_sau"].value_counts().reindex(NHA_O).fillna(0)
            fig2 = go.Figure()
            fig2.add_bar(x=NHA_O, y=truoc.values, name="Trước di dời", marker_color=B200,
                         text=truoc.values.astype(int), textposition="outside")
            fig2.add_bar(x=NHA_O, y=sau.values, name="Sau di dời", marker_color=B700,
                         text=sau.values.astype(int), textposition="outside")
            fig2.update_layout(barmode="group", yaxis_title="Số hộ",
                               yaxis_range=[0, max(truoc.max(), sau.max(), 1) * 1.3])
            hien_thi_bieu_do(fig2, 340)
        with cb:
            # Bảng chuyển đổi (dòng = trước, cột = sau) dạng bản đồ nhiệt
            chuyen = pd.crosstab(d["nha_o_truoc"], d["nha_o_sau"]).reindex(
                index=NHA_O, columns=NHA_O, fill_value=0)
            fig2b = px.imshow(chuyen.values, x=NHA_O, y=NHA_O, text_auto=True,
                              color_continuous_scale=["#FFFFFF", B700], aspect="auto")
            fig2b.update_layout(coloraxis_showscale=False, xaxis_title=None,
                                yaxis_title=None)
            fig2b.update_xaxes(tickangle=-35)
            hien_thi_bieu_do(fig2b, 340)
            st.caption("Bảng chuyển đổi: dòng = trước, cột = sau.")

    # ---------- Biểu đồ 3: thay đổi thời gian đi học / đi làm (RQ2)
    with st.container(key="card_bd3"):
        tieu_de_the("3. Thay đổi thời gian đi học và đi làm", "RQ2")
        lua_chon = st.radio("Xem theo", ["Đi học của con", "Đi làm của phụ huynh"],
                            horizontal=True, key="xem_di_lai")
        if lua_chon == "Đi học của con":
            c_truoc, c_sau, c_doi, thu_tu = "tg_hoc_truoc", "tg_hoc_sau", "doi_tg_hoc", TG_DI_HOC
        else:
            c_truoc, c_sau, c_doi, thu_tu = "tg_lam_truoc", "tg_lam_sau", "doi_tg_lam", TG_DI_LAM
        g1, g2 = st.columns([3, 2], gap="medium")
        with g1:
            a = d[c_truoc].value_counts().reindex(thu_tu).fillna(0)
            b = d[c_sau].value_counts().reindex(thu_tu).fillna(0)
            fig3 = go.Figure()
            fig3.add_bar(x=thu_tu, y=a.values, name="Trước di dời", marker_color=B200)
            fig3.add_bar(x=thu_tu, y=b.values, name="Sau di dời", marker_color=B700)
            fig3.update_layout(barmode="group", yaxis_title="Số hộ")
            hien_thi_bieu_do(fig3, 330)
        with g2:
            thu_tu_doi = ["Giảm", "Không đổi", "Tăng"]
            cnt = d[c_doi].value_counts().reindex(thu_tu_doi).fillna(0)
            if cnt.sum() == 0:
                st.info("Không có hộ nào xác định được thay đổi trong nhóm đang lọc.")
            else:
                fig3b = px.pie(names=cnt.index, values=cnt.values, hole=0.55,
                               color=cnt.index,
                               color_discrete_map={"Giảm": TEAL, "Không đổi": GREY,
                                                   "Tăng": RED})
                fig3b.update_traces(textinfo="label+percent", sort=False)
                fig3b.update_layout(showlegend=False)
                hien_thi_bieu_do(fig3b, 330)
        if lua_chon == "Đi làm của phụ huynh":
            st.caption("Hộ 'Không thường xuyên' đi làm không được tính vào biểu đồ tròn.")

    # ---------- Biểu đồ 4 & 5: ưu tiên (RQ3) và giữ trường theo ưu tiên (H2)
    cx, cy = st.columns(2, gap="medium")
    with cx:
        with st.container(key="card_bd4"):
            tieu_de_the("4. Mức quan trọng các yếu tố khi chọn nơi ở", "RQ3 · thang 1–5")
            tb = pd.DataFrame({
                "Yếu tố": YEU_TO,
                "Điểm trung bình": [d[COT_QT[t]].mean() for t in YEU_TO],
            }).sort_values("Điểm trung bình")
            fig4 = px.bar(tb, x="Điểm trung bình", y="Yếu tố", orientation="h",
                          text=tb["Điểm trung bình"].round(2),
                          color_discrete_sequence=[B500])
            fig4.update_layout(xaxis_range=[0, 5.6], yaxis_title=None)
            fig4.update_traces(textposition="outside", cliponaxis=False)
            hien_thi_bieu_do(fig4, 300)
    with cy:
        with st.container(key="card_bd5"):
            tieu_de_the("5. Kết quả giữ trường theo mức ưu tiên giữ trường", "mô tả khám phá cho H2")
            nhom = pd.crosstab(d["nhom_uu_tien_truong"], d["giu_truong"]).reindex(
                columns=GIU_TRUONG, fill_value=0)
            if nhom.empty:
                st.info("Chưa đủ dữ liệu.")
            else:
                ty_le = nhom.div(nhom.sum(axis=1), axis=0) * 100
                fig5 = go.Figure()
                mau = {"Giữ tất cả": B700, "Một số chuyển": B200, "Tất cả chuyển": GREY}
                nhan_y = [f"{k} · n={int(nhom.loc[k].sum())}" for k in ty_le.index]
                for cot in GIU_TRUONG:
                    fig5.add_bar(y=nhan_y, x=ty_le[cot].values, name=cot, orientation="h",
                                 marker_color=mau[cot],
                                 text=[f"{v:.0f}%" for v in ty_le[cot].values],
                                 textposition="inside")
                fig5.update_layout(barmode="stack", xaxis_range=[0, 100],
                                   xaxis_title="% hộ", yaxis_title=None)
                hien_thi_bieu_do(fig5, 300)
            st.caption("Chỉ mô tả; không suy ra nhân quả. Nhóm dưới 5 hộ không diễn giải.")

    with st.expander("Xem và tải bảng dữ liệu đang lọc (đã ẩn danh)"):
        bang = d[[c for c in CAC_COT_GOC if c in d.columns]]
        st.dataframe(bang, hide_index=True)
        st.download_button("⬇️ Tải dữ liệu đang lọc (CSV)",
                           bang.to_csv(index=False).encode("utf-8-sig"),
                           file_name="du_lieu_dang_loc.csv", mime="text/csv")


with tab2:
    khung_dashboard(df)

# =============================================================================
# TAB 3. CÔNG CỤ TƯƠNG TÁC HỖ TRỢ QUYẾT ĐỊNH (THỜI GIAN THỰC)
# =============================================================================
# 5 phương án giả lập. Điểm 1–5 cho từng yếu tố theo thứ tự YEU_TO:
# [tài chính, giữ trường, thời gian đi làm, hỗ trợ người thân]
# Điểm càng cao = phương án càng "dễ đáp ứng" yếu tố đó. Đây là GIẢ ĐỊNH MINH HỌA
# do nhóm nghiên cứu đặt ra, sẽ được hiệu chỉnh theo xu hướng khảo sát thật.
PHUONG_AN = [
    {"ten": "A. Thuê nhà gần khu cũ (dưới 3 km)", "ngan": "A. Thuê gần khu cũ",
     "diem": [2, 5, 4, 3],
     "duoc": "Giữ trường cũ, đi làm thuận tiện",
     "doi": "Tiền thuê cao, không gian nhỏ, chưa có tài sản sở hữu"},
    {"ten": "B. Mua nhà có vay (3–7 km)", "ngan": "B. Mua nhà có vay",
     "diem": [2, 4, 3, 3],
     "duoc": "Có nhà sở hữu, vẫn tương đối gần trường",
     "doi": "Gánh nặng trả nợ dài hạn, thời gian di chuyển tăng nhẹ"},
    {"ten": "C. Nhà sở hữu giá mềm (7–15 km)", "ngan": "C. Nhà giá mềm xa hơn",
     "diem": [4, 2, 2, 3],
     "duoc": "Chi phí nhà ở thấp hơn, diện tích lớn hơn",
     "doi": "Nhiều khả năng phải đổi trường, đi làm xa hơn"},
    {"ten": "D. Ở cùng/gần người thân", "ngan": "D. Ở cùng người thân",
     "diem": [5, 2, 3, 5],   # giữ trường thấp: nhà người thân thường không cùng khu trường cũ
     "duoc": "Tiết kiệm chi phí, có người đưa đón, trông nom con",
     "doi": "Ít riêng tư, sinh hoạt chung, phụ thuộc điều kiện người thân"},
    {"ten": "E. Ngoài Hà Nội / vùng xa", "ngan": "E. Ngoài Hà Nội",
     "diem": [5, 1, 1, 2],
     "duoc": "Chi phí nhà ở thấp nhất, quỹ đất rộng",
     "doi": "Gần như chắc chắn đổi trường, đi làm rất xa, xa mạng lưới hỗ trợ"},
]

# Khóa trạng thái của 4 thanh trượt và giá trị mặc định
KHOA_W = {"Khả năng tài chính": "w_tc", "Ưu tiên giữ trường": "w_tr",
          "Giới hạn thời gian đi làm": "w_dl", "Hỗ trợ từ người thân": "w_ht"}
# Các kịch bản mẫu: (nhãn nút, [tài chính, giữ trường, đi làm, người thân])
KICH_BAN_MAU = [
    ("Giữ trường + ngân sách", [5, 5, 3, 2]),
    ("Đi làm gần + ngân sách", [5, 2, 5, 2]),
    ("Cần người thân", [4, 3, 3, 5]),
    ("Đặt lại", [3, 3, 3, 3]),
]
for _k in KHOA_W.values():
    st.session_state.setdefault(_k, 3)   # giá trị khởi tạo của thanh trượt


def ap_kich_ban(gia_tri):
    """Gán mức ưu tiên của một kịch bản mẫu vào 4 thanh trượt."""
    for khoa, v in zip(KHOA_W.values(), gia_tri):
        st.session_state[khoa] = v


def tinh_phuong_an(w):
    """Tính điểm cho từng phương án.
    Mức khớp (%) = Σ(mức quan trọng × điểm phương án) ÷ (5 × Σ mức quan trọng) × 100.
    Trả về danh sách dict đã sắp xếp giảm dần theo mức khớp; mỗi dict có thêm
    'dong_gop' = phần điểm do từng yếu tố đóng góp (cộng lại = mức khớp)."""
    tong = sum(w)
    ds = []
    for pa in PHUONG_AN:
        dong_gop = [wi * si / (5 * tong) * 100 for wi, si in zip(w, pa["diem"])]
        # Xung đột: yếu tố được chấm quan trọng (>=4) nhưng phương án đáp ứng kém (<=2)
        xung_dot = [YEU_TO[i] for i in range(4) if w[i] >= 4 and pa["diem"][i] <= 2]
        ds.append({**pa, "dong_gop": dong_gop, "khop": sum(dong_gop), "xung_dot": xung_dot})
    return sorted(ds, key=lambda x: x["khop"], reverse=True)


def goi_y_danh_doi(w):
    """Bộ quy tắc 'nếu – thì' về đánh đổi thường gặp theo tổ hợp ưu tiên.
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
                  "hãy xem mục 'Xung đột với ưu tiên cao' của từng phương án.")
    return ds


@st.fragment   # kéo thanh trượt chỉ chạy lại phần này -> cập nhật tức thì, không giật
def khung_cong_cu():
    with st.container(key="card_gioi_thieu_cc"):
        tieu_de_the("Công cụ so sánh phương án theo mức ưu tiên", "cập nhật tức thì khi kéo thanh trượt")
        st.markdown(
            "Chấm mức quan trọng từ **1 (ít quan trọng)** đến **5 (rất quan trọng)**. "
            "Biểu đồ và phân tích bên dưới **tự cập nhật ngay**. Công cụ **không dự báo một hộ cụ thể** "
            "và **không xác định phương án đúng**."
        )
        st.caption("Hoặc thử nhanh một kịch bản mẫu:")
        cot_nut = st.columns(len(KICH_BAN_MAU))
        for o, (nhan, gia_tri) in zip(cot_nut, KICH_BAN_MAU):
            o.button(nhan, on_click=ap_kich_ban, args=(gia_tri,), key="nut_" + nhan)

    cs, ck = st.columns([2, 3], gap="medium")
    with cs:
        with st.container(key="card_thanh_truot"):
            tieu_de_the("Mức quan trọng của bạn", "1–5")
            st.slider("1. Khả năng tài chính", 1, 5, key=KHOA_W["Khả năng tài chính"],
                      help="Điểm cao = ngân sách nhà ở bị hạn chế, cần tiết kiệm chi phí.")
            st.slider("2. Ưu tiên giữ trường cho con", 1, 5,
                      key=KHOA_W["Ưu tiên giữ trường"])
            st.slider("3. Giới hạn thời gian đi làm", 1, 5,
                      key=KHOA_W["Giới hạn thời gian đi làm"],
                      help="Điểm cao = muốn nơi ở gần nơi làm việc.")
            st.slider("4. Hỗ trợ từ người thân", 1, 5,
                      key=KHOA_W["Hỗ trợ từ người thân"])

    # Đọc giá trị hiện tại của 4 thanh trượt và tính lại toàn bộ kết quả
    w = [st.session_state[KHOA_W[t]] for t in YEU_TO]
    kq = tinh_phuong_an(w)
    top, nhi = kq[0], kq[1]
    chenh_lech = top["khop"] - nhi["khop"]

    with ck:
        with st.container(key="card_diem_so"):
            tieu_de_the("Điểm khớp của từng kịch bản", "cột chồng = phần điểm do mỗi yếu tố đóng góp")
            # Biểu đồ cột chồng ngang: tổng độ dài = mức khớp (%)
            thu_tu_ve = list(reversed(kq))   # phương án khớp nhất nằm trên cùng
            mau_yeu_to = [B900, B500, TEAL, AMBER]
            fig = go.Figure()
            for i, ten_yt in enumerate(YEU_TO):
                fig.add_bar(y=[p["ngan"] for p in thu_tu_ve],
                            x=[p["dong_gop"][i] for p in thu_tu_ve],
                            name=ten_yt, orientation="h", marker_color=mau_yeu_to[i],
                            hovertemplate="%{y}<br>" + ten_yt + ": %{x:.1f} điểm<extra></extra>")
            for p in thu_tu_ve:
                fig.add_annotation(x=p["khop"], y=p["ngan"], text=f"<b>{p['khop']:.0f}%</b>",
                                   xanchor="left", xshift=6, showarrow=False)
            fig.update_layout(barmode="stack", xaxis_range=[0, 112],
                              xaxis_title="Mức khớp ưu tiên (%)", yaxis_title=None)
            hien_thi_bieu_do(fig, 380, chu_giai_tren=True)

    # ---------- Phân tích đánh đổi (thay đổi theo thanh trượt)
    ca, cb = st.columns([2, 3], gap="medium")
    with ca:
        with st.container(key="card_radar"):
            tieu_de_the("Ưu tiên của bạn so với phương án khớp nhất")
            nhan_truc = ["Tài chính", "Giữ trường", "Đi làm gần", "Người thân"]
            dong = nhan_truc + nhan_truc[:1]
            radar = go.Figure()
            radar.add_trace(go.Scatterpolar(r=w + w[:1], theta=dong, fill="toself",
                                            name="Mức quan trọng bạn chọn",
                                            line=dict(color=B700),
                                            fillcolor="rgba(18,87,168,.25)"))
            radar.add_trace(go.Scatterpolar(r=top["diem"] + top["diem"][:1], theta=dong,
                                            name=f"Điểm đáp ứng – {top['ngan']}",
                                            line=dict(color=AMBER, dash="dash")))
            radar.update_layout(polar=dict(radialaxis=dict(range=[0, 5], dtick=1)))
            hien_thi_bieu_do(radar, 340, le=dict(l=95, r=95, t=30, b=10))
    with cb:
        with st.container(key="card_phan_tich"):
            tieu_de_the("📌 Gợi ý phân tích đánh đổi", "tự cập nhật theo ưu tiên")
            k1, k2, k3 = st.columns(3)
            with k1:
                o_chi_so("Khớp nhất", top["ngan"])
            with k2:
                o_chi_so("Mức khớp", f"{top['khop']:.0f}%")
            with k3:
                o_chi_so("Hơn phương án thứ hai", f"{chenh_lech:.1f} điểm %")
            st.write("")

            if chenh_lech < 3:
                st.markdown(
                    f"<div class='insight'>Hai phương án đầu (<b>{top['ngan']}</b> và "
                    f"<b>{nhi['ngan']}</b>) gần như ngang nhau; ưu tiên của bạn chưa đủ phân biệt, "
                    f"quyết định sẽ phụ thuộc yếu tố ngoài mô hình.</div>", unsafe_allow_html=True)
            else:
                st.markdown(
                    f"<div class='insight'>Với ưu tiên hiện tại, <b>{top['ten']}</b> khớp nhất. "
                    f"<br>✅ <b>Đạt được:</b> {top['duoc']}.<br>⚖️ <b>Phải đánh đổi:</b> {top['doi']}.</div>",
                    unsafe_allow_html=True)
            if top["xung_dot"]:
                st.warning("Phương án khớp nhất vẫn kém ở yếu tố bạn đặt cao: "
                           + ", ".join(top["xung_dot"]) + ".")

            cao_nhat = max(w)
            if min(w) == cao_nhat:
                st.markdown("Bạn chấm các yếu tố **ngang nhau**, nên kết quả phản ánh điểm đáp ứng "
                            "trung bình của từng phương án.")
            elif cao_nhat >= 4:
                ten_cao = [t for t, x in zip(YEU_TO, w) if x == cao_nhat]
                st.markdown("Yếu tố đang chi phối kết quả: **" + "**, **".join(ten_cao) + "**.")

            st.markdown("**Đánh đổi thường gặp với tổ hợp ưu tiên này:**")
            for dong_gy in goi_y_danh_doi(w):
                st.markdown(f"- {dong_gy}")

    # ---------- Bảng chi tiết
    with st.container(key="card_bang"):
        tieu_de_the("Bảng phân tích đánh đổi chi tiết", "xếp theo mức khớp giảm dần")
        bang = pd.DataFrame([{
            "Phương án": p["ten"],
            "Mức khớp ưu tiên (%)": round(p["khop"], 1),
            "Điều đạt được": p["duoc"],
            "Điều phải đánh đổi": p["doi"],
            "Xung đột với ưu tiên cao": ", ".join(p["xung_dot"]) if p["xung_dot"] else "—",
        } for p in kq])
        st.dataframe(bang, hide_index=True)
        with st.expander("Cách tính (để giải thích trước hội đồng)"):
            st.markdown(
                "- Mỗi phương án có điểm 1–5 cho 4 yếu tố (giả định minh họa).\n"
                "- **Mức khớp (%) = Σ(mức quan trọng × điểm phương án) ÷ (5 × Σ mức quan trọng) × 100.**\n"
                "- Biểu đồ cột chồng tách mức khớp thành phần đóng góp của từng yếu tố.\n"
                "- 'Xung đột' xuất hiện khi yếu tố được chấm ≥ 4 nhưng phương án chỉ đạt ≤ 2 điểm.\n"
                "- Mức khớp cao **không có nghĩa** đó là lựa chọn đúng; chỉ phản ánh sự phù hợp "
                "với ưu tiên đã nhập."
            )

    # Tuyên bố từ chối trách nhiệm (BẮT BUỘC) - luôn hiển thị dưới công cụ
    st.markdown(
        "<div class='disclaimer'>⚠️ Công cụ này chỉ mang tính chất minh họa dựa trên dữ liệu "
        "khảo sát nghiên cứu khoa học, không phải lời khuyên tài chính hay pháp lý tuyệt đối.</div>",
        unsafe_allow_html=True,
    )


with tab3:
    khung_cong_cu()

# =============================================================================
# TAB 4. TÀI LIỆU & MÃ NGUỒN MỞ (OPEN SCIENCE)
# =============================================================================
with tab4:
    d1, d2 = st.columns(2, gap="medium")
    with d1:
        with st.container(key="card_co"):
            tieu_de_the("✅ Dữ liệu có trong bộ công khai", "đã mã hóa, ẩn danh")
            st.markdown(
                """
- Mã phiếu ngẫu nhiên (H001, H002…), không liên hệ được với người trả lời.
- Khoảng cách theo **nhóm** (không phải số chính xác).
- Hình thức nhà ở trước – sau, giữ/đổi trường, nhóm thời gian đi lại.
- Mức quan trọng các yếu tố (thang 1–5), mức hài lòng (thang 1–5).
                """
            )
    with d2:
        with st.container(key="card_khong"):
            tieu_de_the("🚫 Không thu thập")
            st.markdown(
                """
- Họ tên, số điện thoại, email.
- Địa chỉ cũ/mới, vị trí GPS.
- Tên trường, tên nơi làm việc.
- Thu nhập, dư nợ, số tiền bồi thường chính xác.
                """
            )
    st.markdown(
        "<div class='insight'>Nghiên cứu tuân thủ nguyên tắc: tự nguyện, người tham gia từ 18 tuổi, "
        "mỗi hộ một phiếu, phiếu gốc lưu riêng và chỉ công khai kết quả tổng hợp.</div>",
        unsafe_allow_html=True,
    )

    with st.container(key="card_tu_dien"):
        tieu_de_the("Từ điển biến (rút gọn)")
        tu_dien = pd.DataFrame([
            ["ma_phieu", "Mã phiếu ẩn danh", "Văn bản"],
            ["khoang_cach", "Khoảng cách nơi ở mới – cũ (nhóm)", "5 nhóm"],
            ["nha_o_truoc / nha_o_sau", "Hình thức nhà ở trước/sau di dời", "5 nhóm"],
            ["giu_truong", "Kết quả giữ trường cho các con", "3 nhóm"],
            ["tg_hoc_truoc / tg_hoc_sau", "Thời gian đi học một chiều", "5 nhóm"],
            ["tg_lam_truoc / tg_lam_sau", "Thời gian đi làm một chiều", "5 nhóm"],
            ["doi_tg_hoc / doi_tg_lam", "Thay đổi: Giảm / Không đổi / Tăng / Không xác định", "Phân loại"],
            ["qt_tai_chinh, qt_giu_truong, qt_di_lam, qt_nguoi_than",
             "Mức quan trọng của 4 yếu tố khi chọn nơi ở", "Thang 1–5"],
            ["kha_nang_tai_chinh",
             "Mức nguồn lực tài chính huy động được tại thời điểm chốt nơi ở (thấp = 1–2)", "Thang 1–5"],
            ["so_phuong_an", "Số phương án đã cân nhắc", "Số nguyên"],
            ["hai_long", "Mức hài lòng sau di dời", "Thang 1–5"],
        ], columns=["Tên biến", "Ý nghĩa", "Kiểu dữ liệu"])
        st.dataframe(tu_dien, hide_index=True)
        # utf-8-sig để Excel đọc đúng tiếng Việt
        st.download_button(
            "⬇️ Tải dữ liệu giả lập (CSV)",
            data=df_goc.to_csv(index=False).encode("utf-8-sig"),
            file_name="du_lieu_gia_lap_vanh_dai_2_5.csv",
            mime="text/csv",
        )

    with st.container(key="card_so_tay"):
        tieu_de_the("Sổ tay Python phân tích dữ liệu")
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

st.caption("Đề tài NCKH học sinh phổ thông • Dữ liệu minh họa giả lập • Mã nguồn mở phục vụ tái lập kết quả")
