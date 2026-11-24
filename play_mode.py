from pico2d import *  # 이벤트 처리와 캔버스 렌더링에 필요한 pico2d 기능을 가져온다.
import game_world  # 게임 객체의 등록, 갱신, 렌더링, 충돌을 관리하는 모듈을 가져온다.
import game_framework  # 게임 종료와 프레임 기반 모드 실행을 담당하는 모듈을 가져온다.
from boy import Boy  # 플레이어 캐릭터인 Boy 클래스를 가져온다.
from grass import Grass  # 지면 역할을 하는 Grass 클래스를 가져온다.
from ball import Ball  # 맵에 배치할 공을 만들기 위해 Ball 클래스를 가져온다.
from zombie import Zombie  # 좀비 객체를 만들 수 있도록 Zombie 클래스를 가져온다.
import random  # 공의 초기 x좌표를 무작위로 정하기 위한 표준 모듈을 가져온다.

boy = None  # 현재 플레이 모드에서 사용할 소년 객체 참조를 보관한다.
balls = []  # 현재 플레이 모드가 처음 배치한 공 목록을 보관한다.


def handle_events():  # 한 프레임 동안 발생한 입력과 창 이벤트를 처리한다.
    event_list = get_events()  # pico2d의 이벤트 큐에 쌓인 이벤트들을 목록으로 가져온다.
    for event in event_list:  # 발생한 이벤트를 시간 순서대로 하나씩 처리한다.
        if event.type == SDL_QUIT:  # 창의 닫기 버튼으로 종료를 요청했는지 확인한다.
            game_framework.quit()  # 게임 프레임워크에 전체 루프 종료를 요청한다.
            return  # 종료 이벤트 뒤의 나머지 이벤트는 처리하지 않는다.
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:  # Esc 키를 눌렀는지 확인한다.
            game_framework.quit()  # Esc 입력도 게임 종료 요청으로 처리한다.
        else:  # 종료 요청이 아닌 일반 입력이라면
            boy.handle_event(event)  # 소년 객체가 이동과 발사 입력을 처리하게 한다.


def init():  # 플레이 모드에 필요한 객체와 충돌 그룹을 초기화한다.
    global boy, balls  # 모듈 전역의 소년 참조와 공 목록을 새 객체들로 바꾸겠다고 선언한다.

    boy = Boy()  # 플레이어가 조종할 소년 객체를 생성한다.

    grass = Grass()  # 화면 바닥과 충돌할 잔디 객체를 생성한다.

    balls = [Ball(random.randint(100, 1700), 60, 0) for _ in range(30)]  # 무작위 x좌표에 정지된 공 30개를 만든다.
    game_world.add_objects(balls, 1)  # 생성한 공들을 일반 객체 깊이인 1번 레이어에 등록한다.
    game_world.add_oject(grass, 0)  # 잔디가 다른 객체보다 먼저 그려지도록 배경 레이어에 등록한다.
    game_world.add_collision_pairs("grass:ball", grass, None)  # 잔디를 grass:ball 그룹의 a측에 등록한다.
    game_world.add_oject(boy)  # 소년을 기본 깊이의 게임 월드에 등록한다.

    # 소년과 공 사이의 충돌을 검사할 양쪽 객체들을 충돌 그룹에 등록한다.
    game_world.add_collision_pairs("boy:ball", boy, None)  # 소년을 boy:ball 그룹의 a측에 등록한다.
    for ball in balls:  # 맵에 처음 배치한 공들을 하나씩 순회한다.
        game_world.add_collision_pairs("boy:ball", None, ball)  # 각 공을 boy:ball 그룹의 b측에 등록한다.
    zombies = [Zombie() for _ in range(4)]
    game_world.add_objects(zombies, 1)
    game_world.add_collision_pairs("ball:zombies", None, ball)
    game_world.add_collision_pairs("ball:zombies", zombies, None)


def pause():  # 다른 모드가 위에 쌓일 때 플레이 모드를 일시 정지한다.
    boy.pause()  # 눌린 키와 달리기 상태가 남지 않도록 소년을 정지시킨다.


def resume():  # 위의 모드가 닫혔을 때 플레이 모드 실행을 재개한다.
    pass  # 현재는 재개 시 별도로 복원할 상태가 없다.


def finish():  # 플레이 모드를 끝내며 등록된 객체와 참조를 정리한다.
    global boy, balls  # 전역 소년 참조와 공 목록을 초기 상태로 되돌리겠다고 선언한다.
    game_world.clear()  # 게임 월드의 모든 객체와 충돌 페어를 제거한다.
    boy = None  # 종료된 소년 객체를 더 이상 참조하지 않도록 비운다.
    balls = []  # 플레이 모드가 보관하던 초기 공 목록도 빈 목록으로 바꾼다.


def update():  # 플레이 모드의 모든 객체와 충돌 상태를 한 프레임 갱신한다.
    game_world.update()  # 먼저 월드에 있는 각 객체의 위치와 상태를 갱신한다.
    game_world.handle_collision()  # 갱신된 위치를 기준으로 등록된 객체들의 충돌을 처리한다.


def render():  # 플레이 모드의 현재 장면을 캔버스에 출력한다.
    clear_canvas()  # 이전 프레임의 그림이 남지 않도록 백 버퍼를 지운다.
    game_world.render()  # 월드의 모든 객체를 깊이 순서대로 백 버퍼에 그린다.
    update_canvas()  # 완성된 백 버퍼를 화면에 표시한다.









