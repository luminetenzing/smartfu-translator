import base64
from pathlib import Path
import streamlit as st
import translator

ROOT = Path(__file__).parent


def find_asset(stem):
    for ext in (".png", ".jpg", ".jpeg", ".webp"):
        p = ROOT / f"{stem}{ext}"
        if p.exists():
            return p
    return None


def to_data_uri(path):
    ext = path.suffix.lower().lstrip(".")
    mime = "jpeg" if ext == "jpg" else ext
    b64 = base64.b64encode(path.read_bytes()).decode()
    return f"data:image/{mime};base64,{b64}"


icon_file = find_asset("icon")
bg_file = find_asset("bg")

st.set_page_config(
    page_title="smartfu translator",
    page_icon=str(icon_file) if icon_file else None,
    layout="wide",
)

# Load external stylesheet + inject background image separately
css = (ROOT / "style.css").read_text(encoding="utf-8")
if bg_file:
    bg_uri = to_data_uri(bg_file)
    css += f"""
    .stApp {{
        background-image: linear-gradient(rgba(10, 30, 60, 0.18), rgba(10, 30, 60, 0.25)), url("{bg_uri}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    """
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


@st.cache_data
def cached_languages():
    return translator.load_languages()


@st.cache_data(show_spinner=False)
def cached_translate(text, target_code):
    return translator.translate(text, target_code)


name_to_code, code_to_name = cached_languages()

if "history" not in st.session_state:
    st.session_state.history = []

if icon_file:
    st.markdown(
        f"""
        <div class="header-row">
            <img src="{to_data_uri(icon_file)}" class="app-logo" alt="logo" />
            <div>
                <h1 class="app-name">smartfu translator</h1>
                <p class="app-desc">Auto-detect translation & pronunciation tool</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.title("smartfu translator")

st.divider()

left, right = st.columns(2, gap="large")

with left:
    st.subheader("Văn bản gốc")
    src_text = st.text_area(
        "Input",
        height=220,
        placeholder="Nhập nội dung cần dịch...",
        label_visibility="collapsed",
    )
    st.caption(f"{len(src_text)} ký tự")

with right:
    st.subheader("Bản dịch")
    langs = list(name_to_code.keys())
    default_idx = langs.index("Vietnamese") if "Vietnamese" in langs else 0

    target_name = st.selectbox(
        "Target",
        options=langs,
        index=default_idx,
        label_visibility="collapsed",
    )
    target_code = name_to_code[target_name]

    if st.button("Dịch ngay", type="primary", use_container_width=True):
        if not src_text.strip():
            st.warning("Bạn chưa nhập nội dung.")
        else:
            with st.spinner("Đang dịch..."):
                try:
                    result, src_code, provider = cached_translate(src_text, target_code)
                    src_name = code_to_name.get(src_code.lower(), src_code.upper()) if src_code else "Unknown"

                    st.info(f"Phát hiện: **{src_name}** ({provider})")
                    st.text_area("Output", value=result, height=150, label_visibility="collapsed")

                    try:
                        audio = translator.text_to_speech(result, target_code)
                        st.audio(audio, format="audio/mp3")
                    except Exception:
                        st.caption("Không hỗ trợ phát âm cho ngôn ngữ này.")

                    st.session_state.history.insert(0, {
                        "from": src_name,
                        "to": target_name,
                        "src": src_text,
                        "out": result,
                    })
                except Exception as err:
                    st.error(f"Lỗi khi dịch: {err}")

if st.session_state.history:
    st.divider()
    with st.expander(f"Lịch sử dịch ({len(st.session_state.history)})"):
        for entry in st.session_state.history[:5]:
            st.markdown(f"**{entry['from']} -> {entry['to']}**")
            st.write(entry["src"])
            st.write(f"> {entry['out']}")
            st.markdown("---")