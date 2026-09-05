////////////////////////////////////////////////////////////////
// 00460814: no function (creating)
// WindowMgr_setWindowMax @ 00460814  size=1
// callers: 
// callees: 

void WindowMgr_setWindowMax(int param_1,int param_2)

{
  *(int *)(param_1 + 0x2c) = param_2;
  if (param_2 < 1) {
    *(undefined1 *)(*(int *)(param_1 + 0x1c) + 0xc) = 0;
  }
  else {
    *(undefined1 *)(*(int *)(param_1 + 0x1c) + 0xc) = 1;
  }
  if (1 < *(int *)(param_1 + 0x2c)) {
    *(undefined1 *)(*(int *)(param_1 + 0x24) + 0xc) = 1;
    return;
  }
  *(undefined1 *)(*(int *)(param_1 + 0x24) + 0xc) = 0;
  return;
}


////////////////////////////////////////////////////////////////
// WindowMgr_getWindowMax @ 0045f274  size=12
// callers: FUN_0046058c@0046058c FUN_00172764@00172764 
// callees: 

undefined4 WindowMgr_getWindowMax(int param_1)

{
  return *(undefined4 *)(param_1 + 0x2c);
}


////////////////////////////////////////////////////////////////
// WindowMgr_disableAllWindows @ 00460868  size=96
// callers: FUN_00175ad8@00175ad8 
// callees: FUN_00465b6c@00465b6c 

void WindowMgr_disableAllWindows(int param_1)

{
  bool bVar1;
  int iVar2;
  int iVar3;
  int *piVar4;
  
  iVar3 = 0;
  piVar4 = (int *)(param_1 + 0x1c);
  do {
    *(undefined1 *)(*piVar4 + 0xc) = 0;
    iVar2 = *piVar4;
    piVar4 = piVar4 + 2;
    FUN_00465b6c(iVar2);
    bVar1 = iVar3 != 1;
    iVar3 = iVar3 + 1;
  } while (bVar1);
  return;
}


////////////////////////////////////////////////////////////////
// WindowMgr_setupWindows @ 0046058c  size=280
// callers: 
// callees: FUN_0045f890@0045f890 FUN_00464288@00464288 FUN_00467d04@00467d04 WindowMgr_getWindowMax@0045f274 

void WindowMgr_setupWindows(int param_1,undefined1 param_2,undefined1 param_3,undefined1 param_4)

{
  bool bVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  undefined4 *puVar5;
  
  iVar4 = 0;
  puVar5 = (undefined4 *)(param_1 + 0x1c);
  do {
    iVar3 = WindowMgr_getWindowMax(param_1);
    if (iVar3 < 2) {
      FUN_00464288(*puVar5,0,&DAT_01784614);
    }
    else {
      FUN_00464288(*puVar5,0,&DAT_0178463c);
    }
    uVar2 = *puVar5;
    puVar5 = puVar5 + 2;
    FUN_00467d04(uVar2,param_2,param_3,param_4);
    bVar1 = iVar4 != 1;
    iVar4 = iVar4 + 1;
  } while (bVar1);
  *(undefined1 *)(param_1 + 0x36) = param_4;
  *(undefined1 *)(param_1 + 0x34) = param_2;
  *(undefined1 *)(param_1 + 0x35) = param_3;
  FUN_0045f890(param_1);
  return;
}


////////////////////////////////////////////////////////////////
// Window_setCameraTable @ 00464288  size=112
// callers: WindowMgr_setupWindows@0046058c 
// callees: 

void Window_setCameraTable(int param_1,int param_2,int param_3)

{
  int iVar1;
  int *piVar2;
  int iVar3;
  int *piVar4;
  int iVar5;
  
  piVar2 = (int *)(param_1 + param_2 * 0x10 + 0x10);
  piVar2[1] = 0;
  iVar1 = *piVar2;
  *piVar2 = param_3;
  if (*(int *)(param_3 + 4) != -1) {
    iVar5 = 1;
    iVar3 = param_3;
    do {
      piVar2[1] = iVar5;
      iVar5 = iVar5 + 1;
      piVar4 = (int *)(iVar3 + 0xc);
      iVar3 = iVar3 + 8;
    } while (*piVar4 != -1);
  }
  if (iVar1 != param_3) {
    piVar2[2] = 0;
  }
  piVar2[3] = piVar2[2];
  return;
}


////////////////////////////////////////////////////////////////
// Window_setFlags @ 00467d04  size=636
// callers: WindowMgr_setupWindows@0046058c 
// callees: FUN_00464850@00464850 FUN_0047075c@0047075c FUN_004642f8@004642f8 FUN_0047079c@0047079c FUN_00466cdc@00466cdc FUN_00485120@00485120 

void Window_setFlags(int param_1,int param_2,int param_3,int param_4)

{
  char cVar2;
  int iVar1;
  int *piVar3;
  
  iVar1 = *(int *)(param_1 + 4);
  *(char *)(iVar1 + 0xda0a) = (char)param_4;
  *(char *)(iVar1 + 0xda08) = (char)param_2;
  *(char *)(iVar1 + 0xda09) = (char)param_3;
  if ((param_3 == 0 && param_2 == 0) && param_4 == 0) {
    piVar3 = (int *)(param_1 + 4);
    *(undefined4 *)(*piVar3 + 0xd9cc) = 0;
    *(undefined4 *)(*piVar3 + 0xd9d4) = 1;
    *(undefined1 *)(*piVar3 + 0xe425) = 0;
    *(undefined1 *)(*piVar3 + 0xd9d8) = 0;
  }
  else {
    piVar3 = (int *)(param_1 + 4);
    *(undefined4 *)(*piVar3 + 0xd9cc) = 1;
    *(undefined4 *)(*piVar3 + 0xd9d4) = 0;
    *(undefined1 *)(*piVar3 + 0xe425) = 1;
    *(undefined1 *)(*piVar3 + 0xd9d8) = 0;
  }
  piVar3 = (int *)(param_1 + 4);
  *(undefined4 *)(*piVar3 + 0xe410) = 0;
  *(undefined4 *)(*piVar3 + 0xe414) = 0;
  *(undefined4 *)(*piVar3 + 0xe418) = 0;
  *(undefined4 *)(*piVar3 + 0xd9dc) = 0;
  *(undefined1 *)(*piVar3 + 0xd9e0) = 0;
  *(undefined4 *)(*piVar3 + 0xd9e4) = 0;
  *(undefined1 *)(*piVar3 + 0xd9e8) = 0;
  *(undefined4 *)(*piVar3 + 0xd9ec) = 0;
  *(undefined1 *)(*piVar3 + 0xd9f0) = 0;
  *(undefined1 *)(*piVar3 + 0xd9f2) = *(undefined1 *)(*piVar3 + 0xd9f1);
  *(undefined1 *)(*piVar3 + 0xe40c) = 0;
  if (*(char *)(*piVar3 + 0xd9f3) != '\0') {
    *(undefined4 *)(param_1 + 0x18) = 1;
  }
  cVar2 = FUN_004642f8(param_1);
  if (cVar2 == '\0') {
    iVar1 = FUN_00464850(param_1);
    *(undefined4 *)(iVar1 + 8) = 1;
  }
  else {
    iVar1 = FUN_00464850(param_1);
    *(undefined4 *)(iVar1 + 8) = 0;
    FUN_00466cdc(param_1,param_1 + 0x10);
  }
  FUN_00485120(*piVar3);
  iVar1 = FUN_00464850(param_1);
  *(undefined4 *)(iVar1 + 0x44) = 0;
  *(undefined4 *)(*(int *)(param_1 + 4) + 0xe3b0) = 0;
  *(undefined4 *)(*(int *)(param_1 + 4) + 0xda14) = 0;
  *(undefined4 *)(*(int *)(param_1 + 4) + 0xda18) = 0;
  *(undefined4 *)(*piVar3 + 0xd9bc) = *(undefined4 *)(*piVar3 + 0xd9b0);
  FUN_0047075c(param_1 + 0x50);
  FUN_0047075c(param_1 + 0x84);
  FUN_0047079c(param_1 + 0x50);
  FUN_0047079c(param_1 + 0x84);
  *(undefined1 *)(*piVar3 + 0xe428) = 1;
  return;
}


////////////////////////////////////////////////////////////////
// WindowMgr_copyConfig @ 00460e34  size=288
// callers: FUN_0016e984@0016e984 FUN_00176ec8@00176ec8 
// callees: FUN_00a8b00c@00a8b00c 

void WindowMgr_copyConfig(undefined4 *param_1,undefined4 *param_2)

{
  *param_1 = *param_2;
  FUN_00a8b00c(param_1 + 1,param_2 + 1);
  param_1[2] = param_2[2];
  FUN_00a8b00c(param_1 + 3,param_2 + 3);
  param_1[4] = param_2[4];
  FUN_00a8b00c(param_1 + 5,param_2 + 5);
  DAT_017fd40c = *param_1;
  FUN_00a8b00c(&DAT_017fd410,param_1 + 1);
  DAT_017fd414 = param_1[2];
  FUN_00a8b00c(&DAT_017fd418,param_1 + 3);
  DAT_017fd41c = param_1[4];
  FUN_00a8b00c(&DAT_017fd420,param_1 + 5);
  return;
}


////////////////////////////////////////////////////////////////
// 002381a0: no function (creating)
// RaceDisp_setWindowNum @ 002381a0  size=1
// callers: 
// callees: 

void RaceDisp_setWindowNum(int param_1,undefined1 param_2)

{
  *(undefined1 *)(param_1 + 3) = param_2;
  return;
}


////////////////////////////////////////////////////////////////
// RaceDisp_getWindowNum @ 00238194  size=12
// callers: FUN_0023864c@0023864c 
// callees: 

undefined1 RaceDisp_getWindowNum(int param_1)

{
  return *(undefined1 *)(param_1 + 3);
}


////////////////////////////////////////////////////////////////
// 00238188: no function (creating)
// RaceDisp_set3c40 @ 00238188  size=1
// callers: 
// callees: 

void RaceDisp_set3c40(int param_1,undefined4 param_2,undefined4 param_3)

{
  *(undefined4 *)(param_1 + 0x3c) = param_2;
  *(undefined4 *)(param_1 + 0x40) = param_3;
  return;
}


////////////////////////////////////////////////////////////////
// 00238394: no function (creating)
// RaceDisp_reset @ 00238394  size=1
// callers: 
// callees: 

void RaceDisp_reset(int param_1)

{
  bool bVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  
  iVar2 = 0;
  iVar4 = param_1 + 0x414;
  iVar5 = param_1 + 0x22c;
  *(undefined4 *)(&DAT_000369b0 + param_1) = 0;
  *(undefined4 *)(&DAT_000369a8 + param_1) = 0;
  *(undefined4 *)(&DAT_000369ac + param_1) = 0;
  iVar3 = param_1 + 0x44;
  do {
    func_0x002380f0(iVar3);
    func_0x002380f0(iVar5);
    func_0x002380f0(iVar4);
    bVar1 = iVar2 != 3;
    iVar5 = iVar5 + 0x5bc;
    iVar4 = iVar4 + 0x5bc;
    iVar2 = iVar2 + 1;
    iVar3 = iVar3 + 0x5bc;
  } while (bVar1);
  return;
}


////////////////////////////////////////////////////////////////
// 00238644: no function (creating)
// Adhoc_setRaceDisplayWindowNum_thunk @ 00238644  size=1
// callers: 
// callees: 

void Adhoc_setRaceDisplayWindowNum_thunk(int *param_1,undefined1 param_2)

{
  *(undefined1 *)(*param_1 + 3) = param_2;
  return;
}


////////////////////////////////////////////////////////////////
// 00172738: no function (creating)
// MOrganizer_setWindowMax @ 00172738  size=1
// callers: 
// callees: 

void MOrganizer_setWindowMax(int *param_1)

{
  WindowMgr_setWindowMax(*param_1 + 0xa90);
  return;
}


////////////////////////////////////////////////////////////////
// 00171790: no function (creating)
// MOrganizer_getRaceDisp @ 00171790  size=1
// callers: 
// callees: 

int MOrganizer_getRaceDisp(int *param_1)

{
  return *param_1 + 0xae8;
}


////////////////////////////////////////////////////////////////
// Organizer_initA @ 0016e984  size=272
// callers: FUN_001791d8@001791d8 
// callees: FUN_004effa0@004effa0 WindowMgr_copyConfig@00460e34 FUN_004efbc8@004efbc8 FUN_00189090@00189090 FUN_0045f340@0045f340 

bool Organizer_initA(int param_1)

{
  undefined *puVar1;
  char cVar2;
  undefined1 local_80 [36];
  undefined1 local_5c [44];
  
  puVar1 = &UNK_00033d18 + param_1;
  cVar2 = FUN_004effa0(puVar1);
  if (cVar2 != '\0') {
    FUN_004efbc8(puVar1,local_80,0);
    WindowMgr_copyConfig(param_1 + 0xa90,puVar1);
    (*(code *)**(undefined4 **)(**(int **)(param_1 + 0xad4) + 0x10))
              (*(int **)(param_1 + 0xad4),puVar1);
    FUN_00189090(&UNK_00033d30 + param_1,puVar1);
  }
  else {
    FUN_0045f340(param_1 + 0xa90);
    FUN_0045f340(param_1 + 0xa90,local_5c,0);
  }
  return cVar2 != '\0';
}


////////////////////////////////////////////////////////////////
// 002284f8: no function (creating)
// WindowLoopA @ 002284f8  size=260
// callers: 
// callees: FUN_00227fc0@00227fc0 FUN_004601b0@004601b0 WindowMgr_getWindowMax@0045f274 

void WindowLoopA(ulonglong param_1)

{
  bool bVar1;
  char cVar3;
  int iVar2;
  undefined4 unaff_r25;
  int unaff_r26;
  undefined8 unaff_r27;
  undefined8 unaff_r28;
  int unaff_r29;
  int unaff_r30;
  int unaff_r31;
  undefined4 in_stack_0000008c;
  undefined4 in_stack_00000090;
  uint in_stack_00000094;
  int in_stack_00000098;
  
  while( true ) {
    iVar2 = WindowMgr_getWindowMax(param_1);
    bVar1 = iVar2 <= unaff_r30;
    unaff_r30 = unaff_r30 + 1;
    if (bVar1) break;
    cVar3 = FUN_004601b0(*(undefined4 *)(unaff_r31 + 8),unaff_r27,unaff_r29);
    if (cVar3 != '\0') {
      FUN_00227fc0(unaff_r28,unaff_r29,unaff_r25,CONCAT44(in_stack_0000008c,in_stack_00000090));
    }
    cVar3 = FUN_004601b0(*(undefined4 *)(unaff_r31 + 8),
                         *(undefined4 *)
                          (*(int *)(*(int *)(unaff_r31 + 4) + 0x9fc) +
                          *(int *)(unaff_r26 + 0x38) * 0xc),unaff_r29);
    if ((cVar3 != '\0') && (in_stack_00000098 == 0)) {
      FUN_00227fc0(unaff_r28,unaff_r29,0,(ulonglong)in_stack_00000094 << 0x20);
    }
    param_1 = (ulonglong)*(uint *)(unaff_r31 + 8);
    unaff_r29 = unaff_r30;
  }
  return;
}


////////////////////////////////////////////////////////////////
// 00229310: no function (creating)
// WindowLoopB @ 00229310  size=408
// callers: 
// callees: FUN_00227fc0@00227fc0 FUN_00238604@00238604 FUN_00388554@00388554 FUN_004601b0@004601b0 WindowMgr_getWindowMax@0045f274 

void WindowLoopB(ulonglong param_1)

{
  byte bVar1;
  char cVar3;
  int iVar2;
  int unaff_r25;
  undefined4 unaff_r26;
  undefined8 unaff_r27;
  int unaff_r28;
  undefined8 unaff_r30;
  int unaff_r31;
  undefined4 in_stack_0000008c;
  undefined4 in_stack_00000090;
  undefined4 in_stack_00000094;
  undefined4 in_stack_00000098;
  byte bStack000000d0;
  
  for (; iVar2 = WindowMgr_getWindowMax(param_1), unaff_r28 < iVar2; unaff_r28 = unaff_r28 + 1) {
    cVar3 = FUN_004601b0(*(undefined4 *)(unaff_r31 + 8),unaff_r30,unaff_r28);
    if (cVar3 != '\0') {
      FUN_00227fc0(unaff_r27,unaff_r28,unaff_r26,CONCAT44(in_stack_0000008c,in_stack_00000090));
    }
    cVar3 = FUN_004601b0(*(undefined4 *)(unaff_r31 + 8),*(undefined4 *)(unaff_r25 + 0x20c),unaff_r28
                        );
    if (cVar3 != '\0') {
      FUN_00227fc0(unaff_r27,unaff_r28,0,CONCAT44(in_stack_00000094,in_stack_00000098));
    }
    param_1 = (ulonglong)*(uint *)(unaff_r31 + 8);
  }
  FUN_00388554(*(undefined4 *)(unaff_r31 + 4),unaff_r30);
  FUN_00388554(*(undefined4 *)(unaff_r31 + 4),unaff_r30);
  iVar2 = FUN_00388554(*(undefined4 *)(unaff_r31 + 4),unaff_r30);
  bVar1 = *(byte *)(iVar2 + 0x251);
  FUN_00388554(*(undefined4 *)(unaff_r31 + 4),unaff_r30);
  bStack000000d0 = (byte)(-(ulonglong)bVar1 >> 0x18) >> 7;
  FUN_00238604(*(undefined4 *)(unaff_r31 + 0x14),&stack0x000000a0);
  return;
}


////////////////////////////////////////////////////////////////
// 00481d94: no function (creating)
// setupWindows_callerC @ 00481d94  size=100
// callers: 
// callees: FUN_004645f0@004645f0 FUN_0046565c@0046565c WindowMgr_setupWindows@0046058c FUN_00bcf5ec@00bcf5ec 

void setupWindows_callerC(void)

{
  undefined4 uVar1;
  int unaff_r28;
  int unaff_r31;
  
  WindowMgr_setupWindows();
  FUN_0046565c(*(undefined4 *)(unaff_r31 + 0x340),&stack0x00000070);
  uVar1 = FUN_004645f0(*(undefined4 *)(unaff_r31 + 0x340),4,0);
  FUN_00bcf5ec(unaff_r28 + 0x10,uVar1,0x330);
  return;
}


////////////////////////////////////////////////////////////////
// 0016d0cc: no function (creating)
// setupWindows_callerA @ 0016d0cc  size=1
// callers: 
// callees: 

char setupWindows_callerA(void)

{
  char cVar4;
  undefined4 uVar1;
  undefined1 uVar5;
  undefined4 uVar2;
  undefined4 uVar3;
  undefined4 unaff_r20;
  int unaff_r21;
  undefined8 unaff_r22;
  undefined8 unaff_r23;
  undefined4 unaff_r24;
  byte unaff_r25;
  ulonglong unaff_r26;
  int iVar7;
  ulonglong uVar6;
  int unaff_r28;
  ulonglong unaff_r29;
  ulonglong unaff_r30;
  undefined8 uVar8;
  int *unaff_r31;
  
  WindowMgr_setupWindows();
  FUN_0045f8e4(*unaff_r31 + 0xa90);
  iVar7 = (int)unaff_r26;
  if (iVar7 == 2) {
    FUN_0045f8e4(*unaff_r31 + 0xa90);
  }
  else if (iVar7 == 3) {
    FUN_0045f8e4(*unaff_r31 + 0xa90);
    func_0x00460270(*unaff_r31 + 0xa90);
  }
  if (((bool)(((byte)(unaff_r29 >> 0x1c) & 0xf) >> 1 & 1)) &&
     (uVar6 = unaff_r30 >> 0x18, unaff_r30 = ((unaff_r30 << 0x20) >> 0x3c) << 0x1c,
     (bool)((byte)uVar6 >> 5 & 1))) {
    func_0x0016c2cc(unaff_r23,1);
  }
  cVar4 = FUN_00379b20(unaff_r24);
  if (cVar4 == '\0') {
    if ((bool)(((byte)(unaff_r29 >> 0x1c) & 0xf) >> 1 & 1)) {
      uVar6 = unaff_r30 >> 0x18;
      unaff_r30 = ((unaff_r30 << 0x20) >> 0x3c) << 0x1c;
      if ((bool)((byte)uVar6 >> 5 & 1)) {
        if (*(int *)(*(int *)(&UNK_00018d54 + unaff_r28) +
                     *(int *)(&UNK_00018d60 + unaff_r28) * 0xb40 + 0x10) != 1) {
          cVar4 = FUN_0037a908(unaff_r24);
          uVar1 = 1;
          if (cVar4 == '\0') goto code_r0x0016d210;
        }
      }
      uVar1 = 0;
    }
    else {
      uVar1 = 2;
    }
code_r0x0016d210:
    *(undefined4 *)(*(int *)(*unaff_r31 + 0xa78) + 0x18) = uVar1;
  }
  else {
    *(undefined4 *)(*(int *)(*unaff_r31 + 0xa78) + 0x18) = 1;
  }
  *(byte *)(*(int *)(*unaff_r31 + 0xa78) + 0x4c) = unaff_r25 ^ 1;
  if (((bool)(((byte)(unaff_r30 >> 0x1c) & 0xf) >> 1 & 1)) &&
     (uVar6 = unaff_r29 >> 0x18, unaff_r29 = ((unaff_r29 << 0x20) >> 0x3c) << 0x1c,
     (bool)((byte)uVar6 >> 5 & 1))) {
    uVar6 = ((longlong)(iVar7 >> 0x1f) - ((longlong)(iVar7 >> 0x1f) ^ unaff_r26) << 0x20) >> 0x3f;
  }
  else {
    uVar6 = 1;
  }
  iVar7 = *unaff_r31;
  if ((*(char *)(iVar7 + 0xa69) == '\0') && (cVar4 = '\x01', *(char *)(iVar7 + 0xa6a) != '\0'))
  goto code_r0x0016d318;
  if ((bool)(((byte)(unaff_r29 >> 0x1c) & 0xf) >> 1 & 1)) {
code_r0x0016d2c8:
    uVar8 = 0;
  }
  else {
    uVar1 = FUN_0016c210(unaff_r23);
    cVar4 = FUN_00235a20(uVar1);
    if (cVar4 == '\0') {
      iVar7 = *unaff_r31;
      goto code_r0x0016d2c8;
    }
    uVar8 = 1;
    iVar7 = *unaff_r31;
  }
  uVar1 = thunk_FUN_0037ea9c(unaff_r21);
  uVar5 = FUN_0037ae24(uVar1);
  (&UNK_00032a1b)[iVar7] = uVar5;
  cVar4 = FUN_00380618(unaff_r21,unaff_r24,uVar6,uVar8,0);
  FUN_0037ea14(unaff_r21,unaff_r20);
  iVar7 = *unaff_r31;
code_r0x0016d318:
  uVar1 = FUN_00379a68(unaff_r24);
  uVar5 = FUN_00379b20(unaff_r24);
  func_0x0045f544(iVar7 + 0xa90,uVar1,uVar5);
  uVar1 = FUN_00360c98();
  uVar2 = FUN_0016c1ec(unaff_r23);
  uVar3 = func_0x0016c1f8(unaff_r23);
  func_0x00360b30(uVar1,uVar2,uVar3);
  uVar1 = FUN_0035e9b8();
  uVar2 = FUN_0038dda0(unaff_r21);
  uVar3 = FUN_0016c1ec(unaff_r23);
  func_0x0035fff4(uVar1,uVar2,uVar3,uVar3);
  uVar1 = FUN_0045a3c8();
  func_0x0045a290(uVar1,*(undefined4 *)(unaff_r21 + 0xa00));
  uVar1 = FUN_0035c844();
  FUN_0035e370(uVar1,*(undefined4 *)(unaff_r21 + 0xa00),unaff_r24);
  if (cVar4 != '\0') {
    *(undefined1 *)(*unaff_r31 + 0xa69) = 0;
    FUN_00a8e534(0xffffffffffffffff);
  }
  *(undefined4 *)(&UNK_00032a0c + *unaff_r31) = 0;
  FUN_0016c2dc(unaff_r22);
  return cVar4;
}


