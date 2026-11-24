from pico2d import draw_rectangle, get_canvas_width, load_image  # 공의 충돌 영역 표시, 화면 너비 조회, 이미지 로드 함수를 가져온다.

import game_world  # 공을 게임 월드에서 제거하기 위한 모듈을 가져온다.
import game_framework  # 프레임 사이의 경과 시간을 사용하기 위한 모듈을 가져온다.

# 아래 물리 상수의 단위는 픽셀과 초를 기준으로 한다.
LAUNCH_SPEED_X = 300.0  # 공을 던졌을 때의 수평 초기 속력을 지정한다.
LAUNCH_SPEED_Y = 300.0  # 공을 던졌을 때의 수직 초기 속력을 지정한다.
GRAVITY = 9.8 * (10.0 / 0.3)  # 중력 가속도 9.8m/s²를 픽셀/s²로 변환한다.
GROUND_Y = 40  # 잔디 윗면에 해당하는 지면의 y좌표를 지정한다.


class Ball:  # 포물선 운동을 하고 다른 객체와 충돌하는 공을 나타낸다.
    images = {}  # 공 종류별 이미지를 한 번만 읽어 공유할 클래스 "딕셔너리"다.

    def __init__(self, x, y, direction, ball_type=1):  # 위치, 발사 방향, 공 종류로 새 공을 초기화한다.
        if ball_type not in Ball.images:  # images 딕셔너리에 ball_type 키가 없으면 아직 읽지 않은 공 종류이므로
            Ball.images[ball_type] = load_image(  # 공 종류를 키로 사용해 읽은 이미지를 캐시에 저장한다.
                'ball21x21.png' if ball_type == 1 else 'ball41x41.png')  # 1번은 작은 공, 나머지는 큰 공 이미지를 선택한다.
        self.image = Ball.images[ball_type]  # 이 공이 그릴 이미지를 클래스 캐시에서 가져온다.
        self.x, self.y = x, y  # 공 중심의 현재 x, y좌표를 저장한다.
        self.velocity_x = direction * LAUNCH_SPEED_X  # 방향 부호를 반영해 수평 속도를 계산한다.
        self.velocity_y = LAUNCH_SPEED_Y  # 공이 처음 위로 날아가도록 수직 초기 속도를 설정한다.
        self.radius = 10.5 if ball_type == 1 else 20.5  # 이미지 크기에 맞는 충돌 반지름을 정한다.
        self.stopped = (direction == 0)  # 방향이 0인 배치용 공은 처음부터 정지 상태로 둔다.

    def update(self):  # 한 프레임 동안 공의 위치와 속도를 갱신한다.
        if self.stopped:  # 이미 정지한 공이면 물리 계산을 하지 않는다.
            return  # 현재 프레임의 갱신을 즉시 끝낸다.
        dt = game_framework.frame_time  # 직전 프레임에 걸린 시간을 초 단위로 가져온다.
        self.x += self.velocity_x * dt  # 속도와 시간을 곱해 수평 위치를 이동시킨다.
        self.y += self.velocity_y * dt - 0.5 * GRAVITY * dt ** 2  # 등가속도 운동 공식으로 수직 위치를 계산한다.
        self.velocity_y -= GRAVITY * dt  # 중력의 영향을 반영해 수직 속도를 감소시킨다.
        if (self.x < -self.radius or self.x > get_canvas_width() + self.radius  # 공이 화면의 좌우 경계를 완전히 벗어났거나
                or self.y - self.radius <= GROUND_Y):  # 공의 아랫면이 지면 높이에 닿았는지 검사한다.
            # game_world.remove_object(self)  # 필요하다면 경계에 닿은 공을 월드에서 제거할 수 있다.
            pass  # 현재는 직접 처리하지 않고 이후 충돌 처리에 맡긴다.


    def draw(self):  # 현재 위치에 공과 충돌 영역을 그린다.
        self.image.draw(self.x, self.y)  # 공 이미지를 공의 중심 좌표에 출력한다.
        draw_rectangle(*self.get_bb())  # 디버깅을 위해 공의 바운딩 박스를 그린다.

    def get_bb(self):  # 공의 축 정렬 충돌 사각형 좌표를 계산한다.
        return (self.x - self.radius, self.y - self.radius,  # 충돌 사각형의 왼쪽과 아래쪽 좌표를 반환하고
                self.x + self.radius, self.y + self.radius)  # 오른쪽과 위쪽 좌표를 함께 반환한다.

    def handle_collision(self, group, other):  # 충돌 그룹에 따라 공의 반응을 처리한다.
        if group == "boy:ball":  # 소년과 공 사이의 충돌인지 확인한다.
            game_world.remove_object(self)  # 소년이 획득한 공을 게임 월드에서 제거한다.
        if group == "grass:ball":  # 잔디와 공 사이의 충돌인지 확인한다.
            self.stopped = True  # 지면에 닿은 공의 이동과 물리 계산을 멈춘다.
