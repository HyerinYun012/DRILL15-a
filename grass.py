from pico2d import *  # 잔디와 자 이미지를 그리고 충돌 영역을 표시할 pico2d 기능을 가져온다.

class Grass:  # 화면의 지면과 배경 자를 나타내는 객체다.
    def __init__(self):  # 잔디 객체가 사용할 이미지 자원을 초기화한다.
        self.image = load_image('grass.png')  # 잔디 이미지를 파일에서 읽는다.
        self.ruler_image = load_image('ruler.png')  # 배경에 표시할 자 이미지를 파일에서 읽는다.

    def update(self):  # 매 프레임 호출되는 잔디의 갱신 함수다.
        pass  # 잔디는 움직이지 않으므로 갱신할 내용이 없다.

    def draw(self):  # 잔디, 자, 충돌 영역을 화면에 그린다.
        self.image.draw(400, 30)  # 화면 왼쪽 절반의 중앙에 첫 번째 잔디 이미지를 그린다.
        self.image.draw(1200, 30)  # 화면 오른쪽 절반의 중앙에 두 번째 잔디 이미지를 그린다.
        self.ruler_image.draw(800, 350)  # 화면 중앙 위쪽에 높이를 확인할 자 이미지를 그린다.
        draw_rectangle(*self.get_bb())  # 디버깅을 위해 지면의 충돌 사각형을 그린다.

    def get_bb(self):  # 잔디 지면의 축 정렬 충돌 사각형을 반환한다.
        return 0, 0, 1600, 40  # 화면 바닥부터 y=40까지를 지면 충돌 영역으로 지정한다.

    def handle_collision(self, group, other):  # 잔디가 다른 객체와 충돌했을 때 호출된다.
        pass  # 잔디 자체는 충돌해도 상태를 바꿀 필요가 없다.

