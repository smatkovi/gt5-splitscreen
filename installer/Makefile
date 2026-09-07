# GT5 3P/4P split-screen installer - PS3 homebrew package
#
#   make VARIANT=4p            build the installer self only (no payload)
#   make VARIANT=4p pkg        wrap it into a .pkg, including whatever is staged
#                              under build/<variant>/pkg/USRDIR/payload
#
# The payload (patched EBOOT.BIN + PDIPFS overlay) is never in this repository.
# installer/build_pkg.sh stages it from the user's own copy of the game.

ifeq ($(PSL1GHT),)
  $(error PSL1GHT is not set - source your ps3dev environment)
endif

VARIANT ?= 4p
ifeq ($(VARIANT),4p)
  APPID    := GT5SPLT4
  VARNAME  := 4P
else ifeq ($(VARIANT),3p)
  APPID    := GT5SPLT3
  VARNAME  := 3P
else
  $(error VARIANT must be 3p or 4p)
endif

TITLE     := GT5 $(VARNAME) Split Screen Installer
CONTENTID := UP0001-$(APPID)_00-0000000000000000
SELF_DIR  := /dev_hdd0/game/$(APPID)/USRDIR

BUILD := build/$(VARIANT)
PKGDIR := $(BUILD)/pkg

CC       := $(PSL1GHT)/ppu/bin/ppu-gcc
STRIP    := $(PSL1GHT)/ppu/bin/ppu-strip
SPRX     := sprxlinker
SELF_NPDRM := make_self_npdrm
SFO      := sfo.py
PKG      := pkg.py
PACKAGE_FINALIZE := package_finalize
PYTHON   ?= python
SFOXML   := $(PSL1GHT)/bin/sfo.xml

SRC := source/main.c source/md5.c
OBJ := $(SRC:source/%.c=$(BUILD)/%.o)

CFLAGS := -O2 -Wall -Wextra -mcpu=cell \
          -I$(PSL1GHT)/ppu/include -Isource \
          -DVARIANT=\"$(VARNAME)\" -DSELF_DIR=\"$(SELF_DIR)\"
LDFLAGS := -mcpu=cell -L$(PSL1GHT)/ppu/lib -lrsx -lgcm_sys -lsysutil -lio -lrt -llv2 -lm

TARGET := $(BUILD)/installer.elf
PKGFILE := gt5-$(VARIANT)-installer.pkg

.PHONY: all pkg clean
all: $(TARGET)

$(BUILD)/%.o: source/%.c
	@mkdir -p $(dir $@)
	@echo "  CC   $<"
	@$(CC) $(CFLAGS) -c $< -o $@

$(TARGET): $(OBJ)
	@echo "  LINK $@"
	@$(CC) -o $@ $^ $(LDFLAGS)

pkg: $(PKGFILE)

$(PKGFILE): $(TARGET)
	@echo "  SELF $@"
	@$(STRIP) $(TARGET) -o $(BUILD)/installer_stripped.elf
	@$(SPRX) $(BUILD)/installer_stripped.elf
	@$(SELF_NPDRM) $(BUILD)/installer_stripped.elf $(BUILD)/EBOOT.BIN $(CONTENTID)
	@mkdir -p $(PKGDIR)/USRDIR
	@cp $(BUILD)/EBOOT.BIN $(PKGDIR)/USRDIR/
	@$(SFO) --title "$(TITLE)" --appid "$(APPID)" -f $(SFOXML) $(PKGDIR)/PARAM.SFO
	@$(PKG) --contentid $(CONTENTID) $(PKGDIR)/ $@
	@$(PACKAGE_FINALIZE) $@
	@echo "  DONE $@"

clean:
	rm -rf build gt5-3p-installer.pkg gt5-4p-installer.pkg
