#include <iostream>
#include <cstring>
#include <unistd.h>
#include <thread>
#include <vector>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#define PORT 9527

void client_handler(int cfd) {
    char buf[1024];
    std::cout << "新线程开始，cfd = " << cfd << std::endl;
    
    while (true) {
        int ret = read(cfd, buf, sizeof(buf));
        if (ret <= 0) {
            std::cout << "客户端断开，cfd = " << cfd << std::endl;
            break;
        }
        
        // 转大写
        for (int i = 0; i < ret; i++) {
            buf[i] = toupper(buf[i]);
        }
        write(cfd, buf, ret);
    }
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
