#include <iostream>
#include <cstring>
#include <unistd.h>
#include <vector>
#include <queue>
#include <cmath>
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

struct Player {
    int fd;
    int score;
    time_t enter_time;  // 进入队列的时间，用于超时处理
};

vector<int> g_clients;
queue<Player> g_match_queue;

// 广播匹配结果给客户端
void send_match_result(int fd, bool success, int room_id = 0) {
    json resp;
    if (success) {
        resp["cmd"] = "match_success";
        resp["room_id"] = room_id;
    } else {
        resp["cmd"] = "match_fail";
        resp["reason"] = "timeout";
    }
    string msg = resp.dump() + "\n";
    write(fd, msg.c_str(), msg.size());
}

// 检查并配对
void try_match() {
    while (g_match_queue.size() >= 2) {
        Player a = g_match_queue.front();
        g_match_queue.pop();
        Player b = g_match_queue.front();
        g_match_queue.pop();

        if (abs(a.score - b.score) <= SCORE_RANGE) {
            // 配对成功
            static int room_id = 1001;
            cout << "配对成功: " << a.fd << "(" << a.score << ") <-> " 
                 << b.fd << "(" << b.score << "), 房间号: " << room_id << endl;
            send_match_result(a.fd, true, room_id);
            send_match_result(b.fd, true, room_id);
            room_id++;
        } else {
            // 分数差距太大，重新排队等待
            g_match_queue.push(a);
            g_match_queue.push(b);
            break;
        }
    }
}

int main() {
    // 1. socket -> bind -> listen
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

    cout << "匹配服务器启动，端口 " << PORT << endl;

    // 2. epoll 初始化
    int epfd = epoll_create(1);
    if (epfd == -1) { perror("epoll_create"); return 1; }

    struct epoll_event ev, events[MAX_EVENTS];
    ev.events = EPOLLIN;
    ev.data.fd = lfd;
    epoll_ctl(epfd, EPOLL_CTL_ADD, lfd, &ev);

    // 3. 主循环
    while (true) {
        int n = epoll_wait(epfd, events, MAX_EVENTS, 1000);  // 1秒超时，用于定时检查
        
        // 处理超时匹配
        if (n == 0) {
            cout << "检查超时..." << endl;
            queue<Player> remaining;
            time_t now = time(nullptr);
            while (!g_match_queue.empty()) {
                Player p = g_match_queue.front();
                g_match_queue.pop();
                if (difftime(now, p.enter_time) >= TIMEOUT_SEC) {
                    cout << "玩家 " << p.fd << " 匹配超时" << endl;
                    send_match_result(p.fd, false);
                } else {
                    remaining.push(p);
                }
            }
            g_match_queue = remaining;
            continue;
        }

        if (n == -1) { perror("epoll_wait"); break; }

        for (int i = 0; i < n; ++i) {
            int fd = events[i].data.fd;

            if (fd == lfd) {
                // 新连接
                int cfd = accept(lfd, nullptr, nullptr);
                if (cfd == -1) { perror("accept"); continue; }
                g_clients.push_back(cfd);
                ev.events = EPOLLIN;
                ev.data.fd = cfd;
                epoll_ctl(epfd, EPOLL_CTL_ADD, cfd, &ev);
                cout << "新客户端连接: " << cfd << endl;
            } else {
                // 读数据
                char buf[1024] = {0};
                int ret = read(fd, buf, sizeof(buf) - 1);
                if (ret <= 0) {
                    cout << "客户端断开: " << fd << endl;
                    close(fd);
                    epoll_ctl(epfd, EPOLL_CTL_DEL, fd, nullptr);
                    // 从队列中移除
                    queue<Player> remaining;
                    while (!g_match_queue.empty()) {
                        Player p = g_match_queue.front();
                        g_match_queue.pop();
                        if (p.fd != fd) remaining.push(p);
                    }
                    g_match_queue = remaining;
                    continue;
                }

                string data(buf, ret);
                cout << "收到: " << data << endl;

                try {
                    json j = json::parse(data);
                    string cmd = j["cmd"];

                    if (cmd == "match") {
                        int score = j["score"];
                        Player p;
                        p.fd = fd;
                        p.score = score;
                        p.enter_time = time(nullptr);
                        g_match_queue.push(p);
                        cout << "玩家 " << fd << " 加入匹配队列，当前等待: " << g_match_queue.size() << endl;
                        try_match();  // 立刻尝试配对
                    } else {
                        write(fd, "未知命令\n", 10);
                    }
                } catch (const exception& e) {
                    string err = "JSON解析错误: " + string(e.what()) + "\n";
                    write(fd, err.c_str(), err.size());
                }
            }
        }
    }

    close(lfd);
    close(epfd);
    return 0;
}
