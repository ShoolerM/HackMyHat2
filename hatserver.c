#include <signal.h>
#include <stdio.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <string.h>
#include <stdlib.h>
#include <sys/un.h>
#include <errno.h>
#include <sys/signal.h>
#include <wait.h>
#include <unistd.h>
#include <sys/stat.h>
#include <stdbool.h>
#include <time.h>
#define PID_PATH "/home/hat/hatserver.pid"
#define SOCK_PATH "/home/hat/hatsock"
#define LED_SOCK_PATH "/home/hat/ledsock"
#define LOG_PATH "/home/hat/.hatlog"

void fork_handler(int);
void handle_connection(int);
void handle_args(int argc, char *argv[]);
void kill_daemon();
void daemonize();
void stop_server();
void init_socket();
void init_led_socket();
void bootsnake();
void yeehaw();

int server_sockfd;
int led_sockfd;


static char gNFC_data[32];
static int  tarnation;
static char a_hacker;
static char is_dev;

int main(int argc, char *argv[])
{
        int client_sockfd;
        struct sockaddr_un remote;
        int t;

        if(argc > 1) {handle_args(argc, argv);}

        signal(SIGTERM, stop_server);

        init_socket();

        if(listen(server_sockfd, 5) == -1)
        {
                perror("listen");
                exit(1);
        }

        printf("Listening...\n");
        fflush(stdout);

        for(;;) //This might take a while...
        {
                printf("Waiting for a connection\n");
                fflush(stdout);
                t = sizeof(remote);
                if((client_sockfd = accept(server_sockfd, (struct sockaddr *)&remote, &t)) == -1)
                {
                        perror("accept");
                        exit(1);
                }

                printf("Accepted connection\n");
                fflush(stdout);
                handle_connection(client_sockfd);
        }
}

void bootsnake()
{
    printf("There's a snake in my boot!\n");
}

void yeehaw()
{
    system("/home/hat/yeehaw.sh");
}

void check_lights(char* flag_token)
{
    //Use the rand_key generator NFC tag
    bool check = true;
    for(int i=0; i<10; i++)
    {
        if (gNFC_data[i] != flag_token[i] )
            check = false;
    }
    if (check)
    {
        init_led_socket();
        char sendme[6] = "blink\0";
        send(led_sockfd, sendme, strlen(sendme), 0);
        close(led_sockfd);
    }
}

void run_lights()
{
    /*
    Rundown of the light commands:
    blink = Blink
    color_wipe = Color Wipe (1 Color)
    theater_chase = Theater Chase
    rainbow = Rainbow, like color wipe but rainbows
    rainbow_cycle = Rainbow Cycle, all leds cycle a rainbow
    rand = Randomly lights up some leds!
    solid_rand = like rand, but with 1 color
    rand_clear = Clears the leds randomly until all off
    clear = like color wipe, but turns off the leds
    allclear =  Turn off all the leds at once

    sample command:
    color_wipe rand_clear rainbow allclear
    */

    if (is_dev && !a_hacker)
    {
        init_led_socket();
        send(led_sockfd, gNFC_data, strlen(gNFC_data), 0);
        close(led_sockfd);
    }
}

void format_NFC_data(char* buffer)
{
    tarnation = &bootsnake;
    for(int i=0; i<strlen(buffer); i++)
    {
        if (buffer[i] == 33)
            gNFC_data[i] = 0;
        else
            gNFC_data[i] = buffer[i];
    }
}

void handle_data(char* flag_token)
{
    //Admin function to test the LEDS, should get removed for production
    check_lights(flag_token);
    run_lights();
    //Now where in tarnation did I put that third flag?
}

void generate_flag_token(char *flag_buf)
{
    flag_buf[11] = 0; //Make sure we null terminate!
    //Utilize random memory to make a random string!
    for(int i=0; i<10; i++)
    {
        flag_buf[i] = flag_buf[i+20];
    }
}

void handle_connection(int client_sockfd)
{
        unsigned int len;

        printf("Handling connection\n");
        fflush(stdout);
        char nfc_card_data[512] = {0};
        char flag_buf[11] = {0};
        while(len = recv(client_sockfd, nfc_card_data, sizeof(nfc_card_data), 0),
              len > 0)
        {
            printf("Receieved nfc_card_data: %s\n", nfc_card_data);
            generate_flag_token(flag_buf);
            format_NFC_data(nfc_card_data);
            handle_data(flag_buf);
        }
        close(client_sockfd);
        printf("Done handling\n");
        fflush(stdout);
}

void handle_args(int argc, char *argv[])
{
        if(strcmp(argv[1], "kill") == 0) {kill_daemon();}
        if(strcmp(argv[1], "-D") == 0 || strcmp(argv[1], "--daemon") == 0) {daemonize();}
}

void kill_daemon()
{
        FILE *pidfile;
        pid_t pid;
        char pidtxt[32];

        if(pidfile = fopen(PID_PATH, "r"))
        {
                fscanf(pidfile, "%d", &pid);
                printf("Killing PID %d\n", pid);
                kill(pid, SIGTERM); //kill it gently
        }
        else
        {
                printf("un_server not running\n"); //or you have bigger problems
        }
        exit(0);
}

void daemonize()
{
        FILE *pidfile;
        pid_t pid;

        switch(pid = fork())
        {
                case 0:
                        //redirect I/O streams
                        freopen("/dev/null", "r", stdin);
                        freopen(LOG_PATH, "w", stdout);
                        freopen(LOG_PATH, "w", stderr);
                        //make process group leader
                        setsid();
                        chdir("/");
                        break;
                case -1:
                        perror("Failed to fork daemon\n");
                        exit(1);
                default:
                        //write pidfile & you can go home!
                        pidfile = fopen(PID_PATH, "w");
                        fprintf(pidfile, "%d", pid);
                        fflush(stdout);
                        fclose(pidfile);
                        exit(0);
        }
}

void stop_server()
{
        unlink(PID_PATH);  //Get rid of pesky pidfile, socket
        unlink(SOCK_PATH);
        kill(0, SIGKILL);  //Infanticide :(
        exit(0);
}

void init_socket()
{
        struct sockaddr_un local;
        int len;

        // setup this server socket
        if((server_sockfd = socket(AF_UNIX, SOCK_STREAM, 0)) == -1)
        {
                perror("Error creating server socket");
                exit(1);
        }

        local.sun_family = AF_UNIX;
        strcpy(local.sun_path, SOCK_PATH);
        unlink(local.sun_path);
        len = strlen(local.sun_path) + sizeof(local.sun_family);
        if(bind(server_sockfd, (struct sockaddr *)&local, len) == -1)
        {
                perror("binding");
                exit(1);
        }
        chmod(SOCK_PATH,0777);
}

void init_led_socket()
{
        struct sockaddr_un local;
        int len;
        
        // connect to led driver
        if((led_sockfd = socket(AF_UNIX, SOCK_STREAM, 0)) == -1)
        {
                perror("Error connecting to led server socket");
                exit(1);
        }

        local.sun_family = AF_UNIX;
        strcpy(local.sun_path, LED_SOCK_PATH);
        len = strlen(local.sun_path) + sizeof(local.sun_family);
        if(connect(led_sockfd, (struct sockaddr *)&local, len) == -1)
        {
                perror("connecting");
                exit(1);
        }
}
