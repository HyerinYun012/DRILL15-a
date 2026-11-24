from pico2d import open_canvas, close_canvas  # 게임 창을 열고 닫는 함수만 가져온다.
import game_framework  # 게임 모드를 실행할 공통 프레임워크를 가져온다.

import play_mode as start_mode  # 플레이 모드를 첫 실행 모드라는 이름으로 가져온다.

open_canvas(1600, 600)  # 너비 1600, 높이 600인 게임 캔버스를 연다.
game_framework.run(start_mode)  # 플레이 모드부터 게임 루프를 시작한다.
close_canvas()  # 게임 루프가 끝나면 캔버스와 관련 자원을 정리한다.

