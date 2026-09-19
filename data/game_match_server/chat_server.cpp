#include <iostream>
#include <cstring>
#include <unistd.h>
#include <thread>
#include <vector>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <algorithm>
#include <pthread.h>

using namespace std;

#define PORT 9527

// 在线客户端列表
vector<int> g_clients;
pthread_mutex_t g_mutex = PTHREAD_MUTEX_INITIALIZER;

void client_handler(int cfd) {
    char buf[1024];
    
    // 加入在线列表（加锁保护）
    pthread_mutex_lock(&g_mutex);
    g_clients.push_back(cfd);
    pthread_mutex_unlock(&g_mutex);
    
    cout << "新用户加入，当前在线人数: " << g_clients.size() << endl;

    while (true) {
        int ret = read(cfd, buf, sizeof(buf));
        if (ret <= 0) {
            cout << "用户断开，cfd = " << cfd << endl;
            break;
        }

        // 广播消息给所有其他客户端（加锁保护）
        pthread_mutex_lock(&g_mutex);
        for (int fd : g_clients) {
            if (fd != cfd) {
                write(fd, buf, ret);
            }
        }
        pthread_mutex_unlock(&g_mutex);
    }

    // 离开：从列表中移除（加锁保护）
    pthread_mutex_lock(&g_mutex);
    g_clients.erase(remove(g_clients.begin(), g_clients.end(), cfd), g_clients.end());
    pthread_mutex_unlock(&g_mutex);
    
    close(cfd);
}
int main() {
    int lfd = socket(AF_INET, SOCK_STREAM, 0);
    if (lfd == -1) {
        perror("socket");
        return 1;
    }

    sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_port = htons(PORT);
    addr.sin_addr.s_addr = INADDR_ANY;

    if (bind(lfd, (sockaddr*)&addr, sizeof(addr)) == -1) {
        perror("bind");
        return 1;
    }

    if (listen(lfd, 128) == -1) {
        perror("listen");
        return 1;
    }

    std::cout << "多线程服务器启动，端口 " << PORT << std::endl;

    while (true) {
        int cfd = accept(lfd, nullptr, nullptr);
        if (cfd == -1) {
            perror("accept");
            continue;
        }
        std::cout << "新客户端连接，cfd = " << cfd << std::endl;

        // 创建线程，处理这个客户端
        std::thread t(client_handler, cfd);
        t.detach();  // 让线程独立运行
    }

    close(lfd);
    return 0;
}
