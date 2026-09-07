/* GT5 3P/4P split-screen installer for PS3 (CFW/HEN).
 *
 * Replaces the EBOOT.BIN of the Gran Turismo 5 2.17 update with a patched one and
 * copies the Adhoc script overlay into PDIPFS. The patched EBOOT is NOT shipped with
 * this program: it is built on the user's own machine from the user's own copy of the
 * game (see installer/build_pkg.sh) and injected into this package at that point.
 *
 * The original EBOOT.BIN is kept as EBOOT.BIN.orig, every overwritten PDIPFS file as
 * <name>.orig, so "Restore" puts the console back exactly as it was.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <dirent.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <malloc.h>

#include <ppu-types.h>
#include <rsx/rsx.h>
#include <sysutil/video.h>
#include <sysutil/sysutil.h>
#include <sysutil/msg.h>
#include <sys/process.h>

#include "md5.h"

SYS_PROCESS_PARAM(1001, 0x100000);

#ifndef VARIANT
#define VARIANT "4P"
#endif
#ifndef SELF_DIR
#define SELF_DIR "/dev_hdd0/game/GT5SPLIT/USRDIR"
#endif

#define GAME_DIR  "/dev_hdd0/game/BCES00569/USRDIR"
#define EBOOT     GAME_DIR "/EBOOT.BIN"
#define EBOOT_BAK GAME_DIR "/EBOOT.BIN.orig"
#define PDIPFS    GAME_DIR "/PDIPFS"

/* Unmodified EBOOT.BIN of the Gran Turismo 5 2.17 update (BCES00569), 9505120 bytes. */
#define ORIG_MD5  "a8924d1fdca785acab26ee7854bd650a"

#define COPY_CHUNK (512 * 1024)
#define PATH_MAX_  1024

/* ------------------------------------------------------------------ video --
 * The system message dialogs draw on top of the application's framebuffer, so the
 * program needs a video output and has to keep flipping while a dialog is up.
 * Nothing is rendered beyond a flat background, which the CPU writes directly.
 */

#define FB_COUNT 2

static gcmContextData *ctx;
static void *host_buf;
static u32 *fb[FB_COUNT];
static videoResolution vres;
static u32 cur_fb;
static int first_flip = 1;

static int video_start(void) {
    static const u32 modes[] = { VIDEO_RESOLUTION_720, VIDEO_RESOLUTION_480,
                                 VIDEO_RESOLUTION_576, VIDEO_RESOLUTION_1080 };
    u32 i, pitch, ofs;

    host_buf = memalign(1024 * 1024, 32 * 1024 * 1024);
    if (!host_buf) return -1;
    if (rsxInit(&ctx, 0x10000, 32 * 1024 * 1024, host_buf) < 0) return -1;

    for (i = 0; i < sizeof(modes) / sizeof(modes[0]); ++i) {
        videoConfiguration cfg;
        if (videoGetResolutionAvailability(VIDEO_PRIMARY, modes[i], VIDEO_ASPECT_AUTO, 0) != 1)
            continue;
        if (videoGetResolution(modes[i], &vres) != 0) continue;
        memset(&cfg, 0, sizeof(cfg));
        cfg.resolution = (u8)modes[i];
        cfg.format     = VIDEO_BUFFER_FORMAT_XRGB;
        cfg.aspect     = VIDEO_ASPECT_AUTO;
        cfg.pitch      = vres.width * 4;
        if (videoConfigure(VIDEO_PRIMARY, &cfg, NULL, 0) == 0) break;
    }
    if (i == sizeof(modes) / sizeof(modes[0])) return -1;

    pitch = vres.width * 4;
    for (i = 0; i < FB_COUNT; ++i) {
        fb[i] = (u32 *)rsxMemalign(64, vres.height * pitch);
        if (!fb[i]) return -1;
        rsxAddressToOffset(fb[i], &ofs);
        gcmSetDisplayBuffer(i, ofs, pitch, vres.width, vres.height);
        /* flat dark background */
        { u32 n = vres.width * vres.height, k; for (k = 0; k < n; ++k) fb[i][k] = 0xff101418; }
    }
    gcmSetFlipMode(GCM_FLIP_VSYNC);
    return 0;
}

static void flip(void) {
    if (first_flip) { gcmResetFlipStatus(); first_flip = 0; }
    else {
        u32 guard = 0;
        while (gcmGetFlipStatus() && ++guard < 50000) usleep(200);
        gcmResetFlipStatus();
    }
    gcmSetFlip(ctx, cur_fb);
    rsxFlushBuffer(ctx);
    gcmSetWaitFlip(ctx);
    cur_fb ^= 1;
}

/* ----------------------------------------------------------------- dialogs -- */

static volatile int dlg_open;
static volatile msgButton dlg_btn;

static void dlg_cb(msgButton button, void *user) {
    (void)user;
    dlg_btn = button;
    dlg_open = 0;
}

static msgButton ask(msgType type, const char *text) {
    dlg_open = 1;
    dlg_btn = MSG_DIALOG_BTN_NONE;
    if (msgDialogOpen2(type, text, dlg_cb, NULL, NULL) < 0) return MSG_DIALOG_BTN_ESCAPE;
    while (dlg_open) {
        sysUtilCheckCallback();
        flip();
    }
    msgDialogAbort();
    return dlg_btn;
}

static void say(const char *text) {
    ask(MSG_DIALOG_NORMAL | MSG_DIALOG_BTN_TYPE_OK | MSG_DIALOG_DISABLE_CANCEL_ON, text);
}

static void die(const char *text) {
    ask(MSG_DIALOG_ERROR | MSG_DIALOG_BTN_TYPE_OK | MSG_DIALOG_DISABLE_CANCEL_ON, text);
    exit(0);
}

static int confirm(const char *text) {
    return ask(MSG_DIALOG_NORMAL | MSG_DIALOG_BTN_TYPE_YESNO, text) == MSG_DIALOG_BTN_YES;
}

/* -------------------------------------------------------------------- files -- */

static int file_exists(const char *path) {
    struct stat st;
    return stat(path, &st) == 0 && S_ISREG(st.st_mode);
}

static int dir_exists(const char *path) {
    struct stat st;
    return stat(path, &st) == 0 && S_ISDIR(st.st_mode);
}

/* md5 of a file; returns 0 on success and writes 32 hex chars + NUL */
static int file_md5(const char *path, char out[33]) {
    FILE *f = fopen(path, "rb");
    unsigned char digest[16];
    char *buf;
    md5_ctx c;
    size_t n;

    if (!f) return -1;
    buf = (char *)malloc(COPY_CHUNK);
    if (!buf) { fclose(f); return -1; }

    md5_init(&c);
    while ((n = fread(buf, 1, COPY_CHUNK, f)) > 0) md5_update(&c, buf, (unsigned int)n);
    md5_final(&c, digest);
    md5_hex(digest, out);

    free(buf);
    fclose(f);
    return 0;
}

static int copy_file(const char *src, const char *dst) {
    FILE *in = fopen(src, "rb");
    FILE *out;
    char *buf;
    size_t n;
    int ok = 0;

    if (!in) return -1;
    out = fopen(dst, "wb");
    if (!out) { fclose(in); return -1; }
    buf = (char *)malloc(COPY_CHUNK);
    if (!buf) { fclose(in); fclose(out); return -1; }

    for (;;) {
        n = fread(buf, 1, COPY_CHUNK, in);
        if (n == 0) { ok = feof(in) ? 0 : -1; break; }
        if (fwrite(buf, 1, n, out) != n) { ok = -1; break; }
    }
    free(buf);
    fclose(in);
    if (fclose(out) != 0) ok = -1;
    return ok;
}

static void mkdirs(const char *path) {
    char tmp[PATH_MAX_];
    char *p;
    size_t len = strlen(path);
    if (len >= sizeof(tmp)) return;
    strcpy(tmp, path);
    for (p = tmp + 1; *p; ++p) {
        if (*p == '/') { *p = 0; mkdir(tmp, 0777); *p = '/'; }
    }
    mkdir(tmp, 0777);
}

/* Path joining with an explicit bound: PDIPFS names are short, but the recursion
   means the compiler cannot prove it, and a silently truncated path would be worse
   than a skipped file. */
static int join(char *out, size_t n, const char *a, const char *sep, const char *b) {
    size_t la = strlen(a), ls = strlen(sep), lb = strlen(b);
    if (la + ls + lb + 1 > n) return -1;
    memcpy(out, a, la);
    memcpy(out + la, sep, ls);
    memcpy(out + la + ls, b, lb);
    out[la + ls + lb] = 0;
    return 0;
}

static void mkparent(const char *path) {
    char parent[PATH_MAX_];
    char *slash;
    if (strlen(path) >= sizeof(parent)) return;
    strcpy(parent, path);
    slash = strrchr(parent, '/');
    if (slash) { *slash = 0; mkdirs(parent); }
}

/* Copy payload/pdipfs/<rel> over PDIPFS/<rel>, keeping one .orig backup per file.
   Returns the number of files copied, or -1 on the first failure. */
static int copy_overlay(const char *src_root, const char *dst_root, const char *rel) {
    char dir[PATH_MAX_], src[PATH_MAX_], dst[PATH_MAX_], bak[PATH_MAX_], sub[PATH_MAX_];
    DIR *d;
    struct dirent *e;
    int count = 0;

    if (join(dir, sizeof(dir), src_root, rel[0] ? "/" : "", rel) != 0) return -1;
    d = opendir(dir);
    if (!d) return 0;

    while ((e = readdir(d)) != NULL) {
        struct stat st;
        if (e->d_name[0] == '.' && (e->d_name[1] == 0 ||
            (e->d_name[1] == '.' && e->d_name[2] == 0))) continue;

        if (join(sub, sizeof(sub), rel, rel[0] ? "/" : "", e->d_name) != 0 ||
            join(src, sizeof(src), src_root, "/", sub) != 0 ||
            join(dst, sizeof(dst), dst_root, "/", sub) != 0 ||
            join(bak, sizeof(bak), dst, "", ".orig") != 0) { closedir(d); return -1; }

        if (stat(src, &st) != 0) continue;

        if (S_ISDIR(st.st_mode)) {
            int sub_count = copy_overlay(src_root, dst_root, sub);
            if (sub_count < 0) { closedir(d); return -1; }
            count += sub_count;
            continue;
        }

        /* back up the untouched original exactly once */
        if (file_exists(dst) && !file_exists(bak) && copy_file(dst, bak) != 0) {
            closedir(d); return -1;
        }
        mkparent(dst);
        if (copy_file(src, dst) != 0) { closedir(d); return -1; }
        ++count;
    }
    closedir(d);
    return count;
}

static int restore_overlay(const char *dst_root, const char *rel) {
    char dir[PATH_MAX_], path[PATH_MAX_], bak[PATH_MAX_], sub[PATH_MAX_];
    DIR *d;
    struct dirent *e;
    int count = 0;

    if (join(dir, sizeof(dir), dst_root, rel[0] ? "/" : "", rel) != 0) return 0;
    d = opendir(dir);
    if (!d) return 0;

    while ((e = readdir(d)) != NULL) {
        struct stat st;
        size_t len;
        if (e->d_name[0] == '.' && (e->d_name[1] == 0 ||
            (e->d_name[1] == '.' && e->d_name[2] == 0))) continue;

        if (join(sub, sizeof(sub), rel, rel[0] ? "/" : "", e->d_name) != 0 ||
            join(path, sizeof(path), dst_root, "/", sub) != 0) continue;
        if (stat(path, &st) != 0) continue;
        if (S_ISDIR(st.st_mode)) { count += restore_overlay(dst_root, sub); continue; }

        len = strlen(path);
        if (len > 5 && strcmp(path + len - 5, ".orig") == 0) {
            memcpy(bak, path, len + 1);
            path[len - 5] = 0;
            if (copy_file(bak, path) == 0) { remove(bak); ++count; }
        }
    }
    closedir(d);
    return count;
}

/* --------------------------------------------------------------------- main -- */

static void do_restore(void) {
    char md5[33];
    int n;

    if (!file_exists(EBOOT_BAK))
        die("No backup found.\n\n" GAME_DIR "/EBOOT.BIN.orig does not exist,\n"
            "so there is nothing to restore. If the game is broken, reinstall\n"
            "the Gran Turismo 5 2.17 update from the PlayStation Store.");

    if (file_md5(EBOOT_BAK, md5) != 0) die("Cannot read the backup EBOOT.BIN.orig.");
    if (strcmp(md5, ORIG_MD5) != 0)
        die("The backup EBOOT.BIN.orig is not the original 2.17 EBOOT.\n"
            "Refusing to restore it. Reinstall the 2.17 update instead.");

    if (copy_file(EBOOT_BAK, EBOOT) != 0) die("Could not write " EBOOT ".");
    remove(EBOOT_BAK);
    n = restore_overlay(PDIPFS, "");

    { char msg[512];
      snprintf(msg, sizeof(msg),
               "Restored.\n\nEBOOT.BIN is the original 2.17 again and %d PDIPFS\n"
               "file(s) were put back. Gran Turismo 5 is unmodified.", n);
      say(msg); }
}

static void do_install(void) {
    char src_eboot[512], src_pdipfs[512];
    char cur[33], want[33], got[33], msg[768];
    int copied;

    snprintf(src_eboot, sizeof(src_eboot), "%s/payload/EBOOT.BIN", SELF_DIR);
    snprintf(src_pdipfs, sizeof(src_pdipfs), "%s/payload/pdipfs", SELF_DIR);

    if (!file_exists(src_eboot))
        die("This package carries no patched EBOOT.\n\n"
            "The patched EBOOT is not distributed. Build the package yourself\n"
            "from your own copy of the game with installer/build_pkg.sh,\n"
            "then install that package.");

    if (!dir_exists(GAME_DIR))
        die("Gran Turismo 5 (BCES00569) is not installed on the internal drive.\n\n"
            "Expected " GAME_DIR ".\n"
            "Install the game update 2.17 first.");

    if (!file_exists(EBOOT)) die("Not found: " EBOOT);
    if (file_md5(EBOOT, cur) != 0) die("Cannot read " EBOOT ".");

    if (strcmp(cur, ORIG_MD5) == 0) {
        /* untouched game: keep the original before replacing it */
        if (!file_exists(EBOOT_BAK) && copy_file(EBOOT, EBOOT_BAK) != 0)
            die("Could not write the backup " EBOOT_BAK ".");
    } else {
        /* already modified: only proceed if a genuine original is safely backed up */
        char bak[33];
        if (!file_exists(EBOOT_BAK) || file_md5(EBOOT_BAK, bak) != 0 || strcmp(bak, ORIG_MD5) != 0) {
            snprintf(msg, sizeof(msg),
                     "Unexpected EBOOT.BIN.\n\n"
                     "Found md5 %s,\nexpected  %s\n(Gran Turismo 5 update 2.17).\n\n"
                     "Either the update is not 2.17, or the game was modified without\n"
                     "a backup. Reinstall update 2.17, then run this installer again.",
                     cur, ORIG_MD5);
            die(msg);
        }
        if (!confirm("A modified EBOOT.BIN is already installed.\n\n"
                     "Replace it with the " VARIANT " version?"))
            return;
    }

    if (file_md5(src_eboot, want) != 0) die("Cannot read the patched EBOOT from this package.");
    if (copy_file(src_eboot, EBOOT) != 0) die("Could not write " EBOOT ".\nIs Gran Turismo 5 still running?");
    if (file_md5(EBOOT, got) != 0 || strcmp(got, want) != 0)
        die("The EBOOT was written but does not read back correctly.\n"
            "The drive may be full. Restore the original with this installer.");

    copied = copy_overlay(src_pdipfs, PDIPFS, "");
    if (copied < 0)
        die("EBOOT.BIN was replaced, but the PDIPFS script overlay could not be\n"
            "written. The game would run with mismatched scripts - use Restore.");

    snprintf(msg, sizeof(msg),
             "Installed: Gran Turismo 5 " VARIANT " split screen.\n\n"
             "EBOOT.BIN replaced (backup: EBOOT.BIN.orig)\n"
             "%d PDIPFS file(s) copied\n\n"
             "Start the game from the XMB, then:\n"
             "Arcade -> 2P Split Screen -> track -> cars,\n"
             "then answer the extra player prompts with Yes.\n\n"
             "Run this installer again to restore the original.",
             copied);
    say(msg);
}

int main(void) {
    if (video_start() != 0) return 1;

    if (!confirm("Gran Turismo 5 - " VARIANT " split screen\n\n"
                 "This replaces EBOOT.BIN of BCES00569 (update 2.17) and copies\n"
                 "a script overlay into PDIPFS. The original files are backed up.\n\n"
                 "Install now?\n"
                 "(No = restore the original files)")) {
        do_restore();
        return 0;
    }
    do_install();
    return 0;
}
