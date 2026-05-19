import streamlit as st
from ultralytics import YOLO
from PIL import Image
import cv2
import numpy as np
import sqlite3
import os
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

# =====================
# Cấu hình giao diện
# =====================

st.set_page_config(
    page_title="Helmet Detection System",
    page_icon="🚦",
    layout="wide"
)

# =====================
# CSS GIAO DIỆN ĐẸP
# =====================

st.markdown("""
<style>

/* nền */
.stApp{
background:linear-gradient(
135deg,
#F3F9FF,
#E8F5FF
);
}

/* sidebar */

section[data-testid="stSidebar"]{

background:linear-gradient(
180deg,
#1565C0,
#6A1B9A
);

padding-top:25px;
}


/* chữ sidebar */

section[data-testid="stSidebar"] *{

color:white!important;
}


/* radio */

.stRadio > div{
gap:14px;
}


.stRadio label{

background:rgba(
255,
255,
255,
0.2
);

padding:18px;

border-radius:15px;

font-size:18px;

font-weight:bold;

transition:0.3s;
}


.stRadio label:hover{

background:white!important;

transform:scale(1.03);

color:black!important;
}


/* card */

.custom-card{

background:white;

padding:20px;

border-radius:20px;

box-shadow:
0 4px 10px rgba(
0,
0,
0,
0.15
);

margin-bottom:15px;
}


/* metric */

[data-testid="metric-container"]{

background:white;

border-radius:15px;

padding:15px;

box-shadow:
0px 4px 10px rgba(
0,
0,
0,
0.1
);

border-left:
6px solid #1976D2;
}


/* button */

.stButton>button{

width:100%;

height:50px;

font-size:17px;

font-weight:bold;

border-radius:12px;

background:#1565C0;

color:white;

border:none;
}


.stButton>button:hover{

background:#0D47A1;
}


/* upload */

[data-testid="stFileUploader"]{

background:white;

padding:15px;

border-radius:15px;

box-shadow:
0px 2px 10px rgba(
0,
0,
0,
0.1
);
}

</style>

""",unsafe_allow_html=True)

# =====================
# Tạo thư mục
# =====================

os.makedirs("uploads", exist_ok=True)
os.makedirs("output", exist_ok=True)

# =====================
# Database
# =====================

conn=sqlite3.connect(
    "history.db",
    check_same_thread=False
)

cursor=conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS history(
id INTEGER PRIMARY KEY AUTOINCREMENT,
filename TEXT,
resultfile TEXT,
status TEXT,
time TEXT
)
""")

conn.commit()

# =====================
# Load model
# =====================

model=YOLO("best.pt")

# =====================
# Sidebar
# =====================

st.sidebar.markdown("""

<h1 style='
text-align:center;
font-size:35px'>

🚦 Helmet Detection

</h1>

<hr>

""",unsafe_allow_html=True)


menu=st.sidebar.radio(
    "Chức năng",
    [
        "🏠 Trang chủ",
        "📷 Kiểm tra",
        "📁 Lịch sử",
        "📊 Thống kê"
    ]
)


# =====================
# Trang chủ
# =====================

if menu=="🏠 Trang chủ":

    # ===== TIÊU ĐỀ =====
    st.markdown("""
    <h1 style='
    text-align:center;
    color:#1565C0;
    font-size:38px;'>
    🚦 HỆ THỐNG PHÁT HIỆN NGƯỜI ĐI XE MÁY KHÔNG ĐỘI MŨ BẢO HIỂM
    </h1>
    """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)


    # ===== CHIA 2 CỘT: ẢNH + GIỚI THIỆU =====
    col1, col2 = st.columns([1,1.5])

    with col1:
        st.image(
            "traffic.jpg",
            width=350
        )

    with col2:

        st.markdown("""
        <div style="
        background-color:#E3F2FD;
        padding:25px;
        border-radius:15px;
        border-left:8px solid #1976D2;
        ">

        <h3 style='color:#0D47A1'>
        ⛑️ An toàn giao thông
        </h3>

        <p style='font-size:18px'>

        Đội mũ bảo hiểm khi tham gia giao thông 
        là trách nhiệm của mọi người nhằm giảm thiểu
        nguy cơ chấn thương và nâng cao ý thức chấp hành luật.

        </p>

        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)


    # ===== THÔNG TIN HỆ THỐNG =====

    st.subheader("📌 Chức năng hệ thống")

    c1,c2,c3 = st.columns(3)

    with c1:

        st.markdown("""
        <div style='
        background:#E8F5E9;
        padding:20px;
        border-radius:15px;
        height:220px'>
        
        <h3>🤖 AI Detection</h3>

        ✔ Phát hiện người

        <br>✔ Phát hiện xe máy

        <br>✔ Phát hiện mũ bảo hiểm

        </div>
        """,unsafe_allow_html=True)

    with c2:

        st.markdown("""
        <div style='
        background:#FFF3E0;
        padding:20px;
        border-radius:15px;
        height:220px'>
        
        <h3>⚙️ Rule-Based</h3>

        ✔ Có đội mũ

        <br>✔ Không đội mũ

        <br>✔ Cảnh báo vi phạm

        </div>
        """,unsafe_allow_html=True)

    with c3:

        st.markdown("""
        <div style='
        background:#F3E5F5;
        padding:20px;
        border-radius:15px;
        height:220px'>
        
        <h3>📷 Hỗ trợ</h3>

        ✔ Tải ảnh/video

        <br>✔ Theo dõi lịch sử

        <br>✔ Thống kê dữ liệu

        </div>
        """,unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)


    # ===== QUY TRÌNH =====

    st.subheader("🔄 Quy trình hoạt động")

    st.markdown("""
    <div style='
    background:#FAFAFA;
    padding:25px;
    border-radius:15px;
    text-align:center;
    font-size:20px;'>

    📤 Upload ảnh/video
    
    ⬇️
    
    🤖 YOLOv8 Detection
    
    ⬇️
    
    ⚙️ Rule-Based
    
    ⬇️
    
    📊 Xử lý kết quả
    
    ⬇️
    
    💾 Lưu lịch sử

    </div>
    """, unsafe_allow_html=True)


    st.markdown("<br>", unsafe_allow_html=True)


    # ===== FOOTER =====

    st.markdown("""
    <div style='
    text-align:center;
    color:gray;
    padding:15px'>
    
    Hệ thống hỗ trợ phát hiện và cảnh báo người điều khiển 
    xe máy không đội mũ bảo hiểm nhằm nâng cao ý thức 
    chấp hành luật giao thông.

    </div>
    """, unsafe_allow_html=True)

# =====================
# KIỂM TRA
# =====================

elif menu=="📷 Kiểm tra":

    st.title(
        "📷 Tải ảnh hoặc video để nhận diện"
    )

    file=st.file_uploader(
    "Chọn ảnh hoặc video",
    type=[
        "jpg",
        "jpeg",
        "png",
        "mp4",
        "avi",
        "mov"
    ]
    )

    if file:

        filename=file.name

        upload_path=f"uploads/{filename}"

        with open(upload_path,"wb") as f:

            f.write(
                file.getbuffer()
            )

        ext=filename.split(".")[-1].lower()

        person_count=0
        motorbike_count=0
        helmet_count=0
        violation_count=0


        # ==================================
        # ẢNH
        # ==================================

        if ext in ["jpg","jpeg","png"]:

            image=Image.open(
                upload_path
            )

            img=np.array(
                image
            )

            col1,col2=st.columns(2)

            with col1:

                st.subheader(
                    "Ảnh gốc"
                )

                st.image(
                    image
                )


            with st.spinner(
                "Đang xử lý..."
            ):

                results=model.predict(
                    img,
                    conf=0.25
                )


            result=results[0]

            result_img=img.copy()

            boxes=result.boxes.xyxy.cpu().numpy()
            classes=result.boxes.cls.cpu().numpy()

            persons=[]
            helmets=[]
            motorbikes=[]


            # ==================
            # Tách object
            # ==================

            for box,cls in zip(
                boxes,
                classes
            ):

                x1,y1,x2,y2=map(
                    int,
                    box
                )

                if cls==0:

                    persons.append(
                        [x1,y1,x2,y2]
                    )

                elif cls==1:

                    motorbikes.append(
                        [x1,y1,x2,y2]
                    )

                elif cls==2:

                    helmets.append(
                        [x1,y1,x2,y2]
                    )


            person_count=len(
                persons
            )

            helmet_count=len(
                helmets
            )

            motorbike_count=len(
                motorbikes
            )


            # ==================
            # Rule
            # ==================

            for p in persons:

                px1,py1,px2,py2=p

                head_y=py1+(py2-py1)//3

                helmet_found=False

                for h in helmets:

                    hx1,hy1,hx2,hy2=h

                    center_x=(hx1+hx2)//2

                    center_y=(hy1+hy2)//2


                    if(
                        px1<center_x<px2
                        and
                        py1<center_y<head_y
                    ):

                        helmet_found=True
                        break


                # xanh = có mũ

                if helmet_found:

                    color=(0,255,0)

                    label="Helmet"


                # đỏ = vi phạm

                else:

                    color=(0,0,255)

                    label="No Helmet"

                    violation_count+=1


                cv2.rectangle(
                    result_img,
                    (px1,py1),
                    (px2,py2),
                    color,
                    3
                )


                cv2.putText(
                    result_img,
                    label,
                    (px1,py1-10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    color,
                    2
                )


            output_file=f"output/result_{filename}"

            cv2.imwrite(
                output_file,
                cv2.cvtColor(
                    result_img,
                    cv2.COLOR_BGR2RGB
                )
            )


            with col2:

                st.subheader(
                    "Kết quả"
                )

                st.image(
                    result_img,
                    channels="BGR"
                )



        # ==================================
        # VIDEO
        # ==================================

        else:

            st.subheader(
                "🎥 Video gốc"
            )

            st.video(
                upload_path
            )


            cap=cv2.VideoCapture(
                upload_path
            )

            width=int(
                cap.get(
                    cv2.CAP_PROP_FRAME_WIDTH
                )
            )

            height=int(
                cap.get(
                    cv2.CAP_PROP_FRAME_HEIGHT
                )
            )

            fps=int(
                cap.get(
                    cv2.CAP_PROP_FPS
                )
            )

            output_file=f"output/result_{filename}"

            out=cv2.VideoWriter(
                output_file,
                cv2.VideoWriter_fourcc(
                    *'mp4v'
                ),
                fps,
                (width,height)
            )

            progress=st.progress(
                0
            )

            total_frames=int(
                cap.get(
                    cv2.CAP_PROP_FRAME_COUNT
                )
            )

            frame_count=0


            while cap.isOpened():

                ret,frame=cap.read()

                if not ret:

                    break


                results=model.predict(
                    frame,
                    conf=0.25
                )

                result=results[0]

                result_frame=frame.copy()

                boxes=result.boxes.xyxy.cpu().numpy()
                classes=result.boxes.cls.cpu().numpy()

                persons=[]
                helmets=[]
                motorbikes=[]


                for box,cls in zip(
                    boxes,
                    classes
                ):

                    x1,y1,x2,y2=map(
                        int,
                        box
                    )

                    if cls==0:

                        persons.append(
                            [x1,y1,x2,y2]
                        )

                    elif cls==1:

                        motorbikes.append(
                            [x1,y1,x2,y2]
                        )

                    elif cls==2:

                        helmets.append(
                            [x1,y1,x2,y2]
                        )


                person_count=max(
                    person_count,
                    len(persons)
                )

                helmet_count=max(
                    helmet_count,
                    len(helmets)
                )

                motorbike_count=max(
                    motorbike_count,
                    len(motorbikes)
                )


                for p in persons:

                    px1,py1,px2,py2=p

                    head_y=py1+(py2-py1)//3

                    helmet_found=False


                    for h in helmets:

                        hx1,hy1,hx2,hy2=h

                        center_x=(hx1+hx2)//2

                        center_y=(hy1+hy2)//2


                        if(
                            px1<center_x<px2
                            and
                            py1<center_y<head_y
                        ):

                            helmet_found=True
                            break


                    if helmet_found:

                        color=(0,255,0)

                        label="Helmet"

                    else:

                        color=(0,0,255)

                        label="No Helmet"

                        violation_count+=1


                    cv2.rectangle(
                        result_frame,
                        (px1,py1),
                        (px2,py2),
                        color,
                        3
                    )

                    cv2.putText(
                        result_frame,
                        label,
                        (px1,py1-10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        color,
                        2
                    )

                out.write(
                    result_frame
                )

                frame_count+=1

                progress.progress(
                    frame_count/total_frames
                )

            cap.release()
            out.release()

            st.video(
                output_file
            )


        # ======================
        # HIỂN THỊ THỐNG KÊ
        # ======================

        st.markdown("---")

        c1,c2,c3,c4=st.columns(4)

        c1.metric(
            "👤 Người",
            person_count
        )

        c2.metric(
            "🏍 Xe máy",
            motorbike_count
        )

        c3.metric(
            "⛑ Mũ BH",
            helmet_count
        )

        c4.metric(
            "🚫 Vi phạm",
            violation_count
        )


        if violation_count>0:

            status="Vi phạm"

            st.error(
                f"⚠ Phát hiện {violation_count} người không đội mũ"
            )

        else:

            status="Không vi phạm"

            st.success(
                "✅ Không phát hiện vi phạm"
            )


        # ======================
        # LƯU DATABASE
        # ======================

        cursor.execute(
            """
            INSERT INTO history
            (filename,resultfile,status,time)
            VALUES(?,?,?,?)
            """,
            (
                filename,
                output_file,
                status,
                datetime.now().strftime(
                    "%d/%m/%Y %H:%M"
                )
            )
        )

        conn.commit()


        with open(
            output_file,
            "rb"
        ) as f:

            st.download_button(
                "📥 Tải kết quả",
                f,
                file_name=filename
            )


# =====================
# LỊCH SỬ
# =====================

elif menu=="📁 Lịch sử":

    st.title(
        "📁 Lịch sử nhận diện"
    )

    # =====================
    # Xóa toàn bộ
    # =====================

    if st.button(
        "🧹 Xóa toàn bộ lịch sử"
    ):

        cursor.execute(
            "SELECT resultfile FROM history"
        )

        files=cursor.fetchall()

        for file in files:

            path=file[0]

            if os.path.exists(path):

                os.remove(path)

        cursor.execute(
            "DELETE FROM history"
        )

        conn.commit()

        st.success(
            "✅ Đã xóa toàn bộ"
        )

        st.rerun()


    st.markdown("---")


    # =====================
    # Lấy dữ liệu
    # =====================

    cursor.execute(
        "SELECT * FROM history ORDER BY id DESC"
    )

    rows=cursor.fetchall()


    if len(rows)==0:

        st.warning(
            "Chưa có dữ liệu"
        )

    else:

        for row in rows:

            id,filename,resultfile,status,time=row


            with st.expander(
                f"📄 {filename} | {time}"
            ):

                st.write(
                    f"**Trạng thái:** {status}"
                )


                # =====================
                # Xác định loại file
                # =====================

                ext=filename.split(
                    "."
                )[-1].lower()


                if os.path.exists(
                    resultfile
                ):


                    # Ảnh

                    if ext in [
                        "jpg",
                        "jpeg",
                        "png"
                    ]:

                        st.image(
                            resultfile,
                            width=500
                        )


                    # Video

                    elif ext in [
                        "mp4",
                        "avi",
                        "mov"
                    ]:

                        st.video(
                            resultfile
                        )


                col1,col2=st.columns(
                    2
                )


                # =====================
                # Tải xuống
                # =====================

                with col1:

                    if os.path.exists(
                        resultfile
                    ):

                        with open(
                            resultfile,
                            "rb"
                        ) as f:

                            st.download_button(
                                "📥 Tải xuống",
                                f,
                                file_name=filename,
                                key=f"download{id}"
                            )


                # =====================
                # Xóa riêng
                # =====================

                with col2:

                    if st.button(
                        "🗑 Xóa",
                        key=f"delete{id}"
                    ):

                        if os.path.exists(
                            resultfile
                        ):

                            os.remove(
                                resultfile
                            )

                        cursor.execute(
                            """
                            DELETE FROM history
                            WHERE id=?
                            """,
                            (id,)
                        )

                        conn.commit()

                        st.success(
                            "Đã xóa"
                        )

                        st.rerun()
# =====================
# THỐNG KÊ
# =====================

elif menu=="📊 Thống kê":

    import matplotlib.pyplot as plt

    st.title(
        "📊 Dashboard thống kê hệ thống"
    )


    # ======================
    # Đọc dữ liệu
    # ======================

    data=pd.read_sql_query(
        "SELECT * FROM history",
        conn
    )

    if len(data)==0:

        st.warning(
            "⚠ Chưa có dữ liệu"
        )

        st.stop()


    # ======================
    # Tính dữ liệu
    # ======================

    total=len(data)

    violation=len(
        data[
            data["status"]=="Vi phạm"
        ]
    )

    safe=len(
        data[
            data["status"]=="Không vi phạm"
        ]
    )

    images=0
    videos=0

    for file in data["filename"]:

        ext=file.split(
            "."
        )[-1].lower()

        if ext in [
            "jpg",
            "jpeg",
            "png"
        ]:

            images+=1

        elif ext in [
            "mp4",
            "avi",
            "mov"
        ]:

            videos+=1


    # ======================
    # THẺ THỐNG KÊ
    # ======================

    st.subheader(
        "📌 Tổng quan"
    )

    c1,c2,c3,c4,c5=st.columns(5)

    c1.metric(
        "📂 Tổng",
        total
    )

    c2.metric(
        "🚫 Vi phạm",
        violation
    )

    c3.metric(
        "✅ An toàn",
        safe
    )

    c4.metric(
        "🖼 Ảnh",
        images
    )

    c5.metric(
        "🎥 Video",
        videos
    )


    st.markdown("---")


    # ======================
    # BIỂU ĐỒ
    # ======================

    st.subheader(
        "📈 Phân tích dữ liệu"
    )

    col1,col2=st.columns(
        2
    )


    # ======================
    # Biểu đồ cột
    # ======================

    with col1:

        st.markdown(
            "### 📊 Trạng thái"
        )

        fig1,ax1=plt.subplots(
            figsize=(4,3)
        )

        labels=[
            "Vi phạm",
            "An toàn"
        ]

        values=[
            violation,
            safe
        ]

        ax1.bar(
            labels,
            values,
            color=[
                "#EF5350",
                "#43A047"
            ]
        )

        ax1.set_ylabel(
            "Số lượng"
        )

        st.pyplot(
            fig1
        )


    # ======================
    # Biểu đồ tròn
    # ======================

    with col2:

        st.markdown(
            "### 🥧 Loại dữ liệu"
        )

        fig2,ax2=plt.subplots(
            figsize=(4,3)
        )

        ax2.pie(
            [
                images,
                videos
            ],
            labels=[
                "Ảnh",
                "Video"
            ],
            colors=[
                "#42A5F5",
                "#AB47BC"
            ],
            autopct='%1.1f%%'
        )

        st.pyplot(
            fig2
        )


    st.markdown("---")


    # ======================
    # Bảng dữ liệu
    # ======================

    st.subheader(
        "📋 Lịch sử xử lý"
    )

    show_data=data[
        [
            "filename",
            "status",
            "time"
        ]
    ]

    show_data.columns=[
        "Tên file",
        "Trạng thái",
        "Thời gian"
    ]

    st.dataframe(
        show_data,
        use_container_width=True
    )
