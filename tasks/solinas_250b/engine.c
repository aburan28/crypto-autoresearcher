/* Public point-window sampler: fixed same-point starts, batched normalization.
   Measurement = every x bit 64, exact scores, witnesses and all rare frames.
   Full coordinate streams may optionally be saved on a sufficiently large disk. */
#include <openssl/ec.h>
#include <openssl/bn.h>
#include <openssl/sha.h>
#include <openssl/obj_mac.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define WINDOW 256

static BIGNUM *decimal(const char *s) { BIGNUM *v=NULL; return BN_dec2bn(&v,s)?v:NULL; }
static int draw(BIGNUM *v,const BIGNUM *limit,const unsigned char *seed,uint64_t *counter,int nonzero) {
    unsigned char m[40],h[32];int bits=BN_num_bits(limit),bytes=(bits+7)/8;
    if(bytes>32)return 0;memcpy(m,seed,32);
    do { uint64_t c=(*counter)++;for(int i=0;i<8;i++)m[39-i]=(unsigned char)(c>>(8*i));
        SHA256(m,40,h);h[0]&=(unsigned char)(0xff>>(8*bytes-bits));
        if(!BN_bin2bn(h,bytes,v))return 0;
    } while(BN_cmp(v,limit)>=0 || (nonzero && BN_is_zero(v)));
    return 1;
}
static int affine_draw(EC_GROUP *group,EC_POINT *q,const BIGNUM *p,const BIGNUM *a,const BIGNUM *b,
                       const unsigned char *seed,uint64_t *counter,BN_CTX *ctx) {
    BIGNUM *x,*y,*rhs,*tmp;int ok=0;BN_CTX_start(ctx);
    x=BN_CTX_get(ctx);y=BN_CTX_get(ctx);rhs=BN_CTX_get(ctx);tmp=BN_CTX_get(ctx);
    if(!tmp)goto done;
    for(;;) {
        if(!draw(x,p,seed,counter,0) || !BN_mod_sqr(rhs,x,p,ctx) || !BN_mod_mul(rhs,rhs,x,p,ctx) ||
           !BN_mod_mul(tmp,a,x,p,ctx) || !BN_mod_add(rhs,rhs,tmp,p,ctx) || !BN_mod_add(rhs,rhs,b,p,ctx))goto done;
        unsigned char m[40],h[32];memcpy(m,seed,32);uint64_t c=(*counter)++;
        for(int i=0;i<8;i++)m[39-i]=(unsigned char)(c>>(8*i));SHA256(m,40,h);int sign=h[0]&1;
        if(BN_is_zero(rhs)) {if(sign)continue;BN_zero(y);}
        else {if(!BN_mod_sqrt(y,rhs,p,ctx))continue;if(BN_is_odd(y)!=sign && !BN_sub(y,p,y))goto done;}
        ok=EC_POINT_set_affine_coordinates(group,q,x,y,ctx);break;
    }
done:BN_CTX_end(ctx);return ok;
}
static void score(const unsigned char *bits,uint32_t *out) {
    int counts[16]={0},parity=0,run=1,longest=1;
    for(int i=1;i<WINDOW;i++){run=(bits[i]==bits[i-1])?run+1:1;if(run>longest)longest=run;}
    for(int i=0;i<WINDOW-2;i++)parity+=(bits[i]^bits[i+1]^bits[i+2])?1:-1;
    for(int i=0;i<WINDOW-3;i++)counts[8*bits[i]+4*bits[i+1]+2*bits[i+2]+bits[i+3]]++;
    uint32_t squares=0;for(int i=0;i<16;i++)squares+=(uint32_t)counts[i]*counts[i];
    out[0]=(uint32_t)longest;out[1]=(uint32_t)(parity<0?-parity:parity);
    out[2]=16*squares-(WINDOW-3)*(WINDOW-3);
}
static int frame(FILE *file,uint64_t index,uint64_t start_before,uint64_t gen_before,uint32_t flags,
                 const unsigned char *r,int width,const unsigned char *raw,int cohorts) {
    unsigned char header[28];uint64_t values[3]={index,start_before,gen_before};
    for(int j=0;j<3;j++)for(int i=0;i<8;i++)header[8*j+i]=(unsigned char)(values[j]>>(8*i));
    for(int i=0;i<4;i++)header[24+i]=(unsigned char)(flags>>(8*i));
    return fwrite(header,1,28,file)==28 && fwrite(r,1,width,file)==(size_t)width &&
           fwrite(raw,1,(size_t)cohorts*WINDOW*2*width,file)==(size_t)cohorts*WINDOW*2*width;
}

/* named 1=P192, 2=P224; 0=ordinary-prime curve with a public step, not a certified generator.
   Cohorts for named curve: selected H, actual published G, new random rG.
   All named cohorts start at exactly the same uniform Q=kG for each window. */
int windows(const char *ps,const char *as,const char *bs,const char *ns,const char *hxs,const char *hys,
            int named,uint64_t count,uint32_t metric,uint32_t threshold,uint64_t max_event_frames,uint64_t event_limit_bytes,
            const unsigned char *starts,const unsigned char *generators,
            const char *event_path,const char *witness_path,const char *full_path,
            unsigned char *packed,uint32_t *scores,unsigned char *public_r,unsigned char *coordinate_hashes,
            uint64_t *used,uint64_t *checks) {
    int status=-1,width=0,cohorts=named?3:1;
    uint64_t sc=0,gc=0,oncurve=0,event_frames=0,event_bytes=0,extreme_frames=0;
    FILE *events=NULL,*witness=NULL,*full=NULL,*extreme=NULL;char *extreme_path=NULL;
    BN_CTX *ctx=BN_CTX_new();BIGNUM *p=decimal(ps),*a=decimal(as),*b=decimal(bs),*n=decimal(ns),*hx=decimal(hxs),*hy=decimal(hys);
    BIGNUM *k=BN_new(),*r=BN_new(),*x=BN_new(),*y=BN_new(),*cp=BN_new(),*ca=BN_new(),*cb=BN_new(),*cn=BN_new();
    EC_GROUP *group=NULL,*reference=NULL;EC_POINT *step[3]={NULL,NULL,NULL},*q=NULL,*tmp=NULL,*refq=NULL,*refh=NULL,*points[3*WINDOW]={NULL};
    unsigned char *raw=NULL;SHA256_CTX hashes[3];
    if(metric>2 || !count || !ctx || !p || !a || !b || !n || !hx || !hy || !k || !r || !x || !y || !cp || !ca || !cb || !cn)goto done;
    width=(BN_num_bits(p)+7)/8;
    group=EC_GROUP_new_curve_GFp(p,a,b,ctx);
    if(!group)goto done;
    if(named) {
        reference=EC_GROUP_new_by_curve_name(named==1?NID_X9_62_prime192v1:NID_secp224r1);
        if(!reference || !EC_GROUP_get_curve(reference,cp,ca,cb,ctx) || !EC_GROUP_get_order(reference,cn,ctx) ||
           BN_cmp(p,cp) || BN_cmp(a,ca) || BN_cmp(b,cb) || BN_cmp(n,cn))goto done;
        refq=EC_POINT_new(reference);refh=EC_POINT_new(reference);if(!refq || !refh)goto done;
    }
    q=EC_POINT_new(group);tmp=EC_POINT_new(group);
    for(int c=0;c<cohorts;c++){step[c]=EC_POINT_new(group);SHA256_Init(&hashes[c]);}
    if(!q || !tmp || !step[0] || !EC_POINT_set_affine_coordinates(group,step[0],hx,hy,ctx) || EC_POINT_is_on_curve(group,step[0],ctx)!=1)goto done;
    if(!EC_POINT_mul(group,tmp,NULL,step[0],n,ctx) || EC_POINT_is_at_infinity(group,tmp)!=1)goto done;
    if(named && (!step[1] || !step[2] || !EC_POINT_get_affine_coordinates(reference,EC_GROUP_get0_generator(reference),x,y,ctx) ||
       !EC_POINT_set_affine_coordinates(group,step[1],x,y,ctx) || !EC_GROUP_set_generator(group,step[1],n,BN_value_one())))goto done;
    for(int i=0;i<cohorts*WINDOW;i++){points[i]=EC_POINT_new(group);if(!points[i])goto done;}
    raw=malloc((size_t)cohorts*WINDOW*2*width);if(!raw)goto done;
    extreme_path=malloc(strlen(event_path)+9);if(!extreme_path)goto done;
    sprintf(extreme_path,"%s.extreme",event_path);
    events=fopen(event_path,"wbx");witness=fopen(witness_path,"wbx");extreme=fopen(extreme_path,"wbx");if(full_path)full=fopen(full_path,"wbx");
    if(!events || !witness || !extreme || (full_path && !full)){status=-5;goto done;}
    for(uint64_t w=0;w<count;w++) {
        uint64_t sb=sc,gb=gc;
        if(named) {
            if(!draw(k,n,starts,&sc,1) || !draw(r,n,generators,&gc,1) ||
               !EC_POINT_mul(reference,refq,k,NULL,NULL,ctx) || !EC_POINT_mul(reference,refh,r,NULL,NULL,ctx) ||
               !EC_POINT_get_affine_coordinates(reference,refq,x,y,ctx) || !EC_POINT_set_affine_coordinates(group,q,x,y,ctx) ||
               !EC_POINT_get_affine_coordinates(reference,refh,x,y,ctx) || !EC_POINT_set_affine_coordinates(group,step[2],x,y,ctx)){status=-2;goto done;}
            if(BN_bn2binpad(r,public_r+w*width,width)!=width){status=-2;goto done;}
        } else {
            if(!affine_draw(group,q,p,a,b,starts,&sc,ctx)){status=-2;goto done;}
            BN_zero(r);memset(public_r+w*width,0,width);
        }
        for(int c=0;c<cohorts;c++) {
            if(!EC_POINT_copy(points[c*WINDOW],q)){status=-2;goto done;}
            for(int i=1;i<WINDOW;i++)if(!EC_POINT_add(group,points[c*WINDOW+i],points[c*WINDOW+i-1],step[c],ctx)){status=-2;goto done;}
        }
        if(!EC_POINTs_make_affine(group,(size_t)cohorts*WINDOW,points,ctx)){status=-2;goto done;}
        uint32_t flags=0,extreme_flags=0;
        for(int c=0;c<cohorts;c++) {
            unsigned char bits[WINDOW];size_t offset=((size_t)w*cohorts+c)*32;memset(packed+offset,0,32);
            for(int i=0;i<WINDOW;i++) {
                EC_POINT *point=points[c*WINDOW+i];
                if(EC_POINT_is_at_infinity(group,point)){status=-3;goto done;}
                if(EC_POINT_is_on_curve(group,point,ctx)!=1){status=-4;goto done;}oncurve++;
                if(!EC_POINT_get_affine_coordinates(group,point,x,y,ctx)){status=-2;goto done;}
                unsigned char *dest=raw+(c*WINDOW+i)*2*width;
                if(BN_bn2binpad(x,dest,width)!=width || BN_bn2binpad(y,dest+width,width)!=width){status=-2;goto done;}
                bits[i]=(unsigned char)BN_is_bit_set(x,64);packed[offset+i/8]|=(unsigned char)(bits[i]<<(i%8));
            }
            uint32_t *s=scores+((size_t)w*cohorts+c)*3;score(bits,s);if(s[metric]>=threshold)flags|=1U<<c;
            if(s[0]>=28)extreme_flags|=1U<<c;
            SHA256_Update(&hashes[c],raw+c*WINDOW*2*width,(size_t)WINDOW*2*width);
        }
        const unsigned char *rp=public_r+w*width;
        if(flags && event_frames<max_event_frames) {
            uint64_t bytes=28+(uint64_t)width+(uint64_t)cohorts*WINDOW*2*width;
            if(bytes>event_limit_bytes || event_bytes>event_limit_bytes-bytes){status=-6;goto done;}
            if(!frame(events,w,sb,gb,flags,rp,width,raw,cohorts)){status=-5;goto done;}
            event_frames++;event_bytes+=bytes;
        }
        if(extreme_flags && extreme_frames<8) {
            if(!frame(extreme,w,sb,gb,extreme_flags,rp,width,raw,cohorts)){status=-5;goto done;}
            extreme_frames++;
        }
        if((w<2 || w==count/2 || w==count-1) && !frame(witness,w,sb,gb,flags,rp,width,raw,cohorts)){status=-5;goto done;}
        if(full && fwrite(raw,1,(size_t)cohorts*WINDOW*2*width,full)!=(size_t)cohorts*WINDOW*2*width){status=-5;goto done;}
    }
    for(int c=0;c<cohorts;c++)SHA256_Final(coordinate_hashes+32*c,&hashes[c]);
    used[0]=sc;used[1]=gc;*checks=oncurve;status=1;
done:
    used[0]=sc;used[1]=gc;*checks=oncurve;
    if(extreme && fclose(extreme) && status==1)status=-5;free(extreme_path);
    if(events && fclose(events) && status==1)status=-5;if(witness && fclose(witness) && status==1)status=-5;if(full && fclose(full) && status==1)status=-5;
    free(raw);for(int i=0;i<3*WINDOW;i++)EC_POINT_free(points[i]);for(int c=0;c<3;c++)EC_POINT_free(step[c]);EC_POINT_free(q);EC_POINT_free(tmp);EC_POINT_free(refq);EC_POINT_free(refh);EC_GROUP_free(group);EC_GROUP_free(reference);
    BN_free(p);BN_free(a);BN_free(b);BN_free(n);BN_free(hx);BN_free(hy);BN_free(k);BN_free(r);BN_free(x);BN_free(y);BN_free(cp);BN_free(ca);BN_free(cb);BN_free(cn);BN_CTX_free(ctx);return status;
}
