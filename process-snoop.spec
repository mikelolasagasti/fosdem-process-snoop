Name:           process-snoop
Version:        1.0
Release:        2%{?dist}
Summary:        A pure CO-RE eBPF process monitor

License:        GPLv2
Source0:        %{name}-%{version}.tar.gz

# --- BUILD DEPENDENCIES ---
# compilers for C and BPF
BuildRequires:  clang
BuildRequires:  llvm
BuildRequires:  gcc
# tool to generate skeleton
BuildRequires:  bpftool
# library headers
BuildRequires:  libbpf-devel
# It provides vmlinux.h
BuildRequires:  kernel-devel

# --- RUNTIME DEPENDENCIES ---
# Notice: NO clang/llvm here! Just the library.
Requires:       libbpf >= 1.3

%description
A demonstration of a Pure CO-RE eBPF tool packaged for Fedora.

%prep
%setup -q

%build
# 1. FIND VMLINUX.H
# We query the installed kernel-devel package for its version
KVER=$(rpm -q --qf '%%{VERSION}-%%{RELEASE}.%%{ARCH}' kernel-core | head -n 1)

# Fedora ships vmlinux.h directly in the kernel headers directory
# We simply copy it to our source tree so our BPF code finds it
cp "/usr/src/kernels/$KVER/vmlinux.h" vmlinux.h

# 2. COMPILE BPF (KERNEL SIDE)
# Compile directly against the local vmlinux.h
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
* Sun Feb 01 2026 FOSDEM Demo - 1.0-2
- Rely on kernel-devel provided vmlinux.h instead of extracting it from kernel-core

* Fri Jan 30 2026 FOSDEM Demo - 1.0-1
- Initial CO-RE package
