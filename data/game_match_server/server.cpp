#include <iostream>
#include <cstring>
#include <cctype>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#define SERV_PORT 9527

void sys_err(const char *str) {
    perror(str);
    exit(1);
}

int main() {
    int lfd, cfd;
    struct sockaddr_in serv_addr, clit_addr;
    socklen_t clit_addr_len;
    char buf[1024];
    int ret;

    lfd = socket(AF_INET, SOCK_STREAM, 0);
    if (lfd == -1) {
        sys_err("socket error");
    }

    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(SERV_PORT);
    serv_addr.sin_addr.s_addr = htonl(INADDR_ANY);
    if (bind(lfd, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) == -1) {
        sys_err("bind error");
    }

    if (listen(lfd, 128) == -1) {
        sys_err("listen error");
    }
    std::cout << "服务器启动成功，监听端口 " << SERV_PORT << std::endl;

    clit_addr_len = sizeof(clit_addr);
    cfd = accept(lfd, (struct sockaddr *)&clit_addr, &clit_addr_len);
    if (cfd == -1) {
        sys_err("accept error");
    }
    std::cout << "有客户端连接上了！" << std::endl;

    while (true) {
        ret = read(cfd, buf, sizeof(buf));
        if (ret <= 0) {
            std::cout << "客户端已断开" << std::endl;
            break;
        }

        write(STDOUT_FILENO, buf, ret);

        for (int i = 0; i < ret; ++i) {
            buf[i] = std::toupper(buf[i]);
        }

        write(cfd, buf, ret);
    }

    close(cfd);
    close(lfd);
    return 0;
}
