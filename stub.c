
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
    code1();
}


//these guys have a crazy hack, when you call them they populate a table with a pointer to itself
//then they also set the "choosen" move
//asrludn
void move_a(){
    asm volatile (
    "call _l1\n"
    "_l1:\n"
    "pop rax\n"
    "sub rax, 9\n"
    "mov qword ptr ["XSTR(COMPUTING_HEAP_START+fpointer_table_move_a_off)"], rax\n"
    //"int3\n"
    );
    *(unsigned char*)(COMPUTING_HEAP_START + moveout_off) = 'a';
}
void move_s(){
    asm volatile (
    "call _l2\n"
    "_l2:\n"
    "pop rax\n"
    "sub rax, 9\n"
    "mov qword ptr ["XSTR(COMPUTING_HEAP_START+fpointer_table_move_s_off)"], rax\n"
    //"int3\n"
    );
    *(unsigned char*)(COMPUTING_HEAP_START + moveout_off) = 's';
}
void move_r(){
    asm volatile (
    "call _l3\n"
    "_l3:\n"
    "pop rax\n"
    "sub rax, 9\n"
    "mov qword ptr ["XSTR(COMPUTING_HEAP_START+fpointer_table_move_r_off)"], rax\n"
    //"int3\n"
    );
    *(unsigned char*)(COMPUTING_HEAP_START + moveout_off) = 'r';
}
void move_l(){
    asm volatile (
    "call _l4\n"
    "_l4:\n"
    "pop rax\n"
    "sub rax, 9\n"
    "mov qword ptr ["XSTR(COMPUTING_HEAP_START+fpointer_table_move_l_off)"], rax\n"
    //"int3\n"
    );
    *(unsigned char*)(COMPUTING_HEAP_START + moveout_off) = 'l';
}
void move_u(){
    asm volatile (
    "call _l5\n"
    "_l5:\n"
    "pop rax\n"
    "sub rax, 9\n"
    "mov qword ptr ["XSTR(COMPUTING_HEAP_START+fpointer_table_move_u_off)"], rax\n"
    //"int3\n"
    );
    *(unsigned char*)(COMPUTING_HEAP_START + moveout_off) = 'u';
}
void move_d(){
    asm volatile (
    "call _l6\n"
    "_l6:\n"
    "pop rax\n"
    "sub rax, 9\n"
    "mov qword ptr ["XSTR(COMPUTING_HEAP_START+fpointer_table_move_d_off)"], rax\n"
    //"int3\n"
    );
    *(unsigned char*)(COMPUTING_HEAP_START + moveout_off) = 'd';
}
void move_n(){
    asm volatile (
    "call _l7\n"
    "_l7:\n"
    "pop rax\n"
    "sub rax, 9\n"
    "mov qword ptr ["XSTR(COMPUTING_HEAP_START+fpointer_table_move_n_off)"], rax\n"
    //"int3\n"
    );
    *(unsigned char*)(COMPUTING_HEAP_START + moveout_off) = 'n';
}

int check_stuff(){
    //this should check that the first 2 layers are only 2 neurons
    unsigned int off = *(unsigned int*)(COMPUTING_HEAP_START+pointer_inputs_off);
    off += 4*1;
    unsigned int v = *(unsigned int*)((((unsigned char*)INPUT_START)+off));
    if(v>2){
        return 0;
    }else{
        return 1;
    }
}


double expd2(double x) {
    double term = 1.0;
    double result = term;

    /* 
    the only trick is that term can be positive as well as negative; 
    we should either use abs in any implementation or putr two conditions
    */
    for (int n = 1; term > 0.000001 || term < -0.000001; ++n) {
        term = term * x / n; 

        result += term;
    } 

    return result;
}


float myexp(float x){
    double r;
    r = expd2((double) x);
    return (float) r;
}

typedef struct ropship_model {
    /* How many inputs, outputs, and hidden neurons. */
    unsigned int inputs, hidden_layers, hidden, outputs, ltype1, ltype2, ltype3;
    //total_weight
    //total_neurons
    /* All weights (total_weights long). */
    float weight[16000];

    /* Stores input array and output of each neuron (total_neurons long). */
    float output[8];

} ropship_model;


float ROPSHIP_SIGMOID(float a) {
    if (a < -45.0) return 0;
    if (a > 45.0) return 1;
    return 1.0 / (1 + myexp(-a));
}

float ROPSHIP_RELU(float a) {
    if (a <= 0.0) return 0.0;
    if (a > 0.0) return a;
}

float ROPSHIP_LAYER_FUNCTION(float a, unsigned int type){
    if(type==0){
        return ROPSHIP_RELU(a);
    }else if(type==1){
        return ROPSHIP_SIGMOID(a);
    }else{
        return 0.0;
    }
}

float const *ropship_run(ropship_model *ann, float const *inputs) {
    //asm volatile("int 3\n");
    float const *w = ann->weight;
    float *o = ann->output + ann->inputs;
    float const *i = ann->output;


    /* Copy the inputs to the scratch area, where we also store each neuron's
     * output, for consistency. This way the first layer isn't a special case. */
    for(unsigned int j=0; j<ann->inputs; j++){
        (ann->output)[j] = inputs[j];
    }

    int h, j, k;
    int c =0;


    /* Figure input layer */
    //asm volatile("int 3\n");
    for (j = 0; j < ann->hidden; ++j) {
        float sum = *w++ * -1.0;
        for (k = 0; k < ann->inputs; ++k) {
            sum += *w++ * i[k];c+=1;
        }
        *o++ = ROPSHIP_LAYER_FUNCTION(sum, ann->ltype1);
    }

    i += ann->inputs;

    /* Figure hidden layers, if any. */
    for (h = 1; h < ann->hidden_layers; ++h) {
        for (j = 0; j < ann->hidden; ++j) {
            float sum = *w++ * -1.0;
            for (k = 0; k < ann->hidden; ++k) {
                sum += *w++ * i[k];c+=1;
            }
            *o++ = ROPSHIP_LAYER_FUNCTION(sum, ann->ltype2);
        }

        i += ann->hidden;
    }

    float const *ret = o;

    /* Figure output layer. */
    for (j = 0; j < ann->outputs; ++j) {
        float sum = *w++ * -1.0;
        for (k = 0; k < ann->hidden; ++k) {
            sum += *w++ * i[k];c+=1;
        }
        *o++ = ROPSHIP_LAYER_FUNCTION(sum, ann->ltype3);
    }
    return ret;
}


unsigned int getint(){
    unsigned int off = *(unsigned int*)(COMPUTING_HEAP_START+pointer_inputs_off);
    *(unsigned int*)(COMPUTING_HEAP_START+pointer_inputs_off)+=4;
    unsigned int v = *(unsigned int*)((((unsigned char*)INPUT_START)+off));
    return v;
}

float getfloat(){
    unsigned int off = *(unsigned int*)(COMPUTING_HEAP_START+pointer_inputs_off);
    *(unsigned int*)(COMPUTING_HEAP_START+pointer_inputs_off)+=4;
    float v = *(float*)((((unsigned char*)INPUT_START)+off));
    return v;
}

unsigned int run_network(){
    //asm volatile("int 3\n"); //sigtrap takes > 0.1 seconds!
    //asm volatile("int 3\n"); 


    //printf("%08x\n", (unsigned int)getcurrentinputpointer());
    //asm volatile("int 3\n");
    ropship_model* model = (ropship_model*)(((unsigned char*)COMPUTING_HEAP_START)+model_off);
    model->inputs = getint();
    model->hidden_layers = 2;
    //printf("=\n");
    //asm volatile("int 3\n");
    model->hidden = getint();
    model->outputs = getint();

    if(model->inputs>64 || model->hidden>64 || model->outputs>64)
    {
        asm volatile(
            "mov rax, 60\n"
            "mov rdi, 12\n"
            "syscall"
        );
    }

    unsigned int nstates = getint();
    float states[50];
    for(unsigned int i=0; i<nstates; i++){
        //asm volatile("int 3\n");
        states[i] = ((float*)STATE_START)[getint()];
        //asm volatile("int 3\n");
        //asm volatile("int 3\n");
    }

    model->ltype1 = getint();
    model->ltype2 = getint();
    model->ltype3 = getint();
    //printf("=== %d\n", model->outputs);

    for(unsigned int j=0; j<((model->inputs*model->hidden)+((model->hidden)*model->hidden)+(model->hidden*model->outputs)+(model->hidden*2)+(model->outputs)); j++){
        float v = getfloat();
        //printf("- %d %f\n", j, v);
        model->weight[j] = v;
    }
    
    //asm volatile("int 3\n");    
    const float *outputs = ropship_run(model, states);
    //asm volatile("int 3\n");



    for(unsigned long i=0; i<model->outputs; i++){
        *(float*)(COMPUTING_HEAP_START + exit_neuron_a_off + i*8) = outputs[i];
    }


    //asm volatile("int 3\n");
    return model->outputs;

    //this commented block is the exploit scenario
    //the last neuron is the highest one, we are going to jump to the "address" of the value of the first neuron
    //the first neuron needs to be computed so that it is the right value when considering aslr
    //we want to ultimately jump to run_network again
    //we will use a pointer into the "consumed" INPUT so that when we jump here again, we use new values from INPUT
    /*
    *(float*)(COMPUTING_HEAP_START + exit_neuron_a_off) = 0.58203125; // equal to address 0x3f150000
    *(float*)(COMPUTING_HEAP_START + exit_neuron_s_off) = 0.1f;
    *(float*)(COMPUTING_HEAP_START + exit_neuron_r_off) = 0.1f;
    *(float*)(COMPUTING_HEAP_START + exit_neuron_l_off) = 0.1f;
    *(float*)(COMPUTING_HEAP_START + exit_neuron_u_off) = 0.1f;
    *(float*)(COMPUTING_HEAP_START + exit_neuron_d_off) = 0.1f;
    *(float*)(COMPUTING_HEAP_START + exit_neuron_n_off) = 0.1f;
    *(float*)(COMPUTING_HEAP_START + exit_neuron_8_off) = 0.9f;
    */
    

}

void run_network_wrapper(){
    unsigned int dummyguy = 0x84762231; //used by generate_inputs to find this functions
    unsigned int noutputs = run_network();

    //get highest exit neuron index
    float v;
    float max_v = 0.0;
    unsigned long j = 0;
    for(unsigned long i=0; i<noutputs; i++){
        v = *(float*)(COMPUTING_HEAP_START + exit_neuron_a_off + i*8);
        //asm volatile("int 3\n");
        if(v>max_v){
            j = i;
            max_v = v;
        }
    }
    //asm volatile("int 3\n");
    //use the index of the highest valud neruon in a table of function pointers
    //however the index = 7 (neuron8) is going to make it use the value of the first exit neuron as a function pointer 
    //asm volatile("int 3\n");
    unsigned long fp = *(unsigned long*)(COMPUTING_HEAP_START+fpointer_table_move_a_off + (8*j));
    //asm volatile("int 3\n");
    //asm volatile("int 3\n");
    ((void (*)(void)) (fp) )();

    //asm volatile("int 3\n");
    //exit with the move as the exit code
    asm volatile(
        "mov rax, 60\n"
        "mov rdi, qword ptr ["XSTR(COMPUTING_HEAP_START+moveout_off)"]\n"
        "syscall"
    );
}

void code1(){
    //setup pointer table
    move_a();
    move_s();
    move_l();
    move_r();
    move_u();
    move_d();
    move_n();
    //asm volatile("int 3\n");

    //asm volatile("int 3\n"); 
    if(!check_stuff()){//this should check that the network is "small"
        move_n();
        //exit with the move as the exit code
        asm volatile(
            "mov rax, 60\n"
            "mov rdi, 11\n"
            "syscall"
        );
    } 
    //asm volatile("int 3\n");
    run_network_wrapper();
    //asm volatile("int 3\n");


    //asm volatile("int 3\n");
    while(1){;}
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

    fd = open(argv[1], O_RDONLY, 0);
    mmap((void*) INPUT_START, 0x100000, PROT_READ, MAP_FIXED | MAP_PRIVATE | MAP_POPULATE, fd, 0); //1MB size
    close(fd); 

    fd = open(argv[2], O_RDONLY, 0);
    mmap((void*) STATE_START, 0x100000, PROT_READ, MAP_FIXED | MAP_PRIVATE | MAP_POPULATE, fd, 0);
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

    while(1){
        if(ptr[i] == 0x5b && ptr[i+1] == 0xd3 & ptr[i+2] == 0xfc & ptr[i+3] == 0x3d){
            last1 = i; //copy +-0x80 around the floating point dummy value to get rodata 
            last1 = i-0x80;
            last2 = i+0x80;
            break;
        }
        i++;
    }

    i=0;
    while(1){
        if(i>last2){
            break;
        }
        if(ptr[i] == 0xcc && ptr[i+1] == 0xcc & ptr[i+2] == 0xcc & ptr[i+3] == 0xcc){
            found = 1;
        }
        if(found==0 || i>last1){
            //printf("%08x\n", i);
            ((unsigned char*)codep)[i] = ptr[i];
        }else{
            //printf("CC %08x\n", i);
            ((unsigned char*)codep)[i] = 0xcc;
        }

        i++;
    }

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
ls -1 aslrtests/ | xargs -n1 -P1 -I{} bash -c 'A={}; echo {}; ./stub inputs/team1 /dev/shm/ropship/round_state_1 0x3e"$A"0000; echo $?
*/
