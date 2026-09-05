////////////////////////////////////////////////////////////////
// 0002dce4: no function (creating)
// FUN_0002dce4 @ 0002dce4  size=152
// callers: 
// callees: FUN_00568190@00568190 FUN_0017243c@0017243c FUN_0045f824@0045f824 FUN_0016c0c8@0016c0c8 

void FUN_0002dce4(void)

{
  uint uVar1;
  undefined4 uVar2;
  char cVar4;
  uint *puVar3;
  longlong lVar5;
  uint uVar6;
  ulonglong uVar7;
  undefined4 unaff_r28;
  undefined4 unaff_r29;
  undefined8 unaff_r30;
  int unaff_r31;
  char in_RESERVE;
  byte in_cr0;
  
  uVar2 = FUN_0016c0c8();
  uVar1 = *(uint *)(*(int *)(unaff_r31 + 0x158) + 0x1c);
  cVar4 = FUN_0045f824(uVar2);
  if (cVar4 != '\0') {
    cVar4 = FUN_0017243c(unaff_r30);
    uVar6 = 0;
    lVar5 = 0;
    if (cVar4 != '\0') goto LAB_0002dd28;
  }
  uVar6 = 1;
  lVar5 = 1;
LAB_0002dd28:
  uVar7 = *(ulonglong *)(uVar1 + 0x108);
  if (uVar6 != ((uint)(uVar7 >> 0xe) & 1)) {
    do {
      puVar3 = (uint *)((ulonglong)uVar1 + 0x108);
      if (in_RESERVE != '\0') {
        uVar6 = storeWordConditionalIndexed
                          ((ulonglong)*puVar3 | 2,0,(ulonglong)uVar1 + 0x108 & 0xffffffff);
        *puVar3 = uVar6;
        in_cr0 = 2;
      }
    } while (!(bool)(in_cr0 >> 1 & 1));
    uVar7 = *(ulonglong *)(uVar1 + 0x108);
  }
  *(ulonglong *)(uVar1 + 0x108) = lVar5 << 0xe | uVar7 & 0xffffffffffffbfff;
  FUN_00568190(unaff_r28,unaff_r29);
  return;
}


////////////////////////////////////////////////////////////////
// 0016e288: no function (creating)
// FUN_0016e288 @ 0016e288  size=1
// callers: 
// callees: 

void FUN_0016e288(void)

{
  undefined4 uVar1;
  
  uVar1 = FUN_0016c0c8();
  WindowMgr_initDefault(uVar1,&stack0x00000070,0);
  return;
}


////////////////////////////////////////////////////////////////
// 0017414c: no function (creating)
// FUN_0017414c @ 0017414c  size=1
// callers: 
// callees: 

void FUN_0017414c(void)

{
  undefined4 uVar1;
  
  uVar1 = FUN_0016c0c8();
  WindowMgr_initDefault(uVar1,&stack0x00000070,0);
  return;
}


////////////////////////////////////////////////////////////////
// 00175568: no function (creating)
// FUN_00175568 @ 00175568  size=1
// callers: 
// callees: 

uint FUN_00175568(void)

{
  uint uVar1;
  undefined4 uVar2;
  uint in_stack_00000090;
  
  uVar2 = FUN_0016c0c8();
  WindowMgr_initDefault(uVar2,&stack0x00000070,0);
  uVar1 = (int)(in_stack_00000090 ^ 2) >> 0x1f;
  return ((uVar1 ^ in_stack_00000090 ^ 2) - uVar1) - 1 >> 0x1f;
}


////////////////////////////////////////////////////////////////
// 00189e94: no function (creating)
// FUN_00189e94 @ 00189e94  size=1
// callers: 
// callees: 

void FUN_00189e94(void)

{
  undefined4 uVar1;
  undefined4 in_stack_0000009c;
  uint in_stack_000000b0;
  
  uVar1 = FUN_0016c0c8();
  WindowMgr_initDefault(uVar1,&stack0x00000074,0);
  if (0xf < in_stack_000000b0) {
    FUN_00ac1e34(in_stack_0000009c);
  }
  return;
}


////////////////////////////////////////////////////////////////
// 0018a674: no function (creating)
// FUN_0018a674 @ 0018a674  size=1
// callers: 
// callees: 

void FUN_0018a674(void)

{
  undefined4 uVar1;
  undefined4 in_stack_00000098;
  uint in_stack_000000ac;
  
  uVar1 = FUN_0016c0c8();
  WindowMgr_initDefault(uVar1,&stack0x00000070,0);
  if (0xf < in_stack_000000ac) {
    FUN_00ac1e34(in_stack_00000098);
  }
  return;
}


////////////////////////////////////////////////////////////////
// 0018aa48: no function (creating)
// FUN_0018aa48 @ 0018aa48  size=1
// callers: 
// callees: 

void FUN_0018aa48(void)

{
  undefined4 uVar1;
  undefined4 in_stack_00000098;
  uint in_stack_000000ac;
  
  uVar1 = FUN_0016c0c8();
  WindowMgr_initDefault(uVar1,&stack0x00000070,0);
  if (0xf < in_stack_000000ac) {
    FUN_00ac1e34(in_stack_00000098);
  }
  return;
}


////////////////////////////////////////////////////////////////
// 004623b0: no function (creating)
// FUN_004623b0 @ 004623b0  size=28
// callers: 
// callees: FUN_0045f2a8@0045f2a8 

int FUN_004623b0(void)

{
  int iVar1;
  
  iVar1 = FUN_0045f2a8();
  return iVar1 + 0xb8;
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


