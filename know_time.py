import streamlit as st
import datetime
import jpholiday
import time
import pandas as pd
import numpy as np
from PIL import Image

st.set_page_config(
    page_title='Know Time',
    page_icon='⏰',
    layout='centered',
    initial_sidebar_state='collapsed',
)

default_categories = ['自由']
default_times = [[12, 12]]
default_time = 12
new_times = [12, 12]
reserve_items = ['未設定', '計測期間', '']

if 'st_date' not in st.session_state:
    st.session_state.st_date = datetime.date.today()
if 'end_date' not in st.session_state:
    st.session_state.end_date = datetime.date.today()

if 'categories' not in st.session_state:
    st.session_state.categories = default_categories
if 'choices' not in st.session_state:
    st.session_state.choices = default_categories
if 'selected' not in st.session_state:
    st.session_state.selected = default_categories
if 'times' not in st.session_state:
    st.session_state.times = default_times
if 'item' not in st.session_state:
    st.session_state.item = ''


image = Image.open('title.png')
st.image(image)


# -------------------
with st.expander('① 計測の期間を設定する'):
    date_sections = st.columns(2)
    date_sections[0].date_input(
        "■ 開始日", key='st_date'
    )
    max_life = 130
    td = datetime.timedelta(days=1)
    date_sections[1].date_input(
        "■ 終了日", key='end_date',
        max_value=datetime.datetime(year=datetime.datetime.today().year+max_life,
                                    month=datetime.datetime.today().month, day=datetime.datetime.today().day)-td)

    if st.session_state.st_date > st.session_state.end_date:
        st.write(
            '<span style="color:red">終了日が開始日より過去です</span>',
            unsafe_allow_html=True)
        uncalculatable = True
        uncalculatable = True
    else:
        uncalculatable = False
# -------------------

# -------------------
with st.expander('② 時間の項目を設定する'):
    category_space = st.columns(1)
    new_item_space = st.columns(1)
    new_item_button_sections = st.columns([2, 1, 1])
    post_button = new_item_button_sections[1].button(
        "　追加　",
    )
    reset_button = new_item_button_sections[2].button(
        "リセット",
    )
    if post_button:
        st.session_state.selected = st.session_state.categories
        if st.session_state.item not in st.session_state.choices \
           and st.session_state.item not in reserve_items \
           and not st.session_state.item.isspace():
            st.session_state.choices.append(st.session_state.item)
            st.session_state.selected.append(st.session_state.item)
            st.session_state.item = ''

    new_item_space[0].text_input(
        label='■ 追加する項目名', key='item', max_chars=15)
    if reset_button:
        del st.session_state.categories, st.session_state.choices, \
            st.session_state.selected, st.session_state.times, \
            st.session_state['left-1'], st.session_state['right-1']
        st.session_state.choices, st.session_state.selected = default_categories, default_categories
        st.session_state.times = default_times

    st.session_state.categories = category_space[0].multiselect(
        '■ 時間の項目一覧', st.session_state.choices, st.session_state.selected)


# -------------------
with st.expander('③ 時間の配分を設定する'):
    left_slider, right_slider = st.columns(2)

    left_weekday_str = '<span style="font-size:24px;font-weight:bold">■ 月〜金（平日）</span>'
    right_weekday_str = '<span style="font-size:24px;font-weight:bold">■ 土・日・祝</span>'
    left_slider.write(left_weekday_str, unsafe_allow_html=True)
    right_slider.write(right_weekday_str, unsafe_allow_html=True)

    left_hold = left_slider.empty()
    right_hold = right_slider.empty()
    left_slider.write('')
    right_slider.write('')

    left_str = '<span style="font-size:24px">■ 月〜金（平日）</span>'

    left_h = 0
    right_h = 0
    alert_str = ' <span style="color:red">1日24時間を超えています</span>'
    for i in range(len(st.session_state.choices)):
        if i == len(st.session_state.times):
            st.session_state.times.append(new_times)

        if 'left-'+str(i+1) not in st.session_state:
            st.session_state['left-'+str(i+1)] = st.session_state.times[i][0]
        if 'right-'+str(i+1) not in st.session_state:
            st.session_state['right-'+str(i+1)] = st.session_state.times[i][1]

        if st.session_state.choices[i] in st.session_state.categories:
            st.session_state.times[i][0] = left_slider.slider(
                '■ ' + st.session_state.choices[i], 0, 24, value=st.session_state['left-'+str(i+1)],  key='left-'+str(i+1))
            st.session_state.times[i][1] = right_slider.slider(
                '■ ' + st.session_state.choices[i], 0, 24, value=st.session_state['right-'+str(i+1)],  key='right-'+str(i+1))
            left_h += st.session_state.times[i][0]
            right_h += st.session_state.times[i][1]

    left_str = '<span style="font-size:24px">[ ' + \
        str(left_h)+' / ' + '24 ]</span>'
    right_str = '<span style="font-size:24px">[ ' + \
        str(right_h)+' / ' + '24 ]</span>'

    if left_h > 24:
        left_hold.write(
            left_str + alert_str,
            unsafe_allow_html=True)
        uncalculatable = True
    else:
        left_hold.write(
            left_str,
            unsafe_allow_html=True)

    if right_h > 24:
        right_hold.write(
            right_str + alert_str,
            unsafe_allow_html=True)
        uncalculatable = True
    else:
        right_hold.write(
            right_str,
            unsafe_allow_html=True)

    left_slider.write('')
    right_slider.write('')
# -------------------


# -------------------
with st.expander('④ 計測する'):
    calculate_button = st.button('　計測　', disabled=uncalculatable)

    if calculate_button:
        total_date = st.session_state.end_date - st.session_state.st_date
        total_days = total_date.days + 1
        choices_len = len(st.session_state.choices)
        results_len = len(st.session_state.categories)

        results_inds = [0 for i in range(results_len)]
        results_names = [0 for i in range(results_len)]
        for i in range(results_len):
            results_inds[i] = st.session_state.choices.index(
                st.session_state.categories[i])

        results = [0 for i in range(results_len)]
        for i in range(total_days):
            td_i = datetime.timedelta(days=i)
            target_date = st.session_state.st_date + td_i

            if target_date.weekday() >= 5 or jpholiday.is_holiday(target_date):
                time_slider_ind = 1
            else:
                time_slider_ind = 0

            for j in range(results_len):
                results[j] += st.session_state.times[results_inds[j]
                                                     ][time_slider_ind]

        result_top = '■ 計測期間：' + str(total_days) + \
            '日［ ' + str(total_days * 24) + '時間 ］'
        st.write(
            '<span style="font-size:20px">' + result_top + '</span>',
            unsafe_allow_html=True)

        accumulate_h = 0
        for i in range(results_len):
            accumulate_h += results[i]
            result_dh_d = str(results[i] // 24)
            result_dh_h = str(results[i] % 24)
            result_h = str(results[i])
            st.write('■ ' + st.session_state.categories[i] + '：' +
                     result_dh_d + '日 + ' + result_dh_h + '時間［ ' + result_h + '時間 ］')
        if accumulate_h != total_days * 24:
            not_set_h = total_days * 24 - accumulate_h
            result_dh_d = str(not_set_h // 24)
            result_dh_h = str(not_set_h % 24)
            result_h = str(not_set_h)

            st.write('■ ' + reserve_items[0] + '：' +
                     result_dh_d + '日 + ' + result_dh_h + '時間［ ' + result_h + '時間 ］')
# -------------------
