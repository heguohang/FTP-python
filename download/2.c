#include <winsock2.h>
#include <stdio.h>
#include <stdlib.h>
#pragma comment(lib,"ws2_32.lib")
#define DEFAULT_PORT        2302
#define DEFAULT_BUFFER      2048
#define DEFAULT_MESSAGE     "This is a test of the emergency \ broadcasting system"
char szServerip[128],          // Server to connect to
      szMessage[1024];        // Message to send to sever
int   iPort     = DEFAULT_PORT; // Port on server to connect to
//DWORD dwCount   = DEFAULT_COUNT; // Number of times to send message
BOOL bSendOnly = FALSE;         // Send data only; don't receive
int dirfun();
int getfun();
int putfun();
int pwdfun();
int cdfun();
int mdfun();
int delfun();
int usafun();
 
void usage()
{
    printf("usage: client [-p:x] [-s:IP] [-n:x] [-o]\n\n");
    printf("       -p:x      Remote port to send to\n");
    printf("       -s:IP     Server's IP address or hostname\n");
    printf("       -n:x      Number of times to send message\n");
    printf("       -o        Send messages only; don't receive\n");
    ExitProcess(1);
}
void ValidateArgs(int argc, char **argv)
{
    int                i;
 
    for(i = 1; i < argc; i++)
    {
        if ((argv[i][0] == '-') || (argv[i][0] == '/'))
        {
            switch (tolower(argv[i][1]))
            {
                case 'p':        // Remote port
                    if (strlen(argv[i]) > 3)
                        iPort = atoi(&argv[i][3]);
                    break;
                case 's':       // Server
                    if (strlen(argv[i]) > 3)
                        strcpy(szServerip, &argv[i][3]);
                    break;
                case 'n':       // Number of times to send message
                    if (strlen(argv[i]) > 3)
                        //dwCount = atol(&argv[i][3]);
                    break;
               case 'o':       // Only send message; don't receive
                    bSendOnly = TRUE;
                    break;
                default:
                    usage();
                    break;
            }
        }
    }
}
int main(int argc, char **argv)
{
    WSADATA       wsd;
    SOCKET        sClient;
    char          szBuffer[DEFAULT_BUFFER];
    int           ret;
    //unsigned int           i;
     //int j;
    struct sockaddr_in server;
    struct hostent    *host = NULL;
     char choice[5],choice2[40];
    // Parse the command line and load Winsock
    //
     argv[1]="-s:127.0.0.1";
     strcpy(szServerip, &argv[1][3]);
    //ValidateArgs(argc, argv);
    if (WSAStartup(MAKEWORD(2,2), &wsd) != 0)
    {
        printf("Failed to load Winsock library!\n");
        return 1;
    }
    //strcpy(szMessage, DEFAULT_MESSAGE);
    //
    // Create the socket, and attempt to connect to the server
    //
    sClient = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (sClient == INVALID_SOCKET)
    {
        printf("socket() failed: %d\n", WSAGetLastError());
        return 1;
    }
    server.sin_family = AF_INET;
    server.sin_port = htons(iPort);
     printf("server.sin_port=%u\n",server.sin_port);
    server.sin_addr.s_addr = inet_addr(szServerip);
   //
    // If the supplied server address wasn't in the form
    // "aaa.bbb.ccc.ddd" it's a hostname, so try to resolve it
    //
    if (server.sin_addr.s_addr == INADDR_NONE)
    {
        host = gethostbyname(szServerip);
        if (host == NULL)
        {
            printf("Unable to resolve server: %s\n", szServerip);
            return 1;
        }
        CopyMemory(&server.sin_addr, host->h_addr_list[0],
            host->h_length);
    }
    if (connect(sClient, (struct sockaddr *)&server, 
        sizeof(server)) == SOCKET_ERROR)
    {
        printf("connect() failed: %d\n", WSAGetLastError());
        return 1;
    }
    //显示接通信息
     //
     //
     //for(j=0;j<2;j++)
     //
     {
             ret = recv(sClient, szBuffer, DEFAULT_BUFFER, 0);
            if (ret == 0)        // Graceful close
                return 0;
            else if (ret == SOCKET_ERROR)
            {
                printf("recv() failed: %d\n", WSAGetLastError());
                return 0;
            }
            szBuffer[ret] = '\0';
              printf("%s\n",szBuffer);
              if(ret<15)
              {
                   ret = recv(sClient, szBuffer, DEFAULT_BUFFER, 0);
                   if (ret == 0)        // Graceful close
                       return 0;
                   else if (ret == SOCKET_ERROR)
                   {
                       //printf("recv() failed: %d\n", WSAGetLastError());
                       return 0;
                   }
                   szBuffer[ret] = '\0';
                   printf("%s\n",szBuffer);
              }
              //printf("DEFAULT_BUFFER=%d\n",DEFAULT_BUFFER);
 
     }
     while(1)
     {    
         puts("------------------------------------------");
         printf("ftp> ");
         scanf("%s", choice);
         
         
         if(strncmp(choice,"dir",3)==0||strncmp(choice,"DIR",2)==0)
         {
              dirfun(sClient);
              continue;
         }    
              else if(strncmp(choice,"pwd",3)==0||strncmp(choice,"PWD",3)==0)
              {
 
                   pwdfun(sClient);
                   continue;
              }
              else if(strncmp(choice,"?",1)==0)
              {
                   usafun(sClient);
                   continue;
              }
              else if(strncmp(choice,"quit",4)==0||strncmp(choice,"QUIT",2)==0)
              {
                   break;
              }
              scanf("%s", choice2);
              if(strncmp(choice,"get",3)==0||strncmp(choice,"GET",3)==0)
              {
                   getfun(sClient,choice2);
                   continue;
              }
              else if(strncmp(choice,"put",3)==0||strncmp(choice,"PUT",3)==0)
              {
                   putfun(sClient,choice2);
                   continue;
              }
 
              else if(strncmp(choice,"cd",2)==0||strncmp(choice,"CD",2)==0)
              {
                   cdfun(sClient,choice2);
                   continue;
              }
              else if(strncmp(choice,"md",2)==0||strncmp(choice,"MD",2)==0)
              {
                   mdfun(sClient,choice2);
                   continue;
              }
              else if(strncmp(choice,"del",3)==0||strncmp(choice,"DEL",3)==0)
              {
                   delfun(sClient,choice2);
                   continue;
              }
 
         //else
         puts("输入错误，请重新输入");
         fflush(stdin);
         fflush(stdin);
         printf("\n");   
         printf("\n");
     }
 
    closesocket(sClient);
 
    WSACleanup();
    return 0;
}
int dirfun(SOCKET sClient)
{
         int ret;
         char *MSG="dir$";char szBuffer[80];
         strcpy(szMessage, MSG);
 
         ret = send(sClient, szMessage, strlen(szMessage), 0);
        if (ret == 0)
            return 1;
        else if (ret == SOCKET_ERROR)
        {
            printf("send() failed: %d\n", WSAGetLastError());
            return 1;
        }
        //printf("Send %d bytes\n", ret);
         //printf("bSendOnly=%d\n",bSendOnly);
        while(!bSendOnly)
        {
              //读取流并显示         
              //ret = recv(sClient, szBuffer, 80, 0);
              //printf("%s",szBuffer);
            ret = recv(sClient, szBuffer, 80, 0);
            if (ret == 0)        // Graceful close
                return 1;
            else if (ret == SOCKET_ERROR)
            {
                printf("recv() failed: %d\n", WSAGetLastError());
                return 1;
            }
            szBuffer[ret] = '\0';
              
                       
              if(strncmp(szBuffer,"226 Close",strlen("226 Close"))==0)
              {
                   break;
              }
              printf("%s",szBuffer);
              if(strncmp(szBuffer,"500 Syntax error",strlen("500 Syntax error"))==0)
              {
                   break;
              }
              
         }
     return 0;
}
int getfun(SOCKET sClient,char filename[40])
{
         int ret;
         FILE *fpre;
         char szBuffer[80]; 
         szMessage[0]='\0';
         strcat(szMessage, "get$");
         //strcat(szMessage, "\\");
         strcat(szMessage,filename);
         //printf("MSG[4]=%c\n",szMessage[4]);
         
         //szMessage[0]='g';szMessage[1]='e';szMessage[2]='t';
         //
         //szMessage[4]='m';szMessage[5]='e';szMessage[6]='.';szMessage[7]='t';
         //
         //szMessage[8]='x';szMessage[9]='t';szMessage[10]='\0';
        ret = send(sClient, szMessage, strlen(szMessage)+1, 0);
        if (ret == 0)
            return 1;
        else if (ret == SOCKET_ERROR)
        {
            printf("send() failed: %d\n", WSAGetLastError());
            return 1;
        }
        printf("Send %d bytes\n", ret);
         ret = recv(sClient, szBuffer, 80, 0);
      /*if (ret == 0)        // Graceful close
                break;
         else if (ret == SOCKET_ERROR)
         {
              printf("recv() failed: %d\n", WSAGetLastError());
              break;
         }*/
        szBuffer[ret] = '\0';
         printf("%s\n",szBuffer);
         if(strncmp( szBuffer,"125 Transfering...",strlen("125 Transfering...") )==0)
         {
              if( (fpre=fopen(filename,"w")) == NULL )
              {
                   printf("open errer");
                   return 1;
              }
              printf("bSendOnly=%d\n",bSendOnly);
              while(!bSendOnly)
              {
                   //读取流并显示
                   ret = recv(sClient, szBuffer, 80, 0);
                   if (ret == 0)        // Graceful close
                       return 1;
                   else if (ret == SOCKET_ERROR)
                   {
                       printf("recv() failed: %d\n", WSAGetLastError());
                       return 1;
                   }
                   szBuffer[ret] = '\0';
                   
                   //printf("%s",szBuffer);             
                   if(strncmp(szBuffer,"226 Transfer",strlen("226 Transfer"))==0)
                   {
                       break;
                   }
                   if(strncmp(szBuffer,"500 Syntax error",strlen("500 Syntax error"))==0)
                   {
                       break;
                   }
                   fprintf(fpre,"%s",szBuffer);
              }
              printf("%s\n",szBuffer);
              fclose(fpre);
         }
     return 0;
}
int putfun(SOCKET sClient,char filename[40])
{
         int ret;//int i;
         FILE *fpse;//char *filename;
         //char *MSG="get\0me.txt";
         
         char szBuffer[80],temp_buffer[80];
         //sprintf(szMessage, "get\0","te.txt\0");
         szMessage[0]='\0';
         strcat(szMessage, "put$");
         strcat(szMessage,filename);
        ret = send(sClient, szMessage, strlen(szMessage)+1, 0);
        if (ret == 0)
            return 0;
        else if (ret == SOCKET_ERROR)
        {
            printf("send() failed: %d\n", WSAGetLastError());
            return 1;
        }
        //printf("Send %d bytes\n", ret);
         //filename="me.txt";
         printf("filename=%s\n",filename);
         if( (fpse=fopen(filename,"r")) == NULL )
         {
              printf("open errer");
              return 1;
         }
         else
         {
              printf("The file %s found,ready to transfer.\n",filename);
              //i=0;
              while (fgets(temp_buffer,80,fpse)!=NULL)
              {
                   sprintf(szBuffer,"%s",temp_buffer); 
                   send(sClient, szBuffer, 80, 0);
              }
         }
         sprintf(szBuffer, "226 Transfer completed... \r\n");    
         ret = send(sClient, szBuffer, strlen(szBuffer), 0);
 
         fclose(fpse);
         return 0;
}
int pwdfun(SOCKET sClient)
{
     int ret;
     char *MSG="pwd$";
     char szBuffer[160];
     strcpy(szMessage, MSG);
     ret = send(sClient, szMessage, strlen(szMessage), 0);
    if (ret == 0)
         return 1;
     else if (ret == SOCKET_ERROR)
         {
            printf("send() failed: %d\n", WSAGetLastError());
            return 1;
        }
     printf("Send %d bytes\n", ret);
     printf("bSendOnly=%d\n",bSendOnly);
     while(!bSendOnly)
     {
              //读取流并显示
         ret = recv(sClient, szBuffer, 160, 0);
         if (ret == 0)        // Graceful close
              return 1;
         else if (ret == SOCKET_ERROR)
         {
            printf("recv() failed: %d\n", WSAGetLastError());
            return 1;
         }
         szBuffer[ret] = '\0';
         printf("%s\n",szBuffer);
         
         if(strncmp(szBuffer,"226 Close",strlen("226 Close"))==0)
         {
              break;
         }
         if(strncmp(szBuffer,"500 Syntax error",strlen("500 Syntax error"))==0)
         {
              break;
         }
     }
     return 0;
}
int cdfun(SOCKET sClient,char pathname[40])
{
     int ret;
     
         szMessage[0]='\0';
         strcat(szMessage, "cd$");
         strcat(szMessage,pathname);
        ret = send(sClient, szMessage, strlen(szMessage)+1, 0);
        if (ret == 0)
            return 1;
        else if (ret == SOCKET_ERROR)
        {
            printf("send() failed: %d\n", WSAGetLastError());
            return 1;
        }
        printf("Send %d bytes\n", ret);
     
     return 0;
}
int mdfun(SOCKET sClient,char pathname[20])
{
     int ret;char szBuffer[160];
     //char *MSG="md$";
     szMessage[0]='\0';
     strcat(szMessage, "md$");
         //strcat(szMessage, "\\");
     strcat(szMessage,pathname);
     //strcpy(szMessage, MSG);
 
         ret = send(sClient, szMessage, strlen(szMessage)+1, 0);
        if (ret == 0)
            return 1;
        else if (ret == SOCKET_ERROR)
        {
            printf("send() failed: %d\n", WSAGetLastError());
            return 1;
        }
        printf("Send %d bytes\n", ret);
        while(!bSendOnly)
        {
              //读取流并显示         
            ret = recv(sClient, szBuffer, 80, 0);
            if (ret == 0)        // Graceful close
                return 1;
            else if (ret == SOCKET_ERROR)
            {
                printf("recv() failed: %d\n", WSAGetLastError());
                return 1;
            }
            szBuffer[ret] = '\0';
              
            printf("%s",szBuffer);             
              if(strncmp(szBuffer,"226 Close",strlen("226 Close"))==0)
              {
                   break;
              }
              if(strncmp(szBuffer,"500 Syntax error",strlen("500 Syntax error"))==0)
              {
                   break;
              }
              
         }
     return 0;
}
int delfun(SOCKET sClient,char name[20])
{
     int ret;char szBuffer[80];
     szMessage[0]='\0';
     strcat(szMessage, "del$");
 
     strcat(szMessage,name);
     ret = send(sClient, szMessage, strlen(szMessage)+1, 0);
    if (ret == 0)
         return 1;
     else if (ret == SOCKET_ERROR)
     {
         printf("send() failed: %d\n", WSAGetLastError());
         return 1;
     }
     printf("Send %d bytes\n", ret);
     while(!bSendOnly)
    {
         ret = recv(sClient, szBuffer, 80, 0);
         if (ret == 0)        // Graceful close
              return 1;
         else if (ret == SOCKET_ERROR)
         {
                printf("recv() failed: %d\n", WSAGetLastError());
                return 1;
         }
            szBuffer[ret] = '\0';
              
         if(strncmp(szBuffer,"del ok",strlen("del ok"))==0)
         {
                   printf("del %s ok\n",name);
                   break;
         }
         printf("%s",szBuffer);
         if(strncmp(szBuffer,"500 Syntax error",strlen("500 Syntax error"))==0)
         {
                   break;
         }
              
     }
     return 0;
}
int usafun()
{
     puts("------------------------------------------");
     puts("get：取远方的一个文件");
     puts("put：传给远方一个文件");
     puts("pwd：显示远主当前目录");
     puts("dir：列出远方当前目录");
     puts("md ：在远方新建文件夹");
     puts("cd ：改变远方当前目录");
     puts("？ ：显示你提供的命令");
     puts("quit ：退出返回");
     return 0;
}
//int quit()