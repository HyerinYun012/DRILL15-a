from math import pi  # 수면 자세의 회전 각도를 라디안으로 계산하기 위해 원주율을 가져온다.

from pico2d import *  # 소년의 이미지·글꼴 로드, 시간·화면 조회, 그리기 기능을 가져온다.

from sdl2 import (SDL_KEYDOWN, SDL_KEYUP, SDLK_LEFT, SDLK_RIGHT,  # 방향키의 누름·뗌 이벤트 상수를 가져오고
                  SDLK_SPACE)  # 공 발사와 수면 해제에 사용할 스페이스 키 상수를 가져온다.
from transitions import Machine  # 소년의 IDLE, SLEEP, RUN 상태 전이를 관리할 상태 머신을 가져온다.

import game_world  # 발사한 공을 게임 월드와 충돌 그룹에 등록하기 위해 가져온다.
from ball import Ball  # 소년이 발사할 공 객체를 생성하기 위해 Ball 클래스를 가져온다.

import game_framework  # 프레임 독립적인 이동과 애니메이션에 경과 시간을 사용하기 위해 가져온다.

# 소년의 달리기 속력을 km/h에서 m/min, m/s, pixel/s 순서로 변환한다.
PIXEL_PER_METER = (10.0 / 0.3)  # 현실의 0.3m가 게임에서 10픽셀이라는 비율을 계산한다.
RUN_SPEED_KMPH = 20.0  # 소년의 달리기 속력을 시속 20km로 지정한다.
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)  # km/h 단위의 속력을 m/min 단위로 변환한다.
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)  # m/min 단위의 속력을 m/s 단위로 변환한다.
RUN_SPEED_PPS = (RUN_SPEED_MPS * PIXEL_PER_METER)  # 현실의 m/s를 게임 좌표의 pixel/s로 변환한다.

# 한 보폭의 길이와 보폭당 이미지 수를 이용해 달리기 애니메이션 속도를 계산한다.
# 속력(m/s)을 보폭(m)으로 나누면 1초 동안 밟는 보폭 수를 얻는다.
# 1초 동안의 보폭 수에 보폭당 프레임 수를 곱하면 초당 애니메이션 프레임 수가 된다.
STRIDE_LENGTH_M = 1.5  # 소년이 달릴 때 한 보폭의 길이를 1.5m로 지정한다.
RUN_FRAMES_PER_STRIDE = 5  # 한 보폭을 표현하는 데 사용할 이미지 프레임 수를 지정한다.
RUN_FRAMES_PER_SECOND = RUN_SPEED_MPS / STRIDE_LENGTH_M * RUN_FRAMES_PER_STRIDE  # 이동 속도와 보폭에 맞는 초당 프레임 수를 계산한다.





class Idle:  # 소년이 서서 기다리는 IDLE 상태의 행동을 정의한다.
    def enter(self, boy):  # 소년이 IDLE 상태에 들어올 때 초기 상태를 설정한다.
        boy.idle_started_at = get_time()  # 잠들기까지의 대기 시간을 재기 위해 진입 시각을 기록한다.
        boy.frame = 0  # 대기 애니메이션을 첫 번째 프레임부터 시작한다.

    def do(self, boy):  # IDLE 상태에서 매 프레임 수행할 행동을 처리한다.
        if get_time() - boy.idle_started_at >= 5.0:  # 아무 동작 없이 5초 이상 지났는지 확인한다.
            boy.fall_asleep()  # 상태 머신의 fall_asleep 전이를 발생시켜 SLEEP으로 이동한다.
        else:  # 아직 5초가 지나지 않았다면
            boy.frame = (boy.frame + 1) % 8  # 0부터 7까지 대기 애니메이션 프레임을 반복한다.

    def draw(self, boy):  # IDLE 상태의 소년 이미지를 현재 방향에 맞게 그린다.
        row = 300 if boy.face_dir == 1 else 200  # 오른쪽은 시트의 300행, 왼쪽은 200행을 선택한다.
        boy.image.clip_draw(boy.frame * 100, row, 100, 100, boy.x, boy.y)  # 현재 프레임 영역을 잘라 소년 위치에 그린다.

    def space(self, boy):  # IDLE 상태에서 스페이스 키 입력을 처리한다.
        boy.fire_ball()  # 소년이 가진 아이템에 맞는 공을 현재 방향으로 발사한다.

    def move(self, boy):  # IDLE 상태에서 방향키 이동 입력을 처리한다.
        boy.start_run()  # 상태 머신의 start_run 전이를 발생시켜 RUN 상태로 이동한다.


class Sleep:  # 소년이 누워 잠든 SLEEP 상태의 행동을 정의한다.
    def enter(self, boy):  # 소년이 SLEEP 상태에 들어올 때 초기 상태를 설정한다.
        boy.frame = 0  # 수면 자세에 사용할 애니메이션 프레임을 첫 장으로 맞춘다.

    def do(self, boy):  # SLEEP 상태에서 매 프레임 수행할 행동을 처리한다.
        pass  # 잠든 동안에는 시간에 따라 바꿀 상태가 없다.

    def draw(self, boy):  # SLEEP 상태의 소년을 방향에 맞춰 눕혀서 그린다.
        angle = pi / 2 if boy.face_dir == 1 else -pi / 2  # 보는 방향에 따라 이미지를 시계 또는 반시계 방향으로 90도 회전한다.
        flip = '' if boy.face_dir == 1 else 'h'  # 왼쪽을 보던 경우에는 이미지의 수평 반전 옵션을 선택한다.
        boy.image.clip_composite_draw(  # 스프라이트 일부에 회전과 반전을 함께 적용해 그린다.
            boy.frame * 100, 300, 100, 100,  # 이미지 시트에서 현재 수면 자세가 들어 있는 100×100 영역을 선택한다.
            angle, flip, boy.x, boy.y - 30, 100, 100  # 회전·반전 후 지면 쪽으로 내린 위치에 100×100 크기로 그린다.
        )  # 수면 상태 이미지의 합성 그리기 호출을 마친다.

    def space(self, boy):  # SLEEP 상태에서 스페이스 키 입력을 처리한다.
        boy.wake_up()  # 상태 머신의 wake_up 전이를 발생시켜 IDLE 상태로 돌아간다.

    def move(self, boy):  # SLEEP 상태에서 방향키 이동 입력을 처리한다.
        boy.start_run()  # 즉시 RUN 상태로 전이해 일어나면서 달리게 한다.


class Run:  # 소년이 좌우로 달리는 RUN 상태의 행동을 정의한다.
    def enter(self, boy):  # 소년이 RUN 상태에 들어올 때 애니메이션을 초기화한다.
        boy.frame = 0  # 달리기 애니메이션을 첫 번째 프레임부터 시작한다.

    def do(self, boy):  # RUN 상태에서 애니메이션과 위치를 한 프레임 갱신한다.
        boy.frame = (boy.frame + RUN_FRAMES_PER_SECOND * game_framework.frame_time) % 8  # 경과 시간만큼 프레임을 진행해 8장 안에서 반복한다.
        boy.x += boy.dir * RUN_SPEED_PPS * game_framework.frame_time  # 방향, 초당 속력, 경과 시간으로 수평 위치를 이동한다.
        boy.x = max(25, min(get_canvas_width() - 25, boy.x))  # 소년 중심이 화면 좌우 경계에서 25픽셀 안쪽에 머물게 한다.

    def draw(self, boy):  # RUN 상태의 소년 이미지를 현재 방향과 프레임에 맞게 그린다.
        row = 100 if boy.face_dir == 1 else 0  # 오른쪽 달리기는 100행, 왼쪽 달리기는 0행을 선택한다.
        # 시간 기반 프레임 값은 실수로 유지하고 실제 이미지를 선택할 때만 정수로 바꾼다.
        boy.image.clip_draw(int(boy.frame) * 100, row, 100, 100, boy.x, boy.y)  # 현재 달리기 프레임을 잘라 소년 위치에 그린다.

    def space(self, boy):  # RUN 상태에서 스페이스 키 입력을 처리한다.
        boy.fire_ball()  # 달리는 중에도 현재 바라보는 방향으로 공을 발사한다.

    def move(self, boy):  # 이미 RUN 상태일 때 추가 방향키 입력을 처리한다.
        pass  # 방향 값은 이벤트 처리에서 직접 갱신되므로 별도 상태 전이가 필요 없다.


class Boy:  # 입력에 따라 상태를 바꾸고 이동하거나 공을 발사하는 플레이어 캐릭터다.
    def __init__(self):  # 소년의 자원, 위치, 입력 상태, 아이템, 상태 머신을 초기화한다.
        self.font = load_font('ENCR10B.TTF', 16)  # 남은 공 개수를 표시할 16포인트 글꼴을 읽는다.
        self.x, self.y = 400, 90  # 소년 중심의 시작 위치를 x=400, y=90으로 정한다.
        self.frame = 0  # 현재 표시할 애니메이션 프레임 번호를 첫 장으로 설정한다.
        self.image = load_image('animation_sheet.png')  # 소년의 모든 상태가 담긴 스프라이트 시트를 읽는다.
        self.idle_started_at = get_time()  # 처음 IDLE 상태가 시작된 시각을 기록한다.
        self.dir = 0  # 현재 수평 이동 방향을 정지 상태인 0으로 설정한다.
        self.face_dir = 1  # 처음 바라보는 방향을 오른쪽을 뜻하는 1로 설정한다.
        self.pressed_keys = set()  # 동시에 눌린 좌우 방향키를 중복 없이 저장할 집합을 만든다.
        self.item = 'Ball'  # 현재 장착 아이템을 작은 공을 뜻하는 Ball로 설정한다.
        self.ball_count = 10  # 소년이 처음 가지고 있는 공의 개수를 10개로 설정한다.

        self.states = {'IDLE': Idle(), 'SLEEP': Sleep(), 'RUN': Run()}  # 상태 이름별 행동 객체를 딕셔너리에 준비한다.

        self.machine = Machine(  # transitions 라이브러리로 소년의 유한 상태 머신을 생성한다.
            model=self,  # 전이 메서드와 현재 state 속성을 이 Boy 객체에 연결한다.
            states=['IDLE', 'SLEEP', 'RUN'],  # 상태 머신이 가질 수 있는 세 상태를 등록한다.
            transitions=[  # 허용할 상태 전이의 트리거, 출발 상태, 도착 상태를 정의한다.
                {'trigger': 'fall_asleep',  # fall_asleep 호출을 수면 전이의 트리거로 지정하고
                 'source': 'IDLE', 'dest': 'SLEEP'},  # IDLE에서 SLEEP으로 이동하도록 연결한다.
                {'trigger': 'wake_up',  # wake_up 호출을 기상 전이의 트리거로 지정하고
                 'source': 'SLEEP', 'dest': 'IDLE'},  # SLEEP에서 IDLE로 이동하도록 연결한다.
                {'trigger': 'start_run',  # start_run 호출을 달리기 전이의 트리거로 지정하고
                 'source': ['IDLE', 'SLEEP'], 'dest': 'RUN'},  # IDLE 또는 SLEEP에서 RUN으로 이동하도록 연결한다.
                {'trigger': 'stop_run',  # stop_run 호출을 달리기 종료 전이의 트리거로 지정하고
                 'source': 'RUN', 'dest': 'IDLE'},  # RUN에서 IDLE로 이동하도록 연결한다.
            ],  # 소년에게 허용되는 상태 전이 목록 정의를 마친다.
            initial='IDLE',  # 상태 머신의 최초 상태를 IDLE로 지정한다.
            auto_transitions=False,  # 라이브러리가 to_STATE 형태의 자동 전이 메서드를 만들지 않게 한다.
        )  # 소년 상태 머신 생성을 마친다.

    def on_enter_IDLE(self):  # 상태 머신이 IDLE에 진입한 직후 자동으로 호출한다.
        self.states['IDLE'].enter(self)  # IDLE 행동 객체가 진입 시각과 애니메이션을 초기화하게 한다.

    def on_enter_SLEEP(self):  # 상태 머신이 SLEEP에 진입한 직후 자동으로 호출한다.
        self.states['SLEEP'].enter(self)  # SLEEP 행동 객체가 수면 애니메이션을 초기화하게 한다.

    def on_enter_RUN(self):  # 상태 머신이 RUN에 진입한 직후 자동으로 호출한다.
        self.states['RUN'].enter(self)  # RUN 행동 객체가 달리기 애니메이션을 초기화하게 한다.

    def fire_ball(self):  # 현재 아이템과 바라보는 방향에 맞는 공을 하나 발사한다.
        if self.item is None or self.ball_count <= 0:  # 장착 아이템이 없거나 남은 공이 없는지 확인한다.
            return  # 발사할 수 없는 상태이면 아무 객체도 만들지 않고 끝낸다.
        self.ball_count -= 1  # 발사에 사용한 공 한 개를 소지 개수에서 차감한다.
        ball = Ball(self.x + self.face_dir * 40, self.y + 60, self.face_dir,  # 소년의 앞쪽과 위쪽에서 현재 방향으로 날아갈 공을 만들고
                    1 if self.item == 'Ball' else 2)  # Ball 아이템이면 작은 공, 그 외에는 큰 공 종류를 선택한다.
        game_world.add_oject(ball)  # 새 공을 기본 깊이의 게임 월드에 등록한다.
        game_world.add_collision_pairs("grass:ball", None, ball)  # 새 공을 잔디 충돌 그룹의 b측에 등록한다.
        game_world.add_collision_pairs("boy:ball", None, ball)  # 새 공을 소년 충돌 그룹의 b측에도 등록한다.

    def pause(self):  # 플레이 모드가 일시 정지될 때 소년의 입력과 이동을 정리한다.
        self.pressed_keys.clear()  # 현재 눌린 것으로 기록된 모든 방향키를 제거한다.
        if self.state == 'RUN':  # 일시 정지 직전에 소년이 달리는 상태였는지 확인한다.
            self.dir = 0  # 수평 이동 방향을 0으로 바꿔 이동을 멈춘다.
            self.stop_run()  # 상태 머신을 RUN에서 IDLE로 전이시킨다.

    def handle_event(self, event):  # 키보드 이벤트를 현재 상태와 눌린 키 조합에 맞게 처리한다.
        if event.type == SDL_KEYDOWN and event.key == SDLK_SPACE:  # 스페이스 키를 새로 눌렀는지 확인한다.
            self.states[self.state].space(self)  # 현재 상태 객체의 스페이스 키 행동을 실행한다.
            return  # 같은 이벤트를 방향키 처리에 다시 사용하지 않고 끝낸다.

        if (event.type not in (SDL_KEYDOWN, SDL_KEYUP) or  # 키를 누르거나 떼는 종류의 이벤트가 아니거나
                event.key not in (SDLK_LEFT, SDLK_RIGHT)):  # 해당 키가 좌우 방향키가 아닌 경우인지 확인한다.
            return  # 이동과 관계없는 이벤트이므로 더 처리하지 않는다.

        if event.type == SDL_KEYDOWN:  # 좌우 방향키를 누른 이벤트인지 확인한다.
            self.pressed_keys.add(event.key)  # 누른 키를 현재 입력 집합에 추가한다.
        else:  # 좌우 방향키를 뗀 이벤트라면
            self.pressed_keys.discard(event.key)  # 해당 키가 없어도 오류 없이 입력 집합에서 제거한다.

        direction = (int(SDLK_RIGHT in self.pressed_keys) -  # 오른쪽 키가 눌렸으면 1, 아니면 0을 만들고
                     int(SDLK_LEFT in self.pressed_keys))  # 왼쪽 키의 1 또는 0을 빼서 -1, 0, 1 방향을 계산한다.

        if direction != 0:  # 두 방향키의 조합 결과 실제 이동 방향이 있는지 확인한다.
            self.dir = direction  # 이번 프레임부터 사용할 수평 이동 방향을 저장한다.
            self.face_dir = direction  # 마지막 이동 방향을 소년이 바라볼 방향으로도 저장한다.
            self.states[self.state].move(self)  # 현재 상태 객체가 이동 입력에 맞는 상태 전이를 처리하게 한다.
        elif self.state == 'RUN':  # 이동 방향이 없어졌는데 현재 상태가 RUN인지 확인한다.
            self.dir = 0  # 수평 방향을 정지 값인 0으로 설정한다.
            self.stop_run()  # 상태 머신을 RUN에서 IDLE로 전이시킨다.

    def update(self):  # 현재 상태에서 소년의 한 프레임 행동을 갱신한다.
        self.states[self.state].do(self)  # 상태 이름에 해당하는 행동 객체의 do 함수를 호출한다.

    def draw(self):  # 소년, 남은 공 개수, 충돌 영역을 화면에 그린다.
        self.states[self.state].draw(self)  # 현재 상태에 맞는 자세와 애니메이션으로 소년을 그린다.
        self.font.draw(self.x - 10, self.y + 50, f'{self.ball_count:02d}', (255, 255, 0))  # 머리 위에 공 개수를 두 자리 노란색 글자로 표시한다.
        draw_rectangle(*self.get_bb())  # 디버깅을 위해 소년의 충돌 사각형을 그린다.

    # 소년의 중심 위치를 기준으로 축 정렬 바운딩 박스를 계산한다.
    def get_bb(self):  # 소년의 충돌 영역을 왼쪽, 아래, 오른쪽, 위 순서로 반환한다.
        return self.x - 20, self.y - 50, self.x + 20, self.y + 50  # 너비 40, 높이 100인 충돌 사각형을 만든다.

    def handle_collision(self, group, other):  # 충돌 그룹에 따라 소년의 반응을 처리한다.
        if group == "boy:ball":  # 소년과 공 사이의 충돌인지 확인한다.
            self.ball_count += 1  # 닿은 공을 획득한 것으로 처리해 소지 개수를 하나 늘린다.
            # game_world.remove_object(other)  # 공 제거는 Ball.handle_collision에서 수행하도록 맡겨 둔다.
        if group == "boy:zombies":
            game_world.remove_object(self)
