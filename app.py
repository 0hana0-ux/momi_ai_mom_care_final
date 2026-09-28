import streamlit as st
import streamlit.components.v1 as components
from datetime import date, datetime, timedelta
import calendar
import random
import pandas as pd
import altair as alt
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# ==========================================
# 기본 설정
# ==========================================

st.set_page_config(
    page_title="MOMI",
    page_icon="✦",
    layout="centered"
)


# ==========================================
# Session State
# ==========================================

if "page" not in st.session_state:
    st.session_state.page = "signup"

if "mom_name" not in st.session_state:
    st.session_state.mom_name = ""

if "baby_name" not in st.session_state:
    st.session_state.baby_name = ""

if "pregnancy_week" not in st.session_state:
    st.session_state.pregnancy_week = 18

if "due_date" not in st.session_state:
    st.session_state.due_date = date(2027, 1, 20)

# 선택한 주차를 저장
if "selected_week" not in st.session_state:
    st.session_state.selected_week = 18


# ==========================================
# DAILY HEALTH RECORDS
# 날짜별 건강 기록 저장
# ==========================================

if "health_records" not in st.session_state:
    st.session_state.health_records = {}

# ==========================================
# PEER COMPARISON PASTEL COLORS
# 그래프 색상만 파스텔톤으로 통일
# ==========================================

PEER_PINK = "#F6B6D2"
PEER_LAVENDER = "#CDB8F2"
PEER_MINT = "#A9E6D3"
PEER_YELLOW = "#F8D99A"
PEER_BLUE = "#AFCDF4"
PEER_PEACH = "#F6C2A8"
PEER_LEMON = "#F4E6A6"
PEER_LILAC = "#D9C7F2"


# ==========================================
# PEER COMPARISON
# 검진 결과와 같은 임신 주차의 참고 그룹 비교
# ==========================================

if "peer_user_values" not in st.session_state:
    st.session_state.peer_user_values = {}


# ==========================================
# HOSPITAL DATA
# ==========================================

if "hospital_data" not in st.session_state:
    hospital_names = [
        "Seoul Women's Hospital",
        "Mirae Women's Hospital",
        "Harmony Women's Clinic",
        "Bloom Women's Hospital",
        "Grace Women's Hospital",
        "Moms Care Hospital",
        "Bright Hope Women's Clinic",
        "Evergreen Women's Hospital",
        "Pure Heart Women's Clinic",
        "Morning Star Hospital",
        "Little Bloom Women's Hospital",
        "Warm Nest Women's Clinic",
        "Blue Sky Women's Hospital",
        "Gentle Care Women's Clinic",
        "Spring Hope Hospital",
        "Lovely Mom Women's Hospital",
        "Rainbow Women's Clinic",
        "Sunny Days Women's Hospital",
        "Dream Tree Women's Clinic",
        "New Life Women's Hospital"
    ]

    first_names = [
        "Emily", "Sarah", "Daniel", "Olivia", "Sophia", "James",
        "Grace", "Michael", "Emma", "Noah", "Hannah", "Ethan",
        "Chloe", "Lucas", "Mia", "Henry", "Ella", "David",
        "Lily", "Alex", "Sophie", "Ryan", "Anna", "Leo",
        "Claire", "Matthew", "Julia", "Andrew", "Lucy", "William"
    ]

    last_names = [
        "Kim", "Lee", "Park", "Choi", "Jung", "Kang", "Han", "Yoon",
        "Lim", "Shin", "Seo", "Moon", "Kwon", "Baek", "Song", "Oh",
        "Hwang", "Ryu", "Jeon", "Jang"
    ]

    time_pool = [
        "09:00", "09:30", "10:00", "10:30", "11:00", "11:30",
        "13:00", "13:30", "14:00", "14:30", "15:00", "15:30",
        "16:00", "16:30", "17:00"
    ]

    rng = random.Random(20260921)
    generated_hospitals = {}
    available_dates = [date.today() + timedelta(days=i) for i in range(2, 46)]

    name_index = 0

    for hospital in hospital_names:
        doctors = []

        for doctor_number in range(4):
            first = first_names[name_index % len(first_names)]
            last = last_names[(name_index * 3 + doctor_number) % len(last_names)]
            name_index += 1

            doctor_schedule = {}
            selected_dates = sorted(rng.sample(available_dates, 9))

            for available_date in selected_dates:
                selected_times = sorted(rng.sample(time_pool, 3))
                doctor_schedule[available_date.isoformat()] = selected_times

            doctors.append({
                "name": f"Dr. {first} {last}",
                "specialty": "Obstetrics & Gynecology",
                "schedule": doctor_schedule
            })

        generated_hospitals[hospital] = doctors

    st.session_state.hospital_data = generated_hospitals

if "appointments" not in st.session_state:
    st.session_state.appointments = []

# Simple hospital contact information for Hospital Messages
# The existing hospital_data structure is kept unchanged.
if "hospital_contact_data" not in st.session_state:
    hospital_contact_data = {}

    hospital_addresses = [
        "12 Harmony-ro, Seoul", "28 Mirae-gil, Seoul", "41 Harmony-ro, Seoul",
        "7 Bloom-ro, Seoul", "19 Grace-gil, Seoul", "33 Care-ro, Seoul",
        "52 Hope-gil, Seoul", "16 Evergreen-ro, Seoul", "24 Pure Heart-gil, Seoul",
        "9 Morning Star-ro, Seoul", "38 Little Bloom-gil, Seoul", "21 Warm Nest-ro, Seoul",
        "45 Blue Sky-gil, Seoul", "14 Gentle Care-ro, Seoul", "31 Spring Hope-gil, Seoul",
        "26 Lovely Mom-ro, Seoul", "18 Rainbow-gil, Seoul", "40 Sunny Days-ro, Seoul",
        "11 Dream Tree-gil, Seoul", "35 New Life-ro, Seoul"
    ]

    hospital_services = [
        "Maternity Care, Prenatal Checkups, Ultrasound",
        "Maternity Care, Prenatal Checkups, Laboratory Tests",
        "Maternity Care, Prenatal Checkups, Ultrasound",
        "Maternity Care, Prenatal Checkups, Birth Preparation",
        "Maternity Care, Prenatal Checkups, Ultrasound",
        "Maternity Care, Prenatal Checkups, Newborn Care",
        "Maternity Care, Prenatal Checkups, Laboratory Tests",
        "Maternity Care, Prenatal Checkups, Ultrasound",
        "Maternity Care, Prenatal Checkups, Birth Preparation",
        "Maternity Care, Prenatal Checkups, Ultrasound",
        "Maternity Care, Prenatal Checkups, Newborn Care",
        "Maternity Care, Prenatal Checkups, Laboratory Tests",
        "Maternity Care, Prenatal Checkups, Ultrasound",
        "Maternity Care, Prenatal Checkups, Birth Preparation",
        "Maternity Care, Prenatal Checkups, Ultrasound",
        "Maternity Care, Prenatal Checkups, Newborn Care",
        "Maternity Care, Prenatal Checkups, Laboratory Tests",
        "Maternity Care, Prenatal Checkups, Ultrasound",
        "Maternity Care, Prenatal Checkups, Birth Preparation",
        "Maternity Care, Prenatal Checkups, Ultrasound"
    ]

    for index, hospital in enumerate(st.session_state.hospital_data.keys()):
        hospital_contact_data[hospital] = {
            "address": hospital_addresses[index],
            "phone": f"02-5{index + 1:02d}-2{index + 1:03d}",
            "services": hospital_services[index]
        }

    st.session_state.hospital_contact_data = hospital_contact_data

if "personal_schedules" not in st.session_state:
    st.session_state.personal_schedules = {}

if "hospital_selected_hospital" not in st.session_state:
    st.session_state.hospital_selected_hospital = None

if "hospital_selected_doctor" not in st.session_state:
    st.session_state.hospital_selected_doctor = None

if "hospital_selected_date" not in st.session_state:
    st.session_state.hospital_selected_date = None

if "hospital_selected_time" not in st.session_state:
    st.session_state.hospital_selected_time = None

if "schedule_month" not in st.session_state:
    st.session_state.schedule_month = date.today().replace(day=1)

if "schedule_selected_date" not in st.session_state:
    st.session_state.schedule_selected_date = date.today()


# ==========================================
# MILESTONE DATA
# 1~40주
# ==========================================

milestones = {

    1: {
        "baby": "This is the beginning of the pregnancy timeline. The body is preparing for ovulation and a possible pregnancy. Pregnancy weeks are counted from the first day of the last menstrual period.",
        "mom": "Start building healthy habits with folate-rich vegetables, fruits, beans, and whole grains. Regular sleep, hydration, and gentle daily movement can help prepare your body.",
        "message": "Every beautiful journey starts with a first little step. 🌷"
    },

    2: {
        "baby": "Ovulation may occur around this time, and fertilization can happen during this part of the cycle. The baby's organs have not yet formed; this is the very beginning of the pregnancy timeline.",
        "mom": "Continue taking folic acid if recommended for you, and choose balanced meals throughout the day. Avoid alcohol and smoking, and check any regular medications with your healthcare provider.",
        "message": "Something wonderful may be just beginning. Take it one day at a time. ✦"
    },

    3: {
        "baby": "If fertilization has occurred, the cells begin dividing rapidly as the early embryo develops. The cells start organizing into structures that will later form the baby and placenta.",
        "mom": "Keep folate-rich foods such as leafy greens, beans, and citrus fruits in your meals. If you feel tired or nauseous, small meals and regular hydration may feel easier.",
        "message": "A tiny beginning can lead to something truly amazing. 💕"
    },

    4: {
        "baby": "The early embryo may attach to the lining of the uterus during this stage. Cells begin taking on different roles that will eventually form the baby's body and supporting tissues.",
        "mom": "If pregnancy is confirmed, begin planning your prenatal care. Choose a variety of vegetables, fruits, whole grains, and protein foods while giving yourself plenty of gentle rest.",
        "message": "A tiny new beginning is finding its place. 🌸"
    },

    5: {
        "baby": "The early brain and spinal cord begin developing from the neural tube. The heart and digestive system also start forming, making this an important stage for early organ development.",
        "mom": "Folate is especially important during early pregnancy because it supports neural tube development. Try leafy greens, beans, fortified grains, and a prenatal supplement if recommended.",
        "message": "Some of your baby's first important structures are beginning to form. 🌱"
    },

    6: {
        "baby": "The early brain continues to develop, and the heart begins its early rhythmic activity. Small structures that will become the eyes, ears, arms, and legs are also starting to appear.",
        "mom": "If nausea is bothering you, try small meals such as crackers, bananas, rice, or toast. Sip water regularly and give yourself extra time to rest when your energy feels low.",
        "message": "A tiny heart and developing nervous system are already hard at work. 💗"
    },

    7: {
        "baby": "The brain and facial structures continue developing, while the early spine and bones begin taking shape. The tiny limb buds are becoming more defined.",
        "mom": "Include protein foods such as eggs, tofu, beans, or lean meat in your meals. If you feel comfortable, a short gentle walk can be a refreshing way to move your body.",
        "message": "Your baby's little face and body are slowly taking shape. 🌷"
    },

    8: {
        "baby": "The arms and legs become longer, and the hands and feet begin taking clearer shape. The brain continues rapid development, while the early lungs also begin forming.",
        "mom": "Enjoy a colorful mix of fruits and vegetables along with protein-rich foods. You can also spend a few quiet minutes listening to music or talking gently to your baby.",
        "message": "Tiny hands and feet are beginning to take shape. 🍼"
    },

    9: {
        "baby": "The elbows, fingers, and toes become more recognizable as muscles and joints continue developing. Most major organs have begun forming and are now growing and becoming more organized.",
        "mom": "Choose iron-containing foods such as lean meat, beans, spinach, and fortified grains. Pairing a variety of vegetables and fruits with meals can help you enjoy a wider range of nutrients.",
        "message": "Your baby's little body is becoming more recognizable every day. ✨"
    },

    10: {
        "baby": "The eyelids, outer ears, and facial features become more defined. The digestive system continues developing, and the embryo has now entered the fetal stage of development.",
        "mom": "Keep regular meals and hydration part of your routine. If you have prenatal appointments coming up, write down questions and bring a list of medications or supplements you take.",
        "message": "Your little one is beginning to look more and more like a tiny baby. 🌸"
    },

    11: {
        "baby": "The fingers and toes are clearly separated, while facial features continue to develop. The liver and blood-forming systems are becoming more active, and early tooth structures begin developing.",
        "mom": "Include iron and protein through foods such as lean meat, eggs, beans, and leafy greens. Add colorful fruits and vegetables to make meals both nutritious and enjoyable.",
        "message": "Even tiny fingers and toes are taking shape. 🌷"
    },

    12: {
        "baby": "The fingers and toes continue to develop, and the baby can make small movements. The brain and nervous system are becoming more organized as the body learns to coordinate movement.",
        "mom": "Calcium-rich foods such as milk, yogurt, tofu, or fortified alternatives can be useful choices. Relax with a favorite book or gentle music when you need a quiet moment.",
        "message": "You've made it through an important early stage. You're doing beautifully. 💕"
    },

    13: {
        "baby": "Bones and muscles continue developing, making the arms and legs stronger. Facial proportions also begin changing as the head and body gradually become more balanced.",
        "mom": "Choose meals that combine protein and calcium, such as tofu, eggs, yogurt, or beans. If your energy allows, enjoy a gentle walk and a little fresh air.",
        "message": "Your baby's little body is becoming stronger and more defined. 🌱"
    },

    14: {
        "baby": "The face and neck become more developed, while bones and muscles continue growing. The nervous system is also developing the connections needed for future movement and coordination.",
        "mom": "Whole grains, vegetables, and fruits can provide useful fiber and nutrients. Take a relaxed walk, listen to music, or talk softly to your baby during a peaceful moment.",
        "message": "A new chapter of growth is beginning. 🌸"
    },

    15: {
        "baby": "Bones continue becoming stronger, while muscles and joints allow the arms and legs to move more naturally. The skin is still very thin and continues developing its protective layers.",
        "mom": "Include calcium and protein through foods such as yogurt, tofu, eggs, beans, and fish that are appropriate during pregnancy. Try a relaxing playlist while resting.",
        "message": "Your baby is practicing little movements inside. ✦"
    },

    16: {
        "baby": "Bones, joints, and muscles continue developing, allowing a wider range of movement. Facial muscles are also developing, creating the foundations for future expressions and movements.",
        "mom": "Keep meals balanced with iron, protein, vegetables, and whole grains. Gentle stretching or a short walk can help you stay comfortably active if your healthcare provider has no restrictions.",
        "message": "Your little one is learning how to move and grow. 🍼"
    },

    17: {
        "baby": "Bones continue to develop, and the body begins storing small amounts of fat. Structures involved in hearing are also developing as the baby becomes more prepared to receive sounds.",
        "mom": "Foods containing omega-3 fatty acids, such as pregnancy-safe fish, can be part of a balanced diet. Check local pregnancy fish guidelines and enjoy calming music during your quiet time.",
        "message": "Your baby is preparing not only to grow, but also to experience the world. 🎵"
    },

    18: {
        "baby": "The nervous system and muscles continue connecting, allowing the baby's movements to become more active. The ears are developing further and becoming better prepared to receive sounds.",
        "mom": "Include iron, protein, vegetables, and fruits throughout your meals. Try reading a short book aloud or telling your baby about your day.",
        "message": "Your voice and your baby's growing world are getting closer every day. 💗"
    },

    19: {
        "baby": "Hearing structures continue developing, helping the baby become more responsive to sounds. The skin develops further and is covered by a protective coating that helps protect it from the surrounding fluid.",
        "mom": "Choose calcium-rich and protein-rich foods such as yogurt, tofu, eggs, or beans. Take a gentle walk, listen to calming music, or simply enjoy a few peaceful minutes together.",
        "message": "Your baby is slowly getting ready to hear the world around them. 🎶"
    },

    20: {
        "baby": "The brain and nervous system continue developing, while the baby's movements become more coordinated. Swallowing and digestive movements are also being practiced as the body learns new functions.",
        "mom": "Keep meals balanced with iron, calcium, protein, fruits, and vegetables. Check your prenatal appointment schedule and make time for gentle movement and comfortable rest.",
        "message": "You're halfway through this beautiful journey. Look how far you've come. 🌷"
    },

    21: {
        "baby": "The baby's hearing continues developing, making sounds easier to receive. The digestive system also practices swallowing as the baby becomes more familiar with basic body functions.",
        "mom": "Try protein-rich foods such as eggs, tofu, beans, and lean meat with plenty of vegetables. Reading aloud or talking softly to your baby can become a relaxing daily ritual.",
        "message": "Your little one is beginning to experience more of your world. 💕"
    },

    22: {
        "baby": "Eyebrows and eyelashes become more visible, while fingernails continue growing. Muscles are becoming stronger, and the digestive system continues practicing important movements.",
        "mom": "Include iron-rich foods such as lean meat, beans, and leafy greens, along with enough water. If you've been sitting for a long time, change positions and gently move your body.",
        "message": "Tiny eyebrows, eyelashes, and nails are appearing. How amazing is that? 🌸"
    },

    23: {
        "baby": "The bone marrow becomes more involved in making blood cells, while the airways and structures of the lungs continue developing. Fat begins accumulating under the skin.",
        "mom": "Combine iron-rich foods with colorful fruits and vegetables. A short bedtime story or calming music can be a simple way to create a peaceful routine.",
        "message": "Your baby is practicing one tiny function after another. 🌱"
    },

    24: {
        "baby": "The airways and air sacs in the lungs continue to develop, while the nervous system grows rapidly. The lungs are preparing for breathing after birth, although they are still developing.",
        "mom": "Choose balanced meals with protein and iron, such as eggs, beans, lean meat, and leafy greens. Stay hydrated and enjoy a gentle walk or light stretching if you feel comfortable.",
        "message": "Your baby's little lungs are getting ready for their first breath. 🫶"
    },

    25: {
        "baby": "The small airways and blood vessels in the lungs continue developing. Bones and muscles grow steadily, while more fat begins forming under the skin.",
        "mom": "Include protein and omega-3-rich foods such as eggs, beans, and pregnancy-safe fish when appropriate. Read a favorite book aloud and enjoy a calm moment with your baby.",
        "message": "Your baby is quietly preparing for life outside the womb. ✨"
    },

    26: {
        "baby": "The eyes continue developing, while eyebrows and eyelashes become more noticeable. Unique fingerprints are forming, and the lungs continue preparing for breathing.",
        "mom": "Choose meals with calcium, protein, vegetables, and fruit. You can listen to music together, talk to your baby, or simply relax with your hands resting comfortably on your belly.",
        "message": "Even tiny fingerprints are becoming uniquely your baby's. 🍼"
    },

    27: {
        "baby": "The brain grows rapidly and the nervous system becomes better at coordinating body functions. The eyelids can open and close, while the lungs continue their long process of maturation.",
        "mom": "Keep iron and protein-rich foods in your regular meals. Try creating a calming bedtime routine with gentle music, comfortable lighting, and enough time for sleep.",
        "message": "Your baby's brain and nervous system are growing so quickly. 🌷"
    },

    28: {
        "baby": "The baby can open and close the eyes, while brain development becomes increasingly active. The lungs continue developing important structures needed for breathing after birth.",
        "mom": "As the third trimester begins, keep up with prenatal visits and recommended checks. Continue balanced meals with iron, calcium, and protein while making room for plenty of rest.",
        "message": "You've reached another beautiful milestone. The final chapter is beginning. 💗"
    },

    29: {
        "baby": "The brain and nervous system continue forming more complex connections, helping control movement and body functions. The lungs keep maturing as the baby practices movements related to breathing.",
        "mom": "Enjoy iron-rich foods such as beans, leafy greens, and lean meat along with fruits and vegetables. A gentle walk or favorite music can help make your daily routine feel lighter.",
        "message": "Your baby is getting ready for a whole new world, one step at a time. 🌸"
    },

    30: {
        "baby": "The brain continues rapid growth and becomes increasingly involved in coordinating movement and body functions. The lungs and eyes also continue developing as the baby prepares for life after birth.",
        "mom": "Keep protein and calcium in your meals and drink water regularly. You can slowly organize baby supplies and create a comfortable space for the weeks ahead.",
        "message": "The day you'll meet your baby is getting closer. ✦"
    },

    31: {
        "baby": "The baby continues gaining weight and storing fat under the skin. Bones keep developing, while the lungs practice rhythmic movements that prepare the body for breathing.",
        "mom": "Choose meals with iron, protein, vegetables, and whole grains. Change positions regularly and take comfortable breaks if sitting or standing for long periods feels tiring.",
        "message": "Your baby is building a cozy little body for the outside world. 🍼"
    },

    32: {
        "baby": "The brain and nervous system continue maturing, while the lungs make steady progress toward greater function. More body fat develops, making the skin appear smoother.",
        "mom": "Include calcium-rich foods such as yogurt, milk, tofu, or fortified alternatives along with protein. Choose a favorite song or story to share during a quiet evening.",
        "message": "Your baby's little body is becoming softer, stronger, and more ready. 🌷"
    },

    33: {
        "baby": "The brain and nervous system continue developing, and the lungs keep maturing for life after birth. Increasing body fat helps the baby prepare to regulate body temperature.",
        "mom": "Keep iron and protein in your daily meals and drink enough water. Check your hospital plan, important contacts, and baby supplies so you can feel more prepared.",
        "message": "The final preparations are quietly happening inside and outside. 💕"
    },

    34: {
        "baby": "Bones and muscles continue developing while the baby stores more fat. The lungs keep maturing, and rhythmic breathing movements continue as the baby prepares for birth.",
        "mom": "Choose balanced meals with protein, vegetables, calcium, and iron. Gentle walks and comfortable rest can help you care for your changing body.",
        "message": "Your baby is getting closer to being ready for the big day. 🌸"
    },

    35: {
        "baby": "More fat develops under the skin, making the baby's appearance rounder and smoother. The heart and blood vessels are well developed, while muscles and bones continue growing.",
        "mom": "Keep protein and calcium-rich foods in your meals and drink water regularly. Start checking your hospital bag and make sure important items are easy to find.",
        "message": "Your little one is beginning to look more like the newborn you'll soon meet. 🍼"
    },

    36: {
        "baby": "The baby continues gaining weight and storing fat for life outside the womb. Brain development continues, and the baby's sleep and wake patterns become more noticeable.",
        "mom": "Keep meals balanced with iron, calcium, protein, fruits, and vegetables. Review your prenatal appointments and make your daily routine as comfortable and restful as possible.",
        "message": "You're getting so close now. Both of you are preparing beautifully. 🌷"
    },

    37: {
        "baby": "The baby's major body systems are prepared for life after birth, while the brain and lungs continue developing. More fat is stored under the skin as the baby becomes rounder.",
        "mom": "Continue regular meals, hydration, and comfortable activity. Review your route to the hospital, important phone numbers, and your birth bag so everything is ready.",
        "message": "The moment you've been waiting for is getting very close. 💗"
    },

    38: {
        "baby": "The baby continues gaining weight and storing body fat. Fingernails may extend beyond the fingertips, while the skin, hair, and other features continue changing as birth approaches.",
        "mom": "Choose easy-to-digest balanced meals with protein, vegetables, and fruit, and keep drinking water. Keep your hospital bag nearby and give yourself plenty of quiet rest.",
        "message": "Your little one is almost ready to meet you. 🌸"
    },

    39: {
        "baby": "The brain and nervous system continue developing even as the baby is well prepared for birth. More fat is stored under the skin, helping the baby prepare for life outside the womb.",
        "mom": "Continue eating regular balanced meals and staying hydrated. Keep your hospital information and important supplies ready, and contact your healthcare provider if you have questions about changes you notice.",
        "message": "Just a little more waiting. Your meeting is almost here. 🫶"
    },

    40: {
        "baby": "At around 40 weeks, the baby is ready for birth and continues preparing for life outside the womb. The brain and lungs keep developing while the body maintains healthy fat stores.",
        "mom": "Keep eating balanced meals, drinking enough water, and resting comfortably. Follow your prenatal care plan and contact your healthcare provider with questions about labor signs or changes you notice.",
        "message": "Forty weeks of growing, waiting, and loving. Your beautiful journey has brought you here. 💕"
    }
}


# ==========================================
# CSS
# 기존 디자인 그대로
# ==========================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Baloo+2:wght@400;500;600;700;800&family=Fredoka:wght@400;500;600;700&display=swap');

.stApp {
    background:
        radial-gradient(
            circle at 10% 10%,
            #FFE5F0 0%,
            transparent 25%
        ),
        radial-gradient(
            circle at 90% 20%,
            #E8DFFF 0%,
            transparent 25%
        ),
        radial-gradient(
            circle at 20% 90%,
            #DFF7F0 0%,
            transparent 25%
        ),
        linear-gradient(
            180deg,
            #FFF9FC 0%,
            #F9F3FC 100%
        );
}

* {
    font-family:
        'Baloo 2',
        sans-serif;
}

.block-container {
    max-width: 720px;
    padding-top: 35px;
    padding-bottom: 70px;
}

h1,
h2,
h3 {
    font-family:
        'Fredoka',
        sans-serif !important;

    color: #735579 !important;

    text-align: center;
}

.stMarkdown,
.stCaption {
    text-align: center;
}

.logo {
    text-align: center;

    font-family:
        'Fredoka',
        sans-serif;

    font-size: 24px;

    font-weight: 700;

    letter-spacing: 3px;

    color: #B87FA8;

    margin-bottom: 0;
}

.subtitle {
    text-align: center;

    font-size: 14px;

    font-weight: 600;

    letter-spacing: 2px;

    color: #A98DAE;
}

.stTextInput,
.stNumberInput,
.stDateInput,
.stSelectbox,
.stSlider {
    text-align: center;
}

.stTextInput label,
.stNumberInput label,
.stDateInput label,
.stSelectbox label,
.stSlider label {
    text-align: center !important;

    width: 100%;

    font-family:
        'Fredoka',
        sans-serif !important;

    color: #85678C !important;

    font-size: 15px !important;
}

.stTextInput input,
.stNumberInput input,
.stDateInput input {
    border-radius: 18px !important;

    border:
        3px solid #E8D4E7 !important;

    background:
        rgba(255,255,255,0.9) !important;

    text-align: center !important;

    font-family:
        'Baloo 2',
        sans-serif !important;

    font-size: 16px !important;
}

.stButton {
    text-align: center;
}

.stButton > button {
    width: 100%;

    border: none;

    border-radius: 22px;

    padding: 16px;

    font-family:
        'Fredoka',
        sans-serif !important;

    font-size: 18px;

    font-weight: 600;

    letter-spacing: 1px;

    color: white;

    background:
        linear-gradient(
            135deg,
            #F29AC2,
            #C5A5E8
        );

    box-shadow:
        0 8px 20px
        rgba(190,140,200,0.25);
}

.stButton > button:hover {
    transform: translateY(-2px);

    color: white;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    background:
        rgba(255,255,255,0.78);

    border:
        4px solid
        #E3CBE4 !important;

    border-radius:
        25px !important;

    box-shadow:
        0 8px 20px
        rgba(130,90,140,0.08);

    padding:
        8px;
}

div[data-testid="stVerticalBlockBorderWrapper"] p {
    text-align: center;

    color: #735F76;

    font-size: 15px;
}

.stCaption {
    color: #A88AAA !important;

    font-family:
        'Fredoka',
        sans-serif !important;

    font-weight: 500;
}

div[data-testid="stVerticalBlockBorderWrapper"]
h1 {
    font-size: 60px !important;

    color: #C47EAB !important;

    margin: 0;
}

hr {
    border:
        none;

    border-top:
        2px dashed
        #E6D4E7;
}

.stAlert {
    border-radius: 20px;
}

div[data-testid="stHorizontalBlock"] .stButton > button {
    font-size: 14px !important;

    padding: 12px 4px !important;

    min-height: 65px;

    white-space: pre-line;
}

@media (max-width: 700px) {
    .block-container {
        padding-left: 25px;
        padding-right: 25px;
    }
}

</style>
""", unsafe_allow_html=True)

# ==========================================
# HANA · Microsoft Trainee WATERMARK
# 모든 페이지에서 오른쪽 아래에 고정 표시
# ==========================================

st.markdown("""
<style>
.momi-hana-watermark {
    position: fixed;
    right: 14px;
    bottom: 10px;
    z-index: 999999;
    font-family: 'Fredoka', sans-serif;
    font-size: 10px;
    font-weight: 500;
    letter-spacing: 0.4px;
    color: #9E8FA3;
    opacity: 0.48;
    pointer-events: none;
    user-select: none;
    white-space: nowrap;
}

@media (max-width: 700px) {
    .momi-hana-watermark {
        right: 8px;
        bottom: 7px;
        font-size: 9px;
        opacity: 0.42;
    }
}
</style>
<div class="momi-hana-watermark">HANA · Microsoft Trainee</div>
""", unsafe_allow_html=True)



# ==========================================
# MOMI 캐릭터
# ==========================================

def show_momi():

    momi_svg = """
    <!DOCTYPE html>

    <html>

    <head>

    <style>

    body {
        margin: 0;
        padding: 0;
        background: transparent;
        display: flex;
        justify-content: center;
        align-items: center;
    }

    </style>

    </head>

    <body>

    <svg
        width="280"
        height="280"
        viewBox="0 0 280 280"
        xmlns="http://www.w3.org/2000/svg"
    >

        <circle
            cx="140"
            cy="140"
            r="120"
            fill="#F8EFF9"
        />

        <text
            x="48"
            y="80"
            font-size="22"
            fill="#B9A4D8"
        >✦</text>

        <text
            x="205"
            y="92"
            font-size="18"
            fill="#E5A9C7"
        >✧</text>

        <text
            x="215"
            y="195"
            font-size="21"
            fill="#B9A4D8"
        >✦</text>

        <text
            x="50"
            y="198"
            font-size="16"
            fill="#E5A9C7"
        >✧</text>

        <line
            x1="140"
            y1="88"
            x2="140"
            y2="65"
            stroke="#B9A4D8"
            stroke-width="3"
            stroke-linecap="round"
        />

        <circle
            cx="140"
            cy="60"
            r="6"
            fill="#E5A9C7"
        />

        <circle
            cx="94"
            cy="105"
            r="25"
            fill="#E7D8EE"
        />

        <circle
            cx="186"
            cy="105"
            r="25"
            fill="#E7D8EE"
        />

        <circle
            cx="94"
            cy="105"
            r="13"
            fill="#F3CFE0"
        />

        <circle
            cx="186"
            cy="105"
            r="13"
            fill="#F3CFE0"
        />

        <ellipse
            cx="140"
            cy="168"
            rx="59"
            ry="69"
            fill="#E7D7EE"
        />

        <circle
            cx="140"
            cy="135"
            r="48"
            fill="#FFF8FB"
        />

        <circle
            cx="123"
            cy="132"
            r="5"
            fill="#69566B"
        />

        <circle
            cx="157"
            cy="132"
            r="5"
            fill="#69566B"
        />

        <ellipse
            cx="113"
            cy="151"
            rx="11"
            ry="6"
            fill="#F1BBD0"
        />

        <ellipse
            cx="167"
            cy="151"
            rx="11"
            ry="6"
            fill="#F1BBD0"
        />

        <path
            d="M130 151 Q140 160 150 151"
            stroke="#69566B"
            stroke-width="3"
            fill="none"
            stroke-linecap="round"
        />

        <text
            x="140"
            y="207"
            text-anchor="middle"
            font-size="27"
            fill="#D88EAF"
        >♡</text>

    </svg>

    </body>

    </html>
    """

    components.html(
        momi_svg,
        height=290,
        scrolling=False
    )


# ==========================================
# SIGN UP
# ==========================================

def show_signup():

    st.markdown(
        '<div class="logo">✦ MOMI ✦</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">MOM CARE AI</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        "# 40 WEEK ADVENTURE"
    )

    st.caption(
        "Your gentle AI companion throughout pregnancy"
    )

    show_momi()

    mom_name = st.text_input(
        "Mom Name",
        value=st.session_state.mom_name,
        placeholder="Enter your name"
    )

    baby_name = st.text_input(
        "Baby Name",
        value=st.session_state.baby_name,
        placeholder="Enter your baby name"
    )

    pregnancy_week = st.number_input(
        "Pregnancy Week",
        min_value=1,
        max_value=40,
        value=st.session_state.pregnancy_week
    )

    due_date = st.date_input(
        "Due Date",
        value=st.session_state.due_date,
        min_value=date(2026, 1, 1),
        max_value=date(2030, 12, 31)
    )

    st.write("")

    if st.button("START ✦"):

        st.session_state.mom_name = mom_name
        st.session_state.baby_name = baby_name
        st.session_state.pregnancy_week = pregnancy_week
        st.session_state.due_date = due_date

        st.session_state.selected_week = pregnancy_week

        st.session_state.page = "home"

        st.rerun()


# ==========================================
# HOME
# ==========================================

def show_home():

    mom_name = st.session_state.mom_name
    baby_name = st.session_state.baby_name
    week = st.session_state.pregnancy_week
    due_date = st.session_state.due_date

    st.markdown(
        '<div class="logo">✦ MOMI ✦</div>',
        unsafe_allow_html=True
    )

    st.caption(
        f"Good morning, {mom_name} 🌷"
    )

    st.markdown(
        f"# Baby {baby_name}"
    )

    st.caption(
        f"Your pregnancy journey · Week {week}"
    )

    show_momi()

    with st.container(border=True):

        st.caption("CURRENT WEEK")

        st.markdown(
            f"# {week}"
        )

        st.caption("OF 40 WEEKS")

    st.write("")

    col1, col2 = st.columns(2)

    with col1:

        with st.container(border=True):

            st.caption("🌸 HEALTH")

            st.write("Sleep · 7.2 h")
            st.write("Stress · ●●○○○")
            st.write("Exercise · 30 min")

    with col2:

        with st.container(border=True):

            st.caption("🍼 BABY")

            st.write("Growth looks good")
            st.write("Weekly milestone")
            st.write("✦ Keep going")

    st.write("")

    with st.container(border=True):

        st.caption("🌷 TODAY'S MILESTONE")

        st.write(
            "Baby is growing every day."
        )

        st.write(
            "Take a little time to rest,"
        )

        st.write(
            "hydrate and listen to your body."
        )

    st.write("")

    with st.container(border=True):

        st.caption("✨ AI CONSULTANT")

        st.write(
            "You're doing beautifully."
        )

        st.write(
            "Let's take care of you and baby,"
        )

        st.write(
            "one day at a time."
        )

    st.write("")

    with st.container(border=True):

        st.caption("🎀 DUE DATE")

        st.write(
            due_date.strftime("%B %d, %Y")
        )

    st.write("")

    if st.button("EDIT PROFILE"):

        st.session_state.page = "signup"

        st.rerun()

    st.write("")

    if st.button("WELCOME 🌷"):

        st.session_state.page = "welcome"

        st.rerun()


# ==========================================
# WELCOME
# ==========================================

def show_welcome():

    st.markdown(
        '<div class="logo">✦ MOMI ✦</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        "# Welcome 🌷"
    )

    st.caption(
        "Your pregnancy journey starts here."
    )

    show_momi()

    st.write("")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:

        if st.button(
            "🌷\nTODAY",
            use_container_width=True
        ):

            st.session_state.page = "today"

            st.rerun()

    with col2:

        if st.button(
            "🌸\nHEALTH",
            use_container_width=True
        ):

            st.session_state.page = "health"

            st.rerun()

    with col3:

        if st.button(
            "🍼\nMILESTONE",
            use_container_width=True
        ):

            st.session_state.page = "milestone"

            st.rerun()

    with col4:

        if st.button(
            "✨\nAI",
            use_container_width=True
        ):

            st.session_state.page = "ai"

            st.rerun()

    with col5:

        if st.button(
            "🏥\nHOSPITAL",
            use_container_width=True
        ):

            st.session_state.page = "hospital"

            st.rerun()


# ==========================================
# TODAY
# ==========================================

def show_today():

    st.markdown(
        '<div class="logo">✦ MOMI ✦</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        "# 🌷 Today"
    )

    st.caption(
        "Your daily pregnancy journey"
    )

    show_momi()

    st.write("")

    col1, col2, col3 = st.columns(3)

    with col1:

        if st.button(
            "📝 Daily Health Check",
            use_container_width=True
        ):

            st.session_state.page = "daily_health"

            st.rerun()

    with col2:

        if st.button(
            "🌸 Weekly Milestone",
            use_container_width=True
        ):

            st.session_state.selected_week = st.session_state.pregnancy_week

            st.session_state.page = "weekly_milestone"

            st.rerun()

    with col3:

        if st.button(
            "🏥 Next Hospital Visit",
            use_container_width=True
        ):

            st.session_state.page = "next_hospital"

            st.rerun()

    st.write("")

    if st.button("← BACK TO HOME"):

        st.session_state.page = "home"

        st.rerun()


# ==========================================
# 📝 DAILY HEALTH CHECK
# ==========================================

def show_daily_health():

    st.markdown(
        '<div class="logo">✦ MOMI ✦</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        "# 📝 Daily Health Check"
    )

    st.caption(
        "Take a little moment to check in with yourself"
    )

    show_momi()

    st.write("")

    # ------------------------------------------
    # 날짜
    # ------------------------------------------

    check_date = st.date_input(
        "Check Date",
        value=date.today(),
        key="daily_check_date"
    )

    date_key = check_date.isoformat()

    existing = st.session_state.health_records.get(date_key, {})

    st.write("")

    # ------------------------------------------
    # BODY
    # ------------------------------------------

    with st.container(border=True):

        st.markdown("### 🩷 BODY")

        weight = st.number_input(
            "Weight (kg)",
            min_value=30.0,
            max_value=200.0,
            value=float(existing.get("weight", 60.0)),
            step=0.1
        )

    st.write("")

    # ------------------------------------------
    # LIFESTYLE
    # ------------------------------------------

    with st.container(border=True):

        st.markdown("### 🌿 LIFESTYLE")

        sleep = st.number_input(
            "😴 Sleep (hours)",
            min_value=0.0,
            max_value=24.0,
            value=float(existing.get("sleep", 7.0)),
            step=0.1
        )

        water = st.selectbox(
            "💧 Water",
            ["0–2 cups", "3–4 cups", "5–6 cups", "7–8 cups", "9+ cups"],
            index=[
                "0–2 cups",
                "3–4 cups",
                "5–6 cups",
                "7–8 cups",
                "9+ cups"
            ].index(existing.get("water", "5–6 cups"))
        )

        meals = st.selectbox(
            "🍚 Meals",
            ["0 meals", "1 meal", "2 meals", "3 meals", "4+ meals"],
            index=[
                "0 meals",
                "1 meal",
                "2 meals",
                "3 meals",
                "4+ meals"
            ].index(existing.get("meals", "3 meals"))
        )

        healthy_food = st.selectbox(
            "🥗 Healthy Food",
            [
                "Not today",
                "A little",
                "Balanced meal"
            ],
            index=[
                "Not today",
                "A little",
                "Balanced meal"
            ].index(existing.get("healthy_food", "A little"))
        )

        exercise = st.selectbox(
            "🏃‍♀️ Exercise",
            [
                "None",
                "10–20 min",
                "20–40 min",
                "40+ min"
            ],
            index=[
                "None",
                "10–20 min",
                "20–40 min",
                "40+ min"
            ].index(existing.get("exercise", "None"))
        )

        pregnancy_learning = st.checkbox(
            "📚 I learned something about pregnancy today",
            value=bool(existing.get("pregnancy_learning", False))
        )

        baby_bonding = st.checkbox(
            "🎵 I spent a little time bonding with my baby",
            value=bool(existing.get("baby_bonding", False))
        )

    st.write("")

    # ------------------------------------------
    # FEELINGS
    # ------------------------------------------

    with st.container(border=True):

        st.markdown("### 💕 FEELINGS")

        mood = st.selectbox(
            "😊 Mood",
            [
                "😄 Great",
                "🙂 Good",
                "😐 Okay",
                "😟 Worried",
                "😢 Low"
            ],
            index=[
                "😄 Great",
                "🙂 Good",
                "😐 Okay",
                "😟 Worried",
                "😢 Low"
            ].index(existing.get("mood", "🙂 Good"))
        )

        energy = st.selectbox(
            "⚡ Energy",
            [
                "⚡ High",
                "🙂 Normal",
                "🥱 Low"
            ],
            index=[
                "⚡ High",
                "🙂 Normal",
                "🥱 Low"
            ].index(existing.get("energy", "🙂 Normal"))
        )

        stress = st.slider(
            "😰 Stress",
            min_value=1,
            max_value=5,
            value=int(existing.get("stress", 2)),
            help="1 = very relaxed · 5 = very stressed"
        )

    st.write("")

    # ------------------------------------------
    # SAVE
    # ------------------------------------------

    if st.button(
        "💾 SAVE TODAY'S CHECK",
        use_container_width=True
    ):

        st.session_state.health_records[date_key] = {

            "date": check_date,

            "weight": weight,

            "sleep": sleep,

            "water": water,

            "meals": meals,

            "healthy_food": healthy_food,

            "exercise": exercise,

            "pregnancy_learning": pregnancy_learning,

            "baby_bonding": baby_bonding,

            "mood": mood,

            "energy": energy,

            "stress": stress
        }

        st.success(
            f"Your health check for {check_date.strftime('%b %d, %Y')} has been saved! 🌷"
        )

    st.write("")

    # ------------------------------------------
    # DASHBOARD BUTTON
    # ------------------------------------------

    if st.button(
        "❤️ VIEW HEALTH DASHBOARD",
        use_container_width=True
    ):

        st.session_state.page = "health_dashboard"

        st.rerun()

    st.write("")

    if st.button("← BACK TO TODAY"):

        st.session_state.page = "today"

        st.rerun()


# ==========================================
# HEALTH
# ==========================================

def show_health():

    st.markdown(
        '<div class="logo">✦ MOMI ✦</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        "# 🌸 Health"
    )

    st.caption(
        "Take care of you and baby"
    )

    show_momi()

    st.write("")

    col1, col2, col3 = st.columns(3)

    with col1:

        if st.button(
            "❤️ Health Dashboard",
            use_container_width=True
        ):

            st.session_state.page = "health_dashboard"

            st.rerun()

    with col2:

        if st.button(
            "👥 Peer Comparison",
            use_container_width=True
        ):

            st.session_state.page = "peer_comparison"

            st.rerun()

    with col3:

        if st.button(
            "📈 Health Trend AI",
            use_container_width=True
        ):

            st.session_state.page = "health_trend"

            st.rerun()

    st.write("")

    if st.button("← BACK TO HOME"):

        st.session_state.page = "home"

        st.rerun()


# ==========================================
# HEALTH DASHBOARD CHART COLORS
# ==========================================

SLEEP_COLOR = "#B8A1E3"
WATER_COLOR = "#8FD8C1"
EXERCISE_COLOR = "#F3A6B9"
WEIGHT_COLOR = "#AFA0E8"
MEALS_COLOR = "#F6C39A"
MOOD_COLOR = "#F29AC2"
ENERGY_COLOR = "#F4D77A"
STRESS_COLOR = "#E9A6A6"
LEARNING_COLOR = "#B8A1E3"
BONDING_COLOR = "#F29AC2"
HEALTHY_FOOD_COLOR = "#A8D5BA"


# ==========================================
# ❤️ HEALTH DASHBOARD
# ==========================================

def show_health_dashboard():

    st.markdown(
        '<div class="logo">✦ MOMI ✦</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        "# ❤️ Health Dashboard"
    )

    st.caption(
        "See how your daily health journey changes over time"
    )

    show_momi()

    st.write("")

    records = st.session_state.health_records

    # ------------------------------------------
    # 기록이 아직 없는 경우
    # ------------------------------------------

    if not records:

        with st.container(border=True):

            st.markdown(
                "### 🌱 Your health journey starts here"
            )

            st.write(
                "Complete your first Daily Health Check "
                "and your personal charts will appear here."
            )

        st.write("")

        if st.button(
            "📝 GO TO DAILY HEALTH CHECK",
            use_container_width=True
        ):

            st.session_state.page = "daily_health"

            st.rerun()

        st.write("")

        if st.button("← BACK TO HEALTH"):

            st.session_state.page = "health"

            st.rerun()

        return

    # ------------------------------------------
    # DataFrame 만들기
    # ------------------------------------------

    data = list(records.values())

    df = pd.DataFrame(data)

    df = df.sort_values("date")

    # 숫자로 변환할 데이터
    water_map = {
        "0–2 cups": 1,
        "3–4 cups": 3.5,
        "5–6 cups": 5.5,
        "7–8 cups": 7.5,
        "9+ cups": 9
    }

    meals_map = {
        "0 meals": 0,
        "1 meal": 1,
        "2 meals": 2,
        "3 meals": 3,
        "4+ meals": 4
    }

    exercise_map = {
        "None": 0,
        "10–20 min": 15,
        "20–40 min": 30,
        "40+ min": 45
    }

    healthy_food_map = {
        "Not today": 0,
        "A little": 1,
        "Balanced meal": 2
    }

    mood_map = {
        "😢 Low": 1,
        "😟 Worried": 2,
        "😐 Okay": 3,
        "🙂 Good": 4,
        "😄 Great": 5
    }

    energy_map = {
        "🥱 Low": 1,
        "🙂 Normal": 2,
        "⚡ High": 3
    }

    df["water_value"] = df["water"].map(water_map)
    df["meals_value"] = df["meals"].map(meals_map)
    df["exercise_value"] = df["exercise"].map(exercise_map)
    df["healthy_food_value"] = df["healthy_food"].map(healthy_food_map)
    df["mood_value"] = df["mood"].map(mood_map)
    df["energy_value"] = df["energy"].map(energy_map)

    df["learning_value"] = df["pregnancy_learning"].astype(int)
    df["bonding_value"] = df["baby_bonding"].astype(int)

    df["date_label"] = df["date"].apply(
        lambda x: x.strftime("%b %d")
    )

    # ------------------------------------------
    # 기록 개수
    # ------------------------------------------

    with st.container(border=True):

        st.caption("🌷 YOUR HEALTH JOURNEY")

        st.markdown(
            f"### {len(df)} day(s) recorded"
        )

        st.write(
            "Keep checking in to see your personal trends grow."
        )

    st.write("")

    # ==========================================
    # 😴 SLEEP
    # ==========================================

    with st.container(border=True):

        st.markdown("### 😴 SLEEP")

        chart = (
            alt.Chart(df)
            .mark_line(
                point=True,
                strokeWidth=4
            )
            .encode(
                x=alt.X(
                    "date_label:N",
                    title="Date"
                ),
                y=alt.Y(
                    "sleep:Q",
                    title="Hours"
                ),
                tooltip=[
                    alt.Tooltip("date_label:N", title="Date"),
                    alt.Tooltip("sleep:Q", title="Sleep", format=".1f")
                ]
            )
            .encode(color=alt.value(SLEEP_COLOR))
            .properties(height=230)
        )

        st.altair_chart(
            chart,
            use_container_width=True
        )

    st.write("")

    # ==========================================
    # 💧 WATER
    # ==========================================

    with st.container(border=True):

        st.markdown("### 💧 WATER")

        chart = (
            alt.Chart(df)
            .mark_bar(
                cornerRadiusTopLeft=8,
                cornerRadiusTopRight=8
            )
            .encode(
                x=alt.X(
                    "date_label:N",
                    title="Date"
                ),
                y=alt.Y(
                    "water_value:Q",
                    title="Approx. cups"
                ),
                tooltip=[
                    alt.Tooltip("date_label:N", title="Date"),
                    alt.Tooltip("water:N", title="Water")
                ]
            )
            .encode(color=alt.value(WATER_COLOR))
            .properties(height=230)
        )

        st.altair_chart(
            chart,
            use_container_width=True
        )

    st.write("")

    # ==========================================
    # 🏃‍♀️ EXERCISE
    # ==========================================

    with st.container(border=True):

        st.markdown("### 🏃‍♀️ EXERCISE")

        chart = (
            alt.Chart(df)
            .mark_bar(
                cornerRadiusTopLeft=8,
                cornerRadiusTopRight=8
            )
            .encode(
                x=alt.X(
                    "date_label:N",
                    title="Date"
                ),
                y=alt.Y(
                    "exercise_value:Q",
                    title="Minutes"
                ),
                tooltip=[
                    alt.Tooltip("date_label:N", title="Date"),
                    alt.Tooltip("exercise:N", title="Exercise")
                ]
            )
            .encode(color=alt.value(EXERCISE_COLOR))
            .properties(height=230)
        )

        st.altair_chart(
            chart,
            use_container_width=True
        )

    st.write("")

    # ==========================================
    # ⚖️ WEIGHT
    # ==========================================

    with st.container(border=True):

        st.markdown("### ⚖️ WEIGHT")

        chart = (
            alt.Chart(df)
            .mark_line(
                point=True,
                strokeWidth=4
            )
            .encode(
                x=alt.X(
                    "date_label:N",
                    title="Date"
                ),
                y=alt.Y(
                    "weight:Q",
                    title="kg"
                ),
                tooltip=[
                    alt.Tooltip("date_label:N", title="Date"),
                    alt.Tooltip("weight:Q", title="Weight", format=".1f")
                ]
            )
            .encode(color=alt.value(WEIGHT_COLOR))
            .properties(height=230)
        )

        st.altair_chart(
            chart,
            use_container_width=True
        )

    st.write("")

    # ==========================================
    # 🍚 MEALS
    # ==========================================

    with st.container(border=True):

        st.markdown("### 🍚 MEALS")

        chart = (
            alt.Chart(df)
            .mark_bar(
                cornerRadiusTopLeft=8,
                cornerRadiusTopRight=8
            )
            .encode(
                x=alt.X(
                    "date_label:N",
                    title="Date"
                ),
                y=alt.Y(
                    "meals_value:Q",
                    title="Meals"
                ),
                tooltip=[
                    alt.Tooltip("date_label:N", title="Date"),
                    alt.Tooltip("meals:N", title="Meals")
                ]
            )
            .encode(color=alt.value(MEALS_COLOR))
            .properties(height=230)
        )

        st.altair_chart(
            chart,
            use_container_width=True
        )

    st.write("")

    # ==========================================
    # 😊 MOOD
    # ==========================================

    with st.container(border=True):

        st.markdown("### 😊 MOOD")

        chart = (
            alt.Chart(df)
            .mark_line(
                point=True,
                strokeWidth=4
            )
            .encode(
                x=alt.X(
                    "date_label:N",
                    title="Date"
                ),
                y=alt.Y(
                    "mood_value:Q",
                    title="Mood",
                    scale=alt.Scale(domain=[1, 5])
                ),
                tooltip=[
                    alt.Tooltip("date_label:N", title="Date"),
                    alt.Tooltip("mood:N", title="Mood")
                ]
            )
            .encode(color=alt.value(MOOD_COLOR))
            .properties(height=230)
        )

        st.altair_chart(
            chart,
            use_container_width=True
        )

    st.write("")

    # ==========================================
    # ⚡ ENERGY
    # ==========================================

    with st.container(border=True):

        st.markdown("### ⚡ ENERGY")

        chart = (
            alt.Chart(df)
            .mark_line(
                point=True,
                strokeWidth=4
            )
            .encode(
                x=alt.X(
                    "date_label:N",
                    title="Date"
                ),
                y=alt.Y(
                    "energy_value:Q",
                    title="Energy",
                    scale=alt.Scale(domain=[1, 3])
                ),
                tooltip=[
                    alt.Tooltip("date_label:N", title="Date"),
                    alt.Tooltip("energy:N", title="Energy")
                ]
            )
            .encode(color=alt.value(ENERGY_COLOR))
            .properties(height=230)
        )

        st.altair_chart(
            chart,
            use_container_width=True
        )

    st.write("")

    # ==========================================
    # 😰 STRESS
    # ==========================================

    with st.container(border=True):

        st.markdown("### 😰 STRESS")

        chart = (
            alt.Chart(df)
            .mark_line(
                point=True,
                strokeWidth=4
            )
            .encode(
                x=alt.X(
                    "date_label:N",
                    title="Date"
                ),
                y=alt.Y(
                    "stress:Q",
                    title="Stress",
                    scale=alt.Scale(domain=[1, 5])
                ),
                tooltip=[
                    alt.Tooltip("date_label:N", title="Date"),
                    alt.Tooltip("stress:Q", title="Stress")
                ]
            )
            .encode(color=alt.value(STRESS_COLOR))
            .properties(height=230)
        )

        st.altair_chart(
            chart,
            use_container_width=True
        )

    st.write("")

    # ==========================================
    # 📚 PREGNANCY LEARNING
    # ==========================================

    with st.container(border=True):

        st.markdown("### 📚 PREGNANCY LEARNING")

        learning_yes = int(df["pregnancy_learning"].sum())
        learning_no = len(df) - learning_yes

        learning_df = pd.DataFrame({
            "status": ["Learned", "Not yet"],
            "count": [learning_yes, learning_no]
        })

        chart = (
            alt.Chart(learning_df)
            .mark_arc(
                innerRadius=55
            )
            .encode(
                theta="count:Q",
                color=alt.Color(
                    "status:N",
                    scale=alt.Scale(
                        range=[LEARNING_COLOR, "#E8DFFF"]
                    )
                ),
                tooltip=[
                    alt.Tooltip("status:N", title="Status"),
                    alt.Tooltip("count:Q", title="Days")
                ]
            )
            .properties(height=250)
        )

        st.altair_chart(
            chart,
            use_container_width=True
        )

    st.write("")

    # ==========================================
    # 🎵 BABY BONDING
    # ==========================================

    with st.container(border=True):

        st.markdown("### 🎵 BABY BONDING")

        bonding_yes = int(df["baby_bonding"].sum())
        bonding_no = len(df) - bonding_yes

        bonding_df = pd.DataFrame({
            "status": ["Bonding", "Not yet"],
            "count": [bonding_yes, bonding_no]
        })

        chart = (
            alt.Chart(bonding_df)
            .mark_arc(
                innerRadius=55
            )
            .encode(
                theta="count:Q",
                color=alt.Color(
                    "status:N",
                    scale=alt.Scale(
                        range=[BONDING_COLOR, "#FFE5F0"]
                    )
                ),
                tooltip=[
                    alt.Tooltip("status:N", title="Status"),
                    alt.Tooltip("count:Q", title="Days")
                ]
            )
            .properties(height=250)
        )

        st.altair_chart(
            chart,
            use_container_width=True
        )

    st.write("")

    # ==========================================
    # 🥗 HEALTHY FOOD
    # ==========================================

    with st.container(border=True):

        st.markdown("### 🥗 HEALTHY FOOD")

        chart = (
            alt.Chart(df)
            .mark_bar(
                cornerRadiusTopLeft=8,
                cornerRadiusTopRight=8
            )
            .encode(
                x=alt.X(
                    "date_label:N",
                    title="Date"
                ),
                y=alt.Y(
                    "healthy_food_value:Q",
                    title="Balanced food",
                    scale=alt.Scale(domain=[0, 2])
                ),
                tooltip=[
                    alt.Tooltip("date_label:N", title="Date"),
                    alt.Tooltip("healthy_food:N", title="Food")
                ]
            )
            .encode(color=alt.value(HEALTHY_FOOD_COLOR))
            .properties(height=230)
        )

        st.altair_chart(
            chart,
            use_container_width=True
        )

    st.write("")

    # ==========================================
    # 최근 기록
    # ==========================================

    with st.container(border=True):

        st.markdown("### 🌷 RECENT RECORDS")

        display_df = df[
            [
                "date",
                "weight",
                "sleep",
                "water",
                "meals",
                "exercise",
                "mood",
                "energy",
                "stress"
            ]
        ].copy()

        display_df["date"] = display_df["date"].apply(
            lambda x: x.strftime("%b %d, %Y")
        )

        display_df.columns = [
            "Date",
            "Weight",
            "Sleep",
            "Water",
            "Meals",
            "Exercise",
            "Mood",
            "Energy",
            "Stress"
        ]

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )

    st.write("")

    if st.button(
        "📝 ADD / EDIT DAILY CHECK",
        use_container_width=True
    ):

        st.session_state.page = "daily_health"

        st.rerun()

    st.write("")

    if st.button("← BACK TO HEALTH"):

        st.session_state.page = "health"

        st.rerun()


# ==========================================
# MILESTONE
# ==========================================

def show_milestone():

    st.markdown(
        '<div class="logo">✦ MOMI ✦</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        "# 🍼 Milestone"
    )

    st.caption(
        "See your baby's weekly journey"
    )

    show_momi()

    st.write("")

    st.markdown(
        "### 🌸 SELECT WEEK"
    )

    st.write("")

    for row in range(5):

        cols = st.columns(8)

        for i in range(8):

            week_number = row * 8 + i + 1

            if week_number <= 40:

                with cols[i]:

                    if st.button(
                        str(week_number),
                        use_container_width=True,
                        key=f"week_{week_number}"
                    ):

                        st.session_state.selected_week = week_number

                        st.session_state.page = "milestone_week"

                        st.rerun()

    st.write("")

    if st.button("← BACK TO HOME"):

        st.session_state.page = "home"

        st.rerun()


# ==========================================
# 선택한 주차의 실제 내용
# ==========================================

def show_milestone_content(week):

    data = milestones[week]

    with st.container(border=True):

        st.caption("🍼 BABY GROWTH")

        st.write(
            data["baby"]
        )

    st.write("")

    with st.container(border=True):

        st.caption("🌸 MOM'S CARE")

        st.write(
            data["mom"]
        )

    st.write("")

    with st.container(border=True):

        st.caption("✦ MOMI'S MESSAGE")

        st.write(
            data["message"]
        )


# ==========================================
# 선택한 주차
# ==========================================

def show_milestone_week():

    week = st.session_state.selected_week

    st.markdown(
        '<div class="logo">✦ MOMI ✦</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f"# Week {week} 🌸"
    )

    st.caption(
        f"Pregnancy information for Week {week}"
    )

    show_momi()

    st.write("")

    show_milestone_content(week)

    st.write("")

    if st.button("← SELECT ANOTHER WEEK"):

        st.session_state.page = "milestone"

        st.rerun()

    if st.button("← BACK TO HOME"):

        st.session_state.page = "home"

        st.rerun()


# ==========================================
# AI
# ==========================================

def show_ai():

    st.markdown(
        '<div class="logo">✦ MOMI ✦</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        "# ✨ AI Consultant"
    )

    st.caption(
        "Your gentle AI pregnancy companion"
    )

    show_momi()

    st.write("")

    if st.button(
        "🤖 AI Consultation",
        use_container_width=True
    ):

        st.session_state.page = "ai_consultation"

        st.rerun()

    st.write("")

    if st.button("← BACK TO HOME"):

        st.session_state.page = "home"

        st.rerun()


# ==========================================
# HOSPITAL
# ==========================================

def hospital_card(title, lines):

    with st.container(border=True):
        st.markdown(f"### {title}")
        for line in lines:
            st.write(line)


def get_upcoming_appointments():

    today = date.today()
    upcoming = []

    for appointment in st.session_state.appointments:
        appointment_date = datetime.strptime(
            appointment["date"], "%Y-%m-%d"
        ).date()

        if appointment_date >= today:
            upcoming.append(appointment)

    upcoming.sort(
        key=lambda item: (
            item["date"],
            item["time"]
        )
    )

    return upcoming


def show_hospital():

    st.markdown(
        '<div class="logo">✦ MOMI ✦</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        "# 🏥 Hospital"
    )

    st.caption(
        "Find and manage your hospital information"
    )

    show_momi()

    st.write("")

    col1, col2, col3 = st.columns(3)

    with col1:

        if st.button(
            "📅 Schedule",
            use_container_width=True
        ):

            st.session_state.page = "hospital_schedule"

            st.rerun()

    with col2:

        if st.button(
            "📋 Appointments",
            use_container_width=True
        ):

            st.session_state.page = "hospital_appointments"

            st.rerun()

    with col3:

        if st.button(
            "💌 Hospital Messages",
            use_container_width=True
        ):

            st.session_state.page = "hospital_messages"

            st.rerun()

    st.write("")

    upcoming = get_upcoming_appointments()

    if upcoming:
        next_visit = upcoming[0]

        with st.container(border=True):
            st.caption("🏥 NEXT VISIT")
            st.markdown(f"### {next_visit['hospital']}")
            st.write(f"👨‍⚕️ {next_visit['doctor']}")
            st.write(
                f"📅 {datetime.strptime(next_visit['date'], '%Y-%m-%d').strftime('%B %d, %Y')}"
            )
            st.write(f"⏰ {next_visit['time']}")

    st.write("")

    if st.button("← BACK TO HOME"):

        st.session_state.page = "home"

        st.rerun()


def show_appointments():

    st.markdown(
        '<div class="logo">✦ MOMI ✦</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        "# 📋 Appointments"
    )

    st.caption(
        "Book and manage your hospital appointments"
    )

    show_momi()

    st.write("")

    # ------------------------------------------
    # Existing appointments
    # ------------------------------------------

    upcoming = get_upcoming_appointments()

    if upcoming:
        with st.container(border=True):
            st.caption("YOUR UPCOMING APPOINTMENTS")

            for index, appointment in enumerate(upcoming):
                appointment_date = datetime.strptime(
                    appointment["date"], "%Y-%m-%d"
                ).date()

                st.markdown(f"### 🏥 {appointment['hospital']}")
                st.write(f"👨‍⚕️ {appointment['doctor']}")
                st.write(
                    f"📅 {appointment_date.strftime('%B %d, %Y')} · ⏰ {appointment['time']}"
                )

                if st.button(
                    "Cancel Appointment",
                    key=f"cancel_appointment_{index}",
                    use_container_width=True
                ):
                    st.session_state.appointments.remove(appointment)
                    st.rerun()

                if index < len(upcoming) - 1:
                    st.write("")

        st.write("")

    # ------------------------------------------
    # Step 1: Hospital
    # ------------------------------------------

    st.markdown("### 1. SELECT HOSPITAL")

    if st.session_state.hospital_selected_hospital is None:

        hospitals = list(st.session_state.hospital_data.keys())

        for row in range(0, len(hospitals), 2):
            col1, col2 = st.columns(2)

            for col, hospital_index in zip(
                [col1, col2],
                range(row, min(row + 2, len(hospitals)))
            ):
                hospital = hospitals[hospital_index]

                with col:
                    if st.button(
                        f"🏥 {hospital}",
                        key=f"hospital_select_{hospital_index}",
                        use_container_width=True
                    ):
                        st.session_state.hospital_selected_hospital = hospital
                        st.session_state.hospital_selected_doctor = None
                        st.session_state.hospital_selected_date = None
                        st.session_state.hospital_selected_time = None
                        st.rerun()

    else:

        selected_hospital = st.session_state.hospital_selected_hospital

        with st.container(border=True):
            st.caption("SELECTED HOSPITAL")
            st.markdown(f"### 🏥 {selected_hospital}")

        st.write("")

        if st.button("↩ CHANGE HOSPITAL", use_container_width=True):
            st.session_state.hospital_selected_hospital = None
            st.session_state.hospital_selected_doctor = None
            st.session_state.hospital_selected_date = None
            st.session_state.hospital_selected_time = None
            st.rerun()

        st.write("")

        # ------------------------------------------
        # Step 2: Doctor
        # ------------------------------------------

        st.markdown("### 2. SELECT DOCTOR")

        if st.session_state.hospital_selected_doctor is None:

            doctors = st.session_state.hospital_data[selected_hospital]

            for doctor_index, doctor in enumerate(doctors):
                with st.container(border=True):
                    st.markdown(f"### 👨‍⚕️ {doctor['name']}")
                    st.caption(doctor["specialty"])

                    if st.button(
                        "VIEW AVAILABLE TIMES",
                        key=f"doctor_select_{doctor_index}",
                        use_container_width=True
                    ):
                        st.session_state.hospital_selected_doctor = doctor_index
                        st.session_state.hospital_selected_date = None
                        st.session_state.hospital_selected_time = None
                        st.rerun()

                st.write("")

        else:

            doctor_index = st.session_state.hospital_selected_doctor
            doctor = st.session_state.hospital_data[selected_hospital][doctor_index]

            with st.container(border=True):
                st.caption("SELECTED DOCTOR")
                st.markdown(f"### 👨‍⚕️ {doctor['name']}")
                st.write(doctor["specialty"])

            st.write("")

            if st.button("↩ CHANGE DOCTOR", use_container_width=True):
                st.session_state.hospital_selected_doctor = None
                st.session_state.hospital_selected_date = None
                st.session_state.hospital_selected_time = None
                st.rerun()

            st.write("")

            # ------------------------------------------
            # Step 3: Date
            # ------------------------------------------

            st.markdown("### 3. SELECT DATE")

            doctor_dates = sorted(doctor["schedule"].keys())

            date_columns = st.columns(3)

            for date_index, date_key in enumerate(doctor_dates):
                available_date = datetime.strptime(
                    date_key, "%Y-%m-%d"
                ).date()

                with date_columns[date_index % 3]:
                    if st.button(
                        available_date.strftime("%b %d"),
                        key=f"appointment_date_{date_index}",
                        use_container_width=True
                    ):
                        st.session_state.hospital_selected_date = date_key
                        st.session_state.hospital_selected_time = None
                        st.rerun()

            if st.session_state.hospital_selected_date is not None:

                selected_date = st.session_state.hospital_selected_date

                st.write("")

                # ------------------------------------------
                # Step 4: Time
                # ------------------------------------------

                st.markdown("### 4. SELECT TIME")

                selected_date_object = datetime.strptime(
                    selected_date, "%Y-%m-%d"
                ).date()

                st.caption(
                    selected_date_object.strftime("%B %d, %Y")
                )

                times = doctor["schedule"][selected_date]
                time_columns = st.columns(3)

                for time_index, available_time in enumerate(times):
                    with time_columns[time_index % 3]:
                        if st.button(
                            available_time,
                            key=f"appointment_time_{time_index}",
                            use_container_width=True
                        ):
                            st.session_state.hospital_selected_time = available_time
                            st.rerun()

                if st.session_state.hospital_selected_time is not None:

                    selected_time = st.session_state.hospital_selected_time

                    st.write("")

                    with st.container(border=True):
                        st.caption("APPOINTMENT SUMMARY")
                        st.markdown(f"### 🏥 {selected_hospital}")
                        st.write(f"👨‍⚕️ {doctor['name']}")
                        st.write(
                            f"📅 {selected_date_object.strftime('%B %d, %Y')}"
                        )
                        st.write(f"⏰ {selected_time}")
                        st.caption(doctor["specialty"])

                    st.write("")

                    if st.button(
                        "✓ CONFIRM APPOINTMENT",
                        use_container_width=True
                    ):

                        new_appointment = {
                            "hospital": selected_hospital,
                            "doctor": doctor["name"],
                            "specialty": doctor["specialty"],
                            "date": selected_date,
                            "time": selected_time,
                            "type": "Prenatal Checkup",
                            "preparation": (
                                "Please bring your ID, maternity record book, insurance card, "
                                "previous test results, and any questions you would like to discuss."
                            )
                        }

                        duplicate = any(
                            item["hospital"] == new_appointment["hospital"]
                            and item["doctor"] == new_appointment["doctor"]
                            and item["date"] == new_appointment["date"]
                            and item["time"] == new_appointment["time"]
                            for item in st.session_state.appointments
                        )

                        if not duplicate:
                            st.session_state.appointments.append(
                                new_appointment
                            )

                        st.session_state.hospital_selected_hospital = None
                        st.session_state.hospital_selected_doctor = None
                        st.session_state.hospital_selected_date = None
                        st.session_state.hospital_selected_time = None
                        st.session_state.page = "next_hospital"
                        st.rerun()

    st.write("")

    if st.button("← BACK TO HOSPITAL", use_container_width=True):
        st.session_state.page = "hospital"
        st.rerun()


def show_schedule():

    st.markdown(
        '<div class="logo">✦ MOMI ✦</div>',
        unsafe_allow_html=True
    )

    st.markdown("# 📅 Schedule")
    st.caption("See your hospital visits and personal plans at a glance")

    show_momi()

    st.write("")

    current_month = st.session_state.schedule_month
    year = current_month.year
    month = current_month.month

    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if st.button("←", key="schedule_prev_month", use_container_width=True):
            if month == 1:
                st.session_state.schedule_month = date(year - 1, 12, 1)
            else:
                st.session_state.schedule_month = date(year, month - 1, 1)
            st.rerun()

    with col2:
        st.markdown(
            f"### {current_month.strftime('%B %Y')}",
            unsafe_allow_html=True
        )

    with col3:
        if st.button("→", key="schedule_next_month", use_container_width=True):
            if month == 12:
                st.session_state.schedule_month = date(year + 1, 1, 1)
            else:
                st.session_state.schedule_month = date(year, month + 1, 1)
            st.rerun()

    st.write("")

    calendar_matrix = calendar.monthcalendar(year, month)
    weekday_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    weekday_columns = st.columns(7)
    for index, weekday in enumerate(weekday_names):
        with weekday_columns[index]:
            st.caption(weekday)

    for week_row, week_dates in enumerate(calendar_matrix):
        day_columns = st.columns(7)

        for day_index, day_number in enumerate(week_dates):
            with day_columns[day_index]:
                if day_number == 0:
                    st.write("")
                else:
                    calendar_date = date(year, month, day_number)
                    date_key = calendar_date.isoformat()

                    appointment_here = [
                        item for item in st.session_state.appointments
                        if item["date"] == date_key
                    ]

                    personal_here = st.session_state.personal_schedules.get(
                        date_key, []
                    )

                    marker = ""
                    if appointment_here:
                        marker += "🏥"
                    if personal_here:
                        marker += "✦"

                    label = f"{day_number}"
                    if marker:
                        label += f"\n{marker}"

                    if st.button(
                        label,
                        key=f"calendar_day_{year}_{month}_{day_number}",
                        use_container_width=True
                    ):
                        st.session_state.schedule_selected_date = calendar_date
                        st.rerun()

    selected_date = st.session_state.schedule_selected_date

    st.write("")

    with st.container(border=True):
        st.caption("SELECTED DATE")
        st.markdown(
            f"### {selected_date.strftime('%B %d, %Y')}"
        )

    st.write("")

    # ------------------------------------------
    # Automatic hospital appointments
    # ------------------------------------------

    selected_key = selected_date.isoformat()
    appointments_today = [
        item for item in st.session_state.appointments
        if item["date"] == selected_key
    ]

    if appointments_today:
        st.markdown("### 🏥 HOSPITAL APPOINTMENTS")

        for appointment in appointments_today:
            with st.container(border=True):
                st.caption("AUTOMATIC APPOINTMENT")
                st.markdown(f"### {appointment['hospital']}")
                st.write(f"👨‍⚕️ {appointment['doctor']}")
                st.write(f"⏰ {appointment['time']}")
                st.caption(appointment["specialty"])

        st.write("")

    # ------------------------------------------
    # Personal schedules
    # ------------------------------------------

    personal_today = st.session_state.personal_schedules.get(
        selected_key, []
    )

    if personal_today:
        st.markdown("### ✏️ PERSONAL SCHEDULE")

        for item_index, item in enumerate(personal_today):
            with st.container(border=True):
                st.caption("PERSONAL SCHEDULE")
                st.markdown(f"### {item['title']}")
                st.write(f"⏰ {item['time']}")
                if item["note"]:
                    st.write(item["note"])

                if st.button(
                    "Delete",
                    key=f"delete_personal_{selected_key}_{item_index}",
                    use_container_width=True
                ):
                    personal_today.pop(item_index)
                    if not personal_today:
                        del st.session_state.personal_schedules[selected_key]
                    st.rerun()

        st.write("")

    # ------------------------------------------
    # Add personal schedule
    # ------------------------------------------

    st.markdown("### ✏️ ADD PERSONAL SCHEDULE")

    with st.container(border=True):
        schedule_title = st.text_input(
            "Title",
            placeholder="e.g. Prenatal Yoga",
            key="new_schedule_title"
        )

        schedule_time = st.text_input(
            "Time",
            placeholder="e.g. 19:00",
            key="new_schedule_time"
        )

        schedule_note = st.text_input(
            "Note",
            placeholder="Add a short note",
            key="new_schedule_note"
        )

        if st.button(
            "＋ SAVE SCHEDULE",
            use_container_width=True
        ):
            if schedule_title.strip():
                if selected_key not in st.session_state.personal_schedules:
                    st.session_state.personal_schedules[selected_key] = []

                st.session_state.personal_schedules[selected_key].append({
                    "title": schedule_title.strip(),
                    "time": schedule_time.strip() or "All day",
                    "note": schedule_note.strip()
                })

                st.rerun()
            else:
                st.warning("Please enter a title for your schedule.")

    st.write("")

    if st.button("← BACK TO HOSPITAL", use_container_width=True):
        st.session_state.page = "hospital"
        st.rerun()


def show_next_hospital_visit():

    st.markdown(
        '<div class="logo">✦ MOMI ✦</div>',
        unsafe_allow_html=True
    )

    st.markdown("# 🏥 Next Hospital Visit")
    st.caption("Your next hospital visit and appointment details")

    show_momi()

    st.write("")

    upcoming = get_upcoming_appointments()

    if not upcoming:

        with st.container(border=True):
            st.caption("NEXT VISIT")
            st.markdown("### No upcoming hospital visits")
            st.write(
                "Book an appointment to see your next visit here."
            )

        st.write("")

        if st.button(
            "📋 BOOK AN APPOINTMENT",
            use_container_width=True
        ):
            st.session_state.page = "hospital_appointments"
            st.rerun()

    else:

        appointment = upcoming[0]
        appointment_date = datetime.strptime(
            appointment["date"], "%Y-%m-%d"
        ).date()

        with st.container(border=True):
            st.caption("🏥 NEXT VISIT")
            st.markdown(f"# {appointment['hospital']}")
            st.write("")
            st.markdown(f"### 👨‍⚕️ {appointment['doctor']}")
            st.caption(appointment["specialty"])
            st.write("")
            st.markdown(
                f"### 📅 {appointment_date.strftime('%B %d, %Y')}"
            )
            st.markdown(f"### ⏰ {appointment['time']}")

        st.write("")

        with st.container(border=True):
            st.caption("🎒 THINGS YOU MAY WANT TO BRING")
            st.write("✓ ID Card")
            st.write("✓ Maternity Record Book")
            st.write("✓ Medical Documents")
            st.write("✓ Insurance Card")
            st.write("✓ Previous Test Results")

        st.write("")

        if st.button(
            "📋 VIEW APPOINTMENT",
            use_container_width=True
        ):
            st.session_state.page = "hospital_appointments"
            st.rerun()

    st.write("")

    if st.button("← BACK TO TODAY", use_container_width=True):
        st.session_state.page = "today"
        st.rerun()


# ==========================================
# 🤖 AI CONSULTATION
# ==========================================

def get_current_milestone():

    week = st.session_state.pregnancy_week

    if week in milestones:
        return milestones[week]

    return None


def momi_ai_reply(message):

    text = message.lower().strip()
    week = st.session_state.pregnancy_week
    mom_name = st.session_state.mom_name or "there"
    baby_name = st.session_state.baby_name or "your baby"

    # Urgent symptom safety response
    urgent_words = [
        "heavy bleeding", "severe bleeding", "severe pain",
        "chest pain", "can't breathe", "cannot breathe",
        "difficulty breathing", "fainted", "fainting", "seizure",
        "severe headache", "vision changes", "blurry vision",
        "leaking fluid", "water broke", "passed out"
    ]

    if any(word in text for word in urgent_words):
        return (
            "I’m glad you told me, but this is something a healthcare professional "
            "should assess rather than MOMI trying to judge it. If the symptom is "
            "severe, sudden, or feels like an emergency, please contact your maternity "
            "care team or local emergency medical service now. 💗"
        )

    # Emotional support
    emotional_words = [
        "anxious", "anxiety", "worried", "worry", "stressed", "stress",
        "hard day", "sad", "scared", "overwhelmed", "tired of", "listen",
        "vent", "crying", "upset"
    ]

    if any(word in text for word in emotional_words):
        return (
            f"I’m here with you, {mom_name}. You don’t have to turn every feeling "
            f"into a problem that needs fixing. 💗 You can tell me what has been "
            f"on your mind, and I’ll listen. If your feelings ever become overwhelming "
            "or you feel unsafe, please reach out to someone you trust or a healthcare "
            "professional for extra support."
        )

    # Current week / milestone questions
    week_words = [
        "this week", "my baby", "baby developing", "baby develop",
        "development", "milestone", "pregnancy week", "what changes"
    ]

    if any(word in text for word in week_words):
        milestone = get_current_milestone()

        if milestone:
            return (
                f"You’re at Week {week}, {mom_name}! 🌷\n\n"
                f"🍼 **Baby Growth:** {milestone['baby']}\n\n"
                f"🌸 **Mom’s Care:** {milestone['mom']}\n\n"
                f"✦ **MOMI’s Message:** {milestone['message']}"
            )

    # Food questions
    if any(word in text for word in ["eat", "food", "drink", "meal", "diet"]):
        return (
            "I can help you think through general pregnancy food guidance. 🌷 "
            "For a specific food, tell me its name and how it is prepared. In general, "
            "choose a varied diet and follow the food-safety guidance from your healthcare "
            "provider. For personalized restrictions or medical nutrition advice, please "
            "check with your maternity care team."
        )

    # Sleep questions
    if any(word in text for word in ["sleep", "insomnia", "can't sleep", "cannot sleep"]):
        return (
            "Sleep can feel very different during pregnancy. 🌙 A calm bedtime routine, "
            "comfortable positioning, regular daytime movement, and limiting caffeine "
            "late in the day may help. If sleep problems are persistent or are affecting "
            "your daily life, your healthcare provider can help you find an approach that "
            "fits you."
        )

    # Exercise questions
    if any(word in text for word in ["exercise", "workout", "walk", "yoga", "fitness"]):
        return (
            "Gentle movement can be a lovely part of pregnancy for many people. 🌿 "
            "Walking, comfortable stretching, and pregnancy-appropriate activities may be "
            "options when they fit your individual situation. If you have been given activity "
            "restrictions or have concerns about a particular exercise, check with your "
            "healthcare provider first."
        )

    # General pregnancy questions
    if any(word in text for word in ["pregnant", "pregnancy", "trimester", "prenatal"]):
        return (
            f"Of course, {mom_name}. 💕 You’re currently at Week {week}, and I can help "
            "with general pregnancy information, your current milestone, everyday food, "
            "sleep, movement, or simply listening when you need to talk. I’m here for "
            f"you and {baby_name}, but I’m not a replacement for your healthcare team."
        )

    # Friendly default
    return (
        f"I’m listening, {mom_name}. 💗 Tell me a little more about what you’re thinking "
        f"or wondering about. You’re at Week {week}, so I can also tell you about this "
        f"week’s baby development or Mom’s Care tips for {baby_name}."
    )


def show_ai_consultation():

    st.markdown(
        '<div class="logo">✦ MOMI ✦</div>',
        unsafe_allow_html=True
    )

    st.markdown("# 🤖 AI Consultation")
    st.caption("Talk with MOMI about pregnancy, your feelings, or your questions")

    show_momi()

    if "ai_messages" not in st.session_state:
        st.session_state.ai_messages = [
            {
                "role": "assistant",
                "content": (
                    f"Hi {st.session_state.mom_name or 'there'}! 💗 I’m MOMI. "
                    f"You’re at Week {st.session_state.pregnancy_week}. "
                    "You can ask me about your baby’s development, everyday pregnancy "
                    "questions, or simply tell me how you’re feeling. I’m here to listen."
                )
            }
        ]

    st.write("")

    for message in st.session_state.ai_messages:
        if message["role"] == "user":
            with st.container(border=True):
                st.caption("YOU")
                st.write(message["content"])
        else:
            with st.container(border=True):
                st.caption("✦ MOMI")
                st.markdown(message["content"])

        st.write("")

    col1, col2 = st.columns([4, 1])

    with col1:
        user_message = st.text_input(
            "",
            placeholder="Ask MOMI anything or tell me how you feel...",
            key="ai_message_input"
        )

    with col2:
        send_ai = st.button("SEND", use_container_width=True)

    if send_ai and user_message.strip():
        st.session_state.ai_messages.append({
            "role": "user",
            "content": user_message.strip()
        })

        st.session_state.ai_messages.append({
            "role": "assistant",
            "content": momi_ai_reply(user_message)
        })

        st.rerun()

    st.write("")

    if st.button("← BACK TO AI", use_container_width=True):
        st.session_state.page = "ai"
        st.rerun()


# ==========================================
# 💌 HOSPITAL MESSAGES
# ==========================================

def get_next_appointment():

    upcoming = get_upcoming_appointments()

    if upcoming:
        return upcoming[0]

    return None


def get_hospital_for_appointment(appointment):

    if appointment and appointment.get("hospital") in st.session_state.hospital_data:
        return appointment["hospital"]

    hospitals = list(st.session_state.hospital_data.keys())

    if hospitals:
        return hospitals[0]

    return None


def get_hospital_assistant_info(hospital_name):
    """
    Uses the existing hospital data first.
    Extra guidance is demo/mock information only because the current
    hospital data does not contain parking, payment, or facility fields.
    """

    contact = st.session_state.hospital_contact_data.get(hospital_name, {})
    doctors = st.session_state.hospital_data.get(hospital_name, [])

    hospital_index = list(st.session_state.hospital_data.keys()).index(
        hospital_name
    ) if hospital_name in st.session_state.hospital_data else 0

    parking_options = [
        "Visitor parking is available near the hospital. Please allow a little extra time for parking and check-in.",
        "Visitor parking is available near the main entrance. Please bring your appointment information when checking in.",
        "Parking is available for visitors. Please arrive a little early so you have enough time to park and check in."
    ]

    payment_options = [
        "This demo hospital accepts common payment methods at the hospital payment desk. Please check the final payment details with the hospital.",
        "Payment can be handled at the hospital payment desk. For exact fees or accepted payment methods, please confirm with the hospital.",
        "Please visit the payment desk after your appointment. Exact costs and payment methods may vary, so confirm the details with the hospital."
    ]

    facility_options = [
        "The hospital's listed services include " + contact.get("services", "maternity care") + ".",
        "Available hospital services include " + contact.get("services", "maternity care") + ".",
        "This hospital provides " + contact.get("services", "maternity care") + "."
    ]

    arrival_options = [
        "For a visit, arrive a little early, check in at the main desk, and have your appointment information ready.",
        "For your visit, please allow time for arrival and check-in. Keep your appointment information ready at the front desk.",
        "A simple visit flow is: arrive at the hospital, find the main check-in desk, and confirm your appointment before seeing your doctor."
    ]

    return {
        "address": contact.get("address", "Demo hospital address"),
        "phone": contact.get("phone", "Demo hospital contact"),
        "services": contact.get("services", "Maternity Care"),
        "doctors": doctors,
        "parking": parking_options[hospital_index % len(parking_options)],
        "payment": payment_options[hospital_index % len(payment_options)],
        "facilities": facility_options[hospital_index % len(facility_options)],
        "arrival": arrival_options[hospital_index % len(arrival_options)]
    }


def hospital_assistant_reply(message, hospital_name):
    text = message.lower().strip()

    if not hospital_name:
        return (
            "Please select a hospital first so I can give you "
            "hospital-specific guidance."
        )

    info = get_hospital_assistant_info(hospital_name)
    doctors = info["doctors"]

    # Pregnancy-related questions belong in MOMI AI Consultation.
    pregnancy_words = [
        "baby", "fetus", "pregnancy week", "pregnancy symptom",
        "pregnancy symptoms", "nutrition", "pregnant", "pregnancy",
        "trimester", "development", "morning sickness", "nausea",
        "bleeding", "pain", "contraction", "swelling", "medicine",
        "medication", "diagnosis", "treatment"
    ]

    if any(word in text for word in pregnancy_words):
        return (
            "This assistant is for hospital information and visit guidance. "
            "For pregnancy-related questions, please use MOMI AI Consultation."
        )

    # Appointment information
    if any(word in text for word in [
        "appointment", "appointments", "booking", "book", "visit"
    ]):
        upcoming = [
            item for item in get_upcoming_appointments()
            if item.get("hospital") == hospital_name
        ]

        if upcoming:
            appointment = upcoming[0]
            appointment_date = datetime.strptime(
                appointment["date"], "%Y-%m-%d"
            ).date()

            return (
                f"Your upcoming appointment at {hospital_name} is with "
                f"{appointment['doctor']} on "
                f"{appointment_date.strftime('%B %d, %Y')} at "
                f"{appointment['time']}. "
                f"Appointment type: {appointment.get('type', 'Prenatal Checkup')}."
            )

        return (
            f"You do not currently have an upcoming appointment at "
            f"{hospital_name}. You can book one from Hospital → Appointments."
        )

    # Preparation / what to bring
    if any(word in text for word in [
        "bring", "prepare", "preparation", "documents", "what should i bring"
    ]):
        upcoming = [
            item for item in get_upcoming_appointments()
            if item.get("hospital") == hospital_name
        ]

        if upcoming:
            return upcoming[0].get(
                "preparation",
                "Please bring your ID, appointment information, previous medical "
                "records if available, and any questions you would like to discuss "
                "with your doctor."
            )

        return (
            "Please bring your ID, appointment information, previous medical "
            "records if available, and any questions you would like to discuss "
            "with your doctor."
        )

    # Doctor information
    if any(word in text for word in [
        "doctor", "doctors", "physician", "doctor information"
    ]):
        if doctors:
            doctor_lines = [
                f"• {doctor['name']} — {doctor['specialty']}"
                for doctor in doctors
            ]

            return (
                f"Doctors currently listed for {hospital_name}:\n\n"
                + "\n".join(doctor_lines)
            )

        return "No doctor information is currently listed for this demo hospital."

    # Appointment time
    if any(word in text for word in [
        "time", "times", "available time", "available times", "hours"
    ]):
        if doctors:
            available_times = []

            for doctor in doctors:
                for times in doctor.get("schedule", {}).values():
                    available_times.extend(times)

            available_times = sorted(set(available_times))

            if available_times:
                return (
                    f"Available appointment times currently listed for "
                    f"{hospital_name} include: "
                    + ", ".join(available_times)
                    + ". Availability can vary by doctor and date."
                )

        return (
            "Please open Hospital → Appointments to see the currently "
            "listed dates and times for each doctor."
        )

    # Location / address
    if any(word in text for word in [
        "location", "address", "where", "located"
    ]):
        return (
            f"{hospital_name} is listed at {info['address']}.\n\n"
            "Please use the address shown in this demo app as the hospital "
            "location information."
        )

    # Parking and arrival
    if any(word in text for word in [
        "parking", "park", "arrival", "arrive", "check in", "check-in"
    ]):
        return info["parking"] + "\n\n" + info["arrival"]

    # Payment
    if any(word in text for word in [
        "payment", "pay", "cost", "fee", "fees", "insurance"
    ]):
        return info["payment"]

    # Facilities / services
    if any(word in text for word in [
        "facility", "facilities", "service", "services"
    ]):
        return (
            f"{hospital_name} currently lists these services: "
            f"{info['services']}\n\n"
            f"{info['facilities']}"
        )

    # Contact
    if any(word in text for word in [
        "phone", "telephone", "call", "contact"
    ]):
        return (
            f"The demo contact number listed for {hospital_name} is "
            f"{info['phone']}."
        )

    return (
        "I can help with appointment information, preparation, parking, "
        "doctors, appointment times, payment, facilities, hospital location, "
        "and hospital visit guidance. Please choose one of the options above."
    )


def show_hospital_messages():

    st.markdown(
        '<div class="logo">✦ MOMI ✦</div>',
        unsafe_allow_html=True
    )

    st.markdown("# 💌 Hospital Assistant")
    st.caption("Hospital Guide & Support")

    show_momi()

    if "hospital_selected_for_assistant" not in st.session_state:
        st.session_state.hospital_selected_for_assistant = None

    if "hospital_chat" not in st.session_state:
        st.session_state.hospital_chat = []

    selected_hospital = st.session_state.hospital_selected_for_assistant

    # ------------------------------------------
    # Hospital selection
    # ------------------------------------------

    if selected_hospital is None:

        st.write("")

        with st.container(border=True):
            st.markdown("### 🏥 Which hospital would you like to ask about?")

        st.write("")

        hospitals = list(st.session_state.hospital_data.keys())

        for row in range(0, len(hospitals), 2):
            col1, col2 = st.columns(2)

            for col, hospital_index in zip(
                [col1, col2],
                range(row, min(row + 2, len(hospitals)))
            ):
                hospital = hospitals[hospital_index]

                with col:
                    if st.button(
                        f"🏥 {hospital}",
                        key=f"assistant_hospital_{hospital_index}",
                        use_container_width=True
                    ):
                        st.session_state.hospital_selected_for_assistant = hospital
                        st.session_state.hospital_chat = [
                            {
                                "role": "assistant",
                                "content": (
                                    f"🏥 {hospital}\n\n"
                                    "💬 How can I help you today?"
                                )
                            }
                        ]
                        st.rerun()

        st.write("")

        if st.button("← BACK TO HOSPITAL", use_container_width=True):
            st.session_state.page = "hospital"
            st.rerun()

        return

    # ------------------------------------------
    # Selected hospital
    # ------------------------------------------

    st.write("")

    with st.container(border=True):
        st.caption("SELECTED HOSPITAL")
        st.markdown(f"### 🏥 {selected_hospital}")

    st.write("")

    if st.button("← BACK TO HOSPITAL LIST", use_container_width=True):
        st.session_state.hospital_selected_for_assistant = None
        st.session_state.hospital_chat = []
        st.rerun()

    st.write("")

    # ------------------------------------------
    # Chat history
    # ------------------------------------------

    for message in st.session_state.hospital_chat:
        if message["role"] == "user":
            with st.container(border=True):
                st.caption("YOU")
                st.write(message["content"])
        else:
            with st.container(border=True):
                st.caption("🏥 HOSPITAL ASSISTANT")
                st.markdown(message["content"])

        st.write("")

    # ------------------------------------------
    # Quick questions
    # ------------------------------------------

    st.markdown("### 💬 How can I help you today?")

    quick_questions = [
        ("📅 Appointment Information", "appointment information"),
        ("📋 What should I bring?", "what should I bring?"),
        ("🏥 Hospital Visit Guide", "hospital visit guide"),
        ("🅿️ Parking & Arrival", "parking and arrival"),
        ("💳 Payment Information", "payment information"),
        ("👨‍⚕️ Doctor Information", "doctor information"),
        ("⏰ Appointment Time", "appointment time"),
        ("🏢 Hospital Facilities", "hospital facilities"),
        ("❓ Other Questions", "other questions")
    ]

    for row in range(0, len(quick_questions), 2):
        col1, col2 = st.columns(2)

        for col, question_index in zip(
            [col1, col2],
            range(row, min(row + 2, len(quick_questions)))
        ):
            label, question = quick_questions[question_index]

            with col:
                if st.button(
                    label,
                    key=f"hospital_quick_{question_index}",
                    use_container_width=True
                ):

                    if question == "other questions":
                        st.session_state.hospital_other_question_mode = True
                    else:
                        st.session_state.hospital_chat.append({
                            "role": "user",
                            "content": question
                        })

                        st.session_state.hospital_chat.append({
                            "role": "assistant",
                            "content": hospital_assistant_reply(
                                question,
                                selected_hospital
                            )
                        })

                    st.rerun()

    # ------------------------------------------
    # Other Questions
    # ------------------------------------------

    if st.session_state.get("hospital_other_question_mode", False):

        st.write("")

        with st.container(border=True):
            st.markdown("### 💬 Ask the Hospital Assistant")

            other_question = st.text_input(
                "",
                placeholder="Type your question here...",
                key="hospital_other_question"
            )

            if st.button(
                "SEND",
                key="send_hospital_other_question",
                use_container_width=True
            ):

                if other_question.strip():

                    st.session_state.hospital_chat.append({
                        "role": "user",
                        "content": other_question.strip()
                    })

                    st.session_state.hospital_chat.append({
                        "role": "assistant",
                        "content": hospital_assistant_reply(
                            other_question,
                            selected_hospital
                        )
                    })

                    st.session_state.hospital_other_question_mode = False
                    st.rerun()

        st.write("")

        if st.button(
            "CANCEL",
            key="cancel_hospital_other_question",
            use_container_width=True
        ):
            st.session_state.hospital_other_question_mode = False
            st.rerun()

    st.write("")

    if st.button("← BACK TO HOME", use_container_width=True):
        st.session_state.hospital_selected_for_assistant = None
        st.session_state.hospital_chat = []
        st.session_state.hospital_other_question_mode = False
        st.session_state.page = "home"
        st.rerun()


# ==========================================
# 👥 PEER COMPARISON
# ==========================================

def show_peer_comparison():

    st.markdown(
        '<div class="logo">✦ MOMI ✦</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        "# 👥 Peer Comparison"
    )

    st.caption(
        "Compare your health checkup values with a reference group"
    )

    show_momi()

    st.write("")

    # ------------------------------------------
    # LOAD REFERENCE DATA
    # ------------------------------------------

    try:
        try:
            peer_df = pd.read_csv("data/momi_peer_reference_data.csv")
            indicator_df = pd.read_csv("data/momi_peer_indicator_info.csv")
        except FileNotFoundError:
            peer_df = pd.read_csv("momi_peer_reference_data.csv")
            indicator_df = pd.read_csv("momi_peer_indicator_info.csv")
    except Exception:

        with st.container(border=True):

            st.markdown("### 🌱 Reference data is not available")

            st.write(
                "Please place the Peer Comparison CSV files in the data folder."
            )

        st.write("")

        if st.button("← BACK TO HEALTH", use_container_width=True):
            st.session_state.page = "health"
            st.rerun()

        return

    # ------------------------------------------
    # CURRENT PREGNANCY WEEK
    # ------------------------------------------

    current_week = int(st.session_state.pregnancy_week)

    with st.container(border=True):

        st.caption("YOUR PREGNANCY WEEK")

        st.markdown(
            f"### Week {current_week}"
        )

        st.write(
            "Your comparison group is matched to your current pregnancy week."
        )

    st.write("")

    # ------------------------------------------
    # INDICATOR INFORMATION
    # ------------------------------------------

    indicator_map = dict(
        zip(
            indicator_df["column_name"],
            indicator_df["display_name"]
        )
    )

    unit_map = dict(
        zip(
            indicator_df["column_name"],
            indicator_df["unit"]
        )
    )

    fields = [
        ("height_cm", "Height", "cm", 100.0, 220.0, 0.1),
        ("weight_kg", "Weight", "kg", 30.0, 200.0, 0.1),
        ("waist_cm", "Waist", "cm", 30.0, 180.0, 0.1),
        ("bmi", "BMI", "kg/m²", 10.0, 60.0, 0.1),
        ("systolic_bp_mmhg", "Systolic BP", "mmHg", 50.0, 250.0, 1.0),
        ("diastolic_bp_mmhg", "Diastolic BP", "mmHg", 30.0, 160.0, 1.0),
        ("hemoglobin_g_dl", "Hemoglobin", "g/dL", 5.0, 25.0, 0.1),
        ("fasting_glucose_mg_dl", "Fasting Glucose", "mg/dL", 40.0, 300.0, 1.0),
        ("hba1c_percent", "HbA1c", "%", 2.0, 15.0, 0.1),
        ("total_cholesterol_mg_dl", "Total Cholesterol", "mg/dL", 50.0, 400.0, 1.0),
        ("hdl_cholesterol_mg_dl", "HDL Cholesterol", "mg/dL", 10.0, 150.0, 1.0),
        ("triglycerides_mg_dl", "Triglycerides", "mg/dL", 20.0, 500.0, 1.0),
        ("ldl_cholesterol_mg_dl", "LDL Cholesterol", "mg/dL", 10.0, 300.0, 1.0),
        ("hs_crp_mg_l", "hs-CRP", "mg/L", 0.0, 50.0, 0.1),
        ("ast_u_l", "AST", "U/L", 1.0, 200.0, 1.0),
        ("alt_u_l", "ALT", "U/L", 1.0, 200.0, 1.0),
        ("ggt_u_l", "γ-GTP", "U/L", 1.0, 200.0, 1.0)
    ]

    # ------------------------------------------
    # HEALTH CHECKUP RECORD
    # ------------------------------------------

    with st.container(border=True):

        st.markdown("### 🩷 HEALTH CHECKUP RECORD")

        st.caption(
            "Enter the values from your health checkup sheet."
        )

        existing = st.session_state.peer_user_values

        user_values = {}

        for index, field in enumerate(fields):

            column_name, display_name, unit, minimum, maximum, step = field

            saved_value = existing.get(column_name, None)

            default_value = float(saved_value) if saved_value is not None else float(minimum)

            value = st.number_input(
                f"{display_name} ({unit})",
                min_value=minimum,
                max_value=maximum,
                value=default_value,
                step=step,
                key=f"peer_input_{column_name}"
            )

            user_values[column_name] = value

    st.write("")

    if st.button(
        "💾 SAVE HEALTH CHECKUP",
        use_container_width=True
    ):

        st.session_state.peer_user_values = user_values.copy()

        st.success(
            "Your health checkup values have been saved for comparison. 🌷"
        )

        st.rerun()

    st.write("")

    # ------------------------------------------
    # USE SAVED VALUES
    # ------------------------------------------

    saved = st.session_state.peer_user_values

    if not saved:

        with st.container(border=True):

            st.markdown("### 🌱 Ready when you are")

            st.write(
                "Enter your health checkup values above and save them to see your comparison charts."
            )

        st.write("")

        if st.button("← BACK TO HEALTH", use_container_width=True):
            st.session_state.page = "health"
            st.rerun()

        return

    # ------------------------------------------
    # SAME-WEEK REFERENCE GROUP
    # ------------------------------------------

    week_df = peer_df[
        peer_df["pregnancy_week"] == current_week
    ].copy()

    if week_df.empty:

        with st.container(border=True):

            st.markdown("### 🌱 No reference group found")

            st.write(
                f"There is no reference data available for Week {current_week}."
            )

        st.write("")

        if st.button("← BACK TO HEALTH", use_container_width=True):
            st.session_state.page = "health"
            st.rerun()

        return

    # ------------------------------------------
    # SUMMARY TABLE
    # ------------------------------------------

    summary_rows = []

    for column_name, display_name, unit, *_ in fields:

        if column_name not in saved or column_name not in week_df.columns:
            continue

        values = pd.to_numeric(
            week_df[column_name],
            errors="coerce"
        ).dropna()

        if values.empty:
            continue

        user_value = float(saved[column_name])

        summary_rows.append({
            "Indicator": indicator_map.get(column_name, display_name),
            "Your Value": round(user_value, 2),
            "Peer Average": round(float(values.mean()), 2),
            "Peer Median": round(float(values.median()), 2),
            "Peer Min": round(float(values.min()), 2),
            "Peer Q1": round(float(values.quantile(0.25)), 2),
            "Peer Q3": round(float(values.quantile(0.75)), 2),
            "Peer Max": round(float(values.max()), 2),
            "Unit": unit_map.get(column_name, unit)
        })

    summary_df = pd.DataFrame(summary_rows)

    with st.container(border=True):

        st.markdown("### 📋 YOUR SUMMARY")

        st.dataframe(
            summary_df,
            use_container_width=True,
            hide_index=True
        )

    st.write("")

    # ------------------------------------------
    # CHART INDICATOR SELECTOR
    # ------------------------------------------

    chart_columns = [
        field[0]
        for field in fields
        if field[0] in saved and field[0] in week_df.columns
    ]

    chart_labels = [
        indicator_map.get(
            column_name,
            next(field[1] for field in fields if field[0] == column_name)
        )
        for column_name in chart_columns
    ]

    selected_label = st.selectbox(
        "Select an indicator",
        chart_labels,
        key="peer_selected_indicator"
    )

    selected_column = chart_columns[chart_labels.index(selected_label)]
    selected_unit = unit_map.get(
        selected_column,
        next(field[2] for field in fields if field[0] == selected_column)
    )

    selected_peer_values = pd.to_numeric(
        week_df[selected_column],
        errors="coerce"
    ).dropna()

    selected_user_value = float(saved[selected_column])

    peer_mean = float(selected_peer_values.mean())
    peer_median = float(selected_peer_values.median())
    peer_min = float(selected_peer_values.min())
    peer_max = float(selected_peer_values.max())
    peer_q1 = float(selected_peer_values.quantile(0.25))
    peer_q3 = float(selected_peer_values.quantile(0.75))

    percentile = float(
        (selected_peer_values <= selected_user_value).mean() * 100
    )

    # ------------------------------------------
    # YOUR POSITION
    # ------------------------------------------

    with st.container(border=True):

        st.markdown("### 📍 YOUR POSITION")

        position_df = pd.DataFrame({
            "Metric": [selected_label],
            "Your Value": [selected_user_value],
            "Peer Average": [peer_mean],
            "Peer Median": [peer_median]
        })

        position_chart = alt.Chart(position_df).transform_fold(
            ["Your Value", "Peer Average", "Peer Median"],
            as_=["Type", "Value"]
        ).mark_bar(
            cornerRadiusTopLeft=8,
            cornerRadiusTopRight=8
        ).encode(
            x=alt.X("Type:N", title=None, sort=["Your Value", "Peer Average", "Peer Median"]),
            y=alt.Y("Value:Q", title=selected_unit),
            color=alt.Color(
                "Type:N",
                title=None,
                scale=alt.Scale(range=[PEER_PINK, PEER_LAVENDER, PEER_MINT])
            ),
            tooltip=[
                alt.Tooltip("Type:N", title="Measure"),
                alt.Tooltip("Value:Q", title="Value", format=".2f")
            ]
        ).properties(height=260)

        st.altair_chart(
            position_chart,
            use_container_width=True
        )

        st.write(
            f"Your Value: {selected_user_value:.2f} {selected_unit} · "
            f"Peer Average: {peer_mean:.2f} {selected_unit} · "
            f"Peer Median: {peer_median:.2f} {selected_unit}"
        )

        st.caption(
            f"Your percentile position within the Week {current_week} reference group: {percentile:.0f}th"
        )

    st.write("")

    # ------------------------------------------
    # 1. BAR CHART
    # ------------------------------------------

    st.markdown("### 📊 YOUR VALUE vs PEER AVERAGE")

    bar_df = pd.DataFrame({
        "Measure": ["Your Value", "Peer Average"],
        "Value": [selected_user_value, peer_mean]
    })

    bar_chart = alt.Chart(bar_df).mark_bar(
        cornerRadiusTopLeft=10,
        cornerRadiusTopRight=10
    ).encode(
        x=alt.X("Measure:N", title=None),
        y=alt.Y("Value:Q", title=selected_unit),
        color=alt.Color(
            "Measure:N",
            scale=alt.Scale(range=[PEER_PINK, PEER_LAVENDER]),
            legend=None
        ),
        tooltip=[
            alt.Tooltip("Measure:N", title="Measure"),
            alt.Tooltip("Value:Q", title="Value", format=".2f")
        ]
    ).properties(height=280)

    st.altair_chart(bar_chart, use_container_width=True)

    st.write("")

    # ------------------------------------------
    # 2. LINE CHART - WEEKLY REFERENCE TREND
    # ------------------------------------------

    st.markdown("### 📈 PREGNANCY-WEEK TREND")

    trend_df = (
        peer_df.groupby("pregnancy_week")[selected_column]
        .agg(["mean", "median"])
        .reset_index()
        .rename(columns={"mean": "Peer Average", "median": "Peer Median"})
    )

    trend_long = trend_df.melt(
        id_vars=["pregnancy_week"],
        value_vars=["Peer Average", "Peer Median"],
        var_name="Measure",
        value_name="Value"
    )

    line_chart = alt.Chart(trend_long).mark_line(
        point=True
    ).encode(
        x=alt.X("pregnancy_week:Q", title="Pregnancy Week"),
        y=alt.Y("Value:Q", title=selected_unit),
        color=alt.Color(
            "Measure:N",
            title=None,
            scale=alt.Scale(range=[PEER_LAVENDER, PEER_MINT])
        ),
        tooltip=[
            alt.Tooltip("pregnancy_week:Q", title="Week"),
            alt.Tooltip("Measure:N", title="Measure"),
            alt.Tooltip("Value:Q", title="Value", format=".2f")
        ]
    ).properties(height=280)

    user_week_df = pd.DataFrame({
        "pregnancy_week": [current_week],
        "Value": [selected_user_value]
    })

    user_week_point = alt.Chart(user_week_df).mark_point(
        size=160,
        filled=True,
        color=PEER_PINK
    ).encode(
        x="pregnancy_week:Q",
        y="Value:Q",
        tooltip=[
            alt.Tooltip("pregnancy_week:Q", title="Week"),
            alt.Tooltip("Value:Q", title="Your Value", format=".2f")
        ]
    )

    st.altair_chart(
        line_chart + user_week_point,
        use_container_width=True
    )

    st.write("")

    # ------------------------------------------
    # 3. DONUT CHART - PERCENTILE POSITION
    # ------------------------------------------

    st.markdown("### 🍩 YOUR POSITION IN THE PEER GROUP")

    donut_value = max(0.0, min(100.0, percentile))

    donut_df = pd.DataFrame({
        "Part": ["Your percentile position", "Remaining range"],
        "Value": [donut_value, 100.0 - donut_value]
    })

    donut_chart = alt.Chart(donut_df).mark_arc(
        innerRadius=70,
        outerRadius=105
    ).encode(
        theta=alt.Theta("Value:Q"),
        color=alt.Color(
            "Part:N",
            title=None,
            scale=alt.Scale(range=[PEER_PINK, "#F4EDF8"]),
            legend=None
        ),
        tooltip=[
            alt.Tooltip("Part:N", title="Part"),
            alt.Tooltip("Value:Q", title="Percent", format=".0f")
        ]
    ).properties(height=280)

    st.altair_chart(donut_chart, use_container_width=True)

    st.caption(
        f"Your value is at approximately the {percentile:.0f}th percentile of the Week {current_week} reference group."
    )

    st.write("")

    # ------------------------------------------
    # 4. BOX-AND-WHISKER
    # ------------------------------------------

    st.markdown("### 📦 PEER DISTRIBUTION")

    box_df = week_df[[selected_column]].copy()
    box_df["Group"] = "Peer Group"

    box_chart = alt.Chart(box_df).mark_boxplot(
        size=60,
        extent="min-max"
    ).encode(
        x=alt.X("Group:N", title=None),
        y=alt.Y(selected_column + ":Q", title=selected_unit),
        tooltip=[
            alt.Tooltip(selected_column + ":Q", title="Peer Value", format=".2f")
        ]
    )

    user_box_df = pd.DataFrame({
        "Group": ["Peer Group"],
        "Value": [selected_user_value]
    })

    user_point = alt.Chart(user_box_df).mark_point(
        size=180,
        filled=True,
        color=PEER_PINK
    ).encode(
        x=alt.X("Group:N", title=None),
        y=alt.Y("Value:Q", title=selected_unit),
        tooltip=[
            alt.Tooltip("Value:Q", title="Your Value", format=".2f")
        ]
    )

    st.altair_chart(
        box_chart + user_point,
        use_container_width=True
    )

    st.caption(
        f"Peer range: {peer_min:.2f}–{peer_max:.2f} {selected_unit} · "
        f"Q1: {peer_q1:.2f} · Q3: {peer_q3:.2f}"
    )

    st.write("")

    # ------------------------------------------
    # 5. SCATTER PLOT
    # ------------------------------------------

    st.markdown("### 🔵 RELATED INDICATORS")

    scatter_options = [
        ("bmi", "BMI", "kg/m²", "weight_kg", "Weight", "kg"),
        ("bmi", "BMI", "kg/m²", "waist_cm", "Waist", "cm"),
        ("weight_kg", "Weight", "kg", "waist_cm", "Waist", "cm")
    ]

    scatter_labels = [
        f"{left_label} vs {right_label}"
        for _, left_label, _, _, right_label, _ in scatter_options
    ]

    scatter_label = st.selectbox(
        "Select a related pair",
        scatter_labels,
        key="peer_scatter_pair"
    )

    scatter_index = scatter_labels.index(scatter_label)
    x_col, x_label, x_unit, y_col, y_label, y_unit = scatter_options[scatter_index]

    scatter_peer_df = week_df[[x_col, y_col]].dropna().copy()
    scatter_peer_df["Group"] = "Peer Group"

    scatter_chart = alt.Chart(scatter_peer_df).mark_circle(
        size=80,
        opacity=0.65,
        color=PEER_MINT
    ).encode(
        x=alt.X(x_col + ":Q", title=f"{x_label} ({x_unit})"),
        y=alt.Y(y_col + ":Q", title=f"{y_label} ({y_unit})"),
        tooltip=[
            alt.Tooltip(x_col + ":Q", title=x_label, format=".2f"),
            alt.Tooltip(y_col + ":Q", title=y_label, format=".2f")
        ]
    ).properties(height=300)

    user_scatter_df = pd.DataFrame({
        x_col: [float(saved[x_col])],
        y_col: [float(saved[y_col])]
    })

    user_scatter_point = alt.Chart(user_scatter_df).mark_point(
        size=220,
        filled=True,
        shape="diamond",
        color=PEER_PINK
    ).encode(
        x=x_col + ":Q",
        y=y_col + ":Q",
        tooltip=[
            alt.Tooltip(x_col + ":Q", title="Your " + x_label, format=".2f"),
            alt.Tooltip(y_col + ":Q", title="Your " + y_label, format=".2f")
        ]
    )

    st.altair_chart(
        scatter_chart + user_scatter_point,
        use_container_width=True
    )

    st.write("")

    # ------------------------------------------
    # 6. GROUPED BAR - BLOOD PRESSURE
    # ------------------------------------------

    st.markdown("### 🩷 BLOOD PRESSURE COMPARISON")

    bp_rows = [
        {
            "Measure": "Systolic BP",
            "Type": "Your Value",
            "Value": float(saved["systolic_bp_mmhg"])
        },
        {
            "Measure": "Systolic BP",
            "Type": "Peer Average",
            "Value": float(week_df["systolic_bp_mmhg"].mean())
        },
        {
            "Measure": "Diastolic BP",
            "Type": "Your Value",
            "Value": float(saved["diastolic_bp_mmhg"])
        },
        {
            "Measure": "Diastolic BP",
            "Type": "Peer Average",
            "Value": float(week_df["diastolic_bp_mmhg"].mean())
        }
    ]

    bp_df = pd.DataFrame(bp_rows)

    bp_chart = alt.Chart(bp_df).mark_bar(
        cornerRadiusTopLeft=8,
        cornerRadiusTopRight=8
    ).encode(
        x=alt.X("Measure:N", title=None),
        xOffset=alt.XOffset("Type:N", title=None),
        color=alt.Color(
            "Type:N",
            title=None,
            scale=alt.Scale(range=[PEER_PEACH, PEER_LAVENDER])
        ),
        y=alt.Y("Value:Q", title="mmHg"),
        tooltip=[
            alt.Tooltip("Measure:N", title="Measure"),
            alt.Tooltip("Type:N", title="Type"),
            alt.Tooltip("Value:Q", title="Value", format=".1f")
        ]
    ).properties(height=300)

    st.altair_chart(bp_chart, use_container_width=True)

    st.write("")

    # ------------------------------------------
    # 7. BULLET / GAUGE STYLE PERCENTILE
    # ------------------------------------------

    st.markdown("### 🎯 PEER POSITION SCALE")

    gauge_base = pd.DataFrame({
        "Start": [0],
        "End": [100]
    })

    gauge = alt.Chart(gauge_base).mark_bar(
        height=28,
        cornerRadius=14,
        color=PEER_LILAC
    ).encode(
        x=alt.X("Start:Q", scale=alt.Scale(domain=[0, 100]), title="Percentile"),
        x2="End:Q",
        y=alt.value(0)
    )

    gauge_point = alt.Chart(
        pd.DataFrame({"Percentile": [percentile]})
    ).mark_rule(
        strokeWidth=5,
        color=PEER_PINK
    ).encode(
        x=alt.X("Percentile:Q", scale=alt.Scale(domain=[0, 100]), title=None),
        size=alt.value(8),
        tooltip=[
            alt.Tooltip("Percentile:Q", title="Your Percentile", format=".0f")
        ]
    ).properties(height=70)

    st.altair_chart(
        gauge + gauge_point,
        use_container_width=True
    )

    st.caption(
        "0 = lower end of the reference distribution · 50 = middle · 100 = upper end · This is a percentile position, not a health score."
    )

    st.write("")

    if st.button("← BACK TO HEALTH", use_container_width=True):

        st.session_state.page = "health"

        st.rerun()


# ==========================================
# 🤖 AI ML FUTURE SIZE
# Random Forest Regression for clothing planning
# ==========================================

@st.cache_resource

def train_future_size_model():
    """
    Train Random Forest models once and reuse them during the Streamlit session.
    The CSV contains prototype synthetic longitudinal pregnancy data.
    """

    data_path = "pregnancy_body_training_data.csv"

    df = pd.read_csv(data_path)

    required_columns = [
        "mother_id",
        "height_cm",
        "current_week",
        "current_weight_kg",
        "current_waist_cm",
        "target_week",
        "target_weight_kg",
        "target_waist_cm"
    ]

    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing columns in pregnancy_body_training_data.csv: "
            + ", ".join(missing_columns)
        )

    feature_columns = [
        "height_cm",
        "current_week",
        "current_weight_kg",
        "current_waist_cm",
        "target_week"
    ]

    target_columns = [
        "target_weight_kg",
        "target_waist_cm"
    ]

    X = df[feature_columns]
    y = df[target_columns]
    groups = df["mother_id"]

    # Keep the same mother in only one side of the test split.
    splitter = GroupShuffleSplit(
        n_splits=1,
        test_size=0.2,
        random_state=20260928
    )

    train_index, test_index = next(
        splitter.split(X, y, groups=groups)
    )

    X_train = X.iloc[train_index]
    X_test = X.iloc[test_index]
    y_train = y.iloc[train_index]
    y_test = y.iloc[test_index]

    weight_model = RandomForestRegressor(
        n_estimators=300,
        random_state=20260928,
        min_samples_leaf=2,
        n_jobs=-1
    )

    waist_model = RandomForestRegressor(
        n_estimators=300,
        random_state=20260928,
        min_samples_leaf=2,
        n_jobs=-1
    )

    weight_model.fit(
        X_train,
        y_train["target_weight_kg"]
    )

    waist_model.fit(
        X_train,
        y_train["target_waist_cm"]
    )

    weight_prediction = weight_model.predict(X_test)
    waist_prediction = waist_model.predict(X_test)

    metrics = {
        "weight_mae": mean_absolute_error(
            y_test["target_weight_kg"],
            weight_prediction
        ),
        "weight_rmse": mean_squared_error(
            y_test["target_weight_kg"],
            weight_prediction
        ) ** 0.5,
        "weight_r2": r2_score(
            y_test["target_weight_kg"],
            weight_prediction
        ),
        "waist_mae": mean_absolute_error(
            y_test["target_waist_cm"],
            waist_prediction
        ),
        "waist_rmse": mean_squared_error(
            y_test["target_waist_cm"],
            waist_prediction
        ) ** 0.5,
        "waist_r2": r2_score(
            y_test["target_waist_cm"],
            waist_prediction
        )
    }

    return weight_model, waist_model, metrics


def get_momi_size(height_cm, weight_kg, waist_cm, clothing_type):
    """
    MOMI's approximate ready-to-wear reference.
    This is a clothing-planning rule, not a medical or brand-specific size chart.
    """

    # Each category keeps the same six MOMI size labels while allowing
    # small fit differences between clothing types.
    size_ranges = {
        "Panty": [
            ("S", 150, 170, 45, 55, 68, 74),
            ("M", 150, 175, 52, 63, 74, 80),
            ("L", 155, 178, 60, 72, 80, 88),
            ("XL", 155, 180, 69, 82, 88, 96),
            ("XXL", 158, 185, 78, 94, 96, 106),
            ("XXXL", 158, 190, 90, 110, 106, 125)
        ],
        "T-shirt": [
            ("S", 150, 170, 45, 55, 68, 74),
            ("M", 155, 175, 52, 64, 74, 81),
            ("L", 158, 180, 60, 73, 81, 89),
            ("XL", 158, 183, 69, 83, 89, 97),
            ("XXL", 160, 185, 78, 95, 97, 107),
            ("XXXL", 160, 190, 90, 115, 107, 130)
        ],
        "Pants": [
            ("S", 150, 170, 45, 55, 68, 74),
            ("M", 155, 175, 52, 63, 74, 80),
            ("L", 158, 180, 60, 72, 80, 88),
            ("XL", 158, 183, 69, 82, 88, 96),
            ("XXL", 160, 185, 78, 94, 96, 106),
            ("XXXL", 160, 190, 90, 110, 106, 125)
        ],
        "One-piece": [
            ("S", 150, 168, 45, 55, 68, 74),
            ("M", 153, 173, 52, 63, 74, 81),
            ("L", 156, 178, 60, 72, 81, 89),
            ("XL", 158, 182, 69, 83, 89, 97),
            ("XXL", 160, 185, 78, 95, 97, 107),
            ("XXXL", 160, 190, 90, 115, 107, 130)
        ]
    }

    ranges = size_ranges[clothing_type]

    # Choose the smallest size that contains the predicted measurements.
    for size, min_height, max_height, min_weight, max_weight, min_waist, max_waist in ranges:
        height_ok = min_height <= height_cm <= max_height
        weight_ok = min_weight <= weight_kg <= max_weight
        waist_ok = min_waist <= waist_cm <= max_waist

        if height_ok and weight_ok and waist_ok:
            return size

    # If measurements fall outside a combined range, use waist as the
    # strongest fit signal and keep the recommendation inside S–XXXL.
    if waist_cm < 74:
        return "S"
    if waist_cm < 80:
        return "M"
    if waist_cm < 88:
        return "L"
    if waist_cm < 96:
        return "XL"
    if waist_cm < 106:
        return "XXL"
    return "XXXL"


def show_size_guide_table(clothing_type):
    """Display a compact shopping-style MOMI size reference table."""

    guide_data = {
        "Panty": [
            ["S", "150–170", "45–55", "68–74"],
            ["M", "150–175", "52–63", "74–80"],
            ["L", "155–178", "60–72", "80–88"],
            ["XL", "155–180", "69–82", "88–96"],
            ["XXL", "158–185", "78–94", "96–106"],
            ["XXXL", "158–190", "90–110", "106–125"]
        ],
        "T-shirt": [
            ["S", "150–170", "45–55", "68–74"],
            ["M", "155–175", "52–64", "74–81"],
            ["L", "158–180", "60–73", "81–89"],
            ["XL", "158–183", "69–83", "89–97"],
            ["XXL", "160–185", "78–95", "97–107"],
            ["XXXL", "160–190", "90–115", "107–130"]
        ],
        "Pants": [
            ["S", "150–170", "45–55", "68–74"],
            ["M", "155–175", "52–63", "74–80"],
            ["L", "158–180", "60–72", "80–88"],
            ["XL", "158–183", "69–82", "88–96"],
            ["XXL", "160–185", "78–94", "96–106"],
            ["XXXL", "160–190", "90–110", "106–125"]
        ],
        "One-piece": [
            ["S", "150–168", "45–55", "68–74"],
            ["M", "153–173", "52–63", "74–81"],
            ["L", "156–178", "60–72", "81–89"],
            ["XL", "158–182", "69–83", "89–97"],
            ["XXL", "160–185", "78–95", "97–107"],
            ["XXXL", "160–190", "90–115", "107–130"]
        ]
    }

    table_df = pd.DataFrame(
        guide_data[clothing_type],
        columns=["Size", "Height (cm)", "Weight (kg)", "Waist (cm)"]
    )

    st.dataframe(
        table_df,
        use_container_width=True,
        hide_index=True
    )


def show_health_trend():

    st.markdown(
        '<div class="logo">✦ MOMI ✦</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        "# 🤖 AI ML FUTURE SIZE"
    )

    st.caption(
        "Plan clothing ahead with a machine learning body forecast"
    )

    show_momi()

    st.write("")

    with st.container(border=True):
        st.markdown("### 🧠 MACHINE LEARNING MODEL")
        st.write("Random Forest Regression")
        st.caption(
            "The model predicts future weight and waist measurements "
            "from pregnancy data and a target week."
        )

    st.write("")

    try:
        weight_model, waist_model, metrics = train_future_size_model()
    except FileNotFoundError:
        with st.container(border=True):
            st.markdown("### ⚠️ Training data not found")
            st.write(
                "Please place pregnancy_body_training_data.csv in the "
                "same project folder as app.py."
            )
        if st.button("← BACK TO HEALTH", use_container_width=True):
            st.session_state.page = "health"
            st.rerun()
        return
    except Exception as error:
        with st.container(border=True):
            st.markdown("### ⚠️ Model setup error")
            st.write(str(error))
        if st.button("← BACK TO HEALTH", use_container_width=True):
            st.session_state.page = "health"
            st.rerun()
        return

    current_week = int(st.session_state.pregnancy_week)

    st.markdown("### 🌷 CURRENT PREGNANCY INFORMATION")

    col1, col2 = st.columns(2)

    with col1:
        input_week = st.number_input(
            "Pregnancy Week",
            min_value=1,
            max_value=40,
            value=current_week,
            step=1,
            key="future_size_current_week"
        )

        height_cm = st.number_input(
            "Height (cm)",
            min_value=130.0,
            max_value=210.0,
            value=163.0,
            step=0.5,
            key="future_size_height"
        )

    with col2:
        current_weight = st.number_input(
            "Current Weight (kg)",
            min_value=30.0,
            max_value=200.0,
            value=60.0,
            step=0.1,
            key="future_size_weight"
        )

        current_waist = st.number_input(
            "Current Waist (cm)",
            min_value=50.0,
            max_value=180.0,
            value=82.0,
            step=0.1,
            key="future_size_waist"
        )

    target_week = st.number_input(
        "Target Week",
        min_value=int(input_week),
        max_value=40,
        value=min(max(int(input_week), int(input_week)), 40),
        step=1,
        key="future_size_target_week"
    )

    st.caption(
        "Choose the pregnancy week when you expect to wear the clothing."
    )

    st.write("")

    if st.button(
        "✨ PREDICT FUTURE SIZE",
        use_container_width=True
    ):
        input_data = pd.DataFrame([{
            "height_cm": float(height_cm),
            "current_week": float(input_week),
            "current_weight_kg": float(current_weight),
            "current_waist_cm": float(current_waist),
            "target_week": float(target_week)
        }])

        if int(target_week) == int(input_week):
            predicted_weight = float(current_weight)
            predicted_waist = float(current_waist)
        else:
            predicted_weight = float(weight_model.predict(input_data)[0])
            predicted_waist = float(waist_model.predict(input_data)[0])

        predicted_weight = max(predicted_weight, 0.0)
        predicted_waist = max(predicted_waist, 0.0)

        recommendations = {
            clothing: get_momi_size(
                float(height_cm),
                predicted_weight,
                predicted_waist,
                clothing
            )
            for clothing in [
                "Panty",
                "T-shirt",
                "Pants",
                "One-piece"
            ]
        }

        st.session_state.future_size_result = {
            "target_week": int(target_week),
            "predicted_weight": predicted_weight,
            "predicted_waist": predicted_waist,
            "recommendations": recommendations
        }

    result = st.session_state.get("future_size_result")

    if result:
        st.write("")

        st.markdown("### ✨ FUTURE BODY FORECAST")

        with st.container(border=True):
            st.caption(
                f"TARGET WEEK · {result['target_week']}"
            )

            result_col1, result_col2 = st.columns(2)

            with result_col1:
                st.metric(
                    "Predicted Weight",
                    f"{result['predicted_weight']:.1f} kg"
                )

            with result_col2:
                st.metric(
                    "Predicted Waist",
                    f"{result['predicted_waist']:.1f} cm"
                )

        st.write("")

        st.markdown("### 🛍️ MOMI RECOMMENDED SIZE")

        size_col1, size_col2 = st.columns(2)

        recommendation_items = [
            ("👙 Panty", result["recommendations"]["Panty"]),
            ("👕 T-shirt", result["recommendations"]["T-shirt"]),
            ("👖 Pants", result["recommendations"]["Pants"]),
            ("👗 One-piece", result["recommendations"]["One-piece"])
        ]

        for index, (label, size) in enumerate(recommendation_items):
            target_col = size_col1 if index % 2 == 0 else size_col2
            with target_col:
                with st.container(border=True):
                    st.caption(label)
                    st.markdown(f"### {size}")

        st.write("")

        st.markdown("### 📏 MOMI SIZE GUIDE")
        st.caption(
            "Approximate ready-to-wear reference. Actual fit may vary by brand and design."
        )

        guide_tab1, guide_tab2, guide_tab3, guide_tab4 = st.tabs([
            "👙 Panty",
            "👕 T-shirt",
            "👖 Pants",
            "👗 One-piece"
        ])

        with guide_tab1:
            show_size_guide_table("Panty")

        with guide_tab2:
            show_size_guide_table("T-shirt")

        with guide_tab3:
            show_size_guide_table("Pants")

        with guide_tab4:
            show_size_guide_table("One-piece")

        st.caption(
            "These predictions are estimates for clothing planning only. "
            "Actual body changes may vary."
        )

    st.write("")

    if st.button("← BACK TO HEALTH", use_container_width=True):
        st.session_state.page = "health"
        st.rerun()


# ==========================================
# 임시 세부 화면
# ==========================================

def show_empty_page(title, description):

    st.markdown(
        '<div class="logo">✦ MOMI ✦</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f"# {title}"
    )

    st.caption(
        description
    )

    show_momi()

    st.write("")

    with st.container(border=True):

        st.markdown(
            "### Coming soon 🌷"
        )

        st.write(
            "This page will be ready soon."
        )

    st.write("")

    if st.button("← BACK TO HOME"):

        st.session_state.page = "home"

        st.rerun()


# ==========================================
# 화면 이동
# ==========================================

if st.session_state.page == "signup":

    show_signup()


elif st.session_state.page == "home":

    show_home()


elif st.session_state.page == "welcome":

    show_welcome()


# ==========================================
# TODAY
# ==========================================

elif st.session_state.page == "today":

    show_today()


elif st.session_state.page == "daily_health":

    show_daily_health()


elif st.session_state.page == "weekly_milestone":

    show_milestone_week()


elif st.session_state.page == "next_hospital":

    show_next_hospital_visit()


# ==========================================
# HEALTH
# ==========================================

elif st.session_state.page == "health":

    show_health()


elif st.session_state.page == "health_dashboard":

    show_health_dashboard()


elif st.session_state.page == "peer_comparison":

    show_peer_comparison()


elif st.session_state.page == "health_trend":

    show_health_trend()


# ==========================================
# MILESTONE
# ==========================================

elif st.session_state.page == "milestone":

    show_milestone()


elif st.session_state.page == "milestone_week":

    show_milestone_week()


# ==========================================
# AI
# ==========================================

elif st.session_state.page == "ai":

    show_ai()


elif st.session_state.page == "ai_consultation":

    show_ai_consultation()


# ==========================================
# HOSPITAL
# ==========================================

elif st.session_state.page == "hospital":

    show_hospital()


elif st.session_state.page == "hospital_schedule":

    show_schedule()


elif st.session_state.page == "hospital_appointments":

    show_appointments()


elif st.session_state.page == "hospital_messages":

    show_hospital_messages()