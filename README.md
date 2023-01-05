## :dart: Báo cáo Ticket To Ride 
1.   `Tốc độ chạy`
      - **1000 Game**: 19.3s
      - **1000 Game full numba**: 5.6
      - **10000 Game**: 202s

2. `Chuẩn form`: **Đã test**
3. `Đúng luật`: **Đã check**
4. `Không bị loop vô hạn`: **Đã test** với 1000000 ván
5. `Tốc độ chạy các hàm con mà người chơi dùng`: 1000game: 21.9s
6. `Số ván check_vic > victory_thật`: chạy 10000 ván thì check_victory = check_winner = 
7. `Giá trị state, action: 172 action, 
9. `Tối thiểu số lần truyền vào player`: 1000 ván ~105

## :globe_with_meridians: ENV_state
*   [0:101] **các đường trên bàn**: range(0,5) là của người chơi, chưa bị sở hữu là -1
*   [101:147] **mảng tạm đại diện thẻ route trên bàn chơi, vị trí nào không có thì là -1, số vị trí khác -1 là số thẻ route còn trên bàn**
*   [147:257] **Mảng tạm đại diện cho các thẻ train_car trên bàn chơi, vị trí không có là -1**, Các giá trị là range(0,9) và -1
*   [107 + 12 * p_id:119 + 12 * p_id] **thông tin của người chơi**, gồm có  6 nguyên liệu đang có, 5 nguyên liệu mặc định và điểm
*   [257:542] **THuộc tính của 5 người chơi** (ATTRIBUTE_PLAYER = 57       #(score, number_train, 9 vị trí cho số lượng thẻ traincar mỗi loại, 46 vị trí cho thẻ route đang có (0 là ko có, 1 là đang giữ, -1 là đã drop))
*   [542:547] **Các thẻ train_car lật trên bàn** cấp 1, 2, 3

*   [547:593] **Các thẻ route người chơi được bỏ trong lượt** thẻ nào có thì vị trí tương ứng là 1, không thì là 0
*   [593:602] **Số lượng từng loại thẻ train_car ở chồng bài bỏ**
*   [602:611]   **Số lượng từng loại thẻ người chơi bỏ ra xây hầm**
*   [611:620]  **Số lượng từng loại thẻ bàn chơi lật ra để thách người chơi xây hầm**
*   [620]   **phase của bàn chơi**
*   [621]   **index người chơi hành động**
*   [622]   **kiểm tra game sắp kết thúc chưa** nếu có người còn dưới 3 tàu thì có giá trị 1
*   [623]   **index người cuối cùng được hành động**
*   [624]   **số thẻ train_car người chơi đã lấy trong lượt**
*   [625:634]   **các loại train_car người chơi có thể dùng xây road**
*   [634]       **Con đường người chơi xây trong lượt**
*   [635]   **Số thẻ route người chơi đã bỏ trong lượt**
*   [636]   **turn của bàn chơi** dùng để xét ở đầu game khi những người chơi bỏ thẻ route
**Total env_state length: 637**
## :bust_in_silhouette: P_state
*   [0:5] là **điểm của các người chơi**
*   [5:14] **số lượng từng loại thẻ train_car của người chơi**
*   [14:519]:   **đường của 5 người chơi** mỗi người chơi có 101 vị trí ứng với 101 con đường, có đường nào thì vị trí đường đó có giá trị 1
*   [519:565]:   **thẻ route của người chơi** thẻ nào có thì vị trí tương ứng là 1, còn không thì là 0
*   [565:611]:  **thẻ route người chơi lấy trong turn** thẻ nào có thì vị trí tương ứng là 1, còn không thì là 0
*   [611:620]:   **số lượng thẻ train_car mở trên bàn chơi**
*   [620:629]:  **số lượng từng loại thẻ người chơi dùng xây hầm** trong phase lấy nguyên liệu
*   [629:638]: **thẻ bàn chơi bỏ ra để thách người chơi xây hầm**
*   [638:647]: **Các kiểu xây đường có thể**
*   [647]       **ID action (luôn = 0)**
*   [648:652]: phase của bàn chơi, vị trí ứng với các phase lần lượt là 0-1; 1-2; 2-3; 3-4
*   [652]: **Có lấy được thẻ tuyến đường hay không**
*   [653]: **số thẻ route đã bỏ trong lượt**
*   [654]: **game sắp kết thúc chưa**
*   [655:660]: **vị trí người chơi hành động cuối cùng**
*   [660]:  **số thẻ train_car đã lấy**
*   [661]:  **có láy được thẻ train_car úp không**
*   [662]:  **số tàu người chơi còn**
**Total: player state length = 663**

## :video_game: ALL_ACTION
* range(0,101): action xây đường
* range(101, 147): action drop thẻ route
* range(147, 157): action nhặt thẻ train_car
* range(157, 167): action chọn loại train_car xây road
* range(167, 169): action chọn xây tunnel hay không
* range(169, 171): action nhặt thẻ route và dừng drop thẻ route
* range(171, 172): action skip
**Total 172 action**