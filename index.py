import numpy as np

NUMBER_PLAYER = 5
NUMBER_TRAIN_CAR_CARD_OPEN = 5      #số thẻ train_car được mở
NUMBER_TRAIN_CAR_GET = 4
NUMBER_ROUTE_GET = 3
NUMBER_CARD_TEST_TUNNEL = 3
NUMBER_ROUTE_RECEIVE = 4
NUMBER_ROAD = 101
NUMBER_CITY = 47
NUMBER_ROUTE = 46
NUMBER_TRAIN = 45
NUMBER_PHASE = 4        #edit 13h 4/1/2023
NUMBER_SPECIAL_ROUTE = 6
NUMBER_TYPE_TRAIN_CAR_CARD = 9
# NUMBER_ROUTE_ENV = NUMBER_ROUTE - NUMBER_SPECIAL_ROUTE - NUMBER_ROUTE_GET*NUMBER_PLAYER
NUMBER_TRAIN_CAR_CARD = 110     #tổng số thẻ train_car
ATTRIBUTE_PLAYER = 57       #(score, number_train, 9 vị trí cho số lượng thẻ traincar mỗi loại, 46 vị trí cho thẻ route đang có (0 là ko có, 1 là đang giữ, -1 là đã drop))

NUMBER_ACTIONS = 172
'''
ALL_PHASE
PHASE 0: chọn thẻ route được phát để drop
PHASE 1: bắt đầu lượt chơi(101 action xây đường, 1 action nhặt route card, 10 action nhặt train_car_card)
PHASE 2: chọn tài nguyên xây đường, hầm
PHASE 3: chọn thẻ route đã nhặt để drop
PHASE 4: chọn xây hầm hay không

ALL_ACTION
range(0,101): action xây đường
range(101, 147): action drop thẻ route
range(147, 157): action nhặt thẻ train_car
range(157, 167): action chọn loại train_car xây road
range(167, 169): action chọn xây tunnel hay không
range(169, 171): action nhặt thẻ route và dừng drop thẻ route
range(171, 172): action skip







'''










INDEX = 0
#các đường trên bản đồ
ENV_ROAD_BOARD = INDEX
INDEX += NUMBER_ROAD

#các thẻ tuyến đường bàn chơi
ENV_ROUTE_CARD_BOARD = INDEX
INDEX += NUMBER_ROUTE

#các thẻ train_card_trên bàn
ENV_TRAIN_CAR_CARD = INDEX
INDEX += NUMBER_TRAIN_CAR_CARD

#Thuộc tính các người chơi
ENV_IN4_PLAYER = INDEX
INDEX += ATTRIBUTE_PLAYER*NUMBER_PLAYER

#Train car card open
ENV_TRAIN_CAR_OPEN = INDEX
INDEX += NUMBER_TRAIN_CAR_CARD_OPEN

#route card get
ENV_ROUTE_CARD_GET = INDEX
INDEX += NUMBER_ROUTE

#train_card_drop
ENV_TRAIN_CAR_DROP = INDEX
INDEX += NUMBER_TYPE_TRAIN_CAR_CARD

#card_player_build_tunnel
ENV_CARD_BULD_TUNNEL = INDEX
INDEX += NUMBER_TYPE_TRAIN_CAR_CARD

#card_board_open_to_build_tunnel
ENV_CARD_TEST_TUNNEL = INDEX
INDEX += NUMBER_TYPE_TRAIN_CAR_CARD

#Other in4
ENV_PHASE = INDEX
INDEX += 1
ENV_ID_ACTION = INDEX
INDEX += 1
ENV_CHECK_END = INDEX
INDEX += 1
ENV_ID_PLAYER_END = INDEX
INDEX += 1
ENV_NUMBER_TRAIN_CAR_GET = INDEX
INDEX += 1
ENV_TYPE_TRAIN_CAR_BUILD_ROAD = INDEX
INDEX += NUMBER_TYPE_TRAIN_CAR_CARD
ENV_ROAD_BUILT = INDEX
INDEX += 1
ENV_NUMBER_DROP_ROUTE_CARD = INDEX
INDEX += 1
ENV_TURN = INDEX
INDEX += 1




ENV_LENGTH = INDEX



P_INDEX = 0
#điểm của 5 người chơi
P_SCORE = P_INDEX
P_INDEX += NUMBER_PLAYER
#thẻ traincar của người chơi
P_TRAIN_CAR_CARD = P_INDEX
P_INDEX += NUMBER_TYPE_TRAIN_CAR_CARD
#đường từng người chơi sở hữu
P_PLAYER_ROAD = P_INDEX
P_INDEX += NUMBER_ROAD*NUMBER_PLAYER
#thẻ route của người chơi
P_ROUTE_CARD = P_INDEX
P_INDEX += NUMBER_ROUTE
#thẻ route ngươi chơi lấy trong turn (3) hoặc nhận ban đầu (4)
P_ROUTE_GET = P_INDEX
P_INDEX += NUMBER_ROUTE
#thẻ train_car trên bàn chơi
P_TRAIN_CAR_CARD_BOARD = P_INDEX
P_INDEX += NUMBER_TYPE_TRAIN_CAR_CARD
#thẻ người chơi dùng xây tunnel
P_CARD_BULD_TUNNEL = P_INDEX
P_INDEX += NUMBER_TYPE_TRAIN_CAR_CARD
#thẻ board lật ra để test tunnel
P_CARD_TEST_TUNNEL = P_INDEX
P_INDEX += NUMBER_TYPE_TRAIN_CAR_CARD
#các cách xây đường có thể
P_TYPE_TRAIN_CAR_BUILD_ROAD = P_INDEX
P_INDEX += NUMBER_TYPE_TRAIN_CAR_CARD

#other in4
P_ID_ACTION = P_INDEX
P_INDEX += 1
P_PHASE = P_INDEX
P_INDEX += NUMBER_PHASE             #edit 13h 4/1/2023
P_CHECK_ROUTE_CARD = P_INDEX
P_INDEX += 1
P_NUMBER_DROP_ROUTE_CARD = P_INDEX
P_INDEX += 1
P_CHEKC_END = P_INDEX
P_INDEX += 1
P_ID_PLAYER_END = P_INDEX
P_INDEX += NUMBER_PLAYER            #edit 13h 4/1/2023
P_NUMBER_TRAIN_CAR_GET = P_INDEX
P_INDEX += 1
P_ACTION_GET_TRAIN_CAR_DOWN = P_INDEX
P_INDEX += 1
P_NUMBER_TRAIN = P_INDEX
P_INDEX += 1

P_LENGTH = P_INDEX












#mỗi con đường ứng với 1 action khi xây đường
LIST_ALL_ACTION_BUILD_ROAD = np.arange(NUMBER_ROAD + 1)

#điểm số cho độ dài từng đoạn đường tương ứng
LIST_SCORE_BUILD_ROAD = np.array([0, 1, 2, 4, 7, 0, 15, 0, 21])

#màu của các đường
LIST_ALL_COLOR_ROAD = np.array([ 3,  1,  5,  4,  2,  6, -1, -1,  7,  3,  8,  1,  6,  5,  1, -1, -1,
                                8,  4,  7,  6, -1,  6,  5,  6, -1,  7,  5, -1, -1, -1, -1,  2, -1,
                                8, -1, -1,  5,  2,  7, -1, -1, -1,  4,  7,  8,  3, -1, -1, -1, -1,
                                -1,  3,  4, -1, -1, -1,  6,  4,  2, -1, -1, -1, -1,  1,  4,  3,  7,
                                2,  5,  1, -1,  1,  7,  8, -1, -1,  2,  6, -1, -1,  6,  7,  8,  4,
                                8,  3,  2,  3,  2,  5,  1,  4,  3,  5, -1, -1,  8,  1, -1, -1])
#độ dài mỗi con đường
LIST_ALL_LENGTH_ROAD = np.array([2, 3, 3, 2, 3, 3, 2, 4, 4, 4, 4, 4, 3, 2, 1, 2, 2, 2, 2, 2, 1, 2,
                                4, 4, 3, 4, 3, 3, 2, 2, 2, 4, 4, 4, 2, 4, 4, 2, 4, 3, 2, 4, 6, 3,
                                3, 4, 4, 4, 8, 2, 6, 2, 3, 3, 2, 4, 4, 3, 3, 3, 3, 3, 4, 2, 4, 4,
                                4, 1, 1, 2, 3, 2, 3, 3, 4, 4, 3, 2, 2, 4, 4, 3, 3, 3, 3, 2, 2, 2,
                                2, 3, 3, 2, 2, 2, 3, 2, 2, 2, 2, 3, 4])

LIST_ALL_TYPE_ROAD = np.array([0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 0, 0, 0, 2,
                                0, 0, 0, 2, 1, 1, 1, 2, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0,
                                0, 0, 0, 0, 1, 1, 2, 2, 0, 0, 1, 1, 0, 0, 0, 0, 2, 2, 0, 0, 0, 0,
                                0, 0, 0, 0, 0, 1, 0, 0, 0, 2, 2, 0, 0, 1, 2, 0, 0, 0, 0, 0, 0, 0,
                                0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 1, 1, 0])

LIST_ALL_ROAD_POINT = np.array([[21, 10], [21, 23], [10, 23], [23,  3], [23, 28], [23, 28], [ 3, 28], [ 3, 24], [28, 24], [28, 29],
                                [28, 29], [28,  5], [ 5, 29], [ 5, 13], [13, 29], [13, 22], [13, 22], [13,  7], [ 7, 29], [ 7, 29],
                                [ 7,  0], [ 0, 22], [22, 14], [22, 14], [15,  1], [15, 35], [15, 38], [ 1, 37], [ 1, 11], [38, 35],
                                [38, 33], [35, 11], [35,  8], [33, 35], [33, 18], [18, 25], [18, 20], [25, 36], [25, 30], [20, 36],
                                [20, 44], [20, 42], [20,  9], [44, 36], [44, 42], [44, 31], [44, 30], [31, 30], [40, 30], [37, 11],
                                [37, 27], [37,  2], [11, 39], [11,  8], [ 8, 39], [ 8,  9], [ 8, 20], [31, 12], [40, 19], [40, 19],
                                [19, 16], [19, 16], [12,  4], [12, 42], [42,  4], [42,  4], [42, 43], [43,  9], [43,  9], [ 9, 45],
                                [ 9, 34], [34, 39], [39,  2], [34, 45], [34,  2], [ 2,  6], [27,  6],[32,  6], [32, 41], [32, 24],
                                [32, 27], [ 4, 17], [ 4, 17], [ 4, 43], [16,  0], [16, 17], [16,  4], [ 0, 17], [17,  7], [17, 29],
                                [17, 29], [17, 26], [26, 46], [26, 41], [26, 43], [45, 43], [45, 41], [46, 41], [46, 24], [46, 29],
                                [29, 24]])

LIST_ALL_ROAD_TEXT = np.array(['Lisboa-Cadiz', 'Lisboa-Madrid', 'Cadiz-Madrid',
                        'Madrid-Barcelona', 'Madrid-Pamplona', 'Madrid-Pamplona',
                        'Barcelona-Pamplona', 'Barcelona-Marseille', 'Pamplona-Marseille',
                        'Pamplona-Paris', 'Pamplona-Paris', 'Pamplona-Brest',
                        'Brest-Paris', 'Brest-Dieppe', 'Dieppe-Paris', 'Dieppe-London',
                        'Dieppe-London', 'Dieppe-Bruxelles', 'Bruxelles-Paris',
                        'Bruxelles-Paris', 'Bruxelles-Amsterdam', 'Amsterdam-London',
                        'London-Edinburgh', 'London-Edinburgh', 'Erzurum-Angora',
                        'Erzurum-Sevastopol', 'Erzurum-Sochi', 'Angora-Smyrna',
                        'Angora-Constantinople', 'Sochi-Sevastopol', 'Sochi-Rostov',
                        'Sevastopol-Constantinople', 'Sevastopol-Bucuresti',
                        'Rostov-Sevastopol', 'Rostov-Kharkov', 'Kharkov-Moskva',
                        'Kharkov-Kyiv', 'Moskva-Smolensk', 'Moskva-Petrograd',
                        'Kyiv-Smolensk', 'Kyiv-Wilno', 'Kyiv-Warszawa', 'Kyiv-Budapest',
                        'Wilno-Smolensk', 'Wilno-Warszawa', 'Wilno-Riga',
                        'Wilno-Petrograd', 'Riga-Petrograd', 'Stockholm-Petrograd',
                        'Smyrna-Constantinople', 'Smyrna-Palermo', 'Smyrna-Athina',
                        'Constantinople-Sofia', 'Constantinople-Bucuresti',
                        'Bucuresti-Sofia', 'Bucuresti-Budapest', 'Bucuresti-Kyiv',
                        'Riga-Danzig', 'Stockholm-Kobenhavn', 'Stockholm-Kobenhavn',
                        'Kobenhavn-Essen', 'Kobenhavn-Essen', 'Danzig-Berlin',
                        'Danzig-Warszawa', 'Warszawa-Berlin', 'Warszawa-Berlin',
                        'Warszawa-Wien', 'Wien-Budapest', 'Wien-Budapest',
                        'Budapest-Zagrab', 'Budapest-Sarajevo', 'Sarajevo-Sofia',
                        'Sofia-Athina', 'Sarajevo-Zagrab', 'Sarajevo-Athina',
                        'Athina-Brindisi', 'Palermo-Brindisi', 'Roma-Brindisi',
                        'Roma-Venezia', 'Roma-Marseille', 'Roma-Palermo',
                        'Berlin-Frankfurt', 'Berlin-Frankfurt', 'Berlin-Wien',
                        'Essen-Amsterdam', 'Essen-Frankfurt', 'Essen-Berlin',
                        'Amsterdam-Frankfurt', 'Frankfurt-Bruxelles', 'Frankfurt-Paris',
                        'Frankfurt-Paris', 'Frankfurt-Munchen', 'Munchen-Zurich',
                        'Munchen-Venezia', 'Munchen-Wien', 'Zagrab-Wien', 'Zagrab-Venezia',
                        'Zurich-Venezia', 'Zurich-Marseille', 'Zurich-Paris',
                        'Paris-Marseille'])

LIST_ALL_POINT_TEXT = np.array(['Amsterdam', 'Angora', 'Athina', 'Barcelona', 'Berlin', 'Brest',
                        'Brindisi', 'Bruxelles', 'Bucuresti', 'Budapest', 'Cadiz',
                        'Constantinople', 'Danzig', 'Dieppe', 'Edinburgh', 'Erzurum',
                        'Essen', 'Frankfurt', 'Kharkov', 'Kobenhavn', 'Kyiv', 'Lisboa',
                        'London', 'Madrid', 'Marseille', 'Moskva', 'Munchen', 'Palermo',
                        'Pamplona', 'Paris', 'Petrograd', 'Riga', 'Roma', 'Rostov',
                        'Sarajevo', 'Sevastopol', 'Smolensk', 'Smyrna', 'Sochi', 'Sofia',
                        'Stockholm', 'Venezia', 'Warszawa', 'Wien', 'Wilno', 'Zagrab',
                        'Zurich'])

LIST_ALL_ROUTE_TEXT = np.array(['Athina-Angora', 'Budapest-Sofia', 'Frankfurt-Kobenhavn',
                        'Rostov-Erzurum', 'Sofia-Smyrna', 'Kyiv-Petrograd',
                        'Zurich-Brindisi', 'Zurich-Budapest', 'Warszawa-Smolensk',
                        'Zagrab-Brindisi', 'Paris-Zagrab', 'Brest-Marseille',
                        'London-Berlin', 'Edinburgh-Paris', 'Amsterdam-Pamplona',
                        'Roma-Smyrna', 'Palermo-Constantinople', 'Sarajevo-Sevastopol',
                        'Madrid-Dieppe', 'Barcelona-Bruxelles', 'Paris-Wien',
                        'Barcelona-Munchen', 'Brest-Venezia', 'Smolensk-Rostov',
                        'Marseille-Essen', 'Kyiv-Sochi', 'Madrid-Zurich',
                        'Berlin-Bucuresti', 'Bruxelles-Danzig', 'Berlin-Roma',
                        'Angora-Kharkov', 'Riga-Bucuresti', 'Essen-Kyiv',
                        'Venezia-Constantinople', 'London-Wien', 'Athina-Wilno',
                        'Stockholm-Wien', 'Berlin-Moskva', 'Amsterdam-Wilno',
                        'Frankfurt-Smolensk', 'Lisboa-Danzig', 'Brest-Petrograd',
                        'Palermo-Moskva', 'Kobenhavn-Erzurum', 'Edinburgh-Athina',
                        'Cadiz-Stockholm'])

LIST_ALL_ROUTE_POINT = np.array([[ 2,  1],[ 9, 39],[17, 19],[33, 15],
                                [39, 37],[20, 30],[46,  6],[46,  9],
                                [42, 36],[45,  6],[29, 45],[ 5, 24],
                                [22,  4],[14, 29],[ 0, 28],[32, 37],
                                [27, 11],[34, 35],[23, 13],[ 3,  7],
                                [29, 43],[ 3, 26],[ 5, 41],[36, 33],                                
                                [24, 16],[20, 38],[23, 46],[ 4,  8],
                                [ 7, 12],[ 4, 32],[ 1, 18],[31,  8],
                                [16, 20],[41, 11],[22, 43],[ 2, 44],
                                [40, 43],[ 4, 25],[ 0, 44],[17, 36],
                                [21, 12],[ 5, 30],[27, 25],[19, 15],
                                [14,  2],[10, 40]])


LIST_ALL_SCORE_ROUTE = np.array([ 5,  5,  5,  5,  5,  6,  6,  6,  6,  6,  7,  7,  7,  7,  7,  8,  8,
                                8,  8,  8,  8,  8,  8,  8,  8,  8,  8,  8,  9,  9, 10, 10, 10, 10,
                                10, 11, 11, 12, 12, 13, 20, 20, 20, 21, 21, 21])


LIST_CIRCLE = np.array([ 4,  5,  9, 10, 15, 16, 18, 19, 22, 23, 58, 
                        59, 60, 61, 64, 65, 67, 68, 81, 82, 89, 90])

                      
LIST_EDGE_SYMETRY = np.array([-1, -1, -1, -1,  5,  4, -1, -1, -1, 10,  9, -1, -1, -1, -1, 16, 15,
                                -1, 19, 18, -1, -1, 23, 22, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
                                -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
                                -1, -1, -1, -1, -1, -1, -1, 59, 58, 61, 60, -1, -1, 65, 64, -1, 68,
                                67, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 82, 81, -1, -1,
                                -1, -1, -1, -1, 90, 89, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1])

LIST_ROAD_LOCOMOTIVES = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 2,
                                    0, 0, 0, 2, 0, 0, 0, 1, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                    0, 0, 0, 0, 0, 0, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0,
                                    0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0,
                                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

POINT_ROAD_RELATIVE = np.array([[20, 21, 84, 87, -1, -1, -1, -1, -1, -1],
                                [24, 27, 28, -1, -1, -1, -1, -1, -1, -1],
                                [51, 72, 74, 75, -1, -1, -1, -1, -1, -1],
                                [3, 6, 7, -1, -1, -1, -1, -1, -1, -1],
                                [62, 64, 65, 81, 82, 83, 86, -1, -1, -1],
                                [11, 12, 13, -1, -1, -1, -1, -1, -1, -1],
                                [75, 76, 77, -1, -1, -1, -1, -1, -1, -1],
                                [17, 18, 19, 20, 88, -1, -1, -1, -1, -1],
                                [32, 53, 54, 55, 56, -1, -1, -1, -1, -1],
                                [42, 55, 67, 68, 69, 70, -1, -1, -1, -1],
                                [0, 2, -1, -1, -1, -1, -1, -1, -1, -1],
                                [28, 31, 49, 52, 53, -1, -1, -1, -1, -1],
                                [57, 62, 63, -1, -1, -1, -1, -1, -1, -1],
                                [13, 14, 15, 16, 17, -1, -1, -1, -1, -1],
                                [22, 23, -1, -1, -1, -1, -1, -1, -1, -1],
                                [24, 25, 26, -1, -1, -1, -1, -1, -1, -1],
                                [60, 61, 84, 85, 86, -1, -1, -1, -1, -1],
                                [81, 82, 85, 87, 88, 89, 90, 91, -1, -1],
                                [34, 35, 36, -1, -1, -1, -1, -1, -1, -1],
                                [58, 59, 60, 61, -1, -1, -1, -1, -1, -1],
                                [36, 39, 40, 41, 42, 56, -1, -1, -1, -1],
                                [0, 1, -1, -1, -1, -1, -1, -1, -1, -1],
                                [15, 16, 21, 22, 23, -1, -1, -1, -1, -1],
                                [1, 2, 3, 4, 5, -1, -1, -1, -1, -1],
                                [7, 8, 79, 98, 100, -1, -1, -1, -1, -1],
                                [35, 37, 38, -1, -1, -1, -1, -1, -1, -1],
                                [91, 92, 93, 94, -1, -1, -1, -1, -1, -1],
                                [50, 76, 80, -1, -1, -1, -1, -1, -1, -1],
                                [4, 5, 6, 8, 9, 10, 11, -1, -1, -1],
                                [9, 10, 12, 14, 18, 19, 89, 90, 99, 100],
                                [38, 46, 47, 48, -1, -1, -1, -1, -1, -1],
                                [45, 47, 57, -1, -1, -1, -1, -1, -1, -1],
                                [77, 78, 79, 80, -1, -1, -1, -1, -1, -1],
                                [30, 33, 34, -1, -1, -1, -1, -1, -1, -1],
                                [70, 71, 73, 74, -1, -1, -1, -1, -1, -1],
                                [25, 29, 31, 32, 33, -1, -1, -1, -1, -1],
                                [37, 39, 43, -1, -1, -1, -1, -1, -1, -1],
                                [27, 49, 50, 51, -1, -1, -1, -1, -1, -1],
                                [26, 29, 30, -1, -1, -1, -1, -1, -1, -1],
                                [52, 54, 71, 72, -1, -1, -1, -1, -1, -1],
                                [48, 58, 59, -1, -1, -1, -1, -1, -1, -1],
                                [78, 93, 96, 97, -1, -1, -1, -1, -1, -1],
                                [41, 44, 63, 64, 65, 66, -1, -1, -1, -1],
                                [66, 67, 68, 83, 94, 95, -1, -1, -1, -1],
                                [40, 43, 44, 45, 46, -1, -1, -1, -1, -1],
                                [69, 73, 95, 96, -1, -1, -1, -1, -1, -1],
                                [92, 97, 98, 99, -1, -1, -1, -1, -1, -1]])

LIST_COLOR = np.array(['Locomotive', 'Pink', 'White', 'Blue', 'Yellow', 'Orange', 'Black', 'Red', 'Green', 'Gray'])

'''
ferry luôn là đường màu xám, 
'''
