# -*- coding: utf-8 -*-
"""
WEBSITE NGHIÊN CỨU KHOA HỌC - PHIÊN BẢN THIẾT KẾ LẠI (v3)
Đề tài: Lựa chọn nơi ở sau di dời của hộ gia đình có con đang học phổ thông
        bị ảnh hưởng bởi dự án Vành đai 2.5 đoạn Ngụy Như Kon Tum – Nhân Hòa – Nguyễn Trãi
Tác giả: Nguyễn Vũ Tuấn Minh (12 Tin 1, THPT chuyên Hà Nội – Amsterdam)

Chạy:  streamlit run app.py
Thư viện: streamlit (>=1.40), pandas, numpy, plotly  (Pillow đã đi kèm streamlit)

CÁCH SỬA NHANH (đọc trước khi chỉnh):
  - Thời gian nghiên cứu, năm ............ biến NAM, THOI_GIAN_NGHIEN_CUU (phần 0)
  - Email nhận góp ý, link sổ tay ........ EMAIL_PHAN_HOI, NOTEBOOK_URL (phần 0)
  - Ảnh/video tư liệu thực địa ........... ANH_TU_LIEU, VIDEO_TU_LIEU (phần 0)
  - Ảnh banner/tác giả/nhóm .............. ANH_BANNER, ANH_TAC_GIA, ANH_NHOM (phần 0)
  - Màu sắc ............................... khối :root trong CSS và nhóm biến màu Plotly

Số liệu trong ứng dụng là DỮ LIỆU GIẢ LẬP để minh họa cấu trúc phân tích.
"""

import base64
import io
import os

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# =============================================================================
# PHẦN 0. CẤU HÌNH CHUNG (chỉ cần sửa ở đây)
# =============================================================================
st.set_page_config(
    page_title="Nơi ở sau di dời – Vành đai 2.5",
    page_icon="🏘️",
    layout="wide",
    initial_sidebar_state="collapsed",   # không dùng sidebar, thông tin tác giả nằm ở Tab 1
)

NAM = "2026"                                          # đổi năm ở MỘT chỗ này
THOI_GIAN_NGHIEN_CUU = f"09/{NAM} – 10/{NAM}"         # hiển thị trên banner và Tab 1
DIA_BAN = "Ngụy Như Kon Tum – Nhân Hòa – Nguyễn Trãi (Hà Nội)"

FILE_DU_LIEU = "processed_data.csv"    # dữ liệu đã mã hóa, đặt cạnh app.py
ANH_BANNER = "NNKT2.jpg"               # ảnh nền banner
ANH_TAC_GIA = "ANH TUAN MINH.jpg"
ANH_NHOM = "NHOM NGHIEN CUU.jpg"

NOTEBOOK_URL = ""        # link sổ tay Python (GitHub/Colab); để trống nếu chưa có
EMAIL_PHAN_HOI = ""      # email nhận góp ý; để trống nếu chưa có

# Tư liệu thực địa (Tab 4): (đường dẫn hoặc URL ảnh, chú thích)
# LƯU Ý: nên thay bằng ảnh tự chụp và ghi rõ nguồn/ngày chụp.
ANH_TU_LIEU = [
    ("https://photo-baomoi.bmcdn.me/w700_r1/2024_03_14_119_48574343/c70c1a9c40339ab30325.jpg",
     "Khu vực nút giao Ngụy Như Kon Tum"),
    ("https://hanoimoi.vn/Uploads/Images/2024/04/10/746820/thanh-xuan-tang-toc-giai-phong-mat-bang-du-an-vanh-dai-2-5-4.jpg",
     "Đoạn qua phố Nhân Hòa"),
    ("https://cms.giaoduc.net.vn/uploaded/2024/2/18/giai-phong-mat-bang-duong-vanh-dai-25-1.jpg",
     "Khu vực kết nối với trục đường Nguyễn Trãi"),
]
# Video (Tab 4): (URL YouTube, tiêu đề)
VIDEO_TU_LIEU = [
    ("https://www.youtube.com/watch?v=Xh0wJk6k_H8", "Toàn cảnh đoạn Ngụy Như Kon Tum – Nhân Hòa"),
    ("https://www.youtube.com/watch?v=Oq7m9P0r2w8", "Thi công kết nối Vành đai 2.5 – Nguyễn Trãi"),
]

# ---- Bảng màu cho biểu đồ (đồng bộ với khối :root trong CSS)
INK = "#0F1B33"      # chữ chính
NAVY = "#0B2A5B"     # xanh navy: tiêu đề
BLUE = "#1D4ED8"     # xanh chủ đạo: dữ liệu "Sau di dời", điểm nhấn
BLUE_L = "#B4C8F2"   # xanh nhạt: dữ liệu "Trước di dời"
SKY = "#5B8DEF"      # xanh vừa
TEAL = "#0EA5A4"     # nhấn: giảm / tích cực
AMBER = "#F59E0B"    # nhấn: nổi bật / lưu ý
RED = "#DC2626"      # nhấn: tăng / cảnh báo
GREY = "#94A3B8"     # trung tính

# ---- Thứ tự các nhóm (cố định để biểu đồ luôn xếp đúng logic)
KHOANG_CACH = ["Dưới 3 km", "3–7 km", "Trên 7–15 km",
               "Trên 15 km (trong Hà Nội)", "Ngoài Hà Nội"]
NHA_O = ["Sở hữu, không vay", "Sở hữu, có vay", "Thuê",
         "Ở cùng người thân", "Tạm thời/khác"]
TG_DI_HOC = ["Dưới 15 phút", "15–30 phút", "31–45 phút", "46–60 phút", "Trên 60 phút"]
TG_DI_LAM = ["Không thường xuyên", "Dưới 30 phút", "30–45 phút", "46–60 phút", "Trên 60 phút"]
GIU_TRUONG = ["Giữ tất cả", "Một số chuyển", "Tất cả chuyển"]
NHOM_TAI_CHINH = ["Thấp (1–2)", "Trung bình (3)", "Cao (4–5)"]
NHOM_DI_LAM = ["Đi làm thường xuyên", "Không thường xuyên"]
YEU_TO = ["Khả năng tài chính", "Ưu tiên giữ trường",
          "Giới hạn thời gian đi làm", "Hỗ trợ từ người thân"]
COT_QT = {"Khả năng tài chính": "qt_tai_chinh", "Ưu tiên giữ trường": "qt_giu_truong",
          "Giới hạn thời gian đi làm": "qt_di_lam", "Hỗ trợ từ người thân": "qt_nguoi_than"}


# =============================================================================
# PHẦN 1. GIAO DIỆN: ẢNH BANNER, CSS, HÀM DỰNG THÀNH PHẦN
# =============================================================================
@st.cache_resource
def anh_sang_base64(duong_dan: str, rong_toi_da: int = 1600) -> str:
    """Thu nhỏ ảnh banner (tối đa 1600px, JPEG 72%) rồi mã hóa base64 để nhúng vào CSS.
    Ảnh nhẹ hơn nhiều so với ảnh gốc nên trang tải nhanh hơn."""
    if not os.path.exists(duong_dan):
        return ""
    try:
        from PIL import Image
        anh = Image.open(duong_dan).convert("RGB")
        anh.thumbnail((rong_toi_da, rong_toi_da))
        bo_nho = io.BytesIO()
        anh.save(bo_nho, format="JPEG", quality=72, optimize=True)
        return base64.b64encode(bo_nho.getvalue()).decode()
    except Exception:
        with open(duong_dan, "rb") as f:            # dự phòng: dùng ảnh gốc
            return base64.b64encode(f.read()).decode()


anh_nen = anh_sang_base64(ANH_BANNER)
NEN_BANNER = (
    f"url('data:image/jpeg;base64,{anh_nen}')" if anh_nen
    else "linear-gradient(135deg, #0B2A5B, #1D4ED8)"
)

# ---- CSS chính (chuỗi thường, KHÔNG phải f-string nên dùng { } thoải mái)
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700;800&display=swap');
:root{
  --ink:#0F1B33; --navy:#0B2A5B; --blue:#1D4ED8; --sky:#DBE7FF; --mist:#EEF3FC;
  --bg:#F4F6FB; --line:#E1E7F2; --muted:#5B6B85; --amber:#F59E0B; --red:#DC2626;
}
/* ---------- Nền, phông chữ (Be Vietnam Pro: thiết kế cho tiếng Việt) ---------- */
html, body, .stApp { background: var(--bg); }
.stApp, .stApp :is(p, li, h1, h2, h3, h4, h5, label, button, input, textarea, td, th, a,
  [data-testid="stMetricValue"], [data-testid="stMetricLabel"], [data-testid="stMetricDelta"]) {
  font-family: 'Be Vietnam Pro', 'Segoe UI', Roboto, Arial, sans-serif;
}
.block-container { max-width: 1240px; padding: 1.2rem 2rem 3rem; }

/* Ẩn phần thừa của Streamlit nhưng GIỮ tiêu đề để không mất các điều khiển */
#MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"],
[data-testid="stStatusWidget"] { visibility: hidden; height: 0; }
[data-testid="stHeader"] { background: transparent; }

/* ---------- Cỡ chữ (lớn, dễ đọc) ---------- */
.stApp .stMarkdown p, .stApp .stMarkdown li { font-size: 1.1rem; line-height: 1.75; color: var(--ink); }
.stApp .stMarkdown li { margin-bottom: .3rem; }
.stApp h2 { font-size: 2rem; font-weight: 800; color: var(--navy); letter-spacing: -.01em; }
.stApp h3 { font-size: 1.5rem; font-weight: 700; color: var(--navy); }
.stApp h4 { font-size: 1.25rem; font-weight: 700; color: var(--navy); }
[data-testid="stCaptionContainer"], .stApp small { font-size: .98rem !important; color: var(--muted); }
[data-testid="stWidgetLabel"] p { font-size: 1.05rem !important; font-weight: 600; color: var(--ink); }

/* ---------- Banner (ảnh nền + lớp phủ gradient, chữ trắng luôn rõ) ---------- */
.stApp .hero {
  background-image: linear-gradient(100deg, rgba(6,24,58,.95) 0%, rgba(11,42,91,.88) 48%, rgba(29,78,216,.62) 100%), HERO_BG;
  background-size: cover; background-position: center;
  border-radius: 26px; padding: 3.2rem 3rem 2.6rem; margin-bottom: 1.4rem;
  box-shadow: 0 18px 44px rgba(11,42,91,.28);
}
.stApp .hero .eyebrow { display: inline-block; text-transform: uppercase; letter-spacing: .09em;
  font-size: .82rem; font-weight: 700; color: #fff; background: rgba(255,255,255,.14);
  border: 1px solid rgba(255,255,255,.32); padding: .35rem 1rem; border-radius: 999px; margin-bottom: 1.2rem; }
.stApp .hero h1 { color: #fff !important; font-size: 2.6rem; font-weight: 800; line-height: 1.25;
  max-width: 920px; margin: 0 0 1rem 0; padding: 0; text-shadow: 0 2px 12px rgba(0,0,0,.35); }
.stApp .hero p.lead { color: rgba(255,255,255,.94) !important; font-size: 1.22rem; line-height: 1.65;
  max-width: 840px; margin: 0 0 1.7rem 0; }
.stApp .hero .chips { display: flex; flex-wrap: wrap; gap: .8rem; }
.stApp .hero .chip { background: rgba(255,255,255,.12); border: 1px solid rgba(255,255,255,.28);
  border-radius: 16px; padding: .65rem 1.1rem; }
.stApp .hero .chip small { display: block; color: rgba(255,255,255,.72) !important; font-size: .76rem !important;
  text-transform: uppercase; letter-spacing: .07em; }
.stApp .hero .chip b { color: #fff; font-size: 1.05rem; font-weight: 600; }

/* ---------- Thanh tab dạng viên thuốc ----------
   Dùng thuộc tính role="tablist"/"tab" (Streamlit mới) kèm data-baseweb (Streamlit cũ);
   !important để thắng CSS mặc định. */
.stTabs > div:first-child { border-bottom: 0 !important; box-shadow: none !important; }
.stTabs [role="tablist"], .stTabs [data-baseweb="tab-list"] {
  gap: .35rem !important; background: #fff !important; padding: .45rem !important;
  border-radius: 18px !important; border: 1px solid var(--line) !important;
  box-shadow: 0 6px 20px rgba(15,27,51,.06) !important; }
.stTabs [role="tab"], .stTabs [data-baseweb="tab"] {
  height: auto !important; padding: .75rem 1.3rem !important; border-radius: 13px !important;
  background: transparent !important; border: 0 !important; }
.stTabs [role="tab"] p, .stTabs [data-baseweb="tab"] p {
  font-size: 1.1rem !important; font-weight: 600 !important; color: var(--muted) !important; }
.stTabs [role="tab"]:hover p { color: var(--blue) !important; }
.stTabs [role="tab"][aria-selected="true"], .stTabs [data-baseweb="tab"][aria-selected="true"] {
  background: var(--blue) !important; box-shadow: 0 6px 16px rgba(29,78,216,.35) !important; }
.stTabs [role="tab"][aria-selected="true"] p { color: #fff !important; }
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] { display: none !important; }
.stTabs [role="tabpanel"], .stTabs [data-testid="stTabPanel"] { padding-top: 1.4rem; }

/* ---------- Thẻ nổi: mọi st.container(key="card_...") ---------- */
div[class*="st-key-card"] { background: #fff; border: 1px solid var(--line); border-radius: 20px;
  box-shadow: 0 12px 32px rgba(15,27,51,.07); padding: 1.6rem 1.8rem; margin-bottom: .8rem; }
div[class*="st-key-card_loc"] { background: var(--mist); border-color: #CBD9F3; }
.ct { font-size: 1.3rem; font-weight: 700; color: var(--navy); margin: 0 0 .7rem 0; line-height: 1.35; }
.ct span { font-size: .92rem; font-weight: 500; color: var(--muted); margin-left: .6rem; }

/* ---------- Tiêu đề mục ---------- */
.sec { margin: .4rem 0 1.1rem 0; }
.sec .eyebrow { color: var(--blue); font-weight: 700; font-size: .88rem; letter-spacing: .09em; text-transform: uppercase; }
.sec h2 { margin: .15rem 0 .3rem 0; padding: 0; }
.sec p { margin: 0; color: var(--muted) !important; font-size: 1.12rem !important; max-width: 860px; }

/* ---------- Ô chỉ số ---------- */
[data-testid="stMetric"] { background: #fff; border: 1px solid var(--line); border-radius: 18px;
  padding: 1rem 1.3rem; box-shadow: 0 8px 22px rgba(15,27,51,.06); }
[data-testid="stMetricLabel"] p { font-size: 1rem !important; color: var(--muted); font-weight: 500; }
[data-testid="stMetricValue"] { color: var(--navy); font-weight: 800; font-size: 2.3rem; }
.kpi { background: var(--mist); border: 1px solid #CBD9F3; border-radius: 16px; padding: .8rem 1.1rem; height: 100%; }
.kpi .nhan { font-size: .92rem; color: var(--muted); font-weight: 500; }
.kpi .tri { font-size: 1.35rem; font-weight: 800; color: var(--blue); line-height: 1.3; }

/* ---------- Khối thông tin ---------- */
.note { background: var(--mist); border: 1px solid #CBD9F3; border-radius: 16px; padding: .9rem 1.2rem; margin: .4rem 0 .8rem; font-size: 1.05rem; line-height: 1.7; }
.warn { background: #FFF6E0; border: 1px solid #F3D9A0; border-radius: 16px; padding: .9rem 1.2rem; font-size: 1.02rem; line-height: 1.65; }
.disclaimer { background: #FDECEA; border: 1px solid #F1B7B0; border-radius: 16px; padding: 1rem 1.3rem;
  color: #7A1F16; font-weight: 600; font-size: 1.05rem; line-height: 1.6; margin-top: .6rem; }
.kv { display: grid; grid-template-columns: 150px 1fr; gap: .55rem 1rem; font-size: 1.05rem; line-height: 1.55; }
.kv .k { color: var(--muted); font-weight: 500; }
.kv .v { color: var(--ink); font-weight: 600; }

/* Bốn câu hỏi nghiên cứu */
.rqs { display: grid; grid-template-columns: repeat(2, 1fr); gap: .9rem; }
.rq { background: var(--mist); border-radius: 16px; padding: 1rem 1.1rem; border: 1px solid #DCE6F8; }
.rq b { display: inline-block; color: #fff; background: var(--blue); border-radius: 8px; padding: .05rem .55rem; font-size: .88rem; margin-bottom: .45rem; }
.rq div { font-size: 1.02rem; line-height: 1.6; color: var(--ink); }

/* Khung khái niệm 4 bước */
.steps { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; }
.step { position: relative; background: #fff; border: 1px solid var(--line); border-radius: 18px; padding: 1.1rem 1.2rem; }
.step .no { width: 2.1rem; height: 2.1rem; border-radius: 50%; background: var(--blue); color: #fff; font-weight: 700;
  display: flex; align-items: center; justify-content: center; margin-bottom: .6rem; }
.step h5 { margin: 0 0 .3rem 0; font-size: 1.12rem; font-weight: 700; color: var(--navy); }
.step div { font-size: 1rem; line-height: 1.6; color: var(--ink); }

/* ---------- Nút, ô nhập, bảng ---------- */
.stButton > button, .stDownloadButton > button, [data-testid="stFormSubmitButton"] > button {
  border-radius: 13px; border: 1px solid #C5D4F1; background: #fff; color: var(--navy);
  font-weight: 600; font-size: 1rem; padding: .55rem 1.1rem; }
.stButton > button:hover, .stDownloadButton > button:hover { border-color: var(--blue); color: var(--blue); }
[data-testid="stExpander"] { border: 1px solid var(--line); border-radius: 16px; background: #fff; }
[data-testid="stExpander"] summary p { font-size: 1.05rem; font-weight: 600; }
[data-testid="stAlert"] { border-radius: 16px; }
[data-testid="stImage"] img { border-radius: 16px; }

/* ---------- Màn hình nhỏ ---------- */
@media (max-width: 900px) {
  .block-container { padding: 1rem 1rem 2rem; }
  .stApp .hero { padding: 1.8rem 1.3rem; border-radius: 20px; }
  .stApp .hero h1 { font-size: 1.7rem; }
  .steps, .rqs { grid-template-columns: 1fr; }
  .kv { grid-template-columns: 1fr; gap: .1rem; }
  .kv .v { margin-bottom: .5rem; }
}
</style>
"""
st.markdown(CSS.replace("HERO_BG", NEN_BANNER), unsafe_allow_html=True)


def tieu_de_muc(nhan_nho, tieu_de, mo_ta=""):
    """Tiêu đề đầu mỗi tab: nhãn nhỏ màu xanh + tiêu đề lớn + mô tả."""
    mo_ta_html = f"<p>{mo_ta}</p>" if mo_ta else ""
    st.markdown(f"<div class='sec'><div class='eyebrow'>{nhan_nho}</div>"
                f"<h2>{tieu_de}</h2>{mo_ta_html}</div>", unsafe_allow_html=True)


def tieu_de_the(tieu_de, phu=""):
    """Tiêu đề đầu mỗi thẻ."""
    phu_html = f"<span>{phu}</span>" if phu else ""
    st.markdown(f"<div class='ct'>{tieu_de}{phu_html}</div>", unsafe_allow_html=True)


def o_chi_so(nhan, gia_tri):
    """Ô chỉ số dạng HTML: chữ dài tự xuống dòng thay vì bị cắt."""
    st.markdown(f"<div class='kpi'><div class='nhan'>{nhan}</div>"
                f"<div class='tri'>{gia_tri}</div></div>", unsafe_allow_html=True)


def hien_thi_bieu_do(fig, chieu_cao=380, le=None, chu_giai_tren=False):
    """Định dạng chung (chữ to, nền trong suốt) cho mọi biểu đồ Plotly rồi hiển thị."""
    fig.update_layout(
        template="plotly_white", height=chieu_cao,
        margin=le or dict(l=10, r=10, t=30, b=10),
        font=dict(family="Be Vietnam Pro, Segoe UI, Roboto, Arial, sans-serif", size=15, color=INK),
        legend=(dict(orientation="h", yanchor="bottom", y=1.02, x=0, font=dict(size=14)) if chu_giai_tren
                else dict(orientation="h", yanchor="bottom", y=-0.32, x=0, font=dict(size=14))),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        hoverlabel=dict(font_size=14),
    )
    fig.update_xaxes(gridcolor="#E9EEF7", zeroline=False, tickfont_size=14, title_font_size=14)
    fig.update_yaxes(gridcolor="#E9EEF7", zeroline=False, tickfont_size=14, title_font_size=14)
    phien_ban = tuple(int(x) for x in st.__version__.split(".")[:2])
    if phien_ban >= (1, 50):
        st.plotly_chart(fig, width="stretch")
    else:
        st.plotly_chart(fig, use_container_width=True)


def xuong_dong(nhan):
    """Ngắt nhãn dài thành 2 dòng để nhãn trục không bị xoay nghiêng."""
    ngat = {"Ở cùng người thân": "Ở cùng<br>người thân", "Tạm thời/khác": "Tạm thời/<br>khác",
            "Ngoài Hà Nội": "Ngoài<br>Hà Nội", "Trên 15 km (trong Hà Nội)": "Trên 15 km<br>(trong Hà Nội)"}
    return ngat.get(nhan, nhan.replace(", ", ",<br>"))


def dat_nhan_truc_x(fig, danh_sach):
    """Đặt nhãn trục X ngang, ngắt dòng, theo đúng thứ tự danh sách."""
    fig.update_xaxes(tickmode="array", tickvals=danh_sach,
                     ticktext=[xuong_dong(x) for x in danh_sach], tickangle=0)


def hien_thi_anh(nguon, chu_thich=None):
    """Hiển thị ảnh an toàn: ảnh cục bộ thiếu thì bỏ qua thay vì làm hỏng trang."""
    if not nguon.startswith("http") and not os.path.exists(nguon):
        return False
    try:
        phien_ban = tuple(int(x) for x in st.__version__.split(".")[:2])
        if phien_ban >= (1, 50):
            st.image(nguon, caption=chu_thich, width="stretch")
        else:
            st.image(nguon, caption=chu_thich, use_container_width=True)
        return True
    except Exception:
        return False


def vnd(x):
    """Định dạng tiền Việt: 12000000 -> '12.000.000 đ'."""
    return f"{x:,.0f}".replace(",", ".") + " đ"


# =============================================================================
# PHẦN 2. DỮ LIỆU (đọc CSV; không có hoặc sai cấu trúc thì sinh giả lập)
# =============================================================================
@st.cache_data
def tao_du_lieu_gia_lap(n: int = 36, seed: int = 2026) -> pd.DataFrame:
    """Sinh dữ liệu giả lập, mỗi dòng = 1 hộ. Có quy luật hợp lý (chuyển càng xa
    càng dễ đổi trường, thời gian đi lại càng dễ tăng) nhưng chỉ mang tính minh họa."""
    rng = np.random.default_rng(seed)     # seed cố định -> kết quả lặp lại được
    df = pd.DataFrame({"ma_phieu": [f"H{i:03d}" for i in range(1, n + 1)]})

    df["khoang_cach"] = rng.choice(KHOANG_CACH, size=n, p=[0.22, 0.33, 0.25, 0.12, 0.08])
    idx_kc = df["khoang_cach"].map(KHOANG_CACH.index).to_numpy()
    df["nha_o_truoc"] = rng.choice(NHA_O, size=n, p=[0.50, 0.10, 0.25, 0.10, 0.05])

    # Nhà ở sau di dời: chọn theo ma trận chuyển đổi (hàng = trước, cột = sau)
    ma_tran = {
        "Sở hữu, không vay": [0.45, 0.30, 0.10, 0.10, 0.05],
        "Sở hữu, có vay":    [0.15, 0.55, 0.15, 0.10, 0.05],
        "Thuê":              [0.02, 0.08, 0.75, 0.10, 0.05],
        "Ở cùng người thân": [0.05, 0.10, 0.20, 0.60, 0.05],
        "Tạm thời/khác":     [0.05, 0.10, 0.35, 0.20, 0.30],
    }
    df["nha_o_sau"] = [rng.choice(NHA_O, p=ma_tran[t]) for t in df["nha_o_truoc"]]

    # Giữ trường: xác suất giữ giảm dần theo khoảng cách
    p_giu = np.array([0.90, 0.70, 0.40, 0.20, 0.10])[idx_kc]
    giu = []
    for xs, x in zip(p_giu, rng.random(n)):
        giu.append("Giữ tất cả" if x < xs else
                   ("Một số chuyển" if x < xs + (1 - xs) * 0.4 else "Tất cả chuyển"))
    df["giu_truong"] = giu

    # Thời gian đi học/đi làm: "sau" = "trước" + độ dịch nhóm (phụ thuộc khoảng cách)
    dich = [-1, 0, 1, 2]
    p_dich = {0: [.10, .55, .30, .05], 1: [.10, .35, .40, .15], 2: [.10, .20, .40, .30],
              3: [.10, .10, .40, .40], 4: [.10, .10, .30, .50]}

    def dich_nhom(idx_truoc, idx_kc_i, nho_nhat):
        return int(np.clip(idx_truoc + rng.choice(dich, p=p_dich[idx_kc_i]), nho_nhat, 4))

    hoc_truoc = rng.choice(5, size=n, p=[.25, .35, .22, .13, .05])
    lam_truoc = rng.choice(5, size=n, p=[.08, .30, .30, .22, .10])
    hoc_sau = [dich_nhom(a, k, 0) for a, k in zip(hoc_truoc, idx_kc)]
    lam_sau = [0 if a == 0 else dich_nhom(a, k, 1) for a, k in zip(lam_truoc, idx_kc)]
    df["tg_hoc_truoc"] = [TG_DI_HOC[i] for i in hoc_truoc]
    df["tg_hoc_sau"] = [TG_DI_HOC[i] for i in hoc_sau]
    df["tg_lam_truoc"] = [TG_DI_LAM[i] for i in lam_truoc]
    df["tg_lam_sau"] = [TG_DI_LAM[i] for i in lam_sau]

    def nhan(truoc, sau, khong_xd=False):
        if khong_xd:
            return "Không xác định"
        return "Tăng" if sau > truoc else ("Giảm" if sau < truoc else "Không đổi")

    df["doi_tg_hoc"] = [nhan(a, b) for a, b in zip(hoc_truoc, hoc_sau)]
    df["doi_tg_lam"] = [nhan(a, b, a == 0) for a, b in zip(lam_truoc, lam_sau)]

    # Mức quan trọng 4 yếu tố (thang 1–5) và nguồn lực tài chính (thấp = 1–2, dùng cho H1)
    tb = {"Khả năng tài chính": 4.2, "Ưu tiên giữ trường": 3.8,
          "Giới hạn thời gian đi làm": 3.6, "Hỗ trợ từ người thân": 3.2}
    for ten, m in tb.items():
        df[COT_QT[ten]] = np.clip(np.round(rng.normal(m, 1.0, n)), 1, 5).astype(int)
    df["kha_nang_tai_chinh"] = np.clip(np.round(rng.normal(3.0, 1.1, n)), 1, 5).astype(int)
    df["so_phuong_an"] = rng.integers(1, 7, size=n)
    df["hai_long"] = np.clip(np.round(rng.normal(3.6 - 0.25 * idx_kc, 0.9)), 1, 5).astype(int)
    return df


def them_cot_phan_nhom(d: pd.DataFrame) -> pd.DataFrame:
    """Tạo các cột PHÂN NHÓM dùng cho bộ lọc (không sửa dữ liệu gốc)."""
    d = d.copy()
    d["nhom_tai_chinh"] = pd.cut(d["kha_nang_tai_chinh"], bins=[0, 2, 3, 5],
                                 labels=NHOM_TAI_CHINH).astype(str)
    d["nhom_di_lam"] = np.where(d["tg_lam_truoc"] == "Không thường xuyên",
                                NHOM_DI_LAM[1], NHOM_DI_LAM[0])
    d["nhom_uu_tien_truong"] = np.where(d[COT_QT["Ưu tiên giữ trường"]] >= 4,
                                        "Ưu tiên giữ trường cao (4–5)", "Thấp/trung bình (1–3)")
    return d


@st.cache_data
def nap_du_lieu() -> pd.DataFrame:
    """Ưu tiên đọc processed_data.csv; thiếu file hoặc thiếu cột thì dùng dữ liệu giả lập."""
    cot_can = list(tao_du_lieu_gia_lap(30).columns)
    try:
        d = pd.read_csv(FILE_DU_LIEU, encoding="utf-8-sig")
        if all(c in d.columns for c in cot_can):
            return d
    except Exception:
        pass
    return tao_du_lieu_gia_lap(36)


df_goc = nap_du_lieu()
CAC_COT_GOC = list(df_goc.columns)
df = them_cot_phan_nhom(df_goc)

# =============================================================================
# PHẦN 3. BANNER ĐẦU TRANG
# =============================================================================
st.markdown(
    f"""
    <div class="hero">
      <span class="eyebrow">Đề tài nghiên cứu khoa học học sinh phổ thông</span>
      <h1>Lựa chọn nơi ở sau di dời của hộ gia đình có con đang học phổ thông</h1>
      <p class="lead">Khảo sát cấu trúc đánh đổi của các hộ bị ảnh hưởng bởi dự án Vành đai 2.5,
      đoạn Ngụy Như Kon Tum – Nhân Hòa – Nguyễn Trãi.</p>
      <div class="chips">
        <div class="chip"><small>Tác giả</small><b>Nguyễn Vũ Tuấn Minh · 12 Tin 1</b></div>
        <div class="chip"><small>Thời gian nghiên cứu</small><b>{THOI_GIAN_NGHIEN_CUU}</b></div>
        <div class="chip"><small>Thiết kế</small><b>Khảo sát cắt ngang hồi cứu</b></div>
        <div class="chip"><small>Mẫu mục tiêu</small><b>30–45 phiếu</b></div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Tổng quan & Bối cảnh",
    "Kết quả khảo sát",
    "Công cụ quyết định",
    "Tư liệu thực địa",
    "Tài liệu & Phản hồi",
])

# =============================================================================
# TAB 1. TỔNG QUAN & BỐI CẢNH
# =============================================================================
with tab1:
    tieu_de_muc("Tổng quan", "Một câu hỏi thực tế dưới góc nhìn của học sinh lớp 12",
                "Các gia đình đã chuyển đến đâu, và điều gì khiến họ chọn nơi ở đó?")
    cot_trai, cot_phai = st.columns([7, 5], gap="medium")

    with cot_trai:
        with st.container(key="card_van_de"):
            tieu_de_the("Vấn đề nghiên cứu")
            st.markdown(
                f"""
Đây là đề tài nghiên cứu nhỏ do **Nguyễn Vũ Tuấn Minh**, học sinh lớp 12 Tin 1 (chuyên Tin), Trường THPT chuyên Hà Nội – Amsterdam, thực hiện từ sự tò mò trước một câu hỏi rất đời thường: *sau khi phải di dời để phục vụ dự án Vành đai 2.5, đoạn Ngụy Như Kon Tum – Nhân Hòa – Nguyễn Trãi, các gia đình đã chuyển đến đâu và điều gì khiến họ lựa chọn nơi ở đó?*

Tại thời điểm nghiên cứu vào tháng 9/{NAM}, việc giải phóng mặt bằng đã hoàn tất và các hộ bị ảnh hưởng đã di dời. Vì quyết định chuyển nhà đã xảy ra, khảo sát tập trung tìm hiểu lại những căn cứ đã được cân nhắc, gồm **khả năng tài chính, trường học của con, thời gian đi làm, sự hỗ trợ của người thân và mức độ ổn định của nơi ở mới**.
                """
            )
        with st.container(key="card_cau_hoi"):
            tieu_de_the("Bốn câu hỏi nghiên cứu")
            st.markdown(
                """
                <div class="rqs">
                  <div class="rq"><b>RQ1</b><div>Hộ chuyển đến đâu, dùng hình thức nhà ở nào, xem xét bao nhiêu phương án?</div></div>
                  <div class="rq"><b>RQ2</b><div>Trường học, thời gian đi học – đi làm, hỗ trợ từ người thân thay đổi thế nào?</div></div>
                  <div class="rq"><b>RQ3</b><div>Hộ ưu tiên, bị giới hạn và đánh đổi những gì?</div></div>
                  <div class="rq"><b>RQ4</b><div>Tài chính, ưu tiên giữ trường, ưu tiên thời gian đi làm liên hệ ra sao với 3 kết quả tương ứng?</div></div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with cot_phai:
        with st.container(key="card_tac_gia"):
            tieu_de_the("Tác giả & nhóm nghiên cứu")
            hien_thi_anh(ANH_TAC_GIA, "Nguyễn Vũ Tuấn Minh · 12 Tin 1")
            hien_thi_anh(ANH_NHOM, "Nhóm nghiên cứu cùng giáo viên hướng dẫn")
        with st.container(key="card_thong_tin"):
            tieu_de_the("Thông tin đề tài")
            st.markdown(
                f"""
                <div class="kv">
                  <div class="k">Địa bàn</div><div class="v">{DIA_BAN}</div>
                  <div class="k">Thời gian</div><div class="v">{THOI_GIAN_NGHIEN_CUU}</div>
                  <div class="k">Đối tượng</div><div class="v">Hộ có con học lớp 1–12 tại thời điểm chọn nơi ở mới</div>
                  <div class="k">Trường</div><div class="v">THPT chuyên Hà Nội – Amsterdam</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with st.container(key="card_khung"):
        tieu_de_the("Khung khái niệm", "Điều kiện → Quá trình → Lựa chọn → Đánh giá sau di dời")
        st.markdown(
            """
            <div class="steps">
              <div class="step"><div class="no">1</div><h5>Điều kiện</h5>
                <div>Tài chính, con đang học, nơi làm việc, hỗ trợ từ người thân <i>tại thời điểm chốt nơi ở</i>.</div></div>
              <div class="step"><div class="no">2</div><h5>Quá trình</h5>
                <div>Số phương án cân nhắc, thời gian tìm, yếu tố ưu tiên, ràng buộc loại phương án.</div></div>
              <div class="step"><div class="no">3</div><h5>Lựa chọn</h5>
                <div>Khoảng cách nơi ở mới, hình thức nhà ở, giữ hay đổi trường.</div></div>
              <div class="step"><div class="no">4</div><h5>Đánh giá sau di dời</h5>
                <div>Thay đổi thời gian đi học – đi làm, hỗ trợ gia đình, mức hài lòng.</div></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.caption("Nghiên cứu đo các mối liên hệ giữa các nhóm thông tin; không xác nhận quan hệ nhân quả "
                   "và không suy rộng cho toàn bộ hộ bị ảnh hưởng.")

    with st.container(key="card_loi_cam_on"):
        tieu_de_the("Lời cảm ơn & tri ân")
        st.markdown(
            """
**Kính gửi cô/chú, anh/chị tham gia khảo sát,**

Con là **Nguyễn Vũ Tuấn Minh**, học sinh lớp 12 Tin 1 (chuyên Tin), Trường THPT chuyên Hà Nội – Amsterdam. Từ sự tò mò của một học sinh trước một vấn đề thực tế của cuộc sống, con đã bắt đầu nghiên cứu này với mong muốn hiểu rõ hơn cách mỗi gia đình đưa ra quyết định về nơi ở sau di dời.

Con chân thành cảm ơn cô/chú, anh/chị đã dành thời gian chia sẻ trải nghiệm và những cân nhắc của gia đình. Mỗi phản hồi đều rất quý giá, giúp con nhìn vấn đề đầy đủ hơn từ những lựa chọn có thật trong cuộc sống.

**Cam kết của con:** Thông tin và kết quả tổng hợp từ khảo sát chỉ được sử dụng cho đề tài nghiên cứu khoa học; không dùng cho mục đích thương mại và không dùng để đánh giá đúng – sai quyết định của bất kỳ gia đình nào. Dữ liệu được thu thập ẩn danh.

Con xin bày tỏ lòng biết ơn sâu sắc tới **cô Lê Thị Thúy** — giáo viên môn Tin học, đồng thời là giáo viên chủ nhiệm của con trong hai năm lớp 11 và lớp 12 — người đã trực tiếp hướng dẫn và đồng hành cùng con trong quá trình thực hiện nghiên cứu. Con cũng chân thành cảm ơn các bạn học sinh đã nhiệt tình hỗ trợ con trong quá trình khảo sát thực tế.

*Việc tham gia hoàn toàn tự nguyện. Cô/chú, anh/chị có thể thử công cụ mà không gửi dữ liệu và có thể dừng bất cứ lúc nào.*
            """
        )
        st.markdown("<p style='text-align:right;font-weight:700;color:#1D4ED8;margin:0'>"
                    "Trân trọng — Nguyễn Vũ Tuấn Minh, lớp 12 Tin 1</p>", unsafe_allow_html=True)

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
# TAB 2. DASHBOARD KẾT QUẢ KHẢO SÁT + BỘ LỌC
# =============================================================================
# Khai báo bộ lọc: (khóa trạng thái, nhãn, cột dữ liệu, danh sách lựa chọn)
BO_LOC = [
    ("loc_kc", "Khoảng cách nơi ở mới", "khoang_cach", KHOANG_CACH),
    ("loc_giu", "Kết quả giữ trường", "giu_truong", GIU_TRUONG),
    ("loc_nha", "Hình thức nhà ở trước di dời", "nha_o_truoc", NHA_O),
    ("loc_tc", "Nguồn lực tài chính khi chọn nơi ở", "nhom_tai_chinh", NHOM_TAI_CHINH),
    ("loc_lam", "Hành trình đi làm", "nhom_di_lam", NHOM_DI_LAM),
]


def dat_lai_bo_loc():
    """Gọi khi bấm 'Đặt lại': xóa lựa chọn = xem toàn bộ mẫu."""
    for khoa, *_ in BO_LOC:
        st.session_state[khoa] = []


def chi_so_tong_hop(d: pd.DataFrame):
    """% giữ trường, % tăng thời gian đi làm, hài lòng trung vị, số hộ có đi làm."""
    giu = (d["giu_truong"] == "Giữ tất cả").mean() * 100
    co_lam = d[d["doi_tg_lam"] != "Không xác định"]
    tang = (co_lam["doi_tg_lam"] == "Tăng").mean() * 100 if len(co_lam) else np.nan
    return giu, tang, d["hai_long"].median(), len(co_lam)


@st.fragment   # chỉ chạy lại phần này khi đổi bộ lọc -> mượt hơn
def khung_dashboard(du_lieu: pd.DataFrame):
    # ---------- Thẻ bộ lọc
    with st.container(key="card_loc"):
        tieu_de_the("Bộ lọc theo nhóm đối tượng", "để trống = xem tất cả · chọn nhiều nhóm để gộp")
        h1 = st.columns(3, gap="medium")
        h2 = st.columns(3, gap="medium")
        for (khoa, nhan, _c, lua_chon), o in zip(BO_LOC, h1 + h2[:2]):
            with o:
                st.multiselect(nhan, lua_chon, key=khoa, placeholder="Tất cả")
        with h2[2]:
            st.write("")
            st.button("↺  Đặt lại bộ lọc", on_click=dat_lai_bo_loc)

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
    st.caption(f"Đang xem **{len(d)}/{len(du_lieu)}** phiếu (dữ liệu giả lập minh họa).")
    if len(d) < 5:
        st.error("Nhóm dưới 5 phiếu: theo quy tắc của đề cương chỉ mô tả số lượng, "
                 "không diễn giải tỷ lệ hay so sánh.")
    elif len(d) < 10:
        st.info("Nhóm nhỏ (dưới 10 phiếu): tỷ lệ dao động mạnh, chỉ nên xem như mô tả.")

    # ---------- Chỉ số tóm tắt (kèm chênh lệch so với toàn mẫu khi đang lọc)
    giu, tang, hl, n_lam = chi_so_tong_hop(d)
    giu0, tang0, hl0, _ = chi_so_tong_hop(du_lieu)

    def chenh(x, x0):
        if not dang_loc or np.isnan(x) or np.isnan(x0):
            return None
        return f"{x - x0:+.0f} điểm % so với toàn mẫu"

    m1, m2, m3, m4 = st.columns(4, gap="medium")
    m1.metric("Số phiếu đang xem", f"{len(d)}")
    m2.metric("Giữ trường cho tất cả con", f"{giu:.0f}%", chenh(giu, giu0), delta_color="off")
    m3.metric("Thời gian đi làm tăng", "—" if np.isnan(tang) else f"{tang:.0f}%",
              chenh(tang, tang0), delta_color="off",
              help=f"Tính trên {n_lam} hộ có hành trình đi làm thường xuyên.")
    m4.metric("Hài lòng trung vị (1–5)", f"{hl:.1f}",
              f"{hl - hl0:+.1f} so với toàn mẫu" if dang_loc else None, delta_color="off")
    st.write("")

    # ---------- Hàng 1 (RQ1): khoảng cách | hình thức nhà ở
    ca, cb = st.columns(2, gap="medium")
    with ca:
        with st.container(key="card_bd1"):
            tieu_de_the("Khoảng cách từ nơi ở mới đến nơi ở cũ", "RQ1")
            dem = (d["khoang_cach"].value_counts().reindex(KHOANG_CACH).fillna(0)
                   .astype(int).rename_axis("Khoảng cách").reset_index(name="Số hộ"))
            dem["Nhãn"] = dem.apply(lambda r: f"{r['Số hộ']} ({r['Số hộ'] / max(dem['Số hộ'].sum(), 1) * 100:.0f}%)", axis=1)
            fig1 = px.bar(dem, x="Khoảng cách", y="Số hộ", text="Nhãn", color_discrete_sequence=[BLUE])
            fig1.update_traces(textposition="outside", cliponaxis=False, textfont_size=14)
            fig1.update_layout(xaxis_title=None, yaxis_title="Số hộ",
                               yaxis_range=[0, max(dem["Số hộ"].max(), 1) * 1.3])
            dat_nhan_truc_x(fig1, KHOANG_CACH)
            hien_thi_bieu_do(fig1, 400)
            st.caption("Khoảng cách do người trả lời ước tính.")
    with cb:
        with st.container(key="card_bd2"):
            tieu_de_the("Hình thức nhà ở trước và sau di dời", "RQ1")
            truoc = d["nha_o_truoc"].value_counts().reindex(NHA_O).fillna(0)
            sau = d["nha_o_sau"].value_counts().reindex(NHA_O).fillna(0)
            fig2 = go.Figure()
            fig2.add_bar(x=NHA_O, y=truoc.values, name="Trước di dời", marker_color=BLUE_L,
                         text=truoc.values.astype(int), textposition="outside")
            fig2.add_bar(x=NHA_O, y=sau.values, name="Sau di dời", marker_color=BLUE,
                         text=sau.values.astype(int), textposition="outside")
            fig2.update_layout(barmode="group", yaxis_title="Số hộ",
                               yaxis_range=[0, max(truoc.max(), sau.max(), 1) * 1.3])
            dat_nhan_truc_x(fig2, NHA_O)
            hien_thi_bieu_do(fig2, 400, chu_giai_tren=True)
            st.caption("Cột nhạt: trước di dời · cột đậm: sau di dời.")

    # ---------- Hàng 2 (RQ1): bảng chuyển đổi nhà ở + nhận xét tự động
    with st.container(key="card_bd3"):
        tieu_de_the("Bảng chuyển đổi hình thức nhà ở", "dòng = trước · cột = sau")
        cc, cd = st.columns([3, 2], gap="large")
        with cc:
            chuyen = pd.crosstab(d["nha_o_truoc"], d["nha_o_sau"]).reindex(
                index=NHA_O, columns=NHA_O, fill_value=0)
            fig3 = px.imshow(chuyen.values, x=NHA_O, y=NHA_O, text_auto=True, aspect="auto",
                             color_continuous_scale=["#FFFFFF", BLUE])
            fig3.update_layout(coloraxis_showscale=False, xaxis_title=None, yaxis_title=None)
            fig3.update_traces(textfont_size=16)
            fig3.update_xaxes(tickangle=-25)
            hien_thi_bieu_do(fig3, 380)
        with cd:
            giu_nguyen = int((d["nha_o_truoc"] == d["nha_o_sau"]).sum())
            sang_thue = int(((d["nha_o_truoc"] != "Thuê") & (d["nha_o_sau"] == "Thuê")).sum())
            co_vay = int(((d["nha_o_truoc"] != "Sở hữu, có vay") & (d["nha_o_sau"] == "Sở hữu, có vay")).sum())
            st.markdown("**Cách đọc:** mỗi ô là số hộ đi từ hình thức ở dòng sang hình thức ở cột; "
                        "đường chéo là số hộ giữ nguyên.")
            st.markdown(
                f"<div class='note'>🔹 <b>{giu_nguyen}/{len(d)}</b> hộ giữ nguyên hình thức nhà ở.<br>"
                f"🔹 <b>{sang_thue}</b> hộ chuyển sang <b>thuê</b>.<br>"
                f"🔹 <b>{co_vay}</b> hộ chuyển sang <b>sở hữu có vay</b>.</div>",
                unsafe_allow_html=True)

    # ---------- Hàng 3 (RQ2): thời gian đi học / đi làm
    with st.container(key="card_bd4"):
        tieu_de_the("Thay đổi thời gian đi học và đi làm", "RQ2")
        lua_chon = st.radio("Xem theo", ["Đi học của con", "Đi làm của phụ huynh"],
                            horizontal=True, key="xem_di_lai")
        if lua_chon == "Đi học của con":
            c_truoc, c_sau, c_doi, thu_tu = "tg_hoc_truoc", "tg_hoc_sau", "doi_tg_hoc", TG_DI_HOC
        else:
            c_truoc, c_sau, c_doi, thu_tu = "tg_lam_truoc", "tg_lam_sau", "doi_tg_lam", TG_DI_LAM
        g1, g2 = st.columns([3, 2], gap="large")
        with g1:
            a = d[c_truoc].value_counts().reindex(thu_tu).fillna(0)
            b = d[c_sau].value_counts().reindex(thu_tu).fillna(0)
            fig4 = go.Figure()
            fig4.add_bar(x=thu_tu, y=a.values, name="Trước di dời", marker_color=BLUE_L)
            fig4.add_bar(x=thu_tu, y=b.values, name="Sau di dời", marker_color=BLUE)
            fig4.update_layout(barmode="group", yaxis_title="Số hộ")
            hien_thi_bieu_do(fig4, 360, chu_giai_tren=True)
        with g2:
            thu_tu_doi = ["Giảm", "Không đổi", "Tăng"]
            cnt = d[c_doi].value_counts().reindex(thu_tu_doi).fillna(0)
            if cnt.sum() == 0:
                st.info("Không có hộ nào xác định được thay đổi trong nhóm đang lọc.")
            else:
                fig4b = px.pie(names=cnt.index, values=cnt.values, hole=0.58, color=cnt.index,
                               color_discrete_map={"Giảm": TEAL, "Không đổi": GREY, "Tăng": RED})
                fig4b.update_traces(textinfo="label+percent", sort=False, textfont_size=15)
                fig4b.update_layout(showlegend=False)
                hien_thi_bieu_do(fig4b, 360)
        if lua_chon == "Đi làm của phụ huynh":
            st.caption("Hộ 'Không thường xuyên' đi làm không được tính vào biểu đồ tròn.")

    # ---------- Hàng 4 (RQ3 & H2): ưu tiên | giữ trường theo ưu tiên
    ce, cf = st.columns(2, gap="medium")
    with ce:
        with st.container(key="card_bd5"):
            tieu_de_the("Mức quan trọng của các yếu tố", "RQ3 · thang 1–5")
            tb = pd.DataFrame({"Yếu tố": YEU_TO,
                               "Điểm trung bình": [d[COT_QT[t]].mean() for t in YEU_TO]
                               }).sort_values("Điểm trung bình")
            fig5 = px.bar(tb, x="Điểm trung bình", y="Yếu tố", orientation="h",
                          text=tb["Điểm trung bình"].round(2), color_discrete_sequence=[SKY])
            fig5.update_layout(xaxis_range=[0, 5.8], yaxis_title=None, xaxis_title=None)
            fig5.update_traces(textposition="outside", cliponaxis=False, textfont_size=15)
            hien_thi_bieu_do(fig5, 340)
    with cf:
        with st.container(key="card_bd6"):
            tieu_de_the("Giữ trường theo mức ưu tiên giữ trường", "mô tả khám phá cho H2")
            nhom = pd.crosstab(d["nhom_uu_tien_truong"], d["giu_truong"]).reindex(
                columns=GIU_TRUONG, fill_value=0)
            ty_le = nhom.div(nhom.sum(axis=1), axis=0) * 100
            mau = {"Giữ tất cả": BLUE, "Một số chuyển": BLUE_L, "Tất cả chuyển": GREY}
            nhan_y = [f"{k} · n={int(nhom.loc[k].sum())}" for k in ty_le.index]
            fig6 = go.Figure()
            for cot in GIU_TRUONG:
                fig6.add_bar(y=nhan_y, x=ty_le[cot].values, name=cot, orientation="h",
                             marker_color=mau[cot], text=[f"{v:.0f}%" for v in ty_le[cot].values],
                             textposition="inside", textfont_size=14)
            fig6.update_layout(barmode="stack", xaxis_range=[0, 100], xaxis_title="% hộ", yaxis_title=None)
            hien_thi_bieu_do(fig6, 340, chu_giai_tren=True)
            st.caption("Chỉ mô tả; không suy ra nhân quả. Nhóm dưới 5 hộ không diễn giải.")

    with st.expander("Xem và tải bảng dữ liệu đang lọc (đã ẩn danh)"):
        bang = d[[c for c in CAC_COT_GOC if c in d.columns]]
        st.dataframe(bang, hide_index=True)
        st.download_button("⬇️ Tải dữ liệu đang lọc (CSV)", bang.to_csv(index=False).encode("utf-8-sig"),
                           file_name="du_lieu_dang_loc.csv", mime="text/csv")


with tab2:
    tieu_de_muc("Dashboard", "Kết quả khảo sát trực quan",
                "Dùng bộ lọc để xem kết quả theo từng nhóm hộ. Số liệu là dữ liệu giả lập minh họa.")
    khung_dashboard(df)

# =============================================================================
# TAB 3. CÔNG CỤ QUYẾT ĐỊNH (THỜI GIAN THỰC) + GÓC TÀI CHÍNH
# =============================================================================
# 5 phương án giả lập. Điểm 1–5 cho từng yếu tố theo thứ tự YEU_TO:
# [tài chính, giữ trường, thời gian đi làm, hỗ trợ người thân]. Điểm càng cao =
# phương án càng "dễ đáp ứng" yếu tố đó. Đây là GIẢ ĐỊNH MINH HỌA của nhóm nghiên cứu.
PHUONG_AN = [
    {"ten": "A. Thuê nhà gần khu cũ (dưới 3 km)", "ngan": "A. Thuê gần khu cũ", "diem": [2, 5, 4, 3],
     "duoc": "Giữ trường cũ, đi làm thuận tiện",
     "doi": "Tiền thuê cao, không gian nhỏ, chưa có tài sản sở hữu"},
    {"ten": "B. Mua nhà có vay (3–7 km)", "ngan": "B. Mua nhà có vay", "diem": [2, 4, 3, 3],
     "duoc": "Có nhà sở hữu, vẫn tương đối gần trường",
     "doi": "Gánh nặng trả nợ dài hạn, thời gian di chuyển tăng nhẹ"},
    {"ten": "C. Nhà sở hữu giá mềm (7–15 km)", "ngan": "C. Nhà giá mềm xa hơn", "diem": [4, 2, 2, 3],
     "duoc": "Chi phí nhà ở thấp hơn, diện tích lớn hơn",
     "doi": "Nhiều khả năng phải đổi trường, đi làm xa hơn"},
    {"ten": "D. Ở cùng/gần người thân", "ngan": "D. Ở cùng người thân", "diem": [5, 2, 3, 5],
     "duoc": "Tiết kiệm chi phí, có người đưa đón, trông nom con",
     "doi": "Ít riêng tư, sinh hoạt chung, phụ thuộc điều kiện người thân"},
    {"ten": "E. Ngoài Hà Nội / vùng xa", "ngan": "E. Ngoài Hà Nội", "diem": [5, 1, 1, 2],
     "duoc": "Chi phí nhà ở thấp nhất, quỹ đất rộng",
     "doi": "Gần như chắc chắn đổi trường, đi làm rất xa, xa mạng lưới hỗ trợ"},
]
KHOA_W = {"Khả năng tài chính": "w_tc", "Ưu tiên giữ trường": "w_tr",
          "Giới hạn thời gian đi làm": "w_dl", "Hỗ trợ từ người thân": "w_ht"}
KICH_BAN_MAU = [
    ("Giữ trường + ngân sách", [5, 5, 3, 2]),
    ("Đi làm gần + ngân sách", [5, 2, 5, 2]),
    ("Cần người thân", [4, 3, 3, 5]),
    ("Đặt lại", [3, 3, 3, 3]),
]
for _k in KHOA_W.values():
    st.session_state.setdefault(_k, 3)      # giá trị khởi tạo của thanh trượt


def ap_kich_ban(gia_tri):
    """Gán mức ưu tiên của kịch bản mẫu vào 4 thanh trượt."""
    for khoa, v in zip(KHOA_W.values(), gia_tri):
        st.session_state[khoa] = v


def tinh_phuong_an(w):
    """Mức khớp (%) = Σ(mức quan trọng × điểm phương án) ÷ (5 × Σ mức quan trọng) × 100.
    Trả về danh sách dict sắp xếp giảm dần; 'dong_gop' = phần điểm do từng yếu tố (cộng lại = mức khớp)."""
    tong = sum(w)
    ds = []
    for pa in PHUONG_AN:
        dong_gop = [wi * si / (5 * tong) * 100 for wi, si in zip(w, pa["diem"])]
        # Xung đột: yếu tố được chấm quan trọng (>=4) nhưng phương án đáp ứng kém (<=2)
        xung_dot = [YEU_TO[i] for i in range(4) if w[i] >= 4 and pa["diem"][i] <= 2]
        ds.append({**pa, "dong_gop": dong_gop, "khop": sum(dong_gop), "xung_dot": xung_dot})
    return sorted(ds, key=lambda x: x["khop"], reverse=True)


def goi_y_danh_doi(w):
    """Quy tắc 'nếu – thì' về đánh đổi thường gặp. w = [tài chính, giữ trường, đi làm, người thân]."""
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


@st.fragment   # kéo thanh trượt chỉ chạy lại phần này -> cập nhật tức thì
def khung_cong_cu():
    with st.container(key="card_cc_gioi_thieu"):
        tieu_de_the("Cách dùng", "kết quả tự cập nhật khi kéo thanh trượt")
        st.markdown(
            "Chấm mức quan trọng từ **1 (ít quan trọng)** đến **5 (rất quan trọng)** cho từng yếu tố. "
            "Công cụ **không quyết định thay gia đình**, không dự báo một hộ cụ thể và không xác định phương án đúng."
        )
        st.caption("Hoặc thử nhanh một kịch bản mẫu:")
        cot_nut = st.columns(len(KICH_BAN_MAU), gap="medium")
        for o, (nhan, gia_tri) in zip(cot_nut, KICH_BAN_MAU):
            o.button(nhan, on_click=ap_kich_ban, args=(gia_tri,), key="nut_" + nhan)

    cs, ck = st.columns([2, 3], gap="medium")
    with cs:
        with st.container(key="card_thanh_truot"):
            tieu_de_the("Mức quan trọng của bạn", "1–5")
            st.slider("1. Khả năng tài chính", 1, 5, key=KHOA_W["Khả năng tài chính"],
                      help="Điểm cao = ngân sách nhà ở bị hạn chế, cần tiết kiệm chi phí.")
            st.slider("2. Ưu tiên giữ trường cho con", 1, 5, key=KHOA_W["Ưu tiên giữ trường"])
            st.slider("3. Giới hạn thời gian đi làm", 1, 5, key=KHOA_W["Giới hạn thời gian đi làm"],
                      help="Điểm cao = muốn nơi ở gần nơi làm việc.")
            st.slider("4. Hỗ trợ từ người thân", 1, 5, key=KHOA_W["Hỗ trợ từ người thân"])

    w = [st.session_state[KHOA_W[t]] for t in YEU_TO]
    kq = tinh_phuong_an(w)
    top, nhi = kq[0], kq[1]
    chenh_lech = top["khop"] - nhi["khop"]

    with ck:
        with st.container(key="card_diem_so"):
            tieu_de_the("Điểm khớp của từng kịch bản", "mỗi màu = phần điểm do một yếu tố đóng góp")
            thu_tu_ve = list(reversed(kq))          # phương án khớp nhất nằm trên cùng
            mau_yt = [NAVY, SKY, TEAL, AMBER]
            fig = go.Figure()
            for i, ten_yt in enumerate(YEU_TO):
                fig.add_bar(y=[p["ngan"] for p in thu_tu_ve], x=[p["dong_gop"][i] for p in thu_tu_ve],
                            name=ten_yt, orientation="h", marker_color=mau_yt[i],
                            hovertemplate="%{y}<br>" + ten_yt + ": %{x:.1f} điểm<extra></extra>")
            for p in thu_tu_ve:
                fig.add_annotation(x=p["khop"], y=p["ngan"], text=f"<b>{p['khop']:.0f}%</b>",
                                   xanchor="left", xshift=6, showarrow=False, font=dict(size=16))
            fig.update_layout(barmode="stack", xaxis_range=[0, 115],
                              xaxis_title="Mức khớp ưu tiên (%)", yaxis_title=None)
            hien_thi_bieu_do(fig, 430, chu_giai_tren=True)

    ca, cb = st.columns([2, 3], gap="medium")
    with ca:
        with st.container(key="card_radar"):
            tieu_de_the("Ưu tiên của bạn so với phương án khớp nhất")
            nhan_truc = ["Tài chính", "Giữ trường", "Đi làm gần", "Người thân"]
            dong = nhan_truc + nhan_truc[:1]
            radar = go.Figure()
            radar.add_trace(go.Scatterpolar(r=w + w[:1], theta=dong, fill="toself",
                                            name="Mức quan trọng bạn chọn", line=dict(color=BLUE),
                                            fillcolor="rgba(29,78,216,.25)"))
            radar.add_trace(go.Scatterpolar(r=top["diem"] + top["diem"][:1], theta=dong,
                                            name=f"Điểm đáp ứng – {top['ngan']}",
                                            line=dict(color=AMBER, dash="dash")))
            radar.update_layout(polar=dict(radialaxis=dict(range=[0, 5], dtick=1)))
            hien_thi_bieu_do(radar, 400, le=dict(l=100, r=100, t=30, b=10))
    with cb:
        with st.container(key="card_phan_tich"):
            tieu_de_the("Gợi ý phân tích đánh đổi", "tự cập nhật theo ưu tiên")
            k1, k2, k3 = st.columns(3, gap="small")
            with k1:
                o_chi_so("Khớp nhất", top["ngan"])
            with k2:
                o_chi_so("Mức khớp", f"{top['khop']:.0f}%")
            with k3:
                o_chi_so("Hơn phương án thứ hai", f"{chenh_lech:.1f} điểm %")
            st.write("")
            if chenh_lech < 3:
                st.markdown(f"<div class='note'>Hai phương án đầu (<b>{top['ngan']}</b> và "
                            f"<b>{nhi['ngan']}</b>) gần như ngang nhau; ưu tiên của bạn chưa đủ phân biệt, "
                            f"quyết định sẽ phụ thuộc yếu tố ngoài mô hình.</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='note'>Với ưu tiên hiện tại, <b>{top['ten']}</b> khớp nhất.<br>"
                            f"✅ <b>Đạt được:</b> {top['duoc']}.<br>⚖️ <b>Phải đánh đổi:</b> {top['doi']}.</div>",
                            unsafe_allow_html=True)
            if top["xung_dot"]:
                st.warning("Phương án khớp nhất vẫn kém ở yếu tố bạn đặt cao: " + ", ".join(top["xung_dot"]) + ".")
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

    with st.container(key="card_bang"):
        tieu_de_the("Bảng phân tích đánh đổi chi tiết", "xếp theo mức khớp giảm dần")
        bang = pd.DataFrame([{
            "Phương án": p["ten"], "Mức khớp ưu tiên (%)": round(p["khop"], 1),
            "Điều đạt được": p["duoc"], "Điều phải đánh đổi": p["doi"],
            "Xung đột với ưu tiên cao": ", ".join(p["xung_dot"]) if p["xung_dot"] else "—",
        } for p in kq])
        st.dataframe(bang, hide_index=True)
        with st.expander("Cách tính (để giải thích trước hội đồng)"):
            st.markdown(
                "- Mỗi phương án có điểm 1–5 cho 4 yếu tố (giả định minh họa).\n"
                "- **Mức khớp (%) = Σ(mức quan trọng × điểm phương án) ÷ (5 × Σ mức quan trọng) × 100.**\n"
                "- Biểu đồ cột chồng tách mức khớp thành phần đóng góp của từng yếu tố.\n"
                "- 'Xung đột' xuất hiện khi yếu tố được chấm ≥ 4 nhưng phương án chỉ đạt ≤ 2 điểm.\n"
                "- Mức khớp cao **không có nghĩa** đó là lựa chọn đúng; chỉ phản ánh sự phù hợp với ưu tiên đã nhập.")


@st.fragment
def khung_tai_chinh():
    """Góc chuyên đề tài chính: tính tổng chi phí nhà ở + đi lại và tỷ trọng so với thu nhập.
    Các số nhập chỉ dùng để tính tại chỗ, không được lưu hay gửi đi đâu."""
    with st.container(key="card_tai_chinh"):
        tieu_de_the("Góc chuyên đề: cân đối chi phí khi di dời", "số nhập không được lưu trữ")
        c1, c2, c3 = st.columns(3, gap="medium")
        with c1:
            thu_nhap = st.number_input("Thu nhập ổn định của hộ mỗi tháng (đ)", min_value=0,
                                       value=30_000_000, step=1_000_000)
        with c2:
            chi_nha = st.number_input("Chi phí thuê/trả góp nhà mỗi tháng (đ)", min_value=0,
                                      value=10_000_000, step=500_000)
        with c3:
            chi_di_lai = st.number_input("Chi phí đi lại phát sinh thêm mỗi tháng (đ)", min_value=0,
                                         value=2_000_000, step=200_000)
        tong = chi_nha + chi_di_lai
        r1, r2, r3 = st.columns(3, gap="medium")
        with r1:
            o_chi_so("Tổng chi phí duy trì / tháng", vnd(tong))
        with r2:
            o_chi_so("Quy đổi cả năm", vnd(tong * 12))
        with r3:
            o_chi_so("Tỷ trọng so với thu nhập", f"{tong / thu_nhap * 100:.0f}%" if thu_nhap > 0 else "—")
        if thu_nhap > 0:
            ty_le = tong / thu_nhap * 100
            mau = "#0EA5A4" if ty_le <= 30 else ("#F59E0B" if ty_le <= 40 else "#DC2626")
            st.markdown(
                f"<div style='margin:1rem 0 .3rem;background:#E9EEF7;border-radius:999px;height:14px;overflow:hidden'>"
                f"<div style='width:{min(ty_le, 100):.0f}%;height:100%;background:{mau}'></div></div>",
                unsafe_allow_html=True)
            st.caption("Nhiều tài liệu tài chính cá nhân dùng mốc tham chiếu khoảng 30–40% thu nhập cho chi phí "
                       "nhà ở. Đây chỉ là mốc tham khảo chung, mỗi hộ có hoàn cảnh riêng.")


with tab3:
    tieu_de_muc("Công cụ tương tác", "Mô phỏng đánh đổi khi chọn nơi ở",
                "Kéo thanh trượt để thấy các kịch bản thay đổi ngay lập tức.")
    khung_cong_cu()
    st.write("")
    khung_tai_chinh()
    st.markdown(
        "<div class='disclaimer'>⚠️ Công cụ này chỉ mang tính chất minh họa dựa trên dữ liệu khảo sát "
        "nghiên cứu khoa học, không phải lời khuyên tài chính hay pháp lý tuyệt đối.</div>",
        unsafe_allow_html=True)

# =============================================================================
# TAB 4. TƯ LIỆU THỰC ĐỊA
# =============================================================================
with tab4:
    tieu_de_muc("Tư liệu", "Khu vực Vành đai 2.5: Ngụy Như Kon Tum – Nhân Hòa – Nguyễn Trãi",
                "Hình ảnh và video tư liệu về khu vực nghiên cứu.")
    with st.container(key="card_anh"):
        tieu_de_the("Hình ảnh tư liệu")
        if ANH_TU_LIEU:
            cot_anh = st.columns(len(ANH_TU_LIEU), gap="medium")
            for o, (nguon, chu_thich) in zip(cot_anh, ANH_TU_LIEU):
                with o:
                    hien_thi_anh(nguon, chu_thich)
        st.caption("Ảnh lấy từ nguồn báo chí trực tuyến, chỉ dùng minh họa học thuật. "
                   "Nên bổ sung ảnh do nhóm tự chụp kèm ngày chụp.")
    with st.container(key="card_video"):
        tieu_de_the("Video cập nhật tiến độ dự án")
        if VIDEO_TU_LIEU:
            cot_vd = st.columns(len(VIDEO_TU_LIEU), gap="medium")
            for o, (url, tieu_de) in zip(cot_vd, VIDEO_TU_LIEU):
                with o:
                    st.markdown(f"**{tieu_de}**")
                    try:
                        st.video(url)
                    except Exception:
                        st.info("Không phát được video này.")

# =============================================================================
# TAB 5. TÀI LIỆU MỞ & PHẢN HỒI
# =============================================================================
with tab5:
    tieu_de_muc("Khoa học mở", "Tài liệu, dữ liệu và phản hồi",
                "Dữ liệu công khai chỉ gồm kết quả đã mã hóa, ẩn danh tuyệt đối.")
    d1, d2 = st.columns(2, gap="medium")
    with d1:
        with st.container(key="card_co"):
            tieu_de_the("Dữ liệu có trong bộ công khai")
            st.markdown(
                """
- Mã phiếu ngẫu nhiên (H001, H002…), không liên hệ được với người trả lời.
- Khoảng cách theo **nhóm** (không phải số chính xác).
- Hình thức nhà ở trước – sau, giữ/đổi trường, nhóm thời gian đi lại.
- Mức quan trọng các yếu tố và mức hài lòng (thang 1–5).
                """)
    with d2:
        with st.container(key="card_khong"):
            tieu_de_the("Không thu thập")
            st.markdown(
                """
- Họ tên, số điện thoại, email.
- Địa chỉ cũ/mới, vị trí GPS.
- Tên trường, tên nơi làm việc.
- Thu nhập, dư nợ, số tiền bồi thường chính xác.
                """)

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
            ["kha_nang_tai_chinh", "Mức nguồn lực tài chính huy động được khi chốt nơi ở (thấp = 1–2)", "Thang 1–5"],
            ["so_phuong_an", "Số phương án đã cân nhắc", "Số nguyên"],
            ["hai_long", "Mức hài lòng sau di dời", "Thang 1–5"],
        ], columns=["Tên biến", "Ý nghĩa", "Kiểu dữ liệu"])
        st.dataframe(tu_dien, hide_index=True)
        st.download_button("⬇️ Tải dữ liệu mẫu (CSV)", df_goc.to_csv(index=False).encode("utf-8-sig"),
                           file_name="du_lieu_vanh_dai_2_5.csv", mime="text/csv")

    with st.container(key="card_so_tay"):
        tieu_de_the("Sổ tay Python phân tích dữ liệu")
        st.markdown(
            "Sổ tay thực hiện toàn bộ quy trình và **tái tạo được mọi bảng, biểu đồ** từ dữ liệu đã xử lý: "
            "nhập dữ liệu → kiểm tra điều kiện tham gia → mã hóa biến → tạo biến thay đổi trước–sau → "
            "xuất bảng mô tả → ba kiểm tra đã định trước (H1–H3) → vẽ biểu đồ.")
        if NOTEBOOK_URL:
            st.link_button("🔗 Mở hướng dẫn đọc sổ tay Python", NOTEBOOK_URL)
        else:
            st.info("Đường dẫn sổ tay sẽ được cập nhật.")
        with st.expander("Quy tắc kiểm tra giả thuyết (H1–H3)"):
            st.markdown(
                "- Chỉ kiểm tra khi tổng mẫu ≥ 30 và mỗi nhóm so sánh có ≥ 5 quan sát; "
                "nếu không, chỉ báo cáo số lượng và tỷ lệ.\n"
                "- Dùng bảng 2×2 và kiểm định Fisher; kết quả chỉ mang tính khám phá.\n"
                "- Kết quả không ủng hộ giả thuyết thì giữ nguyên, không đổi giả thuyết sau khi xem dữ liệu.")

    with st.container(key="card_phan_hoi"):
        tieu_de_the("Góp ý cho nghiên cứu")
        with st.form("form_gop_y"):
            ten = st.text_input("Họ tên / Đơn vị (không bắt buộc)")
            noi_dung = st.text_area("Nội dung góp ý / nhận xét")
            gui = st.form_submit_button("Soạn email góp ý")
        if gui:
            if not noi_dung.strip():
                st.warning("Vui lòng nhập nội dung góp ý.")
            elif EMAIL_PHAN_HOI:
                from urllib.parse import quote
                lien_ket = (f"mailto:{EMAIL_PHAN_HOI}?subject={quote('Góp ý đề tài Vành đai 2.5')}"
                            f"&body={quote(chr(10).join(['Người gửi: ' + ten, '', noi_dung]))}")
                st.success("Bấm liên kết dưới đây để mở email và gửi góp ý:")
                st.markdown(f"[✉️ Mở email để gửi]({lien_ket})")
            else:
                st.info("Trang web chưa lưu góp ý trực tiếp. Bạn vui lòng gửi góp ý qua giáo viên "
                        "hướng dẫn hoặc nhóm nghiên cứu. Cảm ơn bạn!")

st.markdown(
    f"<p style='text-align:center;color:#5B6B85;font-size:.98rem;margin-top:2rem'>© {NAM} · Đề tài NCKH học sinh phổ thông · "
    "Nguyễn Vũ Tuấn Minh (12 Tin 1, THPT chuyên Hà Nội – Amsterdam)</p>",
    unsafe_allow_html=True,
)
