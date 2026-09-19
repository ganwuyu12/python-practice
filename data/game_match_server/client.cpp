#include <iostream>
#include <cstring>
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
	int cfd;
	struct sockaddr_in serv_addr;

	cfd = socket(AF_INET, SOCK_STREAM, 0);
	if (cfd == -1) {
		sys_err("socket error");
	}

	serv_addr.sin_family = AF_INET;
	serv_addr.sin_port = htons(SERV_PORT);

	inet_pton(AF_INET, "127.0.0.1", &serv_addr.sin_addr);

	if(connect(cfd, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) == -1) {
		sys_err("connect error");
	}
	std::cout << "连接服务器成功" << std::endl;

	for (int i = 0; i < 10; ++i) {
		int ret = write(cfd, "hello\n", 6);
		if (ret == -1) {
			sys_err("write error");
		}
		std::cout << "第" << i+1 << " 次发送: hello" << std::endl;
		sleep(1);
	}

	close(cfd);
	std::cout << "客户端退出" << std::endl;
	return 0;
}
