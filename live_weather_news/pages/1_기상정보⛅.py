import streamlit as st
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
import requests
import json


filePath, fileName = os.path.split(__file__)
data_path = os.path.join(filePath,'using_data','korea_weatherlocation_xy.csv')

# 

# 6시쯤 API 호출 안됨
def weatherData():
    # 시간 설정
    base_datebf30 = datetime.now() + timedelta(hours = 9)  - timedelta(minutes = 30)
    
    base_date = base_datebf30.strftime('%Y%m%d')
    if int(base_datebf30.strftime('%d')) > 30:
        base_time = base_datebf30.strftime('%H00')
    else :
        base_time = base_datebf30.strftime('%H30')

    # api 호출준비(지역별 대기값)
    korea_xy_df = pd.read_csv(data_path)

    # 지역 선택
    cd_nm_list = list(korea_xy_df['1단계'].unique())
    cd_nm = st.selectbox('시도 선택',cd_nm_list)

    sgg_nm_list = list(korea_xy_df[korea_xy_df['1단계'] == cd_nm]['2단계'].unique())
    sgg_nm = st.selectbox('시군구 선택',sgg_nm_list)

    # 격자 X, 격자 Y값 찾기
    korea_xy_df = korea_xy_df[(korea_xy_df['1단계'] == cd_nm) & (korea_xy_df['2단계'] == sgg_nm)]
    nx = korea_xy_df.iloc[0,2]
    ny = korea_xy_df.iloc[0,3]

    # api 호출
    url = 'http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtFcst'
    params ={'serviceKey' : 'I3k49MWVfMM1ikcVAQtW+aBQeMCQuFa3+ZqXWrCmB1NqsdllN466vryE/9Nt1OhZ3nx46rQ6oaw0nGhO/FJULg==',
            'pageNo' : '1', 'numOfRows' : '1000', 'dataType' : 'JSON', 'base_date' : base_date, 'base_time' : base_time, 'nx' : nx, 'ny' : ny }

    # json csv 변환
    response = requests.get(url, params=params)
    contents = response.content
    json_ob = json.loads(contents)
    body = json_ob['response']['body']['items']['item']
    body = pd.json_normalize(body)

    # 데이터 나누기
    temperature = body[body['category'] == 'T1H'].reset_index(drop = True)
    raining = body[body['category'] == 'RN1'].reset_index(drop = True)
    sky = body[body['category'] == 'SKY'].reset_index(drop = True)
    shape_rn = body[body['category'] == 'PTY'].reset_index(drop = True)
    humidity = body[body['category'] == 'REH'].reset_index(drop = True)
    thunder = body[body['category'] == 'LGT'].reset_index(drop = True)
    windspeed = body[body['category'] == 'WSD'].reset_index(drop = True)

    return cd_nm, sgg_nm, temperature, raining, sky, shape_rn, humidity, thunder, windspeed




def main():

    st.set_page_config(page_title="Home", page_icon="🏠",layout = 'wide')

    st.write(
            """
            <style>
            [data-testid="stMetricDelta"] svg {
                display: none;
            }
            </style>
            """,
            unsafe_allow_html=True,)
                
                
    st.header("☂️실시간 초단기 기상정보")
    st.write("위치 정보 선택 후, 이후 6시간의 기상정보를 받아보세요🙏")

    cd_nm, sgg_nm, temperature, raining, sky, shape_rn, humidity, thunder, windspeed = weatherData()

    col1, col2, col3, col4, col5, col6 = st.columns(6)
    for idx in temperature.index:
        time = str(raining.loc[idx,'fcstTime'])[0:2] + "시"
        temperature_data = str(temperature.loc[idx,'fcstValue'])
        raining_data = str(raining.loc[idx,'fcstValue'])
        sky_data = str(sky.loc[idx,'fcstValue'])
        if sky_data == "1":
            sky_data = "☀️맑음"
        elif sky_data == "3":
            sky_data = "⛅구름많음"
        elif sky_data == "4":
            sky_data = "☁️흐림"
            
        shape_raining = str(shape_rn.loc[idx,'fcstValue'])
        if shape_raining == "0":
            shape_raining = " "
        elif shape_raining == "1":
            shape_raining = "비🌧️"
        elif shape_raining == "2":
            shape_raining = "비/눈🌨️"
        elif shape_raining == "3":
            shape_raining = "눈🌨️"
        elif shape_raining == "5":
            shape_raining = "빗방울🌧️"
        elif shape_raining == "6":
            shape_raining = "빗방울눈날림🌧️"
        elif shape_raining == "7":
            shape_raining = "눈날림🌨️"
            
        humidity_data = str(humidity.loc[idx,'fcstValue'])
        thunder_data = str(thunder.loc[idx,'fcstValue'])
        windspeed_data = str(windspeed.loc[idx,'fcstValue'])
        
        
        with col1:
            if idx % 6 == 0:
                st.markdown(f"#### {time}")
                st.metric(sky_data, value = temperature_data + "℃", delta = "풍속 : " + windspeed_data + "m/s")
                st.metric("💧습도 : " + humidity_data + "%", value= raining_data, delta= shape_raining)
                if thunder_data != "0":
                    st.write("⚡낙뢰 " + thunder_data + "kA")

        with col2:
            if idx % 6 == 1:

                st.markdown(f"#### {time}")
                st.metric(sky_data, value = temperature_data + "℃", delta = "풍속 : " + windspeed_data + "m/s")
                st.metric("💧습도 : " + humidity_data + "%", value= raining_data, delta= shape_raining)
                if thunder_data != "0":
                    st.write("⚡낙뢰 " + thunder_data + "kA")

        with col3:
            if idx % 6 == 2:
                st.markdown(f"#### {time}")
                st.metric(sky_data, value = temperature_data + "℃", delta = "풍속 : " + windspeed_data + "m/s")
                st.metric("💧습도 : " + humidity_data + "%", value= raining_data, delta= shape_raining)
                if thunder_data != "0":
                    st.write("⚡낙뢰 " + thunder_data + "kA")

        
        with col4:
            if idx % 6 == 3:
                st.markdown(f"#### {time}")
                st.metric(sky_data, value = temperature_data + "℃", delta = "풍속 : " + windspeed_data + "m/s")
                st.metric("💧습도 : " + humidity_data + "%", value= raining_data, delta= shape_raining)
                if thunder_data != "0":
                    st.write("⚡낙뢰 " + thunder_data + "kA")
                    
        with col5:
            if idx % 6 == 4:
                st.markdown(f"#### {time}")
                st.metric(sky_data, value = temperature_data + "℃", delta = "풍속 : " + windspeed_data + "m/s")
                st.metric("💧습도 : " + humidity_data + "%", value= raining_data, delta= shape_raining)
                if thunder_data != "0":
                    st.write("⚡낙뢰 " + thunder_data + "kA")
                    
        with col6:
            if idx % 6 == 5:
                st.markdown(f"#### {time}")
                st.metric(sky_data, value = temperature_data + "℃", delta = "풍속 : " + windspeed_data + "m/s")
                st.metric("💧습도 : " + humidity_data + "%", value= raining_data, delta= shape_raining)
                if thunder_data != "0":
                    st.write("⚡낙뢰 " + thunder_data + "kA")
                
                
    st.write(cd_nm + " " + sgg_nm + "의 초단기 기상정보입니다. 해당 페이지는 기상청 데이터를 사용합니다😊")

if __name__ == "__main__":
    main()