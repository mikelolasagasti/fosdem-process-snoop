Name:           process-snoop
Version:        1.0
Release:        1%{?dist}
Summary:        A pure CO-RE eBPF process monitor

License:        GPLv2
Source0:        %{name}-%{version}.tar.gz

# --- BUILD DEPENDENCIES ---
# compilers for C and BPF
BuildRequires:  clang
BuildRequires:  llvm
BuildRequires:  gcc
# tools to generate vmlinux.h and skeleton
BuildRequires:  bpftool
# library headers
BuildRequires:  libbpf-devel
# THE SECRET SAUCE: Provides BTF for the target distro kernel
BuildRequires:  kernel-devel
BuildRequires:  kernel-core

# --- RUNTIME DEPENDENCIES ---
# Notice: NO clang/llvm here! Just the library.
Requires:       libbpf

%description
A demonstration of a Pure CO-RE eBPF tool packaged for Fedora.

%prep
%setup -q

%build
# 1. Get Kernel Version
# Query kernel-core for the exact version string matching the directory structure
KVER=$(rpm -q --qf '%%{VERSION}-%%{RELEASE}.%%{ARCH}' kernel-core | head -n 1)

# 2. Define Static Paths
VMLINUZ="/lib/modules/$KVER/vmlinuz"
EXTRACT_SCRIPT="/usr/src/kernels/$KVER/scripts/extract-vmlinux"

# 3. Safety Check (Good practice in case KVER parsing drifts)
if [ ! -f "$VMLINUZ" ] || [ ! -x "$EXTRACT_SCRIPT" ]; then
    echo "Error: Files not found at expected paths!"
    echo "  Kernel: $VMLINUZ"
    echo "  Script: $EXTRACT_SCRIPT"
    exit 1
fi

# 4. Decompress and Generate Headers
$EXTRACT_SCRIPT "$VMLINUZ" > vmlinux_local
bpftool btf dump file vmlinux_local format c > vmlinux.h
rm -f vmlinux_local

# 2. COMPILE BPF (KERNEL SIDE)
# -g: debug info (needed for BTF)
# -O2: required by verifier
# -target bpf: output BPF bytecode
clang -g -O2 -target bpf -D__TARGET_ARCH_x86 -c agent.bpf.c -o agent.bpf.o

# 3. GENERATE SKELETON
bpftool gen skeleton agent.bpf.o > agent.skel.h

# 4. COMPILE LOADER (USER SIDE)
gcc -O2 -g -Wall main.c -o process-snoop -lbpf -lelf -lz

%install
mkdir -p %{buildroot}%{_bindir}
install -m 755 process-snoop %{buildroot}%{_bindir}/

%files
%caps(cap_bpf,cap_perfmon=ep) %{_bindir}/process-snoop
%license LICENSE

%changelog
* Fri Jan 30 2026 FOSDEM Demo - 1.0.0-1
- Initial CO-RE package
