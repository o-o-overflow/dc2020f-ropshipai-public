
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/types.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
#include <sys/prctl.h>
#include <linux/seccomp.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/prctl.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>



#define STR(x) #x
#define XSTR(s) STR(s)

/*
The input will have a format like this
number of first layer neurons
number of second layer neurons
number of third layer neurons
for each first layer neuron:
    index withing the "STATE" to use to start with
for each needed weight/bias:
    float32 value
*/

#define INPUT_START 0x00800000

/*
this is basically the serialization to list of float32 of the ~40 value vector we used to train the keras network 
*/
#define STATE_START 0x02000000

#define COMPUTING_STACK_START 0x30000000
#define COMPUTING_STACK_SIZE 0x06000000 //~100MB

#define COMPUTING_HEAP_START 0x38000000
#define COMPUTING_HEAP_SIZE 0x05000000 //~100MB
                            //0x3eff0000//ff
#define SECCOMP_AREA 0x60000000
#define SECCOMP_SIZE 0x1000

#define MEMORY_TOP 0x7ffffffff000
#define UPPER_MEMORY MEMORY_TOP - (SECCOMP_AREA + SECCOMP_SIZE)

//the seccomp filter goes at the beginning
#define moveout_off 0x180
#define codep_off 0x100

//asrludn
#define fpointer_table_move_a_off 0x200
#define fpointer_table_move_r_off 0x208
#define fpointer_table_move_u_off 0x210
#define fpointer_table_move_l_off 0x218
#define fpointer_table_move_s_off 0x220
#define fpointer_table_move_d_off 0x228
#define fpointer_table_move_n_off 0x230

#define exit_neuron_a_off 0x238
#define exit_neuron_r_off 0x240
#define exit_neuron_u_off 0x248
#define exit_neuron_l_off 0x250
#define exit_neuron_s_off 0x258
#define exit_neuron_d_off 0x260
#define exit_neuron_n_off 0x268
#define exit_neuron_8_off 0x270

#define pointer_inputs_off 0x800
#define model_off 0x2000



unsigned char FILTER[] = "\040\000\000\000\004\000\000\000\025\000\000\006\076\000\000\300\040\000\000\000\000\000\000\000\065\000\004\000\000\000\000\100\025\000\002\000\074\000\000\000\025\000\001\000\013\000\000\000\006\000\000\000\000\000\000\000\006\000\000\000\000\000\377\177\006\000\000\000\000\000\000\000";
unsigned long FILTER_LEN = sizeof(FILTER); //72


size_t getFilesize(const char* filename) {
    struct stat st;
    stat(filename, &st);
    return st.st_size;
}


void seccomp_trampoline(){
    asm volatile (
        "mov rax, 157\n"
        "mov rdi, 38\n"
        "mov rsi, 1\n"
        "mov rdx, 0\n"
        "mov r10, 0\n"
        "mov r8, 0\n"
        "syscall\n" //prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0);

        "mov rax, 157\n"
        "mov rdi, 22\n"
        "mov rsi, 2\n"
        "mov rdx, "XSTR(COMPUTING_HEAP_START)"\n"
        "mov r10, 0\n"
        "mov r8, 0\n"
        "syscall\n" //prctl(PR_SET_SECCOMP, SECCOMP_MODE_FILTER, COMPUTING_HEAP_START)
    ); //we allow only munmap and exit

    asm volatile (
        "mov rax, 11\n"
        "mov rdi, 0\n"
        "mov rsi, "XSTR(INPUT_START)"\n"
        "syscall\n" //munmap lower
        "mov rax, 11\n"
        "mov rdi, "XSTR(SECCOMP_AREA + SECCOMP_SIZE)"\n"
        "mov rsi, "XSTR(UPPER_MEMORY)"\n"
        "syscall\n" //munmap upper
    );


    asm volatile (
        //clean heap
        "mov rax, "XSTR(COMPUTING_HEAP_START)"\n"
        "xor rbx, rbx\n"
        "mov qword ptr [rax], rbx\n"
        "mov qword ptr [rax+8], rbx\n"
        "mov qword ptr [rax+16], rbx\n"
        "mov qword ptr [rax+24], rbx\n"
        "mov qword ptr [rax+32], rbx\n"
        "mov qword ptr [rax+40], rbx\n"
        "mov qword ptr [rax+48], rbx\n"
        "mov qword ptr [rax+56], rbx\n"
        "mov qword ptr [rax+64], rbx\n"
        "mov qword ptr [rax+72], rbx\n"
        "mov qword ptr [rax+80], rbx\n"
        "mov qword ptr [rax+88], rbx\n"

        //setup stack
        "mov rsp, "XSTR(COMPUTING_STACK_START+0x06000000-8)"\n"
        //clean regs
        "xor r15, r15\n"
        "xor r14, r14\n"
        "xor r13, r13\n"
        "xor r12, r12\n"
        "xor rbp, rbp\n"
        "xor rbx, rbx\n"
        "xor r11, r11\n"
        "xor r10, r10\n"
        "xor r9, r9\n"
        "xor r8, r8\n"
        "xor rax, rax\n"
        "xor rcx, rcx\n"
        "xor rdx, rdx\n"
        "xor rsi, rsi\n"
        "xor rdi, rdi\n"

        "mov rsi, r9\n"
        "mov rax, 0x1\n"
        "mov rdi, 0x1\n"
        "mov rdx, 0x0a0a670a0a\n"
        "mov rdx, 0x10\n"
        "syscall\n"
        "nop\n"
        "int 3\n"


        "jmp qword ptr ["XSTR(COMPUTING_HEAP_START+codep_off)"]\n"

        "int 3\n"

        "int 3\n"
        "int 3\n"
        "int 3\n"
        "int 3\n"
    );
}


//-----------
void code1();

void codestart(){
    ;
}


void codeend(){
    asm volatile (
        "int 3\n"
        "int 3\n"
        "int 3\n"
        "int 3\n"
        "int 3\n"
    );
}
//-----------



int main(int argc, char** argv) {
    //run_network();

    prctl(1,9);

    //while(1){;}

    size_t filesize;
    unsigned long codep;
    unsigned long codepsize = 0x10000;
    int fd;
    unsigned char* x = 0;
    unsigned char* ptr;
    unsigned long i=0;
    float dummyguy = 0.12345;
    /*float f1 = 0.58203125; //struct.unpack("!f", struct.pack(">I", 0x3eff0000))[0]  #0.125 to 0.498046875

    printf("%08x\n", f1);
    memcpy(x+4, &f1, 4);
    ((void (*)(void))x)();*/


    filesize = getFilesize(argv[1]);
    fd = open(argv[1], O_RDONLY, 0);
    mmap((void*) INPUT_START, filesize, PROT_READ, MAP_FIXED | MAP_PRIVATE | MAP_POPULATE, fd, 0);
    close(fd); 

    filesize = getFilesize(argv[2]);
    fd = open(argv[2], O_RDONLY, 0);
    mmap((void*) STATE_START, filesize, PROT_READ, MAP_FIXED | MAP_PRIVATE | MAP_POPULATE, fd, 0);
    close(fd); 

    codep = strtoul(argv[3], NULL, 16);

    mmap((void*) COMPUTING_STACK_START, COMPUTING_STACK_SIZE, PROT_READ | PROT_WRITE, MAP_FIXED | MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    mmap((void*) COMPUTING_HEAP_START, COMPUTING_HEAP_SIZE, PROT_READ | PROT_WRITE, MAP_FIXED | MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
 
    mmap((void*) SECCOMP_AREA, SECCOMP_SIZE, PROT_READ | PROT_WRITE | PROT_EXEC, MAP_FIXED | MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    ptr = (unsigned char*) seccomp_trampoline;
    i=0;
    while(1){
        ((unsigned char*)SECCOMP_AREA)[i] = ptr[i];
        if(ptr[i] == 0xcc && ptr[i+1] == 0xcc & ptr[i+2] == 0xcc & ptr[i+3] == 0xcc){
            break;
        }
        i++;
    }
    mprotect((void*) SECCOMP_AREA, SECCOMP_SIZE, PROT_READ | PROT_EXEC);

    mmap((void*) codep, codepsize, PROT_READ | PROT_WRITE | PROT_EXEC, MAP_FIXED | MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    ptr = (unsigned char*) codestart;
    i=0;
    unsigned int found = 0;
    unsigned long last1 = 0;
    unsigned long last2 = 0;


    mprotect((void*) codep, codepsize, PROT_READ | PROT_EXEC);
    *(unsigned long*)(COMPUTING_HEAP_START + codep_off) = codep;

    *(unsigned long*)(COMPUTING_HEAP_START) = (FILTER_LEN/8);
    *(unsigned long*)(COMPUTING_HEAP_START+8) = (COMPUTING_HEAP_START+8+8);
    for(unsigned long j=0; j<FILTER_LEN; j++){
        *(unsigned char*)(COMPUTING_HEAP_START + 8 + 8 + j) = FILTER[j];
    }

    //asm volatile("int 3\n");
    ((void (*)(void))SECCOMP_AREA)();
    asm volatile (
        "int 3\n"
    );

}


/*
compile and run with something like this
ii is the INPUT (what the player gives us)
ss is the state (the serialization of what we gave to keras)
0x3eff0000 is the "new base pointer" for the aslr-like mechanism
the exit code is the choosen move
gcc  -fno-stack-protector -O0 stub.c -masm=intel -o stub && ./stub inputs/team1 /dev/shm/ropship/round_state_1 0x3eff0000; echo $?
*/
