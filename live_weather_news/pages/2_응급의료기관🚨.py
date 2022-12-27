import streamlit as st
import pandas as pd
import requests
import pandas as pd
import bs4
import os

filePath, fileName = os.path.split(__file__)
data_path = os.path.join(filePath,'using_data','구호물자정보.csv')

def emergency_hospital(cd_nm, sgg_nm):

        # 공공데이터 조회
        url = 'http://apis.data.go.kr/B552657/ErmctInfoInqireService/getEmrrmRltmUsefulSckbdInfoInqire'
        params ={'serviceKey' : '3ouN4EKp4qGz+V76EbDHKehnbp5sYL0o19tpl5fAl2Q7s4ZosClGRfc1ENwk+2Px4QUPi4gCuCHGuG3kXFrs9w==', 'STAGE1' : cd_nm, 'STAGE2' : sgg_nm, 'pageNo' : '1', 'numOfRows' : '1000' }

        response = requests.get(url, params=params)
        content = response.text

        ### xml을 DataFrame으로 변환하기 ###
        #bs4 사용하여 item 태그 분리

        xml_obj = bs4.BeautifulSoup(content,'lxml-xml')
        rows = xml_obj.findAll('item')

        # 각 행의 컬럼, 이름, 값을 가지는 리스트 만들기
        row_list = [] # 행값
        name_list = [] # 열이름값
        value_list = [] #데이터값

        # xml 안의 데이터 수집
        for i in range(0, len(rows)):
            columns = rows[i].find_all()
            #첫째 행 데이터 수집
            for j in range(0,len(columns)):
                if i ==0:
                    # 컬럼 이름 값 저장
                    name_list.append(columns[j].name)
                # 컬럼의 각 데이터 값 저장
                value_list.append(columns[j].text)
            # 각 행의 value값 전체 저장
            row_list.append(value_list)
            # 데이터 리스트 값 초기화
            value_list=[]

        # xml값 DataFrame으로 만들기
        emergency_hospital_df = pd.DataFrame(row_list, columns=name_list)

        # 데이터 가공
        emergency_hospital_df = emergency_hospital_df[['hvidate','hvec','hvoc','hvgc','hvamyn','dutyName','dutyTel3']]
        emergency_hospital_df.columns = ['정보 업데이트 일시','응급실 가용현황', '수술실 가용현황', '입원실 가용현황', '구급차 가용여부', '기관명', '연락처']
        return emergency_hospital_df


def main():

    #### page setting
    st.set_page_config(page_title="Home", page_icon="🏠",layout = 'wide')


    ####  title setting
    st.header("🚑응급의료기관 정보 실시간 조회")
    st.write("위치 정보를 선택하여  \n 가까운 응급의료기관과 병실현황을 조회하세요!🙏")

    ####  select box data
    df = pd.read_csv(data_path)
    cd_nm = st.selectbox('시도 선택',list(df['시도명'].unique()))
    sgg_nm = st.selectbox('시군구 선택',list(df[df['시도명'] == cd_nm]['시군구명'].unique()))
    df = df[(df['시도명'] == cd_nm) & (df['시군구명'] == sgg_nm)]



    with st.spinner('정보 조회 중입니다. 잠시 기다려주세요.'):
        try:
            #### emergency hospital data 
            emergency_hospital_df = emergency_hospital(cd_nm, sgg_nm)

            #### make summary info
            emergency_hospital_df['응급실 가용현황'] = emergency_hospital_df['응급실 가용현황'].astype('int')
            sum = 0
            for i in emergency_hospital_df['응급실 가용현황']:
                if i > 0:
                    sum += i

            #### show summary info
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("지역 내 응급의료기관 수", str(len(emergency_hospital_df)) + '개')
            col2.metric('지역 내 응급실 가용병상', '총 ' + str(sum) + '개')
            emergency_hospital_df = emergency_hospital_df.set_index('기관명').drop(columns = '정보 업데이트 일시')
            st.dataframe(data=emergency_hospital_df, use_container_width= True)

        except Exception as E:
            st.write("😓죄송합니다. 해당 지역에 의료시설이 없습니다.")

if __name__ == "__main__":
    main()