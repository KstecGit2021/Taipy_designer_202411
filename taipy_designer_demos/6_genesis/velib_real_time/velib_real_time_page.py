# 이 코드는 파리의 Velib 자전거 공유 시스템의 실시간 데이터를 가져와 처리하고, 이를 시각화하기 위한 대시보드를 생성하는 Taipy 애플리케이션의 백엔드 부분입니다. 주요 기능으로는 데이터 가져오기, 처리, 지리 정보 추가, 히트맵 및 바 그래프 데이터 생성, 전역 통계 계산 등이 있습니다.

# 필요한 라이브러리들을 임포트합니다.
from taipy.designer import Page  # Taipy Designer의 Page 클래스를 임포트합니다.
import pandas as pd  # 데이터 처리를 위한 pandas 라이브러리를 임포트합니다.
import geopandas as gpd  # 지리 데이터 처리를 위한 geopandas 라이브러리를 임포트합니다.
from shapely.geometry import Point  # 지리적 점 데이터를 다루기 위한 Point 클래스를 임포트합니다.
import requests  # HTTP 요청을 보내기 위한 requests 라이브러리를 임포트합니다.
import re  # 정규 표현식을 사용하기 위한 re 라이브러리를 임포트합니다.
import numpy as np  # 수치 연산을 위한 numpy 라이브러리를 임포트합니다.

# Velib 자전거 스테이션의 실시간 상태를 가져오는 함수를 정의합니다.
def fetch_stations_status():
    # API 엔드포인트 URL을 지정합니다.
    url = "https://opendata.paris.fr/api/records/1.0/search/?dataset=velib-disponibilite-en-temps-reel&q=&rows=2000&facet=name&facet=is_installed&facet=is_renting&facet=is_returning"
    # GET 요청을 보냅니다.
    response = requests.get(url)
    # 응답 상태 코드가 200(성공)이면 JSON 데이터를 반환하고, 그렇지 않으면 None을 반환합니다.
    if response.status_code == 200:
        return response.json()
    else:
        return None

# 가져온 스테이션 상태 데이터를 처리하는 함수를 정의합니다.
def process_stations_status(data):
    # JSON 데이터를 pandas DataFrame으로 변환합니다.
    df_rt = pd.json_normalize(data["records"])
    # 열 이름에서 "fields." 접두사를 제거합니다.
    df_rt.rename(columns=lambda x: re.sub("^fields\\.", "", x), inplace=True)
    # 불필요한 열을 제거합니다.
    df_rt.drop(["datasetid", "recordid"], axis=1, inplace=True)
    # 위도와 경도 데이터를 별도의 열로 분리합니다.
    df_rt["lat"] = df_rt["coordonnees_geo"].apply(lambda x: x[0])
    df_rt["lng"] = df_rt["coordonnees_geo"].apply(lambda x: x[1])
    # 'OUI'와 'NON' 값을 1과 0으로 변환합니다.
    df_rt["is_renting"] = df_rt["is_renting"].replace(["OUI", "NON"], [1, 0])
    df_rt["is_installed"] = df_rt["is_installed"].replace(["OUI", "NON"], [1, 0])
    # 처리된 데이터를 CSV 파일로 저장합니다.
    df_rt.to_csv("velib_real_time.csv", index=False)
    # 처리된 DataFrame을 반환합니다.
    return df_rt

# 지리 데이터를 추가하는 함수를 정의합니다.
def augment_with_geodata(df_rt, selected_polygon_geojson=None):
    # DataFrame을 복사합니다.
    dfg = df_rt.copy()
    # 자전거 가용성 비율을 계산합니다.
    dfg["bikes_availability_rate"] = dfg["numbikesavailable"] / dfg["capacity"]
    # 스테이션이 가득 찼는지 여부를 나타내는 열을 추가합니다.
    dfg["station_full"] = (dfg["numbikesavailable"] == dfg["capacity"]).astype(int)
    # 스테이션이 비어있는지 여부를 나타내는 열을 추가합니다.
    dfg["station_empty"] = (dfg["numbikesavailable"] == 0).astype(int)
    # 위도와 경도를 이용해 Point 객체를 생성합니다.
    geometry = [Point(xy) for xy in zip(dfg["lng"], dfg["lat"])]
    # GeoDataFrame을 생성합니다.
    geo_df = gpd.GeoDataFrame(dfg, geometry=geometry)
    
    # 선택된 다각형 지역이 있는 경우, 해당 지역 내의 데이터만 필터링합니다.
    if selected_polygon_geojson is not None:
        if len(selected_polygon_geojson["features"]) > 0:
            selected_gpd = gpd.GeoDataFrame.from_features(selected_polygon_geojson)
            selected_polygon = selected_gpd.iloc[0]["geometry"]
            mask = geo_df.within(selected_polygon)
            filtered_geo_df = geo_df[mask]
            return filtered_geo_df
        else:
            return geo_df
    else:
        return geo_df

# ECharts 바 그래프 데이터를 생성하는 함수를 정의합니다.
def generate_echarts_bar_graph(dfg, dockBar):
    # DataFrame을 복사합니다.
    df = dfg.copy()
    # dockBar 값에 따라 측정 항목과 라벨을 설정합니다.
    if dockBar:
        metric = "numdocksavailable"
        labels = ["Full", "1 도크", "2 도크", "3-5 도크", "6-10 도크", "> 10 도크"]
    else:
        metric = "numbikesavailable"
        labels = ["Empty", "1 자전거", "2 자전거", "3-5 자전거", "6-10 자전거", "> 10 자전거"]

    # 구간을 정의하고 각 스테이션의 상태를 분류합니다.
    bins = [-np.inf, 0, 1, 2, 5, 10, np.inf]
    df["station_status"] = pd.cut(df[metric], bins=bins, labels=labels)

    # 각 카테고리별 스테이션 수를 계산합니다.
    station_counts = df["station_status"].value_counts().reset_index()
    station_counts.columns = ["Station Status", "Count"]

    # 데이터프레임을 딕셔너리 리스트로 변환합니다.
    station_counts_dict = station_counts.to_dict("records")

    # 라벨 순서대로 정렬합니다.
    station_counts_dict = sorted(
        station_counts_dict, key=lambda x: labels.index(x["Station Status"])
    )

    # 그래프 제목을 설정합니다.
    if dockBar:
        title = "스테이션당 이용 가능한 도크"
    else:
        title = "역당 이용 가능한 자전거"

    # ECharts 옵션을 생성합니다.
    echarts_option = {
        "title": {"text": title},
        "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
        "grid": {"left": "3%", "right": "4%", "bottom": "3%", "containLabel": True},
        "xAxis": {"type": "value", "boundaryGap": [0, 0.01]},
        "yAxis": {
            "type": "category",
            "data": [d["Station Status"] for d in station_counts_dict],
        },
        "series": [
            {
                "name": "Number of stations",
                "type": "bar",
                "data": [d["Count"] for d in station_counts_dict],
            }
        ],
    }

    return echarts_option

# 히트맵 데이터를 생성하는 함수를 정의합니다.
def generate_heatmap_data(geo_df, cfg):
    # 히트맵에 필요한 데이터를 추출합니다.
    heatmap_data = geo_df[["lat", "lng", "bikes_availability_rate"]].copy()

    # DataFrame을 딕셔너리 리스트로 변환합니다.
    heatmap_data_list = heatmap_data.to_dict(orient="records")

    # 히트맵 설정을 준비합니다.
    heatmap_config = {"data": heatmap_data_list, "config": cfg}
    return heatmap_config

# 전역 통계를 계산하는 함수를 정의합니다.
def compute_global_stats(dfg):
    return {
        "이용 가능한 자전거 수": "{:,}".format(
            int(dfg["numbikesavailable"].sum())
        ).replace(",", " "),
        "사용 가능한 도크 수": "{:,}".format(
            int(dfg["numdocksavailable"].sum())
        ).replace(",", " "),
        "가용 용량": "{:,}".format(int(dfg["capacity"].sum())).replace(",", " "),
        "전체 스테이션 수": "{:,}".format(
            int(dfg["station_full"].sum())
        ).replace(",", " "),
        "빈 스테이션 수": "{:,}".format(
            int(dfg["station_empty"].sum())
        ).replace(",", " "),
        "대여 스테이션 수": "{:,}".format(
            int(dfg["is_renting"].sum())
        ).replace(",", " "),
        "최대 용량": int(dfg["capacity"].max()),
    }

# 대시보드 매개변수를 설정합니다.
cfg = {
    "opacity": 0.9,
    "radius": 30,
    "disableAutoscale": True,
    "min": 0,
    "max": 1,
    "colorScale": "interpolateRdYlBu",
    "reverseColorScale": False,
}

# 초기 변수들을 설정합니다.
selected_polygon_geojson = None
dockBar = False

# 데이터 흐름을 초기화합니다.
indicator = ["Availability rate"]
selected_indicator = indicator[0]
df_rt = pd.read_csv("velib_real_time.csv")
last_update = df_rt["record_timestamp"][0]
last_update = last_update[:10] + " " + last_update[11:16]
dfg = augment_with_geodata(df_rt, selected_polygon_geojson)
heatmap_json = generate_heatmap_data(dfg, cfg)
echarts_option_json = generate_echarts_bar_graph(dfg, dockBar)
global_stats = compute_global_stats(dfg)

# 상태 변경 시 호출되는 함수를 정의합니다.
def on_change(state, var, val):
    if var == "selected_polygon_geojson":
        selected_polygon_geojson = val
        dfg = augment_with_geodata(state.df_rt, selected_polygon_geojson)
        heatmap_json = generate_heatmap_data(dfg, state.cfg)
        echarts_option_json = generate_echarts_bar_graph(dfg, state.dockBar)
        state.heatmap_json = heatmap_json
        state.echarts_option_json = echarts_option_json
        state.global_stats = compute_global_stats(dfg)

    if var == "cfg":
        cfg = val
        state.heatmap_json = generate_heatmap_data(state.dfg, cfg)

    if var == "dockBar":
        dockBar = val
        state.echarts_option_json = generate_echarts_bar_graph(state.dfg, dockBar)

# xprjson 파일 이름을 정의합니다.
xprjson_file_name = "velib_real_time_page.xprjson"
# Page 인스턴스를 생성합니다.
page = Page(xprjson_file_name)