# -*- coding: utf-8 -*-
"""
CÔNG CỤ TRỰC QUAN HÓA & HỖ TRỢ QUYẾT ĐỊNH  -  PHIÊN BẢN THIẾT KẾ LẠI (v3)
Đề tài: Lựa chọn nơi ở sau di dời của hộ gia đình có con đang học phổ thông
        bị ảnh hưởng bởi dự án Vành đai 2.5 đoạn Ngụy Như Kon Tum – Nhân Hòa – Nguyễn Trãi
Tác giả: Nguyễn Vũ Tuấn Minh (Lớp 12 Tin 1, THPT chuyên Hà Nội – Amsterdam)

Thư viện: streamlit (>=1.40), pandas, numpy, plotly
Các tệp đi kèm (đặt cùng thư mục với app.py trên GitHub):
    processed_data.csv      dữ liệu đã mã hóa, ẩn danh
    NNKT2.jpg               ảnh nền banner (nên nén về ~1600 px, dưới 500 KB)
    ANH TUAN MINH.jpg       ảnh tác giả
    NHOM NGHIEN CUU.jpg     ảnh nhóm nghiên cứu
Thiếu tệp ảnh thì ứng dụng vẫn chạy, chỉ bỏ qua phần ảnh.

HỆ THỐNG THIẾT KẾ (tóm tắt để trình bày):
    - Màu: xanh chủ đạo #1F5FD1, xanh navy #0B2F63 cho tiêu đề/banner, nền #F4F7FC,
      thẻ trắng bo góc 18 px đổ bóng nhẹ; màu nhấn: ngọc (tích cực), cam (nổi bật), san hô (tăng/cảnh báo).
    - Chữ: Be Vietnam Pro (hỗ trợ tiếng Việt), nội dung 17-18 px, tiêu đề mục 26-30 px.
    - Bố cục: lưới 2 cột cân xứng, mỗi mục có "nhãn nhỏ + tiêu đề lớn", hạn chế biểu tượng cảm xúc.
"""

import base64
import html
import os
from urllib.parse import quote, urlparse

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# =============================================================================
# PHẦN 0. CẤU HÌNH - CHỈ CẦN SỬA Ở ĐÂY KHI THAY NỘI DUNG
# =============================================================================
st.set_page_config(
    page_title="Lựa chọn nơi ở sau di dời - Vành đai 2.5",
    page_icon="🏡",
    layout="wide",
    initial_sidebar_state="expanded",
)

FILE_DU_LIEU = "processed_data.csv"
ANH_BANNER = "NNKT2.jpg"
ANH_TAC_GIA = "ANH TUAN MINH.jpg"
ANH_NHOM = "NHOM NGHIEN CUU.jpg"

# Đặt False khi đã thay bằng dữ liệu khảo sát thật -> banner "DỮ LIỆU GIẢ LẬP" sẽ biến mất
DU_LIEU_GIA_LAP = True

NOTEBOOK_URL = ""      # đường dẫn sổ tay Python (GitHub/Colab); để trống nếu chưa có
EMAIL_LIEN_HE = ""     # email nhận góp ý, ví dụ "ten@gmail.com"; để trống nếu chưa có
FORM_GOP_Y_URL = ""    # đường dẫn Google Form góp ý (nếu có)

# Ảnh thực địa: (đường dẫn ảnh hoặc tên tệp trong repo, chú thích)
# LƯU Ý: cần kiểm tra lại các đường dẫn ảnh/video bên ngoài còn hoạt động và ghi rõ nguồn.
ANH_THUC_DIA = [
    ("https://photo-baomoi.bmcdn.me/w700_r1/2024_03_14_119_48574343/c70c1a9c40339ab30325.jpg",
     "Khu vực nút giao Ngụy Như Kon Tum hoàn thành giải phóng mặt bằng"),
    ("https://hanoimoi.vn/Uploads/Images/2024/04/10/746820/thanh-xuan-tang-toc-giai-phong-mat-bang-du-an-vanh-dai-2-5-4.jpg",
     "Đoạn qua phố Nhân Hòa trong quá trình thi công xây dựng"),
    ("https://cms.giaoduc.net.vn/uploaded/2024/2/18/giai-phong-mat-bang-duong-vanh-dai-25-1.jpg",
     "Khu vực kết nối với trục đường Nguyễn Trãi"),
]
VIDEO = [
    ("Toàn cảnh đoạn Ngụy Như Kon Tum – Nhân Hòa", "https://www.youtube.com/watch?v=Xh0wJk6k_H8"),
    ("Thi công kết nối Vành đai 2.5 – Nguyễn Trãi", "https://www.youtube.com/watch?v=Oq7m9P0r2w8"),
]

# ---- Bảng màu dùng cho biểu đồ (khớp với biến CSS bên dưới)
PRIMARY = "#1F5FD1"
NAVY = "#0B2F63"
SKY = "#A9C4F5"
TEAL = "#0FA3A3"
AMBER = "#F2A93B"
CORAL = "#E5604D"
GREY = "#CBD5E1"
LINE = "#E3EAF5"

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
# Nhãn ngắn (đã ngắt dòng) dùng cho trục x của biểu đồ, cùng thứ tự với danh sách gốc
NHAN_KC = ["Dưới<br>3 km", "3–7<br>km", "7–15<br>km", "Trên 15 km<br>(trong HN)", "Ngoài<br>Hà Nội"]
NHAN_NHA = ["Sở hữu,<br>không vay", "Sở hữu,<br>có vay", "Thuê", "Ở cùng<br>người thân", "Tạm thời<br>/khác"]
YEU_TO = ["Khả năng tài chính", "Ưu tiên giữ trường",
          "Giới hạn thời gian đi làm", "Hỗ trợ từ người thân"]
COT_QT = {"Khả năng tài chính": "qt_tai_chinh", "Ưu tiên giữ trường": "qt_giu_truong",
          "Giới hạn thời gian đi làm": "qt_di_lam", "Hỗ trợ từ người thân": "qt_nguoi_than"}
# Tên cột kiểu cũ -> tên cột chuẩn (để tệp CSV cũ vẫn đọc được)
TEN_COT_CU = {"ID": "ma_phieu", "Khoang_cach": "khoang_cach", "Nha_truoc": "nha_o_truoc",
              "Nha_sau": "nha_o_sau", "Giu_truong": "giu_truong", "Hai_long": "hai_long"}


# =============================================================================
# PHẦN 1. GIAO DIỆN: ẢNH, CSS, HÀM DỰNG THÀNH PHẦN
# =============================================================================
@st.cache_data(show_spinner=False)
def anh_data_uri(duong_dan: str) -> str:
    """Đọc ảnh cục bộ và mã hóa base64 để nhúng vào HTML/CSS. Không có ảnh -> chuỗi rỗng."""
    if not duong_dan or not os.path.exists(duong_dan):
        return ""
    duoi = os.path.splitext(duong_dan)[1].lower().strip(".")
    loai = "png" if duoi == "png" else "jpeg"
    with open(duong_dan, "rb") as f:
        return f"data:image/{loai};base64," + base64.b64encode(f.read()).decode()


def nguon_anh(nguon: str) -> str:
    """Đường dẫn http giữ nguyên; tên tệp trong repo thì đổi thành data URI."""
    return nguon if nguon.startswith("http") else anh_data_uri(nguon)


CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700;800&display=swap');

:root{
  --ink:#0E1B33; --navy:#0B2F63; --primary:#1F5FD1; --primary-2:#4C8DF0;
  --sky:#DCE9FD; --mist:#F4F7FC; --line:#E3EAF5; --text:#24324B; --muted:#5F6E85;
  --teal:#0FA3A3; --amber:#F2A93B; --coral:#E5604D;
  --shadow:0 10px 30px rgba(15,40,90,.08);
}

/* ---------- Nền, phông chữ, cỡ chữ ---------- */
.stApp{ background:linear-gradient(180deg,#EEF3FB 0%,#F7F9FD 320px,#F7F9FD 100%); }
html, body, .stApp, .stMarkdown, .stMarkdown *, [data-testid="stWidgetLabel"] *,
[data-testid="stMetric"] *, [data-baseweb="tab"] p, button p, input, textarea,
[data-testid="stCaptionContainer"] *{
  font-family:'Be Vietnam Pro','Segoe UI',system-ui,-apple-system,Roboto,Arial,sans-serif;
}
.block-container{ padding-top:1.2rem; padding-bottom:3rem; max-width:1280px; }
.stMarkdown p, .stMarkdown li{ font-size:1.1rem; line-height:1.75; color:var(--text); }
.stMarkdown strong{ color:var(--ink); }
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] *{
  font-size:.98rem !important; color:var(--muted) !important; }
[data-testid="stWidgetLabel"] p{ font-size:1.05rem !important; font-weight:600; color:var(--ink); }
[data-testid="stSliderThumbValue"]{ font-size:1.05rem; font-weight:700; color:var(--primary); }
[data-baseweb="select"] *{ font-size:1rem; }
.stRadio label p, .stCheckbox label p{ font-size:1.05rem !important; }

/* Ẩn phần thừa của Streamlit nhưng GIỮ nút mở/đóng thanh bên */
#MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"]{ visibility:hidden; height:0; }
header[data-testid="stHeader"]{ background:transparent; }

/* ---------- Thẻ nổi ---------- */
div[class*="st-key-card"]{
  background:#fff; border:1px solid var(--line); border-radius:18px;
  box-shadow:var(--shadow); padding:1.5rem 1.7rem; margin-bottom:.4rem;
}
div[class*="st-key-card_loc"]{ background:var(--sky); border-color:#C6DAF8; box-shadow:none; }
/* Các cột trong cùng một hàng có chiều cao bằng nhau -> bố cục cân xứng */
[data-testid="stHorizontalBlock"]{ align-items:stretch; }
[data-testid="stColumn"]{ display:flex; flex-direction:column; }
[data-testid="stColumn"] > [data-testid="stVerticalBlock"]{ flex:1; }
[data-testid="stColumn"] > [data-testid="stVerticalBlock"] > div[class*="st-key-card"]{ height:100%; }
/* Streamlit mới bọc thẻ trong stLayoutWrapper: cho phép giãn để hai thẻ cạnh nhau cao bằng nhau */
[data-testid="stLayoutWrapper"]:has(> div[class*="st-key-card"]){ flex:1 1 auto; }
[data-testid="stLayoutWrapper"] > div[class*="st-key-card"]{ height:100%; }

/* ---------- Tiêu đề mục ---------- */
.eyebrow{ font-size:.82rem; font-weight:700; letter-spacing:.14em; text-transform:uppercase;
  color:var(--primary); margin-bottom:.15rem; }
.sec-title{ font-size:1.75rem; font-weight:800; color:var(--ink); line-height:1.3; margin:0 0 .35rem 0; }
.sec-sub{ font-size:1.08rem; color:var(--muted); line-height:1.65; margin-bottom:.4rem; }
.card-title{ font-size:1.25rem; font-weight:700; color:var(--ink); margin:0 0 .15rem 0; line-height:1.35; }
.card-sub{ font-size:.98rem; color:var(--muted); margin-bottom:.6rem; }
.txt{ font-size:1.1rem; line-height:1.8; color:var(--text); }
.txt + .txt{ margin-top:.8rem; }
.takeaway{ margin-top:.5rem; padding:.65rem .95rem; border-radius:12px; background:var(--mist);
  color:var(--navy); font-size:1rem; line-height:1.55; }

/* ---------- Banner (không dùng lớp phủ giả, chữ luôn nằm trên nền tối) ---------- */
.hero{ border-radius:22px; padding:2.6rem 2.8rem 2.2rem; color:#fff; margin-bottom:1.1rem;
  background-size:cover; background-position:center; box-shadow:0 18px 40px rgba(11,47,99,.28); }
.hero *{ color:#fff !important; }
.hero-eyebrow{ font-size:.85rem; font-weight:700; letter-spacing:.16em; text-transform:uppercase;
  opacity:.92; margin-bottom:.9rem; }
.hero-title{ font-size:2.35rem; font-weight:800; line-height:1.28; max-width:900px;
  text-shadow:0 2px 12px rgba(0,0,0,.35); }
.hero-sub{ font-size:1.2rem; line-height:1.65; max-width:820px; margin-top:.9rem; opacity:.95; }
.chips{ display:flex; gap:.6rem; flex-wrap:wrap; margin-top:1.3rem; }
.chip{ background:rgba(255,255,255,.16); border:1px solid rgba(255,255,255,.4); border-radius:999px;
  padding:.35rem 1rem; font-size:.95rem; font-weight:500; }
.chip.warn{ background:rgba(242,169,59,.28); border-color:rgba(242,169,59,.8); font-weight:700; }
.hero-stats{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:.9rem; margin-top:1.7rem; max-width:820px; }
.hero-stat{ background:rgba(255,255,255,.14); border:1px solid rgba(255,255,255,.3);
  border-radius:16px; padding:.85rem 1.1rem; backdrop-filter:blur(6px); }
.hero-stat .n{ font-size:2rem; font-weight:800; line-height:1.1; }
.hero-stat .l{ font-size:.95rem; opacity:.92; margin-top:.15rem; }

/* ---------- Thanh tab dạng viên thuốc (hỗ trợ cả Streamlit cũ và mới) ---------- */
[role="tablist"], [data-baseweb="tab-list"]{ gap:6px; background:#fff; border:1px solid var(--line);
  border-radius:999px; padding:6px; box-shadow:var(--shadow); margin-bottom:1.3rem; }
[role="tab"], button[data-baseweb="tab"]{ height:auto; padding:.7rem 1.35rem; border-radius:999px; background:transparent; }
[role="tab"] p, button[data-baseweb="tab"] p{ font-size:1.05rem !important; font-weight:600; color:var(--muted) !important; margin:0; }
[role="tab"][aria-selected="true"], button[data-baseweb="tab"][aria-selected="true"]{ background:var(--primary) !important; }
[role="tab"][aria-selected="true"] p, button[data-baseweb="tab"][aria-selected="true"] p{ color:#fff !important; }
[role="tab"] > div:empty, [data-baseweb="tab-highlight"], [data-baseweb="tab-border"]{ display:none !important; }

/* ---------- Ô chỉ số ---------- */
[data-testid="stMetric"]{ background:#fff; border:1px solid var(--line); border-radius:16px;
  padding:1rem 1.2rem; box-shadow:var(--shadow); }
[data-testid="stMetricLabel"] p{ font-size:.95rem !important; color:var(--muted) !important; font-weight:500; }
[data-testid="stMetricValue"]{ font-size:2.2rem; font-weight:800; color:var(--primary); }
.kpi{ background:var(--mist); border:1px solid var(--line); border-radius:14px; padding:.8rem 1rem; height:100%; }
.kpi .nhan{ font-size:.95rem; color:var(--muted); }
.kpi .tri{ font-size:1.3rem; font-weight:800; color:var(--primary); line-height:1.3; }

/* ---------- Nút bấm ---------- */
.stButton > button, .stDownloadButton > button{ border-radius:999px; border:1px solid #C6DAF8;
  background:#fff; color:var(--navy); font-weight:600; padding:.45rem 1.2rem; }
.stButton > button:hover, .stDownloadButton > button:hover{ border-color:var(--primary); color:var(--primary); }
.stButton > button[kind="primary"], .stFormSubmitButton > button{ background:var(--primary); color:#fff; border:none; }

/* ---------- Khối phụ ---------- */
.flow{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:1rem; }
.step{ background:var(--mist); border:1px solid var(--line); border-radius:16px; padding:1.1rem 1.2rem; position:relative; }
.step .so{ display:inline-flex; width:2rem; height:2rem; border-radius:50%; background:var(--primary);
  color:#fff; font-weight:700; align-items:center; justify-content:center; margin-bottom:.5rem; }
.step .tt{ font-weight:700; color:var(--ink); font-size:1.12rem; margin-bottom:.25rem; }
.step .nd{ color:var(--text); font-size:1rem; line-height:1.6; }
.rq-grid{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:1rem; }
.rq{ border:1px solid var(--line); border-radius:16px; padding:1rem 1.2rem; background:#fff; }
.rq b{ display:inline-block; color:#fff; background:var(--navy); border-radius:8px; padding:.05rem .6rem;
  font-size:.9rem; margin-bottom:.4rem; }
.rq div{ font-size:1.05rem; line-height:1.6; color:var(--text); }
.callout{ background:var(--sky); border-radius:14px; padding:1rem 1.2rem; color:var(--navy); font-size:1.05rem; line-height:1.65; }
.callout.warn{ background:#FFF4DE; color:#6B4A0B; }
.disclaimer{ background:#FDECEA; border:1px solid #F1B9B0; border-radius:14px; padding:1rem 1.3rem;
  color:#7A2B20; font-weight:600; font-size:1.05rem; line-height:1.6; }
.profile{ display:flex; gap:1rem; align-items:center; flex-wrap:wrap; }
.avatar{ width:88px; height:88px; border-radius:50%; object-fit:cover; border:3px solid var(--sky); flex:none; }
.profile .ten{ font-weight:800; font-size:1.2rem; color:var(--ink); line-height:1.3; }
.profile .lop{ color:var(--primary); font-weight:600; font-size:1.05rem; }
.profile .truong{ color:var(--muted); font-size:1rem; }
.photo{ width:100%; aspect-ratio:16/9; object-fit:cover; border-radius:14px; display:block; }
.photo-cap{ font-size:.95rem; color:var(--muted); margin:.4rem 0 0 0; }

/* ---------- Bảng HTML cỡ chữ lớn ---------- */
.tbl-wrap{ overflow-x:auto; }
table.tbl{ width:100%; border-collapse:collapse; font-size:1.02rem; }
table.tbl th{ text-align:left; background:var(--mist); color:var(--navy); font-weight:700;
  padding:.75rem .9rem; border-bottom:2px solid var(--line); white-space:nowrap; }
table.tbl td:first-child{ min-width:190px; }
table.tbl code{ font-size:.95rem; }
table.tbl td{ padding:.8rem .9rem; border-bottom:1px solid var(--line); vertical-align:top; color:var(--text); line-height:1.55; }
table.tbl tr:first-child td{ background:#F3F8FF; }
.pbar{ background:var(--line); border-radius:999px; height:10px; min-width:90px; }
.pbar span{ display:block; height:10px; border-radius:999px; background:var(--primary); }

/* ---------- Thanh bên ---------- */
[data-testid="stSidebar"]{ background:#fff; border-right:1px solid var(--line); }
[data-testid="stSidebar"] .stMarkdown p, [data-testid="stSidebar"] .stMarkdown li{ font-size:1.02rem; line-height:1.6; }
.side-card{ background:var(--mist); border-radius:14px; padding:.9rem 1rem; margin-bottom:.7rem; }
.side-card .k{ font-size:.8rem; font-weight:700; letter-spacing:.1em; text-transform:uppercase; color:var(--primary); }
.side-card .v{ font-size:1rem; color:var(--text); line-height:1.5; margin-top:.15rem; }

/* ---------- Màn hình nhỏ ---------- */
@media (max-width: 800px){
  .hero{ padding:1.6rem 1.3rem; } .hero-title{ font-size:1.6rem; } .hero-sub{ font-size:1.05rem; }
  .hero-stats{ grid-template-columns:1fr; } .flow, .rq-grid{ grid-template-columns:1fr; }
  .sec-title{ font-size:1.4rem; }
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


def dau_muc(nhan, tieu_de, mo_ta=""):
    """Đầu mỗi tab: nhãn nhỏ + tiêu đề lớn + mô tả."""
    mo = f"<div class='sec-sub'>{mo_ta}</div>" if mo_ta else ""
    st.markdown(f"<div class='eyebrow'>{nhan}</div><div class='sec-title'>{tieu_de}</div>{mo}",
                unsafe_allow_html=True)


def tieu_de_the(tieu_de, phu=""):
    """Tiêu đề trong mỗi thẻ."""
    p = f"<div class='card-sub'>{phu}</div>" if phu else ""
    st.markdown(f"<div class='card-title'>{tieu_de}</div>{p}", unsafe_allow_html=True)


def o_chi_so(nhan, gia_tri):
    """Ô chỉ số HTML: chữ dài tự xuống dòng, không bị cắt bằng dấu ba chấm."""
    st.markdown(f"<div class='kpi'><div class='nhan'>{nhan}</div><div class='tri'>{gia_tri}</div></div>",
                unsafe_allow_html=True)


def bang_html(tieu_de_cot, hang):
    """Bảng HTML cỡ chữ lớn. 'hang' là danh sách các danh sách ô; ô là chuỗi HTML đã an toàn."""
    th = "".join(f"<th>{html.escape(c)}</th>" for c in tieu_de_cot)
    tr = "".join("<tr>" + "".join(f"<td>{o}</td>" for o in h) + "</tr>" for h in hang)
    st.markdown(f"<div class='tbl-wrap'><table class='tbl'><thead><tr>{th}</tr></thead>"
                f"<tbody>{tr}</tbody></table></div>", unsafe_allow_html=True)


def ve(fig, cao=380, chu_giai_tren=False, le=None):
    """Định dạng chung cho MỌI biểu đồ Plotly: chữ lớn, nền trong suốt, bỏ thanh công cụ."""
    fig.update_layout(
        template="plotly_white", height=cao,
        margin=le or dict(l=8, r=8, t=24, b=8),
        font=dict(family="Be Vietnam Pro, Segoe UI, Arial, sans-serif", size=15, color="#24324B"),
        legend=dict(orientation="h", font=dict(size=14), traceorder="normal",
                    **(dict(yanchor="bottom", y=1.02, x=0) if chu_giai_tren
                       else dict(yanchor="top", y=-0.18, x=0))),
        hoverlabel=dict(font_size=14), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_xaxes(tickfont=dict(size=14), title_font=dict(size=14), gridcolor=LINE, zeroline=False)
    fig.update_yaxes(tickfont=dict(size=14), title_font=dict(size=14), gridcolor=LINE, zeroline=False)
    phien_ban = tuple(int(x) for x in st.__version__.split(".")[:2])
    if phien_ban >= (1, 50):
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
    else:
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def ngat(nhan, toi_da=11):
    """Ngắt nhãn dài thành 2 dòng (thẻ <br>) để nhãn trục không bị xoay chéo."""
    if len(nhan) <= toi_da or " " not in nhan:
        return nhan
    cac_tu = nhan.split(" ")
    tot_nhat = min(range(1, len(cac_tu)), key=lambda i: abs(len(" ".join(cac_tu[:i])) - len(" ".join(cac_tu[i:]))))
    return " ".join(cac_tu[:tot_nhat]) + "<br>" + " ".join(cac_tu[tot_nhat:])


def hien_anh(nguon, chu_thich=""):
    """Ảnh bo góc tỉ lệ 16:9; bỏ qua nếu tệp cục bộ không tồn tại."""
    uri = nguon_anh(nguon)
    if not uri:
        return
    ct = f"<p class='photo-cap'>{html.escape(chu_thich)}</p>" if chu_thich else ""
    st.markdown(f"<img class='photo' src='{uri}' referrerpolicy='no-referrer' alt=''>{ct}",
                unsafe_allow_html=True)


# =============================================================================
# PHẦN 2. DỮ LIỆU (đọc processed_data.csv; không có thì sinh giả lập)
# =============================================================================
@st.cache_data
def tao_du_lieu_gia_lap(n: int = 36, seed: int = 2026) -> pd.DataFrame:
    """Sinh dữ liệu giả lập (mỗi dòng = 1 hộ). Dùng khi không có processed_data.csv."""
    rng = np.random.default_rng(seed)
    df = pd.DataFrame({"ma_phieu": [f"H{i:03d}" for i in range(1, n + 1)]})
    df["khoang_cach"] = rng.choice(KHOANG_CACH, size=n, p=[.22, .33, .25, .12, .08])
    idx_kc = df["khoang_cach"].map(KHOANG_CACH.index).to_numpy()
    df["nha_o_truoc"] = rng.choice(NHA_O, size=n, p=[.50, .10, .25, .10, .05])
    ma_tran = {"Sở hữu, không vay": [.45, .30, .10, .10, .05], "Sở hữu, có vay": [.15, .55, .15, .10, .05],
               "Thuê": [.02, .08, .75, .10, .05], "Ở cùng người thân": [.05, .10, .20, .60, .05],
               "Tạm thời/khác": [.05, .10, .35, .20, .30]}
    df["nha_o_sau"] = [rng.choice(NHA_O, p=ma_tran[t]) for t in df["nha_o_truoc"]]
    p_giu = np.array([.90, .70, .40, .20, .10])[idx_kc]
    u = rng.random(n)
    df["giu_truong"] = ["Giữ tất cả" if x < p else ("Một số chuyển" if x < p + (1 - p) * .4 else "Tất cả chuyển")
                        for p, x in zip(p_giu, u)]
    dich = [-1, 0, 1, 2]
    p_dich = {0: [.10, .55, .30, .05], 1: [.10, .35, .40, .15], 2: [.10, .20, .40, .30],
              3: [.10, .10, .40, .40], 4: [.10, .10, .30, .50]}

    def dich_nhom(i0, k, nho_nhat):
        return int(np.clip(i0 + rng.choice(dich, p=p_dich[k]), nho_nhat, 4))

    hoc0 = rng.choice(5, size=n, p=[.25, .35, .22, .13, .05])
    lam0 = rng.choice(5, size=n, p=[.08, .30, .30, .22, .10])
    hoc1 = [dich_nhom(a, k, 0) for a, k in zip(hoc0, idx_kc)]
    lam1 = [0 if a == 0 else dich_nhom(a, k, 1) for a, k in zip(lam0, idx_kc)]
    df["tg_hoc_truoc"] = [TG_DI_HOC[i] for i in hoc0]
    df["tg_hoc_sau"] = [TG_DI_HOC[i] for i in hoc1]
    df["tg_lam_truoc"] = [TG_DI_LAM[i] for i in lam0]
    df["tg_lam_sau"] = [TG_DI_LAM[i] for i in lam1]

    def doi(a, b, kxd=False):
        return "Không xác định" if kxd else ("Tăng" if b > a else ("Giảm" if b < a else "Không đổi"))

    df["doi_tg_hoc"] = [doi(a, b) for a, b in zip(hoc0, hoc1)]
    df["doi_tg_lam"] = [doi(a, b, a == 0) for a, b in zip(lam0, lam1)]
    for ten, tb in zip(YEU_TO, [4.2, 3.8, 3.6, 3.2]):
        df[COT_QT[ten]] = np.clip(np.round(rng.normal(tb, 1.0, n)), 1, 5).astype(int)
    df["kha_nang_tai_chinh"] = np.clip(np.round(rng.normal(3.0, 1.1, n)), 1, 5).astype(int)
    df["so_phuong_an"] = rng.integers(1, 7, size=n)
    df["hai_long"] = np.clip(np.round(rng.normal(3.6 - .25 * idx_kc, .9)), 1, 5).astype(int)
    return df


@st.cache_data
def nap_du_lieu() -> pd.DataFrame:
    """Đọc CSV (nếu có), chuẩn hóa tên cột; lỗi đọc thì dùng dữ liệu giả lập."""
    if os.path.exists(FILE_DU_LIEU):
        try:
            d = pd.read_csv(FILE_DU_LIEU, encoding="utf-8-sig").rename(columns=TEN_COT_CU)
            if len(d) > 0:
                return d
        except Exception:
            pass
    return tao_du_lieu_gia_lap()


def them_cot_phan_nhom(d):
    """Tạo các cột phân nhóm dùng cho bộ lọc (nếu cột gốc tồn tại)."""
    d = d.copy()
    if "kha_nang_tai_chinh" in d:
        d["nhom_tai_chinh"] = pd.cut(d["kha_nang_tai_chinh"], bins=[0, 2, 3, 5],
                                     labels=NHOM_TAI_CHINH).astype(str)
    if "tg_lam_truoc" in d:
        d["nhom_di_lam"] = np.where(d["tg_lam_truoc"] == "Không thường xuyên",
                                    NHOM_DI_LAM[1], NHOM_DI_LAM[0])
    if COT_QT["Ưu tiên giữ trường"] in d:
        d["nhom_uu_tien_truong"] = np.where(d[COT_QT["Ưu tiên giữ trường"]] >= 4,
                                            "Ưu tiên giữ trường cao (4–5)", "Thấp/trung bình (1–3)")
    return d


def co_cot(d, cac_cot):
    """Kiểm tra dữ liệu có đủ các cột cần cho một biểu đồ hay không."""
    return all(c in d.columns for c in cac_cot)


df_goc = nap_du_lieu()
CAC_COT_GOC = list(df_goc.columns)
df = them_cot_phan_nhom(df_goc)


def ti_le(d, cot, gia_tri):
    """% hộ có d[cot] == gia_tri (NaN nếu thiếu cột hoặc rỗng)."""
    return (d[cot] == gia_tri).mean() * 100 if co_cot(d, [cot]) and len(d) else np.nan


# =============================================================================
# PHẦN 3. THANH BÊN + BANNER
# =============================================================================
with st.sidebar:
    av = anh_data_uri(ANH_TAC_GIA)
    if av:
        st.markdown(f"<div style='text-align:center'><img class='avatar' style='width:130px;height:130px' "
                    f"src='{av}' alt=''></div>", unsafe_allow_html=True)
    st.markdown(
        "<div style='text-align:center;margin:.6rem 0 1rem 0'>"
        "<div style='font-weight:800;font-size:1.3rem;color:#0E1B33'>NGUYỄN VŨ TUẤN MINH</div>"
        "<div style='color:#1F5FD1;font-weight:700;font-size:1.08rem'>Lớp 12 Chuyên Tin 1</div>"
        "<div style='color:#5F6E85;font-size:1rem'>THPT chuyên Hà Nội – Amsterdam</div></div>"
        "<div class='side-card'><div class='k'>Đề tài</div><div class='v'>Lựa chọn nơi ở sau di dời của hộ gia đình "
        "có con học phổ thông</div></div>"
        "<div class='side-card'><div class='k'>Địa bàn</div><div class='v'>Đoạn Ngụy Như Kon Tum – Nhân Hòa – "
        "Nguyễn Trãi, Hà Nội</div></div>"
        "<div class='side-card'><div class='k'>Thời gian thực hiện</div><div class='v'>09/2026 – 12/2026</div></div>",
        unsafe_allow_html=True)

# Nền banner: ảnh + lớp gradient tối nằm CÙNG một thuộc tính background => chữ luôn đọc được
uri_banner = anh_data_uri(ANH_BANNER)
nen_banner = (f"linear-gradient(100deg,rgba(8,26,56,.94) 0%,rgba(11,47,99,.84) 48%,rgba(11,47,99,.40) 100%),"
              f"url('{uri_banner}')") if uri_banner else "linear-gradient(120deg,#0B2F63 0%,#1F5FD1 100%)"

so_phieu = len(df)
ty_le_giu_tb = ti_le(df, "giu_truong", "Giữ tất cả")
gia_tri_hai_long = df["hai_long"].mean() if co_cot(df, ["hai_long"]) else np.nan
chip_gia_lap = "<span class='chip warn'>DỮ LIỆU GIẢ LẬP – MINH HỌA</span>" if DU_LIEU_GIA_LAP else ""

st.markdown(
    f"""
    <div class="hero" style="background-image:{nen_banner}">
      <div class="hero-eyebrow">Nghiên cứu khoa học · Học sinh phổ thông</div>
      <div class="hero-title">Lựa chọn nơi ở sau di dời của hộ gia đình có con đang học phổ thông</div>
      <div class="hero-sub">Khảo sát cấu trúc đánh đổi tại dự án Vành đai 2.5, đoạn Ngụy Như Kon Tum – Nhân Hòa – Nguyễn Trãi.</div>
      <div class="chips">
        <span class="chip">Hà Nội · 09–12/2026</span>
        <span class="chip">Nghiên cứu cắt ngang hồi cứu</span>
        <span class="chip">Dữ liệu ẩn danh</span>{chip_gia_lap}
      </div>
      <div class="hero-stats">
        <div class="hero-stat"><div class="n">{so_phieu}</div><div class="l">Phiếu khảo sát</div></div>
        <div class="hero-stat"><div class="n">{'—' if np.isnan(ty_le_giu_tb) else f'{ty_le_giu_tb:.0f}%'}</div><div class="l">Hộ giữ trường cho tất cả con</div></div>
        <div class="hero-stat"><div class="n">{'—' if np.isnan(gia_tri_hai_long) else f'{gia_tri_hai_long:.1f}/5'}</div><div class="l">Mức hài lòng trung bình</div></div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "1 · Tổng quan", "2 · Kết quả khảo sát", "3 · Công cụ quyết định",
    "4 · Tư liệu thực địa", "5 · Tài liệu mở",
])

# =============================================================================
# TAB 1. TỔNG QUAN & BỐI CẢNH
# =============================================================================
with tab1:
    dau_muc("Tổng quan", "Một câu hỏi thực tế dưới góc nhìn của học sinh lớp 12",
            "Từ sự tò mò về một quyết định rất đời thường của các gia đình sau di dời.")

    c1, c2 = st.columns([7, 5], gap="large")
    with c1:
        with st.container(key="card_gioi_thieu"):
            tieu_de_the("Vì sao có nghiên cứu này?")
            st.markdown(
                "<div class='txt'>Đề tài do <b>Nguyễn Vũ Tuấn Minh</b>, học sinh lớp 12 Tin 1 (chuyên Tin), "
                "Trường THPT chuyên Hà Nội – Amsterdam thực hiện, xuất phát từ câu hỏi: <i>sau khi phải di dời để "
                "phục vụ dự án Vành đai 2.5, đoạn Ngụy Như Kon Tum – Nhân Hòa – Nguyễn Trãi, các gia đình đã "
                "chuyển đến đâu và điều gì khiến họ lựa chọn nơi ở đó?</i></div>"
                "<div class='txt'>Tại thời điểm nghiên cứu (tháng 9/2026), việc giải phóng mặt bằng đã hoàn tất và "
                "các hộ bị ảnh hưởng đã di dời. Vì quyết định đã xảy ra, khảo sát tìm hiểu lại những căn cứ đã được "
                "cân nhắc: <b>khả năng tài chính, trường học của con, thời gian đi làm, sự hỗ trợ của người thân</b> "
                "và mức độ ổn định của nơi ở mới.</div>", unsafe_allow_html=True)
            st.markdown("<div class='callout warn' style='margin-top:1rem'>Thông tin hoàn tất giải phóng mặt bằng "
                        "cần được bổ sung nguồn chính thức hoặc xác nhận kiểm chứng được trước khi nộp đề tài.</div>",
                        unsafe_allow_html=True)
    with c2:
        with st.container(key="card_tac_gia"):
            tieu_de_the("Tác giả & nhóm nghiên cứu")
            av2 = anh_data_uri(ANH_TAC_GIA)
            hinh = f"<img class='avatar' src='{av2}' alt=''>" if av2 else ""
            st.markdown(f"<div class='profile'>{hinh}<div><div class='ten'>Nguyễn Vũ Tuấn Minh</div>"
                        "<div class='lop'>Lớp 12 Tin 1 (chuyên Tin)</div>"
                        "<div class='truong'>THPT chuyên Hà Nội – Amsterdam</div></div></div>",
                        unsafe_allow_html=True)
            st.write("")
            hien_anh(ANH_NHOM, "Nhóm nghiên cứu cùng giáo viên hướng dẫn")

    st.write("")
    with st.container(key="card_cau_hoi"):
        tieu_de_the("Bốn câu hỏi nghiên cứu", "Mỗi câu hỏi có một nhóm biểu đồ tương ứng ở tab Kết quả khảo sát")
        st.markdown(
            "<div class='rq-grid'>"
            "<div class='rq'><b>RQ1</b><div>Hộ chuyển đến đâu, dùng hình thức nhà ở nào và đã xem xét bao nhiêu phương án?</div></div>"
            "<div class='rq'><b>RQ2</b><div>Trường học, thời gian đi học – đi làm và hỗ trợ từ người thân thay đổi thế nào?</div></div>"
            "<div class='rq'><b>RQ3</b><div>Tại thời điểm chọn nơi ở, hộ ưu tiên, bị giới hạn và chấp nhận đánh đổi những gì?</div></div>"
            "<div class='rq'><b>RQ4</b><div>Tài chính, ưu tiên giữ trường và ưu tiên thời gian đi làm liên hệ ra sao với ba kết quả tương ứng?</div></div>"
            "</div>", unsafe_allow_html=True)

    st.write("")
    with st.container(key="card_khung"):
        tieu_de_the("Khung khái niệm", "Điều kiện → Quá trình → Lựa chọn → Đánh giá sau di dời")
        st.markdown(
            "<div class='flow'>"
            "<div class='step'><div class='so'>1</div><div class='tt'>Điều kiện</div><div class='nd'>Tài chính, con đang học, nơi làm việc, hỗ trợ từ người thân tại thời điểm chốt nơi ở.</div></div>"
            "<div class='step'><div class='so'>2</div><div class='tt'>Quá trình</div><div class='nd'>Số phương án cân nhắc, thời gian tìm, yếu tố ưu tiên và ràng buộc loại phương án.</div></div>"
            "<div class='step'><div class='so'>3</div><div class='tt'>Lựa chọn</div><div class='nd'>Khoảng cách nơi ở mới, hình thức nhà ở, giữ hay đổi trường.</div></div>"
            "<div class='step'><div class='so'>4</div><div class='tt'>Đánh giá sau di dời</div><div class='nd'>Thay đổi thời gian đi học – đi làm, hỗ trợ gia đình, mức hài lòng.</div></div>"
            "</div>", unsafe_allow_html=True)
        st.caption("Nghiên cứu đo mối liên hệ giữa các nhóm thông tin; không xác nhận quan hệ nhân quả "
                   "và không suy rộng cho toàn bộ hộ bị ảnh hưởng.")

    st.write("")
    with st.container(key="card_cam_on"):
        tieu_de_the("Lời cảm ơn & cam kết")
        l1, l2 = st.columns([3, 2], gap="large")
        with l1:
            st.markdown(
                "<div class='txt'><b>Kính gửi cô/chú, anh/chị tham gia khảo sát,</b></div>"
                "<div class='txt'>Con là <b>Nguyễn Vũ Tuấn Minh</b>, học sinh lớp 12 Tin 1 (chuyên Tin), Trường THPT chuyên "
                "Hà Nội – Amsterdam. Từ sự tò mò trước một vấn đề thực tế của cuộc sống, con bắt đầu nghiên cứu này với mong "
                "muốn hiểu rõ hơn cách mỗi gia đình đưa ra quyết định về nơi ở sau di dời.</div>"
                "<div class='txt'>Con chân thành cảm ơn cô/chú, anh/chị đã dành thời gian chia sẻ trải nghiệm và những cân nhắc "
                "của gia đình. Mỗi phản hồi đều rất quý giá, giúp con nhìn vấn đề đầy đủ hơn từ những lựa chọn có thật.</div>"
                "<div class='txt' style='text-align:right;font-weight:700;color:#1F5FD1'>Trân trọng — Nguyễn Vũ Tuấn Minh, lớp 12 Tin 1</div>",
                unsafe_allow_html=True)
        with l2:
            st.markdown(
                "<div class='callout'><b>Cam kết</b><br>Thông tin và kết quả tổng hợp chỉ dùng cho đề tài nghiên cứu khoa học; "
                "không dùng cho mục đích thương mại và không dùng để đánh giá đúng – sai quyết định của bất kỳ gia đình nào. "
                "Dữ liệu được thu thập ẩn danh. Việc tham gia hoàn toàn tự nguyện, có thể dừng bất cứ lúc nào.</div>"
                "<div class='txt' style='margin-top:1rem'><b>Lời tri ân.</b> Con xin biết ơn sâu sắc <b>cô Lê Thị Thúy</b> — giáo viên "
                "Tin học, đồng thời là giáo viên chủ nhiệm của con trong hai năm lớp 11 và 12 — người đã trực tiếp hướng dẫn "
                "và đồng hành cùng con; và cảm ơn các bạn học sinh đã hỗ trợ con trong quá trình khảo sát thực tế.</div>",
                unsafe_allow_html=True)

# =============================================================================
# TAB 2. DASHBOARD KẾT QUẢ KHẢO SÁT + BỘ LỌC
# =============================================================================
BO_LOC = [  # (khóa trạng thái, nhãn, cột dữ liệu, danh sách lựa chọn)
    ("loc_kc", "Khoảng cách nơi ở mới", "khoang_cach", KHOANG_CACH),
    ("loc_giu", "Kết quả giữ trường", "giu_truong", GIU_TRUONG),
    ("loc_nha", "Nhà ở trước di dời", "nha_o_truoc", NHA_O),
    ("loc_tc", "Nguồn lực tài chính", "nhom_tai_chinh", NHOM_TAI_CHINH),
    ("loc_lam", "Hành trình đi làm", "nhom_di_lam", NHOM_DI_LAM),
]


def dat_lai_bo_loc():
    """Nút 'Đặt lại': xóa mọi lựa chọn = xem toàn bộ mẫu."""
    for khoa, *_ in BO_LOC:
        st.session_state[khoa] = []


def chi_so_tong_hop(d):
    """%giữ trường, %tăng thời gian đi làm, hài lòng trung vị, số hộ có đi làm thường xuyên."""
    giu = ti_le(d, "giu_truong", "Giữ tất cả")
    if co_cot(d, ["doi_tg_lam"]):
        co_lam = d[d["doi_tg_lam"] != "Không xác định"]
        tang = (co_lam["doi_tg_lam"] == "Tăng").mean() * 100 if len(co_lam) else np.nan
    else:
        co_lam, tang = d.iloc[0:0], np.nan
    hl = d["hai_long"].median() if co_cot(d, ["hai_long"]) else np.nan
    return giu, tang, hl, len(co_lam)


def thieu_du_lieu(ten):
    st.info(f"Chưa có đủ cột dữ liệu để vẽ biểu đồ «{ten}». Hãy kiểm tra tệp {FILE_DU_LIEU}.")


@st.fragment   # chỉ chạy lại phần này khi đổi bộ lọc -> mượt hơn
def khung_dashboard(du_lieu):
    dau_muc("Kết quả khảo sát", "Bức tranh chung từ các phiếu khảo sát",
            "Dùng bộ lọc để xem riêng từng nhóm hộ; mọi chỉ số và biểu đồ đổi theo ngay.")

    bo_loc = [b for b in BO_LOC if b[2] in du_lieu.columns]
    with st.container(key="card_loc"):
        tieu_de_the("Bộ lọc theo nhóm đối tượng", "Để trống = xem tất cả · chọn nhiều nhóm để gộp lại")
        o = st.columns(3, gap="medium") + st.columns(3, gap="medium")
        for (khoa, nhan, _cot, lua_chon), cot_ui in zip(bo_loc, o):
            with cot_ui:
                st.multiselect(nhan, lua_chon, key=khoa, placeholder="Tất cả")
        with o[len(bo_loc)] if len(bo_loc) < len(o) else st.container():
            st.write("")
            st.button("Đặt lại bộ lọc", on_click=dat_lai_bo_loc)

    mat_na = pd.Series(True, index=du_lieu.index)
    for khoa, _n, cot, _lc in bo_loc:
        chon = st.session_state.get(khoa, [])
        if chon:
            mat_na &= du_lieu[cot].isin(chon)
    d = du_lieu[mat_na]
    dang_loc = len(d) < len(du_lieu)

    if len(d) == 0:
        st.warning("Không có hộ nào thỏa mãn tổ hợp bộ lọc này. Hãy bỏ bớt điều kiện lọc.")
        return
    if len(d) < 5:
        st.error(f"Đang xem {len(d)}/{len(du_lieu)} phiếu. Nhóm dưới 5 phiếu: theo quy tắc của đề cương "
                 "chỉ mô tả số lượng, không diễn giải tỷ lệ hay so sánh.")
    elif len(d) < 10:
        st.info(f"Đang xem {len(d)}/{len(du_lieu)} phiếu. Nhóm nhỏ (dưới 10 phiếu): tỷ lệ dao động mạnh, chỉ nên xem như mô tả.")
    else:
        st.caption(f"Đang xem {len(d)}/{len(du_lieu)} phiếu.")

    # ---- Ô chỉ số (kèm chênh lệch so với toàn mẫu khi đang lọc)
    giu, tang, hl, n_lam = chi_so_tong_hop(d)
    giu0, tang0, hl0, _ = chi_so_tong_hop(du_lieu)

    def chenh(x, x0):
        if not dang_loc or np.isnan(x) or np.isnan(x0):
            return None
        return f"{x - x0:+.0f} điểm % so với toàn mẫu"

    m1, m2, m3, m4 = st.columns(4, gap="medium")
    m1.metric("Số phiếu đang xem", f"{len(d)}")
    m2.metric("Giữ trường (mọi con)", "—" if np.isnan(giu) else f"{giu:.0f}%", chenh(giu, giu0), delta_color="off")
    m3.metric("Đi làm mất thêm giờ", "—" if np.isnan(tang) else f"{tang:.0f}%", chenh(tang, tang0),
              delta_color="off", help=f"Tính trên {n_lam} hộ có hành trình đi làm thường xuyên.")
    m4.metric("Hài lòng trung vị (1–5)", "—" if np.isnan(hl) else f"{hl:.1f}",
              None if (not dang_loc or np.isnan(hl) or np.isnan(hl0)) else f"{hl - hl0:+.1f} so với toàn mẫu",
              delta_color="off")
    st.write("")

    # ---- Hàng 1: khoảng cách | nhà ở trước-sau
    a, b = st.columns(2, gap="large")
    with a:
        with st.container(key="card_bd1"):
            tieu_de_the("1. Khoảng cách từ nơi ở mới đến nơi ở cũ", "RQ1 · số hộ theo nhóm khoảng cách")
            if not co_cot(d, ["khoang_cach"]):
                thieu_du_lieu("khoảng cách")
            else:
                dem = d["khoang_cach"].value_counts().reindex(KHOANG_CACH).fillna(0).astype(int)
                tong = max(int(dem.sum()), 1)
                mau = [PRIMARY if v == dem.max() else SKY for v in dem.values]
                fig = go.Figure(go.Bar(x=NHAN_KC, y=dem.values, marker_color=mau,
                                       text=[f"<b>{v}</b><br>({v / tong * 100:.0f}%)" for v in dem.values],
                                       textposition="outside", textfont=dict(size=15), cliponaxis=False))
                fig.update_layout(yaxis_title="Số hộ", yaxis_range=[0, max(dem.max(), 1) * 1.35])
                fig.update_xaxes(tickangle=0)
                ve(fig, 360)
                top = dem.idxmax()
                st.markdown(f"<div class='takeaway'>Nhóm phổ biến nhất: <b>{top}</b> ({dem.max()} hộ, "
                            f"{dem.max() / tong * 100:.0f}%). Khoảng cách do người trả lời ước tính.</div>",
                            unsafe_allow_html=True)
    with b:
        with st.container(key="card_bd2"):
            tieu_de_the("2. Hình thức nhà ở trước và sau di dời", "RQ1 · so sánh hoặc xem bảng chuyển đổi")
            if not co_cot(d, ["nha_o_truoc", "nha_o_sau"]):
                thieu_du_lieu("hình thức nhà ở")
            else:
                che_do = st.radio("Cách xem", ["So sánh trước – sau", "Bảng chuyển đổi"],
                                  horizontal=True, key="cd_nha", label_visibility="collapsed")
                if che_do == "So sánh trước – sau":
                    tr = d["nha_o_truoc"].value_counts().reindex(NHA_O).fillna(0)
                    sa = d["nha_o_sau"].value_counts().reindex(NHA_O).fillna(0)
                    fig = go.Figure()
                    nhan_x = NHAN_NHA
                    fig.add_bar(x=nhan_x, y=tr.values, name="Trước di dời", marker_color=SKY,
                                text=tr.values.astype(int), textposition="outside", cliponaxis=False)
                    fig.add_bar(x=nhan_x, y=sa.values, name="Sau di dời", marker_color=PRIMARY,
                                text=sa.values.astype(int), textposition="outside", cliponaxis=False)
                    fig.update_layout(barmode="group", yaxis_title="Số hộ",
                                      yaxis_range=[0, max(tr.max(), sa.max(), 1) * 1.3])
                    fig.update_xaxes(tickangle=0)
                    ve(fig, 330, chu_giai_tren=True)
                else:
                    ch = pd.crosstab(d["nha_o_truoc"], d["nha_o_sau"]).reindex(
                        index=NHA_O, columns=NHA_O, fill_value=0)
                    fig = px.imshow(ch.values, x=NHA_O, y=NHA_O, text_auto=True, aspect="auto",
                                    color_continuous_scale=["#FFFFFF", PRIMARY])
                    fig.update_layout(coloraxis_showscale=False)
                    fig.update_xaxes(tickangle=-25, title="Sau di dời")
                    fig.update_yaxes(title="Trước di dời")
                    ve(fig, 330)
                st.caption("Dòng của bảng chuyển đổi = hình thức trước, cột = hình thức sau.")

    st.write("")
    # ---- Hàng 2: phân bố thời gian | tỷ lệ tăng/giảm
    a, b = st.columns(2, gap="large")
    with a:
        with st.container(key="card_bd3"):
            tieu_de_the("3. Thời gian di chuyển một chiều trước và sau", "RQ2 · số hộ theo nhóm thời gian")
            lc = st.radio("Xem theo", ["Đi học của con", "Đi làm của phụ huynh"], horizontal=True,
                          key="xem_di_lai", label_visibility="collapsed")
            hoc = lc == "Đi học của con"
            c_tr, c_sa, thu_tu = (("tg_hoc_truoc", "tg_hoc_sau", TG_DI_HOC) if hoc
                                  else ("tg_lam_truoc", "tg_lam_sau", TG_DI_LAM))
            if not co_cot(d, [c_tr, c_sa]):
                thieu_du_lieu("thời gian di chuyển")
            else:
                x0 = d[c_tr].value_counts().reindex(thu_tu).fillna(0)
                x1 = d[c_sa].value_counts().reindex(thu_tu).fillna(0)
                fig = go.Figure()
                nhan_x = [ngat(k, 9) for k in thu_tu]
                fig.add_bar(x=nhan_x, y=x0.values, name="Trước di dời", marker_color=SKY)
                fig.add_bar(x=nhan_x, y=x1.values, name="Sau di dời", marker_color=PRIMARY)
                fig.update_layout(barmode="group", yaxis_title="Số hộ")
                fig.update_xaxes(tickangle=0)
                ve(fig, 330, chu_giai_tren=True)
    with b:
        with st.container(key="card_bd4"):
            tieu_de_the("4. Tỷ lệ hộ tăng – giảm thời gian đi lại", "RQ2 · so sánh nhóm thời gian sau với trước")
            if not co_cot(d, ["doi_tg_hoc", "doi_tg_lam"]):
                thieu_du_lieu("thay đổi thời gian đi lại")
            else:
                hang, ket_qua = [], {}
                for ten, cot in [("Đi học của con", "doi_tg_hoc"), ("Đi làm của phụ huynh", "doi_tg_lam")]:
                    xd = d[d[cot] != "Không xác định"][cot]
                    dem = xd.value_counts().reindex(["Giảm", "Không đổi", "Tăng"]).fillna(0)
                    hang.append(f"{ten} · n={int(dem.sum())}")
                    ket_qua[ten] = dem / dem.sum() * 100 if dem.sum() else dem
                fig = go.Figure()
                for nhom, mau in [("Giảm", TEAL), ("Không đổi", GREY), ("Tăng", CORAL)]:
                    gt = [ket_qua[t][nhom] for t in ket_qua]
                    fig.add_bar(y=hang, x=gt, name=nhom, orientation="h", marker_color=mau,
                                text=[f"{v:.0f}%" if v >= 8 else "" for v in gt], textposition="inside",
                                textfont=dict(size=15, color="#0E1B33" if nhom == "Không đổi" else "#fff"))
                fig.update_layout(barmode="stack", xaxis_range=[0, 100], xaxis_title="% hộ")
                ve(fig, 330, chu_giai_tren=True)
                st.caption("Hộ không đi làm thường xuyên không được tính ở dòng «Đi làm».")

    st.write("")
    # ---- Hàng 3: mức quan trọng | giữ trường theo ưu tiên
    a, b = st.columns(2, gap="large")
    with a:
        with st.container(key="card_bd5"):
            tieu_de_the("5. Mức quan trọng của các yếu tố khi chọn nơi ở", "RQ3 · điểm trung bình, thang 1–5")
            cac = [t for t in YEU_TO if COT_QT[t] in d.columns]
            if not cac:
                thieu_du_lieu("mức quan trọng")
            else:
                tb = pd.DataFrame({"y": cac, "v": [d[COT_QT[t]].mean() for t in cac]}).sort_values("v")
                mau = [PRIMARY if v == tb["v"].max() else SKY for v in tb["v"]]
                fig = go.Figure(go.Bar(x=tb["v"], y=tb["y"], orientation="h", marker_color=mau,
                                       text=tb["v"].round(2), textposition="outside", textfont=dict(size=15),
                                       cliponaxis=False))
                fig.update_layout(xaxis_range=[0, 5.7], xaxis_title="Điểm trung bình (1–5)")
                ve(fig, 320)
                st.markdown(f"<div class='takeaway'>Yếu tố được chấm cao nhất: <b>{tb.iloc[-1]['y']}</b> "
                            f"({tb.iloc[-1]['v']:.2f}/5).</div>", unsafe_allow_html=True)
    with b:
        with st.container(key="card_bd6"):
            tieu_de_the("6. Kết quả giữ trường theo mức ưu tiên giữ trường", "Mô tả khám phá cho giả thuyết H2")
            if not co_cot(d, ["nhom_uu_tien_truong", "giu_truong"]):
                thieu_du_lieu("giữ trường theo ưu tiên")
            else:
                nh = pd.crosstab(d["nhom_uu_tien_truong"], d["giu_truong"]).reindex(columns=GIU_TRUONG, fill_value=0)
                pc = nh.div(nh.sum(axis=1), axis=0) * 100
                nhan_y = [f"{k} · n={int(nh.loc[k].sum())}" for k in pc.index]
                fig = go.Figure()
                for cot, mau in zip(GIU_TRUONG, [PRIMARY, SKY, GREY]):
                    fig.add_bar(y=nhan_y, x=pc[cot].values, name=cot, orientation="h", marker_color=mau,
                                text=[f"{v:.0f}%" if v >= 8 else "" for v in pc[cot].values],
                                textposition="inside",
                                textfont=dict(size=15, color="#fff" if cot == "Giữ tất cả" else "#0E1B33"))
                fig.update_layout(barmode="stack", xaxis_range=[0, 100], xaxis_title="% hộ")
                ve(fig, 320, chu_giai_tren=True)
                st.caption("Chỉ mô tả, không suy ra nhân quả. Nhóm dưới 5 hộ không diễn giải.")

    with st.expander("Xem và tải bảng dữ liệu đang lọc (đã ẩn danh)"):
        bang = d[[c for c in CAC_COT_GOC if c in d.columns]]
        st.dataframe(bang, hide_index=True)
        st.download_button("Tải dữ liệu đang lọc (CSV)", bang.to_csv(index=False).encode("utf-8-sig"),
                           file_name="du_lieu_dang_loc.csv", mime="text/csv")


with tab2:
    khung_dashboard(df)

# =============================================================================
# TAB 3. CÔNG CỤ QUYẾT ĐỊNH (THỜI GIAN THỰC) + GÓC TÀI CHÍNH
# =============================================================================
# 5 phương án giả lập. Điểm 1–5 theo thứ tự YEU_TO: [tài chính, giữ trường, đi làm, người thân].
# Điểm càng cao = phương án càng "dễ đáp ứng" yếu tố đó. Đây là GIẢ ĐỊNH MINH HỌA của nhóm nghiên cứu.
PHUONG_AN = [
    {"ten": "A. Thuê nhà gần khu cũ (dưới 3 km)", "ngan": "A. Thuê gần khu cũ", "diem": [2, 5, 4, 3],
     "duoc": "Giữ trường cũ, đi làm thuận tiện", "doi": "Tiền thuê cao, không gian nhỏ, chưa có tài sản sở hữu"},
    {"ten": "B. Mua nhà có vay (3–7 km)", "ngan": "B. Mua nhà có vay", "diem": [2, 4, 3, 3],
     "duoc": "Có nhà sở hữu, vẫn tương đối gần trường", "doi": "Gánh nặng trả nợ dài hạn, thời gian di chuyển tăng nhẹ"},
    {"ten": "C. Nhà sở hữu giá mềm (7–15 km)", "ngan": "C. Nhà giá mềm xa hơn", "diem": [4, 2, 2, 3],
     "duoc": "Chi phí nhà ở thấp hơn, diện tích lớn hơn", "doi": "Nhiều khả năng phải đổi trường, đi làm xa hơn"},
    {"ten": "D. Ở cùng/gần người thân", "ngan": "D. Ở cùng người thân", "diem": [5, 2, 3, 5],
     "duoc": "Tiết kiệm chi phí, có người đưa đón, trông nom con",
     "doi": "Ít riêng tư, sinh hoạt chung; nhà người thân thường không cùng khu trường cũ"},
    {"ten": "E. Ngoài Hà Nội / vùng xa", "ngan": "E. Ngoài Hà Nội", "diem": [5, 1, 1, 2],
     "duoc": "Chi phí nhà ở thấp nhất, quỹ đất rộng",
     "doi": "Gần như chắc chắn đổi trường, đi làm rất xa, xa mạng lưới hỗ trợ"},
]
KHOA_W = {"Khả năng tài chính": "w_tc", "Ưu tiên giữ trường": "w_tr",
          "Giới hạn thời gian đi làm": "w_dl", "Hỗ trợ từ người thân": "w_ht"}
MAC_DINH_W = [4, 4, 3, 3]
KICH_BAN_MAU = [("Giữ trường + ngân sách", [5, 5, 3, 2]), ("Đi làm gần + ngân sách", [5, 2, 5, 2]),
                ("Cần người thân", [4, 3, 3, 5]), ("Đặt lại", MAC_DINH_W)]
for _k, _v in zip(KHOA_W.values(), MAC_DINH_W):
    st.session_state.setdefault(_k, _v)


def ap_kich_ban(gia_tri):
    """Gán mức ưu tiên của một kịch bản mẫu vào 4 thanh trượt."""
    for khoa, v in zip(KHOA_W.values(), gia_tri):
        st.session_state[khoa] = v


def tinh_phuong_an(w):
    """Mức khớp (%) = Σ(mức quan trọng × điểm phương án) ÷ (5 × Σ mức quan trọng) × 100.
    'dong_gop' là phần điểm do từng yếu tố tạo ra (cộng lại = mức khớp)."""
    tong = sum(w)
    ds = []
    for pa in PHUONG_AN:
        dong_gop = [wi * si / (5 * tong) * 100 for wi, si in zip(w, pa["diem"])]
        xung_dot = [YEU_TO[i] for i in range(4) if w[i] >= 4 and pa["diem"][i] <= 2]
        ds.append({**pa, "dong_gop": dong_gop, "khop": sum(dong_gop), "xung_dot": xung_dot})
    return sorted(ds, key=lambda x: x["khop"], reverse=True)


def goi_y_danh_doi(w):
    """Quy tắc 'nếu – thì' về đánh đổi thường gặp. w = [tài chính, giữ trường, đi làm, người thân]."""
    tc, tr, dl, ht = w
    ds = []
    if tr >= 4 and tc >= 4:
        ds.append("<b>Giữ trường + ngân sách hạn chế</b> → xu hướng thuê nhà trọ/nhà nhỏ gần trường, hoặc chấp nhận "
                  "tăng thời gian di chuyển của người lớn.")
    if tr >= 4 and tc <= 2:
        ds.append("<b>Giữ trường + tài chính thoải mái</b> → có thể chọn nhà gần trường (thuê hoặc vay), đánh đổi là "
                  "chi phí nhà ở/nợ cao hơn.")
    if dl >= 4 and tr >= 4:
        ds.append("<b>Vừa gần trường vừa gần nơi làm</b> → vùng lựa chọn rất hẹp, giá thuê/mua cao, ít phương án.")
    if dl >= 4 and tc >= 4:
        ds.append("<b>Đi làm gần + ngân sách hạn chế</b> → thường phải chấp nhận diện tích nhỏ hơn hoặc thuê thay vì sở hữu.")
    if ht >= 4 and tc >= 4:
        ds.append("<b>Cần người thân hỗ trợ + ngân sách hạn chế</b> → ở cùng/gần người thân là phương án cân bằng, "
                  "đánh đổi là quyền riêng tư và không gian sinh hoạt.")
    if ht >= 4 and tr >= 4:
        ds.append("<b>Cần người thân + giữ trường</b> → chỉ khả thi nếu người thân ở gần trường cũ; nếu không phải ưu tiên một trong hai.")
    if tr <= 2 and tc >= 4:
        ds.append("<b>Ít gắn với trường cũ + ngân sách hạn chế</b> → có thể đổi trường để đổi lấy nhà rẻ/rộng hơn; "
                  "đánh đổi là con phải thích nghi môi trường mới.")
    if not ds:
        ds.append("Các ưu tiên tương đối cân bằng, chưa xuất hiện đánh đổi nổi trội; hãy xem cột «Xung đột» của từng phương án.")
    return ds


@st.fragment   # kéo thanh trượt chỉ chạy lại phần này -> cập nhật tức thì
def khung_cong_cu():
    dau_muc("Công cụ quyết định", "So sánh các kịch bản theo mức ưu tiên của gia đình",
            "Kéo thanh trượt, biểu đồ và phân tích tự cập nhật ngay.")
    with st.container(key="card_huong_dan"):
        st.markdown("<div class='callout'><b>Cần hiểu trước khi dùng.</b> Công cụ không quyết định thay gia đình và "
                    "<b>không dự báo một hộ cụ thể</b>. Bạn cho biết yếu tố nào quan trọng (1 = ít, 5 = rất quan trọng); "
                    "công cụ chỉ cho thấy mỗi phương án giả lập khớp với ưu tiên đó đến đâu và phải đánh đổi điều gì.</div>",
                    unsafe_allow_html=True)
        st.caption("Thử nhanh một kịch bản mẫu:")
        cot_nut = st.columns(len(KICH_BAN_MAU), gap="small")
        for o, (nhan, gia_tri) in zip(cot_nut, KICH_BAN_MAU):
            o.button(nhan, on_click=ap_kich_ban, args=(gia_tri,), key="nut_" + nhan)
    st.write("")

    cs, ck = st.columns([2, 3], gap="large")
    with cs:
        with st.container(key="card_thanh_truot"):
            tieu_de_the("Mức quan trọng của bạn", "Thang 1–5")
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
            tieu_de_the("Điểm khớp của từng kịch bản", "Cột chồng = phần điểm do mỗi yếu tố đóng góp")
            ve_thu_tu = list(reversed(kq))
            mau_yt = [NAVY, PRIMARY, TEAL, AMBER]
            fig = go.Figure()
            for i, ten_yt in enumerate(YEU_TO):
                fig.add_bar(y=[p["ngan"] for p in ve_thu_tu], x=[p["dong_gop"][i] for p in ve_thu_tu],
                            name=ten_yt, orientation="h", marker_color=mau_yt[i],
                            hovertemplate="%{y}<br>" + ten_yt + ": %{x:.1f} điểm<extra></extra>")
            for p in ve_thu_tu:
                fig.add_annotation(x=p["khop"], y=p["ngan"], text=f"<b>{p['khop']:.0f}%</b>", xanchor="left",
                                   xshift=6, showarrow=False, font=dict(size=15))
            fig.update_layout(barmode="stack", xaxis_range=[0, 115], xaxis_title="Mức khớp ưu tiên (%)")
            ve(fig, 400, chu_giai_tren=True)

    st.write("")
    ca, cb = st.columns([2, 3], gap="large")
    with ca:
        with st.container(key="card_radar"):
            tieu_de_the("Ưu tiên của bạn so với phương án khớp nhất", top["ngan"])
            nhan_truc = ["Tài chính", "Giữ trường", "Đi làm gần", "Người thân"]
            dong = nhan_truc + nhan_truc[:1]
            radar = go.Figure()
            radar.add_trace(go.Scatterpolar(r=w + w[:1], theta=dong, fill="toself", name="Mức quan trọng bạn chọn",
                                            line=dict(color=PRIMARY), fillcolor="rgba(31,95,209,.25)"))
            radar.add_trace(go.Scatterpolar(r=top["diem"] + top["diem"][:1], theta=dong, name="Điểm đáp ứng của phương án",
                                            line=dict(color=AMBER, dash="dash")))
            radar.update_layout(polar=dict(radialaxis=dict(range=[0, 5], dtick=1, tickfont=dict(size=12)),
                                           angularaxis=dict(tickfont=dict(size=15))))
            ve(radar, 420, le=dict(l=70, r=70, t=24, b=8))
    with cb:
        with st.container(key="card_phan_tich"):
            tieu_de_the("Gợi ý phân tích đánh đổi", "Tự cập nhật theo ưu tiên bạn chọn")
            k1, k2, k3 = st.columns([3, 2, 3], gap="small")
            with k1:
                o_chi_so("Khớp nhất", top["ngan"])
            with k2:
                o_chi_so("Mức khớp", f"{top['khop']:.0f}%")
            with k3:
                o_chi_so("Hơn phương án thứ hai", f"{chenh_lech:.1f} điểm %")
            st.write("")
            if chenh_lech < 3:
                st.markdown(f"<div class='callout'>Hai phương án đầu (<b>{top['ngan']}</b> và <b>{nhi['ngan']}</b>) gần như "
                            "ngang nhau; ưu tiên hiện tại chưa đủ phân biệt, quyết định sẽ phụ thuộc yếu tố ngoài mô hình.</div>",
                            unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='callout'>Với ưu tiên hiện tại, <b>{top['ten']}</b> khớp nhất.<br>"
                            f"<b>Đạt được:</b> {top['duoc']}.<br><b>Phải đánh đổi:</b> {top['doi']}.</div>",
                            unsafe_allow_html=True)
            if top["xung_dot"]:
                st.markdown("<div class='callout warn' style='margin-top:.6rem'>Phương án khớp nhất vẫn kém ở yếu tố bạn đặt cao: <b>"
                            + ", ".join(top["xung_dot"]) + "</b>.</div>", unsafe_allow_html=True)
            cao_nhat = max(w)
            if min(w) == cao_nhat:
                mo = "Bạn chấm các yếu tố <b>ngang nhau</b>, nên kết quả phản ánh điểm đáp ứng trung bình của từng phương án."
            elif cao_nhat >= 4:
                mo = "Yếu tố đang chi phối kết quả: <b>" + "</b>, <b>".join(t for t, x in zip(YEU_TO, w) if x == cao_nhat) + "</b>."
            else:
                mo = ""
            if mo:
                st.markdown(f"<div class='txt' style='margin-top:.8rem'>{mo}</div>", unsafe_allow_html=True)
            st.markdown("<div class='txt' style='margin-top:.8rem'><b>Đánh đổi thường gặp với tổ hợp ưu tiên này:</b></div>"
                        + "".join(f"<div class='txt' style='margin-top:.3rem'>• {x}</div>" for x in goi_y_danh_doi(w)),
                        unsafe_allow_html=True)

    st.write("")
    with st.container(key="card_bang"):
        tieu_de_the("Bảng phân tích đánh đổi chi tiết", "Xếp theo mức khớp giảm dần")
        hang = []
        for p in kq:
            thanh = (f"<b>{p['khop']:.1f}%</b><div class='pbar'><span style='width:{min(p['khop'], 100):.0f}%'></span></div>")
            hang.append([f"<b>{html.escape(p['ten'])}</b>", thanh, html.escape(p["duoc"]), html.escape(p["doi"]),
                         html.escape(", ".join(p["xung_dot"])) if p["xung_dot"] else "—"])
        bang_html(["Phương án", "Mức khớp", "Điều đạt được", "Điều phải đánh đổi", "Xung đột với ưu tiên cao"], hang)
        with st.expander("Cách tính (để giải thích trước hội đồng)"):
            st.markdown(
                "- Mỗi phương án có điểm 1–5 cho 4 yếu tố (giả định minh họa của nhóm nghiên cứu).\n"
                "- **Mức khớp (%) = Σ(mức quan trọng × điểm phương án) ÷ (5 × Σ mức quan trọng) × 100.**\n"
                "- Biểu đồ cột chồng tách mức khớp thành phần đóng góp của từng yếu tố.\n"
                "- «Xung đột» xuất hiện khi yếu tố được chấm ≥ 4 nhưng phương án chỉ đạt ≤ 2 điểm.\n"
                "- Mức khớp cao **không có nghĩa** đó là lựa chọn đúng; chỉ phản ánh sự phù hợp với ưu tiên đã nhập.")


@st.fragment
def khung_tai_chinh():
    dau_muc("Góc chuyên đề", "Ước tính chi phí định kỳ khi di dời nhà",
            "Phép tính minh họa tại chỗ; số liệu bạn nhập không được lưu lại.")
    with st.container(key="card_tai_chinh"):
        i1, i2 = st.columns([1, 1], gap="large")
        with i1:
            nha = st.number_input("Chi phí thuê/trả góp nhà hàng tháng (VNĐ)", min_value=0, value=10_000_000, step=500_000)
            di_lai = st.number_input("Chi phí đi lại phát sinh thêm mỗi tháng (VNĐ)", min_value=0, value=2_000_000, step=200_000)
            thu_nhap = st.number_input("Thu nhập ổn định hàng tháng của hộ (VNĐ) – tùy chọn", min_value=0, value=0, step=1_000_000,
                                       help="Để 0 nếu không muốn nhập. Chỉ dùng để tính tỷ trọng, không được lưu.")
        with i2:
            tong = nha + di_lai
            t1, t2 = st.columns(2, gap="small")
            with t1:
                o_chi_so("Tổng chi phí mỗi tháng", f"{tong:,.0f} VNĐ")
            with t2:
                o_chi_so("Ước tính mỗi năm", f"{tong * 12:,.0f} VNĐ")
            if thu_nhap > 0:
                st.write("")
                phan_tram = tong / thu_nhap * 100
                o_chi_so("Chiếm trong thu nhập hàng tháng", f"{phan_tram:.0f}%")
                st.caption("Con số chỉ mô tả tỷ trọng theo dữ liệu bạn nhập, không phải khuyến nghị mức chi tiêu phù hợp.")
            else:
                st.caption("Nhập thu nhập (tùy chọn) để xem tỷ trọng chi phí trong thu nhập.")


with tab3:
    khung_cong_cu()
    st.write("")
    khung_tai_chinh()
    st.write("")
    # Tuyên bố từ chối trách nhiệm (BẮT BUỘC) - luôn hiển thị cuối tab
    st.markdown("<div class='disclaimer'>Công cụ này chỉ mang tính chất minh họa dựa trên dữ liệu khảo sát nghiên cứu khoa học, "
                "không phải lời khuyên tài chính hay pháp lý tuyệt đối.</div>", unsafe_allow_html=True)

# =============================================================================
# TAB 4. TƯ LIỆU THỰC ĐỊA
# =============================================================================
with tab4:
    dau_muc("Tư liệu thực địa", "Khu vực Vành đai 2.5: Ngụy Như Kon Tum – Nhân Hòa – Nguyễn Trãi",
            "Hình ảnh và video ghi nhận khu vực giải phóng mặt bằng dọc tuyến đường.")
    with st.container(key="card_anh"):
        tieu_de_the("Hình ảnh", "Ảnh lấy từ nguồn công khai; hãy ghi rõ nguồn khi trích dẫn")
        cot_anh = st.columns(len(ANH_THUC_DIA), gap="medium")
        for o, (nguon, ct) in zip(cot_anh, ANH_THUC_DIA):
            with o:
                ten_nguon = urlparse(nguon).netloc if nguon.startswith("http") else "tư liệu của nhóm"
                hien_anh(nguon, f"{ct} · Nguồn: {ten_nguon}")
    st.write("")
    with st.container(key="card_video"):
        tieu_de_the("Video cập nhật tiến độ dự án")
        cot_vd = st.columns(max(len(VIDEO), 1), gap="large")
        for o, (tieu_de, url) in zip(cot_vd, VIDEO):
            with o:
                st.markdown(f"<div class='txt'><b>{html.escape(tieu_de)}</b></div>", unsafe_allow_html=True)
                st.video(url)

# =============================================================================
# TAB 5. TÀI LIỆU & MÃ NGUỒN MỞ
# =============================================================================
with tab5:
    dau_muc("Khoa học mở", "Tài liệu, dữ liệu và mã nguồn",
            "Toàn bộ quy trình phân tích có thể chạy lại từ dữ liệu đã mã hóa.")
    d1, d2 = st.columns(2, gap="large")
    with d1:
        with st.container(key="card_co"):
            tieu_de_the("Dữ liệu có trong bộ công khai", "Đã mã hóa, ẩn danh tuyệt đối")
            st.markdown("<div class='txt'>• Mã phiếu ngẫu nhiên (H001, H002…), không liên hệ được với người trả lời.<br>"
                        "• Khoảng cách theo <b>nhóm</b>, không phải số chính xác.<br>"
                        "• Hình thức nhà ở trước – sau, giữ/đổi trường, nhóm thời gian đi lại.<br>"
                        "• Mức quan trọng các yếu tố và mức hài lòng (thang 1–5).</div>", unsafe_allow_html=True)
    with d2:
        with st.container(key="card_khong"):
            tieu_de_the("Không thu thập", "Theo quy tắc đạo đức nghiên cứu")
            st.markdown("<div class='txt'>• Họ tên, số điện thoại, email.<br>• Địa chỉ cũ/mới, vị trí GPS.<br>"
                        "• Tên trường, tên nơi làm việc.<br>• Thu nhập, dư nợ, số tiền bồi thường chính xác.</div>",
                        unsafe_allow_html=True)
    st.write("")
    with st.container(key="card_tu_dien"):
        tieu_de_the("Từ điển biến (rút gọn)")
        bang_html(["Tên biến", "Ý nghĩa", "Kiểu"], [
            ["<code>ma_phieu</code>", "Mã phiếu ẩn danh", "Văn bản"],
            ["<code>khoang_cach</code>", "Khoảng cách nơi ở mới – cũ (nhóm)", "5 nhóm"],
            ["<code>nha_o_truoc</code>, <code>nha_o_sau</code>", "Hình thức nhà ở trước/sau di dời", "5 nhóm"],
            ["<code>giu_truong</code>", "Kết quả giữ trường cho các con", "3 nhóm"],
            ["<code>tg_hoc_*</code>, <code>tg_lam_*</code>", "Thời gian đi học/đi làm một chiều, trước và sau", "5 nhóm"],
            ["<code>doi_tg_hoc</code>, <code>doi_tg_lam</code>", "Thay đổi: Giảm / Không đổi / Tăng / Không xác định", "Phân loại"],
            ["<code>qt_tai_chinh</code>, <code>qt_giu_truong</code>, <code>qt_di_lam</code>, <code>qt_nguoi_than</code>",
             "Mức quan trọng của 4 yếu tố khi chọn nơi ở", "Thang 1–5"],
            ["<code>kha_nang_tai_chinh</code>", "Nguồn lực tài chính huy động được lúc chốt nơi ở (thấp = 1–2)", "Thang 1–5"],
            ["<code>so_phuong_an</code>, <code>hai_long</code>", "Số phương án đã cân nhắc; mức hài lòng sau di dời", "Số nguyên / 1–5"],
        ])
        st.write("")
        st.download_button("Tải dữ liệu (CSV)", df_goc.to_csv(index=False).encode("utf-8-sig"),
                           file_name="du_lieu_vanh_dai_2_5.csv", mime="text/csv")
    st.write("")
    n1, n2 = st.columns(2, gap="large")
    with n1:
        with st.container(key="card_so_tay"):
            tieu_de_the("Sổ tay Python phân tích dữ liệu")
            st.markdown("<div class='txt'>Nhập dữ liệu → kiểm tra điều kiện tham gia → mã hóa biến → tạo biến thay đổi "
                        "trước–sau → xuất bảng mô tả → ba kiểm tra đã định trước (H1–H3) → vẽ biểu đồ.</div>",
                        unsafe_allow_html=True)
            st.write("")
            if NOTEBOOK_URL:
                st.markdown(f"[Mở hướng dẫn đọc sổ tay Python]({NOTEBOOK_URL})")
            else:
                st.caption("Đường dẫn sổ tay sẽ được cập nhật (biến NOTEBOOK_URL ở đầu tệp app.py).")
            with st.expander("Quy tắc kiểm tra giả thuyết H1–H3"):
                st.markdown("- Chỉ kiểm tra khi tổng mẫu ≥ 30 và mỗi nhóm so sánh có ≥ 5 quan sát; nếu không, chỉ báo cáo số lượng và tỷ lệ.\n"
                            "- Dùng bảng 2×2 và kiểm định Fisher; kết quả chỉ mang tính khám phá.\n"
                            "- Kết quả không ủng hộ giả thuyết thì giữ nguyên, không đổi giả thuyết sau khi xem dữ liệu.")
    with n2:
        with st.container(key="card_gop_y"):
            tieu_de_the("Góp ý từ cộng đồng", "Nội dung bạn nhập ở đây chưa được lưu lên máy chủ")
            with st.form("feedback_form"):
                ten = st.text_input("Họ tên / Đơn vị (không bắt buộc)")
                nd = st.text_area("Nội dung góp ý / nhận xét", height=110)
                gui = st.form_submit_button("Soạn góp ý")
            if gui:
                if not nd.strip():
                    st.warning("Vui lòng nhập nội dung góp ý.")
                else:
                    st.success("Đã soạn xong. Ứng dụng không lưu nội dung này, hãy gửi qua kênh bên dưới để nhóm nhận được.")
                    if EMAIL_LIEN_HE:
                        thu = quote(f"Góp ý về đề tài Vành đai 2.5 - {ten}")
                        st.markdown(f"[Gửi góp ý qua email](mailto:{EMAIL_LIEN_HE}?subject={thu}&body={quote(nd)})")
                    if FORM_GOP_Y_URL:
                        st.markdown(f"[Gửi góp ý qua biểu mẫu]({FORM_GOP_Y_URL})")
                    if not (EMAIL_LIEN_HE or FORM_GOP_Y_URL):
                        st.caption("Nhóm chưa cấu hình kênh nhận góp ý (biến EMAIL_LIEN_HE hoặc FORM_GOP_Y_URL ở đầu tệp app.py).")

    st.markdown("<div style='text-align:center;color:#5F6E85;font-size:1rem;margin-top:2rem'>© 2026 — Đề tài NCKH học sinh phổ thông · "
                "Thực hiện bởi Nguyễn Vũ Tuấn Minh (12 Tin 1, THPT chuyên Hà Nội – Amsterdam)</div>", unsafe_allow_html=True)
