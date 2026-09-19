#include <iostream>
#include <cstring>
#include <unistd.h>
#include <vector>
#include <queue>
#include <map>
#include <cmath>
#include <ctime>
#include <algorithm>
#include <sys/socket.h>
#include <sys/epoll.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include "json.hpp"

using namespace std;
using json = nlohmann::json;

#define PORT 9527
#define MAX_EVENTS 1024
#define SCORE_RANGE 200
#define TIMEOUT_SEC 30
#define HEARTBEAT_SEC 15

// ========== 数据结构 ==========

struct Player {
    int fd;
    string name;
    int score;
    int rating;
    time_t enter_time;
    time_t last_heartbeat;
};

struct Room {
    int player1_fd;
    int player2_fd;
    string player1_name;
    string player2_name;
    int board[15][15];
    int current_player_fd;
    int player1_color;
    int player2_color;
    bool game_over;
    int winner;
    vector<string> chat_history;
};

// ========== 全局状态 ==========

vector<int> g_clients;
queue<Player> g_match_queue;
map<int, Room> g_rooms;
map<string, int> g_name_to_fd;
map<int, string> g_fd_to_name;
map<string, int> g_ratings;  // username -> rating
int g_next_room_id = 1001;
int g_next_player_id = 1;

// ========== 辅助函数 ==========

void send_json(int fd, const json& j) {
    string msg = j.dump() + "\n";
    write(fd, msg.c_str(), msg.size());
}

void broadcast_rank(int fd) {
    vector<pair<string, int>> ranked;
    for (auto& kv : g_ratings) {
        ranked.push_back({kv.first, kv.second});
    }
    sort(ranked.begin(), ranked.end(), [](auto& a, auto& b) {
        return a.second > b.second;
    });

    json resp;
    resp["cmd"] = "rank_list";
    for (int i = 0; i < min(10, (int)ranked.size()); i++) {
        json entry;
        entry["rank"] = i + 1;
        entry["name"] = ranked[i].first;
        entry["score"] = ranked[i].second;
        resp["list"].push_back(entry);
    }
    send_json(fd, resp);
}

bool check_win(int board[15][15], int row, int col, int player) {
    int directions[4][2] = {{1,0}, {0,1}, {1,1}, {1,-1}};
    for (auto& d : directions) {
        int count = 1;
        for (int step = 1; step < 5; ++step) {
            int r = row + d[0] * step;
            int c = col + d[1] * step;
            if (r < 0 || r >= 15 || c < 0 || c >= 15 || board[r][c] != player) break;
            count++;
        }
        for (int step = 1; step < 5; ++step) {
            int r = row - d[0] * step;
            int c = col - d[1] * step;
            if (r < 0 || r >= 15 || c < 0 || c >= 15 || board[r][c] != player) break;
            count++;
        }
        if (count >= 5) return true;
    }
    return false;
}

void try_match() {
    while (g_match_queue.size() >= 2) {
        Player a = g_match_queue.front();
        g_match_queue.pop();
        Player b = g_match_queue.front();
        g_match_queue.pop();

        if (abs(a.rating - b.rating) <= SCORE_RANGE || true) {
            Room room;
            memset(room.board, 0, sizeof(room.board));
            room.player1_fd = a.fd;
            room.player2_fd = b.fd;
            room.player1_name = a.name;
            room.player2_name = b.name;
            room.current_player_fd = a.fd;
            room.player1_color = 1;
            room.player2_color = 2;
            room.game_over = false;
            room.winner = 0;
            room.chat_history.clear();

            int room_id = g_next_room_id++;
            g_rooms[room_id] = room;

            cout << "配对成功: " << a.name << "(" << a.rating << ") <-> " 
                 << b.name << "(" << b.rating << "), 房间号: " << room_id << endl;

            json resp;
            resp["cmd"] = "match_success";
            resp["room_id"] = room_id;
            resp["color"] = "black";
            resp["name"] = a.name;
            resp["opponent"] = b.name;
            send_json(a.fd, resp);

            resp["color"] = "white";
            resp["name"] = b.name;
            resp["opponent"] = a.name;
            send_json(b.fd, resp);
        } else {
            g_match_queue.push(a);
            g_match_queue.push(b);
            break;
        }
    }
}

// ========== 主函数 ==========

int main() {
    int lfd = socket(AF_INET, SOCK_STREAM, 0);
    if (lfd == -1) { perror("socket"); return 1; }

    int opt = 1;
    setsockopt(lfd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_port = htons(PORT);
    addr.sin_addr.s_addr = INADDR_ANY;

    if (bind(lfd, (sockaddr*)&addr, sizeof(addr)) == -1) { perror("bind"); return 1; }
    if (listen(lfd, 128) == -1) { perror("listen"); return 1; }

    cout << "🎮 五子棋服务器启动，端口 " << PORT << endl;
    cout << "积分榜已启用，聊天功能已启用" << endl;

    int epfd = epoll_create(1);
    if (epfd == -1) { perror("epoll_create"); return 1; }

    struct epoll_event ev, events[MAX_EVENTS];
    ev.events = EPOLLIN;
    ev.data.fd = lfd;
    epoll_ctl(epfd, EPOLL_CTL_ADD, lfd, &ev);

    while (true) {
        int n = epoll_wait(epfd, events, MAX_EVENTS, 1000);

        if (n == 0) {
            time_t now = time(nullptr);
            queue<Player> remaining;
            while (!g_match_queue.empty()) {
                Player p = g_match_queue.front();
                g_match_queue.pop();
                if (difftime(now, p.last_heartbeat) >= HEARTBEAT_SEC) {
                    cout << "玩家 " << p.name << " 心跳超时" << endl;
                    close(p.fd);
                    continue;
                }
                if (difftime(now, p.enter_time) >= TIMEOUT_SEC) {
                    cout << "玩家 " << p.name << " 匹配超时" << endl;
                    json resp;
                    resp["cmd"] = "match_fail";
                    resp["reason"] = "timeout";
                    send_json(p.fd, resp);
                    continue;
                }
                remaining.push(p);
            }
            g_match_queue = remaining;
            continue;
        }

        if (n == -1) { perror("epoll_wait"); break; }

        for (int i = 0; i < n; ++i) {
            int fd = events[i].data.fd;

            if (fd == lfd) {
                int cfd = accept(lfd, nullptr, nullptr);
                if (cfd == -1) { perror("accept"); continue; }
                g_clients.push_back(cfd);
                ev.events = EPOLLIN;
                ev.data.fd = cfd;
                epoll_ctl(epfd, EPOLL_CTL_ADD, cfd, &ev);
                cout << "新客户端连接: " << cfd << endl;
            } else {
                char buf[4096] = {0};
                int ret = read(fd, buf, sizeof(buf) - 1);
                if (ret <= 0) {
                    cout << "客户端断开: " << fd << endl;
                    close(fd);
                    epoll_ctl(epfd, EPOLL_CTL_DEL, fd, nullptr);

                    string name = g_fd_to_name[fd];
                    g_name_to_fd.erase(name);
                    g_fd_to_name.erase(fd);

                    queue<Player> remaining;
                    while (!g_match_queue.empty()) {
                        Player p = g_match_queue.front();
                        g_match_queue.pop();
                        if (p.fd != fd) remaining.push(p);
                    }
                    g_match_queue = remaining;

                    for (auto& kv : g_rooms) {
                        Room& room = kv.second;
                        if (room.player1_fd == fd || room.player2_fd == fd) {
                            room.game_over = true;
                            int winner_fd = (room.player1_fd == fd) ? room.player2_fd : room.player1_fd;
                            send_json(winner_fd, {{"cmd", "opponent_quit"}});
                        }
                    }
                    continue;
                }

                string data(buf, ret);
                cout << "收到: " << data << endl;

                try {
                    json j = json::parse(data);
                    string cmd = j["cmd"];

                    if (cmd == "login") {
                        string name = j["name"];
                        if (g_name_to_fd.find(name) != g_name_to_fd.end()) {
                            send_json(fd, {{"cmd", "login_fail"}, {"reason", "用户名已存在"}});
                            continue;
                        }
                        g_name_to_fd[name] = fd;
                        g_fd_to_name[fd] = name;
                        if (g_ratings.find(name) == g_ratings.end()) {
                            g_ratings[name] = 1000;
                        }
                        send_json(fd, {{"cmd", "login_ok"}, {"name", name}, {"rating", g_ratings[name]}});
                        cout << "用户登录: " << name << " (" << fd << ")" << endl;

                    } else if (cmd == "match") {
                        string name = g_fd_to_name[fd];
                        if (name.empty()) {
                            send_json(fd, {{"cmd", "error"}, {"msg", "请先登录"}});
                            continue;
                        }
                        Player p;
                        p.fd = fd;
                        p.name = name;
                        p.rating = g_ratings[name];
                        p.enter_time = time(nullptr);
                        p.last_heartbeat = time(nullptr);
                        g_match_queue.push(p);
                        cout << "玩家 " << name << " 加入匹配，当前等待: " << g_match_queue.size() << endl;
                        try_match();

                    } else if (cmd == "move") {
                        int row = j["row"];
                        int col = j["col"];
                        int room_id = -1;
                        int player_type = 0;

                        for (auto& kv : g_rooms) {
                            Room& room = kv.second;
                            if (room.player1_fd == fd) {
                                room_id = kv.first;
                                player_type = 1;
                                break;
                            } else if (room.player2_fd == fd) {
                                room_id = kv.first;
                                player_type = 2;
                                break;
                            }
                        }

                        if (room_id == -1) {
                            send_json(fd, {{"cmd", "error"}, {"msg", "不在房间中"}});
                            continue;
                        }

                        Room& room = g_rooms[room_id];
                        if (room.game_over) {
                            send_json(fd, {{"cmd", "error"}, {"msg", "游戏已结束"}});
                            continue;
                        }
                        if (room.current_player_fd != fd) {
                            send_json(fd, {{"cmd", "error"}, {"msg", "还没轮到你"}});
                            continue;
                        }
                        if (row < 0 || row >= 15 || col < 0 || col >= 15 || room.board[row][col] != 0) {
                            send_json(fd, {{"cmd", "error"}, {"msg", "位置无效"}});
                            continue;
                        }

                        room.board[row][col] = player_type;
                        int opponent_fd = (player_type == 1) ? room.player2_fd : room.player1_fd;

                        bool win = check_win(room.board, row, col, player_type);
                        if (win) {
                            room.game_over = true;
                            room.winner = player_type;
                            string winner_name = (player_type == 1) ? "black" : "white";

                            string p1_name = g_fd_to_name[room.player1_fd];
                            string p2_name = g_fd_to_name[room.player2_fd];
                            if (player_type == 1) {
                                g_ratings[p1_name] += 10;
                                g_ratings[p2_name] -= 5;
                            } else {
                                g_ratings[p2_name] += 10;
                                g_ratings[p1_name] -= 5;
                            }

                            json resp;
                            resp["cmd"] = "game_over";
                            resp["winner"] = winner_name;
                            resp["row"] = row;
                            resp["col"] = col;
                            send_json(fd, resp);
                            send_json(opponent_fd, resp);
                            cout << "游戏结束，胜者: " << winner_name << endl;
                            continue;
                        }

                        json resp;
                        resp["cmd"] = "move_ok";
                        resp["row"] = row;
                        resp["col"] = col;
                        resp["player"] = player_type;
                        send_json(fd, resp);

                        json resp2;
                        resp2["cmd"] = "opponent_move";
                        resp2["row"] = row;
                        resp2["col"] = col;
                        resp2["player"] = player_type;
                        send_json(opponent_fd, resp2);

                        room.current_player_fd = opponent_fd;

                    } else if (cmd == "chat") {
                        string msg = j["msg"];
                        int room_id = -1;
                        for (auto& kv : g_rooms) {
                            Room& room = kv.second;
                            if (room.player1_fd == fd || room.player2_fd == fd) {
                                room_id = kv.first;
                                break;
                            }
                        }
                        if (room_id != -1) {
                            Room& room = g_rooms[room_id];
                            string name = g_fd_to_name[fd];
                            string chat_msg = name + ": " + msg;
                            json resp;
                            resp["cmd"] = "chat_msg";
                            resp["msg"] = chat_msg;
                            send_json(room.player1_fd, resp);
                            send_json(room.player2_fd, resp);
                        }

                    } else if (cmd == "rank") {
                        broadcast_rank(fd);

                    } else {
                        send_json(fd, {{"cmd", "error"}, {"msg", "未知命令: " + cmd}});
                    }

                } catch (const exception& e) {
                    send_json(fd, {{"cmd", "error"}, {"msg", string("JSON解析错误: ") + e.what()}});
                }
            }
        }
    }

    close(lfd);
    close(epfd);
    return 0;
}
