import numpy as np
import pandas as pd
import numba as nb
from index import*





@nb.njit()
def getAgentSize():
    return NUMBER_PLAYER

#########################################################

@nb.njit()
def getActionSize():
    return NUMBER_ACTIONS

#########################################################

@nb.njit()
def getStateSize():
    return P_LENGTH 

#########################################################

@nb.njit()
def initEnv():
    #tạo env_state full 0
    env_state = np.zeros(ENV_LENGTH)
    #các đường vô chủ gán là -1
    env_state[ENV_ROAD_BOARD : ENV_ROUTE_CARD_BOARD] = -1
    #các thẻ route đã bị người chơi sở hữu gán là -1
    env_state[ENV_TRAIN_CAR_CARD : ENV_IN4_PLAYER] = -1

    all_special_route_card = np.arange(NUMBER_ROUTE-NUMBER_SPECIAL_ROUTE, NUMBER_ROUTE)
    #chọn 5 thẻ special route cho người chơi
    special_route_card = np.random.choice(all_special_route_card, NUMBER_PLAYER, replace= False)

    all_normal_route_card = np.arange(NUMBER_ROUTE-NUMBER_SPECIAL_ROUTE)
    np.random.shuffle(all_normal_route_card)
    normal_route_card = all_normal_route_card[:NUMBER_PLAYER*NUMBER_ROUTE_GET]
    env_state[ENV_ROUTE_CARD_BOARD : ENV_TRAIN_CAR_CARD] = np.concatenate((all_normal_route_card[NUMBER_PLAYER*NUMBER_ROUTE_GET:],np.full(NUMBER_SPECIAL_ROUTE+NUMBER_PLAYER*NUMBER_ROUTE_GET, -1)))
    all_train_car_card = np.concatenate((np.zeros(14), np.ones(12), np.full(12,2),
                                        np.full(12,3), np.full(12,4), np.full(12,5),
                                        np.full(12,6), np.full(12,7), np.full(12,8)))
    #các thẻ xe lửa                                                            
    np.random.shuffle(all_train_car_card)
    train_car_card = all_train_car_card[:NUMBER_PLAYER*NUMBER_TRAIN_CAR_GET]            #các thẻ xe lửa cho người chơi
    #các thẻ xe lửa trong chồng bài úp
    env_state[ENV_TRAIN_CAR_CARD : ENV_TRAIN_CAR_CARD + NUMBER_TRAIN_CAR_CARD - NUMBER_PLAYER*NUMBER_TRAIN_CAR_GET - NUMBER_TRAIN_CAR_CARD_OPEN] = all_train_car_card[NUMBER_PLAYER*NUMBER_TRAIN_CAR_GET + NUMBER_TRAIN_CAR_CARD_OPEN :]
    
    for id_pl in range(NUMBER_PLAYER):
        special_route_id = special_route_card[id_pl]
        normal_route_id = normal_route_card[id_pl*NUMBER_ROUTE_GET : NUMBER_ROUTE_GET*(id_pl+1)]
        train_car_card_id = train_car_card[id_pl*NUMBER_TRAIN_CAR_GET : NUMBER_TRAIN_CAR_GET*(id_pl+1)]

        score_train_car = np.array([0, NUMBER_TRAIN])
        train_card_id = np.zeros(9)
        for id_train in train_car_card_id:
            train_card_id[int(id_train)] += 1
        route_card_id = np.zeros(NUMBER_ROUTE)
        route_card_id[special_route_id] = 1
        route_card_id[normal_route_id] = 1
        env_state[ENV_IN4_PLAYER + ATTRIBUTE_PLAYER*id_pl : ENV_IN4_PLAYER + ATTRIBUTE_PLAYER*(id_pl + 1)] = np.concatenate((score_train_car, train_card_id, route_card_id))
    #các thẻ xe lửa được mở
    env_state[ENV_TRAIN_CAR_OPEN : ENV_TRAIN_CAR_OPEN + NUMBER_TRAIN_CAR_CARD_OPEN] = all_train_car_card[NUMBER_PLAYER*NUMBER_TRAIN_CAR_GET : NUMBER_PLAYER*NUMBER_TRAIN_CAR_GET + NUMBER_TRAIN_CAR_CARD_OPEN]
    env_state[ENV_ROUTE_CARD_GET : ENV_ROUTE_CARD_GET + NUMBER_ROUTE_RECEIVE] = -1
    #Other in4
    env_state[ENV_PHASE] = 3        #đầu game thì đi loại thẻ route
    env_state[ENV_CHECK_END] = 0
    env_state[ENV_ID_PLAYER_END] = -1
    env_state[ENV_ROAD_BUILT] = -1
    env_state[ENV_TURN] = 1
    id_action = int(env_state[ENV_ID_ACTION])
    env_state[ENV_ROUTE_CARD_GET : ENV_TRAIN_CAR_DROP] = env_state[ENV_IN4_PLAYER : ENV_TRAIN_CAR_OPEN][id_action * ATTRIBUTE_PLAYER : (id_action+1) * ATTRIBUTE_PLAYER][2 + NUMBER_TYPE_TRAIN_CAR_CARD : ]
    env_state[ENV_IN4_PLAYER : ENV_TRAIN_CAR_OPEN][id_action * ATTRIBUTE_PLAYER : (id_action+1) * ATTRIBUTE_PLAYER][2 + NUMBER_TYPE_TRAIN_CAR_CARD : ] = 0
    env_state[ENV_PHASE] = 3

    return env_state

#########################################################

@nb.njit()
def getAgentState(env_state):
    id_action = int(env_state[ENV_ID_ACTION])
    #điểm tất cả người chơi
    all_player_score = env_state[ENV_IN4_PLAYER : ENV_TRAIN_CAR_OPEN : ATTRIBUTE_PLAYER]
    player_state = np.zeros(P_LENGTH)
    player_state[P_SCORE : P_TRAIN_CAR_CARD] = np.concatenate((all_player_score[id_action :], all_player_score[: id_action]))
    #số thẻ train_car_card của người chơi
    player_state[P_TRAIN_CAR_CARD : P_PLAYER_ROAD] = env_state[ENV_IN4_PLAYER : ENV_TRAIN_CAR_OPEN][id_action * ATTRIBUTE_PLAYER : (id_action+1) * ATTRIBUTE_PLAYER][2 : 2 + NUMBER_TYPE_TRAIN_CAR_CARD]
    #số tàu người chơi còn
    player_state[P_NUMBER_TRAIN] = env_state[ENV_IN4_PLAYER : ENV_TRAIN_CAR_OPEN][id_action * ATTRIBUTE_PLAYER : (id_action+1) * ATTRIBUTE_PLAYER][1]
    #đường của các người chơi
    for id_ in range(NUMBER_PLAYER):
        list_road_id_ = np.where(env_state[ENV_ROAD_BOARD : ENV_ROUTE_CARD_BOARD] == id_)[0]
        idx = (id_ - id_action) % NUMBER_PLAYER
        player_state[P_PLAYER_ROAD : P_ROUTE_CARD][idx*NUMBER_ROAD : (idx+1) * NUMBER_ROAD][list_road_id_] = 1
    #thẻ route của người chơi
    player_route_card = np.zeros(NUMBER_ROUTE)
    player_route_card[np.where(env_state[ENV_IN4_PLAYER : ENV_TRAIN_CAR_OPEN][id_action * ATTRIBUTE_PLAYER : (id_action+1) * ATTRIBUTE_PLAYER][2 + NUMBER_TYPE_TRAIN_CAR_CARD : ] > 0)[0]] = 1
    
    player_state[P_ROUTE_CARD : P_ROUTE_GET] = player_route_card
    #route card get
    route_card_get = env_state[ENV_ROUTE_CARD_GET : ENV_TRAIN_CAR_DROP].astype(np.int64)
    player_state[P_ROUTE_GET : P_TRAIN_CAR_CARD_BOARD] = route_card_get
    #thẻ train_car trên bàn chơi
    for type_car in env_state[ENV_TRAIN_CAR_OPEN : ENV_ROUTE_CARD_GET]:
        if type_car != -1:
            player_state[P_TRAIN_CAR_CARD_BOARD : P_CARD_BULD_TUNNEL][int(type_car)] += 1
    player_state[P_CARD_BULD_TUNNEL : P_CARD_TEST_TUNNEL] = env_state[ENV_CARD_BULD_TUNNEL : ENV_CARD_TEST_TUNNEL]
    player_state[P_ID_ACTION] = 0       #dấu hiệu đánh giá mình hành động
    player_state[P_PHASE + int(env_state[ENV_PHASE]) - 1 ] = 1          #edit 13h 4/1/2023
    player_state[P_CHECK_ROUTE_CARD] = int(env_state[ENV_ROUTE_CARD_BOARD] > -1)
    player_state[P_CHEKC_END] = int(env_state[ENV_CHECK_END] / 2)
    # print(env_state[ENV_CHECK_END], player_state[P_CHEKC_END])
    if env_state[ENV_ID_PLAYER_END] != -1:
        player_state[P_ID_PLAYER_END + int((env_state[ENV_ID_PLAYER_END] - id_action) % NUMBER_PLAYER)] =  1     #edit 13h 4/1/2023
    player_state[P_NUMBER_TRAIN_CAR_GET] = env_state[ENV_NUMBER_TRAIN_CAR_GET]
    player_state[P_NUMBER_DROP_ROUTE_CARD] = env_state[ENV_NUMBER_DROP_ROUTE_CARD]
    player_state[P_CARD_TEST_TUNNEL : P_TYPE_TRAIN_CAR_BUILD_ROAD] = env_state[ENV_CARD_TEST_TUNNEL : ENV_CARD_TEST_TUNNEL + NUMBER_TYPE_TRAIN_CAR_CARD]
    player_state[P_TYPE_TRAIN_CAR_BUILD_ROAD : P_TYPE_TRAIN_CAR_BUILD_ROAD + NUMBER_TYPE_TRAIN_CAR_CARD] = env_state[ENV_TYPE_TRAIN_CAR_BUILD_ROAD : ENV_TYPE_TRAIN_CAR_BUILD_ROAD + NUMBER_TYPE_TRAIN_CAR_CARD]
    if env_state[ENV_TRAIN_CAR_CARD] != -1 and np.min(env_state[ENV_TRAIN_CAR_OPEN : ENV_ROUTE_CARD_GET]) > -1:
        player_state[P_ACTION_GET_TRAIN_CAR_DOWN] = 1
    return player_state

#########################################################

@nb.njit()
def find_blank_road(player_state):
    #đưa vào tất cả các đường
    road_status = np.ones(NUMBER_ROAD)
    all_road_built = np.where(player_state[P_PLAYER_ROAD : P_PLAYER_ROAD + NUMBER_ROAD] == 1)[0]
    #loại bỏ các cạnh đối xứng với các đường người chơi đã xây
    for road in all_road_built:
        if road in LIST_CIRCLE:
            road_status[LIST_EDGE_SYMETRY[road]] = 0
    for id in range(1, NUMBER_PLAYER):
        all_road_built = np.append(all_road_built,  np.where(player_state[P_PLAYER_ROAD + NUMBER_ROAD * id : P_PLAYER_ROAD + NUMBER_ROAD * (id + 1)] == 1)[0])
    road_status[all_road_built] = 0
    road_blank = np.where(road_status == 1)[0]
    return road_blank

#########################################################

@nb.njit()
def check_road_can_build(player_state):
    number_train_else = player_state[P_NUMBER_TRAIN]
    road_blank = find_blank_road(player_state)
    road_can_build = np.zeros(NUMBER_ROAD)
    player_train_car = player_state[P_TRAIN_CAR_CARD : P_PLAYER_ROAD]
    temp_train_car = player_train_car.copy()
    temp_train_car[1:] +=  temp_train_car[0]
    for road in road_blank:
        if LIST_ALL_LENGTH_ROAD[road] > number_train_else:
            continue
        #nếu là đường không cần đầu máy
        if LIST_ALL_TYPE_ROAD[road] !=  2:
            road_color = LIST_ALL_COLOR_ROAD[road]
            #nếu là đường màu xám
            if road_color == -1:
                if np.max(temp_train_car) >= LIST_ALL_LENGTH_ROAD[road]:
                    road_can_build[road] = 1
                else:
                    continue
            #nếu đường có màu bình thường
            else:
                if player_train_car[road_color] >= LIST_ALL_LENGTH_ROAD[road]:
                    road_can_build[road] = 1
                else:
                    continue
        else:
            #nếu là ferry
            if temp_train_car[0] >= LIST_ROAD_LOCOMOTIVES[road] and np.max(temp_train_car) >= LIST_ALL_LENGTH_ROAD[road]:
                road_can_build[road] = 1
            else:
                continue
    road_enough_to_build = np.where(road_can_build == 1)[0]
    return road_enough_to_build

#########################################################

@nb.njit()
def find_longest_road(length: int, start_point, set_road_used, player_road, player_point):
    list_road_check = [9999]
    for road in POINT_ROAD_RELATIVE[start_point]:
        if road in player_road:
            if road not in set_road_used:
                list_road_check.append(road)
    list_road_check.remove(9999)
    if len(list_road_check) == 0 or start_point not in player_point:
        if length != 0:
            return length
    list_length = [9999]
    for road in list_road_check:
        set_road_used_copy = set_road_used.copy()
        set_road_used_copy = np.append(set_road_used_copy, road)
        start_point_i = 9999
        for point in LIST_ALL_ROAD_POINT[road]:
            if point != start_point:
                start_point_i = point
                break
        if start_point_i != 9999:
            length_i = length + LIST_ALL_LENGTH_ROAD[road]
            list_length.append(find_longest_road(length_i, start_point_i, set_road_used_copy, player_road, player_point))
    list_length.remove(9999)
    return max(list_length)

#########################################################

@nb.njit()
def calculator_longest_road(p_road):
    length = 0
    pointOfRoad = LIST_ALL_ROAD_POINT[p_road]
    player_point = np.unique(pointOfRoad.flatten()).astype(np.int64)
    list_len_road = [-9999]
    for point in player_point:
        length_point_i = find_longest_road(length, point, np.array([-999]), p_road, player_point)
        list_len_road.append(length_point_i)
    return max(list_len_road)

#########################################################

@nb.njit()
def check_done_route_card(p_road, point_source, point_dest):
    pointOfRoad = LIST_ALL_ROAD_POINT[p_road]
    player_point = np.unique(pointOfRoad.flatten()).astype(np.int64)
    if point_source not in player_point or point_dest not in player_point:
        return 0
    else:
        road_checked = np.zeros(NUMBER_ROAD)
        check = True
        check_point = np.array([point_source], dtype=np.int64)
        point_checked = np.zeros(NUMBER_CITY)
        point_checked[check_point] = 1
        while check:
            point_checked[check_point] = 1
            check_point_new = np.zeros(NUMBER_CITY)
            test_road = np.unique(POINT_ROAD_RELATIVE[check_point].flatten())
            test_road = test_road[test_road > -1]
            for road in test_road:
                # print(road)
                if road_checked[road] == 0 and road in p_road:
                    if point_dest in LIST_ALL_ROAD_POINT[road]:
                        return 1
                    else:
                        check_point_new[LIST_ALL_ROAD_POINT[road]] = 1
                road_checked[road] = 1
            check_point = np.where((check_point_new > point_checked) == True)[0].astype(np.int64)
            if len(check_point) == 0:
                check = False
        return 0

#########################################################

@nb.njit()
def shuffle_drop_card(env_state):
    drop_card = env_state[ENV_TRAIN_CAR_DROP : ENV_CARD_BULD_TUNNEL].astype(np.int64)
    list_card = np.zeros(drop_card[0])
    for id in range(1, len(drop_card)):
        list_card = np.append(list_card, np.full(drop_card[id], id))
    np.random.shuffle(list_card)
    temp_card_board = env_state[ENV_TRAIN_CAR_CARD : ENV_IN4_PLAYER]
    start_slice = np.where(temp_card_board == -1)[0][0]
    temp_card_board[start_slice : start_slice + len(list_card)] = list_card
    card_open = env_state[ENV_TRAIN_CAR_OPEN : ENV_ROUTE_CARD_GET]
    #nếu các thẻ mở đang ko đủ bài
    if np.min(card_open) == -1:
        card_open = np.sort(card_open)
        number_train_card_need = len(card_open[card_open == -1])
        card_open = np.concatenate((temp_card_board[:number_train_card_need], card_open[number_train_card_need:]))
        env_state[ENV_TRAIN_CAR_CARD : ENV_IN4_PLAYER - number_train_card_need] = temp_card_board[number_train_card_need:]
    else:
        env_state[ENV_TRAIN_CAR_CARD : ENV_IN4_PLAYER] = temp_card_board
    env_state[ENV_TRAIN_CAR_DROP : ENV_CARD_BULD_TUNNEL] = 0
    return env_state

#########################################################

@nb.njit()
def process_train_car_board(env_state):
    # number_train_card_board = len(np.where(env_state[ENV_TRAIN_CAR_OPEN : ENV_ROUTE_CARD_GET] != -1)) + np.sum(env_state[ENV_TRAIN_CAR_DROP : ENV_CARD_BULD_TUNNEL])
    check = True
    while check:
        car_open = env_state[ENV_TRAIN_CAR_OPEN : ENV_ROUTE_CARD_GET]
        if len(np.where(car_open == 0)[0]) < 3:
            return env_state
        else:
            # print('Có 3 thẻ locomotive trên bàn', car_open, env_state[ENV_TRAIN_CAR_DROP : ENV_CARD_BULD_TUNNEL], LIST_COLOR)
            #nếu thẻ lật có quá 3 thẻ locomotive
            #drop hết thẻ trên bàn
            for car in car_open:
                if car != -1:
                    env_state[ENV_TRAIN_CAR_DROP : ENV_CARD_BULD_TUNNEL][int(car)] += 1
            #kiểm tra chồng bài úp
            card_board = env_state[ENV_TRAIN_CAR_CARD : ENV_IN4_PLAYER].astype(np.int64)
            card_board = card_board[card_board > -1]
            # nếu đủ lật tiếp
            if len(card_board) >= NUMBER_TRAIN_CAR_CARD_OPEN:
                env_state[ENV_TRAIN_CAR_OPEN : ENV_ROUTE_CARD_GET] = env_state[ENV_TRAIN_CAR_CARD : ENV_TRAIN_CAR_CARD + NUMBER_TRAIN_CAR_CARD_OPEN]
                env_state[ENV_TRAIN_CAR_CARD : ENV_IN4_PLAYER] = np.concatenate((env_state[ENV_TRAIN_CAR_CARD : ENV_IN4_PLAYER][NUMBER_TRAIN_CAR_CARD_OPEN:], np.array([-1]*NUMBER_TRAIN_CAR_CARD_OPEN)))
                check = True
            else:
                #nếu k đủ lật tiếp 5 lá thì đi gộp với bài cũ
                drop_card = env_state[ENV_TRAIN_CAR_DROP : ENV_CARD_BULD_TUNNEL].astype(np.int64)
                list_card = np.zeros(drop_card[0])
                for id in range(1, NUMBER_TYPE_TRAIN_CAR_CARD):
                    list_card = np.append(list_card, np.full(drop_card[id], id))
                np.random.shuffle(list_card)
                temp_card_board = env_state[ENV_TRAIN_CAR_CARD : ENV_IN4_PLAYER]        
                start_slice = np.where(temp_card_board == -1)[0][0]
                temp_card_board[start_slice : start_slice + len(list_card)] = list_card
                #nếu tổng số thẻ train_car trên bàn >= 5 nhưng số thẻ khác locomotive <= 2 thì ko lật ra thẻ nào, ko cho nhặt chồng bài úp
                if len(temp_card_board[temp_card_board > -1]) >= NUMBER_TRAIN_CAR_CARD_OPEN:
                    if len(temp_card_board[temp_card_board > 0]) < 3:
                        env_state[ENV_TRAIN_CAR_OPEN : ENV_ROUTE_CARD_GET] = -1
                        env_state[ENV_TRAIN_CAR_DROP : ENV_CARD_BULD_TUNNEL] = 0
                        env_state[ENV_TRAIN_CAR_CARD : ENV_IN4_PLAYER] = temp_card_board
                        return env_state
                    else:
                        #lật thẻ cho open card
                        env_state[ENV_TRAIN_CAR_OPEN : ENV_ROUTE_CARD_GET] = temp_card_board[:NUMBER_TRAIN_CAR_CARD_OPEN]
                        #đẩy chỗ thẻ còn lại vào chồng bài úp
                        env_state[ENV_TRAIN_CAR_CARD : ENV_IN4_PLAYER] = np.concatenate((temp_card_board[NUMBER_TRAIN_CAR_CARD_OPEN :], np.array([-1]*NUMBER_TRAIN_CAR_CARD_OPEN)))
                        env_state[ENV_TRAIN_CAR_DROP : ENV_CARD_BULD_TUNNEL] = 0
                        check = True

                #nếu còn ít thẻ quá
                else:
                    #nếu nhiều locomotive quá k lật đc thì k lật thẻ nào
                    if len(temp_card_board[temp_card_board == 0]) >= 3:
                        env_state[ENV_TRAIN_CAR_OPEN : ENV_ROUTE_CARD_GET] = -1
                        env_state[ENV_TRAIN_CAR_DROP : ENV_CARD_BULD_TUNNEL] = 0
                        env_state[ENV_TRAIN_CAR_CARD : ENV_IN4_PLAYER] = temp_card_board
                        return env_state
                    #nếu ít locomotive và lật đc thẻ thì lật hết ra
                    else:
                        #lật thẻ cho open card
                        env_state[ENV_TRAIN_CAR_OPEN : ENV_ROUTE_CARD_GET] = temp_card_board[:NUMBER_TRAIN_CAR_CARD_OPEN]
                        #đẩy chỗ thẻ còn lại vào chồng bài úp
                        env_state[ENV_TRAIN_CAR_CARD : ENV_IN4_PLAYER] = np.concatenate((temp_card_board[NUMBER_TRAIN_CAR_CARD_OPEN :], np.array([-1]*NUMBER_TRAIN_CAR_CARD_OPEN)))
                        env_state[ENV_TRAIN_CAR_DROP : ENV_CARD_BULD_TUNNEL] = 0
                        
                        check = True

#########################################################

@nb.njit()
def getReward(player_state):
    list_score = player_state[P_SCORE : P_TRAIN_CAR_CARD]
    if player_state[P_CHEKC_END] == 1:
        if np.argmax(list_score) == 0:
            # if len(np.where(list_score == np.max(list_score))[0]) == 1:
            #     return 1
            # else:
            #     return 0
            return 1
        else:
            return 0
    else:
        return -1

#########################################################

def player_random(player_state, file_per):
    list_action = np.where(getValidActions(player_state) > 0)[0]
    action = int(np.random.choice(list_action))
    if getReward(player_state) == -1:
        # print('chưa hết game')
        pass
    else:
        if getReward(player_state) == 1:
            # print('win')
            pass
        else:
            # print('lose')
            pass
    return action, file_per

#########################################################

@nb.njit()
def check_winner(env_state):
    #B1: tìm người chơi con đường dài nhất
    list_longest_path = np.zeros(NUMBER_PLAYER)
    all_road = env_state[ENV_ROAD_BOARD : ENV_ROUTE_CARD_BOARD]
    number_route_comp = np.zeros(NUMBER_PLAYER)
    for player in range(NUMBER_PLAYER):
        p_road = np.where(all_road == player)[0]
        all_player_route_card = np.where(env_state[ENV_IN4_PLAYER + ATTRIBUTE_PLAYER * player : ENV_IN4_PLAYER + ATTRIBUTE_PLAYER* (player + 1)][2 + NUMBER_TYPE_TRAIN_CAR_CARD:] == 1)[0]
        #tính toán điểm của thẻ route
        for route_card in all_player_route_card:
            point_source = LIST_ALL_ROUTE_POINT[route_card][0]
            point_dest = LIST_ALL_ROUTE_POINT[route_card][1]
            check_done = check_done_route_card(p_road, point_source, point_dest)
            if check_done == 1:
                number_route_comp[player] += 1
                env_state[ENV_IN4_PLAYER + ATTRIBUTE_PLAYER * player : ENV_IN4_PLAYER + ATTRIBUTE_PLAYER* (player + 1)][0] += LIST_ALL_SCORE_ROUTE[route_card]
            else:
                env_state[ENV_IN4_PLAYER + ATTRIBUTE_PLAYER * player : ENV_IN4_PLAYER + ATTRIBUTE_PLAYER* (player + 1)][0] -= LIST_ALL_SCORE_ROUTE[route_card]
        list_longest_path[player] = calculator_longest_road(p_road)
    max_road = np.max(list_longest_path)
    player_longest_path = np.where(list_longest_path == max_road)[0]
    #cộng 10đ cho những người có đường dài nhất
    for player in player_longest_path:
        env_state[ENV_IN4_PLAYER + ATTRIBUTE_PLAYER * player : ENV_IN4_PLAYER + ATTRIBUTE_PLAYER* (player + 1)][0] += 10
    #xét người chiến thắng
    all_player_score = env_state[ENV_IN4_PLAYER : ENV_TRAIN_CAR_OPEN - 1 : ATTRIBUTE_PLAYER]
    score_max = np.max(all_player_score)
    winner_1 = np.where(all_player_score == score_max)[0]
    if len(winner_1) == 1:
        return winner_1, env_state
    else:
        number_route_winner_comp = np.full(NUMBER_PLAYER, -1)
        number_route_winner_comp[winner_1] = number_route_comp[winner_1]
        route_max = np.max(number_route_winner_comp)
        # if route_max
        winner_2 = np.where(number_route_winner_comp == route_max)[0]
        if len(winner_2) == 1:
            player_win = winner_2[0]
            env_state[ENV_IN4_PLAYER + ATTRIBUTE_PLAYER * player_win : ENV_IN4_PLAYER + ATTRIBUTE_PLAYER* (player_win + 1)][0] += 0.1
            return winner_2, env_state
        else:
            winner_3 = np.array([-1])
            count = 0
            for player in winner_2:
                if player in player_longest_path:
                    winner_3 = np.append(winner_3, player)
                    count += 1
            if len(winner_3) == 1:
                return winner_2, env_state
            else:
                winner_3 = winner_3[1:]
                if len(winner_3) == 1:
                    player_win = winner_3[0]
                    env_state[ENV_IN4_PLAYER + ATTRIBUTE_PLAYER * player_win : ENV_IN4_PLAYER + ATTRIBUTE_PLAYER* (player_win + 1)][0] += 0.1
                return winner_3, env_state
            

#########################################################

@nb.njit()
def system_check_end(env_state):
    if env_state[ENV_CHECK_END] == 2 and env_state[ENV_ID_PLAYER_END] == env_state[ENV_ID_ACTION]:
        return False
    else:
        return True

#########################################################
 
def normal_main(list_player, num_games, per_file):
    if len(list_player) != NUMBER_PLAYER:
        print(f'Game yêu cầu {NUMBER_PLAYER} người chơi')
        return [-1]*NUMBER_PLAYER, per_file
    count = np.zeros(len(list_player)+1)
    all_id_player = np.arange(len(list_player))

    for van in range(num_games):
        np.random.shuffle(all_id_player)
        shuffle = all_id_player.copy()
        shuffle_player = [list_player[id] for id in shuffle]
        winner, per_file = one_game(shuffle_player, per_file)
        if winner[0] == -1:
            count[winner] += 1
        else:
            count[shuffle[winner]] += 1
    return list(count.astype(np.int64)), per_file

#########################################################
   
def one_game(list_player, file_per):
    env_state = initEnv()
    count_turn = 0
    while system_check_end(env_state) and count_turn < 7000:
        count_turn += 1
        current_player = int(env_state[ENV_ID_ACTION])
        player_state = getAgentState(env_state)
        action,file_per = list_player[current_player](player_state,file_per)
        list_action = getValidActions(player_state)
        if list_action[int(action)] != 1:
            raise Exception('Action không hợp lệ')
        env_state = stepEnv(env_state, action)
    winner, env_state = check_winner(env_state)
    all_player_score = env_state[ENV_IN4_PLAYER : ENV_TRAIN_CAR_OPEN - 1 : ATTRIBUTE_PLAYER]
    for current_player in range(NUMBER_PLAYER):
        env_state[ENV_PHASE] = 1
        env_state[ENV_ID_ACTION] = current_player
        player_state = getAgentState(env_state)
        action,file_per = list_player[current_player](player_state,file_per)
    # print(winner)
    return winner, file_per

#########################################################

@nb.njit()
def getValidActions(player_state_origin):
    player_state = player_state_origin.copy()
    phase_game = np.where(player_state[P_PHASE : P_PHASE + NUMBER_PHASE] == 1)[0][0] + 1
    # print(phase_game, 'phase')
    list_action_return = np.zeros(NUMBER_ACTIONS)
    if phase_game == 1:
        #kiểm tra các hành động nhặt train_car làm được
        train_car_board = player_state[P_TRAIN_CAR_CARD_BOARD : P_CARD_BULD_TUNNEL]
        if player_state[P_ACTION_GET_TRAIN_CAR_DOWN] == 1:
            list_action_return[156] = 1             #action nhặt thẻ úp
        if player_state[P_NUMBER_TRAIN_CAR_GET] == 0:
            #kiểm tra nhặt được thẻ ko
            if player_state[P_CHECK_ROUTE_CARD] != 0:
                list_action_return[169] = 1
            #kiểm tra các đường xây được
            road_can_build = check_road_can_build(player_state)
            # print(road_can_build)
            list_action_return[road_can_build] = 1
            train_car_can_get = np.where(train_car_board > 0)[0] + 147
            list_action_return[train_car_can_get] = 1
        else:      # player_state[P_NUMBER_TRAIN_CAR_GET] != 0:
            #nếu đã nhặt thẻ train_car thì k được nhặt thẻ locomotive
            train_car_board[0] = 0
            train_car_can_get = np.where(train_car_board > 0)[0] + 147
            list_action_return[train_car_can_get] = 1
    elif phase_game == 2:
        #chọn tài nguyên để xây đường
        '''
        các kiểu dùng tài nguyên để xây con đường muốn xây được lưu ở player_state, từ đó xác định các cách xây có thể
        '''
        type_train_car_build_road = np.where(player_state[P_TYPE_TRAIN_CAR_BUILD_ROAD : P_TYPE_TRAIN_CAR_BUILD_ROAD + NUMBER_TYPE_TRAIN_CAR_CARD] > 0)[0]
        list_action_return[type_train_car_build_road + 157] = 1

    elif phase_game == 3:
        route_card_can_drop = np.where(player_state[P_ROUTE_GET : P_TRAIN_CAR_CARD_BOARD] == 1)[0]
        if player_state[P_NUMBER_DROP_ROUTE_CARD] < 2:
            list_action_return[route_card_can_drop + NUMBER_ROAD] = 1
        list_action_return[170] = 1         #dừng drop thẻ route
    
    elif phase_game == 4:
        card_build_tunnel = np.where(player_state[P_CARD_BULD_TUNNEL : P_CARD_TEST_TUNNEL] > 0)[0]
        card_test_tunnel = player_state[P_CARD_TEST_TUNNEL : P_TYPE_TRAIN_CAR_BUILD_ROAD]
        player_train_car = player_state[P_TRAIN_CAR_CARD : P_PLAYER_ROAD]
        check = 1
        test_train_car = 0
        for type_car in card_build_tunnel:
            if card_test_tunnel[type_car] > 0:
                if type_car == 0:
                    test_train_car -= card_test_tunnel[type_car]
                else:
                    test_train_car -= max(card_test_tunnel[type_car] - player_train_car[type_car], 0)
            else:
                continue
        if player_train_car[0] + test_train_car < 0:
            check = 0
        list_action_return[167] = check
        list_action_return[168] = 1
    if np.sum(list_action_return) == 0:
        # print(list(player_state))
        list_action_return[-1] = 1


    return list_action_return

#########################################################

@nb.njit()
def stepEnv(env_state, action):
    phase_game = env_state[ENV_PHASE]
    id_action = int(env_state[ENV_ID_ACTION])

    if phase_game == 1:

        if action < NUMBER_ROAD:    #nếu action là xây đường, xử lí xây đường
            road = action
            player_train_car = env_state[ENV_IN4_PLAYER + ATTRIBUTE_PLAYER * id_action : ENV_IN4_PLAYER + ATTRIBUTE_PLAYER* (id_action + 1)][2 : 2 + NUMBER_TYPE_TRAIN_CAR_CARD]
            temp_train_car = player_train_car.copy()
            train_car_else = np.where(temp_train_car[1:] > 0)[0] + 1
            temp_train_car[train_car_else] +=  temp_train_car[0]
            #nếu đường ko cần đầu máy
            if LIST_ALL_TYPE_ROAD[road] !=  2:
                road_color = LIST_ALL_COLOR_ROAD[road]
                #nếu là đường màu xám
                if road_color == -1:
                    type_build = np.where(temp_train_car >= LIST_ALL_LENGTH_ROAD[road])[0]
                    env_state[ENV_TYPE_TRAIN_CAR_BUILD_ROAD : ENV_TYPE_TRAIN_CAR_BUILD_ROAD + NUMBER_TYPE_TRAIN_CAR_CARD][type_build] = 1
                else:
                    if player_train_car[0] >= LIST_ALL_LENGTH_ROAD[road]:
                        env_state[ENV_TYPE_TRAIN_CAR_BUILD_ROAD : ENV_TYPE_TRAIN_CAR_BUILD_ROAD + NUMBER_TYPE_TRAIN_CAR_CARD][0] = 1
                    env_state[ENV_TYPE_TRAIN_CAR_BUILD_ROAD : ENV_TYPE_TRAIN_CAR_BUILD_ROAD + NUMBER_TYPE_TRAIN_CAR_CARD][road_color] = 1

            #nếu là ferry cần locomotive 
            else:       
                type_build = np.where(temp_train_car >= LIST_ALL_LENGTH_ROAD[road])[0]
                env_state[ENV_TYPE_TRAIN_CAR_BUILD_ROAD : ENV_TYPE_TRAIN_CAR_BUILD_ROAD + NUMBER_TYPE_TRAIN_CAR_CARD][type_build] = 1
            env_state[ENV_PHASE] = 2
            env_state[ENV_ROAD_BUILT] = action
        #nếu nhặt thẻ locomotive thì update thông tin bàn chơi rồi chuyển người
        elif action == 147:
            #cập nhật các thẻ mở

            new_train_car = env_state[ENV_TRAIN_CAR_CARD]
            index_drop = np.where(env_state[ENV_TRAIN_CAR_OPEN : ENV_ROUTE_CARD_GET] == 0)[0][0]
            env_state[ENV_TRAIN_CAR_OPEN : ENV_ROUTE_CARD_GET][index_drop] = new_train_car
            env_state[ENV_TRAIN_CAR_CARD : ENV_IN4_PLAYER] = np.concatenate((env_state[ENV_TRAIN_CAR_CARD : ENV_IN4_PLAYER][1:], np.array([-1])))
                
            env_state[ENV_IN4_PLAYER + ATTRIBUTE_PLAYER * id_action : ENV_IN4_PLAYER + ATTRIBUTE_PLAYER* (id_action + 1)][action - 147 + 2] += 1
            env_state[ENV_ID_ACTION] = (id_action + 1) % NUMBER_PLAYER
            if env_state[ENV_CHECK_END] >= 1:
                if env_state[ENV_ID_ACTION] == env_state[ENV_ID_PLAYER_END]:
                    env_state[ENV_CHECK_END] += 0.5              #edit by Hieu 05012023
            env_state = process_train_car_board(env_state)
            #xáo thẻ drop nếu chồng bài úp hết bài
            if env_state[ENV_TRAIN_CAR_CARD] == -1 and np.sum(env_state[ENV_TRAIN_CAR_DROP : ENV_CARD_BULD_TUNNEL]) > 0:
                env_state = shuffle_drop_card(env_state)
        #nếu nhặt thẻ thường
        elif action < 156:
            type_car_get = action - 147
            new_train_car = env_state[ENV_TRAIN_CAR_CARD]
            index_drop = np.where(env_state[ENV_TRAIN_CAR_OPEN : ENV_ROUTE_CARD_GET] == type_car_get)[0][0]
            env_state[ENV_TRAIN_CAR_OPEN : ENV_ROUTE_CARD_GET][index_drop] = new_train_car
            env_state[ENV_TRAIN_CAR_CARD : ENV_IN4_PLAYER] = np.concatenate((env_state[ENV_TRAIN_CAR_CARD : ENV_IN4_PLAYER][1:], np.array([-1])))
            env_state[ENV_IN4_PLAYER + ATTRIBUTE_PLAYER * id_action : ENV_IN4_PLAYER + ATTRIBUTE_PLAYER* (id_action + 1)][type_car_get + 2] += 1
            env_state = process_train_car_board(env_state)

            #xáo thẻ drop nếu chồng bài úp hết bài
            if env_state[ENV_TRAIN_CAR_CARD] == -1 and np.sum(env_state[ENV_TRAIN_CAR_DROP : ENV_CARD_BULD_TUNNEL]):
                env_state = shuffle_drop_card(env_state)
            env_state[ENV_NUMBER_TRAIN_CAR_GET] += 1
            #nếu đã nhặt đủ 2 thẻ
            if env_state[ENV_NUMBER_TRAIN_CAR_GET] == 2:
                #reset số thẻ đã nhặt, cập nhật người chơi mơi
                env_state[ENV_NUMBER_TRAIN_CAR_GET] = 0
                env_state[ENV_ID_ACTION] = (id_action + 1) % NUMBER_PLAYER
                if env_state[ENV_CHECK_END] >= 1:
                    if env_state[ENV_ID_ACTION] == env_state[ENV_ID_PLAYER_END]:
                        env_state[ENV_CHECK_END] += 0.5              #edit by Hieu 05012023
        #nếu nhặt thẻ từ chồng train_Car úp
        elif action == 156:
            new_train_car = int(env_state[ENV_TRAIN_CAR_CARD])
            # print('màu của thẻ úp được nhặt là ', LIST_COLOR[int(new_train_car)])
            env_state[ENV_IN4_PLAYER + ATTRIBUTE_PLAYER * id_action : ENV_IN4_PLAYER + ATTRIBUTE_PLAYER* (id_action + 1)][new_train_car + 2] += 1
            env_state[ENV_TRAIN_CAR_CARD : ENV_IN4_PLAYER] = np.concatenate((env_state[ENV_TRAIN_CAR_CARD : ENV_IN4_PLAYER][1:], np.array([-1])))
            env_state[ENV_NUMBER_TRAIN_CAR_GET] += 1
            #xáo thẻ drop nếu chồng bài úp hết bài
            if env_state[ENV_TRAIN_CAR_CARD] == -1 and np.sum(env_state[ENV_TRAIN_CAR_DROP : ENV_CARD_BULD_TUNNEL]):
                env_state = shuffle_drop_card(env_state)
            #nếu đã nhặt đủ 2 thẻ
            if env_state[ENV_NUMBER_TRAIN_CAR_GET] == 2:
                #reset số thẻ đã nhặt, cập nhật người chơi mơi
                env_state[ENV_NUMBER_TRAIN_CAR_GET] = 0
                env_state[ENV_ID_ACTION] = (id_action + 1) % NUMBER_PLAYER
                if env_state[ENV_CHECK_END] >= 1:
                    if env_state[ENV_ID_ACTION] == env_state[ENV_ID_PLAYER_END]:
                        env_state[ENV_CHECK_END] += 0.5              #edit by Hieu 05012023
        #nếu nhặt thẻ routecard thì cập nhật rồi sang phase 3
        elif action == 169:
            route_card_get = env_state[ENV_ROUTE_CARD_BOARD : ENV_ROUTE_CARD_BOARD + NUMBER_ROUTE_GET]
            route_card_get = route_card_get[route_card_get > -1].astype(np.int64)
            env_state[ENV_ROUTE_CARD_GET : ENV_TRAIN_CAR_DROP][route_card_get] = 1
            env_state[ENV_ROUTE_CARD_BOARD : ENV_TRAIN_CAR_CARD] = np.concatenate((env_state[ENV_ROUTE_CARD_BOARD : ENV_TRAIN_CAR_CARD][NUMBER_ROUTE_GET:], np.array([-1]*NUMBER_ROUTE_GET)))
            env_state[ENV_PHASE] = 3
            if len(route_card_get) == 3:
                env_state[ENV_NUMBER_DROP_ROUTE_CARD] = 0
            else:
                env_state[ENV_NUMBER_DROP_ROUTE_CARD] = 2
        #nếu ko action được gì khác thì skip
        else:
            #action == 171
            #skip qua người chơi
            env_state[ENV_NUMBER_TRAIN_CAR_GET] = 0
            env_state[ENV_ID_ACTION] = (id_action + 1) % NUMBER_PLAYER
            if env_state[ENV_CHECK_END] >= 1:
                if env_state[ENV_ID_ACTION] == env_state[ENV_ID_PLAYER_END]:
                    env_state[ENV_CHECK_END] += 0.5              #edit by Hieu 05012023

    elif phase_game == 2:
        type_train_car_use = action - 157
        road = int(env_state[ENV_ROAD_BUILT])
        type_road = LIST_ALL_TYPE_ROAD[road]
        player_train_car = env_state[ENV_IN4_PLAYER + ATTRIBUTE_PLAYER * id_action : ENV_IN4_PLAYER + ATTRIBUTE_PLAYER* (id_action + 1)][2 : 2 + NUMBER_TYPE_TRAIN_CAR_CARD]
        #nếu xây road thường
        if type_road == 0:
            if player_train_car[type_train_car_use] >= LIST_ALL_LENGTH_ROAD[road]:
                #bỏ thẻ vào chồng bài drop
                env_state[ENV_TRAIN_CAR_DROP : ENV_CARD_BULD_TUNNEL][type_train_car_use] += LIST_ALL_LENGTH_ROAD[road]
                #đủ train_Car nên chỉ trừ train_Car
                env_state[ENV_IN4_PLAYER + ATTRIBUTE_PLAYER * id_action : ENV_IN4_PLAYER + ATTRIBUTE_PLAYER* (id_action + 1)][2 : 2 + NUMBER_TYPE_TRAIN_CAR_CARD][type_train_car_use] -= LIST_ALL_LENGTH_ROAD[road]
            else:
                #nếu k đủ traincar thì tối thiểu việc dùng locomotive
                locomotive_use = LIST_ALL_LENGTH_ROAD[road] - player_train_car[type_train_car_use]
                #bỏ thẻ vào chồng bài drop
                env_state[ENV_TRAIN_CAR_DROP : ENV_CARD_BULD_TUNNEL][type_train_car_use] += env_state[ENV_IN4_PLAYER + ATTRIBUTE_PLAYER * id_action : ENV_IN4_PLAYER + ATTRIBUTE_PLAYER* (id_action + 1)][2 : 2 + NUMBER_TYPE_TRAIN_CAR_CARD][type_train_car_use]
                env_state[ENV_TRAIN_CAR_DROP : ENV_CARD_BULD_TUNNEL][type_train_car_use - type_train_car_use] += locomotive_use
                #trừ tài nguyên người chơi
                env_state[ENV_IN4_PLAYER + ATTRIBUTE_PLAYER * id_action : ENV_IN4_PLAYER + ATTRIBUTE_PLAYER* (id_action + 1)][2 : 2 + NUMBER_TYPE_TRAIN_CAR_CARD][type_train_car_use - type_train_car_use] -= locomotive_use
                env_state[ENV_IN4_PLAYER + ATTRIBUTE_PLAYER * id_action : ENV_IN4_PLAYER + ATTRIBUTE_PLAYER* (id_action + 1)][2 : 2 + NUMBER_TYPE_TRAIN_CAR_CARD][type_train_car_use] = 0
                
            #cộng điểm cho người chơi, trừ số tàu của người chơi           
            env_state[ENV_IN4_PLAYER + ATTRIBUTE_PLAYER * id_action : ENV_IN4_PLAYER + ATTRIBUTE_PLAYER* (id_action + 1)][0] += LIST_SCORE_BUILD_ROAD[LIST_ALL_LENGTH_ROAD[int(env_state[ENV_ROAD_BUILT])]]
            env_state[ENV_IN4_PLAYER + ATTRIBUTE_PLAYER * id_action : ENV_IN4_PLAYER + ATTRIBUTE_PLAYER* (id_action + 1)][1] -= LIST_ALL_LENGTH_ROAD[int(env_state[ENV_ROAD_BUILT])]
            if env_state[ENV_IN4_PLAYER + ATTRIBUTE_PLAYER * id_action : ENV_IN4_PLAYER + ATTRIBUTE_PLAYER* (id_action + 1)][1] <= 2 and env_state[ENV_CHECK_END] == 0:
                env_state[ENV_CHECK_END] = 1
                env_state[ENV_ID_PLAYER_END] = (id_action + 1) % NUMBER_PLAYER
            #update đường của người chơi
            env_state[road] = id_action
            env_state[ENV_ROAD_BUILT] = -1
            env_state[ENV_TYPE_TRAIN_CAR_BUILD_ROAD : ENV_TYPE_TRAIN_CAR_BUILD_ROAD + NUMBER_TYPE_TRAIN_CAR_CARD] = 0
            env_state[ENV_PHASE] = 1
            env_state[ENV_ID_ACTION] = (id_action + 1) % NUMBER_PLAYER
            if env_state[ENV_CHECK_END] >= 1:
                if env_state[ENV_ID_ACTION] == env_state[ENV_ID_PLAYER_END]:
                    env_state[ENV_CHECK_END] += 0.5              #edit by Hieu 05012023
            if env_state[ENV_TRAIN_CAR_CARD] == -1 and np.sum(env_state[ENV_TRAIN_CAR_DROP : ENV_CARD_BULD_TUNNEL]) > 0:
                env_state = shuffle_drop_card(env_state)
        #nếu xây ferry
        elif type_road == 2:
            temp_train_car = player_train_car.copy()
            temp_train_car[1:] +=  temp_train_car[0]
            locomotive_need_use = LIST_ROAD_LOCOMOTIVES[road]
            #player_train_car
            if player_train_car[type_train_car_use] >= LIST_ALL_LENGTH_ROAD[road]:
                #nếu đủ train_Car thì chỉ trừ train_Car
                env_state[ENV_IN4_PLAYER + ATTRIBUTE_PLAYER * id_action : ENV_IN4_PLAYER + ATTRIBUTE_PLAYER* (id_action + 1)][2 : 2 + NUMBER_TYPE_TRAIN_CAR_CARD][type_train_car_use - type_train_car_use] -= locomotive_need_use
                env_state[ENV_IN4_PLAYER + ATTRIBUTE_PLAYER * id_action : ENV_IN4_PLAYER + ATTRIBUTE_PLAYER* (id_action + 1)][2 : 2 + NUMBER_TYPE_TRAIN_CAR_CARD][type_train_car_use] -= LIST_ALL_LENGTH_ROAD[road] - locomotive_need_use
                env_state[ENV_TRAIN_CAR_DROP : ENV_CARD_BULD_TUNNEL][type_train_car_use - type_train_car_use] += locomotive_need_use
                env_state[ENV_TRAIN_CAR_DROP : ENV_CARD_BULD_TUNNEL][type_train_car_use] += LIST_ALL_LENGTH_ROAD[road] - locomotive_need_use

            else:
                locomotive_need_use += LIST_ALL_LENGTH_ROAD[road] - locomotive_need_use - player_train_car[type_train_car_use]
                env_state[ENV_IN4_PLAYER + ATTRIBUTE_PLAYER * id_action : ENV_IN4_PLAYER + ATTRIBUTE_PLAYER* (id_action + 1)][2 : 2 + NUMBER_TYPE_TRAIN_CAR_CARD][type_train_car_use - type_train_car_use] -= locomotive_need_use
                env_state[ENV_IN4_PLAYER + ATTRIBUTE_PLAYER * id_action : ENV_IN4_PLAYER + ATTRIBUTE_PLAYER* (id_action + 1)][2 : 2 + NUMBER_TYPE_TRAIN_CAR_CARD][type_train_car_use] -= LIST_ALL_LENGTH_ROAD[road] - locomotive_need_use
                env_state[ENV_TRAIN_CAR_DROP : ENV_CARD_BULD_TUNNEL][type_train_car_use - type_train_car_use] += locomotive_need_use
                env_state[ENV_TRAIN_CAR_DROP : ENV_CARD_BULD_TUNNEL][type_train_car_use] += LIST_ALL_LENGTH_ROAD[road] - locomotive_need_use
            env_state[ENV_IN4_PLAYER + ATTRIBUTE_PLAYER * id_action : ENV_IN4_PLAYER + ATTRIBUTE_PLAYER* (id_action + 1)][0] += LIST_SCORE_BUILD_ROAD[LIST_ALL_LENGTH_ROAD[int(env_state[ENV_ROAD_BUILT])]]
            env_state[ENV_IN4_PLAYER + ATTRIBUTE_PLAYER * id_action : ENV_IN4_PLAYER + ATTRIBUTE_PLAYER* (id_action + 1)][1] -= LIST_ALL_LENGTH_ROAD[int(env_state[ENV_ROAD_BUILT])]
            if env_state[ENV_IN4_PLAYER + ATTRIBUTE_PLAYER * id_action : ENV_IN4_PLAYER + ATTRIBUTE_PLAYER* (id_action + 1)][1] <= 2:
                env_state[ENV_CHECK_END] = 1
                env_state[ENV_ID_PLAYER_END] = (id_action + 1) % NUMBER_PLAYER
            #update đường của người chơi
            env_state[road] = id_action
            env_state[ENV_ROAD_BUILT] = -1
            env_state[ENV_TYPE_TRAIN_CAR_BUILD_ROAD : ENV_TYPE_TRAIN_CAR_BUILD_ROAD + NUMBER_TYPE_TRAIN_CAR_CARD] = 0
            env_state[ENV_PHASE] = 1
            env_state[ENV_ID_ACTION] = (id_action + 1) % NUMBER_PLAYER
            if env_state[ENV_CHECK_END] >= 1:
                if env_state[ENV_ID_ACTION] == env_state[ENV_ID_PLAYER_END]:
                    env_state[ENV_CHECK_END] += 0.5              #edit by Hieu 05012023
            if env_state[ENV_TRAIN_CAR_CARD] == -1 and np.sum(env_state[ENV_TRAIN_CAR_DROP : ENV_CARD_BULD_TUNNEL]) > 0:
                env_state = shuffle_drop_card(env_state)
        #nếu xây tunnel
        else:
            if player_train_car[type_train_car_use] >= LIST_ALL_LENGTH_ROAD[road]:
                #bỏ thẻ vào chồng bài build_tunnel
                env_state[ENV_CARD_BULD_TUNNEL : ENV_CARD_TEST_TUNNEL][type_train_car_use] += LIST_ALL_LENGTH_ROAD[road]
                #nếu đủ train_Car thì chỉ trừ train_Car
                env_state[ENV_IN4_PLAYER + ATTRIBUTE_PLAYER * id_action : ENV_IN4_PLAYER + ATTRIBUTE_PLAYER* (id_action + 1)][2 : 2 + NUMBER_TYPE_TRAIN_CAR_CARD][type_train_car_use] -= LIST_ALL_LENGTH_ROAD[road]
            else:
                #nếu k đủ traincar thì tối thiểu việc dùng locomotive
                locomotive_use = LIST_ALL_LENGTH_ROAD[road] - player_train_car[type_train_car_use]
                #bỏ thẻ vào chồng bài build_tunnel
                env_state[ENV_CARD_BULD_TUNNEL : ENV_CARD_TEST_TUNNEL][type_train_car_use] += env_state[ENV_IN4_PLAYER + ATTRIBUTE_PLAYER * id_action : ENV_IN4_PLAYER + ATTRIBUTE_PLAYER* (id_action + 1)][2 : 2 + NUMBER_TYPE_TRAIN_CAR_CARD][type_train_car_use]
                env_state[ENV_CARD_BULD_TUNNEL : ENV_CARD_TEST_TUNNEL][type_train_car_use - type_train_car_use] += locomotive_use
                #trừ tài nguyên người chơi
                env_state[ENV_IN4_PLAYER + ATTRIBUTE_PLAYER * id_action : ENV_IN4_PLAYER + ATTRIBUTE_PLAYER* (id_action + 1)][2 : 2 + NUMBER_TYPE_TRAIN_CAR_CARD][type_train_car_use - type_train_car_use] -= locomotive_use
                env_state[ENV_IN4_PLAYER + ATTRIBUTE_PLAYER * id_action : ENV_IN4_PLAYER + ATTRIBUTE_PLAYER* (id_action + 1)][2 : 2 + NUMBER_TYPE_TRAIN_CAR_CARD][type_train_car_use] = 0
            
            #đi lật bài để test tunnel
            if env_state[ENV_TRAIN_CAR_CARD + 3] == -1:
                env_state = shuffle_drop_card(env_state)
            car_test_tunnel = env_state[ENV_TRAIN_CAR_CARD : ENV_TRAIN_CAR_CARD + NUMBER_CARD_TEST_TUNNEL].astype(np.int64)
            for car in car_test_tunnel:
                env_state[ENV_CARD_TEST_TUNNEL + car] += 1
            #điều chỉnh chồng bài úp
            env_state[ENV_TRAIN_CAR_CARD : ENV_IN4_PLAYER] = np.concatenate((env_state[ENV_TRAIN_CAR_CARD : ENV_IN4_PLAYER][NUMBER_CARD_TEST_TUNNEL:], np.array([-1]*NUMBER_CARD_TEST_TUNNEL)))
            env_state[ENV_TYPE_TRAIN_CAR_BUILD_ROAD : ENV_TYPE_TRAIN_CAR_BUILD_ROAD + NUMBER_TYPE_TRAIN_CAR_CARD] = 0
            env_state[ENV_PHASE] = 4

    elif phase_game == 3:
        #nếu dừng bỏ thẻ:
        if action == 170:
            route_card_save = np.where(env_state[ENV_ROUTE_CARD_GET : ENV_TRAIN_CAR_DROP] == 1)[0]
            player_route_card = env_state[ENV_IN4_PLAYER + ATTRIBUTE_PLAYER * id_action : ENV_IN4_PLAYER + ATTRIBUTE_PLAYER * (id_action + 1)][11:]
            player_route_card[route_card_save] = 1
            env_state[ENV_IN4_PLAYER + ATTRIBUTE_PLAYER * id_action : ENV_IN4_PLAYER + ATTRIBUTE_PLAYER * (id_action + 1)][11:] = player_route_card
            env_state[ENV_ROUTE_CARD_GET : ENV_TRAIN_CAR_DROP] = 0
            env_state[ENV_NUMBER_DROP_ROUTE_CARD] = 0
            env_state[ENV_PHASE] = 1
            env_state[ENV_ID_ACTION] = (id_action + 1) % NUMBER_PLAYER
            if env_state[ENV_CHECK_END] >= 1:
                if env_state[ENV_ID_ACTION] == env_state[ENV_ID_PLAYER_END]:
                    env_state[ENV_CHECK_END] += 0.5              #edit by Hieu 05012023
            
            if env_state[ENV_TURN] <= NUMBER_PLAYER:
                env_state[ENV_TURN] += 1
            if env_state[ENV_TURN] <= NUMBER_PLAYER:
                id_action = int(env_state[ENV_ID_ACTION])
                env_state[ENV_ROUTE_CARD_GET : ENV_TRAIN_CAR_DROP] = env_state[ENV_IN4_PLAYER : ENV_TRAIN_CAR_OPEN][id_action * ATTRIBUTE_PLAYER : (id_action+1) * ATTRIBUTE_PLAYER][2 + NUMBER_TYPE_TRAIN_CAR_CARD : ]
                env_state[ENV_IN4_PLAYER : ENV_TRAIN_CAR_OPEN][id_action * ATTRIBUTE_PLAYER : (id_action+1) * ATTRIBUTE_PLAYER][2 + NUMBER_TYPE_TRAIN_CAR_CARD : ] = 0
                env_state[ENV_PHASE] = 3
        else:
            drop_card = action - 101
            #lưu thẻ mình đã bỏ nếu ko phải lượt bỏ thẻ ban đầu
            if env_state[ENV_TURN] > NUMBER_PLAYER:
                route_card_board = env_state[ENV_ROUTE_CARD_BOARD : ENV_TRAIN_CAR_CARD]
                route_insert = np.where(route_card_board == -1)[0][0]
                route_card_board[route_insert] = drop_card
                env_state[ENV_ROUTE_CARD_BOARD : ENV_TRAIN_CAR_CARD] = route_card_board
            env_state[ENV_IN4_PLAYER + ATTRIBUTE_PLAYER * id_action : ENV_IN4_PLAYER + ATTRIBUTE_PLAYER * (id_action + 1)][11:][drop_card] = -1
            env_state[ENV_ROUTE_CARD_GET : ENV_TRAIN_CAR_DROP][drop_card] = 0
            env_state[ENV_NUMBER_DROP_ROUTE_CARD] += 1
            #nếu ko được bỏ thẻ nữa
            if env_state[ENV_NUMBER_DROP_ROUTE_CARD] == 2:
                route_card_save = np.where(env_state[ENV_ROUTE_CARD_GET : ENV_TRAIN_CAR_DROP] == 1)[0]
                player_route_card = env_state[ENV_IN4_PLAYER + ATTRIBUTE_PLAYER * id_action : ENV_IN4_PLAYER + ATTRIBUTE_PLAYER * (id_action + 1)][11:]
                player_route_card[route_card_save] = 1
                env_state[ENV_IN4_PLAYER + ATTRIBUTE_PLAYER * id_action : ENV_IN4_PLAYER + ATTRIBUTE_PLAYER * (id_action + 1)][11:] = player_route_card
                env_state[ENV_ROUTE_CARD_GET : ENV_TRAIN_CAR_DROP] = 0
                env_state[ENV_NUMBER_DROP_ROUTE_CARD] = 0
                env_state[ENV_PHASE] = 1
                env_state[ENV_ID_ACTION] = (id_action + 1) % NUMBER_PLAYER

                if env_state[ENV_CHECK_END] >= 1:
                    if env_state[ENV_ID_ACTION] == env_state[ENV_ID_PLAYER_END]:
                        env_state[ENV_CHECK_END] += 0.5              #edit by Hieu 05012023
                # env_state[ENV_TURN] += 1
                if env_state[ENV_TURN] <= NUMBER_PLAYER:
                    env_state[ENV_TURN] += 1
                if env_state[ENV_TURN] <= NUMBER_PLAYER:
                    env_state[ENV_PHASE] = 3
                    id_action = int(env_state[ENV_ID_ACTION])
                    env_state[ENV_ROUTE_CARD_GET : ENV_TRAIN_CAR_DROP] = env_state[ENV_IN4_PLAYER : ENV_TRAIN_CAR_OPEN][id_action * ATTRIBUTE_PLAYER : (id_action+1) * ATTRIBUTE_PLAYER][2 + NUMBER_TYPE_TRAIN_CAR_CARD : ]
                    env_state[ENV_IN4_PLAYER : ENV_TRAIN_CAR_OPEN][id_action * ATTRIBUTE_PLAYER : (id_action+1) * ATTRIBUTE_PLAYER][2 + NUMBER_TYPE_TRAIN_CAR_CARD : ] = 0

    elif phase_game == 4:
        train_car_return = env_state[ENV_CARD_BULD_TUNNEL : ENV_CARD_TEST_TUNNEL]
        test_train_car = env_state[ENV_CARD_TEST_TUNNEL : ENV_PHASE]
        if action == 168:       #không xây hầm
            #trả tài nguyên cho người chơi đã bỏ ra để định xây hầm, nạp các thẻ test xây hầm vào chồng bài úp
            env_state[ENV_IN4_PLAYER + ATTRIBUTE_PLAYER * id_action : ENV_IN4_PLAYER + ATTRIBUTE_PLAYER * (id_action + 1)][2 : 2 + NUMBER_TYPE_TRAIN_CAR_CARD] += train_car_return
            env_state[ENV_TRAIN_CAR_DROP : ENV_CARD_BULD_TUNNEL] += test_train_car

        elif action == 167:     #có xây hầm
            #kiểm tra xem trùng loại thẻ nào, trừ loại thẻ đấy rồi cho hết lá bài vào drop
            temp = train_car_return * test_train_car
            subtract_car = (temp >= 1) * test_train_car
            #trừ tài nguyên nếu trùng vs tài nguyên test tunnel
            train_car_player = env_state[ENV_IN4_PLAYER + ATTRIBUTE_PLAYER * id_action : ENV_IN4_PLAYER + ATTRIBUTE_PLAYER * (id_action + 1)][2 : 2 + NUMBER_TYPE_TRAIN_CAR_CARD]
            train_car_player -= subtract_car
            for type_train_car in range(1, NUMBER_TYPE_TRAIN_CAR_CARD):
                if train_car_player[type_train_car] < 0:
                    train_car_player[0] += train_car_player[type_train_car]
                    train_car_player[type_train_car] = 0
            env_state[ENV_IN4_PLAYER + ATTRIBUTE_PLAYER * id_action : ENV_IN4_PLAYER + ATTRIBUTE_PLAYER * (id_action + 1)][2 : 2 + NUMBER_TYPE_TRAIN_CAR_CARD] = train_car_player
            env_state[ENV_TRAIN_CAR_DROP : ENV_CARD_BULD_TUNNEL] += test_train_car + train_car_return + subtract_car
            #cộng điểm cho người chơi
            env_state[ENV_IN4_PLAYER + ATTRIBUTE_PLAYER * id_action : ENV_IN4_PLAYER + ATTRIBUTE_PLAYER* (id_action + 1)][0] += LIST_SCORE_BUILD_ROAD[LIST_ALL_LENGTH_ROAD[int(env_state[ENV_ROAD_BUILT])]]
            env_state[ENV_IN4_PLAYER + ATTRIBUTE_PLAYER * id_action : ENV_IN4_PLAYER + ATTRIBUTE_PLAYER* (id_action + 1)][1] -= LIST_ALL_LENGTH_ROAD[int(env_state[ENV_ROAD_BUILT])]
            if env_state[ENV_IN4_PLAYER + ATTRIBUTE_PLAYER * id_action : ENV_IN4_PLAYER + ATTRIBUTE_PLAYER* (id_action + 1)][1] <= 2 and env_state[ENV_CHECK_END] == 0:
                env_state[ENV_CHECK_END] = 1
                env_state[ENV_ID_PLAYER_END] = (id_action + 1) % NUMBER_PLAYER
            #ghi nhận đường cho người chơi:
            env_state[int(env_state[ENV_ROAD_BUILT])] = id_action
        #update phase, chuyển người chơi
        env_state[ENV_PHASE] = 1
        env_state[ENV_CARD_BULD_TUNNEL : ENV_PHASE] = 0
        env_state[ENV_ID_ACTION] = (id_action + 1) % NUMBER_PLAYER
        if env_state[ENV_CHECK_END] >= 1:
                if env_state[ENV_ID_ACTION] == env_state[ENV_ID_PLAYER_END]:
                    env_state[ENV_CHECK_END] += 0.5              #edit by Hieu 05012023
        if env_state[ENV_TRAIN_CAR_CARD] == -1 and np.sum(env_state[ENV_TRAIN_CAR_DROP : ENV_CARD_BULD_TUNNEL]) > 0:
                env_state = shuffle_drop_card(env_state)

    return env_state

#########################################################

@nb.njit()
def numba_one_game(p_lst_idx_shuffle, p0, p1, p2, p3, p4, per_file):
    env_state = initEnv()
    count_turn = 0
    while system_check_end(env_state) and count_turn < 7000:
        count_turn += 1
        p_idx = int(env_state[ENV_ID_ACTION])
        p_state = getAgentState(env_state)
        if p_lst_idx_shuffle[p_idx] == 0:
            action, per_file = p0(p_state, per_file)
        elif p_lst_idx_shuffle[p_idx] == 1:
            action, per_file = p1(p_state, per_file)
        elif p_lst_idx_shuffle[p_idx] == 2:
            action, per_file = p2(p_state, per_file)
        elif p_lst_idx_shuffle[p_idx] == 3:
            action, per_file = p3(p_state, per_file)
        else:
            action, per_file = p4(p_state, per_file)
        if getValidActions(p_state)[action] != 1:
            raise Exception('bot dua ra action khong hop le')
        env_state = stepEnv(env_state, action)
    winner, env_state = check_winner(env_state)
    for current_player in range(NUMBER_PLAYER):
        env_state[ENV_PHASE] = 1
        env_state[ENV_ID_ACTION] = current_player
        p_idx = int(env_state[ENV_ID_ACTION])
        p_state = getAgentState(env_state)
        if p_lst_idx_shuffle[p_idx] == 0:
            action, per_file = p0(p_state, per_file)
        elif p_lst_idx_shuffle[p_idx] == 1:
            action, per_file = p1(p_state, per_file)
        elif p_lst_idx_shuffle[p_idx] == 2:
            action, per_file = p2(p_state, per_file)
        elif p_lst_idx_shuffle[p_idx] == 3:
            action, per_file = p3(p_state, per_file)
        else:
            action, per_file = p4(p_state, per_file)
    return winner, per_file

#########################################################

@nb.njit()
def numba_main(p0, p1, p2, p3, p4, num_game,per_file):
    num_won = np.array([0,0,0,0,0,0])
    p_lst_idx = np.array([0,1,2,3,4])
    for _n in range(num_game):
        np.random.shuffle(p_lst_idx)
        winner, per_file = numba_one_game(p_lst_idx, p0, p1, p2, p3, p4, per_file )
        num_won[p_lst_idx[winner]] += 1

    return num_won, per_file

#########################################################

@nb.njit()
def random_Env(p_state, per):
    arr_action = getValidActions(p_state)
    arr_action = np.where(arr_action == 1)[0]
    act_idx = np.random.randint(0, len(arr_action))
    return arr_action[act_idx], per

#########################################################

@nb.jit()
def one_game_numba(p0, list_other, per_player, per1, per2, per3, per4, p1, p2, p3, p4):
    env_state = initEnv()
    count_turn = 0

    while system_check_end(env_state) and count_turn < 7000:
        count_turn += 1
        p_idx = int(env_state[ENV_ID_ACTION])
        p_state = getAgentState(env_state)

        if list_other[p_idx] == -1:
            action, per_player = p0(p_state, per_player)
        elif list_other[p_idx] == 1:
            action, per1 = p1(p_state, per1)
        elif list_other[p_idx] == 2:
            action, per2 = p2(p_state, per2)
        elif list_other[p_idx] == 3:
            action, per3 = p3(p_state, per3)
        else:
            action, per4 = p4(p_state, per4)
        if getValidActions(p_state)[action] != 1:
            raise Exception('bot dua ra action khong hop le')
        env_state = stepEnv(env_state, action)
    winner, env_state = check_winner(env_state)
    for current_player in range(NUMBER_PLAYER):
        env_state[ENV_PHASE] = 1
        env_state[ENV_ID_ACTION] = current_player
        p_idx = int(env_state[ENV_ID_ACTION])
        p_state = getAgentState(env_state)

        if list_other[p_idx] == -1:
            action, per_player = p0(p_state, per_player)
        elif list_other[p_idx] == 1:
            action, per1 = p1(p_state, per1)
        elif list_other[p_idx] == 2:
            action, per2 = p2(p_state, per2)
        elif list_other[p_idx] == 3:
            action, per3 = p3(p_state, per3)
        else:
            action, per4 = p4(p_state, per4)
    if np.where(list_other == -1)[0][0] in  winner:
        winner = True
    else: 
        winner = False
    return winner,  per_player

 

@nb.jit()
def n_game_numba(p0, num_game, per_player, list_other, per1, per2, per3, per4, p1, p2, p3, p4):
    win = 0
    for _n in range(num_game):
        np.random.shuffle(list_other)
        winner,per_player  = one_game_numba(p0, list_other, per_player, per1, per2, per3, per4, p1, p2, p3, p4)
        win += winner
    return win, per_player


import importlib.util, json, sys
# from setup import SHOT_PATH
SHOT_PATH = ''

def load_module_player(player):
    return  importlib.util.spec_from_file_location('Agent_player', f"{SHOT_PATH}Agent/{player}/Agent_player.py").loader.load_module()

def numba_main_2(p0, n_game, per_player, level):
    list_other = np.array([1, 2, 3, 4, -1])
    if level == 0:
        per_agent_env = np.array([0])
        return n_game_numba(p0, n_game, per_player, list_other, per_agent_env, per_agent_env, per_agent_env, per_agent_env, random_Env, random_Env, random_Env, random_Env)
    else:
        env_name = sys.argv[1]
        dict_level = json.load(open(f'{SHOT_PATH}Log/level_game.json'))

        if str(level) not in dict_level[env_name]:
            raise Exception('Hiện tại không có level này') 
        lst_agent_level = dict_level[env_name][str(level)][2]

        p1 = load_module_player(lst_agent_level[0]).Test
        p2 = load_module_player(lst_agent_level[1]).Test
        p3 = load_module_player(lst_agent_level[2]).Test
        p4 = load_module_player(lst_agent_level[4]).Test

        per_level = []
        for id in range(getAgentSize()-1):
            data_agent_env = list(np.load(f'{SHOT_PATH}Agent/{lst_agent_level[id]}/Data/{env_name}_{level}/Train.npy',allow_pickle=True))
            per_level.append(data_agent_env)
        
        return n_game_numba(p0, n_game, per_player, list_other, per_level[0], per_level[1], per_level[2], per_level[3], p1, p2, p3, p4)
































# @nb.njit()
# def n_game_numba(p0, num_game, per_player, list_other, per1, per2, per3, p1, p2, p3):
#     win = 0
#     for _n in range(num_game):
#         np.random.shuffle(list_other)
#         winner,per_player  = one_game_numba(p0, list_other, per_player, per1, per2, per3, p1, p2, p3)
#         win += winner
#     return win, per_player

# def numba_main_2(p0, n_game, per_player, level):
#     list_other = np.array([1, 2, 3, -1])
#     if level == 0:
#         per_agent_env = np.array([0])
#         return n_game_numba(p0, n_game, per_player, list_other, per_agent_env, per_agent_env, per_agent_env, random_Env, random_Env, random_Env)
#     else:
#         env_name = sys.argv[1]
#         dict_level = json.load(open(f'{SHOT_PATH}Log/level_game.json'))

#         if str(level) not in dict_level[env_name]:
#             raise Exception('Hiện tại không có level này') 
#         lst_agent_level = dict_level[env_name][str(level)][2]

#         p1 = load_module_player(lst_agent_level[0]).Agent
#         p2 = load_module_player(lst_agent_level[1]).Agent
#         p3 = load_module_player(lst_agent_level[2]).Agent
#         per_level = []
#         for id in range(getAgentSize()):
#             data_agent_env = list(np.load(f'{SHOT_PATH}Agent/{lst_agent_level[0]}/Data/{env_name}_{level}/Train.npy',allow_pickle=True))
#             per_level.append(data_agent_env)
        
#         return n_game_numba(p0, n_game, per_player, list_other, per_level[0], per_level[1], per_level[2], p1, p2, p3)




