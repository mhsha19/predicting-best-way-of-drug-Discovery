import streamlit as st
import pandas as pd
from PIL import Image
import os
import base64
import pickle


st.markdown("""
    <style>
        body {
            direction: rtl;
            text-align: right;
        }
    </style>
""", unsafe_allow_html=True)

# حساب توصیف‌گر مولکولی
def desc_calc():
    # محاسبه توصیف‌گر را انجام می‌دهد
    from padelpy import padeldescriptor

    input_directory = './'
    output_file = 'descriptors_output.csv'

    padeldescriptor(
        mol_dir=input_directory,
        d_file=output_file,
        fingerprints=True,
        removesalt=True,
        standardizenitro=True,
        descriptortypes='./PaDEL-Descriptor/PubchemFingerprinter.xml',
        maxruntime=1000,
        threads=4
    )
    os.remove('molecule.smi')

# دانلود فایل
def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # **تبدیل رشته‌ها به بایت‌ها و بالعکس**
    href = f'<a href="data:file/csv;base64,{b64}" download="prediction.csv">دانلود پیش‌بینی‌ها</a>'
    return href

# مدل‌سازی
def build_model(input_data):
    # مدل رگرسیون ذخیره‌شده را می‌خواند
    load_model = pickle.load(open('Coronavirus_model.pkl', 'rb'))
    # **اعمال مدل برای انجام پیش‌بینی‌ها**
    prediction = load_model.predict(input_data)
    st.header('**خروجی پیش‌بینی**')
    prediction_output = pd.Series(prediction, name='pIC50')
    molecule_name = pd.Series(load_data[1], name='molecule_name')
    df = pd.concat([molecule_name, prediction_output], axis=1)
    st.write(df)
    st.markdown(filedownload(df), unsafe_allow_html=True)

# تصویر لوگو

image = Image.open('logo.webp')

st.image(image, use_container_width=True)

# عنوان صفحه
st.markdown("""
# برنامه پیش‌بینی زیست فعالی (ویروس کرونا)

این برنامه به شما این امکان را می‌دهد که بیواکتیویته مربوط به مهار آنزیم `ویروس کرونا` را پیش‌بینی کنید. `ویروس کرونا` هدف دارویی برای بیماری آلزایمر است.

**برگرفته از**
- این برنامه با استفاده از `Python` + `Streamlit`  ساخته شده است.
- توصیف‌گر با استفاده از [PaDEL-Descriptor](http://www.yapcwsoft.com/dd/padeldescriptor/) محاسبه شده است [[مطالعه مقاله]](https://doi.org/10.1002/jcc.21707).
---

""")

# نوار کناری
with st.sidebar.header('1.فایل داده CSV خود را بارگذاری کنید'):
    uploaded_file = st.sidebar.file_uploader("فایل ورودی خود را بارگذاری کنید", type=['txt'])
    st.sidebar.markdown("""
[فایل ورودی نمونه](https://github.com/mhsha19/predicting-best-way-of-drug-Discovery/blob/main/example_coronavirus.txt)
""")

if st.sidebar.button('پیش‌بینی'):
    load_data = pd.read_table(uploaded_file, sep=' ', header=None)
    load_data.to_csv('./molecule.smi', sep = '\t', header = False, index = False)

    st.header('**داده‌های ورودی اصلی**')
    st.write(load_data)

    with st.spinner("در حال محاسبه توصیف‌گرها..."):
        desc_calc()

    # خواندن توصیف‌گرهای محاسبه‌شده و نمایش دیتافریم
    st.header('**توصیف‌گرهای مولکولی محاسبه‌شده**')
    desc = pd.read_csv('descriptors_output.csv')
    st.write(desc)
    st.write(desc.shape)

    # خواندن لیست توصیف‌گرهای استفاده‌شده در مدل ساخته‌شده قبلی
    st.header('**زیرمجموعه‌ای از توصیف‌گرها از مدل‌های ساخته‌شده قبلی**')
    Xlist = list(pd.read_csv('descriptor_list.csv').columns)
    desc_subset = desc[Xlist]
    st.write(desc_subset)
    st.write(desc_subset.shape)

    # اعمال مدل آموزش‌دیده برای انجام پیش‌بینی روی ترکیبات
    build_model(desc_subset)
else:
    st.info('برای شروع، داده‌های ورودی را در نوار کناری بارگذاری کنید')
