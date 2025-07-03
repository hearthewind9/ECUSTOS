// backend/executor.c (V3 - 支持管道和重定向的最终版)

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>
#include <string.h>
#include <fcntl.h> // 用于文件控制，如 open

// 函数声明
void execute_single_command(char *argv[]);
void execute_pipe_command(char *cmd1_argv[], char *cmd2_argv[]);
void execute_redirect_command(char *argv[], char *filename);

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "使用方法: %s <命令> [参数...]\n", argv[0]);
        exit(EXIT_FAILURE);
    }

    // --- 检查是否有重定向或管道 ---
    int pipe_index = -1;
    int redirect_index = -1;

    for (int i = 1; i < argc; i++) {
        if (argv[i] == NULL) continue;
        if (strcmp(argv[i], "|") == 0) {
            pipe_index = i;
            break; 
        }
        if (strcmp(argv[i], ">") == 0) {
            redirect_index = i;
            break;
        }
    }

    // 根据符号执行不同逻辑
    if (pipe_index != -1) {
        argv[pipe_index] = NULL;
        char **cmd1_argv = &argv[1];
        char **cmd2_argv = &argv[pipe_index + 1];
        if (cmd2_argv[0] == NULL) {
            fprintf(stderr, "管道 `|` 后面缺少命令\n");
            exit(EXIT_FAILURE);
        }
        execute_pipe_command(cmd1_argv, cmd2_argv);
    } else if (redirect_index != -1) {
        char *filename = argv[redirect_index + 1];
        if (filename == NULL) {
            fprintf(stderr, "重定向 `>` 后面缺少文件名\n");
            exit(EXIT_FAILURE);
        }
        argv[redirect_index] = NULL;
        execute_redirect_command(&argv[1], filename);
    } else {
        execute_single_command(&argv[1]);
    }

    return 0;
}

// 单命令执行函数 (传入的argv不包含程序名本身)
void execute_single_command(char *argv[]) {
    pid_t pid = fork();

    if (pid < 0) {
        perror("fork 失败");
        exit(EXIT_FAILURE);
    } else if (pid == 0) {
        execvp(argv[0], argv);
        perror("execvp 失败");
        exit(EXIT_FAILURE);
    } else {
        wait(NULL);
    }
}

// 管道命令执行函数
void execute_pipe_command(char *cmd1_argv[], char *cmd2_argv[]) {
    int pipefd[2];
    pid_t pid1, pid2;

    if (pipe(pipefd) < 0) {
        perror("pipe 创建失败");
        exit(EXIT_FAILURE);
    }

    pid1 = fork();
    if (pid1 < 0) {
        perror("fork 失败");
        exit(EXIT_FAILURE);
    }
    if (pid1 == 0) { // 第一个子进程
        dup2(pipefd[1], STDOUT_FILENO);
        close(pipefd[0]);
        close(pipefd[1]);
        execvp(cmd1_argv[0], cmd1_argv);
        perror("第一个命令 execvp 失败");
        exit(EXIT_FAILURE);
    }

    pid2 = fork();
    if (pid2 < 0) {
        perror("fork 失败");
        exit(EXIT_FAILURE);
    }
    if (pid2 == 0) { // 第二个子进程
        dup2(pipefd[0], STDIN_FILENO);
        close(pipefd[0]);
        close(pipefd[1]);
        execvp(cmd2_argv[0], cmd2_argv);
        perror("第二个命令 execvp 失败");
        exit(EXIT_FAILURE);
    }

    close(pipefd[0]);
    close(pipefd[1]);
    waitpid(pid1, NULL, 0);
    waitpid(pid2, NULL, 0);
}

// 输出重定向执行函数 (全新)
void execute_redirect_command(char *argv[], char *filename) {
    // O_WRONLY: 只写模式 | O_CREAT: 如果文件不存在则创建 | O_TRUNC: 如果文件已存在则清空内容
    // 0644 是文件权限：拥有者可读写，同组用户和其他用户只可读
    int fd = open(filename, O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (fd < 0) {
        perror("open 文件失败");
        exit(EXIT_FAILURE);
    }

    pid_t pid = fork();

    if (pid < 0) {
        perror("fork 失败");
        exit(EXIT_FAILURE);
    } else if (pid == 0) { // 子进程
        // 将标准输出重定向到文件描述符fd
        dup2(fd, STDOUT_FILENO);
        close(fd); // 关闭不再需要的文件描述符
        execvp(argv[0], argv);
        perror("execvp 失败");
        exit(EXIT_FAILURE);
    } else { // 父进程
        close(fd); // 父进程也需要关闭文件描述符
        wait(NULL);
    }
}