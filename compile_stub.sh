#/usr/bin/bash

rm stub
gcc -fno-stack-protector -O0 stub.c -masm=intel -o stub
strip -s stub

rm stub_seccomp_test
gcc -fno-stack-protector -O0 stub_seccomp_test.c -masm=intel -o stub_seccomp_test
strip -s stub_seccomp_test
