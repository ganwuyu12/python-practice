#include <iostream>
#include <cstring>
#include <unistd.h>
#include <vector>
#include <algorithm>
#include <sys/socket.h>
#include <sys/epoll.h>
#include <netinet/in.h>
#include <arpa/inet.h>

using namespace std;

#define PORT 9527
#define MAX_EVENTS 1024

vector<int> g_clients;  // 不再需要锁，因为只有主线程访问

int main() {
    // 1. 创建 socket、bind、listen（和原来完全一样）
    int lfd = socket(AF_INET, SOCK_STREAM, 0);
    if (lfd == -1) { perror("socket"); return 1; }

    // 设置端口复用，防止重启时端口被占用
    int opt = 1;
    setsockopt(lfd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_port = htons(PORT);
    addr.sin_addr.s_addr = INADDR_ANY;

    if (bind(lfd, (sockaddr*)&addr, sizeof(addr)) == -1) { perror("bind"); return 1; }
    if (listen(lfd, 128) == -1) { perror("listen"); return 1; }

    cout << "epoll 聊天室启动，端口 " << PORT << endl;

    // 2. 创建 epoll 实例
    int epfd = epoll_create(1);
    if (epfd == -1) { perror("epoll_create"); return 1; }

    // 3. 把 lfd 加入 epoll 监听
    struct epoll_event ev;
    ev.events = EPOLLIN;
    ev.data.fd = lfd;
    if (epoll_ctl(epfd, EPOLL_CTL_ADD, lfd, &ev) == -1) {
        perror("epoll_ctl: lfd");
        return 1;
    }

    // 4. 事件数组
    struct epoll_event events[MAX_EVENTS];

    // 5. 主循环（核心替换）
    while (true) {
        int n = epoll_wait(epfd, events, MAX_EVENTS, -1);
        if (n == -1) { perror("epoll_wait"); break; }

        for (int i = 0; i < n; ++i) {
            int fd = events[i].data.fd;

            if (fd == lfd) {
                // 新客户端连接
                int cfd = accept(lfd, nullptr, nullptr);
                if (cfd == -1) { perror("accept"); continue; }

                // 加入在线列表
                g_clients.push_back(cfd);
                cout << "新用户加入，当前在线人数: " << g_clients.size() << endl;

                // 把 cfd 也加入 epoll 监听
                ev.events = EPOLLIN;
                ev.data.fd = cfd;
                epoll_ctl(epfd, EPOLL_CTL_ADD, cfd, &ev);
            } else {
                // 客户端发来数据
                char buf[1024];
                int ret = read(fd, buf, sizeof(buf));

                if (ret <= 0) {
                    // 客户端断开
                    cout << "用户断开" << endl;
                    close(fd);
                    epoll_ctl(epfd, EPOLL_CTL_DEL, fd, nullptr);
                    g_clients.erase(remove(g_clients.begin(), g_clients.end(), fd), g_clients.end());
                    cout << "当前在线人数: " << g_clients.size() << endl;
                } else {
                    // 广播给所有其他客户端
                    for (int client_fd : g_clients) {
                        if (client_fd != fd) {
                            write(client_fd, buf, ret);
                        }
                    }
                }
            }
        }
    }

    close(lfd);
    close(epfd);
    return 0;
}
