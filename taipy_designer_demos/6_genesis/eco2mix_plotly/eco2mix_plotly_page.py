from taipy.designer import Page  # Taipy 디자이너에서 Page 클래스를 임포트 (인터페이스 관련)
import pandas as pd  # 데이터 처리용 pandas 라이브러리 임포트
import requests  # HTTP 요청을 위한 requests 라이브러리 임포트
import plotly.graph_objects as go  # Plotly에서 그래프 객체를 사용하기 위한 임포트
import plotly.express as px  # Plotly Express를 통한 간단한 그래프 작성 임포트
import re  # 정규 표현식을 위한 re 라이브러리 임포트
from datetime import datetime, timedelta  # 날짜 및 시간 계산을 위한 datetime 모듈 임포트

# 변수 선언
today = datetime.now()  # 현재 날짜를 가져옴
yesterday = today - timedelta(days=60)  # 60일 전 날짜 계산
date = yesterday.strftime("%Y-%m-%d")  # 날짜를 "YYYY-MM-DD" 형식으로 포맷
bSampling = True  # 샘플링 여부를 True로 설정
table = [["Date", date], ["Sampling", bSampling]]  # 날짜와 샘플링 여부를 담은 리스트 생성

# 데이터 쿼리 URL 생성 함수
def create_query_url(date):  
    date_url = date.replace("-", "%2F")  # 날짜 포맷을 URL 인코딩 형식으로 변환
    return f"https://odre.opendatasoft.com/api/records/1.0/search/?dataset=eco2mix-national-tr&q=&rows=96&sort=-date_heure&facet=nature&facet=date_heure&refine.date_heure={date_url}"  
    # 오픈 데이터를 조회하는 API URL 생성

# REST API를 통한 데이터 호출 함수
def fetch_data(url):
    response = requests.get(url, headers={"Content-Type": "application/json"})  # URL로 GET 요청을 보내서 응답을 받음
    if response.status_code == 200:  # 응답 코드가 200일 때 성공적으로 데이터를 받은 경우
        return response.json()["records"]  # JSON 응답에서 'records' 항목만 반환
    else:
        return []  # 실패 시 빈 리스트 반환

# 데이터 처리 함수
def process_data(records):
    df = pd.json_normalize(records).dropna().reset_index(drop=True)  # JSON 데이터를 pandas DataFrame으로 변환 후 결측값 제거
    df.rename(columns=lambda x: re.sub("^fields\.", "", x), inplace=True)  # 컬럼명에서 'fields.' 접두사 제거
    df["date_heure"] = pd.to_datetime(df["date_heure"])  # 'date_heure' 컬럼을 datetime 형식으로 변환
    df.set_index("date_heure", inplace=True)  # 'date_heure'를 인덱스로 설정
    # 컬럼명 변경 (프랑스어 -> 한국어)
    column_mapping = {  
        "nucleaire": "원자력",  
        "hydraulique": "수력",  
        "eolien": "풍력",  
        "gaz": "가스",  
        "bioenergies": "바이오에너지",  
        "solaire": "태양열",  
        "fioul": "연료유",  
    } 
    df.rename(columns=column_mapping, inplace=True)  # 컬럼명을 영어로 변경
    return df[["원자력", "수력", "풍력", "가스", "바이오에너지", "태양열", "연료유"]]  # 필요한 컬럼만 반환

# 에너지 합계 계산 함수
def calculate_energy(df):
    dff = df.resample("H").mean()  # 시간 단위로 데이터를 리샘플링 (시간당 평균값 계산)
    return dff.sum()  # 각 컬럼별 합계를 계산하여 반환

# 데이터 시각화 함수 (선 그래프 또는 막대 그래프)
def plot_data(df, date, bSampling):
    if not bSampling:  # 샘플링이 False일 경우 선 그래프
        fig = go.Figure()  # 그래프 객체 생성
        for col in df.columns:  # 각 에너지 생산원에 대해 그래프 추가
            fig.add_trace(
                go.Scatter(  # 선 그래프 추가
                    x=df.index,  # x축: 날짜
                    y=df[col],  # y축: 에너지 값
                    hoverinfo="x+y",  # 마우스 오버 시 x와 y 값 표시
                    mode="lines",  # 선 그래프
                    line=dict(width=0.5),  # 선 두께 설정
                    name=col,  # 각 컬럼명으로 그래프에 레이블 추가
                    stackgroup="one",  # 여러 시리즈를 스택으로 그룹화
                )
            )
        layout = dict(
            showlegend=True,  # 범례 표시
            xaxis_type="date",  # x축: 날짜 타입
            yaxis=dict(type="linear", range=[0, 90000], ticksuffix=" MW"),  # y축: 에너지(단위 MW)
            xaxis_title="Time",  # x축 제목
            yaxis_title="전력 [MW]",  # y축 제목
            title=f"{date}의 일일 전력량",  # 그래프 제목
        )
        fig.update_layout(layout)  # 레이아웃 업데이트
    else:  # 샘플링이 True일 경우 막대 그래프
        dff = df.resample("H").mean()  # 시간 단위로 리샘플링
        fig = px.bar(dff, barmode="stack")  # Plotly Express를 사용하여 스택된 막대 그래프 생성
        layout = dict(
            showlegend=True,  # 범례 표시
            xaxis_type="date",  # x축: 날짜 타입
            yaxis=dict(type="linear", range=[0, 90000], ticksuffix=" MW"),  # y축: 에너지(단위 MW)
            xaxis_title="Time",  # x축 제목
            yaxis_title="전력 [MW]",  # y축 제목
            title=f"{date}의 일일 전력량",  # 그래프 제목
        )
        fig.update_layout(layout)  # 레이아웃 업데이트
    return fig  # 생성된 그래프 반환

# 에너지 총합에 대한 파이 차트 시각화 함수
def plot_pie(total_energy_GWh):
    labels_with_units = [f"{label} (GWh)" for label in total_energy_GWh.index]  # 에너지 원별 GWh 단위 추가
    fig = go.Figure(
        data=[
            go.Pie(labels=labels_with_units, values=total_energy_GWh.values, hole=0.3)  # 파이 차트 생성 (원형 그래프)
        ]
    )
    fig.update_layout(title_text="부문별 총 에너지 생산량")  # 그래프 제목 설정
    return fig  # 생성된 파이 차트 반환

# 메인 실행 함수
def main_exec(date, bSampling):
    query_url = create_query_url(date)  # 쿼리 URL 생성
    records = fetch_data(query_url)  # 데이터 가져오기
    df = process_data(records)  # 데이터 처리
    energy_sum = calculate_energy(df)  # 에너지 합계 계산
    fig_data = plot_data(df, date, bSampling)  # 선/막대 그래프 생성
    fig_pie = plot_pie(energy_sum / 1000)  # 파이 차트 생성 (단위를 GWh로 변환)
    return df, fig_data, fig_pie  # DataFrame과 그래프 두 개 반환

# 데이터 및 그래프 업데이트 함수
def update_exec(df, date, bSampling):
    energy_sum = calculate_energy(df)  # 에너지 합계 계산
    fig_data = plot_data(df, date, bSampling)  # 선/막대 그래프 생성
    fig_pie = plot_pie(energy_sum / 1000)  # 파이 차트 생성 (단위를 GWh로 변환)
    return fig_data, fig_pie  # 그래프 두 개 반환

df, fig_data, fig_pie = main_exec(date, bSampling)  # 메인 실행 함수 호출

# 변수 변경 시 처리할 함수
def on_change(state, var, val):
    if var == "date":  # 날짜가 변경되었을 때
        df, state.fig_data, state.fig_pie = main_exec(val, state.bSampling)  # 날짜에 맞는 데이터 및 그래프 갱신
    elif var == "bSampling":  # 샘플링 방식이 변경되었을 때
        state.fig_data, state.fig_pie = update_exec(state.df, state.date, val)  # 샘플링 방식에 맞게 그래프 갱신

# xprjson 파일 이름 정의 (Taipy 페이지를 위한 파일)
xprjson_file_name = "eco2mix_plotly_page.xprjson"

# 페이지 인스턴스 생성 (Taipy Designer 페이지)
page = Page(xprjson_file_name)  # 지정한 xprjson 파일을 사용하여 페이지 생성
