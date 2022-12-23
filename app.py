import numpy as np
import requests
import pprint
import json
import pandas as pd
import datetime
from datetime import datetime, timedelta
import datetime
import streamlit as st
import folium
from folium.plugins import MarkerCluster
from folium.plugins import MiniMap
from streamlit_folium import st_folium


 
def special_report_map(all_data,data,special_report):
    m = folium.Map(
        location=[all_data['LAT,'].mean(), all_data['LON,'].mean()],
        zoom_start= 7, width = '70%', height = '50%'
        )
    
    text = str(special_report['제목']).split('/')
    coords = data[['LAT,', 'LON,', 'WRN_KO,', 'STN_KO,']]
    for idx in coords.index:
        result = ''.join(text[idx].split(' ')[1:3])
        folium.Marker([coords.loc[idx, 'LAT,'], coords.loc[idx, 'LON,']], icon = folium.Icon(color="green"), tooltip = coords.loc[idx,'WRN_KO,'] + '<br>[특보] :' + str(result)  ).add_to(m)
    return m

# 기상 특보 데이터
def special_report_df():
    url = 'http://apis.data.go.kr/1360000/WthrWrnInfoService/getWthrWrnList'
    params ={'serviceKey' : 'I3k49MWVfMM1ikcVAQtW+aBQeMCQuFa3+ZqXWrCmB1NqsdllN466vryE/9Nt1OhZ3nx46rQ6oaw0nGhO/FJULg==', 'pageNo' : '1', 'numOfRows' : '10', 'dataType' : 'JSON'}

    response = requests.get(url, params=params)
    contents = response.text
    json_ob = json.loads(contents)
    body = json_ob['response']['body']['items']['item']
    body = pd.json_normalize(body)
    return body

def main():
    
    # 홈페이지 상단 
    st.set_page_config(page_title="Home", page_icon="🏠",layout = 'wide')


    st.title('기상 특보 발령사항')
    st.header('최근 7일 이내의 전국 특보현황🌍')
    
    try :
        # 데이터 프레임 형식으로 추출
        special_report = special_report_df()
        
        # 지점코드와 지역명을 merge
        local_code = pd.read_excel('C://Users//user//Documents//python-streamlit//data//지역코드.xlsx')
        local_code = local_code.drop([0],axis = 0)
        for i in local_code.index:
            local_code.loc[i,'#STN_ID,']=local_code.loc[i,'#STN_ID,'][:-1]
            local_code.loc[i,'STN_KO,']=local_code.loc[i,'STN_KO,'][:-1]
        local_code.rename(columns={'#STN_ID,':'stnId','STN_KO,':'지역명'},inplace=True)
        special_report = pd.merge(special_report,local_code)
        special_report=special_report[['stnId', '지역명','title', 'tmFc', 'tmSeq']]
        special_report['발표시각'] = np.NaN
    
        # 날짜 분리
        for i in special_report.index:
            year = special_report['tmFc'][i].astype('str')[:4] + '년'
            month = special_report['tmFc'][i].astype('str')[4:6] + '월'
            day = special_report['tmFc'][i].astype('str')[6:8] + '일'
            hour = special_report['tmFc'][i].astype('str')[8:10] + '시'
            minute = special_report['tmFc'][i].astype('str')[10:12] + '분'
            special_report['발표시각'][i] = year+month+day+' '+hour +minute

        # 컬럼 rename
        special_report.rename(columns={'tmSeq': '발표번호'},inplace=True)
        special_report.rename(columns={'title': '제목'},inplace=True)
        special_report.rename(columns={'stnId': '지점코드'},inplace=True)
        special_report.drop(labels='tmFc',axis = 1,inplace=True)

        st.write(special_report)
    except:
        st.subheader("🌞기상특보가 없습니다. 화창한 날씨로 예상됩니다.🌞")
        pass

    # 특보 지도 띄우기
    try :
        special_local_code = pd.read_excel('C://Users//user//Documents//python-streamlit//data//특보구역코드.xlsx')

        for i in local_code.index:
            special_local_code.loc[i,'LAT,']=special_local_code.loc[i,'LAT,'][:-1]
            special_local_code.loc[i,'LON,']=special_local_code.loc[i,'LON,'][:-1]
            special_local_code.loc[i,'#STN_ID,'] = special_local_code.loc[i,'#STN_ID,'][:-1]
            special_local_code.loc[i,'WRN_KO,'] = special_local_code.loc[i,'WRN_KO,'][:-1]
            special_local_code.loc[i,'STN_KO,'] = special_local_code.loc[i,'STN_KO,'][:-1]
        special_local_code = special_local_code.drop([0],axis = 0)
        special_local_code['LAT,'] = special_local_code['LAT,'].astype('float')
        special_local_code['LON,'] = special_local_code['LON,'].astype('float')


        special_local_code = special_local_code[['LAT,', 'LON,', 'WRN_KO,', 'STN_KO,','#STN_ID,']]
        special_local_code.rename(columns={'#STN_ID,' : '지점코드'},inplace=True)
        map_lat_lod = pd.merge(special_report,special_local_code)
        map = special_report_map(special_local_code,map_lat_lod,special_report)
        st_folium(map)
        
    except:
        st.write('지도오류')


if __name__ == "__main__" :
    main()