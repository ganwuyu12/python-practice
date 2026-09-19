#include <iostream>
#include <cstring>
#include <unistd.h>
#include <signal.h>
#include <sys/wait.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#define SERV_PORT 9527
#define BUFSIZE 1024

void sys_err(const char *str) {
    perror(str);
    exit(1);
}

// 信号捕捉函数：回收僵尸子进程
void sig_chld_handler(int signo) {
    // 非阻塞回收所有已退出的子进程
    while (waitpid(-1, NULL, WNOHANG) > 0);
}

// 子进程处理函数：服务一个客户端
void do_client(int cfd) {
    char buf[BUFSIZE];
    int ret;

    while (1) {
        ret = read(cfd, buf, sizeof(buf));
        if (ret <= 0) {
            std::cout << "客户端已断开" << std::endl;
            break;
        }

        // 转大写
        for (int i = 0; i < ret; ++i) {
            buf[i] = toupper(buf[i]);
        }

        write(cfd, buf, ret);
    }

    close(cfd);
}

int main() {
    int lfd, cfd;
    struct sockaddr_in serv_addr, clit_addr;
    socklen_t clit_addr_len;
    pid_t pid;

    // 1. 注册信号捕捉，防止子进程变僵尸
    signal(SIGCHLD, sig_chld_handler);

    // 2. 创建 socket
    lfd = socket(AF_INET, SOCK_STREAM, 0);
    if (lfd == -1) sys_err("socket error");

    // 3. 绑定地址
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(SERV_PORT);
    serv_addr.sin_addr.s_addr = htonl(INADDR_ANY);
    if (bind(lfd, (struct sockaddr*)&serv_addr, sizeof(serv_addr)) == -1) {
        sys_err("bind error");
    }

    // 4. 监听
    if (listen(lfd, 128) == -1) sys_err("listen error");
    std::cout << "多进程服务器启动成功，端口 " << SERV_PORT << std::endl;

    // 5. 循环 accept
    while (1) {
        clit_addr_len = sizeof(clit_addr);
        cfd = accept(lfd, (struct sockaddr*)&clit_addr, &clit_addr_len);
        if (cfd == -1) {
            sys_err("accept error");
        }

        std::cout << "新客户端连接上了！" << std::endl;

        // 6. 创建子进程
        pid = fork();
        if (pid == 0) {
            // 子进程：服务客户端
            close(lfd);                     // 子进程不需要监听 fd
            do_client(cfd);
            close(cfd);
            exit(0);                        // 子进程退出，触发 SIGCHLD
        } else if (pid > 0) {
            // 父进程：继续 accept
            close(cfd);                     // 父进程不需要通信 fd
        } else {
            sys_err("fork error");
        }
    }

    close(lfd);
    return 0;
}
