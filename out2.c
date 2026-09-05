////////////////////////////////////////////////////////////////
// WindowMgr_initDefault @ 0045f340  size=52
// callers: FUN_003b5b3c@003b5b3c FUN_0045f430@0045f430 FUN_003b5798@003b5798 Organizer_initA@0016e984 
// callees: FUN_00467654@00467654 

void WindowMgr_initDefault(int param_1,undefined8 param_2,int param_3)

{
  FUN_00467654(*(undefined4 *)(param_1 + param_3 * 8 + 0x1c));
  return;
}


////////////////////////////////////////////////////////////////
// WindowMgr_afterSetup @ 0045f890  size=84
// callers: WindowMgr_setupWindows@0046058c FUN_001799bc@001799bc 
// callees: FUN_004657d8@004657d8 

void WindowMgr_afterSetup(int param_1)

{
  bool bVar1;
  int iVar2;
  
  iVar2 = 0;
  do {
    FUN_004657d8(*(undefined4 *)(param_1 + iVar2 + 0x1c),0);
    bVar1 = iVar2 != 8;
    iVar2 = iVar2 + 8;
  } while (bVar1);
  return;
}


////////////////////////////////////////////////////////////////
// WindowMgr_fn_45f8e4 @ 0045f8e4  size=84
// callers: FUN_001799bc@001799bc 
// callees: FUN_004657d8@004657d8 

void WindowMgr_fn_45f8e4(int param_1)

{
  bool bVar1;
  int iVar2;
  
  iVar2 = 0;
  do {
    FUN_004657d8(*(undefined4 *)(param_1 + iVar2 + 0x1c),1);
    bVar1 = iVar2 != 8;
    iVar2 = iVar2 + 8;
  } while (bVar1);
  return;
}


////////////////////////////////////////////////////////////////
// 00460270: no function (creating)
// WindowMgr_fn_460270 @ 00460270  size=1
// callers: 
// callees: 

void WindowMgr_fn_460270(int param_1)

{
  bool bVar1;
  undefined4 uVar2;
  int iVar3;
  undefined4 *puVar4;
  
  iVar3 = 0;
  puVar4 = (undefined4 *)(param_1 + 0x1c);
  do {
    func_0x00466114(*puVar4);
    func_0x004659e4(*puVar4,0x400);
    uVar2 = *puVar4;
    puVar4 = puVar4 + 2;
    func_0x004659e4(uVar2,2);
    bVar1 = iVar3 != 1;
    iVar3 = iVar3 + 1;
  } while (bVar1);
  return;
}


////////////////////////////////////////////////////////////////
// WindowMgr_fn_4601b0 @ 004601b0  size=192
// callers: FUN_0036c6c4@0036c6c4 WindowLoopA@002284f8 WindowLoopB@00229310 
// callees: FUN_0045f2c0@0045f2c0 

undefined8 WindowMgr_fn_4601b0(int param_1,int param_2,int param_3)

{
  bool bVar1;
  int iVar2;
  undefined8 uVar3;
  int iVar4;
  int *piVar5;
  byte in_cr0;
  byte in_cr1;
  byte in_cr2;
  byte in_cr3;
  byte unaff_cr4;
  byte in_cr5;
  byte in_cr6;
  byte in_cr7;
  uint uStack00000008;
  
  uStack00000008 =
       (uint)(in_cr0 & 0xf) << 0x1c | (uint)(in_cr1 & 0xf) << 0x18 | (uint)(in_cr2 & 0xf) << 0x14 |
       (uint)(in_cr3 & 0xf) << 0x10 | (uint)(unaff_cr4 & 0xf) << 0xc | (uint)(in_cr5 & 0xf) << 8 |
       (uint)(in_cr6 & 0xf) << 4 | (uint)(in_cr7 & 0xf);
  piVar5 = (int *)(param_1 + 0x1c);
  uVar3 = 0;
  iVar4 = 0;
  do {
    iVar2 = *piVar5;
    piVar5 = piVar5 + 2;
    if (*(char *)(iVar2 + 0xc) != '\0') {
      if (((param_3 < 0) || (param_3 == iVar4)) &&
         (iVar2 = FUN_0045f2c0(param_1,iVar4), iVar2 == param_2)) {
        uVar3 = 1;
      }
    }
    bVar1 = iVar4 != 1;
    iVar4 = iVar4 + 1;
  } while (bVar1);
  return uVar3;
}


////////////////////////////////////////////////////////////////
// 0045f544: no function (creating)
// WindowMgr_fn_45f544 @ 0045f544  size=1
// callers: 
// callees: 

void WindowMgr_fn_45f544(undefined8 param_1,ulonglong param_2)

{
  bool bVar1;
  char cVar2;
  int iVar3;
  undefined1 auStack_50 [56];
  
  cVar2 = FUN_00c4e3c0();
  if (cVar2 == '\0') {
    cVar2 = FUN_0045f294(param_1);
    if (((cVar2 == '\0') && (cVar2 = FUN_0045f28c(param_1), cVar2 == '\0')) &&
       ((param_2 & 0xffffffff) < 0x16)) {
                    /* WARNING: Could not recover jumptable at 0x0045f6c4. Too many branches */
                    /* WARNING: Treating indirect jump as call */
      (*(code *)(&UNK_0045f6c8 + *(int *)(&UNK_0045f6c8 + (int)(param_2 << 2))))();
      return;
    }
  }
  else if ((param_2 & 0xffffffff) < 0x16) {
                    /* WARNING: Could not recover jumptable at 0x0045f59c. Too many branches */
                    /* WARNING: Treating indirect jump as call */
    (*(code *)(&UNK_0045f5a0 + *(int *)(&UNK_0045f5a0 + (int)(param_2 << 2))))();
    return;
  }
  iVar3 = 0;
  do {
    WindowMgr_initDefault(param_1,auStack_50,iVar3);
    bVar1 = iVar3 != 1;
    iVar3 = iVar3 + 1;
  } while (bVar1);
  return;
}


////////////////////////////////////////////////////////////////
// caller_disableAll @ 00175ad8  size=1252
// callers: 
// callees: FUN_007558d8@007558d8 FUN_00428ed8@00428ed8 FUN_0017fbec@0017fbec FUN_0017a000@0017a000 WindowMgr_disableAllWindows@00460868 FUN_00182f88@00182f88 FUN_00235688@00235688 FUN_0045fde8@0045fde8 FUN_00bfd3a8@00bfd3a8 FUN_001798c8@001798c8 FUN_0048e358@0048e358 FUN_0016c2dc@0016c2dc FUN_00bbcc84@00bbcc84 FUN_0036c3b4@0036c3b4 FUN_00c3d724@00c3d724 FUN_0039d530@0039d530 

void caller_disableAll(int param_1)

{
  bool bVar1;
  undefined4 *puVar2;
  int *piVar3;
  int iVar4;
  int iVar5;
  undefined1 uStack_70;
  undefined1 uStack_6f;
  undefined1 auStack_6e [14];
  
  piVar3 = *(int **)(param_1 + 0xa78);
  if (piVar3 != (int *)0x0) {
    (*(code *)**(undefined4 **)(*piVar3 + 4))(piVar3);
  }
  *(undefined4 *)(param_1 + 0xa78) = 0;
  FUN_0017a000(&UNK_00032b58 + param_1);
  iVar4 = *(int *)(&DAT_00018d00 + param_1);
  if (iVar4 != 0) {
    FUN_0017fbec(iVar4);
    FUN_00bbcc84(iVar4);
  }
  iVar4 = *(int *)(param_1 + 0xae4);
  *(undefined4 *)(&DAT_00018d00 + param_1) = 0;
  if (iVar4 != 0) {
    FUN_0036c3b4(iVar4);
    FUN_00bbcc84(iVar4);
  }
  iVar4 = *(int *)(param_1 + 0xae0);
  *(undefined4 *)(param_1 + 0xae4) = 0;
  if (iVar4 != 0) {
    FUN_0016c2dc(iVar4);
    FUN_00bbcc84(iVar4);
  }
  iVar4 = *(int *)(param_1 + 0xa6c);
  *(undefined4 *)(param_1 + 0xae0) = 0;
  if (iVar4 != 0) {
    FUN_0039d530(iVar4);
    FUN_00bbcc84(iVar4);
    *(undefined4 *)(param_1 + 0xa6c) = 0;
  }
  piVar3 = *(int **)(&DAT_00018620 + param_1);
  if (piVar3 != (int *)0x0) {
    (*(code *)**(undefined4 **)(*piVar3 + 4))(piVar3);
    *(undefined4 *)(&DAT_00018620 + param_1) = 0;
  }
  FUN_00c3d724(auStack_6e,*(undefined4 *)(param_1 + 0xadc));
  *(undefined4 *)(param_1 + 0xadc) = 0;
  FUN_00c3d724(&uStack_6f,*(undefined4 *)(param_1 + 0xad8));
  *(undefined4 *)(param_1 + 0xad8) = 0;
  FUN_00c3d724(&uStack_70,*(undefined4 *)(param_1 + 0xad4));
  *(undefined4 *)(param_1 + 0xad4) = 0;
  FUN_0045fde8(param_1 + 0xa90);
  WindowMgr_disableAllWindows(param_1 + 0xa90);
  FUN_007558d8(&UNK_00032a38 + param_1);
  FUN_00bfd3a8(param_1 + 0xa7c);
  FUN_001798c8(&UNK_00018d10 + param_1);
  FUN_00235688(&UNK_00018d40 + param_1);
  FUN_00bfd3a8(param_1 + 0xae8);
  piVar3 = *(int **)(param_1 + 0xa70);
  if (piVar3 != (int *)0x0) {
    *(undefined4 *)(param_1 + 0xa70) = 0;
    (*(code *)**(undefined4 **)(*piVar3 + 4))(piVar3);
  }
  iVar5 = 0;
  iVar4 = param_1 + 0x2b8;
  do {
    FUN_0048e358(iVar4,param_1 + 0x270);
    bVar1 = iVar5 != 1;
    iVar5 = iVar5 + 1;
    iVar4 = iVar4 + 0x290;
  } while (bVar1);
  *(undefined4 *)(param_1 + 0x60) = 0;
  *(undefined1 *)(param_1 + 0x268) = 0;
  *(undefined1 *)(param_1 + 0x269) = 0;
  *(undefined1 *)(param_1 + 0x26a) = 0;
  (*(code *)**(undefined4 **)(**(int **)(param_1 + 0xa0) + 0x34))(*(int **)(param_1 + 0xa0),0);
  (*(code *)**(undefined4 **)(**(int **)(param_1 + 0x9c) + 0x34))(*(int **)(param_1 + 0x9c),0);
  iVar4 = *(int *)(param_1 + 0xa4);
  if (iVar4 != 0) {
    FUN_00428ed8(iVar4);
    FUN_00bbcc84(iVar4);
  }
  piVar3 = (int *)(&UNK_00032b28 + param_1);
  iVar4 = 0;
  *(undefined4 *)(param_1 + 0xa4) = 0;
  do {
    if (*piVar3 != 0) {
      puVar2 = (undefined4 *)piVar3[1];
      if (puVar2 != (undefined4 *)0x0) {
        (*(code *)**(undefined4 **)*puVar2)(puVar2,*piVar3);
        piVar3[1] = 0;
        *piVar3 = 0;
      }
      *piVar3 = 0;
      if (DAT_01941110 == '\0') {
        DAT_01941118 = &PTR_PTR_LAB_016c4c08;
        DAT_01941110 = '\x01';
      }
      piVar3[1] = (int)&DAT_01941118;
    }
    bVar1 = iVar4 != 3;
    piVar3 = piVar3 + 2;
    iVar4 = iVar4 + 1;
  } while (bVar1);
  piVar3 = (int *)(&DAT_00034e80 + param_1);
  if (*piVar3 != 0) {
    puVar2 = *(undefined4 **)(&DAT_00034e84 + param_1);
    if (puVar2 != (undefined4 *)0x0) {
      (*(code *)**(undefined4 **)*puVar2)(puVar2,*piVar3);
      *piVar3 = 0;
      *(undefined4 *)(&DAT_00034e84 + param_1) = 0;
    }
    *piVar3 = 0;
    if (DAT_01941108 == '\0') {
      DAT_0194111c = &PTR_PTR_LAB_016c4c50;
      DAT_01941108 = '\x01';
    }
    *(undefined ****)(&DAT_00034e84 + param_1) = &DAT_0194111c;
  }
  (*(code *)**(undefined4 **)(**(int **)(param_1 + 0xa0) + 0x10))(*(int **)(param_1 + 0xa0));
  (*(code *)**(undefined4 **)**(undefined4 **)(param_1 + 0xa0))(*(undefined4 **)(param_1 + 0xa0));
  (*(code *)**(undefined4 **)(**(int **)(param_1 + 0x9c) + 0x10))(*(int **)(param_1 + 0x9c));
  (*(code *)**(undefined4 **)**(undefined4 **)(param_1 + 0x9c))(*(undefined4 **)(param_1 + 0x9c));
  FUN_00182f88(param_1);
  return;
}


////////////////////////////////////////////////////////////////
// RaceDisp_getSlotVal @ 002381a8  size=28
// callers: FUN_0023863c@0023863c 
// callees: 

undefined4 RaceDisp_getSlotVal(int param_1,int param_2)

{
  return *(undefined4 *)(param_1 + param_2 * 0x5bc + 0x5fc);
}


////////////////////////////////////////////////////////////////
// 002380f0: no function (creating)
// RaceDisp_slotInit @ 002380f0  size=1
// callers: 
// callees: 

void RaceDisp_slotInit(undefined2 *param_1)

{
  *(undefined1 *)(param_1 + 0xde) = 0;
  *(undefined4 *)(param_1 + 10) = 0;
  *param_1 = 0;
  *(undefined1 *)(param_1 + 1) = 0;
  *(undefined4 *)(param_1 + 4) = 0;
  param_1[6] = 0;
  param_1[7] = 0;
  param_1[0xc] = 0;
  *(undefined1 *)((int)param_1 + 0x1af) = 0;
  *(undefined1 *)(param_1 + 0xd8) = 0;
  *(undefined1 *)(param_1 + 0xce) = 0;
  return;
}


////////////////////////////////////////////////////////////////
// Window_disable @ 00465b6c  size=204
// callers: WindowMgr_disableAllWindows@00460868 
// callees: 

void Window_disable(int param_1)

{
  bool bVar1;
  int *piVar2;
  int iVar3;
  int iVar4;
  
  iVar4 = 0;
  iVar3 = 0xd970;
  do {
    piVar2 = *(int **)(*(int *)(param_1 + 4) + iVar3);
    (*(code *)**(undefined4 **)(*piVar2 + 0xc))(piVar2);
    bVar1 = iVar4 != 0xf;
    iVar4 = iVar4 + 1;
    iVar3 = iVar3 + 4;
  } while (bVar1);
  piVar2 = (int *)(param_1 + 4);
  *(undefined4 *)(*piVar2 + 0xd9b0) = *(undefined4 *)(*piVar2 + 0xd970);
  *(undefined4 *)(*(int *)(param_1 + 4) + 0xda10) = 0xffffffff;
  *(undefined4 *)(*piVar2 + 0xe558) = 0;
  *(undefined1 *)(*piVar2 + 0xe424) = 0;
  return;
}


////////////////////////////////////////////////////////////////
// 0016d0a0: no function (creating)
// Organizer_startRaceBody @ 0016d0a0  size=1
// callers: 
// callees: 

char Organizer_startRaceBody(void)

{
  int iVar1;
  char cVar5;
  undefined4 uVar2;
  undefined1 uVar6;
  undefined4 uVar3;
  undefined4 uVar4;
  int in_r11;
  undefined4 unaff_r20;
  int unaff_r21;
  undefined8 unaff_r22;
  undefined8 unaff_r23;
  undefined4 unaff_r24;
  byte unaff_r25;
  ulonglong unaff_r26;
  int iVar8;
  ulonglong uVar7;
  undefined1 unaff_r27;
  int unaff_r28;
  int iVar9;
  ulonglong unaff_r29;
  ulonglong unaff_r30;
  undefined8 uVar10;
  int *unaff_r31;
  byte in_cr0;
  
  iVar8 = (int)unaff_r26;
  *(int *)(in_r11 + 0x2a14) = iVar8;
  (&UNK_00032a18)[*unaff_r31] = unaff_r25;
  iVar9 = iVar8 >> 0x1f;
  if ((bool)(in_cr0 >> 1 & 1)) {
    iVar1 = *unaff_r31;
    if ((*(char *)(iVar1 + 0xa69) != '\0') || (*(char *)(iVar1 + 0xa6a) == '\0')) {
      WindowMgr_setupWindows
                (iVar1 + 0xa90,unaff_r27,(longlong)iVar9 - ((longlong)iVar9 ^ unaff_r26) >> 0x1f & 1
                 ,0);
    }
  }
  else {
    WindowMgr_setupWindows(*unaff_r31 + 0xa90,0,1,1);
    WindowMgr_fn_45f8e4(*unaff_r31 + 0xa90);
  }
  if (iVar8 == 2) {
    WindowMgr_fn_45f8e4(*unaff_r31 + 0xa90);
  }
  else if (iVar8 == 3) {
    WindowMgr_fn_45f8e4(*unaff_r31 + 0xa90);
    WindowMgr_fn_460270(*unaff_r31 + 0xa90);
  }
  if (((bool)(((byte)(unaff_r29 >> 0x1c) & 0xf) >> 1 & 1)) &&
     (uVar7 = unaff_r30 >> 0x18, unaff_r30 = ((unaff_r30 << 0x20) >> 0x3c) << 0x1c,
     (bool)((byte)uVar7 >> 5 & 1))) {
    func_0x0016c2cc(unaff_r23,1);
  }
  cVar5 = FUN_00379b20(unaff_r24);
  if (cVar5 == '\0') {
    if ((bool)(((byte)(unaff_r29 >> 0x1c) & 0xf) >> 1 & 1)) {
      uVar7 = unaff_r30 >> 0x18;
      unaff_r30 = ((unaff_r30 << 0x20) >> 0x3c) << 0x1c;
      if ((bool)((byte)uVar7 >> 5 & 1)) {
        if (*(int *)(*(int *)(&UNK_00018d54 + unaff_r28) +
                     *(int *)(&UNK_00018d60 + unaff_r28) * 0xb40 + 0x10) != 1) {
          cVar5 = FUN_0037a908(unaff_r24);
          uVar2 = 1;
          if (cVar5 == '\0') goto code_r0x0016d210;
        }
      }
      uVar2 = 0;
    }
    else {
      uVar2 = 2;
    }
code_r0x0016d210:
    *(undefined4 *)(*(int *)(*unaff_r31 + 0xa78) + 0x18) = uVar2;
  }
  else {
    *(undefined4 *)(*(int *)(*unaff_r31 + 0xa78) + 0x18) = 1;
  }
  *(byte *)(*(int *)(*unaff_r31 + 0xa78) + 0x4c) = unaff_r25 ^ 1;
  if (((bool)(((byte)(unaff_r30 >> 0x1c) & 0xf) >> 1 & 1)) &&
     (uVar7 = unaff_r29 >> 0x18, unaff_r29 = ((unaff_r29 << 0x20) >> 0x3c) << 0x1c,
     (bool)((byte)uVar7 >> 5 & 1))) {
    uVar7 = ((longlong)iVar9 - ((longlong)iVar9 ^ unaff_r26) << 0x20) >> 0x3f;
  }
  else {
    uVar7 = 1;
  }
  iVar9 = *unaff_r31;
  if ((*(char *)(iVar9 + 0xa69) == '\0') && (cVar5 = '\x01', *(char *)(iVar9 + 0xa6a) != '\0'))
  goto code_r0x0016d318;
  if ((bool)(((byte)(unaff_r29 >> 0x1c) & 0xf) >> 1 & 1)) {
code_r0x0016d2c8:
    uVar10 = 0;
  }
  else {
    uVar2 = FUN_0016c210(unaff_r23);
    cVar5 = FUN_00235a20(uVar2);
    if (cVar5 == '\0') {
      iVar9 = *unaff_r31;
      goto code_r0x0016d2c8;
    }
    uVar10 = 1;
    iVar9 = *unaff_r31;
  }
  uVar2 = thunk_FUN_0037ea9c(unaff_r21);
  uVar6 = FUN_0037ae24(uVar2);
  (&UNK_00032a1b)[iVar9] = uVar6;
  cVar5 = FUN_00380618(unaff_r21,unaff_r24,uVar7,uVar10,0);
  FUN_0037ea14(unaff_r21,unaff_r20);
  iVar9 = *unaff_r31;
code_r0x0016d318:
  uVar2 = FUN_00379a68(unaff_r24);
  uVar6 = FUN_00379b20(unaff_r24);
  WindowMgr_fn_45f544(iVar9 + 0xa90,uVar2,uVar6);
  uVar2 = FUN_00360c98();
  uVar3 = FUN_0016c1ec(unaff_r23);
  uVar4 = func_0x0016c1f8(unaff_r23);
  func_0x00360b30(uVar2,uVar3,uVar4);
  uVar2 = FUN_0035e9b8();
  uVar3 = FUN_0038dda0(unaff_r21);
  uVar4 = FUN_0016c1ec(unaff_r23);
  func_0x0035fff4(uVar2,uVar3,uVar4,uVar4);
  uVar2 = FUN_0045a3c8();
  func_0x0045a290(uVar2,*(undefined4 *)(unaff_r21 + 0xa00));
  uVar2 = FUN_0035c844();
  FUN_0035e370(uVar2,*(undefined4 *)(unaff_r21 + 0xa00),unaff_r24);
  if (cVar5 != '\0') {
    *(undefined1 *)(*unaff_r31 + 0xa69) = 0;
    FUN_00a8e534(0xffffffffffffffff);
  }
  *(undefined4 *)(&UNK_00032a0c + *unaff_r31) = 0;
  FUN_0016c2dc(unaff_r22);
  return cVar5;
}


////////////////////////////////////////////////////////////////
// Organizer_initCaller @ 001791d8  size=236
// callers: FUN_001841e8@001841e8 
// callees: FUN_001771c4@001771c4 FUN_0023575c@0023575c Organizer_initA@0016e984 FUN_0016e7ec@0016e7ec FUN_00178c6c@00178c6c FUN_0016e760@0016e760 FUN_0016e734@0016e734 FUN_0016eb90@0016eb90 

undefined4 Organizer_initCaller(int param_1)

{
  char cVar2;
  undefined4 uVar1;
  
  cVar2 = FUN_0016e7ec(param_1);
  if ((((cVar2 == '\0') || (cVar2 = FUN_001771c4(param_1), cVar2 == '\0')) ||
      (cVar2 = FUN_00178c6c(param_1), cVar2 == '\0')) ||
     (((cVar2 = FUN_0016eb90(param_1), cVar2 == '\0' ||
       (cVar2 = FUN_0016e760(param_1), cVar2 == '\0')) ||
      (cVar2 = Organizer_initA(param_1), cVar2 == '\0')))) {
    uVar1 = 0;
  }
  else {
    cVar2 = FUN_0023575c(&UNK_00018d40 + param_1);
    if (cVar2 != '\0') {
      FUN_0016e734(param_1);
    }
    uVar1 = 1;
    (&DAT_00034f88)[param_1] = 0;
  }
  return uVar1;
}


////////////////////////////////////////////////////////////////
// copyConfig_caller2 @ 00176ec8  size=152
// callers: FUN_001789e0@001789e0 
// callees: FUN_00189090@00189090 WindowMgr_copyConfig@00460e34 FUN_00176d7c@00176d7c 

void copyConfig_caller2(int param_1)

{
  undefined *puVar1;
  
  puVar1 = &UNK_00033d18 + param_1;
  FUN_00176d7c(param_1);
  WindowMgr_copyConfig(param_1 + 0xa90,puVar1);
  (*(code *)**(undefined4 **)(**(int **)(param_1 + 0xad4) + 0x10))
            (*(int **)(param_1 + 0xad4),puVar1);
  FUN_00189090(&UNK_00033d30 + param_1,puVar1);
  return;
}


////////////////////////////////////////////////////////////////
// WindowLoop_helper @ 00227fc0  size=152
// callers: WindowLoopB@00229310 WindowLoopA@002284f8 
// callees: FUN_00238604@00238604 

void WindowLoop_helper(int param_1,undefined8 param_2,undefined8 param_3,undefined8 param_4)

{
  undefined8 uStack00000048;
  undefined1 local_50 [64];
  
  uStack00000048 = param_4;
  FUN_00238604(*(undefined4 *)(param_1 + 0x14),local_50);
  return;
}


