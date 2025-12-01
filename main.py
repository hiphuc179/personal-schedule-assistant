import streamlit as st
from streamlit_calendar import calendar
from database.database_service import EventManager
from datetime import datetime, time
import sys
import os
import pandas as pd

# Import NLP
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from nlp.nlp_engine import NLPEngine
except ImportError:
    from nlp.nlp_engine import NLPEngine 

# --- 1. INIT ---
st.set_page_config(layout="wide", page_title="App Đặt Lịch")

if "db_service" not in st.session_state:
    st.session_state.db_service = EventManager()
if "nlp_engine" not in st.session_state:
    st.session_state.nlp_engine = NLPEngine()

if "calendar_version" not in st.session_state: st.session_state["calendar_version"] = 0
if "nlp_data_cache" not in st.session_state: st.session_state["nlp_data_cache"] = None

# CSS
st.markdown("""
    <style>
        .stButton button { width: 100%; border-radius: 5px; }
        .block-container { padding-top: 1rem; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. HỆ THỐNG NHẮC NHỞ (CÓ ÂM THANH)
# ==========================================
@st.fragment(run_every=60) # Chạy ngầm mỗi 60 giây
def check_reminders():
    """Quét DB để nhắc nhở sự kiện sắp tới"""
    if "db_service" not in st.session_state: return
    
    now = datetime.now()
    # Quan trọng: Lấy lại connection mới mỗi lần chạy trong fragment để tránh lỗi thread
    # (Trong code db_service đã handle việc mở/đóng conn rồi nên gọi hàm là được)
    events = st.session_state.db_service.get_all_events()
    
    found_alarm = False
    
    for e in events:
        try:
            start_dt = datetime.fromisoformat(e.start_time)
            
            if start_dt > now:
                diff_minutes = (start_dt - now).total_seconds() / 60
                remind_limit = e.reminder_time if e.reminder_time is not None else 15
                
                if 0 < diff_minutes <= remind_limit:
                    time_str = start_dt.strftime('%H:%M')
                    msg = f"⏰ Sắp diễn ra: **{e.event_name}** lúc {time_str}"
                    if e.place: msg += f" tại {e.place}"
                    
                    # 1. Hiện Pop-up
                    st.toast(msg, icon="🔔")
                    found_alarm = True
                    
        except Exception:
            continue
            
    # 2. Phát Âm thanh (Nếu có sự kiện cần nhắc)
    if found_alarm:
        # Link âm thanh "Beep" ngắn gọn
        sound_url = "assets/Rick Astley - Never Gonna Give You Up (Official Video) (4K Remaster) - Rick Astley (youtube).mp3" 
        
        st.audio(sound_url, format="audio/mp3", autoplay=True)

check_reminders()

# ==========================================
# 3. DIALOGS (THÊM - SỬA - XÓA)
# ==========================================

# --- DIALOG SỬA SỰ KIỆN (MỚI) ---
@st.dialog("Chỉnh sửa sự kiện", on_dismiss="ignore")
def dialog_edit_event(event_id):
    e = st.session_state.db_service.get_event_by_id(event_id)
    if not e:
        st.error("Không tìm thấy sự kiện!")
        return

    with st.form("form_edit_event"):
        name = st.text_input("Tên sự kiện", value=e.event_name)
        loc = st.text_input("Địa điểm", value=e.place or "")
        
        # Parse time cũ
        try:
            dt_old = datetime.fromisoformat(e.start_time)
            d_val = dt_old.date()
            t_val = dt_old.time()
        except:
            d_val = datetime.now().date()
            t_val = datetime.now().time()

        c1, c2 = st.columns(2)
        with c1: d = st.date_input("Ngày", value=d_val)
        with c2: t = st.time_input("Giờ", value=t_val)
        
        remind = st.number_input("Nhắc trước (phút)", value=int(e.reminder_time or 0))
        
        if st.form_submit_button("Cập nhật"):
            start_iso = datetime.combine(d, t).isoformat()
            st.session_state.db_service.update_event(
                event_id, name, start_iso, loc, None, remind, e.status
            )
            st.success("Đã cập nhật!")
            st.session_state["calendar_version"] += 1
            st.rerun()

# --- DIALOG SỬA THÓI QUEN (MỚI) ---
@st.dialog("Chỉnh sửa thói quen", on_dismiss="ignore")
def dialog_edit_habit(habit_id):
    # Lưu ý: Cần thêm hàm get_habit_by_id trong DB Service nếu chưa có
    # Ở đây em sẽ load all rồi lọc tạm (để tránh phải sửa DB Service nhiều)
    habits = st.session_state.db_service.get_all_habits()
    h = next((x for x in habits if x.id == habit_id), None)
    
    if not h:
        st.error("Không tìm thấy!")
        return

    with st.form("form_edit_habit"):
        name = st.text_input("Tên thói quen", value=h.habit_name)
        loc = st.text_input("Địa điểm", value=h.place or "")
        
        freq_options = ["daily", "weekly", "monthly"]
        idx = freq_options.index(h.frequency) if h.frequency in freq_options else 0
        freq = st.selectbox("Tần suất", freq_options, index=idx)
        
        remind = st.number_input("Nhắc trước (phút)", value=int(h.reminder_time or 0))
        
        if st.form_submit_button("Cập nhật"):
            # Logic update habit (Cần implement trong DB nếu muốn chuẩn)
            # Tạm thời: Xóa cũ tạo mới cho nhanh
            st.session_state.db_service.delete_habit(habit_id)
            st.session_state.db_service.create_habit(name, freq, place=loc, reminderTime=remind)
            
            st.success("Đã cập nhật!")
            st.rerun()

@st.dialog("Xác nhận thông tin AI", on_dismiss="ignore")
def dialog_confirm_nlp(data, intent):
    st.info("AI đã trích xuất được thông tin sau:")
    with st.form("form_nlp"):
        name = st.text_input("Tên:", value=data['event_name'])
        loc = st.text_input("Địa điểm:", value=data['location'] if data['location'] else "")
        
        if intent == 'create_habit':
            freq = st.selectbox("Tần suất:", ["daily", "weekly", "monthly"], index=0)
            remind = st.number_input("Nhắc trước (phút):", value=int(data['reminder'] or 0))
            date_val = datetime.now().date()
            time_val = datetime.now().time()
        else:
            t = data['time']
            d_default = t['date'].date() if t.get('date') else datetime.now().date()
            t_default = time(t['start_time']['hour'], t['start_time']['minute']) if t.get('start_time') else datetime.now().time()
            
            c1, c2 = st.columns(2)
            with c1: date_val = st.date_input("Ngày:", value=d_default)
            with c2: time_val = st.time_input("Giờ:", value=t_default)
            remind = st.number_input("Nhắc trước (phút):", value=int(data['reminder'] or 15))
            freq = None

        if st.form_submit_button("💾 Lưu ngay"):
            if intent == 'create_habit':
                st.session_state.db_service.create_habit(name, freq, place=loc, reminderTime=remind)
                st.toast("Đã tạo thói quen!")
            else:
                start_iso = datetime.combine(date_val, time_val).isoformat()
                st.session_state.db_service.create_event(name, start_iso, place=loc, reminderTime=remind)
                st.toast("Đã tạo sự kiện!")
            
            st.session_state["nlp_data_cache"] = None
            st.session_state["calendar_version"] += 1
            st.rerun()

@st.dialog("Thêm sự kiện thủ công", on_dismiss="ignore")
def dialog_add_event():
    with st.form("manual_form"):
        name = st.text_input("Tên sự kiện")
        loc = st.text_input("Địa điểm")
        c1, c2 = st.columns(2)
        with c1: d = st.date_input("Ngày")
        with c2: t = st.time_input("Giờ")
        remind = st.number_input("Nhắc trước (phút)", value=15)
        if st.form_submit_button("Lưu"):
            start = datetime.combine(d, t).isoformat()
            st.session_state.db_service.create_event(name, start, place=loc, reminderTime=remind)
            st.session_state["calendar_version"] += 1
            st.rerun()

@st.dialog("Chi tiết", on_dismiss="ignore")
def dialog_detail(id):
    e = st.session_state.db_service.get_event_by_id(id)
    if e:
        st.subheader(e.event_name)
        st.write(f"📍 {e.place or '-'}")
        st.write(f"⏰ {e.start_time}")
        st.write(f"🔔 Nhắc: {e.reminder_time}p")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✏️ Sửa", use_container_width=True):
                dialog_edit_event(id) # Mở dialog sửa
        with c2:
            if st.button("🗑️ Xóa", type="primary", use_container_width=True):
                st.session_state.db_service.delete_event(id)
                st.session_state["calendar_version"] += 1
                st.rerun()

# ==========================================
# 4. GIAO DIỆN CHÍNH
# ==========================================
st.title("📅 Quản Lý Lịch Trình")

# HEADER
c_nlp, c_btn, c_search = st.columns([4, 1, 2], vertical_alignment="bottom")

with c_nlp:
    user_text = st.text_input("🤖 AI:", placeholder="VD: Họp team lúc 9h sáng mai", key="nlp_in")

with c_btn:
    if st.button("✨ Thêm tự động", use_container_width=True):
        if user_text:
            try:
                res = st.session_state.nlp_engine.process_command(user_text)
                st.session_state["nlp_data_cache"] = res
            except Exception as e: st.error(f"Lỗi: {e}")

with c_search:
    search_kw = st.text_input("🔍 Tìm kiếm:", placeholder="Tìm sự kiện...", key="search_in")

if st.session_state["nlp_data_cache"]:
    res = st.session_state["nlp_data_cache"]
    dialog_confirm_nlp(res['data'], res['intent'])

# BODY
col_cal, col_habit = st.columns([2.5, 1]) 

# CỘT TRÁI
with col_cal:
    events = st.session_state.db_service.get_all_events()
    if search_kw: events = [e for e in events if search_kw.lower() in e.event_name.lower()]
    
    cal_events = []
    for e in events:
        cal_events.append({
            "id": str(e.id),
            "title": e.event_name,
            "start": e.start_time,
            "end": e.end_time,
            "backgroundColor": "#3788d8"
        })

    cal = calendar(
        events=cal_events,
        options={
            "headerToolbar": {"left": "today prev,next", "center": "title", "right": "dayGridMonth,timeGridWeek"},
            "initialView": "dayGridMonth",
            "locale": "vi",
            "height": 550
        },
        key=f"cal_{st.session_state['calendar_version']}",
        callbacks=["eventClick"]
    )
    if cal and "eventClick" in cal:
        dialog_detail(cal["eventClick"]["event"]["id"])

    st.divider()
    st.subheader("📝 Danh sách sự kiện")
    if events:
        for e in events:
            with st.container(border=True):
                c1, c2, c3, c4, c5 = st.columns([3, 2, 2, 1, 1])
                c1.write(f"**{e.event_name}**")
                try: dt = datetime.fromisoformat(e.start_time).strftime("%H:%M %d/%m")
                except: dt = e.start_time
                c2.caption(f"🕒 {dt}")
                c3.caption(f"📍 {e.place or '-'}")
                
                # Nút Sửa và Xóa
                if c4.button("✏️", key=f"ed_e_{e.id}"):
                    dialog_edit_event(e.id)
                if c5.button("🗑️", key=f"del_e_{e.id}"):
                    st.session_state.db_service.delete_event(e.id)
                    st.session_state["calendar_version"] += 1
                    st.rerun()
    else:
        st.info("Chưa có sự kiện nào.")

# CỘT PHẢI: HABIT + GIỮ LỬA 🔥
with col_habit:
    if st.button("➕ Thêm thủ công", use_container_width=True):
        st.session_state["nlp_data_cache"] = None
        dialog_add_event()
        
    st.divider()
    st.subheader("🔥 Giữ Lửa Thói Quen")
    habits = st.session_state.db_service.get_all_habits()
    
    if habits:
        for h in habits:
            with st.container(border=True):
                c1, c2 = st.columns([4, 1])
                with c1:
                    st.markdown(f"**{h.habit_name}**")
                    st.caption(f"{h.frequency} | {h.place or '-'}")
                
                with c2:
                    # Check xem hôm nay đã làm chưa
                    today_str = datetime.now().strftime("%Y-%m-%d")
                    is_done = h.last_completed == today_str
                    
                    btn_label = f"🔥 {h.current_streak}"
                    
                    if is_done:
                        # Đã làm -> Disable nút
                        st.button(btn_label, key=f"done_{h.id}", disabled=True, help="Đã hoàn thành hôm nay!")
                    else:
                        # Chưa làm -> Bấm để check-in
                        if st.button(btn_label, key=f"check_{h.id}", type="primary", help="Bấm để điểm danh!"):
                            st.session_state.db_service.check_in_habit(h.id)
                            st.balloons() # 🎆 BẮN PHÁO HOA
                            st.rerun()
                
                # Nút xóa nhỏ
                if st.button("🗑️", key=f"del_h_{h.id}"):
                    st.session_state.db_service.delete_habit(h.id)
                    st.rerun()
    else:
        st.caption("Chưa có thói quen.")