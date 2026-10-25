#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <signal.h>
#include <grp.h>
#include <errno.h>
#include <sys/io.h>
#include <sys/mount.h>
#include <sys/reboot.h>
#include <sys/resource.h>
#include <sys/types.h>
#include <sys/utsname.h>
#include <sys/wait.h>

static volatile sig_atomic_t child = -1, expired = 0;
static void watchdog(int s) {
    (void)s; expired = 1;
    if (child > 0) kill(child, SIGKILL);
}
static void cap(int resource, rlim_t n) {
    struct rlimit r = {n, n};
    if (setrlimit(resource, &r)) _exit(122);
}
int main(void) {
    int console = open("/dev/console", O_RDWR);
    if (console >= 0) { dup2(console, 0); dup2(console, 1); dup2(console, 2); }
    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stderr, NULL, _IONBF, 0);
    mount("proc", "/proc", "proc", 0, NULL);
    struct utsname u;
    if (uname(&u)) return 120;
    printf("__ECPP_KERNEL__ %s %s\n", u.release, u.machine);
    printf("__ECPP_INIT_ABI__ %u %u %u\n", (unsigned)sizeof(int),
           (unsigned)sizeof(long), (unsigned)sizeof(void *));
    char *args[64] = {0}, *line = NULL; size_t len = 0; int argc = 0;
    FILE *f = fopen("/argv", "r");
    if (!f) return 121;
    while (argc < 63 && getline(&line, &len, f) > 0) {
        size_t n = 0; while (line[n] && line[n] != '\n') ++n;
        line[n] = 0; args[argc++] = line; line = NULL; len = 0;
    }
    fclose(f);
    unsigned seconds = 30;
    f = fopen("/cpu_limit", "r");
    if (f) { if (fscanf(f, "%u", &seconds) != 1) return 121; fclose(f); }
    if (!argc || seconds < 1 || seconds > 3600) return 121;
    puts("__ECPP_GUEST_BEGIN__");
    signal(SIGALRM, watchdog);
    child = fork();
    if (child < 0) return 123;
    if (!child) {
        int fd = open("/stdin", O_RDONLY);
        if (fd < 0 || dup2(fd, 0) < 0) _exit(124);
        close(fd);
        cap(RLIMIT_AS, 128UL * 1024 * 1024); cap(RLIMIT_CORE, 0);
        cap(RLIMIT_NPROC, 16); cap(RLIMIT_NOFILE, 64); cap(RLIMIT_CPU, seconds);
        if (setgroups(0, NULL) || setgid(65534) || setuid(65534)) _exit(125);
        execv(args[0], args); perror("execv"); _exit(126);
    }
    alarm(seconds);
    int status; pid_t got;
    do { got = waitpid(child, &status, 0); } while (got < 0 && errno == EINTR);
    alarm(0);
    if (got != child) return 127;
    int code = WIFEXITED(status) ? WEXITSTATUS(status) : 128 + WTERMSIG(status);
    printf("\n__ECPP_CHILD_EXIT__ %d timeout=%d\n", code, (int)expired);
    f = fopen("/tmp/certificate", "rb");
    if (f) {
        puts("__ECPP_CERTIFICATE_BEGIN__");
        int c; while ((c = fgetc(f)) != EOF) putchar(c);
        fclose(f); puts("\n__ECPP_CERTIFICATE_END__");
    }
    puts("__ECPP_GUEST_COMPLETE__");
    sync();
    if (!ioperm(0xf4, 4, 1)) outl(0x10, 0xf4);
    reboot(RB_POWER_OFF);
    for (;;) pause();
}
