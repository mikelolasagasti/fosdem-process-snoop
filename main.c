// main.c
#include <stdio.h>
#include <unistd.h>
#include <stdint.h>
#include <bpf/libbpf.h>
#include "agent.skel.h"

// Use standard types for the userspace view of the data
struct event {
    uint32_t pid;       // u32 -> uint32_t
    uint8_t  comm[16];  // u8  -> uint8_t
};

static int handle_event(void *ctx, void *data, size_t data_sz) {
    const struct event *e = data;
    printf("PID %d ran command: %s\n", e->pid, e->comm);
    return 0;
}

int main(int argc, char **argv) {
    struct agent_bpf *skel;
    struct ring_buffer *rb = NULL;
    int err;

    // 1. Open and Load
    skel = agent_bpf__open_and_load();
    if (!skel) {
        fprintf(stderr, "Failed to load BPF skeleton\n");
        return 1;
    }

    // 2. Attach to Kernel
    err = agent_bpf__attach(skel);
    if (err) {
        fprintf(stderr, "Failed to attach BPF skeleton\n");
        goto cleanup;
    }

    printf("Successfully started! Ctrl+C to stop.\n");

    // 3. Poll the Ring Buffer
    rb = ring_buffer__new(bpf_map__fd(skel->maps.rb), handle_event, NULL, NULL);
    while (true) {
        ring_buffer__poll(rb, 100 /* timeout ms */);
    }

cleanup:
    ring_buffer__free(rb);
    agent_bpf__destroy(skel);
    return -err;
}
