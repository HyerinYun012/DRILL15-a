import time  # 프레임 간 경과 시간을 측정할 표준 시간 모듈을 가져온다.
running = False  # 전체 게임 루프가 계속 실행될지를 나타내는 플래그다.
stack = []  # 현재 실행 중인 모드들을 스택 구조로 관리한다.


def change_mode(mode):  # 현재 모드를 종료하고 전달받은 모드로 완전히 교체한다.
    if stack:  # 종료할 기존 모드가 스택에 있는지 확인한다.
        stack.pop().finish()  # 기존 최상위 모드를 꺼내고 종료 처리를 호출한다.
    stack.append(mode)  # 새 모드를 스택의 최상위에 추가한다.
    mode.init()  # 새 모드가 사용할 객체와 상태를 초기화한다.


def push_mode(mode):  # 현재 모드를 보존한 채 새 모드를 그 위에 쌓는다.
    if stack:  # 일시 정지할 현재 모드가 있는지 확인한다.
        stack[-1].pause()  # 현재 최상위 모드를 스택에 둔 채 일시 정지시킨다.
    stack.append(mode)  # 새 모드를 스택의 최상위에 추가한다.
    mode.init()  # 새 모드의 초기화 함수를 호출한다.


def pop_mode():  # 현재 모드를 제거하고 바로 아래 모드로 돌아간다.
    if stack:  # 제거할 현재 모드가 있는지 확인한다.
        stack.pop().finish()  # 최상위 모드를 꺼내면서 종료 처리를 수행한다.
    if stack:  # 이전 모드가 스택에 남아 있는지 다시 확인한다.
        stack[-1].resume()  # 아래에 있던 모드의 실행을 재개한다.
    else:  # 되돌아갈 모드가 하나도 없다면
        quit()  # 전체 게임 루프가 끝나도록 종료 플래그를 설정한다.


def quit():  # 다음 반복 전에 전체 게임 루프를 종료하도록 요청한다.
    global running  # 모듈 전역의 실행 플래그를 수정하겠다고 선언한다.
    running = False  # 반복 조건을 거짓으로 만들어 게임 루프를 끝낸다.


frame_time = 0.0  # 직전 한 프레임을 처리하는 데 걸린 시간을 초 단위로 저장한다.

def run(start_mode):  # 시작 모드를 받아 메인 게임 루프를 실행한다.
    global running, stack  # 전역 실행 플래그와 모드 스택을 새 실행에 맞게 변경한다.
    running = True  # 게임 루프가 실행되도록 반복 플래그를 켠다.
    stack = [start_mode]  # 전달받은 시작 모드 하나로 모드 스택을 구성한다.
    try:  # 실행 중 오류가 나도 마지막 정리 과정은 수행되도록 보호 구문을 시작한다.
        start_mode.init()  # 게임 루프 진입 전에 시작 모드의 객체들을 초기화한다.
        global frame_time  # 객체들이 읽을 전역 프레임 시간을 수정하겠다고 선언한다.
        frame_time = 0.0  # 첫 프레임 전에는 경과 시간이 없으므로 0으로 초기화한다.
        current_time = time.time()  # 프레임 시간 계산의 기준이 될 현재 시각을 기록한다.
        while running:  # 종료 요청이 들어오기 전까지 매 프레임을 반복한다.
            stack[-1].handle_events()  # 현재 모드가 키보드와 창 이벤트를 처리하게 한다.
            stack[-1].update()  # 현재 모드 안의 게임 객체 상태를 갱신한다.
            stack[-1].render()  # 갱신된 현재 모드를 화면에 그린다.
            frame_time = time.time() - current_time  # 이번 프레임에 실제로 걸린 시간을 계산한다.
            frame_rate = 1.0 / frame_time  # 초당 프레임 수를 계산해 지역 변수에 저장한다.
            current_time += frame_time  # 다음 프레임 측정을 위해 기준 시각을 현재 시각으로 옮긴다.

    finally:  # 정상 종료와 예외 발생 여부에 관계없이 정리 코드를 실행한다.
        while stack:  # 아직 스택에 남아 있는 모든 모드를 하나씩 처리한다.
            stack.pop().finish()  # 각 모드를 꺼내며 모드별 종료 처리를 호출한다.
        running = False  # 정리가 끝난 뒤 실행 상태를 확실하게 종료로 맞춘다.
