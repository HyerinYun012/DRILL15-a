import random  # 좀비의 시작 위치와 이동 방향을 무작위로 정하기 위해 가져온다.

from pico2d import load_image, draw_rectangle, clamp  # 이미지 로드, 충돌 영역 표시, 범위 제한 함수를 가져온다.

import game_framework  # 프레임 사이의 경과 시간을 사용하기 위한 모듈을 가져온다.
import game_world  # 좀비를 게임 월드와 연동할 때 사용할 모듈을 가져온다.

# 좀비의 실제 속력 단위를 km/h에서 게임상의 픽셀/초로 순서대로 변환한다.
PIXEL_PER_METER = (10.0 / 0.3)  # 현실의 0.3m가 게임에서 10픽셀이라는 비율을 계산한다.
RUN_SPEED_KMPH = 10.0  # 좀비의 달리기 속력을 시속 10km로 정한다.
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)  # km/h를 m/min 단위로 변환한다.
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)  # m/min을 m/s 단위로 변환한다.
RUN_SPEED_PPS = (RUN_SPEED_MPS * PIXEL_PER_METER)  # m/s를 게임 좌표계의 pixel/s로 변환한다.

# 좀비의 걷기 동작 한 번은 0.5초 동안 10개의 이미지 프레임으로 재생된다.
TIME_PER_ACTION = 0.5  # 걷기 동작 한 주기를 완료하는 데 걸리는 시간을 지정한다.
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION  # 1초 동안 반복할 동작 주기 수를 계산한다.
FRAMES_PER_ACTION = 10  # 걷기 동작 한 주기에 포함된 이미지 수를 지정한다.

MIN_X, MAX_X = 800, 1600  # 좀비가 왕복할 수 있는 최소·최대 x좌표를 지정한다.

num =0

class Zombie:  # 일정 구간을 좌우로 왕복하며 걷는 좀비를 나타낸다.
    images = None  # 모든 좀비가 함께 사용할 애니메이션 이미지 묶음을 저장한다.

    def load_images(self):  # 걷기 애니메이션 이미지를 최초 한 번만 읽는다.
        if Zombie.images is None:  # 클래스 이미지 캐시가 아직 초기화되지 않았는지 확인한다.
            Zombie.images = {  # 동작 이름별 이미지 목록을 담을 딕셔너리를 생성한다.
                'Walk': [load_image(f'./zombie/Walk ({i}).png') for i in range(1, 11)]  # Walk 1부터 10까지 읽는다.
            }  # 완성한 걷기 이미지 목록 딕셔너리를 클래스 변수에 저장한다.

    def __init__(self):  # 좀비의 이미지, 위치, 애니메이션 프레임, 방향을 초기화한다.
        self.load_images()  # 필요한 걷기 이미지가 클래스 캐시에 준비되도록 한다.
        self.x, self.y = random.randint(MIN_X, MAX_X), 150  # 왕복 구간 안의 무작위 x좌표와 고정 y좌표에 배치한다.
        self.frame = random.randint(0, 9)  # 여러 좀비의 움직임이 겹치지 않도록 시작 프레임을 무작위로 고른다.
        self.dir = random.choice([-1, 1])  # 처음 이동할 방향을 왼쪽 또는 오른쪽 중 무작위로 고른다.

    def update(self):  # 한 프레임 동안 좀비의 애니메이션과 위치를 갱신한다.
        dt = game_framework.frame_time  # 직전 프레임에 걸린 시간을 초 단위로 가져온다.
        self.frame = (self.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * dt) % FRAMES_PER_ACTION  # 시간에 맞춰 프레임을 진행한다.
        self.x += self.dir * RUN_SPEED_PPS * dt  # 방향, 속력, 경과 시간을 이용해 x좌표를 이동한다.
        if self.x > MAX_X:  # 좀비가 오른쪽 이동 한계를 넘어갔는지 확인한다.
            self.dir = -1  # 오른쪽 끝에 도달하면 왼쪽을 향하도록 방향을 바꾼다.
        elif self.x < MIN_X:  # 좀비가 왼쪽 이동 한계를 넘어갔는지 확인한다.
            self.dir = 1  # 왼쪽 끝에 도달하면 오른쪽을 향하도록 방향을 바꾼다.
        self.x = clamp(MIN_X, self.x, MAX_X)  # x좌표가 허용 구간 밖에 남지 않도록 범위 안으로 제한한다.

    def draw(self):  # 현재 애니메이션 프레임과 방향에 맞춰 좀비를 그린다.
        image = Zombie.images['Walk'][int(self.frame)]  # 실수 프레임을 정수 인덱스로 바꿔 현재 이미지를 고른다.
        if self.dir < 0:  # 좀비가 왼쪽으로 이동 중인지 확인한다.
            image.composite_draw(0, 'h', self.x, self.y, 200, 200)  # 이미지를 수평 반전해 왼쪽을 보게 그린다.
        else:  # 좀비가 오른쪽으로 이동 중이라면
            image.draw(self.x, self.y, 200, 200)  # 원본 방향 그대로 오른쪽을 보게 그린다.
        draw_rectangle(*self.get_bb())  # 디버깅을 위해 좀비의 충돌 사각형을 그린다.

    def get_bb(self):  # 좀비의 축 정렬 충돌 사각형 좌표를 계산한다.
        return self.x - 100, self.y - 100, self.x + 100, self.y + 100  # 중심에서 상하좌우 100픽셀 범위를 반환한다.
    def handle_collision(self, group, other):
        global num
        if group == "ball:zombie":
            if num == 1:
                game_world.remove_object(self)
            if num == 0:
                num += 1
                pass
        