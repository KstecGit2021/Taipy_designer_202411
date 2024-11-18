# 이 코드는 Iris 데이터셋을 사용하여 머신러닝 모델을 훈련시키고, 데이터를 시각화하며, 사용자 입력을 받아 예측을 수행하는 Taipy 애플리케이션입니다. 주요 기능으로는 데이터 로딩, 전처리, 모델 훈련, 데이터 시각화, 예측 수행 등이 있으며, Taipy GUI를 사용하여 이를 대화형 웹 애플리케이션으로 구현합니다.

# 필요한 라이브러리와 모듈을 임포트합니다.
from taipy.gui import Gui  # Taipy GUI 모듈을 임포트합니다.
from taipy.designer import Page  # Taipy Designer의 Page 클래스를 임포트합니다.
import pandas as pd  # 데이터 처리를 위한 pandas 라이브러리를 임포트합니다.
from sklearn import datasets  # scikit-learn의 데이터셋 모듈을 임포트합니다.
from sklearn.ensemble import RandomForestClassifier  # RandomForest 분류기를 임포트합니다.
import plotly.express as px  # 데이터 시각화를 위한 plotly express를 임포트합니다.

# 예측 결과를 저장할 변수를 초기화합니다.
prediction = '--'

# Iris 데이터셋을 로드하는 함수를 정의합니다.
def load_dataset():
    iris = datasets.load_iris()  # scikit-learn에서 Iris 데이터셋을 로드합니다.
    return iris

# Iris 데이터를 pandas DataFrame으로 변환하는 함수를 정의합니다.
def create_dataframe(iris):
    # Iris 데이터와 특성 이름을 사용하여 DataFrame을 생성합니다.
    df = pd.DataFrame(data=iris.data, columns=iris.feature_names)
    df["target"] = iris.target  # 타겟(품종) 열을 추가합니다.
    # 타겟 값을 이름으로 매핑합니다.
    target_names = {0: "Setosa", 1: "Versicolour", 2: "Virginica"}
    df['target'] = df['target'].map(target_names)
    return df

# RandomForest 분류기를 훈련시키는 함수를 정의합니다.
def train_classifier(iris):
    clf = RandomForestClassifier()  # RandomForest 분류기 객체를 생성합니다.
    clf.fit(iris.data, iris.target)  # 분류기를 Iris 데이터로 훈련시킵니다.
    return clf

# 데이터를 시각화하는 함수를 정의합니다.
def plot_data(df):
    # plotly를 사용하여 산점도를 생성합니다.
    fig = px.scatter(df, x="꽃받침 폭 (cm)", y="꽃받침 길이 (cm)", color="target",
                     size='꽃잎 길이 (cm)', hover_data=['petal width (cm)'])
    return fig

# 입력 데이터를 사용하여 예측을 수행하는 함수를 정의합니다.
def make_prediction(clf, input_data):
    df = pd.DataFrame(input_data, index=[0])  # 입력 데이터를 DataFrame으로 변환합니다.
    prediction = clf.predict(df)  # 분류기를 사용하여 예측을 수행합니다.
    return iris.target_names[prediction][0]  # 예측된 품종 이름을 반환합니다.

# 예측을 위한 샘플 입력 데이터를 정의합니다.
input_data = {"sepal_length": 2.7, "sepal_width": 5.4, "petal_length": 3, "petal_width": 0.5}

# 메인 실행 부분
iris = load_dataset()  # Iris 데이터셋을 로드합니다.
df = create_dataframe(iris)  # DataFrame을 생성합니다.
clf = train_classifier(iris)  # 분류기를 훈련시킵니다.
fig = plot_data(df)  # 데이터를 시각화합니다.

# 상태 변경 시 호출되는 함수를 정의합니다.
def on_change(state, var, val):
    if var == 'input_data':
        state.prediction = make_prediction(clf, val)  # 새로운 입력 데이터로 예측을 수행합니다.

# Taipy Designer Page 인스턴스를 생성합니다.
page = Page("iris_demo_page.xprjson")

# Taipy GUI 인스턴스를 생성하고 설정합니다.
gui = Gui()
gui.add_page("iris", page)  # 'iris' 페이지를 GUI에 추가합니다.
# GUI를 실행합니다. 디자인 모드를 활성화하고, 브라우저는 자동으로 열지 않으며, 재로더를 사용합니다.
gui.run(design=True, run_browser=False, use_reloader=True)