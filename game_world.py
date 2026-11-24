world = [[], [], []]  # 그리기 깊이별 객체 목록이며 0은 배경, 1은 일반 객체, 2는 UI다.

def add_oject(o, depth=1):  # 객체 하나를 지정한 깊이의 월드 레이어에 추가한다.
    world[depth].append(o)  # 해당 깊이의 목록 끝에 객체를 넣는다.

def add_objects(ol, depth=1):  # 여러 객체를 지정한 깊이의 월드 레이어에 한꺼번에 추가한다.
    world[depth] += ol  # 전달받은 객체 목록을 해당 레이어 목록 뒤에 이어 붙인다.

def remove_object(o):  # 객체를 월드와 모든 충돌 목록에서 제거한다.
    for layer in world:  # 모든 깊이의 레이어를 앞에서부터 순회한다.
        if o in layer:  # 현재 레이어에 제거 대상 객체가 있는지 확인한다.
            layer.remove(o)  # 찾은 객체를 월드 레이어에서 제거한다.
            remove_collision_object(o)  # 같은 객체를 등록된 충돌 페어에서도 제거한다.
            return  # 객체를 찾았으므로 더 이상 다른 레이어를 검사하지 않는다.

def update():  # 월드에 등록된 모든 객체를 한 프레임씩 갱신한다.
    for layer in world:  # 배경부터 UI까지 모든 깊이 레이어를 순회한다.
        for o in layer[:]:  # 갱신 도중 원본이 바뀌어도 안전하도록 복사한 목록을 순회한다.
            o.update()  # 현재 객체의 상태 갱신 함수를 호출한다.

def render():  # 월드의 모든 객체를 깊이 순서대로 화면에 그린다.
    for layer in world:  # 낮은 깊이에서 높은 깊이 순서로 레이어를 순회한다.
        for o in layer[:]:  # 그리는 중 목록이 변해도 안전하도록 복사본을 순회한다.
            o.draw()  # 현재 객체의 그리기 함수를 호출한다.




def clear():  # 월드 객체와 충돌 등록 정보를 모두 비운다.
    for layer in world:  # 모든 깊이 레이어를 하나씩 순회한다.
        layer.clear()  # 현재 레이어에 들어 있는 객체 참조를 전부 제거한다.
    collision_pairs.clear()  # 모든 충돌 그룹과 페어 등록 정보도 제거한다.

# 두 객체의 축 정렬 바운딩 박스를 이용해 충돌 여부를 검사한다.
def collide(a, b):  # 객체 a와 b의 사각형이 서로 겹치는지 판정한다.
    left_a, bottom_a, right_a, top_a = a.get_bb()  # 객체 a의 왼쪽, 아래, 오른쪽, 위 경계를 얻는다.
    left_b, bottom_b, right_b, top_b = b.get_bb()  # 객체 b의 왼쪽, 아래, 오른쪽, 위 경계를 얻는다.

    if left_a > right_b: return False  # a가 b보다 완전히 오른쪽이면 충돌하지 않는다.
    if right_a < left_b: return False  # a가 b보다 완전히 왼쪽이면 충돌하지 않는다.
    if top_a < bottom_b: return False  # a가 b보다 완전히 아래쪽이면 충돌하지 않는다.
    if bottom_a > top_b: return False  # a가 b보다 완전히 위쪽이면 충돌하지 않는다.

    return True  # 네 분리 조건이 모두 아니면 두 사각형이 겹친 것으로 판정한다.

collision_pairs = {}  # 그룹 이름을 키로 하고 a측·b측 객체 목록의 튜플을 값으로 보관한다.

def add_collision_pairs(group, a, b):  # 객체를 지정한 충돌 그룹의 a측 또는 b측에 등록한다.
    if group not in collision_pairs:  # 이 이름의 충돌 그룹이 아직 만들어지지 않았는지 확인한다.
        collision_pairs[group] = ([], [])  # 새 그룹에 a측 목록과 b측 목록을 생성한다.
    if a:  # a측에 추가할 객체가 전달되었는지 확인한다.
        collision_pairs[group][0].append(a)  # 객체 a를 그룹의 첫 번째 목록에 등록한다.
    if b:  # b측에 추가할 객체가 전달되었는지 확인한다.
        collision_pairs[group][1].append(b)  # 객체 b를 그룹의 두 번째 목록에 등록한다.

def handle_collision():  # 등록된 모든 충돌 그룹의 객체 조합을 검사하고 반응을 전달한다.
    for group, pairs in collision_pairs.items():  # 그룹 이름과 양쪽 객체 목록을 하나씩 가져온다.
        for a in pairs[0]:  # 현재 그룹의 a측 객체를 순서대로 선택한다.
            for b in pairs[1]:  # 각 a와 짝지을 b측 객체를 순서대로 선택한다.
                if collide(a, b):  # 선택한 두 객체의 충돌 사각형이 겹쳤는지 검사한다.
                    a.handle_collision(group, b)  # a에게 그룹 이름과 충돌 상대 b를 전달한다.
                    b.handle_collision(group, a)  # b에게도 같은 그룹 이름과 충돌 상대 a를 전달한다.


def remove_collision_object(o):  # 한 객체를 모든 충돌 그룹의 양쪽 목록에서 제거한다.
    for pairs in collision_pairs.values():  # 충돌 그룹별 a측·b측 목록을 모두 순회한다.
        if o in pairs[0]:  # 제거 대상이 현재 그룹의 a측 목록에 있는지 확인한다.
            pairs[0].remove(o)  # 발견한 객체를 a측 충돌 목록에서 제거한다.
        if o in pairs[1]:  # 제거 대상이 현재 그룹의 b측 목록에도 있는지 확인한다.
            pairs[1].remove(o)  # 발견한 객체를 b측 충돌 목록에서 제거한다.
