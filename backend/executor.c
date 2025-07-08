#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>
#include <string.h>
#include <fcntl.h>

// 函数声明
void execute_command(char *argv[], int is_background);
void execute_pipe_command(char *cmd1_argv[], char *cmd2_argv[]);
void execute_redirect_command(char *argv[], char *filename, int is_output_redirect, int is_background);

int main(int argc, char *argv[]) {
    // 如果只输入了程序名，没有其他参数，则直接成功退出
    if (argc < 2) {
        exit(EXIT_SUCCESS);
    }

    // 检查是否为后台任务
    int is_background = 0;
    if (argc > 1 && strcmp(argv[argc - 1], "&") == 0) {
        is_background = 1;
        argv[argc - 1] = NULL; // 从参数列表中移除'&'
        argc--; // 更新参数计数
    }

    int pipe_index = -1;
    int redirect_out_index = -1;
    int redirect_in_index = -1;

    // 查找特殊符号
    for (int i = 1; i < argc; i++) {
        if (argv[i] == NULL) continue;
        if (strcmp(argv[i], "|") == 0) { pipe_index = i; break; }
        if (strcmp(argv[i], ">") == 0) { redirect_out_index = i; break; }
        if (strcmp(argv[i], "<") == 0) { redirect_in_index = i; break; }
    }

    // 根据找到的符号执行不同的逻辑
    if (pipe_index != -1) {
        argv[pipe_index] = NULL;
        execute_pipe_command(&argv[1], &argv[pipe_index + 1]);
    } else if (redirect_out_index != -1) {
        char *filename = argv[redirect_out_index + 1];
        if (filename == NULL) { fprintf(stderr, "> 后面缺少文件名\n"); exit(EXIT_FAILURE); }
        argv[redirect_out_index] = NULL;
        execute_redirect_command(&argv[1], filename, 1, is_background); // 1 代表输出重定向
    } else if (redirect_in_index != -1) {
        char *filename = argv[redirect_in_index + 1];
        if (filename == NULL) { fprintf(stderr, "< 后面缺少文件名\n"); exit(EXIT_FAILURE); }
        argv[redirect_in_index] = NULL;
        execute_redirect_command(&argv[1], filename, 0, is_background); // 0 代表输入重定向
    } else {
        execute_command(&argv[1], is_background);
    }

    return 0;
}

// 执行单个命令（支持后台运行）
void execute_command(char *argv[], int is_background) {
    pid_t pid = fork();
    if (pid < 0) {
        perror("fork 失败");
        exit(EXIT_FAILURE);
    }
    if (pid == 0) { // 子进程
        execvp(argv[0], argv);
        perror("execvp 失败");
        exit(EXIT_FAILURE);
    } else { // 父进程
        if (!is_background) {
            waitpid(pid, NULL, 0); // 前台任务：等待子进程结束
        } else {
            printf("[%d] %d\n", 1, pid); // 后台任务：打印进程号并立即返回
        }
    }
}

// 执行管道命令
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
    if (pid1 == 0) {
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
    if (pid2 == 0) {
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

// 执行重定向命令（输入或输出）
void execute_redirect_command(char *argv[], char *filename, int is_output_redirect, int is_background) {
    pid_t pid = fork();
    if (pid < 0) {
        perror("fork 失败");
        exit(EXIT_FAILURE);
    }
    if (pid == 0) { // 子进程
        int fd;
        if (is_output_redirect) {
            // 输出重定向 >
            fd = open(filename, O_WRONLY | O_CREAT | O_TRUNC, 0644);
            if (fd < 0) { perror("open 输出文件失败"); exit(EXIT_FAILURE); }
            dup2(fd, STDOUT_FILENO);
        } else {
            // 输入重定向 <
            fd = open(filename, O_RDONLY);
            if (fd < 0) { perror("open 输入文件失败"); exit(EXIT_FAILURE); }
            dup2(fd, STDIN_FILENO);
        }
        close(fd);
        execvp(argv[0], argv);
        perror("execvp 失败");
        exit(EXIT_FAILURE);
    } else { // 父进程
        if (!is_background) {
            waitpid(pid, NULL, 0);
        } else {
            printf("[%d] %d\n", 1, pid);
        }
    }
}
