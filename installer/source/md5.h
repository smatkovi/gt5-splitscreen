#ifndef GT5_MD5_H
#define GT5_MD5_H

typedef struct {
    unsigned int h[4];
    unsigned long long len;
    unsigned int n;
    unsigned char buf[64];
} md5_ctx;

void md5_init(md5_ctx *c);
void md5_update(md5_ctx *c, const void *data, unsigned int len);
void md5_final(md5_ctx *c, unsigned char out[16]);
void md5_hex(const unsigned char in[16], char out[33]);

#endif
