from taipy.gui import Gui  # Taipy의 GUI 관련 클래스인 Gui를 임포트
from eco2mix_plotly_page import page  # eco2mix_plotly_page에서 정의된 페이지를 임포트

# Gui 인스턴스를 생성
gui = Gui()

# "eco2mix"라는 이름으로 페이지를 추가 (위에서 임포트한 page 객체를 사용)
gui.add_page("eco2mix", page)

# GUI를 실행. 
# - design=True: GUI가 디자인 모드로 실행됨 (페이지를 디자인할 수 있는 상태)
# - run_browser=True: GUI를 브라우저에서 실행하도록 설정
# - use_reloader=False: 코드 변경 시 자동으로 다시 로드되지 않도록 설정 (디버깅 시 유용)
gui.run(design=True, run_browser=True, use_reloader=False)
